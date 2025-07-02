from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field, validator


class LocationData(BaseModel):
    """Location data for emergency cases"""

    latitude: Optional[float] = Field(None, description="Latitude coordinate")
    longitude: Optional[float] = Field(None, description="Longitude coordinate")
    address: Optional[str] = Field(None, max_length=500, description="Human-readable address")
    description: Optional[str] = Field(None, description="Additional location details")


class EmergencyStatusResponse(BaseModel):
    """Response schema for emergency status check"""

    has_emergency_contacts: bool = Field(..., description="Whether user has emergency contacts configured")
    has_client_profiles: bool = Field(..., description="Whether user has client profiles configured")
    active_emergency_case_id: Optional[int] = Field(None, description="ID of active emergency case if any")
    active_case_status: Optional[str] = Field(None, description="Status of active case")
    assigned_attorney_name: Optional[str] = Field(None, description="Name of assigned attorney if any")
    assigned_court_name: Optional[str] = Field(None, description="Name of assigned court if any")
    can_activate_emergency: bool = Field(..., description="Whether emergency can be activated")

    model_config = ConfigDict(from_attributes=True)


class EmergencyActivationRequest(BaseModel):
    """Request schema for emergency activation"""

    client_profile_id: int = Field(..., description="ID of the client profile for this emergency")
    case_type: str = Field(..., description="Type of emergency: 'self' or 'loved_one'")
    location: LocationData = Field(..., description="Location information for the emergency")

    @validator("case_type")
    def validate_case_type(cls, v):
        if v not in ["self", "loved_one"]:
            raise ValueError('case_type must be either "self" or "loved_one"')
        return v


class EmergencyActivationResponse(BaseModel):
    """Response schema for emergency activation"""

    case_id: int = Field(..., description="ID of the created emergency case")
    status: str = Field(..., description="Current status of the case")
    assigned_court_name: Optional[str] = Field(None, description="Name of assigned court")
    message: str = Field(..., description="Status message for the user")
    attorneys_notified_count: int = Field(0, description="Number of attorneys notified")

    model_config = ConfigDict(from_attributes=True)


class EmergencyStatusUpdate(BaseModel):
    """Schema for emergency case status updates"""

    case_id: int = Field(..., description="ID of the emergency case")
    status: str = Field(..., description="Current status")
    assigned_attorney_name: Optional[str] = Field(None, description="Name of assigned attorney")
    assigned_court_name: Optional[str] = Field(None, description="Name of assigned court")
    last_updated: datetime = Field(..., description="When the status was last updated")
    message: str = Field(..., description="Human-readable status message")

    model_config = ConfigDict(from_attributes=True)


class EmergencyDeactivationRequest(BaseModel):
    """Request schema for emergency deactivation"""

    reason: Optional[str] = Field(None, description="Reason for deactivation")


class EmergencyDeactivationResponse(BaseModel):
    """Response schema for emergency deactivation"""

    success: bool = Field(..., description="Whether deactivation was successful")
    message: str = Field(..., description="Confirmation message")

    model_config = ConfigDict(from_attributes=True)


class AttorneyCaseAcceptanceRequest(BaseModel):
    """Request schema for attorney accepting a case"""

    message: Optional[str] = Field(None, description="Message from attorney to client")


class AttorneyCaseAcceptanceResponse(BaseModel):
    """Response schema for attorney accepting a case"""

    success: bool = Field(..., description="Whether acceptance was successful")
    message: str = Field(..., description="Confirmation message")
    case_id: int = Field(..., description="ID of the accepted case")
    client_contact_info: dict = Field(..., description="Client and emergency contact information")

    model_config = ConfigDict(from_attributes=True)


class AttorneyNotificationPreferenceRequest(BaseModel):
    """Request schema for updating attorney notification preferences"""

    email_enabled: bool = Field(True, description="Enable email notifications")
    sms_enabled: bool = Field(True, description="Enable SMS notifications")
    push_enabled: bool = Field(True, description="Enable push notifications")
    sms_phone_number: Optional[str] = Field(None, description="Phone number for SMS notifications")
    daily_digest_enabled: bool = Field(True, description="Enable daily digest notifications")
    escalated_notifications_enabled: bool = Field(True, description="Enable escalated notifications")


class AttorneyNotificationPreferenceResponse(BaseModel):
    """Response schema for attorney notification preferences"""

    attorney_id: int = Field(..., description="ID of the attorney")
    email_enabled: bool = Field(..., description="Email notifications enabled")
    sms_enabled: bool = Field(..., description="SMS notifications enabled")
    push_enabled: bool = Field(..., description="Push notifications enabled")
    sms_phone_number: Optional[str] = Field(None, description="Phone number for SMS")
    daily_digest_enabled: bool = Field(..., description="Daily digest enabled")
    escalated_notifications_enabled: bool = Field(..., description="Escalated notifications enabled")
    created_at: datetime = Field(..., description="When preferences were created")
    updated_at: datetime = Field(..., description="When preferences were last updated")

    model_config = ConfigDict(from_attributes=True)


class CourtJurisdictionResponse(BaseModel):
    """Response schema for court jurisdiction lookup"""

    court_id: int = Field(..., description="ID of the court")
    court_name: str = Field(..., description="Name of the court")
    court_abbreviation: str = Field(..., description="Court abbreviation")
    confidence: float = Field(..., description="Confidence level of the match (0.0-1.0)")
    message: str = Field(..., description="Human-readable explanation")

    model_config = ConfigDict(from_attributes=True)


class AvailableCaseResponse(BaseModel):
    """Response schema for available emergency cases for attorneys"""

    case_id: int = Field(..., description="ID of the emergency case")
    case_type: str = Field(..., description="Type of emergency")
    location_description: str = Field(..., description="Location description")
    court_name: str = Field(..., description="Assigned court name")
    created_at: datetime = Field(..., description="When the case was created")
    urgency_level: str = Field(..., description="Urgency level based on time elapsed")

    model_config = ConfigDict(from_attributes=True)


class DailyDigestResponse(BaseModel):
    """Response schema for daily digest of unassigned cases"""

    unassigned_cases: List[AvailableCaseResponse] = Field(..., description="List of unassigned cases")
    court_coverage_stats: dict = Field(..., description="Statistics about attorney coverage per court")
    total_unassigned: int = Field(..., description="Total number of unassigned cases")
    digest_date: datetime = Field(..., description="Date of the digest")

    model_config = ConfigDict(from_attributes=True)
