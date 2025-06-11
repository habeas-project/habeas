import logging

from fastapi import APIRouter, Body, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.admin import Admin
from app.models.attorney import Attorney
from app.models.client import Client
from app.models.user import User
from app.schemas.signup import (
    AdminInfo,
    AdminSignupRequest,
    AdminSignupResponse,
    AttorneyInfo,
    AttorneySignupRequest,
    AttorneySignupResponse,
    ClientInfo,
    ClientSignupRequest,
    ClientSignupResponse,
)
from app.schemas.user import UserResponse

# Add logger
logger = logging.getLogger(__name__)

# OAuth 2.0 token type constant (not a password, ignore bandit B105)
OAUTH_TOKEN_TYPE = "bearer"  # nosec B105

router = APIRouter(
    prefix="/signup",
    tags=["signup"],
    responses={400: {"description": "Bad Request"}, 422: {"description": "Validation Error"}},
)


@router.post(
    "/attorney",
    response_model=AttorneySignupResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Attorney Signup",
    description="Complete attorney registration - creates both user account and attorney profile",
    responses={
        201: {
            "description": "Attorney registration successful",
            "content": {
                "application/json": {
                    "example": {
                        "user": {
                            "id": 1,
                            "cognito_id": "mock_jane.doe@example.com",
                            "user_type": "attorney",
                            "is_active": True,
                            "created_at": "2023-01-01T00:00:00",
                            "updated_at": "2023-01-01T00:00:00",
                        },
                        "attorney": {
                            "id": 1,
                            "name": "Jane Doe",
                            "phone_number": "+15551234567",
                            "email": "jane.doe@example.com",
                            "zip_code": "12345",
                            "state": "CA",
                            "created_at": "2023-01-01T00:00:00",
                            "updated_at": "2023-01-01T00:00:00",
                        },
                        "access_token": "mock_token_1",
                        "token_type": "bearer",
                    }
                }
            },
        },
        400: {
            "description": "User with this email already exists",
            "content": {"application/json": {"example": {"detail": "An attorney with this email already exists"}}},
        },
        422: {"description": "Validation Error"},
    },
)
def signup_attorney(
    signup_data: AttorneySignupRequest = Body(
        ...,
        description="Attorney signup information",
        examples=[
            {
                "name": "Jane Doe",
                "phone_number": "+15551234567",
                "email": "jane.doe@example.com",
                "zip_code": "12345",
                "state": "CA",
                "password": "SecurePassword123!",
            }
        ],
    ),
    db: Session = Depends(get_db),
):
    """
    Complete attorney registration process that creates both a user account and attorney profile.

    This endpoint:
    1. Creates a User record with user_type='attorney'
    2. Creates an Attorney record linked to the User via user_id
    3. Returns both user and attorney information
    4. Handles transaction rollback on errors to prevent orphaned records

    **Parameters:**
    - **name**: Full name of the attorney
    - **phone_number**: Contact phone number (E.164 format: +1 followed by 10 digits)
    - **email**: Email address (must be unique)
    - **zip_code**: US postal code (5 digits or 5+4 format)
    - **state**: Two-letter US state code (uppercase)
    - **password**: Password for the account (minimum 8 characters)

    **Returns:**
    - User account information
    - Attorney profile information
    - Mock authentication token (for testing environments)
    """
    try:
        # Check if attorney with this email already exists
        existing_attorney = db.query(Attorney).filter(Attorney.email == signup_data.email).first()
        if existing_attorney:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="An attorney with this email already exists"
            )

        # Check if user with this email already exists (using mock cognito_id format)
        mock_cognito_id = f"mock_{signup_data.email}"
        existing_user = db.query(User).filter(User.cognito_id == mock_cognito_id).first()
        if existing_user:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="A user with this email already exists")

        # Begin transaction - create User first
        db_user = User(
            cognito_id=mock_cognito_id,  # For now, use mock format
            user_type="attorney",
            is_active=True,
        )
        db.add(db_user)
        db.flush()  # Flush to get the user ID without committing

        # Create Attorney record linked to User
        db_attorney = Attorney(
            name=signup_data.name,
            phone_number=signup_data.phone_number,
            email=signup_data.email,
            zip_code=signup_data.zip_code,
            state=signup_data.state,
            user_id=db_user.id,  # Link to the user record
        )
        db.add(db_attorney)

        # Commit transaction
        db.commit()

        # Refresh objects to get updated timestamps
        db.refresh(db_user)
        db.refresh(db_attorney)

        # Create response
        user_response = UserResponse.model_validate(db_user)
        attorney_info = AttorneyInfo.model_validate(db_attorney)

        # Mock authentication token for testing
        mock_token = f"mock_token_{db_user.id}"

        return AttorneySignupResponse(
            user=user_response, attorney=attorney_info, access_token=mock_token, token_type=OAUTH_TOKEN_TYPE
        )

    except HTTPException:
        # Re-raise HTTPExceptions (like our duplicate email check) without modification
        db.rollback()
        raise
    except IntegrityError as e:
        db.rollback()
        logger.error(f"Database integrity error during attorney signup: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Registration failed due to data conflict. Please check your information.",
        )
    except Exception as e:
        db.rollback()
        logger.error(f"Unexpected error during attorney signup: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed due to an internal error. Please try again later.",
        )


@router.post(
    "/client",
    response_model=ClientSignupResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Client Signup",
    description="Complete client registration - creates both user account and client profile",
    responses={
        201: {
            "description": "Client registration successful",
            "content": {
                "application/json": {
                    "example": {
                        "user": {
                            "id": 2,
                            "cognito_id": "mock_john.doe@example.com",
                            "user_type": "client",
                            "is_active": True,
                            "created_at": "2023-01-01T00:00:00",
                            "updated_at": "2023-01-01T00:00:00",
                        },
                        "client": {
                            "id": 1,
                            "first_name": "John",
                            "last_name": "Doe",
                            "country_of_birth": "United States",
                            "nationality": "American",
                            "birth_date": "1990-01-01",
                            "alien_registration_number": "A123456789",
                            "passport_number": None,
                            "school_name": None,
                            "student_id_number": None,
                            "created_at": "2023-01-01T00:00:00",
                            "updated_at": "2023-01-01T00:00:00",
                        },
                        "access_token": "mock_token_2",
                        "token_type": "bearer",
                    }
                }
            },
        },
        400: {
            "description": "User with this email already exists",
            "content": {"application/json": {"example": {"detail": "A client with this email already exists"}}},
        },
        422: {"description": "Validation Error"},
    },
)
def signup_client(
    signup_data: ClientSignupRequest = Body(
        ...,
        description="Client signup information",
        examples=[
            {
                "first_name": "John",
                "last_name": "Doe",
                "country_of_birth": "United States",
                "nationality": "American",
                "birth_date": "1990-01-01",
                "alien_registration_number": "A123456789",
                "passport_number": "US1234567",
                "school_name": "University of Example",
                "student_id_number": "STU123456",
                "password": "SecurePassword123!",
            }
        ],
    ),
    db: Session = Depends(get_db),
):
    """
    Complete client registration process that creates both a user account and client profile.

    This endpoint:
    1. Creates a User record with user_type='client'
    2. Creates a Client record linked to the User via user_id
    3. Returns both user and client information
    4. Handles transaction rollback on errors to prevent orphaned records

    **Parameters:**
    - **first_name**: Client's first name
    - **last_name**: Client's last name
    - **country_of_birth**: Client's country of birth
    - **birth_date**: Client's birth date (YYYY-MM-DD format)
    - **nationality**: Client's nationality (optional)
    - **alien_registration_number**: Client's A-Number (optional)
    - **passport_number**: Client's passport number (optional)
    - **school_name**: Client's school name (optional)
    - **student_id_number**: Client's student ID number (optional)
    - **password**: Password for the account (minimum 8 characters)

    **Returns:**
    - User account information
    - Client profile information
    - Mock authentication token (for testing environments)
    """
    try:
        # Note: Clients don't have email in their model, so we use first_name + last_name for uniqueness check
        # Create a unique identifier for the client based on name and birth date
        existing_client = (
            db.query(Client)
            .filter(
                Client.first_name == signup_data.first_name,
                Client.last_name == signup_data.last_name,
                Client.birth_date == signup_data.birth_date,
            )
            .first()
        )
        if existing_client:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A client with this name and birth date already exists",
            )

        # For client signup, we'll use a combination of name and birth date as unique identifier
        # since clients don't have email in the current schema
        mock_cognito_id = (
            f"mock_client_{signup_data.first_name.lower()}_{signup_data.last_name.lower()}_{signup_data.birth_date}"
        )
        existing_user = db.query(User).filter(User.cognito_id == mock_cognito_id).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="A user with this information already exists"
            )

        # Begin transaction - create User first
        db_user = User(
            cognito_id=mock_cognito_id,  # For now, use mock format
            user_type="client",
            is_active=True,
        )
        db.add(db_user)
        db.flush()  # Flush to get the user ID without committing

        # Create Client record linked to User
        db_client = Client(
            first_name=signup_data.first_name,
            last_name=signup_data.last_name,
            country_of_birth=signup_data.country_of_birth,
            nationality=signup_data.nationality,
            birth_date=signup_data.birth_date,
            alien_registration_number=signup_data.alien_registration_number,
            passport_number=signup_data.passport_number,
            school_name=signup_data.school_name,
            student_id_number=signup_data.student_id_number,
            user_id=db_user.id,  # Link to the user record
        )
        db.add(db_client)

        # Commit transaction
        db.commit()

        # Refresh objects to get updated timestamps
        db.refresh(db_user)
        db.refresh(db_client)

        # Create response
        user_response = UserResponse.model_validate(db_user)
        client_info = ClientInfo.model_validate(db_client)

        # Mock authentication token for testing
        mock_token = f"mock_token_{db_user.id}"

        return ClientSignupResponse(
            user=user_response, client=client_info, access_token=mock_token, token_type=OAUTH_TOKEN_TYPE
        )

    except HTTPException:
        # Re-raise HTTPExceptions (like our duplicate check) without modification
        db.rollback()
        raise
    except IntegrityError as e:
        db.rollback()
        logger.error(f"Database integrity error during client signup: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Registration failed due to data conflict. Please check your information.",
        )
    except Exception as e:
        db.rollback()
        logger.error(f"Unexpected error during client signup: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed due to an internal error. Please try again later.",
        )


@router.post(
    "/admin",
    response_model=AdminSignupResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Admin Signup",
    description="Complete admin registration - creates both user account and admin profile",
    responses={
        201: {
            "description": "Admin registration successful",
            "content": {
                "application/json": {
                    "example": {
                        "user": {
                            "id": 3,
                            "cognito_id": "mock_admin@example.com",
                            "user_type": "admin",
                            "is_active": True,
                            "created_at": "2023-01-01T00:00:00",
                            "updated_at": "2023-01-01T00:00:00",
                        },
                        "admin": {
                            "id": 1,
                            "name": "System Administrator",
                            "email": "admin@example.com",
                            "department": "IT",
                            "role": "admin",
                            "created_at": "2023-01-01T00:00:00",
                            "updated_at": "2023-01-01T00:00:00",
                        },
                        "access_token": "mock_token_3",
                        "token_type": "bearer",
                    }
                }
            },
        },
        400: {
            "description": "User with this email already exists",
            "content": {"application/json": {"example": {"detail": "An admin with this email already exists"}}},
        },
        422: {"description": "Validation Error"},
    },
)
def signup_admin(
    signup_data: AdminSignupRequest = Body(
        ...,
        description="Admin signup information",
        examples=[
            {
                "name": "System Administrator",
                "email": "admin@example.com",
                "department": "IT",
                "role": "admin",
                "password": "SecurePassword123!",
            }
        ],
    ),
    db: Session = Depends(get_db),
):
    """
    Complete admin registration process that creates both a user account and admin profile.

    This endpoint:
    1. Creates a User record with user_type='admin'
    2. Creates an Admin record linked to the User via user_id
    3. Returns both user and admin information
    4. Handles transaction rollback on errors to prevent orphaned records

    **Parameters:**
    - **name**: Full name of the admin
    - **email**: Email address (must be unique)
    - **department**: Department or division (optional)
    - **role**: Admin role or permission level (defaults to 'admin')
    - **password**: Password for the account (minimum 8 characters)

    **Returns:**
    - User account information
    - Admin profile information
    - Mock authentication token (for testing environments)
    """
    try:
        # Check if admin with this email already exists
        existing_admin = db.query(Admin).filter(Admin.email == signup_data.email).first()
        if existing_admin:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="An admin with this email already exists"
            )

        # Check if user with this email already exists (using mock cognito_id format)
        mock_cognito_id = f"mock_{signup_data.email}"
        existing_user = db.query(User).filter(User.cognito_id == mock_cognito_id).first()
        if existing_user:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="A user with this email already exists")

        # Begin transaction - create User first
        db_user = User(
            cognito_id=mock_cognito_id,  # For now, use mock format
            user_type="admin",
            is_active=True,
        )
        db.add(db_user)
        db.flush()  # Flush to get the user ID without committing

        # Create Admin record linked to User
        db_admin = Admin(
            name=signup_data.name,
            email=signup_data.email,
            department=signup_data.department,
            role=signup_data.role,
            user_id=db_user.id,  # Link to the user record
        )
        db.add(db_admin)

        # Commit transaction
        db.commit()

        # Refresh objects to get updated timestamps
        db.refresh(db_user)
        db.refresh(db_admin)

        # Create response
        user_response = UserResponse.model_validate(db_user)
        admin_info = AdminInfo.model_validate(db_admin)

        # Mock authentication token for testing
        mock_token = f"mock_token_{db_user.id}"

        return AdminSignupResponse(
            user=user_response, admin=admin_info, access_token=mock_token, token_type=OAUTH_TOKEN_TYPE
        )

    except HTTPException:
        # Re-raise HTTPExceptions (like our duplicate email check) without modification
        db.rollback()
        raise
    except IntegrityError as e:
        db.rollback()
        logger.error(f"Database integrity error during admin signup: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Registration failed due to data conflict. Please check your information.",
        )
    except Exception as e:
        db.rollback()
        logger.error(f"Unexpected error during admin signup: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed due to an internal error. Please try again later.",
        )
