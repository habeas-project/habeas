"""
Unit tests for NotificationService.
"""

from unittest.mock import Mock

from app.services.notification_service import NotificationChannel, NotificationService, NotificationStatus


def test_notification_service_init():
    """Test notification service initialization"""
    service = NotificationService()
    assert service is not None
    assert hasattr(service, "templates")
    assert "immediate_case" in service.templates


def test_get_enabled_channels():
    """Test getting enabled notification channels"""
    service = NotificationService()

    # Mock preferences
    preferences = Mock()
    preferences.email_enabled = True
    preferences.sms_enabled = True
    preferences.push_enabled = False
    preferences.sms_phone_number = "+1234567890"

    channels = service._get_enabled_channels(preferences)

    assert NotificationChannel.EMAIL in channels
    assert NotificationChannel.SMS in channels
    assert NotificationChannel.PUSH not in channels


def test_send_email_no_client():
    """Test email sending without configured client"""
    service = NotificationService()

    # Mock attorney
    attorney = Mock()
    attorney.email = "test@example.com"

    template = service.templates["immediate_case"]
    template_data = {
        "case_location": "Test Location",
        "court_name": "Test Court",
        "case_id": "123",
        "created_at": "2025-01-15 10:30 UTC",
        "case_url": "https://test.com",
    }

    result = service._send_email(attorney, template, template_data)

    assert result.channel == NotificationChannel.EMAIL
    assert result.status == NotificationStatus.FAILED
    assert "SendGrid client not configured" in result.error_message


def test_template_formatting():
    """Test notification template formatting"""
    service = NotificationService()
    template = service.templates["immediate_case"]

    template_data = {
        "case_location": "Los Angeles, CA",
        "court_name": "Central District of California",
        "case_id": "123",
        "created_at": "2025-01-15 10:30 UTC",
        "case_url": "https://habeas.app/cases/123",
    }

    formatted_subject = template.subject.format(**template_data)
    formatted_message = template.message.format(**template_data)

    assert "Los Angeles, CA" in formatted_subject
    assert "Case ID: #123" in formatted_message
    assert "https://habeas.app/cases/123" in formatted_message
