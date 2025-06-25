"""
Notification service for sending multi-channel notifications to attorneys.

This service handles:
- Email notifications via AWS SES (migrated from SendGrid for cost optimization)
- SMS notifications via Twilio
- Push notifications (placeholder for future implementation)
- Notification preference enforcement
- Delivery status tracking and retry logic
"""

import logging
import os

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

import boto3

from botocore.exceptions import BotoCoreError, ClientError
from pydantic import BaseModel
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from twilio.base.exceptions import TwilioRestException
from twilio.rest import Client as TwilioClient

from app.models.attorney import Attorney
from app.models.emergency_case import AttorneyNotificationPreference, EmergencyCase

logger = logging.getLogger(__name__)


class NotificationChannel(str, Enum):
    """Notification delivery channels"""

    EMAIL = "email"
    SMS = "sms"
    PUSH = "push"


class NotificationStatus(str, Enum):
    """Notification delivery status"""

    PENDING = "pending"
    SENT = "sent"
    DELIVERED = "delivered"
    FAILED = "failed"
    RETRY = "retry"


class NotificationTemplate(BaseModel):
    """Base notification template"""

    subject: str
    message: str
    html_content: Optional[str] = None


class NotificationRequest(BaseModel):
    """Request for sending notifications"""

    attorney_id: int
    case_id: int
    notification_type: str  # "immediate", "escalated", "daily_digest"
    channels: List[NotificationChannel]
    template_data: Dict[str, str]


class NotificationResult(BaseModel):
    """Result of notification attempt"""

    channel: NotificationChannel
    status: NotificationStatus
    message_id: Optional[str] = None
    error_message: Optional[str] = None
    sent_at: Optional[datetime] = None


class NotificationService:
    """Service for sending multi-channel notifications to attorneys"""

    def __init__(self):
        """Initialize notification service with external service clients"""
        # Email service configuration (migrated to AWS SES)
        self.use_ses = os.getenv("USE_AWS_SES", "true").lower() == "true"

        # AWS SES configuration
        self.ses_client = None
        self.ses_from_email = os.getenv("SES_FROM_EMAIL", "alerts@habeas.app")

        if self.use_ses:
            try:
                # Initialize AWS SES client
                aws_region = os.getenv("AWS_REGION", "us-east-1")

                # Use environment variables or IAM role for credentials
                self.ses_client = boto3.client(
                    "ses",
                    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
                    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
                    region_name=aws_region,
                )
                logger.info("AWS SES client initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize AWS SES client: {e}")

        # Legacy SendGrid configuration (fallback during migration)
        self.sendgrid_api_key = os.getenv("SENDGRID_API_KEY")
        self.sendgrid_from_email = os.getenv("SENDGRID_FROM_EMAIL", "alerts@habeas.app")
        self.sendgrid_client = None

        if self.sendgrid_api_key and not self.use_ses:
            try:
                self.sendgrid_client = SendGridAPIClient(api_key=self.sendgrid_api_key)
                logger.info("SendGrid client initialized as fallback")
            except Exception as e:
                logger.error(f"Failed to initialize SendGrid client: {e}")

        # Twilio configuration
        self.twilio_account_sid = os.getenv("TWILIO_ACCOUNT_SID")
        self.twilio_auth_token = os.getenv("TWILIO_AUTH_TOKEN")
        self.twilio_from_number = os.getenv("TWILIO_FROM_NUMBER")
        self.twilio_client = None

        if self.twilio_account_sid and self.twilio_auth_token:
            try:
                self.twilio_client = TwilioClient(self.twilio_account_sid, self.twilio_auth_token)
            except Exception as e:
                logger.error(f"Failed to initialize Twilio client: {e}")

        # Notification templates
        self.templates = self._load_notification_templates()

    def _load_notification_templates(self) -> Dict[str, NotificationTemplate]:
        """Load notification templates for different scenarios"""
        return {
            "immediate_case": NotificationTemplate(
                subject="🚨 URGENT: New Immigration Detention Case - {case_location}",
                message=(
                    "URGENT: A new immigration detention case requires immediate attorney assistance.\n\n"
                    "Location: {case_location}\n"
                    "Court: {court_name}\n"
                    "Case ID: #{case_id}\n"
                    "Time: {created_at}\n\n"
                    "Please respond immediately if you can accept this case.\n"
                    "View case details: {case_url}"
                ),
                html_content=(
                    "<h2 style='color: #dc2626;'>🚨 URGENT: New Immigration Detention Case</h2>"
                    "<p><strong>Location:</strong> {case_location}</p>"
                    "<p><strong>Court:</strong> {court_name}</p>"
                    "<p><strong>Case ID:</strong> #{case_id}</p>"
                    "<p><strong>Time:</strong> {created_at}</p>"
                    "<p style='margin-top: 20px;'>"
                    "<a href='{case_url}' style='background-color: #dc2626; color: white; padding: 12px 24px; "
                    "text-decoration: none; border-radius: 4px; font-weight: bold;'>"
                    "Accept Case</a></p>"
                    "<p style='color: #666; font-size: 14px; margin-top: 20px;'>"
                    "This is an emergency notification. Please respond immediately if you can assist.</p>"
                ),
            ),
            "escalated_case": NotificationTemplate(
                subject="⚠️ FOLLOW-UP: Unassigned Immigration Detention Case - {case_location}",
                message=(
                    "FOLLOW-UP: This immigration detention case still needs attorney assistance.\n\n"
                    "Location: {case_location}\n"
                    "Court: {court_name}\n"
                    "Case ID: #{case_id}\n"
                    "Originally posted: {created_at}\n"
                    "Time waiting: {time_waiting}\n\n"
                    "Please respond if you can accept this case.\n"
                    "View case details: {case_url}"
                ),
                html_content=(
                    "<h2 style='color: #f59e0b;'>⚠️ FOLLOW-UP: Unassigned Immigration Detention Case</h2>"
                    "<p><strong>Location:</strong> {case_location}</p>"
                    "<p><strong>Court:</strong> {court_name}</p>"
                    "<p><strong>Case ID:</strong> #{case_id}</p>"
                    "<p><strong>Originally posted:</strong> {created_at}</p>"
                    "<p><strong>Time waiting:</strong> {time_waiting}</p>"
                    "<p style='margin-top: 20px;'>"
                    "<a href='{case_url}' style='background-color: #f59e0b; color: white; padding: 12px 24px; "
                    "text-decoration: none; border-radius: 4px; font-weight: bold;'>"
                    "Accept Case</a></p>"
                    "<p style='color: #666; font-size: 14px; margin-top: 20px;'>"
                    "This case has been waiting for attorney assistance. Please help if you can.</p>"
                ),
            ),
            "daily_digest": NotificationTemplate(
                subject="📋 Daily Digest: {case_count} Unassigned Immigration Cases",
                message=(
                    "Daily Summary of Unassigned Immigration Detention Cases\n\n"
                    "Total unassigned cases: {case_count}\n"
                    "Your district coverage: {attorney_coverage}\n\n"
                    "{case_list}\n\n"
                    "View all cases: {dashboard_url}"
                ),
                html_content=(
                    "<h2>📋 Daily Digest: Immigration Detention Cases</h2>"
                    "<p><strong>Total unassigned cases:</strong> {case_count}</p>"
                    "<p><strong>Your district coverage:</strong> {attorney_coverage}</p>"
                    "<div style='margin-top: 20px;'>{case_list_html}</div>"
                    "<p style='margin-top: 20px;'>"
                    "<a href='{dashboard_url}' style='background-color: #2563eb; color: white; padding: 12px 24px; "
                    "text-decoration: none; border-radius: 4px; font-weight: bold;'>"
                    "View Attorney Dashboard</a></p>"
                ),
            ),
        }

    def send_immediate_case_notification(
        self, attorney: Attorney, case: EmergencyCase, preferences: AttorneyNotificationPreference
    ) -> List[NotificationResult]:
        """Send immediate notification for new emergency case"""
        template_data = {
            "case_location": case.detention_location or "Location not specified",
            "court_name": case.assigned_court.name if case.assigned_court else "Court TBD",
            "case_id": str(case.id),
            "created_at": case.created_at.strftime("%Y-%m-%d %H:%M UTC"),
            "case_url": f"{os.getenv('FRONTEND_URL', 'https://habeas.app')}/cases/{case.id}",
        }

        channels = self._get_enabled_channels(preferences)
        return self._send_notification(
            attorney=attorney,
            preferences=preferences,
            template_key="immediate_case",
            template_data=template_data,
            channels=channels,
        )

    def send_escalated_case_notification(
        self, attorney: Attorney, case: EmergencyCase, preferences: AttorneyNotificationPreference, time_waiting: str
    ) -> List[NotificationResult]:
        """Send escalated notification for unassigned case"""
        template_data = {
            "case_location": case.detention_location or "Location not specified",
            "court_name": case.assigned_court.name if case.assigned_court else "Court TBD",
            "case_id": str(case.id),
            "created_at": case.created_at.strftime("%Y-%m-%d %H:%M UTC"),
            "time_waiting": time_waiting,
            "case_url": f"{os.getenv('FRONTEND_URL', 'https://habeas.app')}/cases/{case.id}",
        }

        # Only send escalated notifications if attorney has them enabled
        if not preferences.escalated_notifications_enabled:
            return []

        channels = self._get_enabled_channels(preferences)
        return self._send_notification(
            attorney=attorney,
            preferences=preferences,
            template_key="escalated_case",
            template_data=template_data,
            channels=channels,
        )

    def send_daily_digest(
        self,
        attorney: Attorney,
        preferences: AttorneyNotificationPreference,
        unassigned_cases: List[EmergencyCase],
        attorney_coverage_stats: Dict[str, int],
    ) -> List[NotificationResult]:
        """Send daily digest of unassigned cases"""
        if not preferences.daily_digest_enabled:
            return []

        # Format case list for text
        case_list = []
        case_list_html = []

        for case in unassigned_cases:
            age = (datetime.utcnow() - case.created_at).total_seconds() / 3600  # hours
            case_text = (
                f"• Case #{case.id} - {case.detention_location} "
                f"({case.assigned_court.name if case.assigned_court else 'Court TBD'}) "
                f"- {age:.1f}h ago"
            )
            case_list.append(case_text)

            case_html = (
                f"<div style='padding: 10px; border-left: 3px solid #2563eb; margin: 10px 0;'>"
                f"<strong>Case #{case.id}</strong><br>"
                f"Location: {case.detention_location}<br>"
                f"Court: {case.assigned_court.name if case.assigned_court else 'Court TBD'}<br>"
                f"Age: {age:.1f} hours<br>"
                f"<a href='{os.getenv('FRONTEND_URL', 'https://habeas.app')}/cases/{case.id}'>View Case</a>"
                f"</div>"
            )
            case_list_html.append(case_html)

        template_data = {
            "case_count": str(len(unassigned_cases)),
            "attorney_coverage": ", ".join(
                [f"{court}: {count} attorneys" for court, count in attorney_coverage_stats.items()]
            ),
            "case_list": "\n".join(case_list) if case_list else "No unassigned cases today.",
            "case_list_html": "".join(case_list_html) if case_list_html else "<p>No unassigned cases today.</p>",
            "dashboard_url": f"{os.getenv('FRONTEND_URL', 'https://habeas.app')}/attorney/dashboard",
        }

        # Daily digest typically only via email unless attorney specifically wants SMS
        channels = [NotificationChannel.EMAIL]
        if preferences.sms_enabled and preferences.sms_phone_number:
            channels.append(NotificationChannel.SMS)

        return self._send_notification(
            attorney=attorney,
            preferences=preferences,
            template_key="daily_digest",
            template_data=template_data,
            channels=channels,
        )

    def _get_enabled_channels(self, preferences: AttorneyNotificationPreference) -> List[NotificationChannel]:
        """Get list of enabled notification channels for attorney"""
        channels = []

        if preferences.email_enabled:
            channels.append(NotificationChannel.EMAIL)

        if preferences.sms_enabled and preferences.sms_phone_number:
            channels.append(NotificationChannel.SMS)

        if preferences.push_enabled:
            channels.append(NotificationChannel.PUSH)

        return channels

    def _send_notification(
        self,
        attorney: Attorney,
        preferences: AttorneyNotificationPreference,
        template_key: str,
        template_data: Dict[str, str],
        channels: List[NotificationChannel],
    ) -> List[NotificationResult]:
        """Send notification via specified channels"""
        results: List[NotificationResult] = []
        template = self.templates.get(template_key)

        if not template:
            logger.error(f"Template not found: {template_key}")
            return results

        for channel in channels:
            try:
                if channel == NotificationChannel.EMAIL:
                    result = self._send_email(attorney, template, template_data)
                elif channel == NotificationChannel.SMS:
                    result = self._send_sms(attorney, preferences, template, template_data)
                elif channel == NotificationChannel.PUSH:
                    result = self._send_push_notification(attorney, template, template_data)
                else:
                    result = NotificationResult(
                        channel=channel,
                        status=NotificationStatus.FAILED,
                        error_message=f"Unsupported channel: {channel}",
                    )

                results.append(result)

            except Exception as e:
                logger.error(f"Failed to send {channel} notification to attorney {attorney.id}: {e}")
                results.append(
                    NotificationResult(channel=channel, status=NotificationStatus.FAILED, error_message=str(e))
                )

        return results

    def _send_email(
        self, attorney: Attorney, template: NotificationTemplate, template_data: Dict[str, str]
    ) -> NotificationResult:
        """Send email notification via AWS SES or SendGrid fallback"""
        if self.use_ses and self.ses_client:
            return self._send_email_ses(attorney, template, template_data)
        elif self.sendgrid_client:
            return self._send_email_sendgrid(attorney, template, template_data)
        else:
            return NotificationResult(
                channel=NotificationChannel.EMAIL,
                status=NotificationStatus.FAILED,
                error_message="No email client configured (SES or SendGrid)",
            )

    def _send_email_ses(
        self, attorney: Attorney, template: NotificationTemplate, template_data: Dict[str, str]
    ) -> NotificationResult:
        """Send email notification via AWS SES"""
        try:
            # Format template with data
            subject = template.subject.format(**template_data)
            text_content = template.message.format(**template_data)
            html_content = template.html_content.format(**template_data) if template.html_content else None

            # Prepare email destination
            destination = {"ToAddresses": [attorney.email]}

            # Prepare message content
            message: Dict[str, Any] = {
                "Subject": {"Data": subject, "Charset": "UTF-8"},
                "Body": {"Text": {"Data": text_content, "Charset": "UTF-8"}},
            }

            if html_content:
                message["Body"]["Html"] = {"Data": html_content, "Charset": "UTF-8"}

            # Send email via SES
            response = self.ses_client.send_email(
                Source=self.ses_from_email,
                Destination=destination,
                Message=message,
            )

            return NotificationResult(
                channel=NotificationChannel.EMAIL,
                status=NotificationStatus.SENT,
                message_id=response.get("MessageId"),
                sent_at=datetime.utcnow(),
            )

        except (ClientError, BotoCoreError) as e:
            logger.error(f"AWS SES email failed for attorney {attorney.id}: {e}")
            return NotificationResult(
                channel=NotificationChannel.EMAIL,
                status=NotificationStatus.FAILED,
                error_message=f"SES error: {str(e)}",
            )
        except Exception as e:
            logger.error(f"Email sending failed for attorney {attorney.id}: {e}")
            return NotificationResult(
                channel=NotificationChannel.EMAIL, status=NotificationStatus.FAILED, error_message=str(e)
            )

    def _send_email_sendgrid(
        self, attorney: Attorney, template: NotificationTemplate, template_data: Dict[str, str]
    ) -> NotificationResult:
        """Send email notification via SendGrid (legacy fallback)"""
        try:
            # Format template with data
            subject = template.subject.format(**template_data)
            text_content = template.message.format(**template_data)
            html_content = template.html_content.format(**template_data) if template.html_content else None

            # Create email message
            message = Mail(
                from_email=self.sendgrid_from_email,
                to_emails=attorney.email,
                subject=subject,
                plain_text_content=text_content,
                html_content=html_content,
            )

            # Send email
            response = self.sendgrid_client.send(message)

            return NotificationResult(
                channel=NotificationChannel.EMAIL,
                status=NotificationStatus.SENT,
                message_id=response.headers.get("X-Message-Id"),
                sent_at=datetime.utcnow(),
            )

        except Exception as e:
            logger.error(f"SendGrid email failed for attorney {attorney.id}: {e}")
            return NotificationResult(
                channel=NotificationChannel.EMAIL, status=NotificationStatus.FAILED, error_message=str(e)
            )

    def _send_sms(
        self,
        attorney: Attorney,
        preferences: AttorneyNotificationPreference,
        template: NotificationTemplate,
        template_data: Dict[str, str],
    ) -> NotificationResult:
        """Send SMS notification via Twilio"""
        if not self.twilio_client or not self.twilio_from_number:
            return NotificationResult(
                channel=NotificationChannel.SMS,
                status=NotificationStatus.FAILED,
                error_message="Twilio client not configured",
            )

        if not preferences.sms_phone_number:
            return NotificationResult(
                channel=NotificationChannel.SMS,
                status=NotificationStatus.FAILED,
                error_message="No SMS phone number configured for attorney",
            )

        try:
            # Format message (SMS uses plain text only, keep it concise)
            message_text = template.message.format(**template_data)

            # Truncate if too long (SMS limit is 1600 chars for long messages)
            if len(message_text) > 1500:
                message_text = message_text[:1500] + "... [See email for full details]"

            # Send SMS
            message = self.twilio_client.messages.create(
                body=message_text, from_=self.twilio_from_number, to=preferences.sms_phone_number
            )

            return NotificationResult(
                channel=NotificationChannel.SMS,
                status=NotificationStatus.SENT,
                message_id=message.sid,
                sent_at=datetime.utcnow(),
            )

        except TwilioRestException as e:
            logger.error(f"Twilio SMS failed for attorney {attorney.id}: {e}")
            return NotificationResult(
                channel=NotificationChannel.SMS,
                status=NotificationStatus.FAILED,
                error_message=f"Twilio error: {e.msg}",
            )
        except Exception as e:
            logger.error(f"SMS sending failed for attorney {attorney.id}: {e}")
            return NotificationResult(
                channel=NotificationChannel.SMS, status=NotificationStatus.FAILED, error_message=str(e)
            )

    def _send_push_notification(
        self, attorney: Attorney, template: NotificationTemplate, template_data: Dict[str, str]
    ) -> NotificationResult:
        """Send push notification (placeholder for future implementation)"""
        # TODO: Implement push notification service (Firebase, AWS SNS, etc.)
        logger.info(f"Push notification placeholder for attorney {attorney.id}")

        return NotificationResult(
            channel=NotificationChannel.PUSH,
            status=NotificationStatus.FAILED,
            error_message="Push notifications not yet implemented",
        )

    def test_configuration(self) -> Dict[str, bool]:
        """Test notification service configuration"""
        results = {}

        # Test AWS SES
        if self.use_ses:
            results["ses_configured"] = bool(self.ses_client)
            if self.ses_client:
                try:
                    # Test SES connectivity by getting sending quota
                    self.ses_client.get_send_quota()
                    results["ses_valid"] = True
                except Exception:
                    results["ses_valid"] = False
            else:
                results["ses_valid"] = False
        else:
            results["ses_configured"] = False
            results["ses_valid"] = False

        # Test SendGrid (legacy fallback)
        results["sendgrid_configured"] = bool(self.sendgrid_client)
        if self.sendgrid_client:
            try:
                # Test API key validity (this doesn't send an email)
                self.sendgrid_client.client.api_keys.get()
                results["sendgrid_valid"] = True
            except Exception:
                results["sendgrid_valid"] = False
        else:
            results["sendgrid_valid"] = False

        # Test Twilio
        results["twilio_configured"] = bool(self.twilio_client)
        if self.twilio_client:
            try:
                # Test account validity
                account = self.twilio_client.api.accounts(self.twilio_account_sid).fetch()
                results["twilio_valid"] = account.status == "active"
            except Exception:
                results["twilio_valid"] = False
        else:
            results["twilio_valid"] = False

        return results
