from sqlalchemy.orm import Session
from typing import List, Optional

from app.models.example_model import Example
from app.schemas.example_schema import ExampleCreate

class ExampleService:
    """Service for handling Example database operations"""
    
    @staticmethod
    def get_examples(db: Session) -> List[Example]:
        """Get all examples from the database"""
        return db.query(Example).all()
    
    @staticmethod
    def get_example(db: Session, example_id: int) -> Optional[Example]:
        """Get a specific example by ID"""
        return db.query(Example).filter(Example.id == example_id).first()
    
    @staticmethod
    def create_example(db: Session, example: ExampleCreate) -> Example:
        """Create a new example in the database"""
        db_example = Example(
            name=example.name,
            description=example.description
        )
        db.add(db_example)
        db.commit()
        db.refresh(db_example)
        return db_example
    
    @staticmethod
    def update_example(
        db: Session, 
        example_id: int, 
        example_data: ExampleCreate
    ) -> Optional[Example]:
        """Update an existing example"""
        db_example = ExampleService.get_example(db, example_id)
        if db_example:
            # Update attributes
            for key, value in example_data.dict().items():
                setattr(db_example, key, value)
            
            db.commit()
            db.refresh(db_example)
        
        return db_example
    
    @staticmethod
    def delete_example(db: Session, example_id: int) -> bool:
        """Delete an example by ID"""
        db_example = ExampleService.get_example(db, example_id)
        if db_example:
            db.delete(db_example)
            db.commit()
            return True
        return False 