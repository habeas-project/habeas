from sqlalchemy import Boolean, DateTime, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class User(Base):
    """User model for authentication via AWS Cognito"""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    cognito_id: Mapped[str] = mapped_column(String(36), unique=True, nullable=False, index=True)
    user_type: Mapped[str] = mapped_column(String(20), nullable=False, index=True)  # Keep for compatibility
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )

    # NEW: Enhanced role management for hybrid architecture
    primary_role: Mapped[str | None] = mapped_column(
        String(20), nullable=True, index=True, comment="Primary role: attorney, client_helper, or admin"
    )

    # Relationships
    attorney = relationship("Attorney", back_populates="user", uselist=False)
    admin = relationship("Admin", back_populates="user", uselist=False)
    client_profiles = relationship("ClientProfile", back_populates="user", cascade="all, delete-orphan")
