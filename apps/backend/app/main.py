import logging

from fastapi import Depends, FastAPI, Response, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text  # Import the text function
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

# Import database session dependency
from app.database import get_db

# Import routers
from app.routers import attorney_router, client_router, emergency_contact_router, example_router

app = FastAPI(
    title="Habeas API",
    description="API for the Habeas application - connecting detained individuals with legal representatives",
    version="0.1.0",
)

# Configure logging
logging.basicConfig(level=logging.ERROR)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {"message": "Welcome to the Habeas API"}


@app.get("/health", status_code=status.HTTP_200_OK)
def health_check(response: Response, db: Session = Depends(get_db)):
    """Checks the health of the API, primarily database connectivity."""
    response.headers["Cache-Control"] = "no-cache"
    try:
        # Perform a simple query to check DB connection
        db.execute(text("SELECT 1"))  # Use text() for raw SQL
        return {"status": "ok"}
    except SQLAlchemyError as e:
        logging.error(f"Database connection failed: {e}")
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        return {"status": "error", "detail": "Database connection failed"}
    except Exception as e:
        # Catch any other unexpected errors during the health check
        logging.error(f"An unexpected error occurred: {e}")
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"status": "error", "detail": "An unexpected error occurred"}


# Register routers
app.include_router(example_router.router)
app.include_router(attorney_router.router)
app.include_router(client_router.router)
app.include_router(emergency_contact_router.router)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)  # nosec B104
