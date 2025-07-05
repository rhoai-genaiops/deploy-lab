#!/usr/bin/env python3
"""
Run script for Git Monitor with environment variable support
"""

import os
from dotenv import load_dotenv
from git_monitor import app, GitMonitor
from threading import Thread
import logging

# Load environment variables from .env file if it exists
load_dotenv()

def main():
    """Main function to start the Git Monitor"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Print configuration
    print("🔍 Git Monitor Configuration:")
    print(f"  Repository URL: {os.getenv('GIT_REPO_URL', 'Current directory')}")
    print(f"  Branch: {os.getenv('GIT_BRANCH', 'main')}")
    print(f"  Monitor Interval: {os.getenv('MONITOR_INTERVAL', '30')} seconds")
    print(f"  Flask Host: {os.getenv('FLASK_HOST', '0.0.0.0')}")
    print(f"  Flask Port: {os.getenv('FLASK_PORT', '5000')}")
    print()
    
    try:
        # Create default monitor instance for standalone execution
        default_monitor = GitMonitor()
        
        # Start monitoring in background thread
        monitor_thread = Thread(target=default_monitor.monitor_loop, daemon=True)
        monitor_thread.start()
        
        # Get Flask configuration
        host = os.getenv('FLASK_HOST', '0.0.0.0')
        port = int(os.getenv('FLASK_PORT', '5001'))
        debug = os.getenv('FLASK_DEBUG', 'false').lower() == 'true'
        
        print(f"🚀 Starting web server at http://{host}:{port}")
        print("   Press Ctrl+C to stop")
        print()
        
        # Start Flask app
        app.run(host=host, port=port, debug=debug)
        
    except KeyboardInterrupt:
        print("\n👋 Shutting down Git Monitor...")
    except Exception as e:
        print(f"❌ Error starting Git Monitor: {e}")
        logging.error(f"Error starting Git Monitor: {e}")

if __name__ == '__main__':
    main()