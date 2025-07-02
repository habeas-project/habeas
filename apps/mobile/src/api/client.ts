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
import { logger, LogCategory } from '../utils/logger';

// Track request metadata using a Map to avoid axios type conflicts
const requestMetadata = new Map<string, { requestId: string; startTime: number }>();

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

// Attorney case management interfaces
export interface AvailableCaseResponse {
  case_id: number;
  case_type: 'self' | 'loved_one';
  location_description: string;
  court_name: string;
  created_at: string;
  urgency_level: 'urgent' | 'high' | 'medium' | 'low';
}

export interface AttorneyCaseAcceptanceRequest {
  message?: string;
}

export interface AttorneyCaseAcceptanceResponse {
  success: boolean;
  message: string;
  case_id: number;
  client_contact_info: {
    client_info: {
      first_name: string;
      last_name: string;
      phone_number?: string;
      email?: string;
    };
    emergency_contacts: Array<{
      name: string;
      relationship: string;
      phone: string;
      email?: string;
    }>;
    case_notes?: string;
  };
}

export interface DetailedCaseResponse {
  case_id: number;
  case_type: 'self' | 'loved_one';
  status: 'active' | 'attorney_assigned' | 'resolved' | 'deactivated';
  created_at: string;
  updated_at: string;
  urgency_level: 'urgent' | 'high' | 'medium' | 'low';
  detention_location: {
    description: string;
    city?: string;
    state?: string;
    latitude?: number;
    longitude?: number;
  };
  court_info: {
    court_name: string;
    court_abbreviation: string;
    district_court_contact?: {
      phone?: string;
      email?: string;
    };
  };
  client_info: {
    first_name: string;
    last_name: string;
    case_type: 'self' | 'loved_one';
  };
  time_since_created: string;
  attorneys_notified_count: number;
  case_notes?: string;
  // Full contact info only available after case acceptance
  full_contact_info?: {
    phone_number?: string;
    email?: string;
    emergency_contacts?: Array<{
      name: string;
      relationship: string;
      phone: string;
      email?: string;
    }>;
  };
}

// --- Attorney Notification Preferences Interfaces ---

export interface AttorneyNotificationPreferencesRequest {
  email_enabled: boolean;
  sms_enabled: boolean;
  push_enabled: boolean;
  sms_phone_number?: string;
  daily_digest_enabled: boolean;
  escalated_notifications_enabled: boolean;
}

export interface AttorneyNotificationPreferencesResponse {
  attorney_id: number;
  email_enabled: boolean;
  sms_enabled: boolean;
  push_enabled: boolean;
  sms_phone_number?: string;
  daily_digest_enabled: boolean;
  escalated_notifications_enabled: boolean;
  created_at: string;
  updated_at: string;
}

// --- Daily Digest Interfaces ---

export interface CourtCoverageStats {
  court_id: number;
  court_name: string;
  total_attorneys: number;
  active_cases: number;
  unassigned_cases: number;
}

export interface DailyDigestResponse {
  unassigned_cases: AvailableCaseResponse[];
  court_coverage_stats: { [courtId: string]: CourtCoverageStats };
  total_unassigned: number;
  digest_date: string;
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
    logger.warn(LogCategory.API, 'No API_BASE_URL configured. Using localhost fallback.');
    logger.warn(LogCategory.API, 'For WSL testing, run: ./temp/update_wsl_ip.sh to configure proper IP');
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

logger.info(LogCategory.API, 'API Configuration initialized', {
  baseUrl: apiBaseUrl,
  authMode: authMode
});

// --- Base Configuration ---

const baseConfiguration = new Configuration({
  basePath: apiBaseUrl,
});

// --- Axios Instance ---

// Create an axios instance configured with the base URL
const axiosInstance = axios.create({
  baseURL: apiBaseUrl,
  timeout: 30000,
});

// Add request interceptor for comprehensive logging
axiosInstance.interceptors.request.use(
  (config) => {
    const requestId = Math.random().toString(36).substr(2, 9);
    const startTime = performance.now();
    const requestKey = `${config.method}_${config.url}_${Date.now()}`;

    // Store metadata in our Map
    requestMetadata.set(requestKey, { requestId, startTime });

    // Add request key to config for retrieval in response
    config.headers = config.headers || {};
    config.headers['X-Request-Key'] = requestKey;

    logger.info(LogCategory.API, `API Request initiated`, {
      method: config.method?.toUpperCase(),
      url: config.url,
      baseURL: config.baseURL,
      requestId: requestId,
      hasData: !!config.data,
      hasAuth: !!config.headers?.Authorization,
    });

    return config;
  },
  (error) => {
    logger.error(LogCategory.API, 'API Request setup failed', {}, error);
    return Promise.reject(error);
  }
);

// Add response interceptor for comprehensive logging
axiosInstance.interceptors.response.use(
  (response) => {
    const requestKey = response.config.headers?.['X-Request-Key'] as string;
    const metadata = requestKey ? requestMetadata.get(requestKey) : undefined;
    const { requestId, startTime } = metadata || {};
    const duration = startTime ? performance.now() - startTime : 0;

    // Clean up metadata
    if (requestKey) {
      requestMetadata.delete(requestKey);
    }

    logger.logApiCall(
      response.config.method?.toUpperCase() || 'GET',
      response.config.url || '',
      response.status,
      duration,
      undefined,
      requestId
    );

    return response;
  },
  (error) => {
    const requestKey = error.config?.headers?.['X-Request-Key'] as string;
    const metadata = requestKey ? requestMetadata.get(requestKey) : undefined;
    const { requestId, startTime } = metadata || {};
    const duration = startTime ? performance.now() - startTime : 0;

    // Clean up metadata
    if (requestKey) {
      requestMetadata.delete(requestKey);
    }

    logger.logApiCall(
      error.config?.method?.toUpperCase() || 'GET',
      error.config?.url || '',
      error.response?.status,
      duration,
      error.message,
      requestId
    );

    return Promise.reject(error);
  }
);

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
      logger.info(LogCategory.AUTH, 'Using MOCK registration endpoint', {
        email: userData.email
      });
      // Call mock endpoint directly using axiosInstance
      // The backend mock router expects { email: string, password: string }
      // We only need email and password for the mock call, even if more data is present
      const mockRegisterData = { email: userData.email, password: userData.password };
      return axiosInstance.post('/mock/register', mockRegisterData);
    } else {
      logger.warn(LogCategory.AUTH, 'Using REAL registration endpoint (Not Implemented Yet)');
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
    logger.info(LogCategory.AUTH, 'Attorney signup initiated', {
      email: formData.email,
      jurisdiction: formData.jurisdiction
    });

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
      logger.error(LogCategory.AUTH, 'Attorney registration failed', {
        email: formData.email
      }, error as Error);
      throw error;
    }
  },

  registerClient: async (formData: ClientRegistrationData) => {
    logger.info(LogCategory.AUTH, 'Client signup initiated', {
      firstName: formData.firstName,
      lastName: formData.lastName,
      countryOfBirth: formData.countryOfBirth
    });

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
      logger.error(LogCategory.AUTH, 'Client registration failed', {
        firstName: formData.firstName,
        lastName: formData.lastName
      }, error as Error);
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
    logger.info(LogCategory.AUTH, 'Unified signup initiated', {
      email: signupData.email,
      role: signupData.primary_role
    });

    const response = await axiosInstance.post('/signup/unified', {
      signup_data: signupData,
      role_data: roleData
    });

    logger.info(LogCategory.AUTH, 'Unified signup successful', {
      email: signupData.email,
      userId: response.data.user_id,
      role: response.data.primary_role
    });
    return response.data;
  } catch (error) {
    logger.error(LogCategory.AUTH, 'Unified signup failed', {
      email: signupData.email,
      role: signupData.primary_role
    }, error as Error);
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
      logger.warn(LogCategory.LOCATION, 'Location services are disabled');
      return null;
    }

    // Request permission if not already granted
    const hasPermission = await requestLocationPermission();
    if (!hasPermission) {
      logger.warn(LogCategory.LOCATION, 'Location permission denied by user');
      return null;
    }

    // Get current position with basic accuracy for speed
    const location = await Location.getCurrentPositionAsync({
      accuracy: Location.Accuracy.Balanced, // Faster than High, more accurate than Low
      timeInterval: 10000, // 10 second timeout
      distanceInterval: 0, // No distance filtering
    });

    if (!location) {
      logger.error(LogCategory.LOCATION, 'Failed to get location coordinates');
      return null;
    }

    return {
      latitude: location.coords.latitude,
      longitude: location.coords.longitude,
      description: `GPS: ${location.coords.latitude.toFixed(4)}, ${location.coords.longitude.toFixed(4)}`,
    };
  } catch (error) {
    logger.error(LogCategory.LOCATION, 'Failed to get current location', {}, error as Error);
    return null;
  }
};

// --- Attorney Case Management API Methods ---

/**
 * Get available emergency cases for an attorney
 */
export const getAvailableCases = async (
  attorneyId: number,
  courtId?: number
): Promise<AvailableCaseResponse[]> => {
  try {
    const url = courtId
      ? `/emergency/cases/available/${courtId}?attorney_id=${attorneyId}`
      : `/emergency/cases/unassigned?attorney_id=${attorneyId}`;

    const response = await axiosInstance.get(url);
    return response.data;
  } catch (error) {
    console.error('Failed to fetch available cases:', error);
    throw error;
  }
};

/**
 * Get detailed information about a specific case
 */
export const getCaseDetails = async (caseId: number): Promise<DetailedCaseResponse> => {
  try {
    // Note: This endpoint might need to be created on the backend
    // For now, we'll use the status endpoint and map the response
    const response = await axiosInstance.get(`/emergency/cases/${caseId}/status`);
    const status = response.data;

    // Map the status response to detailed case response format
    // Calculate urgency level based on creation time
    const createdAt = new Date(status.created_at || new Date());
    const hoursElapsed = (Date.now() - createdAt.getTime()) / (1000 * 60 * 60);

    let urgencyLevel: 'urgent' | 'high' | 'medium' | 'low';
    if (hoursElapsed < 1) urgencyLevel = 'urgent';
    else if (hoursElapsed < 6) urgencyLevel = 'high';
    else if (hoursElapsed < 24) urgencyLevel = 'medium';
    else urgencyLevel = 'low';

    const timeAgo = hoursElapsed < 1
      ? `${Math.round(hoursElapsed * 60)} minutes ago`
      : `${Math.round(hoursElapsed)} hours ago`;

    // This is a mock response structure - actual backend integration would need
    // the case details endpoint to be implemented
    return {
      case_id: status.case_id,
      case_type: 'self', // Would come from backend
      status: status.status,
      created_at: status.created_at || new Date().toISOString(),
      updated_at: status.last_updated,
      urgency_level: urgencyLevel,
      detention_location: {
        description: 'Detention facility details', // Would come from backend
      },
      court_info: {
        court_name: status.assigned_court_name || 'Unknown Court',
        court_abbreviation: 'TBD',
      },
      client_info: {
        first_name: 'Client', // Would come from backend
        last_name: 'Name',
        case_type: 'self',
      },
      time_since_created: timeAgo,
      attorneys_notified_count: 0, // Would come from backend
    };
  } catch (error) {
    console.error('Failed to fetch case details:', error);
    throw error;
  }
};

/**
 * Accept an emergency case as an attorney
 */
export const acceptCase = async (
  caseId: number,
  attorneyId: number,
  request: AttorneyCaseAcceptanceRequest
): Promise<AttorneyCaseAcceptanceResponse> => {
  try {
    const response = await axiosInstance.post(
      `/emergency/cases/${caseId}/accept?attorney_id=${attorneyId}`,
      request
    );
    return response.data;
  } catch (error) {
    console.error('Failed to accept case:', error);
    throw error;
  }
};

// --- Attorney Notification Preferences API Methods ---

/**
 * Get attorney notification preferences
 */
export const getAttorneyNotificationPreferences = async (
  attorneyId: number
): Promise<AttorneyNotificationPreferencesResponse> => {
  try {
    const response = await axiosInstance.get(`/emergency/attorneys/${attorneyId}/preferences`);
    return response.data;
  } catch (error) {
    console.error('Failed to fetch attorney notification preferences:', error);
    throw error;
  }
};

/**
 * Update attorney notification preferences
 */
export const updateAttorneyNotificationPreferences = async (
  attorneyId: number,
  preferences: AttorneyNotificationPreferencesRequest
): Promise<AttorneyNotificationPreferencesResponse> => {
  try {
    const response = await axiosInstance.put(
      `/emergency/attorneys/${attorneyId}/preferences`,
      preferences
    );
    return response.data;
  } catch (error) {
    console.error('Failed to update attorney notification preferences:', error);
    throw error;
  }
};

// --- Daily Digest API Methods ---

/**
 * Get daily digest of all unassigned cases across all courts
 */
export const getDailyDigest = async (): Promise<DailyDigestResponse> => {
  try {
    const response = await axiosInstance.get('/emergency/daily-digest');
    return response.data;
  } catch (error) {
    console.error('Failed to fetch daily digest:', error);
    throw error;
  }
};

/**
 * Get all unassigned cases without court coverage statistics
 */
export const getAllUnassignedCases = async (): Promise<AvailableCaseResponse[]> => {
  try {
    const response = await axiosInstance.get('/emergency/cases/unassigned');
    return response.data;
  } catch (error) {
    console.error('Failed to fetch unassigned cases:', error);
    throw error;
  }
};
