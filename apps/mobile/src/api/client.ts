import 'react-native-url-polyfill/auto';
import {
  AttorneysApi,
  AttorneyCreate,
  ClientsApi,
  ClientCreate,
  EmergencyContactsApi,
  EmergencyContactCreate,
  Configuration
} from './generated';
import axios from 'axios';

// Create a configuration with the base path
const configuration = new Configuration({
  basePath: 'http://localhost:8000', // TODO: Replace with API base URL
});

// Create an axios instance (optional, you can customize further if needed)
const axiosInstance = axios.create();

// Create API client instances
const attorneysApi = new AttorneysApi(configuration, undefined, axiosInstance);
const clientsApi = new ClientsApi(configuration, undefined, axiosInstance);
const emergencyContactsApi = new EmergencyContactsApi(configuration, undefined, axiosInstance);

// Main API client with methods that match the application's needs
const api = {
  registerAttorney: async (formData: {
    name: string;
    phoneNumber: string;
    email: string;
    zipCode: string;
    jurisdiction: string;
  }) => {
    // Convert from the application's form data format to the API's expected format
    const attorneyData: AttorneyCreate = {
      name: formData.name,
      phone_number: formData.phoneNumber,
      email: formData.email,
      zip_code: formData.zipCode,
      state: formData.jurisdiction, // Mapping jurisdiction to state field
    };

    // Call the generated API method
    return attorneysApi.createAttorneyAttorneysPost(attorneyData);
  },

  // Send emergency client information to the server
  submitEmergencyClientInfo: async (clientInfo: {
    firstName: string;
    lastName: string;
    countryOfBirth: string;
    nationality?: string;
    birthDate: string;
    alienNumber?: string;
    emergencyContacts?: Array<{
      name: string;
      phone: string;
      relationship?: string;
    }>;
  }) => {
    try {
      // First create the client
      const clientData: ClientCreate = {
        first_name: clientInfo.firstName,
        last_name: clientInfo.lastName,
        country_of_birth: clientInfo.countryOfBirth,
        nationality: clientInfo.nationality || clientInfo.countryOfBirth,
        birth_date: clientInfo.birthDate,
        alien_registration_number: clientInfo.alienNumber,
      };

      const clientResponse = await clientsApi.createClientClientsPost(clientData);
      const clientId = clientResponse.data.id;

      // If we have emergency contacts, submit them
      if (clientInfo.emergencyContacts && clientInfo.emergencyContacts.length > 0) {
        const contactPromises = clientInfo.emergencyContacts.map(contact => {
          const contactData: EmergencyContactCreate = {
            client_id: clientId,
            full_name: contact.name,
            phone_number: contact.phone,
            relationship_to_client: contact.relationship || '',
          };

          return emergencyContactsApi.createEmergencyContactEmergencyContactsPost(contactData);
        });

        await Promise.all(contactPromises);
      }

      return { success: true, clientId };
    } catch (error) {
      console.error('Error submitting emergency client info:', error);
      throw error;
    }
  }
};

export default api;