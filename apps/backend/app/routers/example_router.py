from typing import List

from fastapi import APIRouter, HTTPException

# Import schemas
from app.schemas.example_schema import Example, ExampleCreate

router = APIRouter(
    prefix="/examples",
    tags=["examples"],
    responses={404: {"description": "Not found"}},
)

fake_examples_db = [
    {"id": 1, "name": "Example 1", "description": "Description for example 1"},
    {"id": 2, "name": "Example 2", "description": "Description for example 2"},
]


@router.get("/", response_model=List[Example])
def get_examples():
    """
    Retrieve all examples.
    """
    return fake_examples_db


@router.get("/{example_id}", response_model=Example)
def get_example(example_id: int):
    """
    Retrieve a specific example by ID.
    """
    for example in fake_examples_db:
        if example["id"] == example_id:
            return example
    raise HTTPException(status_code=404, detail="Example not found")


@router.post("/", response_model=Example)
def create_example(example: ExampleCreate):
    """
    Create a new example.
    """
    # This is just a stub - in a real application, you would save to a database
    new_example = {"id": len(fake_examples_db) + 1, **example.dict()}
    fake_examples_db.append(new_example)
    return new_example
