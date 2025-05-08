from typing import TYPE_CHECKING

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, relationship

from app.database import Base

if TYPE_CHECKING:
    from .court import Court  # noqa: F401
    from .normalized_address import NormalizedAddress  # noqa: F401


class IceDetentionFacility(Base):
    __tablename__ = "ice_detention_facilities"

    id: Mapped[int] = Column(Integer, primary_key=True, index=True)
    name: Mapped[str] = Column(String(255), nullable=False, index=True)
    address: Mapped[str | None] = Column(String, nullable=True)  # Original address from Excel
    city: Mapped[str | None] = Column(String(100), nullable=True)
    state: Mapped[str | None] = Column(String(2), nullable=True)  # 2-letter state code
    zip_code: Mapped[str | None] = Column(String(20), nullable=True)
    aor: Mapped[str | None] = Column(String(255), nullable=True, name="aor")  # Area of Responsibility
    facility_type_detailed: Mapped[str | None] = Column(String(255), nullable=True)
    gender_capacity: Mapped[str | None] = Column(String(50), nullable=True)  # e.g., "Male", "Female", "Male/Female"

    # Foreign Key to courts table
    court_id: Mapped[int | None] = Column(Integer, ForeignKey("courts.id"), nullable=True, index=True)

    created_at: Mapped[DateTime] = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[DateTime] = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    # One-to-one relationship to NormalizedAddress
    # The back_populates string must match the relationship name in NormalizedAddress
    normalized_address_info: Mapped["NormalizedAddress"] = relationship(
        "NormalizedAddress", back_populates="ice_facility", cascade="all, delete-orphan"
    )

    # Many-to-one relationship to Court
    court: Mapped["Court"] = relationship("Court")

    def __repr__(self):
        return f"<IceDetentionFacility id={self.id} name='{self.name}'>"
