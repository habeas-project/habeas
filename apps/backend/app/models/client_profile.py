from sqlalchemy import TIMESTAMP, Boolean, Date, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.database import Base


class ClientProfile(Base):
    """
    Client profile model supporting multiple profiles per user.
    Replaces Client model with enhanced multi-profile functionality.
    """

    __tablename__ = "client_profiles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )

    # Profile identification - NEW fields for multi-profile support
    profile_name: Mapped[str] = mapped_column(
        String(255), nullable=False, comment="Display name for profile (e.g., 'John Doe', 'My Son')"
    )
    is_self: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False, comment="True if this profile represents the account holder"
    )

    # Existing Client fields (maintained for compatibility)
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    country_of_birth: Mapped[str] = mapped_column(String(100), nullable=False)
    nationality: Mapped[str | None] = mapped_column(String(100), nullable=True)
    birth_date: Mapped[Date] = mapped_column(Date, nullable=False)
    alien_registration_number: Mapped[str | None] = mapped_column(String(20), nullable=True, unique=True)
    passport_number: Mapped[str | None] = mapped_column(String(20), nullable=True, unique=True)
    school_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    student_id_number: Mapped[str | None] = mapped_column(String(50), nullable=True, unique=True)

    # Metadata
    created_at: Mapped[TIMESTAMP] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[TIMESTAMP] = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    # Relationships
    user = relationship("User", back_populates="client_profiles")
    emergency_contacts = relationship("EmergencyContact", back_populates="client_profile", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<ClientProfile(id={self.id}, profile_name='{self.profile_name}', first_name='{self.first_name}', last_name='{self.last_name}', is_self={self.is_self})>"
