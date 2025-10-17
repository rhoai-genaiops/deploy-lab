#!/usr/bin/env python3
"""
Git Monitor for Model/Prompt Changes
Monitors chart/values-test.yaml and chart/values-prod.yaml for changes
and provides a web interface to view the history.

Environment Variables:
- GIT_REPO_URL: Git repository URL (optional, defaults to current directory)
- GIT_USERNAME: Git username for authentication
- GIT_PASSWORD: Git password/token for authentication
- GIT_BRANCH: Git branch to monitor (optional, defaults to 'main')
- MONITOR_INTERVAL: Monitoring interval in seconds (optional, defaults to 30)
"""

import os
import yaml
import subprocess
import json
from datetime import datetime
from flask import Flask, render_template, jsonify, request, Response, redirect
from threading import Thread
import time
import logging
import shutil
from urllib.parse import urlparse
import tempfile
import boto3
from botocore.exceptions import ClientError

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

class GitMonitor:
    def __init__(self, config=None):
        # Read configuration from environment variables or passed config
        if config:
            self.git_repo_url = config.get('git_repo_url', '')
            self.git_username = config.get('git_username', '')
            self.git_password = config.get('git_password', '')
            self.git_branch = config.get('git_branch', 'main')
            self.monitor_interval = int(config.get('monitor_interval', '30'))
        else:
            self.git_repo_url = os.getenv('GIT_REPO_URL', '')
            self.git_username = os.getenv('GIT_USERNAME', '')
            self.git_password = os.getenv('GIT_PASSWORD', '')
            self.git_branch = os.getenv('GIT_BRANCH', 'main')
            self.monitor_interval = int(os.getenv('MONITOR_INTERVAL', '30'))
            
        # S3 configuration for evaluation results
        if config:
            self.s3_endpoint = config.get('s3_endpoint', os.getenv('S3_ENDPOINT', ''))
            self.s3_access_key = config.get('s3_access_key', os.getenv('S3_ACCESS_KEY', ''))
            self.s3_secret_key = config.get('s3_secret_key', os.getenv('S3_SECRET_KEY', ''))
            self.s3_bucket_name = config.get('s3_bucket_name', os.getenv('S3_BUCKET_NAME', 'test-results'))
            self.s3_ui_url = config.get('s3_ui_url', os.getenv('S3_UI_URL', ''))
            self.s3_refresh_interval = int(config.get('s3_refresh_interval', os.getenv('S3_REFRESH_INTERVAL', '60')))
        else:
            self.s3_endpoint = os.getenv('S3_ENDPOINT', '')
            self.s3_access_key = os.getenv('S3_ACCESS_KEY', '')
            self.s3_secret_key = os.getenv('S3_SECRET_KEY', '')
            self.s3_bucket_name = os.getenv('S3_BUCKET_NAME', 'test-results')
            self.s3_ui_url = os.getenv('S3_UI_URL', '')
            self.s3_refresh_interval = int(os.getenv('S3_REFRESH_INTERVAL', '60'))
        
        # Initialize S3 client if credentials are provided
        self.s3_client = None
        if self.s3_endpoint and self.s3_access_key and self.s3_secret_key:
            try:
                self.s3_client = boto3.client(
                    's3',
                    endpoint_url=self.s3_endpoint,
                    aws_access_key_id=self.s3_access_key,
                    aws_secret_access_key=self.s3_secret_key,
                    region_name='us-east-1',
                    verify=False  # Disable SSL verification for MinIO with self-signed certs
                )
                logging.info("S3 client initialized successfully")
            except Exception as e:
                logging.error(f"Failed to initialize S3 client: {e}")
                self.s3_client = None
        
        # Set up repository path
        if self.git_repo_url:
            self.repo_path = self._setup_external_repo()
        else:
            self.repo_path = "."
            
        self.tracked_files = ["chart/values-test.yaml", "chart/values-prod.yaml"]
        self.changes_history = []
        self.last_commit_hash = None
        self.last_s3_refresh = 0  # Track last S3 refresh time
        
        logging.info(f"Initialized GitMonitor with repo_path: {self.repo_path}")
        logging.info(f"Monitoring interval: {self.monitor_interval} seconds")
        logging.info(f"Git branch: {self.git_branch}")
        
    def _setup_external_repo(self):
        """Set up external Git repository with authentication"""
        try:
            # Create a unique temporary directory for the repo
            temp_base = tempfile.mkdtemp(prefix="git_monitor_")
            repo_dir = os.path.join(temp_base, "repo")
            
            # Ensure the directory exists
            os.makedirs(repo_dir, exist_ok=True)
            
            # Construct authenticated URL if credentials are provided
            if self.git_username and self.git_password:
                parsed_url = urlparse(self.git_repo_url)
                auth_url = f"{parsed_url.scheme}://{self.git_username}:{self.git_password}@{parsed_url.netloc}{parsed_url.path}"
                logging.info(f"Using authenticated URL for repository")
            else:
                auth_url = self.git_repo_url
                logging.info(f"Using non-authenticated URL for repository")
            
            # Clone the repository with better error handling
            logging.info(f"Cloning repository to {repo_dir}")
            clone_cmd = ["git", "clone", "-b", self.git_branch, auth_url, repo_dir]
            
            # Set environment variables for git to avoid config issues
            env = os.environ.copy()
            env['GIT_CONFIG_NOSYSTEM'] = '1'
            env['HOME'] = tempfile.gettempdir()
            
            result = subprocess.run(clone_cmd, capture_output=True, text=True, env=env, cwd=temp_base, encoding='utf-8', errors='replace')
            
            if result.returncode != 0:
                logging.error(f"Failed to clone repository: {result.stderr}")
                # Try fallback approach - clone without specifying branch first
                logging.info("Trying fallback clone without branch specification")
                fallback_cmd = ["git", "clone", auth_url, repo_dir]
                result = subprocess.run(fallback_cmd, capture_output=True, text=True, env=env, cwd=temp_base, encoding='utf-8', errors='replace')
                
                if result.returncode != 0:
                    logging.error(f"Fallback clone also failed: {result.stderr}")
                    raise Exception(f"Git clone failed: {result.stderr}")
                
                # Now checkout the desired branch
                if self.git_branch != "main":
                    checkout_cmd = ["git", "checkout", self.git_branch]
                    result = subprocess.run(checkout_cmd, capture_output=True, text=True, env=env, cwd=repo_dir, encoding='utf-8', errors='replace')
                    if result.returncode != 0:
                        logging.warning(f"Failed to checkout branch {self.git_branch}: {result.stderr}")
            
            logging.info(f"Successfully cloned repository to {repo_dir}")
            return repo_dir
            
        except Exception as e:
            logging.error(f"Error setting up external repository: {e}")
            raise
    
    def _git_pull(self):
        """Pull latest changes from remote repository"""
        # Set environment variables for git to avoid config issues
        env = os.environ.copy()
        env['GIT_CONFIG_NOSYSTEM'] = '1'
        env['HOME'] = tempfile.gettempdir()
        
        if not self.git_repo_url:
            # For local repo, just fetch
            try:
                subprocess.run(["git", "fetch"], cwd=self.repo_path, capture_output=True, check=True, env=env)
                return True
            except subprocess.CalledProcessError as e:
                logging.error(f"Git fetch failed: {e}")
                return False
        
        try:
            # For external repo, pull latest changes
            pull_cmd = ["git", "pull", "origin", self.git_branch]
            result = subprocess.run(pull_cmd, cwd=self.repo_path, capture_output=True, text=True, env=env, encoding='utf-8', errors='replace')
            
            if result.returncode != 0:
                logging.error(f"Git pull failed: {result.stderr}")
                # Try a simple fetch and reset as fallback
                logging.info("Trying fallback fetch and reset")
                fetch_cmd = ["git", "fetch", "origin", self.git_branch]
                result = subprocess.run(fetch_cmd, cwd=self.repo_path, capture_output=True, text=True, env=env, encoding='utf-8', errors='replace')
                if result.returncode == 0:
                    reset_cmd = ["git", "reset", "--hard", f"origin/{self.git_branch}"]
                    result = subprocess.run(reset_cmd, cwd=self.repo_path, capture_output=True, text=True, env=env, encoding='utf-8', errors='replace')
                    if result.returncode == 0:
                        logging.info("Successfully updated using fetch and reset")
                        return True
                return False
            
            logging.info("Successfully pulled latest changes")
            return True
            
        except Exception as e:
            logging.error(f"Error during git pull: {e}")
            return False
        
    def get_git_log(self, file_path):
        """Get git log for a specific file"""
        try:
            # Set environment variables for git to avoid config issues
            env = os.environ.copy()
            env['GIT_CONFIG_NOSYSTEM'] = '1'
            env['HOME'] = tempfile.gettempdir()
            
            cmd = ["git", "log", "--oneline", "--follow", "--", file_path]
            result = subprocess.run(cmd, cwd=self.repo_path, capture_output=True, text=True, 
                                  env=env, encoding='utf-8', errors='replace')
            if result.returncode != 0:
                logging.error(f"Git log command failed for {file_path}: {result.stderr}")
                return []
            return result.stdout.strip().split('\n') if result.stdout.strip() else []
        except Exception as e:
            logging.error(f"Error getting git log for {file_path}: {e}")
            return []
    
    def get_file_content_at_commit(self, commit_hash, file_path):
        """Get file content at specific commit"""
        try:
            # Set environment variables for git to avoid config issues
            env = os.environ.copy()
            env['GIT_CONFIG_NOSYSTEM'] = '1'
            env['HOME'] = tempfile.gettempdir()
            
            cmd = ["git", "show", f"{commit_hash}:{file_path}"]
            result = subprocess.run(cmd, cwd=self.repo_path, capture_output=True, text=True, env=env, encoding='utf-8', errors='replace')
            return result.stdout if result.returncode == 0 else None
        except Exception as e:
            logging.error(f"Error getting file content at {commit_hash}: {e}")
            return None
    
    def get_commit_info(self, commit_hash):
        """Get commit information"""
        try:
            # Set environment variables for git to avoid config issues
            env = os.environ.copy()
            env['GIT_CONFIG_NOSYSTEM'] = '1'
            env['HOME'] = tempfile.gettempdir()
            
            cmd = ["git", "show", "--format=%H|%ai|%s|%an|%ae", "--no-patch", commit_hash]
            result = subprocess.run(cmd, cwd=self.repo_path, capture_output=True, text=True, env=env, encoding='utf-8', errors='replace')
            if result.returncode == 0:
                parts = result.stdout.strip().split('|')
                return {
                    'hash': parts[0],
                    'date': parts[1],
                    'message': parts[2] if len(parts) > 2 else '',
                    'author_name': parts[3] if len(parts) > 3 else '',
                    'author_email': parts[4] if len(parts) > 4 else ''
                }
        except Exception as e:
            logging.error(f"Error getting commit info for {commit_hash}: {e}")
        return None
    
    def parse_yaml_content(self, content):
        """Parse YAML content to extract model and prompt info"""
        try:
            data = yaml.safe_load(content)
            if isinstance(data, dict):
                results = []
                for key, value in data.items():
                    if isinstance(value, dict) and 'model' in value and 'prompt' in value:
                        results.append({
                            'usecase': key,
                            'model': value.get('model', ''),
                            'prompt': value.get('prompt', '').strip(),
                            'enabled': value.get('enabled', True),
                            'temperature': value.get('temperature'),
                            'top_k': value.get('top_k'),
                            'top_p': value.get('top_p'),
                            'max_tokens': value.get('max_tokens')
                        })
                return results
        except Exception as e:
            logging.error(f"Error parsing YAML: {e}")
        return []
    
    def scan_history(self):
        """Scan git history for changes"""
        self.changes_history = []
        
        for file_path in self.tracked_files:
            if not os.path.exists(os.path.join(self.repo_path, file_path)):
                continue
                
            commits = self.get_git_log(file_path)
            environment = "test" if "test" in file_path else "prod"
            
            # Track the last known state of each use case
            usecase_last_state = {}
            
            # Process commits in reverse order (oldest first) to build proper history
            for commit_line in reversed(commits):
                if not commit_line.strip():
                    continue
                    
                commit_hash = commit_line.split()[0]
                commit_info = self.get_commit_info(commit_hash)
                
                if not commit_info:
                    continue
                
                content = self.get_file_content_at_commit(commit_hash, file_path)
                if not content:
                    continue
                
                yaml_data = self.parse_yaml_content(content)
                
                # For each use case in this commit, check if it actually changed
                for item in yaml_data:
                    usecase = item['usecase']
                    current_data = {
                        'model': item['model'],
                        'prompt': item['prompt'],
                        'enabled': item['enabled'],
                        'temperature': item['temperature'],
                        'top_k': item['top_k'],
                        'top_p': item['top_p'],
                        'max_tokens': item['max_tokens']
                    }
                    
                    # Check if this use case actually changed from its last known state
                    has_changed = True
                    if usecase in usecase_last_state:
                        has_changed = current_data != usecase_last_state[usecase]['data']
                        # Debug logging
                        if has_changed:
                            logging.info(f"Change detected for {usecase} in commit {commit_hash}")
                        else:
                            logging.info(f"No change for {usecase} in commit {commit_hash}, skipping")
                    else:
                        logging.info(f"First occurrence of {usecase} in commit {commit_hash}")
                    
                    # Only add to history if it changed (or it's the first time we see this use case)
                    # In test mode, show all commits regardless of changes
                    test_mode = os.getenv('TEST_MODE', 'false').lower() == 'true'
                    if has_changed or test_mode:
                        # Check for duplicates before adding
                        duplicate_exists = any(
                            change['commit_hash'] == commit_hash and 
                            change['usecase'] == usecase and 
                            change['environment'] == environment
                            for change in self.changes_history
                        )
                        
                        if not duplicate_exists:
                            # Check if S3 evaluation results exist for this commit/usecase
                            has_eval_results = self.check_s3_file_exists(commit_hash, item['usecase'])
                            eval_results_url = self.generate_s3_eval_url(commit_hash, item['usecase']) if has_eval_results else None
                            # Generate direct view URL for HTML content
                            eval_direct_url = f"/eval/{commit_hash}" if has_eval_results else None

                            self.changes_history.append({
                                'environment': environment,
                                'usecase': item['usecase'],
                                'model': item['model'],
                                'prompt': item['prompt'],
                                'enabled': item['enabled'],
                                'temperature': item['temperature'],
                                'top_k': item['top_k'],
                                'top_p': item['top_p'],
                                'max_tokens': item['max_tokens'],
                                'commit_hash': commit_hash,
                                'commit_date': commit_info['date'],
                                'commit_message': commit_info['message'],
                                'commit_author_name': commit_info['author_name'],
                                'commit_author_email': commit_info['author_email'],
                                'file_path': file_path,
                                'has_eval_results': has_eval_results,
                                'eval_results_url': eval_results_url,
                                'eval_direct_url': eval_direct_url
                            })
                            logging.info(f"Added change entry for {usecase} in commit {commit_hash}")
                        else:
                            logging.warning(f"Duplicate entry detected for {usecase} in commit {commit_hash}, skipping")
                    
                    # Update the last known state for this use case
                    usecase_last_state[usecase] = {
                        'data': current_data,
                        'commit_hash': commit_hash,
                        'commit_date': commit_info['date']
                    }
        
        # Sort by commit date (newest first)
        self.changes_history.sort(key=lambda x: x['commit_date'], reverse=True)
        
        # Set enabled flag only for the latest prompt of each usecase/environment combination
        self._set_enabled_flags()
        
        # Force refresh S3 status to catch any recently uploaded files
        if self.s3_client and self.changes_history:
            self.refresh_s3_status()
        
        logging.info(f"Found {len(self.changes_history)} changes in history")
    
    def _set_enabled_flags(self):
        """Set show_enabled flag only for the latest prompt of each usecase/environment combination"""
        # Track the latest entry for each usecase/environment combination
        latest_entries = {}
        
        for change in self.changes_history:
            key = f"{change['usecase']}-{change['environment']}"
            if key not in latest_entries:
                latest_entries[key] = change
            else:
                # Compare dates to find the latest
                if change['commit_date'] > latest_entries[key]['commit_date']:
                    latest_entries[key] = change
        
        # Set show_enabled flag to control badge display
        for change in self.changes_history:
            key = f"{change['usecase']}-{change['environment']}"
            if change == latest_entries[key] and change['enabled']:
                # Only show enabled badge for latest entries that are actually enabled
                change['show_enabled'] = True
            else:
                # Don't show any badge for older entries
                change['show_enabled'] = False
    
    def check_s3_file_exists(self, commit_hash, usecase):
        """Check if S3 evaluation results file exists for the given commit and usecase"""
        if not self.s3_client:
            return False
            
        try:
            # Construct the S3 key: commit_hash/usecase_results.html
            s3_key = f"{commit_hash}/{usecase}_results.html"
            
            # Check if file exists using head_object
            self.s3_client.head_object(Bucket=self.s3_bucket_name, Key=s3_key)
            return True
            
        except ClientError as e:
            if e.response["Error"]["Code"] == "404":
                return False
            else:
                logging.error(f"Error checking S3 file {s3_key}: {e}")
                return False
        except Exception as e:
            logging.error(f"Unexpected error checking S3 file: {e}")
            return False
    
    def generate_s3_eval_url(self, commit_hash, usecase):
        """Generate the MinIO UI URL for the evaluation results file"""
        if not self.s3_ui_url:
            return None

        # Construct the MinIO UI URL
        s3_key = f"{commit_hash}/{usecase}_results.html"
        return f"{self.s3_ui_url}/browser/{self.s3_bucket_name}/{s3_key}"

    def get_s3_file_content(self, commit_hash, usecase):
        """Get the content of an S3 file directly"""
        if not self.s3_client:
            return None

        # Try different possible file patterns
        possible_keys = [
            f"{commit_hash}/{usecase}_results.html",  # KFP evaluation results
            f"{commit_hash}/{usecase}.html",          # Direct HTML files
            f"{commit_hash}/benchmark-results.html",  # GuideLL​M benchmark (if usecase is guidellm-benchmark)
        ]
        
        # If usecase contains 'guidellm' or is a benchmark, also try benchmark patterns
        if 'guidellm' in usecase.lower() or usecase == 'guidellm-benchmark':
            possible_keys.extend([
                f"guidellm-benchmarks/{commit_hash}/benchmark-results.html",
                f"guidellm-benchmarks/{commit_hash}/{usecase}.html",
            ])

        for s3_key in possible_keys:
            try:
                response = self.s3_client.get_object(Bucket=self.s3_bucket_name, Key=s3_key)
                return response['Body'].read().decode('utf-8')
            except ClientError as e:
                if e.response["Error"]["Code"] == "NoSuchKey":
                    continue  # Try next key pattern
                else:
                    logging.error(f"Error getting S3 file {s3_key}: {e}")
                    continue
            except Exception as e:
                logging.error(f"Unexpected error getting S3 file {s3_key}: {e}")
                continue
        
        logging.warning(f"No S3 file found for commit {commit_hash}, usecase {usecase}")
        return None
    
    def list_s3_files(self, prefix=""):
        """List all files in S3 bucket with optional prefix"""
        if not self.s3_client:
            return []
            
        try:
            response = self.s3_client.list_objects_v2(
                Bucket=self.s3_bucket_name,
                Prefix=prefix
            )
            
            files = []
            if 'Contents' in response:
                for obj in response['Contents']:
                    files.append(obj['Key'])
            
            return files
            
        except ClientError as e:
            logging.error(f"Error listing S3 files: {e}")
            return []
        except Exception as e:
            logging.error(f"Unexpected error listing S3 files: {e}")
            return []
    
    def list_html_files_for_commit(self, commit_hash):
        """List all HTML files available for a specific commit hash"""
        if not self.s3_client:
            return []
            
        try:
            html_files = []
            
            # Check both regular structure and GuideLL​M structure
            prefixes_to_check = [
                f"{commit_hash}/",                    # Regular KFP evaluation results
                f"guidellm-benchmarks/{commit_hash}/", # GuideLL​M benchmark results
            ]
            
            for prefix in prefixes_to_check:
                files = self.list_s3_files(prefix)
                
                for file_key in files:
                    if file_key.endswith('.html'):
                        # Extract filename from the path
                        filename = file_key.split('/')[-1]
                        
                        # Handle different naming patterns
                        if filename.endswith('_results.html'):
                            # KFP evaluation results: summarize_results.html -> summarize
                            usecase = filename.replace('_results.html', '')
                            file_type = 'evaluation'
                        elif filename.startswith('benchmark-results') or 'benchmark-results' in filename:
                            # GuideLL​M benchmark results: benchmark-results.html or summarize-benchmark-results.html
                            if 'benchmark-results' in filename and not filename.startswith('benchmark-results'):
                                # Extract usecase from files like "summarize-benchmark-results.html"
                                usecase = filename.replace('-benchmark-results.html', '')
                            else:
                                usecase = 'guidellm-benchmark'
                            file_type = 'benchmark'
                        elif filename.startswith('guidellm') or 'guidellm' in filename.lower():
                            # Other GuideLL​M files
                            usecase = filename.replace('.html', '')
                            file_type = 'benchmark'
                        else:
                            # Generic HTML files
                            usecase = filename.replace('.html', '')
                            file_type = 'other'
                        
                        # Avoid duplicates (in case same file appears in both structures)
                        if not any(f['usecase'] == usecase and f['filename'] == filename for f in html_files):
                            html_files.append({
                                'usecase': usecase,
                                'filename': filename,
                                'file_key': file_key,
                                'file_type': file_type,
                                'display_name': self._generate_display_name(usecase, file_type)
                            })
            
            # Sort by file type and usecase
            html_files.sort(key=lambda x: (x['file_type'], x['usecase']))
            return html_files
            
        except Exception as e:
            logging.error(f"Error listing HTML files for commit {commit_hash}: {e}")
            return []
    
    def _generate_display_name(self, usecase, file_type):
        """Generate a user-friendly display name for the HTML file"""
        if file_type == 'evaluation':
            # KFP evaluation results
            usecase_display = usecase.replace('_', ' ').title()
            return f"📊 {usecase_display} Evaluation Results"
        elif file_type == 'benchmark':
            # GuideLL​M benchmark results
            if usecase == 'guidellm-benchmark':
                return "⚡ GuideLL​M Performance Benchmark"
            else:
                return f"⚡ {usecase.replace('_', ' ').title()} Benchmark"
        else:
            # Other HTML files
            return f"📄 {usecase.replace('_', ' ').title()}"
    
    def refresh_s3_status(self):
        """Refresh S3 evaluation results status for all existing changes"""
        if not self.s3_client:
            logging.warning("S3 client not available, skipping S3 status refresh")
            return 0
            
        # List all files to check availability
        all_files = self.list_s3_files()
        
        updated_count = 0
        
        for change in self.changes_history:
            commit_hash = change['commit_hash']
            usecase = change['usecase']
            
            # Check current S3 status
            has_eval_results = self.check_s3_file_exists(commit_hash, usecase)
            eval_results_url = self.generate_s3_eval_url(commit_hash, usecase) if has_eval_results else None
            eval_direct_url = f"/eval/{commit_hash}" if has_eval_results else None

            # Update if status changed
            if change.get('has_eval_results') != has_eval_results:
                change['has_eval_results'] = has_eval_results
                change['eval_results_url'] = eval_results_url
                change['eval_direct_url'] = eval_direct_url
                updated_count += 1
        return updated_count
    
    def cleanup(self):
        """Clean up temporary repository directory"""
        if self.git_repo_url and hasattr(self, 'repo_path') and self.repo_path != "." and os.path.exists(self.repo_path):
            try:
                logging.info(f"Cleaning up repository directory: {self.repo_path}")
                shutil.rmtree(self.repo_path)
            except Exception as e:
                logging.warning(f"Failed to cleanup repository directory: {e}")
    
    def check_for_new_commits(self):
        """Check if there are new commits"""
        try:
            # Set environment variables for git to avoid config issues
            env = os.environ.copy()
            env['GIT_CONFIG_NOSYSTEM'] = '1'
            env['HOME'] = tempfile.gettempdir()
            
            cmd = ["git", "rev-parse", "HEAD"]
            result = subprocess.run(cmd, cwd=self.repo_path, capture_output=True, text=True, env=env, encoding='utf-8', errors='replace')
            current_hash = result.stdout.strip()
            
            if self.last_commit_hash != current_hash:
                self.last_commit_hash = current_hash
                return True
            return False
        except Exception as e:
            logging.error(f"Error checking for new commits: {e}")
            return False
    
    def monitor_loop(self):
        """Continuous monitoring loop"""
        self.scan_history()
        
        while True:
            try:
                current_time = time.time()
                
                # Pull latest changes
                if self._git_pull():
                    if self.check_for_new_commits():
                        logging.info("New commits detected, rescanning history...")
                        self.scan_history()
                else:
                    logging.warning("Failed to pull latest changes")
                
                # Check if it's time to refresh S3 status
                if (current_time - self.last_s3_refresh) >= self.s3_refresh_interval:
                    if self.s3_client and self.changes_history:
                        logging.info("Performing periodic S3 status refresh...")
                        self.refresh_s3_status()
                        self.last_s3_refresh = current_time
                
                time.sleep(self.monitor_interval)
            except Exception as e:
                logging.error(f"Error in monitor loop: {e}")
                time.sleep(60)

# Global monitor instances (can be configured per request)
monitors = {}

# User-based configuration templates
USER_CONFIG_TEMPLATE = {
    'git_repo_url': 'https://gitea-gitea.{cluster_domain}/{user}/canopy-be.git',
    'git_username': '{user}',
    'git_password': 'thisisthepassword',
    'git_branch': 'main',
    'monitor_interval': '30',
    's3_endpoint': 'https://minio-api-{user}-toolings.{cluster_domain}',
    's3_access_key': '{user}',
    's3_secret_key': 'thisisthepassword',
    's3_bucket_name': 'test-results',
    's3_ui_url': 'https://minio-ui-{user}-toolings.{cluster_domain}',
    's3_refresh_interval': '60'
}

def get_user_config(user, cluster_domain):
    """Generate user-specific configuration"""
    config = {}
    for key, value in USER_CONFIG_TEMPLATE.items():
        config[key] = value.format(user=user, cluster_domain=cluster_domain)
    return config

def get_or_create_monitor(config_key):
    """Get or create a monitor instance based on configuration"""
    if config_key not in monitors:
        # Extract configuration from URL parameters
        config = {}
        if request.args.get('git_repo_url'):
            config['git_repo_url'] = request.args.get('git_repo_url')
        if request.args.get('git_username'):
            config['git_username'] = request.args.get('git_username')
        if request.args.get('git_password'):
            config['git_password'] = request.args.get('git_password')
        if request.args.get('git_branch'):
            config['git_branch'] = request.args.get('git_branch')
        if request.args.get('monitor_interval'):
            config['monitor_interval'] = request.args.get('monitor_interval')
        
        # Extract S3 configuration from URL parameters
        if request.args.get('s3_endpoint'):
            config['s3_endpoint'] = request.args.get('s3_endpoint')
        if request.args.get('s3_access_key'):
            config['s3_access_key'] = request.args.get('s3_access_key')
        if request.args.get('s3_secret_key'):
            config['s3_secret_key'] = request.args.get('s3_secret_key')
        if request.args.get('s3_bucket_name'):
            config['s3_bucket_name'] = request.args.get('s3_bucket_name')
        if request.args.get('s3_ui_url'):
            config['s3_ui_url'] = request.args.get('s3_ui_url')
        if request.args.get('s3_refresh_interval'):
            config['s3_refresh_interval'] = request.args.get('s3_refresh_interval')
        
        monitor = GitMonitor(config if config else None)
        # Scan history immediately for URL parameter configurations
        if config and config.get('git_repo_url'):
            monitor.scan_history()
            # Start background monitoring thread for this configuration
            monitor_thread = Thread(target=monitor.monitor_loop, daemon=True)
            monitor_thread.start()
            logging.info(f"Started monitoring thread for config: {config_key}")
        monitors[config_key] = monitor
    return monitors[config_key]

@app.route('/')
def index():
    """Main page"""
    # Get configuration from URL parameters
    config_params = {
        'git_repo_url': request.args.get('git_repo_url', ''),
        'git_username': request.args.get('git_username', ''),
        'git_branch': request.args.get('git_branch', 'main'),
        'monitor_interval': request.args.get('monitor_interval', '30')
    }
    return render_template('index.html', config=config_params)

@app.route('/api/changes')
def get_changes():
    """API endpoint to get changes"""
    config_key = f"{request.args.get('git_repo_url', '')}-{request.args.get('git_branch', 'main')}"
    monitor = get_or_create_monitor(config_key)
    return jsonify(monitor.changes_history)

@app.route('/api/refresh')
def refresh_changes():
    """API endpoint to manually refresh changes"""
    config_key = f"{request.args.get('git_repo_url', '')}-{request.args.get('git_branch', 'main')}"
    monitor = get_or_create_monitor(config_key)
    
    # Pull latest changes from repository
    if monitor.git_repo_url:
        try:
            if monitor._git_pull():
                logging.info("Successfully pulled latest changes")
            else:
                logging.warning("Failed to pull latest changes")
        except Exception as e:
            logging.error(f"Error pulling changes: {e}")
    
    # Scan history for changes
    monitor.scan_history()
    
    # Also refresh S3 status if S3 client is available
    s3_updated_count = 0
    if monitor.s3_client:
        s3_updated_count = monitor.refresh_s3_status()
        monitor.last_s3_refresh = time.time()
    
    return jsonify({
        "status": "refreshed", 
        "count": len(monitor.changes_history),
        "s3_updated": s3_updated_count
    })

@app.route('/user<int:user_id>/<cluster_domain>')
def user_config(user_id, cluster_domain):
    """User-specific configuration endpoint with cluster domain"""
    user = f"user{user_id}"
    config = get_user_config(user, cluster_domain)
    
    
    # Create monitor with user-specific configuration
    config_key = f"{config['git_repo_url']}-{config['git_branch']}"
    
    if config_key not in monitors:
        monitor = GitMonitor(config)
        monitor.scan_history()
        # Start background monitoring thread
        monitor_thread = Thread(target=monitor.monitor_loop, daemon=True)
        monitor_thread.start()
        logging.info(f"Started monitoring thread for user: {user} on cluster: {cluster_domain}")
        monitors[config_key] = monitor
    
    return render_template('index.html', config=config)

@app.route('/user<int:user_id>')
def user_config_legacy(user_id):
    """Legacy user-specific configuration endpoint (backwards compatibility)"""
    # Default cluster domain for backwards compatibility
    cluster_domain = "apps.cluster-gm86c.gm86c.sandbox1062.opentlc.com"
    return user_config(user_id, cluster_domain)

@app.route('/user<int:user_id>/<cluster_domain>/api/changes')
def get_user_changes(user_id, cluster_domain):
    """API endpoint to get changes for specific user with cluster domain"""
    user = f"user{user_id}"
    config = get_user_config(user, cluster_domain)
    config_key = f"{config['git_repo_url']}-{config['git_branch']}"
    
    if config_key not in monitors:
        monitor = GitMonitor(config)
        monitor.scan_history()
        # Start background monitoring thread
        monitor_thread = Thread(target=monitor.monitor_loop, daemon=True)
        monitor_thread.start()
        logging.info(f"Started monitoring thread for user: {user} on cluster: {cluster_domain}")
        monitors[config_key] = monitor
    
    monitor = monitors[config_key]
    return jsonify(monitor.changes_history)

@app.route('/user<int:user_id>/api/changes')
def get_user_changes_legacy(user_id):
    """Legacy API endpoint to get changes for specific user (backwards compatibility)"""
    cluster_domain = "apps.cluster-gm86c.gm86c.sandbox1062.opentlc.com"
    return get_user_changes(user_id, cluster_domain)

@app.route('/user<int:user_id>/<cluster_domain>/api/refresh')
def refresh_user_changes(user_id, cluster_domain):
    """API endpoint to manually refresh changes for specific user with cluster domain"""
    user = f"user{user_id}"
    config = get_user_config(user, cluster_domain)
    config_key = f"{config['git_repo_url']}-{config['git_branch']}"
    
    if config_key not in monitors:
        monitor = GitMonitor(config)
        monitors[config_key] = monitor
    else:
        monitor = monitors[config_key]
    
    # Pull latest changes from repository
    if monitor.git_repo_url:
        try:
            if monitor._git_pull():
                logging.info("Successfully pulled latest changes")
            else:
                logging.warning("Failed to pull latest changes")
        except Exception as e:
            logging.error(f"Error pulling changes: {e}")
    
    # Scan history for changes
    monitor.scan_history()
    
    # Also refresh S3 status if S3 client is available
    s3_updated_count = 0
    if monitor.s3_client:
        s3_updated_count = monitor.refresh_s3_status()
        monitor.last_s3_refresh = time.time()
    
    return jsonify({
        "status": "refreshed", 
        "count": len(monitor.changes_history),
        "s3_updated": s3_updated_count
    })

@app.route('/user<int:user_id>/api/refresh')
def refresh_user_changes_legacy(user_id):
    """Legacy API endpoint to manually refresh changes for specific user (backwards compatibility)"""
    cluster_domain = "apps.cluster-gm86c.gm86c.sandbox1062.opentlc.com"
    return refresh_user_changes(user_id, cluster_domain)

@app.route('/user<int:user_id>/<cluster_domain>/api/s3-debug')
def debug_s3_connection(user_id, cluster_domain):
    """Debug S3 connection and file listing"""
    user = f"user{user_id}"
    config = get_user_config(user, cluster_domain)
    config_key = f"{config['git_repo_url']}-{config['git_branch']}"
    
    if config_key not in monitors:
        monitor = GitMonitor(config)
        monitors[config_key] = monitor
    else:
        monitor = monitors[config_key]
    
    debug_info = {
        "s3_endpoint": monitor.s3_endpoint,
        "s3_bucket_name": monitor.s3_bucket_name,
        "s3_ui_url": monitor.s3_ui_url,
        "s3_client_initialized": monitor.s3_client is not None,
        "s3_files": [],
        "error": None
    }
    
    if monitor.s3_client:
        try:
            # Test basic connectivity
            debug_info["s3_files"] = monitor.list_s3_files()
            debug_info["total_files"] = len(debug_info["s3_files"])
            
            # Test specific file patterns
            debug_info["file_patterns"] = {}
            for file_key in debug_info["s3_files"]:
                if "_results.html" in file_key:
                    debug_info["file_patterns"][file_key] = "evaluation_result"
                    
        except Exception as e:
            debug_info["error"] = str(e)
    else:
        debug_info["error"] = "S3 client not initialized"
    
    return jsonify(debug_info)

@app.route('/user<int:user_id>/api/s3-debug')
def debug_s3_connection_legacy(user_id):
    """Legacy debug S3 connection endpoint"""
    cluster_domain = "apps.cluster-gm86c.gm86c.sandbox1062.opentlc.com"
    return debug_s3_connection(user_id, cluster_domain)

@app.route('/user<int:user_id>/<cluster_domain>/api/s3-refresh')
def force_s3_refresh(user_id, cluster_domain):
    """Force S3 status refresh for user"""
    user = f"user{user_id}"
    config = get_user_config(user, cluster_domain)
    config_key = f"{config['git_repo_url']}-{config['git_branch']}"
    
    if config_key not in monitors:
        return jsonify({"error": "Monitor not found for this user"}), 404
    
    monitor = monitors[config_key]
    
    if not monitor.s3_client:
        return jsonify({"error": "S3 client not initialized"}), 400
    
    # Force refresh S3 status
    updated_count = monitor.refresh_s3_status()
    monitor.last_s3_refresh = time.time()
    
    return jsonify({
        "status": "success",
        "message": f"S3 refresh completed",
        "updated_count": updated_count,
        "total_changes": len(monitor.changes_history)
    })

@app.route('/user<int:user_id>/api/s3-refresh')
def force_s3_refresh_legacy(user_id):
    """Legacy force S3 refresh endpoint"""
    cluster_domain = "apps.cluster-gm86c.gm86c.sandbox1062.opentlc.com"
    return force_s3_refresh(user_id, cluster_domain)

@app.route('/user<int:user_id>/<cluster_domain>/eval/<commit_hash>')
def select_eval_results(user_id, cluster_domain, commit_hash):
    """Show selection page for available evaluation results"""
    user = f"user{user_id}"
    config = get_user_config(user, cluster_domain)
    config_key = f"{config['git_repo_url']}-{config['git_branch']}"

    if config_key not in monitors:
        monitor = GitMonitor(config)
        monitors[config_key] = monitor
    else:
        monitor = monitors[config_key]

    if not monitor.s3_client:
        return "S3 client not available", 503

    # Get list of available HTML files for this commit
    html_files = monitor.list_html_files_for_commit(commit_hash)

    if not html_files:
        return f"No evaluation results found for commit {commit_hash}", 404

    # If only one file available, redirect directly to it
    if len(html_files) == 1:
        file_info = html_files[0]
        return redirect(f"/user{user_id}/{cluster_domain}/eval/{commit_hash}/{file_info['usecase']}")

    # Render selection page with multiple options
    return render_template('results_selection.html', 
                         html_files=html_files, 
                         commit_hash=commit_hash,
                         user_id=user_id,
                         cluster_domain=cluster_domain)

@app.route('/user<int:user_id>/<cluster_domain>/eval/<commit_hash>/<usecase>')
def view_eval_results(user_id, cluster_domain, commit_hash, usecase):
    """Serve evaluation results HTML directly"""
    user = f"user{user_id}"
    config = get_user_config(user, cluster_domain)
    config_key = f"{config['git_repo_url']}-{config['git_branch']}"

    if config_key not in monitors:
        monitor = GitMonitor(config)
        monitors[config_key] = monitor
    else:
        monitor = monitors[config_key]

    if not monitor.s3_client:
        return "S3 client not available", 503

    # Get the HTML content from S3
    html_content = monitor.get_s3_file_content(commit_hash, usecase)

    if html_content is None:
        return f"Evaluation results not found for commit {commit_hash} and usecase {usecase}", 404

    return Response(html_content, mimetype='text/html')

@app.route('/user<int:user_id>/eval/<commit_hash>')
def select_eval_results_legacy(user_id, commit_hash):
    """Legacy endpoint for selecting evaluation results"""
    cluster_domain = "apps.cluster-gm86c.gm86c.sandbox1062.opentlc.com"
    return select_eval_results(user_id, cluster_domain, commit_hash)

@app.route('/user<int:user_id>/eval/<commit_hash>/<usecase>')
def view_eval_results_legacy(user_id, commit_hash, usecase):
    """Legacy endpoint for viewing evaluation results"""
    cluster_domain = "apps.cluster-gm86c.gm86c.sandbox1062.opentlc.com"
    return view_eval_results(user_id, cluster_domain, commit_hash, usecase)


if __name__ == '__main__':
    # For standalone execution, use environment variables
    default_monitor = GitMonitor()
    
    # Start monitoring in background thread
    monitor_thread = Thread(target=default_monitor.monitor_loop, daemon=True)
    monitor_thread.start()
    
    # Start Flask app
    app.run(host='0.0.0.0', port=5000, debug=True)