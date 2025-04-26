from typing import Optional

from fastapi import Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.schemas.user import UserCreate


class AuthService:
    """
    Service for authentication operations.
    This is a placeholder for Cognito integration that will be implemented later.
    """

    def __init__(self, db: Session = Depends(get_db)):
        self.db = db

    def create_user_from_cognito(self, cognito_id: str, user_type: str) -> User:
        """
        Create a new user in the database after successful Cognito authentication.
        This will be called by post-authentication hooks or Lambda triggers.
        """
        # Check if user already exists
        existing_user = self.db.query(User).filter(User.cognito_id == cognito_id).first()
        if existing_user:
            return existing_user

        # Create new user
        user_create = UserCreate(cognito_id=cognito_id, user_type=user_type, is_active=True)

        db_user = User(
            cognito_id=user_create.cognito_id, user_type=user_create.user_type, is_active=user_create.is_active
        )

        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)

        return db_user

    def get_user_by_cognito_id(self, cognito_id: str) -> Optional[User]:
        """Get a user by their Cognito ID"""
        return self.db.query(User).filter(User.cognito_id == cognito_id).first()


# This will be expanded with actual Cognito integration later
auth_service = AuthService()
