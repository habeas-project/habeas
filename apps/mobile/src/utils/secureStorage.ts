import AsyncStorage from '@react-native-async-storage/async-storage';
import CryptoJS from 'react-native-crypto-js';

// TODO: this key should be securely stored
// and not hardcoded in the source code
const ENCRYPTION_KEY = 'habeas-personal-data-encryption-key-2025';

/**
 * Utility class for securely storing data with encryption
 */
export class SecureStorage {
  /**
   * Encrypts data using AES-256
   * @param data - String data to encrypt
   * @returns Encrypted string
   */
  private static encrypt(data: string): string {
    return CryptoJS.AES.encrypt(data, ENCRYPTION_KEY).toString();
  }

  /**
   * Decrypts AES-256 encrypted data
   * @param encryptedData - Encrypted string
   * @returns Decrypted string
   */
  private static decrypt(encryptedData: string): string {
    const bytes = CryptoJS.AES.decrypt(encryptedData, ENCRYPTION_KEY);
    return bytes.toString(CryptoJS.enc.Utf8);
  }

  /**
   * Stores data securely with encryption
   * @param key - Storage key
   * @param data - Data to store (will be stringified)
   */
  public static async saveData(key: string, data: any): Promise<void> {
    try {
      // Convert to JSON string first
      const jsonValue = JSON.stringify(data);

      // Encrypt the data
      const encryptedData = this.encrypt(jsonValue);

      // Save encrypted data to storage
      await AsyncStorage.setItem(key, encryptedData);
    } catch (error) {
      console.error(`Error saving data for key ${key}:`, error);
      throw error;
    }
  }

  /**
   * Retrieves and decrypts data
   * @param key - Storage key
   * @returns Parsed data object or null if no data exists
   */
  public static async loadData<T>(key: string): Promise<T | null> {
    try {
      const encryptedData = await AsyncStorage.getItem(key);

      if (encryptedData != null) {
        // Decrypt the data
        const jsonValue = this.decrypt(encryptedData);

        // Parse the JSON and return
        return JSON.parse(jsonValue) as T;
      }
      return null;
    } catch (error) {
      console.error(`Error loading data for key ${key}:`, error);
      throw error;
    }
  }

  /**
   * Removes data for a given key
   * @param key - Storage key
   */
  public static async removeData(key: string): Promise<void> {
    try {
      await AsyncStorage.removeItem(key);
    } catch (error) {
      console.error(`Error removing data for key ${key}:`, error);
      throw error;
    }
  }

  /**
   * Checks if data exists for a given key
   * @param key - Storage key
   * @returns Boolean indicating if data exists
   */
  public static async hasData(key: string): Promise<boolean> {
    try {
      const value = await AsyncStorage.getItem(key);
      return value !== null;
    } catch (error) {
      console.error(`Error checking data for key ${key}:`, error);
      throw error;
    }
  }
}