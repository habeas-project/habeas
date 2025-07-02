from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    pass


class EmergencyCase(Base):
    """
    Emergency case model representing an emergency activation and its lifecycle
    """

    __tablename__ = "emergency_cases"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    client_profile_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("client_profiles.id", ondelete="CASCADE"), nullable=False, index=True
    )

    # Case details
    case_type: Mapped[str] = mapped_column(
        String(20), nullable=False, index=True, comment="Type of emergency: 'self' or 'loved_one'"
    )
    status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default="active",
        index=True,
        comment="Status: active, attorney_assigned, resolved, deactivated",
    )

    # Location information
    detention_latitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    detention_longitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    detention_address: Mapped[str | None] = mapped_column(String(500), nullable=True)
    location_description: Mapped[str | None] = mapped_column(
        Text, nullable=True, comment="Additional location details provided by user"
    )

    # Court assignment
    assigned_court_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("courts.id"), nullable=True, index=True)

    # Attorney assignment
    assigned_attorney_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("attorneys.id"), nullable=True, index=True
    )
    attorney_assigned_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Notification tracking
    initial_notification_sent_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    escalated_notification_sent_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Case lifecycle timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    deactivated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    user = relationship("User", back_populates="emergency_cases")
    client_profile = relationship("ClientProfile", back_populates="emergency_cases")
    assigned_court = relationship("Court", foreign_keys=[assigned_court_id])
    assigned_attorney = relationship("Attorney", foreign_keys=[assigned_attorney_id])

    def __repr__(self):
        return f"<EmergencyCase(id={self.id}, user_id={self.user_id}, status='{self.status}', case_type='{self.case_type}')>"


class AttorneyNotificationPreference(Base):
    """
    Attorney notification preferences for different types of emergency notifications
    """

    __tablename__ = "attorney_notification_preferences"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    attorney_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("attorneys.id", ondelete="CASCADE"), nullable=False, index=True
    )

    # Notification channels
    email_enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    sms_enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    push_enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Phone number for SMS (can be different from attorney's main phone)
    sms_phone_number: Mapped[str | None] = mapped_column(String(20), nullable=True)

    # Notification timing preferences
    daily_digest_enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    escalated_notifications_enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Metadata
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    # Relationships
    attorney = relationship("Attorney", back_populates="notification_preferences")

    def __repr__(self):
        return f"<AttorneyNotificationPreference(id={self.id}, attorney_id={self.attorney_id})>"
