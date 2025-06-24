# API Reference - Habeas Backend

**API Version**: v2.0 (Multi-Profile Architecture)
**Base URL**: `http://localhost:8000` (development)
**Documentation**: Available at `/docs` (Swagger UI) and `/redoc` (ReDoc)

## Overview

The Habeas API provides endpoints for connecting detained individuals with legal representatives. The API uses an enhanced architecture supporting both traditional single-profile users and modern multi-profile family helpers.

### Key Features

- **Unified Signup**: Human-centered signup flow with progressive disclosure
- **Multi-Profile Support**: Family helpers can manage multiple client profiles
- **Role-Based Access**: Attorney, client helper, and admin roles
- **Comprehensive Profile Management**: Full CRUD operations for client profiles
- **Authentication**: Mock authentication for development/testing

## Authentication

All authenticated endpoints require a valid JWT token in the Authorization header:

```
Authorization: Bearer <jwt_token>
```

**Development Note**: The API currently uses mock authentication for development and testing purposes.

## Endpoint Categories

### 1. Health & Status
- `GET /health` - Health check endpoint

### 2. User Registration
- `POST /signup/unified` - Modern unified signup
- `POST /signup/multi-profile` - Multi-profile signup for family helpers
- `POST /signup/attorney` - Traditional attorney signup (legacy)
- `POST /signup/client` - Traditional client signup (legacy)

### 3. Profile Management
- `POST /client-profiles/` - Create client profile
- `GET /client-profiles/user/{user_id}` - Get user's profiles
- `GET /client-profiles/{profile_id}` - Get specific profile
- `PUT /client-profiles/{profile_id}` - Update profile
- `DELETE /client-profiles/{profile_id}` - Delete profile

### 4. User Management
- `GET /users/{id}` - Get user by ID
- `GET /users/cognito/{cognito_id}` - Get user by Cognito ID
- `PATCH /users/{id}` - Update user profile

### 5. Attorney Management
- `GET /attorneys` - List/search attorneys
- `GET /attorneys/{id}` - Get attorney profile
- `PATCH /attorneys/{id}` - Update attorney profile

### 6. Emergency Case Management
- `GET /emergency/users/{user_id}/status` - Check emergency information status
- `POST /emergency/cases` - Create emergency case
- `POST /emergency/cases/{case_id}/deactivate` - Deactivate emergency case
- `GET /emergency/cases/{case_id}/status` - Get emergency case status
- `GET /emergency/cases/available/{court_id}` - Get available cases for attorneys
- `POST /emergency/cases/{case_id}/accept` - Attorney accepts case
- `GET /emergency/courts/jurisdiction` - Determine court by location

### 7. Attorney Notifications
- `POST /emergency/notify/immediate` - Send immediate notifications
- `POST /emergency/notify/escalated` - Send escalated notifications
- `POST /emergency/notify/daily-digest` - Send daily digest
- `GET /emergency/attorneys/{attorney_id}/preferences` - Get notification preferences
- `PUT /emergency/attorneys/{attorney_id}/preferences` - Update notification preferences

### 8. Notification Testing
- `POST /emergency/test/notifications` - Test notification configuration
- `POST /emergency/test/sendgrid` - Test SendGrid configuration
- `POST /emergency/test/twilio` - Test Twilio configuration

---

## Detailed Endpoint Documentation

### User Registration Endpoints

#### POST /signup/unified

**Modern unified signup with role-based routing and human-centered language.**

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "SecurePassword123!",
  "role": "attorney",
  "attorney_data": {
    "name": "John Doe",
    "phone_number": "+1234567890",
    "zip_code": "90210",
    "state": "CA"
  }
}
```

**Response:**
```json
{
  "success": true,
  "message": "Account created successfully",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "primary_role": "attorney",
    "is_active": true
  },
  "auth_token": "mock_jwt_token_12345",
  "profile_data": {
    "attorney": {
      "id": 1,
      "name": "John Doe",
      "phone_number": "+1234567890",
      "zip_code": "90210",
      "state": "CA"
    }
  }
}
```

**Supported Roles:**
- `attorney` - Legal professional
- `client_helper` - Family helper managing client profiles
- `admin` - System administrator

---

#### POST /signup/multi-profile

**Multi-profile signup for family helpers managing multiple people.**

**Request Body:**
```json
{
  "email": "helper@example.com",
  "password": "SecurePassword123!",
  "has_attorney_capability": false,
  "client_profiles": [
    {
      "profile_name": "Myself",
      "is_self": true,
      "first_name": "Maria",
      "last_name": "Garcia",
      "country_of_birth": "Mexico",
      "birth_date": "1985-03-15"
    },
    {
      "profile_name": "My Brother",
      "is_self": false,
      "first_name": "Carlos",
      "last_name": "Garcia",
      "country_of_birth": "Mexico",
      "birth_date": "1990-07-22"
    }
  ]
}
```

**Response:**
```json
{
  "success": true,
  "message": "Multi-profile account created successfully",
  "user": {
    "id": 2,
    "email": "helper@example.com",
    "primary_role": "client_helper",
    "is_active": true
  },
  "auth_token": "mock_jwt_token_67890",
  "client_profiles": [
    {
      "id": 1,
      "profile_name": "Myself",
      "is_self": true,
      "first_name": "Maria",
      "last_name": "Garcia"
    },
    {
      "id": 2,
      "profile_name": "My Brother",
      "is_self": false,
      "first_name": "Carlos",
      "last_name": "Garcia"
    }
  ]
}
```

---

### Profile Management Endpoints

#### POST /client-profiles/

**Create a new client profile.**

**Request Body:**
```json
{
  "user_id": 1,
  "profile_name": "My Sister",
  "is_self": false,
  "first_name": "Ana",
  "last_name": "Garcia",
  "country_of_birth": "Mexico",
  "nationality": "Mexican",
  "birth_date": "1992-11-30",
  "alien_registration_number": "A123456789"
}
```

**Response:**
```json
{
  "id": 3,
  "user_id": 1,
  "profile_name": "My Sister",
  "is_self": false,
  "first_name": "Ana",
  "last_name": "Garcia",
  "country_of_birth": "Mexico",
  "nationality": "Mexican",
  "birth_date": "1992-11-30",
  "alien_registration_number": "A123456789",
  "created_at": "2025-01-21T10:30:00Z",
  "updated_at": "2025-01-21T10:30:00Z"
}
```

---

#### GET /client-profiles/user/{user_id}

**Get all client profiles for a specific user.**

**Response:**
```json
{
  "profiles": [
    {
      "id": 1,
      "profile_name": "Myself",
      "is_self": true,
      "first_name": "Maria",
      "last_name": "Garcia",
      "country_of_birth": "Mexico",
      "birth_date": "1985-03-15"
    },
    {
      "id": 2,
      "profile_name": "My Brother",
      "is_self": false,
      "first_name": "Carlos",
      "last_name": "Garcia",
      "country_of_birth": "Mexico",
      "birth_date": "1990-07-22"
    }
  ],
  "total_count": 2
}
```

---

#### GET /client-profiles/{profile_id}

**Get a specific client profile by ID.**

**Response:**
```json
{
  "id": 1,
  "user_id": 2,
  "profile_name": "Myself",
  "is_self": true,
  "first_name": "Maria",
  "last_name": "Garcia",
  "country_of_birth": "Mexico",
  "nationality": "Mexican",
  "birth_date": "1985-03-15",
  "alien_registration_number": null,
  "passport_number": null,
  "school_name": null,
  "student_id_number": null,
  "created_at": "2025-01-21T10:00:00Z",
  "updated_at": "2025-01-21T10:00:00Z"
}
```

---

#### PUT /client-profiles/{profile_id}

**Update a client profile.**

**Request Body:**
```json
{
  "profile_name": "My Mother",
  "nationality": "Mexican-American",
  "school_name": "UCLA",
  "student_id_number": "STU123456"
}
```

**Response:**
```json
{
  "id": 1,
  "user_id": 2,
  "profile_name": "My Mother",
  "is_self": true,
  "first_name": "Maria",
  "last_name": "Garcia",
  "country_of_birth": "Mexico",
  "nationality": "Mexican-American",
  "birth_date": "1985-03-15",
  "school_name": "UCLA",
  "student_id_number": "STU123456",
  "updated_at": "2025-01-21T11:00:00Z"
}
```

---

#### DELETE /client-profiles/{profile_id}

**Delete a client profile.**

**Response:**
```json
{
  "success": true,
  "message": "Client profile deleted successfully"
}
```

---

## Error Responses

All endpoints return consistent error responses:

### 400 Bad Request
```json
{
  "detail": "Validation error message"
}
```

### 404 Not Found
```json
{
  "detail": "Resource not found"
}
```

### 409 Conflict
```json
{
  "detail": "Email already registered"
}
```

### 422 Validation Error
```json
{
  "detail": [
    {
      "loc": ["body", "email"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

### 500 Internal Server Error
```json
{
  "detail": "Internal server error"
}
```

---

## Emergency System Endpoints

### GET /emergency/users/{user_id}/status

**Check if user has emergency information configured.**

**Response:**
```json
{
  "has_emergency_info": true,
  "emergency_contacts_count": 2,
  "client_profiles_count": 1
}
```

---

### POST /emergency/cases

**Create an emergency detention case with location and court assignment.**

**Request Body:**
```json
{
  "user_id": 123,
  "client_profile_id": 456,
  "case_type": "self",
  "detention_location": "Los Angeles, CA",
  "latitude": 34.0522,
  "longitude": -118.2437,
  "notes": "Detained at LAX airport"
}
```

**Response:**
```json
{
  "id": 789,
  "user_id": 123,
  "client_profile_id": 456,
  "case_type": "self",
  "status": "active",
  "detention_location": "Los Angeles, CA",
  "latitude": 34.0522,
  "longitude": -118.2437,
  "geocoded_address": "Los Angeles International Airport, Los Angeles, CA 90045, USA",
  "assigned_court": {
    "id": 5,
    "name": "Central District of California",
    "abbreviation": "CDCA"
  },
  "assigned_attorney_id": null,
  "created_at": "2025-01-21T15:30:00Z",
  "updated_at": "2025-01-21T15:30:00Z"
}
```

---

### GET /emergency/cases/{case_id}/status

**Get detailed status of an emergency case with real-time updates.**

**Response:**
```json
{
  "id": 789,
  "status": "attorney_assigned",
  "case_type": "self",
  "detention_location": "Los Angeles, CA",
  "assigned_court": {
    "name": "Central District of California",
    "abbreviation": "CDCA"
  },
  "assigned_attorney": {
    "id": 101,
    "name": "Sarah Johnson, Esq.",
    "email": "sarah@lawfirm.com",
    "phone_number": "+1234567890"
  },
  "attorney_assigned_at": "2025-01-21T16:15:00Z",
  "created_at": "2025-01-21T15:30:00Z",
  "time_elapsed": "45 minutes"
}
```

---

### PUT /emergency/attorneys/{attorney_id}/preferences

**Update attorney notification preferences for emergency cases.**

**Request Body:**
```json
{
  "email_enabled": true,
  "sms_enabled": true,
  "push_enabled": false,
  "sms_phone_number": "+1234567890",
  "daily_digest_enabled": true,
  "escalated_notifications_enabled": true
}
```

**Response:**
```json
{
  "id": 1,
  "attorney_id": 101,
  "email_enabled": true,
  "sms_enabled": true,
  "push_enabled": false,
  "sms_phone_number": "+1234567890",
  "daily_digest_enabled": true,
  "escalated_notifications_enabled": true,
  "updated_at": "2025-01-21T12:00:00Z"
}
```

---

### POST /emergency/test/notifications

**Test notification service configuration and delivery.**

**Request Body:**
```json
{
  "test_email": true,
  "test_sms": true,
  "recipient_email": "test@example.com",
  "recipient_phone": "+1234567890"
}
```

**Response:**
```json
{
  "sendgrid_configured": true,
  "sendgrid_test_result": "success",
  "sendgrid_message_id": "test-email-123",
  "twilio_configured": true,
  "twilio_test_result": "success",
  "twilio_message_sid": "test-sms-456",
  "overall_status": "success"
}
```

---

## Data Models

### User Model
```json
{
  "id": "integer",
  "cognito_id": "string",
  "user_type": "string (legacy)",
  "primary_role": "string (attorney|client_helper|admin)",
  "is_active": "boolean",
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

### ClientProfile Model
```json
{
  "id": "integer",
  "user_id": "integer",
  "profile_name": "string",
  "is_self": "boolean",
  "first_name": "string",
  "last_name": "string",
  "country_of_birth": "string",
  "nationality": "string (optional)",
  "birth_date": "date",
  "alien_registration_number": "string (optional)",
  "passport_number": "string (optional)",
  "school_name": "string (optional)",
  "student_id_number": "string (optional)",
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

### Attorney Model
```json
{
  "id": "integer",
  "user_id": "integer",
  "name": "string",
  "phone_number": "string",
  "email": "string",
  "zip_code": "string",
  "state": "string",
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

### EmergencyCase Model
```json
{
  "id": "integer",
  "user_id": "integer",
  "client_profile_id": "integer (optional)",
  "case_type": "string (self|loved_one)",
  "status": "string (active|attorney_assigned|resolved|deactivated)",
  "detention_location": "string (optional)",
  "latitude": "decimal (optional)",
  "longitude": "decimal (optional)",
  "geocoded_address": "string (optional)",
  "assigned_court_id": "integer (optional)",
  "assigned_attorney_id": "integer (optional)",
  "attorney_assigned_at": "datetime (optional)",
  "notes": "text (optional)",
  "created_at": "datetime",
  "updated_at": "datetime",
  "deactivated_at": "datetime (optional)"
}
```

### AttorneyNotificationPreference Model
```json
{
  "id": "integer",
  "attorney_id": "integer",
  "email_enabled": "boolean",
  "sms_enabled": "boolean",
  "push_enabled": "boolean",
  "sms_phone_number": "string (optional)",
  "daily_digest_enabled": "boolean",
  "escalated_notifications_enabled": "boolean",
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

---

## Migration Notes

### From Legacy to Multi-Profile Architecture

**Breaking Changes:**
- `clients` table replaced with `client_profiles`
- `emergency_contacts.client_id` renamed to `emergency_contacts.client_profile_id`
- New `users.primary_role` field added

**Backward Compatibility:**
- Legacy signup endpoints (`/signup/attorney`, `/signup/client`) still supported
- `users.user_type` field maintained for compatibility

**New Features:**
- Multi-profile support via `client_profiles` table
- Unified signup workflow with human-centered language
- Enhanced profile management capabilities

---

*Last Updated: January 2025*
*API Version: v2.0 (Multi-Profile Architecture)*
