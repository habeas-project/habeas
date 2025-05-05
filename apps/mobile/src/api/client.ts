import 'react-native-url-polyfill/auto';
import Constants from 'expo-constants';
import {
  AttorneysApi,
  AttorneyCreate,
  ClientsApi,
  ClientCreate,
  EmergencyContactsApi,
  EmergencyContactCreate,
  Configuration,
  // MockAuthApi removed as it's not generated
} from './generated';
import axios from 'axios';

// --- Interfaces for API Data ---

interface LoginCredentials {
  email: string;
  password: string;
}

// Interface for registration data - can be expanded for different user types
interface UserRegistrationData {
  email: string;
  password: string;
  // Attorney-specific fields (optional)
  name?: string;
  phoneNumber?: string;
  zipCode?: string;
  jurisdiction?: string; // Maps to 'state' in AttorneyCreate
  // Client-specific fields could be added here (optional)
  // ...
}

// --- Configuration from Environment Variables ---

// Expo Go requires environment variables to be prefixed with EXPO_PUBLIC_
// Access them via Constants.expoConfig.extra
const apiBaseUrl = Constants.expoConfig?.extra?.EXPO_PUBLIC_API_BASE_URL ?? 'http://localhost:8000'; // Default for safety
const authMode = Constants.expoConfig?.extra?.EXPO_PUBLIC_AUTH_MODE ?? 'cognito'; // Default to 'cognito' (real auth)

console.log(`API Config: BaseURL=${apiBaseUrl}, AuthMode=${authMode}`); // For debugging

// --- Base Configuration ---

const baseConfiguration = new Configuration({
  basePath: apiBaseUrl,
});

// --- Axios Instance ---

// Create an axios instance configured with the base URL
const axiosInstance = axios.create({
  baseURL: apiBaseUrl,
});

// --- API Client Instances ---

// Always instantiate main APIs
const attorneysApi = new AttorneysApi(baseConfiguration, undefined, axiosInstance);
const clientsApi = new ClientsApi(baseConfiguration, undefined, axiosInstance);
const emergencyContactsApi = new EmergencyContactsApi(baseConfiguration, undefined, axiosInstance);

// MockAuthApi instance removed

// --- Combined API Client ---

// Main API client with methods that match the application's needs
const api = {
  // --- Authentication ---
  register: async (userData: UserRegistrationData) => {
    if (authMode === 'mock') {
      console.log("Using MOCK registration endpoint");
      // Call mock endpoint directly using axiosInstance
      // The backend mock router expects { email: string, password: string }
      // We only need email and password for the mock call, even if more data is present
      const mockRegisterData = { email: userData.email, password: userData.password };
      return axiosInstance.post('/mock/register', mockRegisterData);
    } else {
      console.log("Using REAL registration endpoint (Not Implemented Yet)");
      // TODO: Implement call to real registration endpoint (Cognito flow)

      // Example placeholder for real attorney registration
      // Check for necessary attorney fields before proceeding
      if (userData.name && userData.phoneNumber && userData.zipCode && userData.jurisdiction) {
        const attorneyData: AttorneyCreate = {
          name: userData.name,
          phone_number: userData.phoneNumber,
          email: userData.email, // Email is always present
          zip_code: userData.zipCode,
          state: userData.jurisdiction, // Mapping jurisdiction to state field
        };
        // Use the generated client for the real endpoint
        return attorneysApi.createAttorneyAttorneysPost(attorneyData);
      } else {
        // Handle other user types or throw error if data is insufficient/mismatched
        // For now, assume only attorney registration is possible via this path
        throw new Error("Real registration logic requires complete attorney data or is not implemented for this user type.");
      }
    }
  },

  login: async (credentials: LoginCredentials) => {
    if (authMode === 'mock') {
      console.log("Using MOCK login endpoint");
      // Call mock endpoint directly using axiosInstance
      // The backend mock router uses { username: string, password: string }
      // Mapping email to username for the mock endpoint
      const mockLoginData = { username: credentials.email, password: credentials.password };
      return axiosInstance.post('/mock/login', mockLoginData);
    } else {
      // TODO: Implement call to real login endpoint (Cognito flow)
      console.log("Using REAL login endpoint (Not Implemented Yet)");
      throw new Error('Real login not implemented');
    }
  },

  // --- Original Attorney Registration (kept for reference, maybe remove later) ---
  // registerAttorney: async (formData: { ... }) => { ... }, // Original function

  // --- Other API methods ---
  createClient: async (clientData: ClientCreate) => {
    return clientsApi.createClientClientsPost(clientData);
  },

  createEmergencyContact: async (contactData: EmergencyContactCreate) => {
    return emergencyContactsApi.createEmergencyContactEmergencyContactsPost(contactData);
  },

  // Add other methods as needed, wrapping the generated clients
  // e.g., getAttorneyById, getClients, etc.
};

export default api;
