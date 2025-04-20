"""
Health check endpoint for the Habeas backend.
"""

from fastapi import APIRouter

router = APIRouter()


@router.get("/health", tags=["Health"], summary="Perform a Health Check")
async def health_check() -> dict[str, str]:
    """
    Simple health check endpoint.

    Returns:
        dict: A dictionary indicating the status.
    """
    return {"status": "ok"}
