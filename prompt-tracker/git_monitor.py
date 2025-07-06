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
from flask import Flask, render_template, jsonify, request
from threading import Thread
import time
import logging
import shutil
from urllib.parse import urlparse
import tempfile

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
        
        # Set up repository path
        if self.git_repo_url:
            self.repo_path = self._setup_external_repo()
        else:
            self.repo_path = "."
            
        self.tracked_files = ["chart/values-test.yaml", "chart/values-prod.yaml"]
        self.changes_history = []
        self.last_commit_hash = None
        
        logging.info(f"Initialized GitMonitor with repo_path: {self.repo_path}")
        logging.info(f"Monitoring interval: {self.monitor_interval} seconds")
        logging.info(f"Git branch: {self.git_branch}")
        
    def _setup_external_repo(self):
        """Set up external Git repository with authentication"""
        try:
            # Create a temporary directory for the repo
            repo_dir = os.path.join(tempfile.gettempdir(), "git_monitor_repo")
            
            # Clean up existing directory if it exists
            if os.path.exists(repo_dir):
                shutil.rmtree(repo_dir)
            
            # Construct authenticated URL if credentials are provided
            if self.git_username and self.git_password:
                parsed_url = urlparse(self.git_repo_url)
                auth_url = f"{parsed_url.scheme}://{self.git_username}:{self.git_password}@{parsed_url.netloc}{parsed_url.path}"
                logging.info(f"Using authenticated URL for repository")
            else:
                auth_url = self.git_repo_url
                logging.info(f"Using non-authenticated URL for repository")
            
            # Clone the repository
            logging.info(f"Cloning repository to {repo_dir}")
            clone_cmd = ["git", "clone", "-b", self.git_branch, auth_url, repo_dir]
            result = subprocess.run(clone_cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                logging.error(f"Failed to clone repository: {result.stderr}")
                raise Exception(f"Git clone failed: {result.stderr}")
            
            logging.info(f"Successfully cloned repository to {repo_dir}")
            return repo_dir
            
        except Exception as e:
            logging.error(f"Error setting up external repository: {e}")
            raise
    
    def _git_pull(self):
        """Pull latest changes from remote repository"""
        if not self.git_repo_url:
            # For local repo, just fetch
            try:
                subprocess.run(["git", "fetch"], cwd=self.repo_path, capture_output=True, check=True)
                return True
            except subprocess.CalledProcessError as e:
                logging.error(f"Git fetch failed: {e}")
                return False
        
        try:
            # For external repo, pull latest changes
            pull_cmd = ["git", "pull", "origin", self.git_branch]
            result = subprocess.run(pull_cmd, cwd=self.repo_path, capture_output=True, text=True)
            
            if result.returncode != 0:
                logging.error(f"Git pull failed: {result.stderr}")
                return False
            
            logging.info("Successfully pulled latest changes")
            return True
            
        except Exception as e:
            logging.error(f"Error during git pull: {e}")
            return False
        
    def get_git_log(self, file_path):
        """Get git log for a specific file"""
        try:
            cmd = ["git", "log", "--oneline", "--follow", "--", file_path]
            result = subprocess.run(cmd, cwd=self.repo_path, capture_output=True, text=True)
            return result.stdout.strip().split('\n') if result.stdout.strip() else []
        except Exception as e:
            logging.error(f"Error getting git log for {file_path}: {e}")
            return []
    
    def get_file_content_at_commit(self, commit_hash, file_path):
        """Get file content at specific commit"""
        try:
            cmd = ["git", "show", f"{commit_hash}:{file_path}"]
            result = subprocess.run(cmd, cwd=self.repo_path, capture_output=True, text=True)
            return result.stdout if result.returncode == 0 else None
        except Exception as e:
            logging.error(f"Error getting file content at {commit_hash}: {e}")
            return None
    
    def get_commit_info(self, commit_hash):
        """Get commit information"""
        try:
            cmd = ["git", "show", "--format=%H|%ai|%s|%an|%ae", "--no-patch", commit_hash]
            result = subprocess.run(cmd, cwd=self.repo_path, capture_output=True, text=True)
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
            
            for commit_line in commits:
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
                
                for item in yaml_data:
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
                        'file_path': file_path
                    })
        
        # Sort by commit date (newest first)
        self.changes_history.sort(key=lambda x: x['commit_date'], reverse=True)
        logging.info(f"Found {len(self.changes_history)} changes in history")
    
    def check_for_new_commits(self):
        """Check if there are new commits"""
        try:
            cmd = ["git", "rev-parse", "HEAD"]
            result = subprocess.run(cmd, cwd=self.repo_path, capture_output=True, text=True)
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
                # Pull latest changes
                if self._git_pull():
                    if self.check_for_new_commits():
                        logging.info("New commits detected, rescanning history...")
                        self.scan_history()
                else:
                    logging.warning("Failed to pull latest changes")
                
                time.sleep(self.monitor_interval)
            except Exception as e:
                logging.error(f"Error in monitor loop: {e}")
                time.sleep(60)

# Global monitor instances (can be configured per request)
monitors = {}

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
        
        monitors[config_key] = GitMonitor(config if config else None)
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
    monitor.scan_history()
    return jsonify({"status": "refreshed", "count": len(monitor.changes_history)})

if __name__ == '__main__':
    # For standalone execution, use environment variables
    default_monitor = GitMonitor()
    
    # Start monitoring in background thread
    monitor_thread = Thread(target=default_monitor.monitor_loop, daemon=True)
    monitor_thread.start()
    
    # Start Flask app
    app.run(host='0.0.0.0', port=5000, debug=True)