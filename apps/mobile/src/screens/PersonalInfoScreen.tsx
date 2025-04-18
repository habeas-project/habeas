import React, { useState, useEffect } from 'react';
import { View, Text, StyleSheet, ScrollView, TextInput, TouchableOpacity, Platform, Alert } from 'react-native';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { SafeAreaView } from 'react-native-safe-area-context';
import CryptoJS from 'react-native-crypto-js';

const STORAGE_KEY = '@personal_info';
// IMPORTANT: In a real application, this key should be securely stored
// and not hardcoded in the source code
const ENCRYPTION_KEY = 'habeas-personal-data-encryption-key-2025';

// Encryption/decryption utility functions
const encryptData = (data: string): string => {
  return CryptoJS.AES.encrypt(data, ENCRYPTION_KEY).toString();
};

const decryptData = (encryptedData: string): string => {
  const bytes = CryptoJS.AES.decrypt(encryptedData, ENCRYPTION_KEY);
  return bytes.toString(CryptoJS.enc.Utf8);
};

interface EmergencyContact {
  id: string;
  name: string;
  phone: string;
  relationship: string;
}

interface PersonalInfo {
  firstName: string;
  lastName: string;
  countryOfBirth: string;
  nationality: string;
  birthDate: string;
  alienNumber: string;
  emergencyContacts: EmergencyContact[];
}

export default function PersonalInfoScreen({ navigation }: any) {
  const [personalInfo, setPersonalInfo] = useState<PersonalInfo>({
    firstName: '',
    lastName: '',
    countryOfBirth: '',
    nationality: '',
    birthDate: '',
    alienNumber: '',
    emergencyContacts: []
  });
  
  const [newContact, setNewContact] = useState({
    name: '',
    phone: '',
    relationship: ''
  });

  // Load personal info on initial mount
  useEffect(() => {
    loadPersonalInfo();
  }, []);
  
  // Save personal info whenever it changes with encryption
  useEffect(() => {
    const saveData = async () => {
      try {
        // Convert to JSON string first
        const jsonValue = JSON.stringify(personalInfo);
        
        // Encrypt the data before storing
        const encryptedData = encryptData(jsonValue);
        
        // Save encrypted data to storage
        await AsyncStorage.setItem(STORAGE_KEY, encryptedData);
      } catch (error) {
        console.error('Error saving data:', error);
      }
    };
    
    // Don't save on initial load when the state is empty
    if (personalInfo.firstName || 
        personalInfo.lastName || 
        personalInfo.countryOfBirth || 
        personalInfo.alienNumber || 
        personalInfo.emergencyContacts.length > 0) {
      saveData();
    }
  }, [personalInfo]);

  const loadPersonalInfo = async () => {
    try {
      const encryptedData = await AsyncStorage.getItem(STORAGE_KEY);
      
      if (encryptedData != null) {
        try {
          // Decrypt the data
          const jsonValue = decryptData(encryptedData);
          
          // Parse the JSON and update state
          setPersonalInfo(JSON.parse(jsonValue));
        } catch (decryptError) {
          console.error('Failed to decrypt data:', decryptError);
          Alert.alert('Error', 'Failed to decrypt personal information');
        }
      }
    } catch (error) {
      Alert.alert('Error', 'Failed to load personal information');
      console.error(error);
    }
  };

  const addEmergencyContact = () => {
    if (!newContact.name || !newContact.phone) {
      Alert.alert('Error', 'Name and phone are required for emergency contacts');
      return;
    }
    
    const updatedInfo = {
      ...personalInfo,
      emergencyContacts: [
        ...personalInfo.emergencyContacts,
        {
          id: Date.now().toString(),
          ...newContact
        }
      ]
    };
    
    setPersonalInfo(updatedInfo);
    setNewContact({ name: '', phone: '', relationship: '' });
  };

  const removeEmergencyContact = (id: string) => {
    const updatedContacts = personalInfo.emergencyContacts.filter(
      contact => contact.id !== id
    );
    
    setPersonalInfo({
      ...personalInfo,
      emergencyContacts: updatedContacts
    });
  };

  return (
    <SafeAreaView style={styles.container}>
      <ScrollView contentContainerStyle={styles.scrollContent}>
        <Text style={styles.title}>Personal Information</Text>
        <Text style={styles.description}>
          This information is stored locally on your device using AES-256 encryption and 
          is not sent to any server. Changes are automatically saved as you type.
        </Text>

        <View style={styles.formGroup}>
          <Text style={styles.label}>First Name *</Text>
          <TextInput
            style={styles.input}
            value={personalInfo.firstName}
            onChangeText={(text) => setPersonalInfo({...personalInfo, firstName: text})}
            placeholder="Enter your first name"
          />
        </View>

        <View style={styles.formGroup}>
          <Text style={styles.label}>Last Name *</Text>
          <TextInput
            style={styles.input}
            value={personalInfo.lastName}
            onChangeText={(text) => setPersonalInfo({...personalInfo, lastName: text})}
            placeholder="Enter your last name"
          />
        </View>

        <View style={styles.formGroup}>
          <Text style={styles.label}>Country of Birth *</Text>
          <TextInput
            style={styles.input}
            value={personalInfo.countryOfBirth}
            onChangeText={(text) => setPersonalInfo({...personalInfo, countryOfBirth: text})}
            placeholder="Enter your country of birth"
          />
        </View>

        <View style={styles.formGroup}>
          <Text style={styles.label}>Nationality (if different)</Text>
          <TextInput
            style={styles.input}
            value={personalInfo.nationality}
            onChangeText={(text) => setPersonalInfo({...personalInfo, nationality: text})}
            placeholder="Enter your nationality if different"
          />
        </View>

        <View style={styles.formGroup}>
          <Text style={styles.label}>Birth Date *</Text>
          <TextInput
            style={styles.input}
            value={personalInfo.birthDate}
            onChangeText={(text) => setPersonalInfo({...personalInfo, birthDate: text})}
            placeholder="YYYY-MM-DD"
          />
        </View>

        <View style={styles.formGroup}>
          <Text style={styles.label}>Alien Registration Number (A-Number)</Text>
          <TextInput
            style={styles.input}
            value={personalInfo.alienNumber}
            onChangeText={(text) => setPersonalInfo({...personalInfo, alienNumber: text})}
            placeholder="A-Number (if applicable)"
          />
        </View>

        <Text style={styles.sectionTitle}>Emergency Contacts</Text>
        
        {personalInfo.emergencyContacts.map((contact) => (
          <View key={contact.id} style={styles.contactCard}>
            <Text style={styles.contactName}>{contact.name}</Text>
            <Text style={styles.contactInfo}>{contact.phone}</Text>
            {contact.relationship && <Text style={styles.contactInfo}>Relationship: {contact.relationship}</Text>}
            <TouchableOpacity
              style={styles.removeButton}
              onPress={() => removeEmergencyContact(contact.id)}
            >
              <Text style={styles.removeButtonText}>Remove</Text>
            </TouchableOpacity>
          </View>
        ))}

        <View style={styles.addContactSection}>
          <Text style={styles.subSectionTitle}>Add Emergency Contact</Text>
          <View style={styles.formGroup}>
            <Text style={styles.label}>Name *</Text>
            <TextInput
              style={styles.input}
              value={newContact.name}
              onChangeText={(text) => setNewContact({...newContact, name: text})}
              placeholder="Contact name"
            />
          </View>
          <View style={styles.formGroup}>
            <Text style={styles.label}>Phone *</Text>
            <TextInput
              style={styles.input}
              value={newContact.phone}
              onChangeText={(text) => setNewContact({...newContact, phone: text})}
              placeholder="Contact phone"
            />
          </View>
          <View style={styles.formGroup}>
            <Text style={styles.label}>Relationship</Text>
            <TextInput
              style={styles.input}
              value={newContact.relationship}
              onChangeText={(text) => setNewContact({...newContact, relationship: text})}
              placeholder="Relationship to you"
            />
          </View>
          <TouchableOpacity
            style={styles.addButton}
            onPress={addEmergencyContact}
          >
            <Text style={styles.buttonText}>Add Contact</Text>
          </TouchableOpacity>
        </View>
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f8f8f8',
  },
  scrollContent: {
    padding: 20,
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    marginBottom: 10,
    textAlign: 'center',
  },
  description: {
    fontSize: 14,
    color: '#666',
    marginBottom: 20,
    textAlign: 'center',
  },
  formGroup: {
    marginBottom: 16,
  },
  label: {
    fontSize: 16,
    marginBottom: 6,
    fontWeight: '500',
  },
  input: {
    backgroundColor: '#fff',
    borderWidth: 1,
    borderColor: '#ddd',
    borderRadius: 4,
    padding: 12,
    fontSize: 16,
  },
  sectionTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    marginTop: 20,
    marginBottom: 10,
  },
  subSectionTitle: {
    fontSize: 18,
    fontWeight: '600',
    marginBottom: 10,
  },
  contactCard: {
    backgroundColor: '#fff',
    borderRadius: 8,
    padding: 16,
    marginBottom: 10,
    borderWidth: 1,
    borderColor: '#ddd',
  },
  contactName: {
    fontSize: 16,
    fontWeight: 'bold',
  },
  contactInfo: {
    fontSize: 14,
    color: '#444',
    marginTop: 4,
  },
  addContactSection: {
    backgroundColor: '#f0f0f0',
    borderRadius: 8,
    padding: 16,
    marginTop: 10,
    marginBottom: 20,
  },
  addButton: {
    backgroundColor: '#4a90e2',
    padding: 12,
    borderRadius: 4,
    alignItems: 'center',
    marginTop: 10,
    marginBottom: 20,
  },
  buttonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '600',
  },
  removeButton: {
    backgroundColor: '#dc3545',
    padding: 8,
    borderRadius: 4,
    alignItems: 'center',
    marginTop: 10,
    alignSelf: 'flex-start',
  },
  removeButtonText: {
    color: '#fff',
    fontSize: 12,
    fontWeight: '600',
  },
});