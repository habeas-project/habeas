# Database Schema Documentation

This document outlines the database schema for the Habeas project backend, based on the SQLAlchemy models found in `apps/backend/app/models/`.

**Schema Version**: Multi-Profile Architecture (v2.0)
**Key Changes**: ClientProfile model replaces Client, multi-profile support, enhanced User model

## Core Tables

### Table: `users`

Represents system users with different roles and multi-profile support.

| Column       | Type               | Constraints                             | Description                               |
| ------------ | ------------------ | --------------------------------------- | ----------------------------------------- |
| `id`         | `Integer`          | Primary Key, Index                      | Unique identifier for the user            |
| `cognito_id` | `String(255)`      | Not Null, Unique                        | AWS Cognito user ID or mock ID            |
| `user_type`  | `String(20)`       | Not Null                                | **LEGACY**: User role: attorney, client, admin |
| `primary_role` | `String(20)`     | Not Null                                | **NEW**: Primary role: attorney, client_helper, admin |
| `is_active`  | `Boolean`          | Not Null, Default: True                 | Whether the user account is active        |
| `created_at` | `TIMESTAMP(timezone=True)` | Not Null, Server Default: `func.now()` | Timestamp of record creation              |
| `updated_at` | `TIMESTAMP(timezone=True)` | Not Null, Server Default: `func.now()`, On Update: `func.now()` | Timestamp of last record update |

**Relationships:**
- One-to-One with `attorneys` (via `attorneys.user_id`)
- **NEW**: One-to-Many with `client_profiles` (via `client_profiles.user_id`)
- One-to-One with `admins` (via `admins.user_id`)

**Migration Notes:**
- `primary_role` field added for enhanced multi-profile support
- `user_type` maintained for backward compatibility
- Multi-profile relationship added via `client_profiles`

---

### Table: `attorneys`

Represents legal professionals who can file habeas corpus petitions.

| Column         | Type               | Constraints                             | Description                           |
| -------------- | ------------------ | --------------------------------------- | ------------------------------------- |
| `id`           | `Integer`          | Primary Key, Index                      | Unique identifier for the attorney    |
| `user_id`      | `Integer`          | Not Null, Foreign Key (`users.id`), Unique | ID of the associated user account     |
| `name`         | `String(255)`      | Not Null                                | Attorney's full name                  |
| `phone_number` | `String(20)`       | Not Null                                | Attorney's phone number               |
| `email`        | `String(255)`      | Not Null, Unique                        | Attorney's email address              |
| `zip_code`     | `String(10)`       | Not Null                                | Attorney's zip code                   |
| `state`        | `String(2)`        | Not Null                                | Attorney's state (2-letter code)      |
| `created_at`   | `TIMESTAMP(timezone=True)` | Not Null, Server Default: `func.now()` | Timestamp of record creation          |
| `updated_at`   | `TIMESTAMP(timezone=True)` | Not Null, Server Default: `func.now()`, On Update: `func.now()` | Timestamp of last record update |

**Relationships:**
- One-to-One with `users` (via `user_id`)
- Many-to-Many with `courts` (via `attorney_court_admissions` junction table)

---

### Table: `client_profiles`

**NEW**: Represents client profiles with multi-profile support for family helpers.

| Column                    | Type               | Constraints                             | Description                               |
| ------------------------- | ------------------ | --------------------------------------- | ----------------------------------------- |
| `id`                      | `Integer`          | Primary Key, Index                      | Unique identifier for the client profile  |
| `user_id`                 | `Integer`          | Not Null, Foreign Key (`users.id`)     | ID of the associated user account         |
| `profile_name`            | `String(100)`      | Not Null                                | **NEW**: Name for this profile (e.g., "Mom", "Brother") |
| `is_self`                 | `Boolean`          | Not Null, Default: False                | **NEW**: Whether this profile represents the user themselves |
| `first_name`              | `String(100)`      | Not Null                                | Client's first name                       |
| `last_name`               | `String(100)`      | Not Null                                | Client's last name                        |
| `country_of_birth`        | `String(100)`      | Not Null                                | Client's country of birth                 |
| `nationality`             | `String(100)`      | Nullable                                | Client's nationality                      |
| `birth_date`              | `Date`             | Not Null                                | Client's date of birth                    |
| `alien_registration_number` | `String(20)`       | Nullable, Unique                        | Client's A-number                         |
| `passport_number`         | `String(20)`       | Nullable, Unique                        | Client's passport number                  |
| `school_name`             | `String(255)`      | Nullable                                | Name of the school the client attends     |
| `student_id_number`       | `String(50)`       | Nullable, Unique                        | Client's student ID number                |
| `created_at`              | `TIMESTAMP(timezone=True)` | Not Null, Server Default: `func.now()` | Timestamp of record creation              |
| `updated_at`              | `TIMESTAMP(timezone=True)` | Not Null, Server Default: `func.now()`, On Update: `func.now()` | Timestamp of last record update |

**Relationships:**
- Many-to-One with `users` (via `user_id`) - **NEW**: Supports multiple profiles per user
- One-to-Many with `emergency_contacts` (via `emergency_contacts.client_profile_id`)

**Multi-Profile Features:**
- **Family Helper Support**: One user can manage multiple client profiles
- **Profile Identification**: `profile_name` helps users organize multiple profiles
- **Self-Identification**: `is_self` flag indicates if profile represents the user themselves
- **Flexible Relationships**: No unique constraint on `user_id` allows multiple profiles per user

---

## Support Tables

### Table: `emergency_contacts`

Represents a person to contact in case of emergency for a client profile.

| Column                | Type               | Constraints                             | Description                                 |
| --------------------- | ------------------ | --------------------------------------- | ------------------------------------------- |
| `id`                  | `Integer`          | Primary Key, Index                      | Unique identifier for the emergency contact |
| `client_profile_id`   | `Integer`          | Not Null, Foreign Key (`client_profiles.id`), On Delete: CASCADE | **UPDATED**: ID of the associated client profile |
| `full_name`           | `String(255)`      | Not Null                                | Full name of the emergency contact          |
| `relationship`        | `String(50)`       | Not Null                                | Relationship to the client                  |
| `phone_number`        | `String(20)`       | Not Null                                | Phone number of the emergency contact       |
| `email`               | `String(255)`      | Nullable                                | Email address of the emergency contact      |
| `address`             | `String(255)`      | Nullable                                | Address of the emergency contact            |
| `notes`               | `Text`             | Nullable                                | Additional notes about the contact          |
| `created_at`          | `TIMESTAMP(timezone=True)` | Not Null, Server Default: `func.now()` | Timestamp of record creation                |
| `updated_at`          | `TIMESTAMP(timezone=True)` | Not Null, Server Default: `func.now()`, On Update: `func.now()` | Timestamp of last record update   |

**Relationships:**
- Many-to-One with `client_profiles` (via `client_profile_id`) - **UPDATED**: References client profiles instead of clients

**Migration Notes:**
- `client_id` field renamed to `client_profile_id` to reference new `client_profiles` table
- Maintains cascade delete behavior for data integrity

---

## Emergency Response Tables

### Table: `emergency_cases`

**NEW**: Tracks emergency detention cases with location and court assignment.

| Column                | Type               | Constraints                             | Description                                 |
| --------------------- | ------------------ | --------------------------------------- | ------------------------------------------- |
| `id`                  | `Integer`          | Primary Key, Index                      | Unique identifier for the emergency case    |
| `user_id`             | `Integer`          | Not Null, Foreign Key (`users.id`)     | ID of the user who created the case         |
| `client_profile_id`   | `Integer`          | Nullable, Foreign Key (`client_profiles.id`) | ID of the client profile (if applicable) |
| `case_type`           | `String(20)`       | Not Null                                | Type of case: "self" or "loved_one"         |
| `status`              | `String(20)`       | Not Null, Default: "active"             | Case status: active, attorney_assigned, resolved, deactivated |
| `detention_location`  | `String(255)`      | Nullable                                | Human-readable detention location           |
| `latitude`            | `Numeric(10,7)`    | Nullable                                | GPS latitude coordinate                     |
| `longitude`           | `Numeric(10,7)`    | Nullable                                | GPS longitude coordinate                    |
| `geocoded_address`    | `String(500)`      | Nullable                                | Reverse-geocoded address from coordinates   |
| `assigned_court_id`   | `Integer`          | Nullable, Foreign Key (`courts.id`)     | Federal district court assigned to case     |
| `assigned_attorney_id`| `Integer`          | Nullable, Foreign Key (`attorneys.id`)  | Attorney who accepted the case              |
| `attorney_assigned_at`| `TIMESTAMP(timezone=True)` | Nullable                        | Timestamp when attorney accepted case       |
| `notes`               | `Text`             | Nullable                                | Additional case notes or details            |
| `created_at`          | `TIMESTAMP(timezone=True)` | Not Null, Server Default: `func.now()` | Timestamp of case creation                  |
| `updated_at`          | `TIMESTAMP(timezone=True)` | Not Null, Server Default: `func.now()`, On Update: `func.now()` | Timestamp of last update |
| `deactivated_at`      | `TIMESTAMP(timezone=True)` | Nullable                        | Timestamp when case was deactivated         |

**Relationships:**
- Many-to-One with `users` (via `user_id`) - User who created the emergency case
- Many-to-One with `client_profiles` (via `client_profile_id`) - Client profile for the detained person
- Many-to-One with `courts` (via `assigned_court_id`) - Federal district court with jurisdiction
- Many-to-One with `attorneys` (via `assigned_attorney_id`) - Attorney who accepted the case

**Emergency Case Features:**
- **Multi-Scenario Support**: Handles both self-detention and loved one detention cases
- **Location Intelligence**: GPS coordinates with reverse geocoding to addresses
- **Court Assignment**: Automatic federal district court determination from location
- **Attorney Matching**: Voluntary attorney assignment based on court admissions
- **Status Tracking**: Complete case lifecycle from creation to resolution

---

### Table: `attorney_notification_preferences`

**NEW**: Attorney notification channel preferences for emergency cases.

| Column                          | Type               | Constraints                             | Description                                 |
| ------------------------------- | ------------------ | --------------------------------------- | ------------------------------------------- |
| `id`                            | `Integer`          | Primary Key, Index                      | Unique identifier for preferences           |
| `attorney_id`                   | `Integer`          | Not Null, Foreign Key (`attorneys.id`), Unique | ID of the attorney                    |
| `email_enabled`                 | `Boolean`          | Not Null, Default: True                 | Whether to send email notifications         |
| `sms_enabled`                   | `Boolean`          | Not Null, Default: False                | Whether to send SMS notifications           |
| `push_enabled`                  | `Boolean`          | Not Null, Default: False                | Whether to send push notifications          |
| `sms_phone_number`              | `String(20)`       | Nullable                                | Phone number for SMS notifications          |
| `daily_digest_enabled`          | `Boolean`          | Not Null, Default: True                 | Whether to receive daily digest emails      |
| `escalated_notifications_enabled` | `Boolean`        | Not Null, Default: True                 | Whether to receive escalated notifications  |
| `created_at`                    | `TIMESTAMP(timezone=True)` | Not Null, Server Default: `func.now()` | Timestamp of record creation                |
| `updated_at`                    | `TIMESTAMP(timezone=True)` | Not Null, Server Default: `func.now()`, On Update: `func.now()` | Timestamp of last update |

**Relationships:**
- One-to-One with `attorneys` (via `attorney_id`) - Attorney's notification preferences

**Notification Features:**
- **Multi-Channel Support**: Email, SMS, and push notification preferences
- **Granular Control**: Separate preferences for immediate, escalated, and daily digest notifications
- **Contact Management**: Separate SMS phone number from attorney's primary contact
- **Default Settings**: Sensible defaults with email enabled, SMS/push opt-in

---

## Legal System Tables

### Table: `courts`

Model for US District Courts.

| Column       | Type             | Constraints                             | Description                               |
| ------------ | ---------------- | --------------------------------------- | ----------------------------------------- |
| `id`         | `Integer`        | Primary Key, Index                      | Unique identifier for the court           |
| `name`       | `String(255)`    | Not Null, Index                         | Full name of the US District Court        |
| `abbreviation` | `String(10)`     | Not Null, Unique, Index                 | Abbreviation for the court                |
| `url`        | `String(255)`    | Not Null                                | URL for the court's website               |
| `created_at` | `DateTime(timezone=True)` | Not Null, Server Default: `func.now()` | Timestamp of record creation              |
| `updated_at` | `DateTime(timezone=True)` | Not Null, Server Default: `func.now()`, On Update: `func.now()` | Timestamp of last record update |

**Relationships:**
- Many-to-Many with `attorneys` (via `attorney_court_admissions` junction table)
- One-to-Many with `court_counties` (via `court_counties.court_id`)
- One-to-Many with `district_court_contacts` (via `district_court_contacts.court_id`)

---

### Table: `attorney_court_admissions`

Junction table for the many-to-many relationship between attorneys and courts.

| Column        | Type      | Constraints                             | Description                               |
| ------------- | --------- | --------------------------------------- | ----------------------------------------- |
| `attorney_id` | `Integer` | Primary Key, Foreign Key (`attorneys.id`) | ID of the attorney admitted to the court  |
| `court_id`    | `Integer` | Primary Key, Foreign Key (`courts.id`)    | ID of the court the attorney is admitted to |

**Relationships:**
- Junction table between `attorneys` and `courts` tables

---

### Table: `court_counties`

Mapping between courts and the counties they serve.

| Column    | Type          | Constraints                           | Description                    |
| --------- | ------------- | ------------------------------------- | ------------------------------ |
| `id`      | `Integer`     | Primary Key, Index                    | Unique identifier              |
| `court_id`| `Integer`     | Not Null, Foreign Key (`courts.id`)  | ID of the associated court     |
| `county`  | `String(100)` | Not Null                              | County name                    |
| `state`   | `String(2)`   | Not Null                              | State code (2-letter)          |

**Relationships:**
- Many-to-One with `courts` (via `court_id`)

---

### Table: `district_court_contacts`

Contact information for district courts.

| Column           | Type          | Constraints                           | Description                        |
| ---------------- | ------------- | ------------------------------------- | ---------------------------------- |
| `id`             | `Integer`     | Primary Key, Index                    | Unique identifier                  |
| `court_id`       | `Integer`     | Not Null, Foreign Key (`courts.id`)  | ID of the associated court         |
| `contact_type`   | `String(50)`  | Not Null                              | Type of contact (clerk, etc.)      |
| `phone_number`   | `String(50)`  | Nullable                              | Contact phone number               |
| `email`          | `String(255)` | Nullable                              | Contact email address              |
| `address`        | `Text`        | Nullable                              | Physical address                   |

**Relationships:**
- Many-to-One with `courts` (via `court_id`)

---

## Location and Facility Tables

### Table: `ice_detention_facilities`

ICE detention facilities information.

| Column                  | Type          | Constraints                             | Description                        |
| ----------------------- | ------------- | --------------------------------------- | ---------------------------------- |
| `id`                    | `Integer`     | Primary Key, Index                      | Unique identifier                  |
| `name`                  | `String(255)` | Not Null                                | Facility name                      |
| `facility_type`         | `String(100)` | Nullable                                | Type of facility                   |
| `address_line_1`        | `String(255)` | Nullable                                | First line of address              |
| `address_line_2`        | `String(255)` | Nullable                                | Second line of address             |
| `city`                  | `String(100)` | Nullable                                | City                               |
| `state`                 | `String(2)`   | Nullable                                | State (2-letter code)              |
| `zip_code`              | `String(10)`  | Nullable                                | ZIP code                           |
| `phone_number`          | `String(20)`  | Nullable                                | Phone number                       |
| `normalized_address_id` | `Integer`     | Nullable, Foreign Key (`normalized_addresses.id`) | Geocoded address reference |
| `created_at`            | `TIMESTAMP(timezone=True)` | Not Null, Server Default: `func.now()` | Timestamp of record creation       |
| `updated_at`            | `TIMESTAMP(timezone=True)` | Not Null, Server Default: `func.now()`, On Update: `func.now()` | Timestamp of last record update |

**Relationships:**
- Many-to-One with `normalized_addresses` (via `normalized_address_id`)

---

### Table: `normalized_addresses`

Geocoded and normalized address information.

| Column     | Type           | Constraints                             | Description                        |
| ---------- | -------------- | --------------------------------------- | ---------------------------------- |
| `id`       | `Integer`      | Primary Key, Index                      | Unique identifier                  |
| `latitude` | `Numeric(9,6)` | Not Null                                | Latitude coordinate                |
| `longitude`| `Numeric(9,6)` | Not Null                                | Longitude coordinate               |
| `county`   | `String(100)`  | Nullable                                | County name                        |
| `state`    | `String(2)`    | Not Null                                | State (2-letter code)              |
| `created_at` | `TIMESTAMP(timezone=True)` | Not Null, Server Default: `func.now()` | Timestamp of record creation       |
| `updated_at` | `TIMESTAMP(timezone=True)` | Not Null, Server Default: `func.now()`, On Update: `func.now()` | Timestamp of last record update |

**Relationships:**
- One-to-Many with `ice_detention_facilities` (via `ice_detention_facilities.normalized_address_id`)

---

## Data Relationships Summary

### Primary Entity Relationships

1. **User → Attorney/ClientProfile**: One-to-One (Attorney) and One-to-Many (ClientProfile) relationships through `user_id` foreign key
2. **Attorney → Courts**: Many-to-Many through `attorney_court_admissions` junction table
3. **ClientProfile → Emergency Contacts**: One-to-Many relationship
4. **Court → Counties**: One-to-Many relationship for jurisdictional mapping
5. **ICE Facility → Normalized Address**: Many-to-One for geocoding
6. **Emergency Case → User/ClientProfile/Court/Attorney**: Complex relationships for emergency response workflow
7. **Attorney → Notification Preferences**: One-to-One relationship for communication preferences

### Emergency Response Relationships

1. **Emergency Case Creation**: User creates emergency case, optionally linked to ClientProfile
2. **Court Assignment**: Emergency cases automatically assigned to federal district court based on location
3. **Attorney Notification**: Attorneys with court admissions receive notifications based on preferences
4. **Case Acceptance**: Attorneys voluntarily accept cases, creating attorney assignment relationship
5. **Multi-Channel Communication**: Notification preferences control email, SMS, and push delivery

### Key Design Patterns

- **User Account Integration**: All user types (attorney, client_helper) have corresponding User records
- **Multi-Profile Support**: Users can manage multiple client profiles for family members
- **Jurisdictional Mapping**: Courts mapped to counties for proper legal jurisdiction
- **Geographic Data**: ICE facilities and emergency cases linked to location data for jurisdiction determination
- **Emergency Response**: Complete workflow from case creation to attorney assignment with notification system
- **Communication Preferences**: Granular control over notification channels and timing
- **Audit Trail**: All tables include `created_at` and `updated_at` timestamps

This schema supports the core Habeas functionality of connecting detained individuals with qualified attorneys in the appropriate legal jurisdictions, with enhanced emergency response capabilities and multi-profile family support.
