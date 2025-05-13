from sqlalchemy import TIMESTAMP, ForeignKey, Integer, String, Text  # Keep TIMESTAMP if used directly
from sqlalchemy.orm import Mapped, mapped_column  # Import mapped_column
from sqlalchemy.orm import relationship as orm_relationship
from sqlalchemy.sql import func

from app.database import Base


class EmergencyContact(Base):
    """
    Emergency contact model representing a person to contact in case of emergency for a client
    """

    __tablename__ = "emergency_contacts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    client_id: Mapped[int] = mapped_column(Integer, ForeignKey("clients.id", ondelete="CASCADE"), nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    relationship: Mapped[str] = mapped_column(String(50), nullable=False)
    phone_number: Mapped[str] = mapped_column(String(20), nullable=False)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    address: Mapped[str | None] = mapped_column(String(255), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[TIMESTAMP] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[TIMESTAMP] = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    # Relationship with client
    client = orm_relationship("Client", back_populates="emergency_contacts")

    def __repr__(self):
        return f"<EmergencyContact(id={self.id}, full_name='{self.full_name}', relationship='{self.relationship}')>"
