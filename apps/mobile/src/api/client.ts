import 'react-native-url-polyfill/auto';
import { AttorneysApi, AttorneyCreate, Configuration } from './generated';
import axios from 'axios';

// Create a configuration with the base path
const configuration = new Configuration({
  basePath: 'http://localhost:8000', // TODO: Replace with API base URL
});

// Create an axios instance (optional, you can customize further if needed)
const axiosInstance = axios.create();

// Create API client instances
const attorneysApi = new AttorneysApi(configuration, undefined, axiosInstance);

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
  }
};

export default api;

