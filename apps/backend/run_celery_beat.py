#!/usr/bin/env python3
"""
Celery Beat Scheduler Startup Script

This script starts the Celery Beat scheduler for scheduling periodic tasks.
Run this script to enable automatic scheduling of:
- Escalated emergency notifications (every 15 minutes)
- Daily digest notifications (daily at 8 AM UTC)

Usage:
    python run_celery_beat.py

Environment Variables:
    CELERY_BROKER_URL: Redis broker URL (default: redis://localhost:6379/0)
    CELERY_RESULT_BACKEND: Redis result backend URL (default: redis://localhost:6379/0)
    DAILY_DIGEST_HOUR: Hour to send daily digest (default: 8)
    DAILY_DIGEST_MINUTE: Minute to send daily digest (default: 0)
    ESCALATED_CHECK_INTERVAL: Minutes between escalated notification checks (default: 15)
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
    """Start the Celery Beat scheduler"""
    print("Starting Celery Beat scheduler for Habeas emergency notification system...")
    print(f"Broker URL: {os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/0')}")
    print(f"Result Backend: {os.getenv('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')}")
    print(
        f"Daily digest scheduled for: {os.getenv('DAILY_DIGEST_HOUR', '8')}:{os.getenv('DAILY_DIGEST_MINUTE', '0')} UTC"
    )
    print(f"Escalated notifications check every: {os.getenv('ESCALATED_CHECK_INTERVAL', '15')} minutes")

    # Start beat scheduler
    celery_app.control.purge()  # Clear any existing scheduled tasks

    celery_app.start(
        ["beat", "--loglevel=info", "--scheduler=celery.beat:PersistentScheduler", "--pidfile=/tmp/celerybeat.pid"]
    )


if __name__ == "__main__":
    main()
