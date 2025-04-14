from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Attorney
from app.schemas import Attorney as AttorneySchema
from app.schemas import AttorneyCreate, AttorneyUpdate

router = APIRouter(
    prefix="/attorneys",
    tags=["attorneys"],
    responses={404: {"description": "Not found"}},
)


@router.post("/", response_model=AttorneySchema, status_code=status.HTTP_201_CREATED)
def create_attorney(attorney: AttorneyCreate, db: Session = Depends(get_db)):
    """Create a new attorney record"""
    db_attorney = Attorney(
        name=attorney.name,
        phone_number=attorney.phone_number,
        email=attorney.email,
        zip_code=attorney.zip_code,
        state=attorney.state,
    )
    db.add(db_attorney)
    db.commit()
    db.refresh(db_attorney)
    return db_attorney


@router.get("/", response_model=List[AttorneySchema])
def read_attorneys(
    skip: int = 0,
    limit: int = 100,
    state: Optional[str] = Query(None, description="Filter by state (two-letter code)"),
    zip_code: Optional[str] = Query(None, description="Filter by zip code"),
    db: Session = Depends(get_db),
):
    """
    Retrieve a list of attorneys with optional filtering by state and zip code
    """
    query = db.query(Attorney)

    # Apply filters if provided
    if state:
        query = query.filter(Attorney.state == state)
    if zip_code:
        query = query.filter(Attorney.zip_code == zip_code)

    attorneys = query.offset(skip).limit(limit).all()
    return attorneys


@router.get("/{attorney_id}", response_model=AttorneySchema)
def read_attorney(attorney_id: int, db: Session = Depends(get_db)):
    """Retrieve a specific attorney by ID"""
    db_attorney = db.query(Attorney).filter(Attorney.id == attorney_id).first()
    if db_attorney is None:
        raise HTTPException(status_code=404, detail="Attorney not found")
    return db_attorney


@router.patch("/{attorney_id}", response_model=AttorneySchema)
def update_attorney(attorney_id: int, attorney: AttorneyUpdate, db: Session = Depends(get_db)):
    """Update an attorney's information"""
    db_attorney = db.query(Attorney).filter(Attorney.id == attorney_id).first()
    if db_attorney is None:
        raise HTTPException(status_code=404, detail="Attorney not found")

    # Update only provided fields
    update_data = attorney.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_attorney, key, value)

    db.commit()
    db.refresh(db_attorney)
    return db_attorney


@router.delete("/{attorney_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_attorney(attorney_id: int, db: Session = Depends(get_db)):
    """Delete an attorney"""
    db_attorney = db.query(Attorney).filter(Attorney.id == attorney_id).first()
    if db_attorney is None:
        raise HTTPException(status_code=404, detail="Attorney not found")

    db.delete(db_attorney)
    db.commit()
    return None
