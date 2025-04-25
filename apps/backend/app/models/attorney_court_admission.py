from sqlalchemy import Column, ForeignKey, Integer, Table

from app.database import Base  # Assuming Base is importable from app.database

# Define the association table directly using SQLAlchemy Table construct
# This is simpler if the table only contains foreign keys
attorney_court_admission_table = Table(
    "attorney_court_admissions",
    Base.metadata,
    Column("attorney_id", Integer, ForeignKey("attorneys.id"), primary_key=True),
    Column("court_id", Integer, ForeignKey("courts.id"), primary_key=True),
)

# Note: If we needed additional fields on the relationship (like admission_date),
# we would define a full DeclarativeBase model class here instead of just a Table.
# Example (if needed later):
# class AttorneyCourtAdmission(Base):
#     __tablename__ = "attorney_court_admissions"
#     attorney_id = Column(Integer, ForeignKey("attorneys.id"), primary_key=True)
#     court_id = Column(Integer, ForeignKey("courts.id"), primary_key=True)
#     admission_date = Column(Date) # Example extra field
#
#     # Optional: relationships back to Attorney and Court if needed
#     attorney = relationship("Attorney", back_populates="court_admissions")
#     court = relationship("Court", back_populates="attorney_admissions")
