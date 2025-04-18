import { Alert, Vibration } from 'react-native';
import { SecureStorage } from './secureStorage';

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
      // Get personal info to check for contacts
      const personalInfoKey = '@personal_info';
      const personalInfo = await SecureStorage.loadData<any>(personalInfoKey);
      
      // Update emergency state
      const newState: EmergencyState = {
        activated: true,
        activatedAt: new Date().toISOString(),
        emergencyType: emergencyType,
        sentNotifications: false
      };
      
      await SecureStorage.saveData(EMERGENCY_STATE_KEY, newState);
      
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