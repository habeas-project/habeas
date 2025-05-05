from fastapi import APIRouter, Depends, HTTPException, status

# Define a simple schema for mock authentication
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.schemas.user import UserCreate

# Standard token type for OAuth 2.0
TOKEN_TYPE = "bearer"  # nosec B105 - not a password, standard OAuth token type


class MockUserRegister(BaseModel):
    """Schema for mock user registration"""

    email: str = Field(..., description="User's email address")
    password: str = Field(..., min_length=8, description="User's password")
    user_type: str = Field(..., description="Type of user: client, attorney, admin")


class MockUserLogin(BaseModel):
    """Schema for mock user login"""

    email: str = Field(..., description="User's email address")
    password: str = Field(..., description="User's password")


class MockAuthResponse(BaseModel):
    """Schema for mock authentication response"""

    access_token: str
    token_type: str
    user_id: int
    cognito_id: str
    user_type: str


router = APIRouter(
    prefix="/mock",
    tags=["mock-auth"],
    responses={401: {"description": "Unauthorized"}},
)


@router.post("/register", response_model=MockAuthResponse, status_code=status.HTTP_201_CREATED)
def register_user(user_data: MockUserRegister, db: Session = Depends(get_db)):
    """
    Mock user registration endpoint for testing purposes.
    This endpoint simulates AWS Cognito registration.
    """
    # Check if user already exists
    existing_user = db.query(User).filter(User.cognito_id == f"mock_{user_data.email}").first()
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User with this email already exists")

    # Create a new user with mock cognito_id
    user_create = UserCreate(cognito_id=f"mock_{user_data.email}", user_type=user_data.user_type, is_active=True)

    db_user = User(cognito_id=user_create.cognito_id, user_type=user_create.user_type, is_active=user_create.is_active)

    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    # Return mock auth response using direct attributes (should work now)
    return MockAuthResponse(
        access_token=f"mock_token_{db_user.id}",
        token_type=TOKEN_TYPE,
        user_id=db_user.id,
        cognito_id=db_user.cognito_id,
        user_type=db_user.user_type,
    )


@router.post("/login", response_model=MockAuthResponse)
def login_user(credentials: MockUserLogin, db: Session = Depends(get_db)):
    """
    Mock user login endpoint for testing purposes.
    This endpoint simulates AWS Cognito authentication.
    """
    # Find user by mock cognito_id
    db_user = db.query(User).filter(User.cognito_id == f"mock_{credentials.email}").first()
    if not db_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    # Return mock auth response using direct attributes (should work now)
    return MockAuthResponse(
        access_token=f"mock_token_{db_user.id}",
        token_type=TOKEN_TYPE,
        user_id=db_user.id,
        cognito_id=db_user.cognito_id,
        user_type=db_user.user_type,
    )
