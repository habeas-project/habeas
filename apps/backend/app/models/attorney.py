from typing import TYPE_CHECKING, List

from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, relationship
from sqlalchemy.sql import func
from sqlalchemy.sql.sqltypes import TIMESTAMP

from app.database import Base
from app.models.attorney_court_admission import attorney_court_admission_table

if TYPE_CHECKING:
    from app.models.court import Court


class Attorney(Base):
    """
    Attorney model representing a legal professional who can file habeas corpus petitions
    """

    __tablename__ = "attorneys"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    phone_number = Column(String(20), nullable=False)
    email = Column(String(255), nullable=False, unique=True)
    zip_code = Column(String(10), nullable=False)
    state = Column(String(2), nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)

    # Define the many-to-many relationship to Court using Mapped
    admitted_courts: Mapped[List["Court"]] = relationship(
        "Court", secondary=attorney_court_admission_table, back_populates="admitted_attorneys", lazy="selectin"
    )

    # Add relationship
    user = relationship("User", back_populates="attorney")

    def __repr__(self):
        return f"<Attorney(id={self.id}, name='{self.name}', email='{self.email}')>"
