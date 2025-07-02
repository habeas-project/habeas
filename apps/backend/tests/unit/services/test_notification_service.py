"""
Unit tests for NotificationService.
"""

import os

from unittest.mock import Mock, patch

import pytest

from app.models.attorney import Attorney
from app.models.emergency_case import AttorneyNotificationPreference
from app.services.notification_service import (
    NotificationChannel,
    NotificationService,
    NotificationStatus,
    NotificationTemplate,
)


@pytest.fixture
def notification_service():
    """Create a notification service instance for testing"""
    return NotificationService()


@pytest.fixture
def sample_attorney():
    """Create a sample attorney for testing"""
    attorney = Mock(spec=Attorney)
    attorney.id = 1
    attorney.email = "test@example.com"
    attorney.full_name = "Test Attorney"
    attorney.phone_number = "+1234567890"
    return attorney


@pytest.fixture
def sample_preferences():
    """Create sample notification preferences"""
    prefs = Mock(spec=AttorneyNotificationPreference)
    prefs.email_enabled = True
    prefs.sms_enabled = True
    prefs.push_enabled = False
    prefs.sms_phone_number = "+1234567890"
    return prefs


@pytest.fixture
def notification_template():
    """Create a sample notification template"""
    return NotificationTemplate(
        subject="Test Emergency Case - {case_location}",
        message="Test case in {case_location}. Case ID: {case_id}",
        html_content="<h1>Test case</h1><p>Location: {case_location}</p>",
    )


class TestNotificationServiceConfiguration:
    """Test notification service configuration and initialization"""

    def test_notification_service_initialization(self, notification_service):
        """Test that notification service initializes correctly"""
        assert notification_service is not None
        assert hasattr(notification_service, "templates")
        assert "immediate_case" in notification_service.templates
        assert "escalated_case" in notification_service.templates
        assert "daily_digest" in notification_service.templates

    def test_ses_configuration_enabled(self, notification_service):
        """Test SES configuration when enabled"""
        with patch.dict(os.environ, {"USE_AWS_SES": "true"}):
            service = NotificationService()
            assert service.use_ses is True

    def test_ses_configuration_disabled(self, notification_service):
        """Test SES configuration when disabled"""
        with patch.dict(os.environ, {"USE_AWS_SES": "false"}):
            service = NotificationService()
            assert service.use_ses is False

    def test_configuration_status(self, notification_service):
        """Test configuration status checking"""
        config_status = notification_service.test_configuration()

        assert isinstance(config_status, dict)
        assert "email_service" in config_status
        assert "sms_service" in config_status
        assert "push_service" in config_status


class TestNotificationChannelSelection:
    """Test notification channel selection logic"""

    def test_get_enabled_channels_all_enabled(self, notification_service, sample_preferences):
        """Test channel selection when all channels are enabled"""
        sample_preferences.email_enabled = True
        sample_preferences.sms_enabled = True
        sample_preferences.push_enabled = True

        channels = notification_service._get_enabled_channels(sample_preferences)

        assert NotificationChannel.EMAIL in channels
        assert NotificationChannel.SMS in channels
        assert NotificationChannel.PUSH in channels

    def test_get_enabled_channels_email_only(self, notification_service, sample_preferences):
        """Test channel selection when only email is enabled"""
        sample_preferences.email_enabled = True
        sample_preferences.sms_enabled = False
        sample_preferences.push_enabled = False

        channels = notification_service._get_enabled_channels(sample_preferences)

        assert NotificationChannel.EMAIL in channels
        assert NotificationChannel.SMS not in channels
        assert NotificationChannel.PUSH not in channels

    def test_get_enabled_channels_none_enabled(self, notification_service, sample_preferences):
        """Test channel selection when no channels are enabled"""
        sample_preferences.email_enabled = False
        sample_preferences.sms_enabled = False
        sample_preferences.push_enabled = False

        channels = notification_service._get_enabled_channels(sample_preferences)

        assert len(channels) == 0


class TestAWSSESIntegration:
    """Test AWS SES email integration"""

    @patch("boto3.client")
    def test_ses_email_sending_success(
        self, mock_boto_client, notification_service, sample_attorney, notification_template
    ):
        """Test successful SES email sending"""
        # Mock SES client
        mock_ses = Mock()
        mock_boto_client.return_value = mock_ses
        mock_ses.send_email.return_value = {"MessageId": "test-message-id-123"}

        # Configure service to use SES
        with patch.dict(os.environ, {"USE_AWS_SES": "true", "SES_FROM_EMAIL": "test@habeas.app"}):
            service = NotificationService()
            service.ses_client = mock_ses

            template_data = {
                "case_location": "Los Angeles, CA",
                "case_id": "123",
                "court_name": "Central District of California",
                "created_at": "2025-01-01 12:00:00",
                "case_url": "https://habeas.app/cases/123",
            }

            result = service._send_email_ses(sample_attorney, notification_template, template_data)

            assert result.status == NotificationStatus.SENT
            assert result.channel == NotificationChannel.EMAIL
            assert result.message_id == "test-message-id-123"
            assert result.error_message is None

            # Verify SES send_email was called with correct parameters
            mock_ses.send_email.assert_called_once()
            call_args = mock_ses.send_email.call_args
            assert call_args[1]["Source"] == "test@habeas.app"
            assert call_args[1]["Destination"]["ToAddresses"] == ["test@example.com"]
            assert "Test Emergency Case - Los Angeles, CA" in call_args[1]["Message"]["Subject"]["Data"]

    @patch("boto3.client")
    def test_ses_email_sending_failure(
        self, mock_boto_client, notification_service, sample_attorney, notification_template
    ):
        """Test SES email sending failure handling"""
        # Mock SES client to raise an exception
        mock_ses = Mock()
        mock_boto_client.return_value = mock_ses
        from botocore.exceptions import ClientError

        mock_ses.send_email.side_effect = ClientError(
            error_response={"Error": {"Code": "MessageRejected", "Message": "Invalid email address"}},
            operation_name="SendEmail",
        )

        # Configure service to use SES
        with patch.dict(os.environ, {"USE_AWS_SES": "true", "SES_FROM_EMAIL": "test@habeas.app"}):
            service = NotificationService()
            service.ses_client = mock_ses

            template_data = {"case_location": "Los Angeles, CA", "case_id": "123"}

            result = service._send_email_ses(sample_attorney, notification_template, template_data)

            assert result.status == NotificationStatus.FAILED
            assert result.channel == NotificationChannel.EMAIL
            assert result.message_id is None
            assert "Invalid email address" in result.error_message

    def test_ses_fallback_to_sendgrid(self, notification_service, sample_attorney, notification_template):
        """Test fallback to SendGrid when SES is unavailable"""
        with patch.dict(os.environ, {"USE_AWS_SES": "true"}):
            service = NotificationService()
            service.ses_client = None  # Simulate SES unavailable

            # Mock SendGrid client
            with patch.object(service, "_send_email_sendgrid") as mock_sendgrid:
                mock_sendgrid.return_value = Mock(status=NotificationStatus.SENT, message_id="sg-123")

                template_data = {"case_location": "Los Angeles, CA", "case_id": "123"}

                result = service._send_email(sample_attorney, notification_template, template_data)

                # Should call SendGrid fallback
                mock_sendgrid.assert_called_once_with(sample_attorney, notification_template, template_data)

                # Verify the result from fallback
                assert result.status == NotificationStatus.SENT
                assert result.message_id == "sg-123"


class TestNotificationTemplates:
    """Test notification template functionality"""

    def test_immediate_case_template(self, notification_service):
        """Test immediate case notification template"""
        template = notification_service.templates["immediate_case"]

        assert "URGENT" in template.subject
        assert "{case_location}" in template.subject
        assert "{case_location}" in template.message
        assert "{case_id}" in template.message
        assert template.html_content is not None
        assert "URGENT" in template.html_content

    def test_escalated_case_template(self, notification_service):
        """Test escalated case notification template"""
        template = notification_service.templates["escalated_case"]

        assert "FOLLOW-UP" in template.subject
        assert "{time_waiting}" in template.message
        assert template.html_content is not None

    def test_daily_digest_template(self, notification_service):
        """Test daily digest notification template"""
        template = notification_service.templates["daily_digest"]

        assert "Daily Digest" in template.subject
        assert "{case_count}" in template.subject
        assert "{case_count}" in template.message
        assert "{case_list}" in template.message
        assert template.html_content is not None


class TestNotificationDelivery:
    """Test notification delivery functionality"""

    def test_immediate_case_notification(self, notification_service, sample_attorney, sample_preferences):
        """Test sending immediate case notifications"""
        from app.models.emergency_case import EmergencyCase

        # Mock emergency case
        case = Mock(spec=EmergencyCase)
        case.id = 123
        case.detention_address = "Los Angeles, CA"
        case.assigned_court = Mock()
        case.assigned_court.name = "Central District of California"
        case.created_at = "2025-01-01 12:00:00"

        with patch.object(notification_service, "_send_notification") as mock_send:
            mock_send.return_value = [Mock(status=NotificationStatus.SENT)]

            results = notification_service.send_immediate_case_notification(sample_attorney, case, sample_preferences)

            assert len(results) > 0
            mock_send.assert_called_once()

    def test_escalated_case_notification(self, notification_service, sample_attorney, sample_preferences):
        """Test sending escalated case notifications"""
        from app.models.emergency_case import EmergencyCase

        # Mock emergency case
        case = Mock(spec=EmergencyCase)
        case.id = 123
        case.detention_address = "Los Angeles, CA"
        case.assigned_court = Mock()
        case.assigned_court.name = "Central District of California"
        case.created_at = "2025-01-01 12:00:00"

        with patch.object(notification_service, "_send_notification") as mock_send:
            mock_send.return_value = [Mock(status=NotificationStatus.SENT)]

            results = notification_service.send_escalated_case_notification(
                sample_attorney, case, sample_preferences, "2 hours"
            )

            assert len(results) > 0
            mock_send.assert_called_once()

    def test_daily_digest_notification(self, notification_service, sample_attorney, sample_preferences):
        """Test sending daily digest notifications"""
        from app.models.emergency_case import EmergencyCase

        # Mock unassigned cases
        cases = [Mock(spec=EmergencyCase) for _ in range(3)]
        for i, case in enumerate(cases):
            case.id = i + 1
            case.detention_address = f"City {i + 1}"
            case.assigned_court = Mock()
            case.assigned_court.name = f"District {i + 1}"

        coverage_stats = {"Central District of California": 15}

        with patch.object(notification_service, "_send_notification") as mock_send:
            mock_send.return_value = [Mock(status=NotificationStatus.SENT)]

            results = notification_service.send_daily_digest(sample_attorney, sample_preferences, cases, coverage_stats)

            assert len(results) > 0
            mock_send.assert_called_once()
