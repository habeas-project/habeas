from sqlalchemy import Column, DateTime, Integer, String, func

from app.database import Base


class IceDetentionFacility(Base):
    __tablename__ = "ice_detention_facilities"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    address = Column(String, nullable=True)
    city = Column(String(100), nullable=True)
    state = Column(String(2), nullable=True)  # 2-letter state code
    zip_code = Column(String(20), nullable=True)
    aor = Column(String(255), nullable=True)  # Area of Responsibility
    facility_type_detailed = Column(String(255), nullable=True)
    gender_capacity = Column(String(50), nullable=True)  # e.g., "Male", "Female", "Male/Female"

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    def __repr__(self):
        return f"<IceDetentionFacility id={self.id} name='{self.name}'>"
