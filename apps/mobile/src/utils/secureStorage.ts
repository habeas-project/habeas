import AsyncStorage from '@react-native-async-storage/async-storage';
import CryptoJS from 'react-native-crypto-js';
import RNSecureKeyStore from 'react-native-secure-key-store';
import 'react-native-get-random-values'; // Import for crypto.getRandomValues polyfill

const ENCRYPTION_KEY_ID = 'habeas-encryption-key';

/**
 * Utility class for securely storing data with encryption
 */
export class SecureStorage {
  /**
   * Generates a random encryption key
   * @returns A random string to use as encryption key
   */
  private static generateEncryptionKey(): string {
    // Generate a random 32-byte (256-bit) key
    const array = new Uint8Array(32);
    crypto.getRandomValues(array);
    return Array.from(array, byte => byte.toString(16).padStart(2, '0')).join('');
  }

  /**
   * Gets the encryption key, generating and storing one if needed
   * @returns The encryption key
   */
  private static async getEncryptionKey(): Promise<string> {
    try {
      // Try to retrieve existing key
      const key = await RNSecureKeyStore.get(ENCRYPTION_KEY_ID);
      return key;
    } catch (error) {
      // Key doesn't exist, generate and store a new one
      const newKey = this.generateEncryptionKey();
      await RNSecureKeyStore.set(ENCRYPTION_KEY_ID, newKey);
      return newKey;
    }
  }

  /**
   * Encrypts data using AES-256
   * @param data - String data to encrypt
   * @returns Encrypted string
   */
  private static async encrypt(data: string): Promise<string> {
    const key = await this.getEncryptionKey();
    return CryptoJS.AES.encrypt(data, key).toString();
  }

  /**
   * Decrypts AES-256 encrypted data
   * @param encryptedData - Encrypted string
   * @returns Decrypted string
   */
  private static async decrypt(encryptedData: string): Promise<string> {
    const key = await this.getEncryptionKey();
    const bytes = CryptoJS.AES.decrypt(encryptedData, key);
    return bytes.toString(CryptoJS.enc.Utf8);
  }

  /**
   * Stores data securely with encryption
   * @param key - Storage key
   * @param data - Data to store (will be stringified)
   */
  public static async saveData<T>(key: string, data: T): Promise<void> {
    try {
      // Convert to JSON string first
      const jsonValue = JSON.stringify(data);

      // Encrypt the data
      const encryptedData = await this.encrypt(jsonValue);

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
        const jsonValue = await this.decrypt(encryptedData);

        // Parse the JSON and return
        return JSON.parse(jsonValue) as T;
      } else {
        // No data found for the key
        console.warn(`No data found for key ${key}`);
        return null;
      }
    } catch (error) {
      console.error(`Error loading data for key ${key}:`, error);
      return null;
      // throw error;
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