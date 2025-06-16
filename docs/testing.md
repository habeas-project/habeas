# Habeas Testing Framework

## Overview

This document outlines the comprehensive testing strategy for the Habeas application, covering both frontend and backend components. Following the project's TDD approach, this plan details how to structure, implement, and maintain unit, integration, and end-to-end tests to ensure code quality and functionality.

## Backend Testing Architecture ✅

### Test Structure ✅

The backend testing architecture follows a hierarchical structure:

```
apps/backend/tests/
├── conftest.py                  # Fixtures shared across all test modules
├── unit/                        # Unit tests directory
│   ├── models/                  # Tests for database models
│   ├── schemas/                 # Tests for Pydantic schemas
│   └── services/                # Tests for business logic services
├── integration/                 # Integration tests directory
│   ├── routers/                 # API endpoint tests
│   └── services/                # Service integration tests
└── e2e/                         # End-to-end tests specific to backend flows
    └── api_flows/               # Complete API flow tests
```

### Backend Testing Framework ✅

- **Primary Framework**: pytest
- **API Testing**: FastAPI TestClient
- **Database Testing**: SQLAlchemy with PostgreSQL (`habeas_test`) for integration tests
- **Test Database**: Separate test database (`habeas_test`) for integration tests
- **Test Data Management**: Factory Boy with Faker integration
- **Dependency Management**: Dependency Injection via FastAPI

## Frontend Testing Architecture (Planned)

### Test Structure (To Do)

The frontend testing architecture (React Native) follows this structure:

```
apps/mobile/tests/             # Mobile app tests directory
├── setup/                     # Test setup and utilities
│   ├── test-utils.tsx         # Common RNTL test utilities and wrappers
│   └── mocks/                 # Mock data and services
├── unit/                      # Unit tests directory
│   ├── components/            # Individual component tests
│   ├── hooks/                 # Custom hook tests
│   └── utils/                 # Utility function tests
├── integration/               # Integration tests directory
│   ├── screens/               # Screen component tests
│   └── features/              # Feature integration tests
└── e2e/                       # End-to-end tests using Maestro
    └── flows/                 # YAML flow definitions for Maestro
```

### Frontend Testing Framework (To Do)

- **Primary Framework**: Jest (Test runner and framework)
- **Component/Integration Testing**: React Native Testing Library (RNTL)
- **API Mocking**: Consider MSW (Mock Service Worker) or Jest's built-in mocking
- **E2E Testing**: Maestro

## End-to-End Testing Architecture (Planned)

End-to-end (E2E) tests verify complete user flows on the mobile application interacting with the backend.

### Test Structure (To Do)

```
apps/mobile/tests/
└── e2e/                       # End-to-end tests directory
    ├── flows/                 # Maestro YAML flow definitions
    │   ├── attorney/          # Attorney workflows
    │   ├── client/            # Client workflows
    │   └── auth/              # Authentication workflows
    ├── setup/                 # Setup scripts or configurations for E2E tests
    └── utils/                 # Utility scripts for API interaction
```

### E2E Testing Framework (To Do)

- **Primary Framework**: Maestro (for mobile E2E automation)
- **Test Environment**: Docker Compose (for backend services)
- **API Interaction**: Axios or similar HTTP client for test setup/verification

## Test Types

### Backend Unit Tests ✅

Unit tests verify individual backend components in isolation, using mocks for external dependencies.

#### Model Tests ✅
- Test model instantiation with valid parameters
- Test model validation constraints (column types, nullable fields, etc.)
- Test model relationships (e.g., attorney to court admissions)
- Test model methods and properties

#### Schema Tests ✅
- Test schema validation for valid and invalid data
- Test schema conversion methods (model to schema, schema to model)
- Test schema inheritance and composition

#### Service Tests ✅
- Test service logic with mocked database interactions
- Test error handling and edge cases
- Test service method return values

### Backend Integration Tests ✅

Backend integration tests verify interactions between components with minimal mocking.

#### Router Tests ✅
- Test HTTP endpoints for correct status codes
- Test request validation
- Test response body structure and content
- Test error handling and edge cases

#### Service Integration Tests ✅
- Test service interactions with the database
- Test complex business logic spanning multiple services
- Test transactions and rollbacks

### Frontend Unit Tests (Planned)

Frontend unit tests verify individual React Native components, hooks, and utilities in isolation.

#### Component Tests (To Do)

```typescript
// Example RNTL component test
import React from 'react';
import { render, fireEvent } from '@testing-library/react-native';
import { AttorneyCard } from '@/components/AttorneyCard';

describe('AttorneyCard', () => {
  it('renders attorney information correctly', () => {
    const attorney = {
      id: 1,
      name: 'John Doe',
      email: 'john@example.com'
    };

    const { getByText } = render(<AttorneyCard attorney={attorney} />);

    expect(getByText(attorney.name)).toBeTruthy();
    expect(getByText(attorney.email)).toBeTruthy();
  });

  it('calls onSelect when pressed', () => {
    const onSelect = jest.fn();
    const attorney = { id: 1, name: 'John Doe' };

    const { getByTestId } = render(
      <AttorneyCard attorney={attorney} onSelect={onSelect} testID="attorney-card-touchable" />
    );

    fireEvent.press(getByTestId('attorney-card-touchable'));

    expect(onSelect).toHaveBeenCalledWith(attorney.id);
  });
});
```

#### Hook Tests (To Do)

```typescript
// Example hook test
import { renderHook, waitFor } from '@testing-library/react-native';
import { useAttorney } from '@/hooks/useAttorney';

jest.mock('@/services/api', () => ({
  fetchAttorney: jest.fn(),
}));

describe('useAttorney', () => {
  it('fetches attorney data successfully', async () => {
    const mockAttorneyData = {
      id: 1,
      name: 'John Doe',
      email: 'john@example.com'
    };

    fetchAttorney.mockResolvedValue(mockAttorneyData);

    const { result } = renderHook(() => useAttorney(1));

    await waitFor(() => {
      expect(result.current.attorney).toEqual(mockAttorneyData);
    });
  });
});
```

## Running Tests

### Backend Tests
```bash
# Run all backend tests
yarn backend:test

# Run specific test file
yarn backend:test tests/unit/models/test_attorney.py

# Run with coverage
yarn backend:test --cov=app --cov-report=html
```

### Frontend Tests (When Implemented)
```bash
# Run all frontend tests
yarn workspace mobile test

# Run in watch mode
yarn workspace mobile test --watch

# Run with coverage
yarn workspace mobile test --coverage
```

### E2E Tests (When Implemented)
```bash
# Run E2E tests
yarn test:e2e

# Run specific flow
maestro test apps/mobile/tests/e2e/flows/attorney-registration.yml
```

## Test Configuration

### Backend Configuration
- **pytest.ini**: Main pytest configuration
- **conftest.py**: Shared fixtures and test setup
- **Factory Boy**: Test data generation in `tests/factories.py`

### Frontend Configuration (To Do)
- **jest.config.js**: Jest configuration for React Native
- **setup-tests.ts**: Test environment setup
- **test-utils.tsx**: Common testing utilities and wrappers

## Best Practices

### General
- Write tests before implementing features (TDD approach)
- Keep tests focused and independent
- Use descriptive test names
- Maintain high test coverage for critical paths

### Backend Specific
- Use TestClient for API integration tests (not AsyncClient)
- Utilize database transactions for test isolation
- Mock external dependencies in unit tests
- Test both success and error scenarios

### Frontend Specific
- Test component behavior, not implementation details
- Use semantic queries (getByRole, getByText) over test IDs when possible
- Mock API calls and external dependencies
- Test user interactions and state changes

### E2E Specific
- Focus on critical user journeys
- Use stable selectors for UI elements
- Include setup and teardown for test data
- Run against test environment only
