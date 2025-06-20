from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from .court import Court  # Assuming court.py contains the Court model


class CourtCounty(Base):
    """Model for associating counties with US District Courts"""

    __tablename__ = "court_counties"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    county_name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    state: Mapped[str] = mapped_column(String(100), nullable=False, index=True)  # Assuming state names/abbreviations

    court_id: Mapped[int] = mapped_column(Integer, ForeignKey("courts.id"), nullable=False, index=True)

    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    # Define the many-to-one relationship to Court
    # The Mapped type hint helps with type checking and editor support.
    # back_populates should match a relationship name on the Court model if a bi-directional relationship is needed.
    # For now, this is a uni-directional reference from CourtCounty to Court.
    # If Court needs to access its counties, a 'counties' relationship would be added there.
    court: Mapped["Court"] = relationship("Court", back_populates="court_counties")  # Added back_populates

    def __repr__(self):
        return f"<CourtCounty id={self.id} name='{self.county_name}' state='{self.state}' court_id={self.court_id}>"
