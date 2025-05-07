from typing import TYPE_CHECKING

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, relationship

from app.database import Base

if TYPE_CHECKING:
    from .court import Court


class DistrictCourtContact(Base):
    __tablename__ = "district_court_contacts"

    id = Column(Integer, primary_key=True, index=True)
    location_name = Column(String(255), nullable=True)
    address = Column(String, nullable=True)  # Using String without length for potentially longer addresses
    phone = Column(String(50), nullable=True)
    email = Column(String(255), nullable=True)
    hours = Column(String(255), nullable=True)

    court_id = Column(Integer, ForeignKey("courts.id"), nullable=False, index=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationship to Court
    court: Mapped["Court"] = relationship("Court", back_populates="contact_details")

    def __repr__(self):
        return f"<DistrictCourtContact id={self.id} court_id={self.court_id} location='{self.location_name}'>"
