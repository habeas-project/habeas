from sqlalchemy import Boolean, Column, DateTime, Integer, String, func
from sqlalchemy.orm import relationship

from app.database import Base


class User(Base):
    """User model for authentication via AWS Cognito"""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    cognito_id = Column(String(36), unique=True, nullable=False, index=True)
    user_type = Column(String(20), nullable=False, index=True)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())

    # Relationships
    attorney = relationship("Attorney", back_populates="user", uselist=False)
    client = relationship("Client", back_populates="user", uselist=False)
