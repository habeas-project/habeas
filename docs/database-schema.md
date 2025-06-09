# Database Schema Documentation

This document outlines the database schema for the Habeas project backend, based on the SQLAlchemy models found in `apps/backend/app/models/`.

## Core Tables

### Table: `users`

Represents system users with different roles (attorney, client, admin).

| Column       | Type               | Constraints                             | Description                               |
| ------------ | ------------------ | --------------------------------------- | ----------------------------------------- |
| `id`         | `Integer`          | Primary Key, Index                      | Unique identifier for the user            |
| `cognito_id` | `String(255)`      | Not Null, Unique                        | AWS Cognito user ID or mock ID            |
| `user_type`  | `String(20)`       | Not Null                                | User role: attorney, client, admin        |
| `is_active`  | `Boolean`          | Not Null, Default: True                 | Whether the user account is active        |
| `created_at` | `TIMESTAMP(timezone=True)` | Not Null, Server Default: `func.now()` | Timestamp of record creation              |
| `updated_at` | `TIMESTAMP(timezone=True)` | Not Null, Server Default: `func.now()`, On Update: `func.now()` | Timestamp of last record update |

**Relationships:**
- One-to-One with `attorneys` (via `attorneys.user_id`)
- One-to-One with `clients` (via `clients.user_id`)

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

### Table: `clients`

Represents individuals who may file a habeas corpus petition.

| Column                    | Type               | Constraints                             | Description                               |
| ------------------------- | ------------------ | --------------------------------------- | ----------------------------------------- |
| `id`                      | `Integer`          | Primary Key, Index                      | Unique identifier for the client          |
| `user_id`                 | `Integer`          | Not Null, Foreign Key (`users.id`), Unique | ID of the associated user account         |
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
- One-to-One with `users` (via `user_id`)
- One-to-Many with `emergency_contacts` (via `emergency_contacts.client_id`)

---

## Support Tables

### Table: `emergency_contacts`

Represents a person to contact in case of emergency for a client.

| Column         | Type               | Constraints                             | Description                                 |
| -------------- | ------------------ | --------------------------------------- | ------------------------------------------- |
| `id`           | `Integer`          | Primary Key, Index                      | Unique identifier for the emergency contact |
| `client_id`    | `Integer`          | Not Null, Foreign Key (`clients.id`), On Delete: CASCADE | ID of the associated client               |
| `full_name`    | `String(255)`      | Not Null                                | Full name of the emergency contact          |
| `relationship` | `String(50)`       | Not Null                                | Relationship to the client                  |
| `phone_number` | `String(20)`       | Not Null                                | Phone number of the emergency contact       |
| `email`        | `String(255)`      | Nullable                                | Email address of the emergency contact      |
| `address`      | `String(255)`      | Nullable                                | Address of the emergency contact            |
| `notes`        | `Text`             | Nullable                                | Additional notes about the contact          |
| `created_at`   | `TIMESTAMP(timezone=True)` | Not Null, Server Default: `func.now()` | Timestamp of record creation                |
| `updated_at`   | `TIMESTAMP(timezone=True)` | Not Null, Server Default: `func.now()`, On Update: `func.now()` | Timestamp of last record update   |

**Relationships:**
- Many-to-One with `clients` (via `client_id`)

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

1. **User → Attorney/Client**: One-to-One relationship through `user_id` foreign key
2. **Attorney → Courts**: Many-to-Many through `attorney_court_admissions` junction table
3. **Client → Emergency Contacts**: One-to-Many relationship
4. **Court → Counties**: One-to-Many relationship for jurisdictional mapping
5. **ICE Facility → Normalized Address**: Many-to-One for geocoding

### Key Design Patterns

- **User Account Integration**: All user types (attorney, client) have corresponding User records
- **Jurisdictional Mapping**: Courts mapped to counties for proper legal jurisdiction
- **Geographic Data**: ICE facilities linked to normalized addresses for location-based matching
- **Audit Trail**: All tables include `created_at` and `updated_at` timestamps

This schema supports the core Habeas functionality of connecting detained individuals with qualified attorneys in the appropriate legal jurisdictions.
