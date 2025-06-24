from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.emergency_case import (
    AttorneyCaseAcceptanceRequest,
    AttorneyCaseAcceptanceResponse,
    AttorneyNotificationPreferenceRequest,
    AttorneyNotificationPreferenceResponse,
    AvailableCaseResponse,
    CourtJurisdictionResponse,
    DailyDigestResponse,
    EmergencyActivationRequest,
    EmergencyActivationResponse,
    EmergencyDeactivationRequest,
    EmergencyDeactivationResponse,
    EmergencyStatusResponse,
    EmergencyStatusUpdate,
    LocationData,
)
from app.services.emergency_service import EmergencyService

router = APIRouter(
    prefix="/emergency",
    tags=["emergency"],
    responses={404: {"description": "Not found"}},
)


@router.get("/users/{user_id}/status", response_model=EmergencyStatusResponse)
def get_user_emergency_status(user_id: int = Path(..., description="ID of the user"), db: Session = Depends(get_db)):
    """Check emergency information status for a user"""
    try:
        service = EmergencyService(db)
        return service.get_user_emergency_status(user_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception:
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/cases", response_model=EmergencyActivationResponse, status_code=status.HTTP_201_CREATED)
def create_emergency_case(
    request: EmergencyActivationRequest,
    user_id: int = Query(..., description="ID of the user creating the emergency"),
    db: Session = Depends(get_db),
):
    """Create emergency case with location"""
    try:
        service = EmergencyService(db)
        emergency_case, attorneys_notified = service.create_emergency_case(user_id, request)

        court_name = None
        if emergency_case.assigned_court:
            court_name = emergency_case.assigned_court.name

        message = "Case posted - attorneys notified"
        if attorneys_notified == 0:
            message = "Case posted - no attorneys available for this jurisdiction"

        return EmergencyActivationResponse(
            case_id=emergency_case.id,
            status=emergency_case.status,
            assigned_court_name=court_name,
            message=message,
            attorneys_notified_count=attorneys_notified,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception:
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/cases/{case_id}/deactivate", response_model=EmergencyDeactivationResponse)
def deactivate_emergency_case(
    request: EmergencyDeactivationRequest,
    case_id: int = Path(..., description="ID of the emergency case"),
    user_id: int = Query(..., description="ID of the user deactivating the case"),
    db: Session = Depends(get_db),
):
    """Deactivate emergency case"""
    try:
        service = EmergencyService(db)
        success = service.deactivate_case(user_id, case_id, request.reason)

        return EmergencyDeactivationResponse(
            success=success, message="Emergency case has been successfully deactivated"
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception:
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/cases/{case_id}/status", response_model=EmergencyStatusUpdate)
def get_emergency_case_status(
    case_id: int = Path(..., description="ID of the emergency case"), db: Session = Depends(get_db)
):
    """Get detailed emergency case status"""
    try:
        from app.models import EmergencyCase

        case = db.query(EmergencyCase).filter(EmergencyCase.id == case_id).first()
        if not case:
            raise HTTPException(status_code=404, detail="Emergency case not found")

        assigned_attorney_name = None
        assigned_court_name = None

        if case.assigned_attorney:
            assigned_attorney_name = case.assigned_attorney.name
        if case.assigned_court:
            assigned_court_name = case.assigned_court.name

        # Generate status message
        if case.status == "attorney_assigned":
            message = f"Attorney accepted case: {assigned_attorney_name}"
        elif case.status == "active":
            message = "Case posted - attorneys notified"
        elif case.status == "deactivated":
            message = "Case deactivated"
        else:
            message = f"Case status: {case.status}"

        return EmergencyStatusUpdate(
            case_id=case.id,
            status=case.status,
            assigned_attorney_name=assigned_attorney_name,
            assigned_court_name=assigned_court_name,
            last_updated=case.updated_at,
            message=message,
        )
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/cases/available/{court_id}", response_model=List[AvailableCaseResponse])
def get_available_cases_for_court(
    court_id: int = Path(..., description="ID of the court"),
    attorney_id: int = Query(..., description="ID of the attorney"),
    db: Session = Depends(get_db),
):
    """Get available cases for court-admitted attorneys"""
    try:
        service = EmergencyService(db)
        cases = service.get_available_cases_for_attorney(attorney_id)

        # Filter by court if specified
        if court_id:
            cases = [case for case in cases if case.assigned_court_id == court_id]

        response_cases = []
        for case in cases:
            # Calculate urgency level based on time elapsed
            hours_elapsed = (datetime.utcnow() - case.created_at).total_seconds() / 3600
            if hours_elapsed < 1:
                urgency_level = "urgent"
            elif hours_elapsed < 6:
                urgency_level = "high"
            elif hours_elapsed < 24:
                urgency_level = "medium"
            else:
                urgency_level = "low"

            location_desc = case.detention_address or "Location information provided"
            court_name = case.assigned_court.name if case.assigned_court else "Unknown Court"

            response_cases.append(
                AvailableCaseResponse(
                    case_id=case.id,
                    case_type=case.case_type,
                    location_description=location_desc,
                    court_name=court_name,
                    created_at=case.created_at,
                    urgency_level=urgency_level,
                )
            )

        return response_cases
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception:
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/cases/{case_id}/accept", response_model=AttorneyCaseAcceptanceResponse)
def accept_emergency_case(
    request: AttorneyCaseAcceptanceRequest,
    case_id: int = Path(..., description="ID of the emergency case"),
    attorney_id: int = Query(..., description="ID of the attorney accepting the case"),
    db: Session = Depends(get_db),
):
    """Attorney accepts case (voluntary)"""
    try:
        service = EmergencyService(db)
        success = service.accept_case(attorney_id, case_id)

        # Get case details to return client contact info
        from app.models import EmergencyCase

        case = db.query(EmergencyCase).filter(EmergencyCase.id == case_id).first()

        if not case or not case.client_profile:
            raise HTTPException(status_code=404, detail="Case or client profile not found")

        # Build client contact info
        client_contact_info = {
            "profile_name": case.client_profile.profile_name,
            "first_name": case.client_profile.first_name,
            "last_name": case.client_profile.last_name,
            "emergency_contacts": [],
        }

        for contact in case.client_profile.emergency_contacts:
            client_contact_info["emergency_contacts"].append(
                {
                    "name": contact.full_name,
                    "relationship": contact.relationship,
                    "phone": contact.phone_number,
                    "email": contact.email,
                }
            )

        return AttorneyCaseAcceptanceResponse(
            success=success,
            message="Case accepted successfully. Client contact information provided.",
            case_id=case_id,
            client_contact_info=client_contact_info,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception:
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/courts/jurisdiction", response_model=CourtJurisdictionResponse)
def determine_court_jurisdiction(
    latitude: float = Query(..., description="Latitude coordinate"),
    longitude: float = Query(..., description="Longitude coordinate"),
    db: Session = Depends(get_db),
):
    """Determine district court by location"""
    try:
        service = EmergencyService(db)
        location = LocationData(latitude=latitude, longitude=longitude, address=None, description=None)
        court = service.determine_court_jurisdiction(location)

        if not court:
            raise HTTPException(status_code=404, detail="No court jurisdiction found for this location")

        return CourtJurisdictionResponse(
            court_id=court.id,
            court_name=court.name,
            court_abbreviation=court.abbreviation,
            confidence=0.8,  # Placeholder confidence score
            message=f"Location falls under jurisdiction of {court.name}",
        )
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/cases/unassigned", response_model=List[AvailableCaseResponse])
def get_unassigned_cases(db: Session = Depends(get_db)):
    """Get unassigned cases for daily digest"""
    try:
        service = EmergencyService(db)
        cases = service.get_unassigned_cases()

        response_cases = []
        for case in cases:
            # Calculate urgency level
            hours_elapsed = (datetime.utcnow() - case.created_at).total_seconds() / 3600
            if hours_elapsed < 1:
                urgency_level = "urgent"
            elif hours_elapsed < 6:
                urgency_level = "high"
            elif hours_elapsed < 24:
                urgency_level = "medium"
            else:
                urgency_level = "low"

            location_desc = case.detention_address or "Location information provided"
            court_name = case.assigned_court.name if case.assigned_court else "Unknown Court"

            response_cases.append(
                AvailableCaseResponse(
                    case_id=case.id,
                    case_type=case.case_type,
                    location_description=location_desc,
                    court_name=court_name,
                    created_at=case.created_at,
                    urgency_level=urgency_level,
                )
            )

        return response_cases
    except Exception:
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/daily-digest", response_model=DailyDigestResponse)
def get_daily_digest(db: Session = Depends(get_db)):
    """Send daily digest of unassigned cases"""
    try:
        service = EmergencyService(db)

        # Get unassigned cases
        cases = service.get_unassigned_cases()
        response_cases = []

        for case in cases:
            hours_elapsed = (datetime.utcnow() - case.created_at).total_seconds() / 3600
            if hours_elapsed < 1:
                urgency_level = "urgent"
            elif hours_elapsed < 6:
                urgency_level = "high"
            elif hours_elapsed < 24:
                urgency_level = "medium"
            else:
                urgency_level = "low"

            location_desc = case.detention_address or "Location information provided"
            court_name = case.assigned_court.name if case.assigned_court else "Unknown Court"

            response_cases.append(
                AvailableCaseResponse(
                    case_id=case.id,
                    case_type=case.case_type,
                    location_description=location_desc,
                    court_name=court_name,
                    created_at=case.created_at,
                    urgency_level=urgency_level,
                )
            )

        # Get court coverage stats
        court_coverage_stats = service.get_court_coverage_stats()

        return DailyDigestResponse(
            unassigned_cases=response_cases,
            court_coverage_stats=court_coverage_stats,
            total_unassigned=len(response_cases),
            digest_date=datetime.utcnow(),
        )
    except Exception:
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/attorneys/{attorney_id}/preferences", response_model=AttorneyNotificationPreferenceResponse)
def get_attorney_notification_preferences(
    attorney_id: int = Path(..., description="ID of the attorney"), db: Session = Depends(get_db)
):
    """Get attorney notification preferences"""
    try:
        service = EmergencyService(db)
        preferences = service.get_or_create_attorney_preferences(attorney_id)

        return AttorneyNotificationPreferenceResponse(
            attorney_id=preferences.attorney_id,
            email_enabled=preferences.email_enabled,
            sms_enabled=preferences.sms_enabled,
            push_enabled=preferences.push_enabled,
            sms_phone_number=preferences.sms_phone_number,
            daily_digest_enabled=preferences.daily_digest_enabled,
            escalated_notifications_enabled=preferences.escalated_notifications_enabled,
            created_at=preferences.created_at,
            updated_at=preferences.updated_at,
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception:
        raise HTTPException(status_code=500, detail="Internal server error")


@router.put("/attorneys/{attorney_id}/preferences", response_model=AttorneyNotificationPreferenceResponse)
def update_attorney_notification_preferences(
    request: AttorneyNotificationPreferenceRequest,
    attorney_id: int = Path(..., description="ID of the attorney"),
    db: Session = Depends(get_db),
):
    """Update attorney notification preferences"""
    try:
        service = EmergencyService(db)
        preferences = service.update_attorney_preferences(attorney_id, request.model_dump())

        return AttorneyNotificationPreferenceResponse(
            attorney_id=preferences.attorney_id,
            email_enabled=preferences.email_enabled,
            sms_enabled=preferences.sms_enabled,
            push_enabled=preferences.push_enabled,
            sms_phone_number=preferences.sms_phone_number,
            daily_digest_enabled=preferences.daily_digest_enabled,
            escalated_notifications_enabled=preferences.escalated_notifications_enabled,
            created_at=preferences.created_at,
            updated_at=preferences.updated_at,
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception:
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/notifications/escalated", status_code=status.HTTP_200_OK)
def send_escalated_notifications(db: Session = Depends(get_db)):
    """Send 1-hour follow-up notifications"""
    try:
        service = EmergencyService(db)
        notifications_sent = service.send_escalated_notifications()

        return {"success": True, "message": f"Sent escalated notifications for {notifications_sent} attorneys"}
    except Exception:
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/notifications/daily-digest", status_code=status.HTTP_200_OK)
def send_daily_digest_notifications(db: Session = Depends(get_db)):
    """Send daily digest notifications to all attorneys"""
    try:
        service = EmergencyService(db)
        notifications_sent = service.send_daily_digest()

        return {"success": True, "message": f"Sent daily digest to {notifications_sent} attorneys"}
    except Exception:
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/notifications/test-configuration")
def test_notification_configuration():
    """Test notification service configuration"""
    try:
        from app.services.notification_service import NotificationService

        notification_service = NotificationService()
        config_status = notification_service.test_configuration()

        return {"success": True, "configuration": config_status, "message": "Notification service configuration tested"}
    except Exception as e:
        return {"success": False, "error": str(e), "message": "Failed to test notification configuration"}


# Background Job Management Endpoints


@router.post("/jobs/escalated-notifications", status_code=status.HTTP_200_OK)
def trigger_escalated_notifications_job():
    """Manually trigger escalated notifications background job"""
    try:
        from app.tasks import send_escalated_notifications

        # Trigger the Celery task asynchronously
        task = send_escalated_notifications.delay()

        return {
            "success": True,
            "message": "Escalated notifications job triggered",
            "task_id": task.id,
            "status": "queued",
        }
    except Exception as e:
        return {"success": False, "error": str(e), "message": "Failed to trigger escalated notifications job"}


@router.post("/jobs/daily-digest", status_code=status.HTTP_200_OK)
def trigger_daily_digest_job():
    """Manually trigger daily digest background job"""
    try:
        from app.tasks import send_daily_digest

        # Trigger the Celery task asynchronously
        task = send_daily_digest.delay()

        return {"success": True, "message": "Daily digest job triggered", "task_id": task.id, "status": "queued"}
    except Exception as e:
        return {"success": False, "error": str(e), "message": "Failed to trigger daily digest job"}


@router.post("/jobs/schedule-escalated/{case_id}", status_code=status.HTTP_200_OK)
def schedule_case_escalated_notification(
    case_id: int = Path(..., description="ID of the emergency case"),
    delay_hours: int = Query(1, description="Hours to wait before sending notification"),
):
    """Schedule escalated notification for a specific case"""
    try:
        from app.tasks import schedule_escalated_notification

        # Schedule the notification
        task = schedule_escalated_notification.delay(case_id, delay_hours)

        return {
            "success": True,
            "message": f"Escalated notification scheduled for case {case_id} in {delay_hours} hours",
            "task_id": task.id,
            "case_id": case_id,
            "delay_hours": delay_hours,
            "status": "scheduled",
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": f"Failed to schedule escalated notification for case {case_id}",
        }


@router.get("/jobs/{task_id}/status")
def get_job_status(task_id: str = Path(..., description="Celery task ID")):
    """Get status of a background job"""
    try:
        from app.celery_app import celery_app

        # Get task result
        task_result = celery_app.AsyncResult(task_id)

        return {
            "task_id": task_id,
            "status": task_result.status,
            "result": task_result.result if task_result.ready() else None,
            "ready": task_result.ready(),
            "successful": task_result.successful() if task_result.ready() else None,
            "failed": task_result.failed() if task_result.ready() else None,
        }
    except Exception as e:
        return {"task_id": task_id, "status": "error", "error": str(e), "message": "Failed to get job status"}


@router.get("/jobs/health-check")
def celery_health_check():
    """Check Celery worker health status"""
    try:
        from app.tasks import health_check

        # Trigger health check task with short timeout
        task = health_check.apply_async(expires=30)  # 30 second timeout

        # Wait for result with timeout
        try:
            result = task.get(timeout=10)
            return {
                "success": True,
                "celery_status": "healthy",
                "worker_response": result,
                "message": "Celery workers are operational",
            }
        except Exception as timeout_error:
            return {
                "success": False,
                "celery_status": "unhealthy",
                "error": str(timeout_error),
                "message": "Celery workers are not responding",
            }

    except Exception as e:
        return {"success": False, "celery_status": "error", "error": str(e), "message": "Failed to check Celery health"}


@router.get("/jobs/stats")
def get_job_statistics():
    """Get background job statistics and queue information"""
    try:
        from app.celery_app import celery_app

        # Get basic Celery stats
        inspect = celery_app.control.inspect()

        # Get active tasks
        active_tasks = inspect.active()

        # Get scheduled tasks
        scheduled_tasks = inspect.scheduled()

        # Get worker stats
        stats = inspect.stats()

        return {
            "success": True,
            "active_tasks": active_tasks or {},
            "scheduled_tasks": scheduled_tasks or {},
            "worker_stats": stats or {},
            "message": "Job statistics retrieved successfully",
        }
    except Exception as e:
        return {"success": False, "error": str(e), "message": "Failed to retrieve job statistics"}
