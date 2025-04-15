import axios from 'axios';

// Base URL for the API
// In a real app, you would use environment variables or config based on the build environment
const API_URL = 'http://localhost:8000';

// Create a configured axios instance
const apiClient = axios.create({
    baseURL: API_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

// Example API functions
const api = {
    // Examples
    getExamples: async () => {
        const response = await apiClient.get('/examples');
        return response.data;
    },

    getExampleById: async (id: number) => {
        const response = await apiClient.get(`/examples/${id}`);
        return response.data;
    },

    createExample: async (data: { name: string; description?: string }) => {
        const response = await apiClient.post('/examples', data);
        return response.data;
    },

        // Attorney registration
    registerAttorney: async (data: { 
        name: string; 
        phoneNumber: string;
        email: string;
        zipCode: string;
        jurisdiction: string;
    }) => {
        const response = await apiClient.post('/attorneys/register', data);
        return response.data;
    },

    // Add more API functions as needed
};

export default api; 