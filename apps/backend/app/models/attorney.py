from typing import TYPE_CHECKING, List

from sqlalchemy import TIMESTAMP, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.database import Base
from app.models.attorney_court_admission import attorney_court_admission_table

if TYPE_CHECKING:
    from app.models.court import Court


class Attorney(Base):
    """
    Attorney model representing a legal professional who can file habeas corpus petitions
    """

    __tablename__ = "attorneys"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    phone_number: Mapped[str] = mapped_column(String(20), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    zip_code: Mapped[str] = mapped_column(String(10), nullable=False)
    state: Mapped[str] = mapped_column(String(2), nullable=False)
    created_at: Mapped[TIMESTAMP] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[TIMESTAMP] = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )
    user_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )

    # Define the many-to-many relationship to Court using Mapped
    admitted_courts: Mapped[List["Court"]] = relationship(
        "Court", secondary=attorney_court_admission_table, back_populates="admitted_attorneys", lazy="selectin"
    )

    # Add relationship
    user = relationship("User", back_populates="attorney")

    def __repr__(self):
        return f"<Attorney(id={self.id}, name='{self.name}', email='{self.email}')>"
