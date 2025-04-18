import { Alert, Vibration } from 'react-native';
import { SecureStorage } from './secureStorage';
import api from '../api/client';

const EMERGENCY_STATE_KEY = '@emergency_state';

interface EmergencyState {
  activated: boolean;
  activatedAt: string | null;
  emergencyType: string | null;
  sentNotifications: boolean;
}

export class EmergencyHandler {

  /**
   * Get the current emergency state
   */
  public static async getEmergencyState(): Promise<EmergencyState> {
    try {
      const state = await SecureStorage.loadData<EmergencyState>(EMERGENCY_STATE_KEY);
      return state || {
        activated: false,
        activatedAt: null,
        emergencyType: null,
        sentNotifications: false
      };
    } catch (error) {
      console.error('Failed to get emergency state:', error);
      return {
        activated: false,
        activatedAt: null,
        emergencyType: null,
        sentNotifications: false
      };
    }
  }

  /**
   * Activate emergency mode
   */
  public static async activateEmergency(emergencyType: string = 'general'): Promise<void> {
    try {
      // Get personal info from secure storage
      const personalInfoKey = '@personal_info';
      const personalInfo = await SecureStorage.loadData<any>(personalInfoKey);
      
      // Update emergency state
      const newState: EmergencyState = {
        activated: true,
        activatedAt: new Date().toISOString(),
        emergencyType: emergencyType,
        sentNotifications: false
      };
      
      // Save the emergency state
      await SecureStorage.saveData(EMERGENCY_STATE_KEY, newState);
      
      // If we have personal info, send it to the server
      if (personalInfo) {
        try {
          // Send the personal information to the server using the API client
          await api.submitEmergencyClientInfo({
            firstName: personalInfo.firstName || '',
            lastName: personalInfo.lastName || '',
            countryOfBirth: personalInfo.countryOfBirth || '',
            nationality: personalInfo.nationality || '',
            birthDate: personalInfo.birthDate || '',
            alienNumber: personalInfo.alienNumber || '',
            emergencyContacts: personalInfo.emergencyContacts || []
          });
          
          console.log('Successfully sent emergency information to server');
        } catch (apiError) {
          // If server submission fails, just log it - we'll still activate emergency mode locally
          console.error('Failed to submit emergency info to server:', apiError);
        }
      } else {
        console.warn('No personal information found to send to server');
      }

      // Visual & haptic feedback
      Vibration.vibrate([500, 200, 500, 200, 500]);

    } catch (error) {
      console.error('Failed to activate emergency:', error);
    }
  }

  /**
   * Deactivate emergency mode
   */
  public static async deactivateEmergency(): Promise<void> {
    try {
      const newState: EmergencyState = {
        activated: false,
        activatedAt: null,
        emergencyType: null,
        sentNotifications: false
      };

      await SecureStorage.saveData(EMERGENCY_STATE_KEY, newState);

      // Add a small vibration to confirm deactivation
      Vibration.vibrate(100);

    } catch (error) {
      console.error('Failed to deactivate emergency:', error);
    }
  }
}