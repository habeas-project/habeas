#!/usr/bin/env python3
"""
Celery Worker Startup Script

This script starts the Celery worker for processing background tasks.
Run this script to start processing emergency notification jobs.

Usage:
    python run_celery_worker.py

Environment Variables:
    CELERY_BROKER_URL: Redis broker URL (default: redis://localhost:6379/0)
    CELERY_RESULT_BACKEND: Redis result backend URL (default: redis://localhost:6379/0)
"""

import os
import sys

from pathlib import Path

# Add the app directory to Python path
app_dir = Path(__file__).parent / "app"
sys.path.insert(0, str(app_dir))

# Import after path setup (noqa: E402)
from app.celery_app import celery_app


def main():
    """Start the Celery worker"""
    print("Starting Celery worker for Habeas emergency notification system...")
    print(f"Broker URL: {os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/0')}")
    print(f"Result Backend: {os.getenv('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')}")

    # Start worker with both default and priority queues
    celery_app.worker_main(
        [
            "worker",
            "--loglevel=info",
            "--queues=default,priority",
            "--concurrency=2",  # Process 2 tasks at once
            "--hostname=habeas-worker@%h",
        ]
    )


if __name__ == "__main__":
    main()
