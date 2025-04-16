# Habeas - Technical Documentation

## Development Requirements

### System Dependencies

The following system-level dependencies are required for development:

#### PostgreSQL and Development Package

The PostgreSQL development package is required for building the `psycopg2-binary` Python package during dependency installation.

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install libpq-dev postgresql
```

**macOS (with Homebrew):**
```bash
brew install postgresql
```

#### Yarn Package Manager

Yarn is required for JavaScript dependency management and running project scripts.

**Ubuntu/Debian:**
```bash
# Option 1: Add the official Yarn repository
curl -sS https://dl.yarnpkg.com/debian/pubkey.gpg | sudo apt-key add -
echo "deb https://dl.yarnpkg.com/debian/ stable main" | sudo tee /etc/apt/sources.list.d/yarn.list
sudo apt update
sudo apt install yarn

# Option 2: Install via npm 
sudo npm install -g yarn
```

**macOS (with Homebrew):**
```bash
brew install yarn
```

### Python Environment Setup

1. Make sure you have Python 3.12+ installed
2. Install uv for Python package management:
   ```bash
   pip install uv
   ```
3. Install system dependencies (including PostgreSQL development files)
4. Run the setup commands from the README.md

#### Python Command

On many systems, `python` refers to Python 2.x, while `python3` refers to Python 3.x. The scripts in package.json should use the appropriate command for your system. If you encounter a "python: not found" error, update the scripts to use `python3` instead.

#### Virtual Environment Activation

The Python dependencies are installed in a virtual environment located in the `apps/backend/.venv` directory. If you encounter module import errors, you may need to activate the virtual environment before running Python commands:

```bash
# From the apps/backend directory
source .venv/bin/activate
```

Alternatively, update the package.json scripts to activate the virtual environment before running Python commands:

```json
"dev:backend": "cd apps/backend && source .venv/bin/activate && python3 -m uvicorn app.main:app --reload"
```

### Python Dependencies

The following Python packages are installed via `uv sync`:

- alembic==1.10.4
- anyio==4.9.0
- click==8.1.8
- fastapi==0.95.1
- greenlet==3.1.1
- h11==0.14.0
- idna==3.10
- mako==1.3.9
- markupsafe==3.0.2
- psycopg2-binary==2.9.6
- pydantic==1.10.7
- python-dotenv==1.0.0
- sniffio==1.3.1
- sqlalchemy==2.0.12
- starlette==0.26.1
- typing-extensions==4.13.1
- uvicorn==0.22.0

## API Development Patterns

### Core Principles
- Use synchronous endpoints for simplicity and testing consistency
- Use `TestClient` for testing (not `AsyncClient`)
- Keep CRUD operations within router files for straightforward implementation
- Focus on maintainability over performance optimization

### Directory Structure

The backend follows a clear directory structure for organizing code:

```
apps/backend/app/
├── routers/             # API route handlers with CRUD operations
├── models/              # SQLAlchemy models
├── schemas/             # Pydantic schemas
└── services/            # Business logic
```

> **Note on CRUD Operation Location:** All database interaction logic (Create, Read, Update, Delete) is intentionally handled directly within the API route handlers located in `app/routers/`. This approach simplifies the structure for synchronous calls and keeps related logic colocated. There is not a separate `app/crud/` directory for these operations in the current architecture.

### Router Implementation Pattern

Each router follows this structure:

```python
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Model
from app.schemas import ModelCreate, ModelUpdate, ModelResponse

router = APIRouter(
    prefix="/models",
    tags=["models"],
    responses={404: {"description": "Not found"}},
)

@router.post("/", response_model=ModelResponse, status_code=status.HTTP_201_CREATED)
def create_model(model: ModelCreate, db: Session = Depends(get_db)):
    """Create a new model record"""
    db_model = Model(**model.dict())
    db.add(db_model)
    db.commit()
    db.refresh(db_model)
    return db_model

@router.get("/", response_model=List[ModelResponse])
def read_models(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """Retrieve models with pagination"""
    models = db.query(Model).offset(skip).limit(limit).all()
    return models

@router.get("/{model_id}", response_model=ModelResponse)
def read_model(model_id: int, db: Session = Depends(get_db)):
    """Retrieve a specific model by ID"""
    db_model = db.query(Model).filter(Model.id == model_id).first()
    if db_model is None:
        raise HTTPException(status_code=404, detail="Model not found")
    return db_model

@router.patch("/{model_id}", response_model=ModelResponse)
def update_model(model_id: int, model: ModelUpdate, db: Session = Depends(get_db)):
    """Update a model's information"""
    db_model = db.query(Model).filter(Model.id == model_id).first()
    if db_model is None:
        raise HTTPException(status_code=404, detail="Model not found")

    # Update only provided fields
    update_data = model.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_model, key, value)

    db.commit()
    db.refresh(db_model)
    return db_model

@router.delete("/{model_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_model(model_id: int, db: Session = Depends(get_db)):
    """Delete a model"""
    db_model = db.query(Model).filter(Model.id == model_id).first()
    if db_model is None:
        raise HTTPException(status_code=404, detail="Model not found")

    db.delete(db_model)
    db.commit()
    return None
```
### Schema Organization

Pydantic schemas follow a consistent pattern:

1. **Base Schema**: Contains common fields and validation rules
2. **Create Schema**: Inherits from base, adds required fields for creation
3. **Update Schema**: Inherits from base, makes all fields optional
4. **Response Schema**: Inherits from base, adds read-only fields

Example:
```python
class ModelBase(BaseModel):
    # Common fields and validation

class ModelCreate(ModelBase):
    # Additional required fields

class ModelUpdate(ModelBase):
    # All fields optional

class ModelResponse(ModelBase):
    # Read-only fields (id, timestamps)
```

### Testing Strategy

We use FastAPI's `TestClient` for testing, which requires synchronous endpoints:

```python
from fastapi.testclient import TestClient

def test_create_model(client: TestClient):
    response = client.post("/models/", json={"name": "Test Model"})
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test Model"
```

### Common Issues

#### Async/await Implementation
- **Problem**: Mixing async and sync patterns
- **Solution**: Stick to synchronous implementation for consistency with testing
- **Why**: Simplifies testing and maintenance without significant performance impact

#### Database Sessions
- **Problem**: Incorrect session handling
- **Solution**: Use `Session = Depends(get_db)` consistently
- **Why**: Ensures proper session lifecycle management

#### Response Models
- **Problem**: Inconsistent response models
- **Solution**: Always specify response_model in route decorators
- **Why**: Ensures consistent API responses and documentation

## Database Migrations

### Overview
Our project uses Alembic for database migrations. Migrations are stored in `apps/backend/migrations/versions/` and follow a sequential naming pattern.

### Migration Structure
- `migrations/versions/`: Contains all migration files
- `migrations/env.py`: Alembic environment configuration
- `migrations/script.py.mako`: Template for new migration files

### Migration Files
1. `initial_schema.py`: Initial database setup including:
   - Clients table
   - Emergency contacts table
   - Courts table
   - All necessary indexes and constraints

### Running Migrations
```bash
# Upgrade to latest version
alembic upgrade head

# Create new migration
alembic revision --autogenerate -m "description"

# Downgrade one version
alembic downgrade -1
```

## Common Issues

### pg_config executable not found

**Error:**
```
error: pg_config executable not found
```

**Solution:**
This error occurs when trying to build psycopg2 without the PostgreSQL development files installed. Install the appropriate package for your system as described in the "PostgreSQL Development Package" section above.

### Python module not found

**Error:**
```
No module named 'uvicorn' (or any other module)
```

**Solution:**
This usually means you're not running Python from the virtual environment where the packages were installed. Activate the virtual environment before running Python commands or update your scripts to do so automatically (see "Virtual Environment Activation" section). 