from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import EmergencyContact
from app.schemas import EmergencyContactCreate, EmergencyContactResponse, EmergencyContactUpdate

router = APIRouter(
    prefix="/emergency-contacts",
    tags=["emergency-contacts"],
    responses={404: {"description": "Not found"}},
)


@router.post("/", response_model=EmergencyContactResponse, status_code=status.HTTP_201_CREATED)
def create_emergency_contact(emergency_contact: EmergencyContactCreate, db: Session = Depends(get_db)):
    """Create a new emergency contact record"""
    db_emergency_contact = EmergencyContact(**emergency_contact.dict())
    db.add(db_emergency_contact)
    db.commit()
    db.refresh(db_emergency_contact)
    return db_emergency_contact


@router.get("/", response_model=List[EmergencyContactResponse])
def read_emergency_contacts(
    client_id: int = Query(..., description="ID of the client"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """Retrieve emergency contacts for a client with pagination"""
    emergency_contacts = (
        db.query(EmergencyContact).filter(EmergencyContact.client_id == client_id).offset(skip).limit(limit).all()
    )
    return emergency_contacts


@router.get("/{emergency_contact_id}", response_model=EmergencyContactResponse)
def read_emergency_contact(emergency_contact_id: int, db: Session = Depends(get_db)):
    """Retrieve a specific emergency contact by ID"""
    db_emergency_contact = db.query(EmergencyContact).filter(EmergencyContact.id == emergency_contact_id).first()
    if db_emergency_contact is None:
        raise HTTPException(status_code=404, detail="Emergency contact not found")
    return db_emergency_contact


@router.patch("/{emergency_contact_id}", response_model=EmergencyContactResponse)
def update_emergency_contact(
    emergency_contact_id: int, emergency_contact: EmergencyContactUpdate, db: Session = Depends(get_db)
):
    """Update an emergency contact's information"""
    db_emergency_contact = db.query(EmergencyContact).filter(EmergencyContact.id == emergency_contact_id).first()
    if db_emergency_contact is None:
        raise HTTPException(status_code=404, detail="Emergency contact not found")

    # Update only provided fields
    update_data = emergency_contact.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_emergency_contact, key, value)

    db.commit()
    db.refresh(db_emergency_contact)
    return db_emergency_contact


@router.delete("/{emergency_contact_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_emergency_contact(emergency_contact_id: int, db: Session = Depends(get_db)):
    """Delete an emergency contact"""
    db_emergency_contact = db.query(EmergencyContact).filter(EmergencyContact.id == emergency_contact_id).first()
    if db_emergency_contact is None:
        raise HTTPException(status_code=404, detail="Emergency contact not found")

    db.delete(db_emergency_contact)
    db.commit()
    return None
