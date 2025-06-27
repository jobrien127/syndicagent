#!/usr/bin/env python3
"""
Agworld Reporter - Application Entry Point

This script provides different ways to run the application:
- Web server (FastAPI)
- Celery worker
- Celery beat scheduler
- Combined mode (all services)
"""

import sys
import argparse
import uvicorn
import subprocess
from pathlib import Path

def run_server(host: str = "0.0.0.0", port: int = 8000, reload: bool = True):
    """Run the FastAPI web server"""
    print(f"🚀 Starting Agworld Reporter web server on {host}:{port}")
    uvicorn.run(
        "app.main:app",
        host=host,
        port=port,
        reload=reload,
        log_level="info"
    )

def run_celery_worker():
    """Run Celery worker"""
    print("🔧 Starting Celery worker...")
    subprocess.run([
        "celery", "-A", "app.tasks.worker", "worker",
        "--loglevel=info",
        "--concurrency=4"
    ])

def run_celery_beat():
    """Run Celery beat scheduler"""
    print("⏰ Starting Celery beat scheduler...")
    subprocess.run([
        "celery", "-A", "app.tasks.worker", "beat",
        "--loglevel=info"
    ])

def run_all_services():
    """Run all services together (development mode)"""
    print("🎯 Starting all Agworld Reporter services...")
    print("Note: In production, run these services separately!")
    
    import multiprocessing
    import time
    
    # Start web server
    server_process = multiprocessing.Process(
        target=run_server,
        kwargs={"reload": False}
    )
    server_process.start()
    
    # Give server time to start
    time.sleep(3)
    
    # Start Celery worker
    worker_process = multiprocessing.Process(target=run_celery_worker)
    worker_process.start()
    
    # Start Celery beat
    beat_process = multiprocessing.Process(target=run_celery_beat)
    beat_process.start()
    
    try:
        # Wait for processes
        server_process.join()
        worker_process.join()
        beat_process.join()
    except KeyboardInterrupt:
        print("\n🛑 Shutting down services...")
        server_process.terminate()
        worker_process.terminate()
        beat_process.terminate()

def main():
    parser = argparse.ArgumentParser(description="Agworld Reporter Application")
    parser.add_argument(
        "mode",
        choices=["server", "worker", "beat", "all"],
        help="Service mode to run"
    )
    parser.add_argument(
        "--host",
        default="0.0.0.0",
        help="Host for web server (default: 0.0.0.0)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port for web server (default: 8000)"
    )
    parser.add_argument(
        "--no-reload",
        action="store_true",
        help="Disable auto-reload for development"
    )
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("🌾 Agworld Reporter")
    print("=" * 60)
    
    if args.mode == "server":
        run_server(
            host=args.host,
            port=args.port,
            reload=not args.no_reload
        )
    elif args.mode == "worker":
        run_celery_worker()
    elif args.mode == "beat":
        run_celery_beat()
    elif args.mode == "all":
        run_all_services()

if __name__ == "__main__":
    main()
