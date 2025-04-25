from pydantic import BaseModel, Field


class AttorneyCourtAdmissionBase(BaseModel):
    """Base schema for attorney-court admission relationship"""

    court_id: int = Field(..., description="ID of the court the attorney is admitted to")


class AttorneyCourtAdmissionCreate(AttorneyCourtAdmissionBase):
    """Schema for creating a new attorney-court admission"""

    pass


class AttorneyCourtAdmission(AttorneyCourtAdmissionBase):
    """Schema for an attorney-court admission with attorney ID"""

    attorney_id: int = Field(..., description="ID of the attorney")

    model_config = {"from_attributes": True}


class AttorneyCourtAdmissionRead(AttorneyCourtAdmission):
    """Schema for retrieving an attorney-court admission"""

    pass
