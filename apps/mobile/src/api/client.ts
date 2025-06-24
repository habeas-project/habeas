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
  firstName?: string;
  lastName?: string;
  countryOfBirth?: string;
  birthDate?: string;
  nationality?: string;
  alienRegistrationNumber?: string;
  passportNumber?: string;
  schoolName?: string;
  studentIdNumber?: string;
}

// Interface for attorney registration data
interface AttorneyRegistrationData {
  name: string;
  phoneNumber: string;
  email: string;
  zipCode: string;
  jurisdiction: string;
  password?: string; // Optional since it might not be provided in all scenarios
}

// Interface for client registration data
interface ClientRegistrationData {
  firstName: string;
  lastName: string;
  countryOfBirth: string;
  birthDate: string; // YYYY-MM-DD format
  password: string;
  // Optional fields
  nationality?: string;
  alienRegistrationNumber?: string;
  passportNumber?: string;
  schoolName?: string;
  studentIdNumber?: string;
}

// Unified signup interfaces
export interface UnifiedSignupData {
  email: string;
  password: string;
  primary_role: 'attorney' | 'client_helper' | 'admin';
}

export interface RoleSpecificData {
  attorney_data?: AttorneyRegistrationData;
  client_profile_data?: ClientProfileData;
  admin_data?: AdminRegistrationData;
}

export interface ClientProfileData {
  profile_name: string;
  is_self: boolean;
  first_name: string;
  last_name: string;
  country_of_birth: string;
  nationality?: string;
  birth_date: string;
  alien_registration_number?: string;
  passport_number?: string;
  school_name?: string;
  student_id_number?: string;
}

export interface AdminRegistrationData {
  name: string;
  email: string;
  department: string;
  role: string;
}

export interface MultiProfileSignupData {
  email: string;
  password: string;
  primary_role: 'client_helper';
  client_profiles: ClientProfileData[];
  attorney_data?: AttorneyRegistrationData;
}

export interface UnifiedSignupResponse {
  message: string;
  user_id: number;
  email: string;
  primary_role: string;
  created_at: string;
}

export interface MultiProfileSignupResponse {
  message: string;
  user_id: number;
  email: string;
  profiles_created: number;
  created_at: string;
}

export interface ClientProfileResponse {
  id: number;
  user_id: number;
  profile_name: string;
  is_self: boolean;
  first_name: string;
  last_name: string;
  country_of_birth: string;
  nationality?: string;
  birth_date: string;
  alien_registration_number?: string;
  passport_number?: string;
  school_name?: string;
  student_id_number?: string;
  created_at: string;
  updated_at: string;
}

// --- Emergency-related interfaces ---

export interface LocationData {
  latitude?: number;
  longitude?: number;
  address?: string;
  description?: string;
}

export interface EmergencyStatusResponse {
  has_emergency_contacts: boolean;
  has_client_profiles: boolean;
  active_emergency_case_id?: number;
  active_case_status?: string;
  assigned_attorney_name?: string;
  assigned_court_name?: string;
  can_activate_emergency: boolean;
}

export interface EmergencyActivationRequest {
  client_profile_id: number;
  case_type: 'self' | 'loved_one';
  location: LocationData;
}

export interface EmergencyActivationResponse {
  case_id: number;
  status: string;
  assigned_court_name?: string;
  message: string;
  attorneys_notified_count: number;
}

export interface EmergencyStatusUpdate {
  case_id: number;
  status: string;
  assigned_attorney_name?: string;
  assigned_court_name?: string;
  last_updated: string;
  created_at: string;
  message: string;
  attorneys_notified_count?: number;
}

export interface EmergencyDeactivationRequest {
  reason?: string;
}

export interface EmergencyDeactivationResponse {
  success: boolean;
  message: string;
}

export interface CourtJurisdictionResponse {
  court_id: number;
  court_name: string;
  court_abbreviation: string;
  confidence: number;
  message: string;
}

// --- Smart Configuration from Environment Variables ---

// Function to detect the best API base URL
function getApiBaseUrl(): string {
  // 1. Try to get from environment variables first
  const envApiUrl = process.env.EXPO_PUBLIC_API_BASE_URL;
  if (envApiUrl) {
    return envApiUrl;
  }

  // 2. Try Constants.expoConfig.extra (fallback)
  const configApiUrl = Constants.expoConfig?.extra?.EXPO_PUBLIC_API_BASE_URL;
  if (configApiUrl) {
    return configApiUrl;
  }

  // 3. Development warning - configuration should be provided
  if (__DEV__) {
    console.warn('⚠️  No API_BASE_URL configured. Using localhost fallback.');
    console.warn('💡 For WSL testing, run: ./temp/update_wsl_ip.sh to configure proper IP');
    return 'http://localhost:8000';
  }

  // 4. Production fallback
  return 'http://localhost:8000';
}

function getAuthMode(): string {
  return process.env.EXPO_PUBLIC_AUTH_MODE ??
    Constants.expoConfig?.extra?.EXPO_PUBLIC_AUTH_MODE ??
    (__DEV__ ? 'mock' : 'cognito');
}

const apiBaseUrl = getApiBaseUrl();
const authMode = getAuthMode();

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

  registerAttorney: async (formData: AttorneyRegistrationData) => {
    console.log("Using attorney signup endpoint");

    // Prepare the signup data according to the backend schema
    const signupData = {
      name: formData.name,
      phone_number: formData.phoneNumber,
      email: formData.email,
      zip_code: formData.zipCode,
      state: formData.jurisdiction.toUpperCase(), // Ensure uppercase for state validation
      password: formData.password, // Password must be explicitly provided
    };

    if (!signupData.password) {
      throw new Error("Password is required for attorney registration.");
    }
    try {
      // Call the signup endpoint directly using axiosInstance
      const response = await axiosInstance.post('/signup/attorney', signupData);
      return response.data;
    } catch (error) {
      console.error('Attorney registration failed:', error);
      throw error;
    }
  },

  registerClient: async (formData: ClientRegistrationData) => {
    console.log("Using client signup endpoint");

    // Prepare the signup data according to the backend schema
    const signupData = {
      first_name: formData.firstName,
      last_name: formData.lastName,
      country_of_birth: formData.countryOfBirth,
      birth_date: formData.birthDate,
      password: formData.password,
      // Optional fields
      nationality: formData.nationality || null,
      alien_registration_number: formData.alienRegistrationNumber || null,
      passport_number: formData.passportNumber || null,
      school_name: formData.schoolName || null,
      student_id_number: formData.studentIdNumber || null,
    };

    try {
      // Call the signup endpoint directly using axiosInstance
      const response = await axiosInstance.post('/signup/client', signupData);
      return response.data;
    } catch (error) {
      console.error('Client registration failed:', error);
      throw error;
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

/**
 * Register user via unified signup endpoint
 */
export const registerUnified = async (
  signupData: UnifiedSignupData,
  roleData: RoleSpecificData
): Promise<UnifiedSignupResponse> => {
  try {
    console.log('Registering user via unified signup:', {
      email: signupData.email,
      role: signupData.primary_role
    });

    const response = await axiosInstance.post('/signup/unified', {
      signup_data: signupData,
      role_data: roleData
    });

    console.log('Unified signup successful:', response.data);
    return response.data;
  } catch (error) {
    console.error('Unified signup failed:', error);
    throw error;
  }
};

/**
 * Register user with multiple client profiles
 */
export const registerMultiProfile = async (
  signupData: MultiProfileSignupData
): Promise<MultiProfileSignupResponse> => {
  try {
    console.log('Registering multi-profile user:', {
      email: signupData.email,
      profileCount: signupData.client_profiles.length
    });

    const response = await axiosInstance.post('/signup/multi-profile', signupData);

    console.log('Multi-profile signup successful:', response.data);
    return response.data;
  } catch (error) {
    console.error('Multi-profile signup failed:', error);
    throw error;
  }
};

/**
 * Create a new client profile for an existing user
 */
export const createClientProfile = async (
  profileData: ClientProfileData & { user_id: number }
): Promise<ClientProfileResponse> => {
  try {
    console.log('Creating client profile:', {
      user_id: profileData.user_id,
      profile_name: profileData.profile_name
    });

    const response = await axiosInstance.post('/client-profiles/', profileData);

    console.log('Client profile created:', response.data);
    return response.data;
  } catch (error) {
    console.error('Client profile creation failed:', error);
    throw error;
  }
};

/**
 * Get all client profiles for a user
 */
export const getUserClientProfiles = async (userId: number): Promise<ClientProfileResponse[]> => {
  try {
    console.log('Fetching client profiles for user:', userId);

    const response = await axiosInstance.get(`/client-profiles/user/${userId}`);

    console.log('Client profiles fetched:', response.data);
    return response.data;
  } catch (error) {
    console.error('Failed to fetch client profiles:', error);
    throw error;
  }
};

/**
 * Update a client profile
 */
export const updateClientProfile = async (
  profileId: number,
  updateData: Partial<ClientProfileData>
): Promise<ClientProfileResponse> => {
  try {
    console.log('Updating client profile:', { profileId, updateData });

    const response = await axiosInstance.put(`/client-profiles/${profileId}`, updateData);

    console.log('Client profile updated:', response.data);
    return response.data;
  } catch (error) {
    console.error('Client profile update failed:', error);
    throw error;
  }
};

/**
 * Delete a client profile
 */
export const deleteClientProfile = async (profileId: number): Promise<void> => {
  try {
    console.log('Deleting client profile:', profileId);

    await axiosInstance.delete(`/client-profiles/${profileId}`);

    console.log('Client profile deleted successfully');
  } catch (error) {
    console.error('Client profile deletion failed:', error);
    throw error;
  }
};

// --- Emergency API Methods ---

/**
 * Get emergency status for a user
 */
export const getUserEmergencyStatus = async (userId: number): Promise<EmergencyStatusResponse> => {
  const response = await axiosInstance.get(`/emergency/users/${userId}/status`);
  return response.data;
};

/**
 * Create an emergency case
 */
export const createEmergencyCase = async (
  userId: number,
  request: EmergencyActivationRequest
): Promise<EmergencyActivationResponse> => {
  const response = await axiosInstance.post(
    `/emergency/cases?user_id=${userId}`,
    request
  );
  return response.data;
};

/**
 * Get emergency case status
 */
export const getEmergencyCaseStatus = async (caseId: number): Promise<EmergencyStatusUpdate> => {
  const response = await axiosInstance.get(`/emergency/cases/${caseId}/status`);
  return response.data;
};

/**
 * Deactivate an emergency case
 */
export const deactivateEmergencyCase = async (
  caseId: number,
  userId: number,
  request: EmergencyDeactivationRequest
): Promise<EmergencyDeactivationResponse> => {
  const response = await axiosInstance.post(
    `/emergency/cases/${caseId}/deactivate?user_id=${userId}`,
    request
  );
  return response.data;
};

/**
 * Get court jurisdiction based on location
 */
export const getCourtJurisdiction = async (
  latitude: number,
  longitude: number
): Promise<CourtJurisdictionResponse> => {
  const response = await axiosInstance.get(
    `/emergency/courts/jurisdiction?latitude=${latitude}&longitude=${longitude}`
  );
  return response.data;
};

/**
 * Poll for emergency case status updates
 * This function will repeatedly check case status until attorney is assigned or case is resolved
 */
export const pollEmergencyCaseStatus = async (
  caseId: number,
  onStatusUpdate: (status: EmergencyStatusUpdate) => void,
  pollingInterval: number = 30000, // 30 seconds
  maxPollingTime: number = 3600000 // 1 hour
): Promise<void> => {
  const startTime = Date.now();
  let isPolling = true;

  const poll = async () => {
    try {
      const status = await getEmergencyCaseStatus(caseId);
      onStatusUpdate(status);

      // Stop polling if case is resolved, attorney assigned, or deactivated
      if (status.status === 'attorney_assigned' ||
        status.status === 'resolved' ||
        status.status === 'deactivated') {
        isPolling = false;
        return;
      }

      // Stop polling if max time exceeded
      if (Date.now() - startTime > maxPollingTime) {
        isPolling = false;
        return;
      }

      // Schedule next poll
      if (isPolling) {
        setTimeout(poll, pollingInterval);
      }
    } catch (error) {
      console.error('Error polling emergency case status:', error);
      // Continue polling even if individual requests fail
      if (isPolling && Date.now() - startTime < maxPollingTime) {
        setTimeout(poll, pollingInterval * 2); // Longer interval on error
      }
    }
  };

  // Start polling
  poll();
};

// --- Location Services ---

import * as Location from 'expo-location';

/**
 * Request location permissions from the user
 */
export const requestLocationPermission = async (): Promise<boolean> => {
  try {
    const { status } = await Location.requestForegroundPermissionsAsync();
    return status === 'granted';
  } catch (error) {
    console.error('Failed to request location permission:', error);
    return false;
  }
};

/**
 * Get user's current location with GPS coordinates
 * Uses expo-location for Expo managed workflow
 */
export const getCurrentLocation = async (): Promise<LocationData | null> => {
  try {
    // Check if location services are enabled
    const isLocationEnabled = await Location.hasServicesEnabledAsync();
    if (!isLocationEnabled) {
      console.log('Location services are disabled');
      return null;
    }

    // Request permission if not already granted
    const hasPermission = await requestLocationPermission();
    if (!hasPermission) {
      console.log('Location permission denied');
      return null;
    }

    // Get current position with basic accuracy for speed
    const location = await Location.getCurrentPositionAsync({
      accuracy: Location.Accuracy.Balanced, // Faster than High, more accurate than Low
      timeInterval: 10000, // 10 second timeout
      distanceInterval: 0, // No distance filtering
    });

    if (!location) {
      console.log('Failed to get location');
      return null;
    }

    return {
      latitude: location.coords.latitude,
      longitude: location.coords.longitude,
      description: `GPS: ${location.coords.latitude.toFixed(4)}, ${location.coords.longitude.toFixed(4)}`,
    };
  } catch (error) {
    console.error('Failed to get current location:', error);
    return null;
  }
};
