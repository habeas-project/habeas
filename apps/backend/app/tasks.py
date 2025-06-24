"""
Celery background tasks for emergency notification system.

This module defines background tasks for:
- Escalated emergency case notifications (1-hour follow-up)
- Daily digest notifications for attorneys
- Job monitoring and error handling
"""

import logging

from typing import Any, Dict

from sqlalchemy.orm import Session

from .celery_app import DatabaseTask, celery_app
from .services.emergency_service import EmergencyService

# Configure logging for background tasks
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@celery_app.task(bind=True, base=DatabaseTask, max_retries=3, default_retry_delay=300)
def send_escalated_notifications(self, db: Session) -> Dict[str, Any]:
    """
    Background task to send escalated notifications for emergency cases.

    This task runs every 15 minutes and checks for emergency cases that:
    - Are still active (unassigned)
    - Were created more than 1 hour ago
    - Need escalated notification reminders

    Args:
        db: Database session (injected by DatabaseTask base class)

    Returns:
        Dictionary with task execution results
    """
    try:
        logger.info("Starting escalated notifications task")

        emergency_service = EmergencyService(db)
        notifications_sent = emergency_service.send_escalated_notifications()

        result = {
            "task": "send_escalated_notifications",
            "status": "success",
            "notifications_sent": notifications_sent,
            "message": f"Sent escalated notifications to {notifications_sent} attorneys",
        }

        logger.info(f"Escalated notifications task completed: {result}")
        return result

    except Exception as exc:
        logger.error(f"Escalated notifications task failed: {str(exc)}")

        # Retry with exponential backoff
        try:
            raise self.retry(exc=exc, countdown=60 * (2**self.request.retries))
        except self.MaxRetriesExceededError:
            # Log final failure and return error result
            error_result = {
                "task": "send_escalated_notifications",
                "status": "failed",
                "error": str(exc),
                "retries_exceeded": True,
            }
            logger.error(f"Escalated notifications task failed permanently: {error_result}")
            return error_result


@celery_app.task(bind=True, base=DatabaseTask, max_retries=3, default_retry_delay=600)
def send_daily_digest(self, db: Session) -> Dict[str, Any]:
    """
    Background task to send daily digest notifications to attorneys.

    This task runs daily at 8:00 AM UTC and sends a digest of:
    - All unassigned emergency cases
    - Court coverage statistics
    - Attorney-specific case information

    Args:
        db: Database session (injected by DatabaseTask base class)

    Returns:
        Dictionary with task execution results
    """
    try:
        logger.info("Starting daily digest task")

        emergency_service = EmergencyService(db)
        notifications_sent = emergency_service.send_daily_digest()

        result = {
            "task": "send_daily_digest",
            "status": "success",
            "notifications_sent": notifications_sent,
            "message": f"Sent daily digest to {notifications_sent} attorneys",
        }

        logger.info(f"Daily digest task completed: {result}")
        return result

    except Exception as exc:
        logger.error(f"Daily digest task failed: {str(exc)}")

        # Retry with exponential backoff
        try:
            raise self.retry(exc=exc, countdown=60 * (2**self.request.retries))
        except self.MaxRetriesExceededError:
            # Log final failure and return error result
            error_result = {
                "task": "send_daily_digest",
                "status": "failed",
                "error": str(exc),
                "retries_exceeded": True,
            }
            logger.error(f"Daily digest task failed permanently: {error_result}")
            return error_result


@celery_app.task(bind=True, max_retries=2, default_retry_delay=60)
def schedule_escalated_notification(self, case_id: int, delay_hours: int = 1) -> Dict[str, Any]:
    """
    Schedule a specific escalated notification for an emergency case.

    This task can be used to schedule one-off escalated notifications
    for specific cases, separate from the periodic escalated notification job.

    Args:
        case_id: ID of the emergency case
        delay_hours: Hours to wait before sending notification (default: 1)

    Returns:
        Dictionary with task execution results
    """
    try:
        logger.info(f"Scheduling escalated notification for case {case_id} in {delay_hours} hours")

        # Schedule the notification using Celery's apply_async with countdown
        countdown_seconds = delay_hours * 3600  # Convert hours to seconds

        send_case_escalated_notification.apply_async(args=[case_id], countdown=countdown_seconds, queue="priority")

        result = {
            "task": "schedule_escalated_notification",
            "status": "scheduled",
            "case_id": case_id,
            "delay_hours": delay_hours,
            "message": f"Escalated notification scheduled for case {case_id}",
        }

        logger.info(f"Escalated notification scheduled: {result}")
        return result

    except Exception as exc:
        logger.error(f"Failed to schedule escalated notification for case {case_id}: {str(exc)}")

        try:
            raise self.retry(exc=exc)
        except self.MaxRetriesExceededError:
            error_result = {
                "task": "schedule_escalated_notification",
                "status": "failed",
                "case_id": case_id,
                "error": str(exc),
            }
            logger.error(f"Failed to schedule escalated notification permanently: {error_result}")
            return error_result


@celery_app.task(bind=True, base=DatabaseTask, max_retries=3, default_retry_delay=180)
def send_case_escalated_notification(self, db: Session, case_id: int) -> Dict[str, Any]:
    """
    Send escalated notification for a specific emergency case.

    This task is used by the scheduler to send targeted escalated
    notifications for individual cases.

    Args:
        db: Database session (injected by DatabaseTask base class)
        case_id: ID of the emergency case

    Returns:
        Dictionary with task execution results
    """
    try:
        logger.info(f"Sending escalated notification for case {case_id}")

        emergency_service = EmergencyService(db)

        # This would require enhancing EmergencyService to handle single cases
        # For now, we'll call the existing method which handles all applicable cases
        notifications_sent = emergency_service.send_escalated_notifications()

        result = {
            "task": "send_case_escalated_notification",
            "status": "success",
            "case_id": case_id,
            "notifications_sent": notifications_sent,
            "message": f"Escalated notification sent for case {case_id}",
        }

        logger.info(f"Case escalated notification completed: {result}")
        return result

    except Exception as exc:
        logger.error(f"Case escalated notification failed for case {case_id}: {str(exc)}")

        try:
            raise self.retry(exc=exc, countdown=60 * (2**self.request.retries))
        except self.MaxRetriesExceededError:
            error_result = {
                "task": "send_case_escalated_notification",
                "status": "failed",
                "case_id": case_id,
                "error": str(exc),
            }
            logger.error(f"Case escalated notification failed permanently: {error_result}")
            return error_result


@celery_app.task
def health_check() -> Dict[str, Any]:
    """
    Health check task for monitoring Celery worker status.

    Returns:
        Dictionary with health check results
    """
    return {"task": "health_check", "status": "healthy", "message": "Celery worker is operational"}
