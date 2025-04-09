# Habeas Backend

This is the FastAPI backend service for the Habeas application.

## Development Setup

### Prerequisites

- Python 3.12+
- uv (Python package manager)
- PostgreSQL

### Setup with uv

From the project root directory:

```bash
# Install dependencies including development tools
yarn backend:install-dev

# Or for production dependencies only
yarn backend:install
```

### Manual Setup with uv

If you prefer to set up directly without using the yarn scripts:

```bash
# Navigate to the backend directory
cd apps/backend

# Create a virtual environment and install dependencies with development tools
uv venv
uv pip install -e ".[dev]"

# Or for production dependencies only
uv pip install -e .
```

### Environment Configuration

Copy the example environment file and configure it:

```bash
cp .env.example .env
# Edit .env with your database credentials and settings
```

### Running the Development Server

From the project root:

```bash
yarn dev:backend
```

Or directly:

```bash
python -m uvicorn app.main:app --reload
```

### API Documentation

When the server is running, access the auto-generated API documentation at:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Testing

Run tests with pytest:

```bash
# From the backend directory
python -m pytest
```

## Code Quality

The project is configured with:

- **Ruff**: Fast Python linter and formatter written in Rust
  - 30x faster than Black for formatting
  - Handles both linting and formatting in a single tool
- **MyPy**: Type checker

Run these tools using:

```bash
# From the backend directory
# Lint code
python -m ruff check .

# Format code
python -m ruff format .

# Type check
python -m mypy .
```

Or use the scripts defined in the root package.json:

```bash
# From the root directory
yarn backend:lint    # Run Ruff linter
yarn backend:format  # Run Ruff formatter
```

### VS Code Integration

Add the following to your `.vscode/settings.json` file for automatic formatting on save:

```json
{
  "editor.formatOnSave": true,
  "[python]": {
    "editor.defaultFormatter": "charliermarsh.ruff",
    "editor.codeActionsOnSave": {
      "source.organizeImports": "explicit"
    }
  }
}
``` 