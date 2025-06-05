from sqlalchemy import TIMESTAMP, Date, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.database import Base


class Client(Base):
    """
    Client model representing an individual who may file a habeas corpus petition
    """

    __tablename__ = "clients"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    country_of_birth: Mapped[str] = mapped_column(String(100), nullable=False)
    nationality: Mapped[str | None] = mapped_column(String(100), nullable=True)
    birth_date: Mapped[Date] = mapped_column(Date, nullable=False)
    alien_registration_number: Mapped[str | None] = mapped_column(String(20), nullable=True, unique=True)
    passport_number: Mapped[str | None] = mapped_column(String(20), nullable=True, unique=True)
    school_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    student_id_number: Mapped[str | None] = mapped_column(String(50), nullable=True, unique=True)
    created_at: Mapped[TIMESTAMP] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[TIMESTAMP] = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )
    user_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )

    # Relationship with emergency contacts
    emergency_contacts = relationship("EmergencyContact", back_populates="client", cascade="all, delete-orphan")
    user = relationship("User", back_populates="client")

    def __repr__(self):
        return f"<Client(id={self.id}, first_name='{self.first_name}', last_name='{self.last_name}')>"
