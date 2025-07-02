from datetime import datetime, timedelta
from typing import List, Optional, Tuple

from sqlalchemy import and_, func, or_
from sqlalchemy.orm import Session

from app.models import (
    Attorney,
    AttorneyNotificationPreference,
    ClientProfile,
    Court,
    EmergencyCase,
    EmergencyContact,
    User,
)
from app.schemas.emergency_case import (
    EmergencyActivationRequest,
    EmergencyStatusResponse,
    LocationData,
)

from .geocoding_service import GeocodingService
from .notification_service import NotificationService


class EmergencyService:
    """Service class for emergency case management"""

    def __init__(self, db: Session):
        self.db = db
        self.geocoding_service = GeocodingService(db)
        self.notification_service = NotificationService()

    def get_user_emergency_status(self, user_id: int) -> EmergencyStatusResponse:
        """Get emergency status for a user"""
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ValueError("User not found")

        # Check if user has client profiles
        has_client_profiles = bool(user.client_profiles)

        # Check if user has emergency contacts
        has_emergency_contacts = False
        if has_client_profiles:
            emergency_contacts_count = (
                self.db.query(EmergencyContact).join(ClientProfile).filter(ClientProfile.user_id == user_id).count()
            )
            has_emergency_contacts = emergency_contacts_count > 0

        # Check for active emergency case
        active_case = (
            self.db.query(EmergencyCase)
            .filter(and_(EmergencyCase.user_id == user_id, EmergencyCase.status.in_(["active", "attorney_assigned"])))
            .first()
        )

        active_case_id = active_case.id if active_case else None
        active_case_status = active_case.status if active_case else None
        assigned_attorney_name = None
        assigned_court_name = None

        if active_case:
            if active_case.assigned_attorney:
                assigned_attorney_name = active_case.assigned_attorney.name
            if active_case.assigned_court:
                assigned_court_name = active_case.assigned_court.name

        can_activate_emergency = has_client_profiles and has_emergency_contacts and not active_case

        return EmergencyStatusResponse(
            has_emergency_contacts=has_emergency_contacts,
            has_client_profiles=has_client_profiles,
            active_emergency_case_id=active_case_id,
            active_case_status=active_case_status,
            assigned_attorney_name=assigned_attorney_name,
            assigned_court_name=assigned_court_name,
            can_activate_emergency=can_activate_emergency,
        )

    def determine_court_jurisdiction(self, location: LocationData) -> Optional[Court]:
        """Determine court jurisdiction based on location"""
        # If we have GPS coordinates, use geocoding service
        if location.latitude and location.longitude:
            # Validate coordinates
            if not self.geocoding_service.validate_coordinates(location.latitude, location.longitude):
                return None

            # Use geocoding service to determine jurisdiction
            address_data, court = self.geocoding_service.geocode_and_determine_jurisdiction(
                location.latitude, location.longitude
            )

            if court:
                return court

            # If geocoding fails, fall back to basic approach

        # Fallback: try to parse location data manually
        if location.address or location.description:
            # Simple fallback - try to extract state from address/description
            # and find a court for that state
            text_to_search = (location.address or "") + " " + (location.description or "")

            # This is a very basic implementation - could be enhanced
            # with more sophisticated text parsing
            courts = self.db.query(Court).all()
            for court in courts:
                if any(word in text_to_search.upper() for word in court.name.upper().split()):
                    return court

        # Final fallback: return the first available court
        return self.db.query(Court).first()

    def create_emergency_case(self, user_id: int, request: EmergencyActivationRequest) -> Tuple[EmergencyCase, int]:
        """Create a new emergency case and notify attorneys"""

        # Validate user has emergency contacts
        status = self.get_user_emergency_status(user_id)
        if not status.can_activate_emergency:
            raise ValueError("User cannot activate emergency - missing prerequisites")

        # Validate client profile exists
        client_profile = (
            self.db.query(ClientProfile)
            .filter(and_(ClientProfile.id == request.client_profile_id, ClientProfile.user_id == user_id))
            .first()
        )
        if not client_profile:
            raise ValueError("Client profile not found")

        # Enhanced location processing with geocoding
        geocoded_address = None
        assigned_court = None

        if request.location.latitude and request.location.longitude:
            # Validate and geocode GPS coordinates
            if self.geocoding_service.validate_coordinates(request.location.latitude, request.location.longitude):
                geocoded_address, assigned_court = self.geocoding_service.geocode_and_determine_jurisdiction(
                    request.location.latitude, request.location.longitude
                )

        # Fallback to original jurisdiction determination if geocoding failed
        if not assigned_court:
            assigned_court = self.determine_court_jurisdiction(request.location)

        # Use geocoded address if available, otherwise use provided address
        final_address = geocoded_address.get("formatted_address") if geocoded_address else request.location.address

        # Create emergency case with enhanced location data
        emergency_case = EmergencyCase(
            user_id=user_id,
            client_profile_id=request.client_profile_id,
            case_type=request.case_type,
            detention_latitude=request.location.latitude,
            detention_longitude=request.location.longitude,
            detention_address=final_address,
            location_description=request.location.description,
            assigned_court_id=assigned_court.id if assigned_court else None,
            status="active",
            initial_notification_sent_at=datetime.utcnow(),
        )

        self.db.add(emergency_case)
        self.db.flush()  # Get the ID

        # Notify attorneys
        attorneys_notified = 0
        if assigned_court:
            attorneys_notified = self._notify_attorneys_for_court(emergency_case.id, assigned_court.id)

        # Schedule escalated notification for 1 hour from now (if not handled by periodic task)
        try:
            from app.tasks import schedule_escalated_notification

            schedule_escalated_notification.delay(emergency_case.id, delay_hours=1)
        except Exception as e:
            # Log but don't fail the case creation if scheduling fails
            print(f"Warning: Failed to schedule escalated notification for case {emergency_case.id}: {e}")

        self.db.commit()
        return emergency_case, attorneys_notified

    def _notify_attorneys_for_court(self, case_id: int, court_id: int) -> int:
        """Notify attorneys admitted to a specific court about a new case"""
        # Get the emergency case
        case = self.db.query(EmergencyCase).filter(EmergencyCase.id == case_id).first()
        if not case:
            return 0

        # Get attorneys admitted to this court
        attorneys = self.db.query(Attorney).join(Attorney.admitted_courts).filter(Court.id == court_id).all()

        attorneys_notified = 0
        for attorney in attorneys:
            try:
                # Get attorney notification preferences
                preferences = self.get_or_create_attorney_preferences(attorney.id)

                # Send immediate case notification
                results = self.notification_service.send_immediate_case_notification(
                    attorney=attorney, case=case, preferences=preferences
                )

                # Count successful notifications
                successful_channels = [r for r in results if r.status == "sent"]
                if successful_channels:
                    attorneys_notified += 1

            except Exception as e:
                # Log error but continue with other attorneys
                print(f"Failed to notify attorney {attorney.id}: {e}")
                continue

        return attorneys_notified

    def accept_case(self, attorney_id: int, case_id: int) -> bool:
        """Attorney accepts an emergency case"""
        # Verify attorney exists
        attorney = self.db.query(Attorney).filter(Attorney.id == attorney_id).first()
        if not attorney:
            raise ValueError("Attorney not found")

        # Verify case exists and is available
        case = (
            self.db.query(EmergencyCase)
            .filter(and_(EmergencyCase.id == case_id, EmergencyCase.status == "active"))
            .first()
        )
        if not case:
            raise ValueError("Case not found or not available")

        # Verify attorney is admitted to the case's court
        if case.assigned_court_id:
            is_admitted = (
                self.db.query(Attorney)
                .join(Attorney.admitted_courts)
                .filter(and_(Attorney.id == attorney_id, Court.id == case.assigned_court_id))
                .first()
            )
            if not is_admitted:
                raise ValueError("Attorney is not admitted to the required court")

        # Accept the case
        case.assigned_attorney_id = attorney_id
        case.attorney_assigned_at = datetime.utcnow()
        case.status = "attorney_assigned"

        self.db.commit()
        return True

    def deactivate_case(self, user_id: int, case_id: int, reason: Optional[str] = None) -> bool:
        """Deactivate an emergency case"""
        case = (
            self.db.query(EmergencyCase)
            .filter(
                and_(
                    EmergencyCase.id == case_id,
                    EmergencyCase.user_id == user_id,
                    EmergencyCase.status.in_(["active", "attorney_assigned"]),
                )
            )
            .first()
        )

        if not case:
            raise ValueError("Case not found or not deactivatable")

        case.status = "deactivated"
        case.deactivated_at = datetime.utcnow()

        self.db.commit()
        return True

    def get_available_cases_for_attorney(self, attorney_id: int) -> List[EmergencyCase]:
        """Get available emergency cases for an attorney"""
        attorney = self.db.query(Attorney).filter(Attorney.id == attorney_id).first()
        if not attorney:
            raise ValueError("Attorney not found")

        # Get cases for courts this attorney is admitted to
        cases = (
            self.db.query(EmergencyCase)
            .join(Court, EmergencyCase.assigned_court_id == Court.id)
            .join(Attorney.admitted_courts)
            .filter(and_(Attorney.id == attorney_id, EmergencyCase.status == "active"))
            .order_by(EmergencyCase.created_at.asc())
            .all()
        )

        return cases

    def get_unassigned_cases(self) -> List[EmergencyCase]:
        """Get all unassigned emergency cases for daily digest"""
        cases = (
            self.db.query(EmergencyCase)
            .filter(EmergencyCase.status == "active")
            .order_by(EmergencyCase.created_at.asc())
            .all()
        )
        return cases

    def get_court_coverage_stats(self) -> dict:
        """Get attorney coverage statistics per court"""
        # Query to get attorney count per court
        coverage_stats = (
            self.db.query(Court.name, Court.abbreviation, func.count(Attorney.id).label("attorney_count"))
            .outerjoin(Attorney.admitted_courts)
            .group_by(Court.id, Court.name, Court.abbreviation)
            .all()
        )

        return {
            stat.abbreviation: {"name": stat.name, "attorney_count": stat.attorney_count} for stat in coverage_stats
        }

    def send_escalated_notifications(self) -> int:
        """Send escalated notifications for cases older than 1 hour"""
        one_hour_ago = datetime.utcnow() - timedelta(hours=1)

        cases_needing_escalation = (
            self.db.query(EmergencyCase)
            .filter(
                and_(
                    EmergencyCase.status == "active",
                    EmergencyCase.created_at <= one_hour_ago,
                    or_(
                        EmergencyCase.escalated_notification_sent_at.is_(None),
                        EmergencyCase.escalated_notification_sent_at <= one_hour_ago,
                    ),
                )
            )
            .all()
        )

        notifications_sent = 0
        for case in cases_needing_escalation:
            if case.assigned_court_id:
                # Get attorneys for this court
                attorneys = (
                    self.db.query(Attorney)
                    .join(Attorney.admitted_courts)
                    .filter(Court.id == case.assigned_court_id)
                    .all()
                )

                # Calculate time waiting
                time_waiting = datetime.utcnow() - case.created_at
                hours = int(time_waiting.total_seconds() / 3600)
                minutes = int((time_waiting.total_seconds() % 3600) / 60)
                time_waiting_str = f"{hours}h {minutes}m"

                # Send escalated notifications
                for attorney in attorneys:
                    try:
                        preferences = self.get_or_create_attorney_preferences(attorney.id)

                        results = self.notification_service.send_escalated_case_notification(
                            attorney=attorney, case=case, preferences=preferences, time_waiting=time_waiting_str
                        )

                        # Count successful notifications
                        successful_channels = [r for r in results if r.status == "sent"]
                        if successful_channels:
                            notifications_sent += 1

                    except Exception as e:
                        print(f"Failed to send escalated notification to attorney {attorney.id}: {e}")
                        continue

                # Update the escalated notification timestamp
                case.escalated_notification_sent_at = datetime.utcnow()

        self.db.commit()
        return notifications_sent

    def get_or_create_attorney_preferences(self, attorney_id: int) -> AttorneyNotificationPreference:
        """Get or create attorney notification preferences"""
        preferences = (
            self.db.query(AttorneyNotificationPreference)
            .filter(AttorneyNotificationPreference.attorney_id == attorney_id)
            .first()
        )

        if not preferences:
            preferences = AttorneyNotificationPreference(attorney_id=attorney_id)
            self.db.add(preferences)
            self.db.commit()

        return preferences

    def update_attorney_preferences(self, attorney_id: int, preferences_data: dict) -> AttorneyNotificationPreference:
        """Update attorney notification preferences"""
        preferences = self.get_or_create_attorney_preferences(attorney_id)

        for key, value in preferences_data.items():
            if hasattr(preferences, key):
                setattr(preferences, key, value)

        self.db.commit()
        return preferences

    def send_daily_digest(self) -> int:
        """Send daily digest to all attorneys"""
        # Get all unassigned cases
        unassigned_cases = self.get_unassigned_cases()

        # Get court coverage stats
        coverage_stats = self.get_court_coverage_stats()

        # Get all attorneys
        attorneys = self.db.query(Attorney).all()

        notifications_sent = 0
        for attorney in attorneys:
            try:
                preferences = self.get_or_create_attorney_preferences(attorney.id)

                # Filter cases relevant to this attorney's courts
                attorney_court_ids = [court.id for court in attorney.admitted_courts]
                relevant_cases = [case for case in unassigned_cases if case.assigned_court_id in attorney_court_ids]

                # Create attorney-specific coverage stats
                attorney_coverage = {
                    court.abbreviation: coverage_stats[court.abbreviation]["attorney_count"]
                    for court in attorney.admitted_courts
                }

                results = self.notification_service.send_daily_digest(
                    attorney=attorney,
                    preferences=preferences,
                    unassigned_cases=relevant_cases,
                    attorney_coverage_stats=attorney_coverage,
                )

                # Count successful notifications
                successful_channels = [r for r in results if r.status == "sent"]
                if successful_channels:
                    notifications_sent += 1

            except Exception as e:
                print(f"Failed to send daily digest to attorney {attorney.id}: {e}")
                continue

        return notifications_sent
