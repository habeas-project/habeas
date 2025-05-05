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
    - [Local CI Testing (`act`)](#local-ci-testing-act)
  - [Continuous Integration (CI)](#continuous-integration-ci)
    - [Workflow Overview](#workflow-overview)
    - [Key Steps](#key-steps)
- [React Native/Expo Development](#react-native-expo-development)
  - [Running the Mobile App](#running-the-mobile-app)
- [Testing](#testing)
  - [Mobile End-to-End (E2E) Testing Setup](#mobile-end-to-end-e2e-testing-setup)
    - [E2E Docker Environment](#e2e-docker-environment)
    - [Prerequisites](#prerequisites)
    - [Running E2E Tests](#running-e2e-tests)
    - [Troubleshooting](#troubleshooting)

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

Tests are located in [`apps/backend/tests/`](../../apps/backend/tests/) and organized into a structured hierarchy. We use `pytest` as our testing framework with additional dependencies such as `factory-boy` for generating test data and FastAPI's `TestClient` for integration testing.

#### Test Directory Structure

```
tests/
├── conftest.py                 # Shared pytest fixtures
├── factories.py                # Factory Boy model factories
├── unit/                       # Unit tests
│   ├── models/                 # Tests for SQLAlchemy models
│   ├── schemas/                # Tests for Pydantic schemas
│   └── services/               # Tests for service layer functions
├── integration/                # Integration tests
│   ├── routers/                # Tests for API endpoints
│   └── services/               # Tests for services with DB interactions
└── __init__.py
```

#### Types of Tests

1. **Unit Tests**:
   - **Model Tests**: Verify model relationships, constraints, and properties
   - **Schema Tests**: Validate Pydantic schema validation rules
   - **Service Tests**: Test service layer functions in isolation

2. **Integration Tests**:
   - **Router Tests**: Test API endpoints using FastAPI's TestClient
   - **Service Integration Tests**: Test service interactions with the database

#### Key Testing Components

- **Test Database**: Tests use an in-memory SQLite database to avoid affecting production data
- **TestClient**: FastAPI's `TestClient` provides an interface for making HTTP requests to API endpoints
- **Factory Boy**: Generates test data for models with realistic values
- **Fixtures**: Common test fixtures in `conftest.py` provide database sessions and factories

#### Key Fixtures

```python
# Database session fixture
@pytest.fixture(scope="function")
def db_session(db_engine):
    """Create a new database session for a test."""
    SessionLocal = sessionmaker(bind=db_engine)
    session = SessionLocal()
    try:
        yield session
    finally:
        session.rollback()
        session.close()

# FastAPI TestClient with DB session override
@pytest.fixture
def client(db_session):
    """Create a test client using the test database session."""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()

# Factory fixtures
@pytest.fixture
def AttorneyTestFactory(SessionScopedFactory):
    """Factory fixture for creating Attorney instances."""
    class TestAttorneyFactory(AttorneyFactory, SessionScopedFactory):
        pass
    return TestAttorneyFactory
```

#### Running Tests

Execute tests using pytest:

```bash
# Run all tests
pytest

# Run specific test categories
pytest tests/unit/
pytest tests/integration/

# Run tests with specific markers
pytest -m unit
pytest -m integration

# Generate test coverage report
pytest --cov=app
```

#### Testing Practices

- **Mock only when necessary**: Prefer testing against the test database for more realistic tests
- **Use markers**: Apply `@pytest.mark.unit` and `@pytest.mark.integration` to categorize tests
- **Test exceptions**: Validate that appropriate exceptions are raised using `pytest.raises`
- **Isolate tests**: Each test should be independent and not rely on state from other tests
- **Test validation**: Ensure schema validation works by testing both valid and invalid inputs
- **Mock Authentication**: Utilize the mock authentication system for relevant development and testing scenarios (see below).

## Mock Authentication (Development/Testing)

### Overview

The mock authentication system provides simplified authentication endpoints for development and testing purposes. These endpoints simulate AWS Cognito authentication without requiring a real Cognito instance to be configured.

### Important Security Warning

**⚠️ NEVER ENABLE MOCK AUTHENTICATION IN PRODUCTION ENVIRONMENTS ⚠️**

The mock authentication system bypasses normal security measures and is intended **only** for:
- Local development
- Automated testing (including E2E tests)
- CI/CD pipeline testing

### How It Works

The mock auth router (`app.routers.mock_auth`) provides two main endpoints when enabled:
- `/mock/register` - Register a new user with only email/password.
- `/mock/login` - Login with email/password to get a standard JWT token.

These endpoints allow easy creation of test users and acquisition of valid tokens for testing protected API routes.

### Enabling Mock Authentication

The system is controlled by the `ENABLE_MOCK_AUTH` environment variable:

```
ENABLE_MOCK_AUTH=true  # Enable mock auth endpoints
ENABLE_MOCK_AUTH=false # Disable mock auth endpoints (default)
```

### Where to Set ENABLE_MOCK_AUTH

This variable should **only** be set in non-production contexts:

1.  **Local Development:** In your root `.env` file (which is gitignored) or exported directly in your shell (`export ENABLE_MOCK_AUTH=true`).
2.  **Automated Tests:**
    *   **Backend:** Set globally via fixture in `apps/backend/tests/conftest.py` or locally using `monkeypatch.setenv("ENABLE_MOCK_AUTH", "true")`.
    *   **E2E:** The `docker-compose.e2e.yml` file sets `ENABLE_MOCK_AUTH=true` for the `backend_e2e` service.
3.  **CI/CD Pipeline:** Set as an environment variable in specific test jobs/steps within the workflow file (e.g., `.github/workflows/test.yml`).

### Testing with Mock Authentication

-   **Direct Unit Tests:** For testing the mock router itself, include it directly in a test FastAPI app instance.
-   **Integration/E2E Tests:** Ensure the environment variable is set as described above when testing the main application. The `TestClient` or mobile app will then be able to hit the `/mock/register` and `/mock/login` endpoints.

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

## React Native Expo Development

### Running the Mobile App

The mobile app uses React Native with Expo. Start development with:

```bash
# From the project root
yarn dev:mobile

# Or from the mobile directory
cd apps/mobile
yarn start
```

### WSL Development Considerations

When developing in Windows Subsystem for Linux (WSL), there are networking challenges when connecting from physical devices to the Expo development server. To address these issues:

1. **Start Docker Desktop**

2. **Run Docker Compose**
  ```bash
  # From apps/ directory
  docker-compose up -d
  ```

3. **Use tunnel mode (recommended):**
   ```bash
   # From the mobile directory
   npx expo start --tunnel
   ```
   This creates a secure tunnel allowing your device to connect regardless of network configuration.


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

### Local CI Testing (`act`)

To run the GitHub Actions workflow locally for faster feedback, you can use [act](https://github.com/nektos/act).

#### Prerequisites

1.  **Docker:** Must be installed and running on your local machine.
2.  **`act` Installation:** `act` needs to be installed separately. It is *not* managed via project dependencies.

    *   **macOS / Linux (using Homebrew):**
        ```bash
        brew install act
        ```
    *   **Other Linux / macOS (using script):**
        ```bash
        curl --proto '=https' --tlsv1.2 -sSf https://raw.githubusercontent.com/nektos/act/master/install.sh | sudo bash
        ```
    *   **See official documentation for all methods:** [nektosact.com/installation/](https://nektosact.com/installation/)

#### Usage

1.  **Secrets:** Create a `.secrets` file in the project root (this file is ignored by git) containing necessary secrets:
    ```plaintext
    # .secrets
    DB_PASSWORD=your_local_dev_password
    ```
2.  **Run:** Execute the workflow using the yarn script:
    ```bash
    yarn test:ci:local
    ```
    This script runs `act -W .github/workflows/test.yml`.

## Continuous Integration (CI)

A GitHub Actions workflow (`.github/workflows/test.yml`) automates backend testing to ensure code quality and stability.

### Workflow Overview

- **Trigger:** Runs on pushes and pull requests to `main` targeting changes in the backend (`apps/backend/`, `apps/tests/`), Docker configuration (`apps/docker-compose.yml`), Python dependencies (`pyproject.toml`), or the workflow file itself.
- **Environment:** Uses Docker Compose (`apps/docker-compose.yml`) to build and run services within an `ubuntu-latest` GitHub Actions runner.
- **Secrets:** Requires the `DB_PASSWORD` secret to be configured in the GitHub repository settings.

### Key Steps

1.  **Checkout Code:** Retrieves the latest code from the repository.
2.  **Set up Docker:** Initializes Docker Buildx.
3.  **Set Environment Variables:** Exports `DATABASE_URL` and `DB_PASSWORD` (using the GitHub secret) for Docker Compose.
4.  **Start Database:** Starts the PostgreSQL service (`db`) using `docker-compose up -d`.
5.  **Wait for Database:** Checks if the database is ready before proceeding.
6.  **Build Backend Image:** Explicitly builds the backend service image, passing `--build-arg INSTALL_DEV=true` to ensure development and testing dependencies are included in the image (`docker compose build --build-arg INSTALL_DEV=true backend`).
7.  **Run Migrations:** Executes database migrations using the `migration` service (`docker-compose run --rm migration`).
8.  **Run Tests:** Runs backend tests (`pytest`) using the pre-built `backend` service image (`docker compose run --rm backend uv run pytest tests`). The `--build` flag is not used here as the image was built in a prior step.
9.  **Cleanup:** Stops and removes Docker Compose services and volumes (`docker-compose down -v --remove-orphans`).

This ensures that migrations and tests are run against a clean, consistent environment on relevant code changes.

## Testing

### Mobile End-to-End (E2E) Testing Setup

Mobile E2E tests use [Maestro](https://maestro.mobile.dev/) to interact with the UI of the mobile application. For a consistent environment, especially across different machines or in CI, the E2E tests utilize a Docker-based setup for the backend services.

#### E2E Docker Environment

The backend environment is defined in [`docker-compose.e2e.yml`](../../docker-compose.e2e.yml) and includes:

*   `db_e2e`: A PostgreSQL database container for test data (`habeas_test`).
*   `backend_e2e`: The backend service built from its Dockerfile, configured to use the test DB and with mock authentication enabled (`ENABLE_MOCK_AUTH=true`).

**Note:** The Android emulator itself is expected to run **outside** of this Docker Compose setup (e.g., started via Android Studio or a physical device connected via ADB). The test runner script (`scripts/testing/run_tests.sh`) verifies that a device/emulator is available via `adb devices` before proceeding.

#### Prerequisites

1.  **Docker and Docker Compose:** Must be installed and running to manage the backend services.
2.  **Android SDK Platform-Tools:** The `adb` command is required on the host machine to communicate with the target emulator or device. Ensure it's installed and in your system PATH.
    *   Install via Android Studio (`Settings` > `Appearance & Behavior` > `System Settings` > `Android SDK` > `SDK Tools` tab > Select `Android SDK Platform-Tools`).
    *   Or, download command-line tools from the [Android Developers website](https://developer.android.com/tools/releases/platform-tools) and add the `platform-tools` directory to your PATH.
    *   Verify by running `adb --version` in your terminal.
3.  **Maestro CLI:** Required to execute the Maestro test flows (`.yml` files).
    *   Install via: `curl -Ls https://get.maestro.mobile.dev | bash`
    *   Verify by running `maestro --version`.
4.  **Running Emulator/Device:** An Android emulator (e.g., from Android Studio) must be running, or a physical device connected and authorized for debugging (`adb devices` should list the target).
5.  **Mobile App Installation:** The mobile application **must be manually built and installed** onto the target emulator/device *before* running the Maestro tests. The test runner script does **not** handle app installation.

#### Running E2E Tests (Semi-Automated)

The test runner script automates the backend environment setup and triggers Maestro, but requires manual preparation:

1.  **Ensure Prerequisites:** Verify Docker is running, `adb` and `maestro` are in your PATH.
2.  **Start Emulator/Connect Device:** Launch your target Android emulator or connect your physical device. Ensure it's listed by `adb devices`.
3.  **Build & Install App:** Manually build the mobile app (e.g., `yarn build:android:dev`) and install the resulting `.apk` onto the target emulator/device (e.g., `adb install <path_to_apk>`). Ensure the app launches correctly.
4.  **Execute the Script:** Run the following command from the project root:
    ```bash
    ./scripts/testing/run_tests.sh --type mobile --e2e
    ```
5.  **Script Actions:**
    *   Starts backend services (`db_e2e`, `backend_e2e`) using `docker-compose.e2e.yml`.
    *   Waits for the `backend_e2e` service to become healthy.
    *   Verifies a device/emulator is connected via `adb`.
    *   Delegates to `scripts/testing/run_tests.py`, which executes `maestro test flows/` (or a specific flow if provided).
    *   Automatically stops the Docker backend services upon completion or interruption.

**Current Status:** The Maestro flow file (`apps/mobile/tests/e2e/flows/attorney-registration.yml`) exists but requires verification of UI selectors and is not yet fully validated or integrated into a fully automated CI process. Testing currently involves the manual steps outlined above.

#### Troubleshooting

*   **Emulator/Device Connection Issues:**
    *   Ensure only one target device/emulator is active or understand Maestro will target the first listed by `adb devices`.
    *   Verify the device is fully booted, unlocked, and authorized.
    *   Check for ADB conflicts (e.g., stop other instances, run `adb kill-server && adb start-server`).
*   **Backend Service Issues:**
    *   Check Docker container logs: `docker compose -f docker-compose.e2e.yml logs backend_e2e db_e2e`.
    *   Ensure ports (e.g., 8000 for backend, 5432 for db) are not already in use on the host if networking issues arise.
*   **Maestro Fails:**
    *   Check Maestro output in the test log file (`temp/logs/test_run_*.log`).
    *   Verify UI selectors in the `.yml` flow file match the current app UI (`maestro hierarchy` can help).
    *   Ensure the mobile app was correctly installed and can communicate with the backend service (check API URLs).
