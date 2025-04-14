from typing import Optional

from pydantic import BaseModel


class ExampleBase(BaseModel):
    """Base schema for Example data"""
    name: str
    description: Optional[str] = None

class ExampleCreate(ExampleBase):
    """Schema for creating a new Example"""
    pass

class Example(ExampleBase):
    """Schema for an Example with ID"""
    id: int

    class Config:
        orm_mode = True
