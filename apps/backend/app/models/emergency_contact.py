from sqlalchemy import Column, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship as orm_relationship
from sqlalchemy.sql import func
from sqlalchemy.sql.sqltypes import TIMESTAMP

from app.database import Base


class EmergencyContact(Base):
    """
    Emergency contact model representing a person to contact in case of emergency for a client
    """

    __tablename__ = "emergency_contacts"

    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey("clients.id", ondelete="CASCADE"), nullable=False)
    full_name = Column(String(255), nullable=False)
    relationship_to_client = Column(String(50), nullable=False)
    phone_number = Column(String(20), nullable=False)
    email = Column(String(255), nullable=True)
    address = Column(String(255), nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationship with client
    client = orm_relationship("Client", back_populates="emergency_contacts")

    def __repr__(self):
        return f"<EmergencyContact(id={self.id}, full_name='{self.full_name}', relationship='{self.relationship_to_client}')>"
