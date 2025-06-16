import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  TextInput,
  StyleSheet,
  TouchableOpacity,
  ScrollView,
  ActivityIndicator
} from 'react-native';
import api from '../api/client';
import { NativeStackNavigationProp } from '@react-navigation/native-stack';

type RootStackParamList = {
  Home: undefined;
  PersonalInfo: undefined;
  AttorneySignup: undefined;
};

type AttorneySignupScreenProps = {
  navigation: NativeStackNavigationProp<RootStackParamList, 'AttorneySignup'>;
};

type SignupFormData = {
  name: string;
  phoneNumber: string;
  email: string;
  zipCode: string;
  jurisdiction: string;
  password: string;
};

export default function AttorneySignupScreen({ navigation }: AttorneySignupScreenProps) {
  const [formData, setFormData] = useState<SignupFormData>({
    name: '',
    phoneNumber: '',
    email: '',
    zipCode: '',
    jurisdiction: '',
    password: '',
  });

  const [errors, setErrors] = useState<Partial<SignupFormData>>({});
  const [loading, setLoading] = useState(false);
  const [isFormValid, setIsFormValid] = useState(false);
  const [touchedFields, setTouchedFields] = useState<Record<string, boolean>>({});

  // Validate form whenever input changes
  useEffect(() => {
    validateForm();
  }, [formData]);

  const validateForm = (): boolean => {
    const newErrors: Partial<SignupFormData> = {};

    if (!formData.name.trim()) newErrors.name = 'Name is required';

    // E.164 format: + followed by 1-15 digits
    const phoneRegex = /^\+[1-9]\d{1,14}$/;
    if (!formData.phoneNumber.trim() || !phoneRegex.test(formData.phoneNumber)) {
      newErrors.phoneNumber = 'Phone number must be in E.164 format (e.g., +12025551234)';
    }

    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!formData.email.trim() || !emailRegex.test(formData.email)) {
      newErrors.email = 'Valid email is required';
    }

    const zipRegex = /^\d{5}(?:[-\s]\d{4})?$/;
    if (!formData.zipCode.trim() || !zipRegex.test(formData.zipCode)) {
      newErrors.zipCode = 'Valid ZIP code is required';
    }

    if (!formData.jurisdiction.trim()) newErrors.jurisdiction = 'Jurisdiction is required';

    if (!formData.password.trim()) {
      newErrors.password = 'Password is required';
    } else if (formData.password.length < 8) {
      newErrors.password = 'Password must be at least 8 characters long';
    }

    setErrors(newErrors);
    const valid = Object.keys(newErrors).length === 0;
    setIsFormValid(valid);
    return valid;
  };

  const handleSignup = async () => {
    // Mark all fields as touched when attempting to submit
    const allTouched = Object.keys(formData).reduce((acc, key) => {
      acc[key] = true;
      return acc;
    }, {} as Record<string, boolean>);
    setTouchedFields(allTouched);

    if (!validateForm()) return;

    try {
      setLoading(true);
      const response = await api.registerAttorney(formData);

      console.log('Attorney registration successful:', response);
      alert('Signup successful! Your attorney account has been created.');
      // Navigate back or to a confirmation screen
      navigation.navigate('Home');
    } catch (error: unknown) {
      console.error('Error during attorney signup:', error);

      // Handle different types of errors
      let errorMessage = 'Failed to submit. Please try again later.';

      // Type guard for axios-like error objects
      const hasResponse = error && typeof error === 'object' && 'response' in error;
      const hasRequest = error && typeof error === 'object' && 'request' in error;

      if (hasResponse) {
        // Server responded with an error status
        const response = (error as { response: { status: number; data?: { detail?: string } } }).response;
        const status = response.status;
        const detail = response.data?.detail;

        if (status === 400 && detail) {
          if (detail.includes('email already exists')) {
            errorMessage = 'An account with this email already exists. Please use a different email or try logging in.';
          } else {
            errorMessage = detail;
          }
        } else if (status === 422) {
          errorMessage = 'Please check your information and ensure all fields are filled correctly.';
        } else if (status >= 500) {
          errorMessage = 'Server error. Please try again later.';
        }
      } else if (hasRequest) {
        // Network error
        errorMessage = 'Network error. Please check your connection and try again.';
      }

      alert(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  return (
    <ScrollView contentContainerStyle={styles.container}>
      <Text style={styles.title}>Attorney Registration</Text>
      <Text style={styles.description}>
        Join our network to provide legal assistance
      </Text>

      <View style={styles.formContainer}>
        <View style={styles.inputGroup}>
          <Text style={styles.label}>Full Name</Text>
          <TextInput
            style={styles.input}
            value={formData.name}
            onChangeText={(text) => setFormData({ ...formData, name: text })}
            onBlur={() => setTouchedFields({ ...touchedFields, name: true })}
            placeholder="Enter your full name"
          />
          {touchedFields.name && errors.name && <Text style={styles.errorText}>{errors.name}</Text>}
        </View>

        <View style={styles.inputGroup}>
          <Text style={styles.label}>Phone Number</Text>
          <TextInput
            style={styles.input}
            value={formData.phoneNumber}
            onChangeText={(text) => setFormData({ ...formData, phoneNumber: text })}
            onBlur={() => setTouchedFields({ ...touchedFields, phoneNumber: true })}
            placeholder="Enter your phone number (e.g., +12025551234)"
            keyboardType="phone-pad"
          />
          {touchedFields.phoneNumber && errors.phoneNumber && <Text style={styles.errorText}>{errors.phoneNumber}</Text>}
        </View>

        <View style={styles.inputGroup}>
          <Text style={styles.label}>Email Address</Text>
          <TextInput
            style={styles.input}
            value={formData.email}
            onChangeText={(text) => setFormData({ ...formData, email: text })}
            onBlur={() => setTouchedFields({ ...touchedFields, email: true })}
            placeholder="Enter your email address"
            keyboardType="email-address"
            autoCapitalize="none"
          />
          {touchedFields.email && errors.email && <Text style={styles.errorText}>{errors.email}</Text>}
        </View>

        <View style={styles.inputGroup}>
          <Text style={styles.label}>Location (ZIP Code)</Text>
          <TextInput
            style={styles.input}
            value={formData.zipCode}
            onChangeText={(text) => setFormData({ ...formData, zipCode: text })}
            onBlur={() => setTouchedFields({ ...touchedFields, zipCode: true })}
            placeholder="Enter your ZIP code"
            keyboardType="numeric"
          />
          {touchedFields.zipCode && errors.zipCode && <Text style={styles.errorText}>{errors.zipCode}</Text>}
        </View>

        <View style={styles.inputGroup}>
          <Text style={styles.label}>Jurisdiction</Text>
          <TextInput
            style={styles.input}
            value={formData.jurisdiction}
            onChangeText={(text) => setFormData({ ...formData, jurisdiction: text })}
            onBlur={() => setTouchedFields({ ...touchedFields, jurisdiction: true })}
            placeholder="Enter your jurisdiction (e.g., CA, NY)"
            autoCapitalize="characters"
            maxLength={2}
          />
          {touchedFields.jurisdiction && errors.jurisdiction && <Text style={styles.errorText}>{errors.jurisdiction}</Text>}
        </View>

        <View style={styles.inputGroup}>
          <Text style={styles.label}>Password</Text>
          <TextInput
            style={styles.input}
            value={formData.password}
            onChangeText={(text) => setFormData({ ...formData, password: text })}
            onBlur={() => setTouchedFields({ ...touchedFields, password: true })}
            placeholder="Enter your password (minimum 8 characters)"
            secureTextEntry={true}
            autoCapitalize="none"
          />
          {touchedFields.password && errors.password && <Text style={styles.errorText}>{errors.password}</Text>}
        </View>

        <TouchableOpacity
          style={[styles.button, (!isFormValid || loading) && styles.buttonDisabled]}
          onPress={handleSignup}
          disabled={!isFormValid || loading}
        >
          {loading ? (
            <ActivityIndicator size="small" color="#fff" />
          ) : (
            <Text style={styles.buttonText}>Submit Registration</Text>
          )}
        </TouchableOpacity>
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  button: {
    alignItems: 'center',
    backgroundColor: '#4a90e2',
    borderRadius: 5,
    height: 50,
    justifyContent: 'center',
    marginTop: 10,
  },
  buttonDisabled: {
    backgroundColor: '#a0c3e8', // lighter blue color
    opacity: 0.7,
  },
  buttonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '600',
  },
  container: {
    flexGrow: 1,
    padding: 20,
  },
  description: {
    color: '#555',
    fontSize: 16,
    marginBottom: 30,
    textAlign: 'center',
  },
  errorText: {
    color: 'red',
    fontSize: 14,
    marginTop: 5,
  },
  formContainer: {
    backgroundColor: '#f9f9f9',
    borderRadius: 10,
    marginBottom: 20,
    padding: 20,
  },
  input: {
    backgroundColor: '#fff',
    borderColor: '#ddd',
    borderRadius: 5,
    borderWidth: 1,
    fontSize: 16,
    height: 50,
    paddingHorizontal: 15,
  },
  inputGroup: {
    marginBottom: 20,
  },
  label: {
    color: '#333',
    fontSize: 16,
    fontWeight: '500',
    marginBottom: 8,
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    marginBottom: 16,
    marginTop: 40,
    textAlign: 'center',
  },
});
