"""SQLAlchemy model for normalized addresses."""

from typing import TYPE_CHECKING

import sqlalchemy as sa

from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.database import Base

if TYPE_CHECKING:
    from .ice_detention_facility import IceDetentionFacility  # noqa: F401


class NormalizedAddress(Base):
    """Model for storing normalized address information from geocoding APIs."""

    __tablename__ = "normalized_addresses"

    id: Mapped[int] = mapped_column(sa.Integer, primary_key=True, index=True)
    ice_detention_facility_id: Mapped[int] = mapped_column(
        sa.Integer, sa.ForeignKey("ice_detention_facilities.id"), unique=True, nullable=False, index=True
    )
    api_source: Mapped[str] = mapped_column(
        sa.String(100), nullable=False, comment="Source of the geocoding API used (e.g., Positionstack)"
    )
    original_address_query: Mapped[str] = mapped_column(
        sa.Text, nullable=False, comment="The original, full address string used for the API query"
    )
    normalized_street_address: Mapped[str | None] = mapped_column(sa.String(255), nullable=True)
    normalized_city: Mapped[str | None] = mapped_column(sa.String(100), nullable=True)
    normalized_state: Mapped[str | None] = mapped_column(sa.String(50), nullable=True)
    normalized_zip_code: Mapped[str | None] = mapped_column(sa.String(20), nullable=True)
    county: Mapped[str] = mapped_column(
        sa.String(100), nullable=False, comment="County name returned by the geocoding API"
    )
    latitude: Mapped[float | None] = mapped_column(sa.Float, nullable=True)
    longitude: Mapped[float | None] = mapped_column(sa.Float, nullable=True)
    api_response_json: Mapped[dict | None] = mapped_column(
        JSONB, nullable=True, comment="Complete JSON response from the geocoding API for reference"
    )

    created_at: Mapped[sa.DateTime] = mapped_column(
        sa.DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[sa.DateTime] = mapped_column(
        sa.DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    # Define the one-to-one relationship to IceDetentionFacility
    # The back_populates string must match the relationship name in IceDetentionFacility
    ice_facility: Mapped["IceDetentionFacility"] = relationship(
        "IceDetentionFacility", back_populates="normalized_address_info"
    )

    def __repr__(self) -> str:
        return f"<NormalizedAddress id={self.id} facility_id={self.ice_detention_facility_id} county='{self.county}'>"
