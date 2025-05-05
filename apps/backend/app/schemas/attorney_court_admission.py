from pydantic import BaseModel, Field


class AttorneyCourtAdmissionBase(BaseModel):
    """Base schema for attorney-court admission relationship"""

    court_id: int = Field(
        ...,
        description="ID of the court the attorney is admitted to",
        gt=0,  # court_id must be greater than 0
    )


class AttorneyCourtAdmissionCreate(BaseModel):
    court_id: int = Field(..., ge=1, description="The ID of the court to link.")


class AttorneyCourtAdmissionResponse(BaseModel):
    """Response schema for creating an attorney court admission."""

    attorney_id: int
    court_id: int

    class Config:
        # orm_mode=True for Pydantic v1
        from_attributes = True


class AttorneyCourtAdmission(AttorneyCourtAdmissionBase):
    """Schema for an attorney-court admission with attorney ID"""

    attorney_id: int = Field(..., description="ID of the attorney")

    model_config = {"from_attributes": True}


class AttorneyCourtAdmissionRead(AttorneyCourtAdmission):
    """Schema for retrieving an attorney-court admission"""

    pass
