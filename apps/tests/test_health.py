"""
Tests for the health check endpoint.
"""

# Assuming your FastAPI app instance is created in app.main
# Adjust the import path if your app instance is located elsewhere
from app.main import app
from fastapi.testclient import TestClient

# Create a TestClient instance
# Per project guidelines, use synchronous TestClient
client = TestClient(app)


def test_health_check() -> None:
    """Test the /health endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
