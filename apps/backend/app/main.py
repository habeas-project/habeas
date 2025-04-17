import logging

from fastapi import Depends, FastAPI, Response, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_swagger_ui_html, get_redoc_html
from fastapi.openapi.utils import get_openapi
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
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
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


@app.get("/custom-docs", include_in_schema=False)
async def custom_swagger_ui_html():
    """
    Custom Swagger UI HTML with improved styling and usability
    """
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title=f"{app.title} - Swagger UI",
        swagger_js_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5.9.0/swagger-ui-bundle.js",
        swagger_css_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5.9.0/swagger-ui.css",
        swagger_favicon_url="https://fastapi.tiangolo.com/img/favicon.png",
        oauth2_redirect_url=app.swagger_ui_oauth2_redirect_url,
    )


@app.get("/custom-redoc", include_in_schema=False)
async def custom_redoc_html():
    """
    Custom ReDoc HTML with improved styling and usability
    """
    return get_redoc_html(
        openapi_url=app.openapi_url,
        title=f"{app.title} - ReDoc",
        redoc_js_url="https://cdn.jsdelivr.net/npm/redoc@next/bundles/redoc.standalone.js",
        redoc_favicon_url="https://fastapi.tiangolo.com/img/favicon.png",
    )


def custom_openapi():
    """
    Custom OpenAPI schema with additional metadata and examples
    """
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )
    
    # Add custom schema components or metadata here if needed
    openapi_schema["info"]["x-logo"] = {
        "url": "https://fastapi.tiangolo.com/img/logo-margin/logo-teal.png"
    }
    
    # Add contact information
    openapi_schema["info"]["contact"] = {
        "name": "Habeas Project",
        "url": "https://github.com/habeas-project",
        "email": "info@example.com"  # Change to actual contact email
    }
    
    # Add license information
    openapi_schema["info"]["license"] = {
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT"
    }
    
    # Add external documentation
    openapi_schema["externalDocs"] = {
        "description": "Find more information here",
        "url": "https://github.com/habeas-project"
    }
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)  # nosec B104
