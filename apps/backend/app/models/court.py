# Import Attorney model for type hinting and relationship definition
# Use TYPE_CHECKING to avoid circular imports at runtime
from typing import TYPE_CHECKING, List

from sqlalchemy import Column, DateTime, Integer, String, func
from sqlalchemy.orm import Mapped, relationship

from app.database import Base

# Import the association table
from app.models.attorney_court_admission import attorney_court_admission_table

if TYPE_CHECKING:
    from .attorney import Attorney


class Court(Base):
    """Model for US District Courts"""

    __tablename__ = "courts"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    abbreviation = Column(String(10), nullable=False, unique=True, index=True)
    url = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Define the many-to-many relationship to Attorney using Mapped
    admitted_attorneys: Mapped[List["Attorney"]] = relationship(
        "Attorney",
        secondary=attorney_court_admission_table,
        back_populates="admitted_courts",
        lazy="selectin",  # Use selectin loading for efficiency
    )

    def __repr__(self):
        return f"<Court {self.abbreviation}: {self.name}>"
