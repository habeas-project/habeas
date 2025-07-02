"""
Celery application configuration for background job system.

This module sets up Celery for:
- Escalated emergency case notifications (1-hour follow-up)
- Daily digest notifications for attorneys
- Job monitoring and retry logic
"""

import os

from celery import Celery
from celery.schedules import crontab

# Configure Celery
celery_app = Celery(
    "habeas-backend",
    broker=os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0"),
    backend=os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/0"),
    include=["app.tasks"],
)

# Celery configuration
celery_app.conf.update(
    # Time zone configuration
    timezone="UTC",
    enable_utc=True,
    # Task configuration
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    # Task routing
    task_routes={
        "app.tasks.send_escalated_notifications": {"queue": "priority"},
        "app.tasks.send_daily_digest": {"queue": "default"},
    },
    # Retry configuration
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    # Beat scheduler configuration
    beat_schedule={
        # Check for escalated notifications every 15 minutes
        "escalated-notifications": {
            "task": "app.tasks.send_escalated_notifications",
            "schedule": crontab(minute="*/15"),  # Every 15 minutes
            "options": {"queue": "priority"},
        },
        # Send daily digest at 8 AM UTC (adjustable per time zone)
        "daily-digest": {
            "task": "app.tasks.send_daily_digest",
            "schedule": crontab(hour=8, minute=0),  # Daily at 8:00 AM UTC
            "options": {"queue": "default"},
        },
    },
    # Worker configuration
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
    # Redis-specific settings
    redis_socket_keepalive=True,
    redis_socket_keepalive_options={
        "TCP_KEEPINTVL": 1,
        "TCP_KEEPCNT": 3,
        "TCP_KEEPIDLE": 1,
    },
    # Result expiration
    result_expires=3600,  # 1 hour
)


class DatabaseTask(celery_app.Task):  # type: ignore
    """Base task class that provides database session handling"""

    def __call__(self, *args, **kwargs):
        from app.database import SessionLocal

        db = SessionLocal()
        try:
            return super().__call__(db, *args, **kwargs)
        finally:
            db.close()
