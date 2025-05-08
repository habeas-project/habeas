"""SQLAlchemy model for district court contact information."""

from typing import TYPE_CHECKING

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, relationship

from app.database import Base

if TYPE_CHECKING:
    from .court import Court


class DistrictCourtContact(Base):
    """Model for district court contact details."""

    __tablename__ = "district_court_contacts"

    id: Mapped[int] = Column(Integer, primary_key=True, index=True)
    court_id: Mapped[int] = Column(Integer, ForeignKey("courts.id"), nullable=False, index=True)
    location_name: Mapped[str | None] = Column(String(255), nullable=True)
    address: Mapped[str | None] = Column(String, nullable=True)
    phone: Mapped[str | None] = Column(String(50), nullable=True)
    email: Mapped[str | None] = Column(String(255), nullable=True)
    hours: Mapped[str | None] = Column(String(255), nullable=True)

    created_at: Mapped[DateTime] = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[DateTime] = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # Define the many-to-one relationship to Court
    court: Mapped["Court"] = relationship("Court", back_populates="contact_details")

    def __repr__(self) -> str:
        """Return a string representation of the DistrictCourtContact."""
        return f"<DistrictCourtContact id={self.id} court_id={self.court_id} location='{self.location_name}'>"
