from fastapi.testclient import TestClient
import pytest
from app.main import app

# Create test client
client = TestClient(app)

def test_read_root():
    """Test the root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to the Habeas API"}

def test_read_examples():
    """Test getting all examples"""
    response = client.get("/examples/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    # Verify that the structure matches our schema
    if response.json():
        example = response.json()[0]
        assert "id" in example
        assert "name" in example

def test_read_example():
    """Test getting a specific example"""
    # First, get all examples to find a valid ID
    examples_response = client.get("/examples/")
    examples = examples_response.json()
    
    if examples:
        # Use the first example's ID
        example_id = examples[0]["id"]
        response = client.get(f"/examples/{example_id}")
        assert response.status_code == 200
        assert response.json()["id"] == example_id
    else:
        # Skip if no examples available
        pytest.skip("No examples available to test individual retrieval")

def test_create_example():
    """Test creating a new example"""
    new_example = {
        "name": "Test Example",
        "description": "Created during testing"
    }
    
    response = client.post("/examples/", json=new_example)
    assert response.status_code == 200
    
    created = response.json()
    assert created["name"] == new_example["name"]
    assert created["description"] == new_example["description"]
    assert "id" in created 