"""
Unit tests for Celery background job system.

Tests cover:
- Task execution and results
- Job scheduling and timing
- Error handling and retries
- Health checks and monitoring
"""

from unittest.mock import Mock, patch

import pytest

from app.tasks import (
    health_check,
    schedule_escalated_notification,
    send_case_escalated_notification,
    send_daily_digest,
    send_escalated_notifications,
)


class TestEscalatedNotificationTasks:
    """Test escalated notification background tasks"""

    @patch("app.tasks.EmergencyService")
    def test_send_escalated_notifications_success(self, mock_emergency_service):
        """Test successful escalated notifications task"""
        # Mock database session
        mock_db = Mock()

        # Mock emergency service
        mock_service_instance = Mock()
        mock_service_instance.send_escalated_notifications.return_value = 3
        mock_emergency_service.return_value = mock_service_instance

        # Execute task
        result = send_escalated_notifications.__wrapped__(None, mock_db)

        # Verify results
        assert result["task"] == "send_escalated_notifications"
        assert result["status"] == "success"
        assert result["notifications_sent"] == 3
        assert "Sent escalated notifications to 3 attorneys" in result["message"]

        # Verify service was called correctly
        mock_emergency_service.assert_called_once_with(mock_db)
        mock_service_instance.send_escalated_notifications.assert_called_once()

    @patch("app.tasks.EmergencyService")
    def test_send_escalated_notifications_failure(self, mock_emergency_service):
        """Test escalated notifications task failure and retry logic"""
        # Mock database session
        mock_db = Mock()

        # Mock emergency service to raise exception
        mock_service_instance = Mock()
        mock_service_instance.send_escalated_notifications.side_effect = Exception("Service error")
        mock_emergency_service.return_value = mock_service_instance

        # Mock task instance for retry testing
        mock_task_instance = Mock()
        mock_task_instance.request.retries = 0
        mock_task_instance.MaxRetriesExceededError = Exception
        mock_task_instance.retry.side_effect = mock_task_instance.MaxRetriesExceededError()

        # Execute task (simulate retry exceeded)
        result = send_escalated_notifications.__wrapped__(mock_task_instance, mock_db)

        # Verify error handling
        assert result["task"] == "send_escalated_notifications"
        assert result["status"] == "failed"
        assert "Service error" in result["error"]
        assert result["retries_exceeded"] is True

    @patch("app.tasks.EmergencyService")
    def test_send_escalated_notifications_no_cases(self, mock_emergency_service):
        """Test escalated notifications task when no cases need escalation"""
        # Mock database session
        mock_db = Mock()

        # Mock emergency service to return 0 notifications
        mock_service_instance = Mock()
        mock_service_instance.send_escalated_notifications.return_value = 0
        mock_emergency_service.return_value = mock_service_instance

        # Execute task
        result = send_escalated_notifications.__wrapped__(None, mock_db)

        # Verify results
        assert result["status"] == "success"
        assert result["notifications_sent"] == 0
        assert "Sent escalated notifications to 0 attorneys" in result["message"]


class TestDailyDigestTasks:
    """Test daily digest background tasks"""

    @patch("app.tasks.EmergencyService")
    def test_send_daily_digest_success(self, mock_emergency_service):
        """Test successful daily digest task"""
        # Mock database session
        mock_db = Mock()

        # Mock emergency service
        mock_service_instance = Mock()
        mock_service_instance.send_daily_digest.return_value = 15
        mock_emergency_service.return_value = mock_service_instance

        # Execute task
        result = send_daily_digest.__wrapped__(None, mock_db)

        # Verify results
        assert result["task"] == "send_daily_digest"
        assert result["status"] == "success"
        assert result["notifications_sent"] == 15
        assert "Sent daily digest to 15 attorneys" in result["message"]

        # Verify service was called correctly
        mock_emergency_service.assert_called_once_with(mock_db)
        mock_service_instance.send_daily_digest.assert_called_once()

    @patch("app.tasks.EmergencyService")
    def test_send_daily_digest_failure(self, mock_emergency_service):
        """Test daily digest task failure handling"""
        # Mock database session
        mock_db = Mock()

        # Mock emergency service to raise exception
        mock_service_instance = Mock()
        mock_service_instance.send_daily_digest.side_effect = Exception("Digest error")
        mock_emergency_service.return_value = mock_service_instance

        # Mock task instance for retry testing
        mock_task_instance = Mock()
        mock_task_instance.request.retries = 0
        mock_task_instance.MaxRetriesExceededError = Exception
        mock_task_instance.retry.side_effect = mock_task_instance.MaxRetriesExceededError()

        # Execute task (simulate retry exceeded)
        result = send_daily_digest.__wrapped__(mock_task_instance, mock_db)

        # Verify error handling
        assert result["task"] == "send_daily_digest"
        assert result["status"] == "failed"
        assert "Digest error" in result["error"]
        assert result["retries_exceeded"] is True


class TestCaseSpecificTasks:
    """Test case-specific notification tasks"""

    @patch("app.tasks.send_case_escalated_notification")
    def test_schedule_escalated_notification_success(self, mock_send_notification):
        """Test successful scheduling of escalated notification"""
        # Mock the send notification task
        mock_task_result = Mock()
        mock_task_result.id = "task-123"
        mock_send_notification.apply_async.return_value = mock_task_result

        # Mock task instance
        mock_task_instance = Mock()

        # Execute scheduling task
        result = schedule_escalated_notification.__wrapped__(mock_task_instance, case_id=42, delay_hours=2)

        # Verify results
        assert result["task"] == "schedule_escalated_notification"
        assert result["status"] == "scheduled"
        assert result["case_id"] == 42
        assert result["delay_hours"] == 2
        assert "Escalated notification scheduled for case 42" in result["message"]

        # Verify task was scheduled correctly
        mock_send_notification.apply_async.assert_called_once_with(
            args=[42],
            countdown=7200,  # 2 hours in seconds
            queue="priority",
        )

    @patch("app.tasks.send_case_escalated_notification")
    def test_schedule_escalated_notification_failure(self, mock_send_notification):
        """Test scheduling failure handling"""
        # Mock the send notification task to raise exception
        mock_send_notification.apply_async.side_effect = Exception("Scheduling error")

        # Mock task instance for retry testing
        mock_task_instance = Mock()
        mock_task_instance.MaxRetriesExceededError = Exception
        mock_task_instance.retry.side_effect = mock_task_instance.MaxRetriesExceededError()

        # Execute scheduling task (simulate retry exceeded)
        result = schedule_escalated_notification.__wrapped__(mock_task_instance, case_id=42, delay_hours=1)

        # Verify error handling
        assert result["task"] == "schedule_escalated_notification"
        assert result["status"] == "failed"
        assert result["case_id"] == 42
        assert "Scheduling error" in result["error"]

    @patch("app.tasks.EmergencyService")
    def test_send_case_escalated_notification_success(self, mock_emergency_service):
        """Test successful case-specific escalated notification"""
        # Mock database session
        mock_db = Mock()

        # Mock emergency service
        mock_service_instance = Mock()
        mock_service_instance.send_escalated_notifications.return_value = 2
        mock_emergency_service.return_value = mock_service_instance

        # Execute task
        result = send_case_escalated_notification.__wrapped__(None, mock_db, case_id=42)

        # Verify results
        assert result["task"] == "send_case_escalated_notification"
        assert result["status"] == "success"
        assert result["case_id"] == 42
        assert result["notifications_sent"] == 2
        assert "Escalated notification sent for case 42" in result["message"]


class TestHealthCheckTasks:
    """Test health check and monitoring tasks"""

    def test_health_check_success(self):
        """Test successful health check task"""
        result = health_check()

        assert result["task"] == "health_check"
        assert result["status"] == "healthy"
        assert result["message"] == "Celery worker is operational"


class TestTaskConfiguration:
    """Test task configuration and settings"""

    def test_task_retry_configuration(self):
        """Test that tasks have proper retry configuration"""
        # Check escalated notifications task configuration
        assert hasattr(send_escalated_notifications, "max_retries")
        assert hasattr(send_escalated_notifications, "default_retry_delay")

        # Check daily digest task configuration
        assert hasattr(send_daily_digest, "max_retries")
        assert hasattr(send_daily_digest, "default_retry_delay")

        # Check scheduling task configuration
        assert hasattr(schedule_escalated_notification, "max_retries")
        assert hasattr(schedule_escalated_notification, "default_retry_delay")

    def test_task_binding_configuration(self):
        """Test that tasks are properly bound for access to task instance"""
        # Tasks that need access to self (for retry) should be bound
        assert getattr(send_escalated_notifications, "bind", False) is True
        assert getattr(send_daily_digest, "bind", False) is True
        assert getattr(schedule_escalated_notification, "bind", False) is True
        assert getattr(send_case_escalated_notification, "bind", False) is True

        # Health check doesn't need binding
        assert getattr(health_check, "bind", False) is False


@pytest.fixture
def mock_celery_app():
    """Mock Celery app for testing"""
    with patch("app.tasks.celery_app") as mock_app:
        mock_app.AsyncResult.return_value = Mock()
        mock_app.control.inspect.return_value = Mock()
        yield mock_app


class TestCeleryIntegration:
    """Test Celery integration and configuration"""

    def test_task_registration(self, mock_celery_app):
        """Test that tasks are properly registered with Celery"""
        # This would test actual task registration in a real integration test
        # For unit tests, we just verify the task functions exist and are callable
        assert callable(send_escalated_notifications)
        assert callable(send_daily_digest)
        assert callable(schedule_escalated_notification)
        assert callable(send_case_escalated_notification)
        assert callable(health_check)

    @patch("app.tasks.logger")
    def test_task_logging(self, mock_logger):
        """Test that tasks properly log their execution"""
        with patch("app.tasks.EmergencyService") as mock_service:
            mock_service_instance = Mock()
            mock_service_instance.send_escalated_notifications.return_value = 1
            mock_service.return_value = mock_service_instance

            # Execute task
            send_escalated_notifications.__wrapped__(None, Mock())

            # Verify logging calls
            mock_logger.info.assert_called()
            log_calls = [call.args[0] for call in mock_logger.info.call_args_list]
            assert any("Starting escalated notifications task" in call for call in log_calls)
            assert any("Escalated notifications task completed" in call for call in log_calls)
