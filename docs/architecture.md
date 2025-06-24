# Habeas - Architecture Documentation

## Project Overview

Habeas is an open-source project designed to help detained individuals connect with legal representatives who can file habeas corpus petitions on their behalf. The goal is to facilitate rapid pairing between detained persons and legal representatives in the appropriate jurisdictions.

## Architecture Overview

The project follows a monorepo structure with a React Native mobile application frontend (written in TypeScript) and a Python FastAPI backend that communicates with a PostgreSQL database. The architecture separates the frontend and backend while providing a clear organization for shared resources.

**Key Architectural Features:**
- **Multi-Profile Data Model**: Support allowing family helpers to manage multiple client profiles
- **Unified Signup Workflow**: Human-centered signup flow with progressive disclosure
- **Role-Based Architecture**: Single user accounts with role-specific capabilities
- **Enhanced Profile Management**: Support for users managing multiple client profiles under one account

## Repository Structure

```
/habeas                  <-- Root of monorepo
├── apps/                <-- Directory for deployable applications
│   ├── mobile/          <-- React Native application (TypeScript)
│   │   ├── android/     # Android native project files
│   │   ├── ios/         # iOS native project files
│   │   ├── src/         # React Native TypeScript source code
│   │   ├── app.json     # App configuration
│   │   ├── index.js     # Entry point
│   │   ├── package.json # Mobile app's dependencies & scripts
│   │   └── tsconfig.json# TypeScript config for mobile
│   │
│   └── backend/         <-- FastAPI service (Python)
│       ├── app/         # Main application source directory
│       │   ├── __init__.py
│       │   ├── main.py    # FastAPI app instance and entry point
│       │   ├── routers/   # API route definitions
│       │   ├── models/    # Database models (SQLAlchemy/SQLModel)
│       │   ├── schemas/   # Pydantic schemas
│       │   └── services/  # Business logic
│       ├── tests/       # Backend tests
│       ├── pyproject.toml # Python dependencies and tool configurations
│       └── .env         # Environment variables (add to .gitignore)
│
├── docs/                <-- Documentation
│   └── architecture.md  # This file
│   └── technical.md     # Technical requirements and troubleshooting
│
├── .gitignore           # Git ignore patterns
├── package.json         # Root package.json for Yarn workspace config
│                        # Defines workspaces and root dev dependencies
├── yarn.lock            # Yarn lock file
└── README.md            # Project overview
```

## Technology Stack

### Frontend (Mobile)
- **Framework:** React Native
- **Language:** TypeScript
- **Package Management:** Yarn Classic (v1)
- **Key Dependencies:** (To be determined as development progresses)

### Backend
- **Framework:** FastAPI
- **Language:** Python 3.12
- **Database:** PostgreSQL
- **ORM:** SQLAlchemy or SQLModel
- **Package Management:** uv
- **API Documentation:** Auto-generated with Swagger/OpenAPI (built into FastAPI)

### Development Tools
- **Monorepo Management:** Yarn Workspaces
- **Version Control:** Git
- **Code Formatting/Linting:** Ruff for Python (linting and formatting), MyPy for Python type checking, ESLint for TypeScript/JavaScript

## Communication Between Frontend and Backend

The React Native mobile app will communicate with the FastAPI backend through RESTful API endpoints. The backend will:

1. Process requests from the frontend
2. Interact with the PostgreSQL database
3. Implement business logic
4. Return appropriate responses to the frontend

The API will handle authentication, data retrieval/storage, and any other server-side operations required by the application.

### API Router Architecture

The backend implements an **enhanced router architecture** that provides clear separation of concerns while supporting the new multi-profile system:

- **`/signup`** - User registration workflows (creates User + Attorney/ClientProfile + handles authentication)
- **`/unified-signup`** - **NEW**: Human-centered unified signup with role-based routing
- **`/client-profiles`** - **NEW**: Multi-profile management for client profiles
- **`/users`** - User entity management (authentication system integration, profile updates)
- **`/attorneys`** - Attorney entity management (discovery, profiles, court admissions)

This enhanced architecture supports both traditional single-profile users and modern multi-profile family helpers, ensuring transaction safety for multi-entity creation while maintaining clear API semantics. For detailed information about router responsibilities and design rationale, see the [Router Architecture section in technical.md](technical.md#router-architecture).

## Data Model Architecture

### Enhanced User Model

The system uses an **enhanced approach** that combines the benefits of unified user accounts with multi-profile support:

```
User (primary_role: attorney|client_helper|admin)
├── Attorney (1:1) - if primary_role = attorney
├── ClientProfile (1:many) - if primary_role = client_helper
└── Admin (1:1) - if primary_role = admin
```

### Key Model Changes

**ClientProfile Model** (replaces Client):
- **Multi-Profile Support**: Users can have multiple ClientProfile records
- **Profile Identification**: `profile_name` and `is_self` fields for profile management
- **Family Helper Support**: Allows one account to manage multiple people's information
- **Clean Relationships**: Proper foreign keys with `client_profiles` table

**Enhanced User Model**:
- **Primary Role Field**: `primary_role` enum (attorney, client_helper, admin)
- **Multi-Profile Relationships**: `client_profiles` relationship for 1:many support
- **Backward Compatible**: Maintains existing attorney and admin relationships

**Updated Emergency Contacts**:
- **ClientProfile Integration**: References `client_profile_id` instead of `client_id`
- **Cascade Support**: Proper deletion cascading for data integrity

### Architecture Benefits

1. **Multi-Profile Support**: Family helpers can manage multiple client profiles
2. **Clean Data Model**: No duplicate user records, proper normalization
3. **Flexible Roles**: Users can have attorney capability + client profiles
4. **Simplified Signup**: Single entry point with progressive disclosure
5. **Enhanced UX**: Human-centered language and workflow

## Mobile Application Architecture

### Unified Signup Flow

The mobile app implements a **human-centered signup workflow** with progressive disclosure:

```
HomeScreen → "Get Help" → UnifiedSignupScreen
    ↓
Intent Selection:
- "I'm worried that ICE may detain me or a loved one"
- "I am an attorney willing to file a habeas petition"
    ↓
Account Info (email, password)
    ↓
Role-Specific Details (based on intent)
    ↓
Confirmation & Account Creation
    ↓
Success → Return to HomeScreen
```

### Key UX Improvements

- **Human-Centered Language**: "I'm worried that ICE may detain me or a loved one" vs technical role selection
- **Empathetic Messaging**: "Get connected with legal help and prepare for potential detention"
- **Unified Entry Point**: Single "Get Help" button replaces separate signup buttons
- **Progressive Disclosure**: Intent → Account → Details → Confirmation flow
- **Role-Based Forms**: Different form fields based on user selection

### Screen Architecture

- **UnifiedSignupScreen**: 4-step progressive disclosure signup process
- **HomeScreen**: Simplified with single "Get Help" entry point
- **Profile Management**: Future screens for managing multiple client profiles

## Testing Architecture

The project implements a comprehensive testing strategy focused on backend code quality and reliability.

### Backend Testing Structure

The backend testing infrastructure follows a hierarchical organization:

```
/apps/backend/tests/           <-- Test root directory
├── conftest.py                # Global test fixtures
├── factories.py               # Factory Boy model factories
├── unit/                      # Unit tests for isolated components
│   ├── models/                # Tests for database models and relationships
│   ├── schemas/               # Tests for Pydantic schema validation
│   └── services/              # Tests for service layer business logic
├── integration/               # Integration tests
│   ├── routers/               # API endpoint tests using TestClient
│   └── services/              # Service integration with database
└── __init__.py
```

### Testing Tools & Dependencies

- **Primary Framework**: pytest
- **Test Database**: In-memory SQLite for isolation and speed
- **Test Data Generation**: Factory Boy for creating test model instances
- **API Testing**: FastAPI's TestClient for simulating HTTP requests
- **Additional Tools**: pytest-cov for coverage reporting, faker for generating realistic test data

### Testing Approach

1. **Unit Testing**:
   - Isolated component testing
   - Model relationship verification
   - Schema validation testing
   - Service layer logic testing with appropriate exceptions

2. **Integration Testing**:
   - API endpoint behavior verification
   - Database interaction testing
   - End-to-end flow testing

3. **Test Markers**:
   - `@pytest.mark.unit`: Unit tests
   - `@pytest.mark.integration`: Integration tests
   - `@pytest.mark.slow`: Tests that might take longer to execute

### Testing Fixtures

Testing fixtures in `conftest.py` provide reusable components for tests:

- Database session fixtures with transaction isolation
- TestClient fixture with database session override
- Factory Boy factory fixtures with session injection

This approach enables efficient test execution while maintaining test isolation and reproducibility.

## Development Workflow

### Frontend Development
- Run `yarn workspace mobile start` from the project root to start the React Native development server
- Use platform-specific commands for running on simulators/devices:
  - iOS: `yarn workspace mobile ios`
  - Android: `yarn workspace mobile android`

### Backend Development
- Set up the Python environment with `yarn backend:install-dev` from the project root
- Run the development server with `yarn dev:backend`
- Format Python code with `yarn backend:format`
- Lint Python code with `yarn backend:lint`
- Access the auto-generated API documentation at `http://localhost:8000/docs`

### Adding Dependencies
- **Frontend:** `yarn workspace mobile add <package-name>`
- **Backend:**
  - Add dependencies to `apps/backend/pyproject.toml`
  - Run `yarn backend:sync` to update the virtual environment
