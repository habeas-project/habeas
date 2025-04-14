from sqlalchemy import Column, Date, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.sql.sqltypes import TIMESTAMP

from app.database import Base


class Client(Base):
    """
    Client model representing an individual who may file a habeas corpus petition
    """

    __tablename__ = "clients"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    country_of_birth = Column(String(100), nullable=False)
    nationality = Column(String(100), nullable=True)
    birth_date = Column(Date, nullable=False)
    alien_registration_number = Column(String(20), nullable=True, unique=True)
    passport_number = Column(String(20), nullable=True, unique=True)
    school_name = Column(String(255), nullable=True)
    student_id_number = Column(String(50), nullable=True, unique=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationship with emergency contacts
    emergency_contacts = relationship("EmergencyContact", back_populates="client", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Client(id={self.id}, first_name='{self.first_name}', last_name='{self.last_name}')>"
