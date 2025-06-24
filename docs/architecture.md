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
- **Framework:** React Native (Expo managed workflow)
- **Language:** TypeScript
- **Package Management:** Yarn Classic (v1)
- **Key Dependencies:**
  - `expo-location`: GPS location services with permission management
  - `@react-native-async-storage/async-storage`: Persistent authentication storage
  - Navigation and UI components (React Navigation, React Native Elements)

### Backend
- **Framework:** FastAPI
- **Language:** Python 3.12
- **Database:** PostgreSQL
- **ORM:** SQLAlchemy with SQLModel patterns
- **Package Management:** uv
- **API Documentation:** Auto-generated with Swagger/OpenAPI (built into FastAPI)
- **External Services:**
  - **Email:** SendGrid for professional notification delivery
  - **SMS:** Twilio for text message notifications
  - **Geocoding:** Nominatim/OpenStreetMap for location services
- **Key Dependencies:**
  - `sendgrid`: Email notification delivery
  - `twilio`: SMS notification delivery
  - `requests`: HTTP client for geocoding API calls
  - `phonenumbers`: Phone number validation and formatting
  - `pydantic[email]`: Email validation

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

The backend implements an **enhanced router architecture** that provides clear separation of concerns while supporting the new multi-profile system and emergency response capabilities:

- **`/signup`** - User registration workflows (creates User + Attorney/ClientProfile + handles authentication)
- **`/unified-signup`** - **NEW**: Human-centered unified signup with role-based routing
- **`/client-profiles`** - **NEW**: Multi-profile management for client profiles
- **`/users`** - User entity management (authentication system integration, profile updates)
- **`/attorneys`** - Attorney entity management (discovery, profiles, court admissions)
- **`/emergency`** - **NEW**: Emergency case management and attorney notification system

#### Emergency Router (`/emergency`)

The emergency router provides comprehensive emergency response capabilities:

- **Case Management**: Create, deactivate, and track emergency cases
- **Attorney Notifications**: Immediate, escalated, and daily digest notifications
- **Court Jurisdiction**: GPS-based court determination and jurisdiction mapping
- **Case Assignment**: Attorney case acceptance and voluntary assignment
- **Notification Preferences**: Attorney notification channel management
- **Status Tracking**: Real-time case status updates and progress monitoring

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

**Emergency Case System**:
- **EmergencyCase Model**: Tracks detention cases with GPS coordinates and court assignments
- **AttorneyNotificationPreference Model**: Multi-channel notification preferences (email, SMS, push)
- **Court Integration**: Leverages existing Court and CourtCounty models for jurisdiction mapping
- **Location Services**: GPS coordinate capture with geocoding to court jurisdictions

### Architecture Benefits

1. **Multi-Profile Support**: Family helpers can manage multiple client profiles
2. **Clean Data Model**: No duplicate user records, proper normalization
3. **Flexible Roles**: Users can have attorney capability + client profiles
4. **Simplified Signup**: Single entry point with progressive disclosure
5. **Enhanced UX**: Human-centered language and workflow
6. **Emergency Response**: Real-time emergency case creation and attorney notification system
7. **Location Intelligence**: GPS-based court jurisdiction determination and address geocoding

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
- **HomeScreen**: Simplified with single "Get Help" entry point + Emergency Slider
- **Profile Management**: Future screens for managing multiple client profiles
- **Emergency Components**: Emergency slider, status display, and setup screens

### Emergency System Architecture

The mobile app implements a comprehensive emergency response system with conditional display and multi-scenario support:

```
HomeScreen (Authenticated User)
    ↓
Emergency Status Check → Has Emergency Info?
    ↓                           ↓
    Yes                         No
    ↓                           ↓
Emergency Slider            Emergency Setup Screen
    ↓
Activation Options:
- "I am about to be detained" (self)
- "Report Loved One Detention" (family member)
    ↓
Location Capture:
- GPS coordinates (with permission)
- Manual location entry (fallback)
    ↓
Case Creation & Attorney Notification
    ↓
Status Display: "Case posted - attorneys notified"
    ↓
Real-time Updates: "Attorney accepted case: [Name]"
```

#### Emergency Components

- **EmergencySlider**: Conditional display with "I am about to be detained" activation
- **EmergencyStatusDisplay**: Post-activation status with real-time attorney updates
- **EmergencySetupScreen**: Guided setup for users without emergency information
- **LovedOneEmergencyModal**: Multi-step loved one detention reporting
- **DetentionLocationInput**: Location capture with city/state or zip code input
- **LocationPermissionModal**: GPS permission education and request
- **PhoneSecurityModal**: Platform-specific phone locking instructions

#### Location Services Integration

- **GPS Capture**: expo-location with permission management
- **Geocoding**: Backend reverse geocoding via Nominatim/OpenStreetMap
- **Court Mapping**: GPS coordinates to federal district court jurisdiction
- **Fallback Flow**: Manual location entry if GPS unavailable

## Service Layer Architecture

The backend implements a comprehensive service layer that encapsulates business logic and external integrations:

### Core Services

#### EmergencyService (`app/services/emergency_service.py`)
- **Case Management**: Create, deactivate, and track emergency cases
- **Court Jurisdiction**: Determine federal district court from location data
- **Attorney Notification**: Integrate with NotificationService for multi-channel alerts
- **Status Tracking**: Monitor case progression and attorney assignment
- **Preference Management**: Handle attorney notification preferences

#### NotificationService (`app/services/notification_service.py`)
- **Multi-Channel Delivery**: Email (SendGrid), SMS (Twilio), Push (framework ready)
- **Template System**: Professional emergency notification templates
- **Preference Enforcement**: Respect attorney notification channel preferences
- **Delivery Tracking**: Monitor notification success/failure with retry logic
- **Configuration Testing**: Built-in service health checks

#### GeocodingService (`app/services/geocoding_service.py`)
- **Reverse Geocoding**: Convert GPS coordinates to addresses via Nominatim/OpenStreetMap
- **Court Mapping**: Determine federal district court jurisdiction from coordinates
- **Rate Limiting**: Comply with free service requirements (1 request/second)
- **Error Handling**: Graceful fallback for API failures
- **Coordinate Validation**: Ensure GPS coordinates are within valid bounds

### External Service Integration

#### Email Notifications (SendGrid)
- **Professional Templates**: HTML email with action buttons and emergency branding
- **Delivery Tracking**: Message ID tracking and delivery status monitoring
- **Error Handling**: Graceful degradation when service unavailable

#### SMS Notifications (Twilio)
- **Concise Messaging**: Automatic truncation for SMS length limits
- **Phone Number Management**: Separate SMS numbers from attorney contact info
- **Delivery Status**: Track SMS delivery and handle failures

#### Location Services (Nominatim/OpenStreetMap)
- **Free Service**: No API key required for basic geocoding
- **Rate Limiting**: Built-in compliance with service terms
- **Address Parsing**: Extract city, county, state, postal code
- **Court Jurisdiction**: Map location data to federal district courts

### Service Integration Patterns

#### Emergency Case Creation Flow
```
1. EmergencyService.create_emergency_case()
2. → GeocodingService.geocode_and_determine_jurisdiction()
3. → EmergencyService._notify_attorneys_for_court()
4. → NotificationService.send_immediate_case_notification()
5. → SendGrid/Twilio API calls (based on preferences)
```

#### Notification Scheduling
```
1. Immediate: T+0 (case creation)
2. Escalated: T+1 hour (EmergencyService.send_escalated_notifications())
3. Daily Digest: Morning (EmergencyService.send_daily_digest())
```

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
