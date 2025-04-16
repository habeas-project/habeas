# Habeas - Technical Documentation

<!-- TOC -->
- [Development Requirements](#development-requirements)
  - [System Dependencies](#system-dependencies)
    - [PostgreSQL and Development Package](#postgresql-and-development-package)
    - [Yarn Package Manager](#yarn-package-manager)
  - [Python Environment Setup](#python-environment-setup)
    - [Python Command Note](#python-command-note)
    - [Virtual Environment Activation](#virtual-environment-activation)
  - [Python Dependencies](#python-dependencies)
- [API Development Patterns](#api-development-patterns)
  - [Core Principles](#core-principles)
  - [Directory Structure](#directory-structure)
  - [Router Implementation Pattern](#router-implementation-pattern)
  - [Schema Organization](#schema-organization)
  - [Testing Strategy](#testing-strategy)
- [Database Migrations](#database-migrations)
  - [Overview](#overview)
  - [Migration Structure](#migration-structure)
  - [Running Migrations](#running-migrations)
- [Common Troubleshooting](#common-troubleshooting)
  - [pg_config executable not found](#pgconfig-executable-not-found)
  - [Python module not found](#python-module-not-found)
- [Development Tools](#development-tools)
  - [Pre-commit Hooks](#pre-commit-hooks)
    - [Setup](#setup)
    - [Configured Hooks](#configured-hooks)
    - [Configuration Files](#configuration-files)
    - [Troubleshooting](#troubleshooting)
<!-- /TOC -->

## Development Requirements

### System Dependencies

System-level dependencies required for development.

#### PostgreSQL and Development Package

Required for building the `psycopg2-binary` Python package.

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

Required for JavaScript dependency management and running project scripts via `package.json`. See official Yarn installation guides if needed.

**Ubuntu/Debian Example (Repository Method):**
```bash
curl -sS https://dl.yarnpkg.com/debian/pubkey.gpg | sudo apt-key add -
echo "deb https://dl.yarnpkg.com/debian/ stable main" | sudo tee /etc/apt/sources.list.d/yarn.list
sudo apt update
sudo apt install yarn
```

**macOS (with Homebrew):**
```bash
brew install yarn
```

### Python Environment Setup

1.  Ensure Python 3.12+ is installed.
2.  Install [uv](https://github.com/astral-sh/uv) for Python package management: `pip install uv`.
3.  Install system dependencies (see above).
4.  Run `yarn backend:install-dev` from the project root to set up the virtual environment and install dependencies using `uv sync` based on `apps/backend/pyproject.toml`.

#### Python Command Note

Scripts in `package.json` use `python3`. If you encounter "python: not found" or similar errors, ensure `python3` points to your Python 3.12+ installation or adjust the scripts accordingly.

#### Virtual Environment Activation

Python dependencies are installed via `uv` into `.venv` within `apps/backend/`. If running Python commands directly (outside of `yarn` scripts), activate the virtual environment first:

```bash
# From the apps/backend directory
source .venv/bin/activate
```

### Python Dependencies

Backend Python dependencies are managed using `uv` and defined in `apps/backend/pyproject.toml`. This includes main dependencies under `[project.dependencies]` and development dependencies under `[project.optional-dependencies.dev]`.

Run `yarn backend:sync` from the project root to install or update dependencies after changes to `pyproject.toml`.

## API Development Patterns

### Core Principles

-   Use synchronous FastAPI endpoints for simplicity and testing consistency.
-   Use FastAPI's synchronous `TestClient` for testing (configured in `pyproject.toml` via Ruff to disallow `httpx.AsyncClient` in tests).
-   Keep database interaction logic (CRUD) directly within router files for straightforward implementation and colocation.
-   Prioritize maintainability and clarity.

### Directory Structure

The backend code is organized within `apps/backend/app/`:

```
app/
├── routers/             # API route handlers with CRUD logic
├── models/              # SQLAlchemy models
├── schemas/             # Pydantic schemas for request/response validation
└── services/            # Business logic distinct from CRUD operations
```

> **Note on CRUD Location:** Database interaction logic (Create, Read, Update, Delete) resides directly within the API route handlers in `app/routers/`. There is no separate `app/crud/` directory.

### Router Implementation Pattern

Routers define API endpoints, handle request validation using Pydantic schemas, interact with the database via SQLAlchemy sessions (`Depends(get_db)`), and return responses.

Key elements include:
-   `APIRouter` instance with prefix and tags.
-   Standard HTTP methods (`@router.post`, `@router.get`, etc.).
-   Dependency injection for database sessions (`db: Session = Depends(get_db)`).
-   Pydantic models for request bodies (`model: ModelCreate`) and response models (`response_model=ModelResponse`).
-   Standard CRUD operations performed directly using the `db` session.
-   HTTPExceptions for error handling (e.g., 404 Not Found).

Refer to files within [`apps/backend/app/routers/`](../../apps/backend/app/routers/) for concrete examples.

### Schema Organization

Pydantic schemas, located in [`apps/backend/app/schemas/`](../../apps/backend/app/schemas/), define the data structures for API requests and responses. They follow a consistent pattern:

1.  **Base Schema**: Contains common fields and validation logic (`ModelBase`).
2.  **Create Schema**: Inherits from base, adding fields required only for creation (`ModelCreate`).
3.  **Update Schema**: Inherits from base, making fields optional for partial updates (`ModelUpdate`).
4.  **Response Schema**: Inherits from base, adding read-only fields like IDs or timestamps (`ModelResponse`).

This structure promotes code reuse and clear data contracts.

### Testing Strategy

API tests are located in [`apps/backend/tests/`](../../apps/backend/tests/). We use `pytest` and FastAPI's `TestClient` for synchronous integration testing against the API endpoints.

Key practices:
-   Use the `client: TestClient` fixture provided by FastAPI/Starlette.
-   Make requests to endpoint paths (e.g., `client.post("/models/", json=...)`).
-   Assert status codes (`response.status_code`) and response data (`response.json()`).

## Database Migrations

### Overview

[Alembic](https://alembic.sqlalchemy.org/) manages database schema migrations. Migration scripts are stored in [`apps/backend/migrations/versions/`](../../apps/backend/migrations/versions/).

### Migration Structure

-   `migrations/versions/`: Contains individual, ordered migration scripts.
-   `migrations/env.py`: Alembic environment configuration (defines how to connect to the DB and find models).
-   `migrations/script.py.mako`: Template for generating new migration files.

### Running Migrations

Use the `alembic` command (typically run from the `apps/backend` directory or via a `yarn` script if configured):

```bash
# Apply all migrations up to the latest version
alembic upgrade head

# Generate a new migration file based on model changes
# Review the generated script carefully before applying!
alembic revision --autogenerate -m "Brief description of changes"

# Revert the last applied migration
alembic downgrade -1
```

## Common Troubleshooting

### pg_config executable not found

**Error:** `error: pg_config executable not found`

**Cause:** Missing PostgreSQL development headers needed to build `psycopg2`.
**Solution:** Install the PostgreSQL development package for your OS (see [System Dependencies](#postgresql-and-development-package) section).

### Python module not found

**Error:** `ModuleNotFoundError: No module named 'fastapi'` (or similar)

**Cause:** The Python interpreter is running outside the project's virtual environment where dependencies are installed.
**Solution:** Activate the virtual environment (`source apps/backend/.venv/bin/activate`) before running Python commands directly, or use the configured `yarn` scripts which handle activation.

## Development Tools

### Pre-commit Hooks

This project uses [pre-commit](https://pre-commit.com/) hooks to automate code quality checks before each commit.

#### Setup

1.  Ensure development dependencies are installed: `yarn backend:install-dev` (from project root).
2.  Install the hooks into your local `.git` configuration:
    ```bash
    # Run from the project root or apps/backend directory
    pre-commit install
    ```

Hooks will now run automatically on `git commit`. To bypass them (not recommended): `git commit --no-verify`.

#### Configured Hooks

The project uses various hooks for:
-   Basic checks (whitespace, file endings, large files, merge conflicts, private keys).
-   Python linting and formatting (`ruff`).
-   Python type checking (`mypy`).
-   JavaScript/TypeScript linting (`eslint`).
-   Security scanning (`gitleaks`, `bandit`).

#### Configuration Files

-   Hook definitions and versions: [`.pre-commit-config.yaml`](../../.pre-commit-config.yaml) (root).
-   Python tool configurations (Ruff, MyPy, Bandit): [`apps/backend/pyproject.toml`](../../apps/backend/pyproject.toml).

#### Troubleshooting

If hooks fail unexpectedly:
1.  Ensure all dependencies are installed (`yarn backend:install-dev`).
2.  Verify the correct Python version/virtual environment is active if running manually.
3.  Try updating hook repositories: `pre-commit autoupdate`.
4.  Run hooks manually on all files to isolate issues: `pre-commit run --all-files`.
Refer to the official pre-commit documentation for more details.
