from sqlalchemy import Integer, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column  # Import Mapped and mapped_column


class Base(DeclarativeBase):
    pass


class Example(Base):
    """Example model for demonstration purposes"""

    __tablename__ = "examples"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
