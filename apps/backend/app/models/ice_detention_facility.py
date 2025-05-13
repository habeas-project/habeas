from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.normalized_address import NormalizedAddress

if TYPE_CHECKING:
    from .court import Court  # noqa: F401


class IceDetentionFacility(Base):
    __tablename__ = "ice_detention_facilities"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    address: Mapped[str | None] = mapped_column(String, nullable=True)  # Original address from Excel
    city: Mapped[str | None] = mapped_column(String(100), nullable=True)
    state: Mapped[str | None] = mapped_column(String(2), nullable=True)  # 2-letter state code
    zip_code: Mapped[str | None] = mapped_column(String(20), nullable=True)
    aor: Mapped[str | None] = mapped_column(String(255), nullable=True, name="aor")  # Area of Responsibility
    facility_type_detailed: Mapped[str | None] = mapped_column(String(255), nullable=True)
    gender_capacity: Mapped[str | None] = mapped_column(
        String(50), nullable=True
    )  # e.g., "Male", "Female", "Male/Female"

    # Foreign Key to courts table
    court_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("courts.id"), nullable=True, index=True)

    # Foreign Key to normalized_addresses table for one-to-one relationship
    normalized_address_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("normalized_addresses.id"), nullable=True, unique=True, index=True
    )

    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    # One-to-one relationship to NormalizedAddress
    normalized_address_info: Mapped["NormalizedAddress"] = relationship(
        "NormalizedAddress", foreign_keys=[normalized_address_id]
    )

    # Many-to-one relationship to Court
    court: Mapped["Court"] = relationship("Court")

    def __repr__(self):
        return f"<IceDetentionFacility id={self.id} name='{self.name}'>"
