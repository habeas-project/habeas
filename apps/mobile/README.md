# Habeas Mobile App

This is the mobile application for the Habeas project.

## Getting Started

### Prerequisites

- Node.js (version 16 or newer)
- npm or yarn
- Expo CLI

### Installation

1. Install dependencies:
   ```bash
   npm install
   # or
   yarn install
   ```

2. Start the development server:
   ```bash
   npm start
   # or
   yarn start
   ```

## API Client Generation

The mobile app uses a TypeScript client generated from the backend's OpenAPI specification. To update the API client:

1. Ensure the backend server is running locally:
   ```bash
   # From the root directory
   cd ../backend
   # Start the backend server using the instructions in the backend README
   ```

2. From the mobile directory, run the provided npm/yarn script:
   ```bash
   # Using npm
   npm run generate-api

   # Or using yarn
   yarn generate-api
   ```

   This script will:
   - Fetch the OpenAPI spec from the running backend
   - Generate the TypeScript client in src/api/generated

3. The generated client will be available in `src/api/generated` and is integrated into the app's API client in `src/api/client.ts`.

## Usage

The API client can be used in your components as follows:

```typescript
import api from '../api/client';

// Using the generated client
const examples = await api.api.readExamplesExamplesGet();

// Using the custom methods
const attorney = await api.registerAttorney({
  name: "Jane Doe",
  phoneNumber: "123-456-7890",
  email: "jane@example.com",
  zipCode: "12345",
  jurisdiction: "California"
});
```

## Project Structure

- `src/` - Source code
  - `api/` - API client and generated code
  - `screens/` - Screen components
  - `App.tsx` - Main app component
