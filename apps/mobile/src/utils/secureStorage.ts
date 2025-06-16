import 'react-native-get-random-values';
import AsyncStorage from '@react-native-async-storage/async-storage';
import CryptoJS from 'react-native-crypto-js';
import * as SecureStore from 'expo-secure-store';
import { v4 as uuidv4 } from 'uuid';

const ENCRYPTION_KEY_ID = 'habeas-personal-encryption-key-id';

/**
 * Utility class for securely storing data with encryption
 */
export class SecureStorage {

  /**
    * Generates a random encryption key
    * @returns A random string to use as encryption key
    */
  private static generateEncryptionKey(): string {
    // Generate a key based on UUID
    return uuidv4().replace(/-/g, '') + uuidv4().replace(/-/g, '');
  }

  /**
 * Gets the encryption key, generating and storing one if needed
 * @returns The encryption key
 */
  private static getEncryptionKey(): string {
    try {
      // Try to retrieve existing key
      const key = SecureStore.getItem(ENCRYPTION_KEY_ID);
      if (key) {
        return key;
      } else {

        const newKey = this.generateEncryptionKey();
        // await RNSecureKeyStore.set(ENCRYPTION_KEY_ID, newKey, { accessible: ACCESSIBLE.ALWAYS_THIS_DEVICE_ONLY });
        SecureStore.setItem(ENCRYPTION_KEY_ID, newKey);
        return newKey;

      }
    } catch {

      // Key doesn't exist, generate and store a new one
      const newKey = this.generateEncryptionKey();
      // await RNSecureKeyStore.set(ENCRYPTION_KEY_ID, newKey, { accessible: ACCESSIBLE.ALWAYS_THIS_DEVICE_ONLY });
      SecureStore.setItem(ENCRYPTION_KEY_ID, newKey);
      return newKey;
    }
  }

  /**
   * Encrypts data using AES-256
   * @param data - String data to encrypt
   * @returns Encrypted string
   */
  private static encrypt(data: string): string {
    const key = this.getEncryptionKey();
    const et = CryptoJS.AES.encrypt(data, key).toString();
    return et;
  }

  /**
   * Decrypts AES-256 encrypted data
   * @param encryptedData - Encrypted string
   * @returns Decrypted string
   */
  private static decrypt(encryptedData: string): string {
    const key = this.getEncryptionKey();
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
      const encryptedData = this.encrypt(jsonValue);
      // Save encrypted data to storage
      return AsyncStorage.setItem(key, encryptedData);
    } catch (error) {
      console.error(`Error saving data for key ${key}:`, error);
      // throw error;
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
      // throw error;
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
