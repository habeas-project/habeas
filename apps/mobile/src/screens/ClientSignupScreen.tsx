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
    ClientSignup: undefined;
};

type ClientSignupScreenProps = {
    navigation: NativeStackNavigationProp<RootStackParamList, 'ClientSignup'>;
};

type ClientFormData = {
    firstName: string;
    lastName: string;
    countryOfBirth: string;
    birthDate: string;
    password: string;
    // Optional fields
    nationality: string;
    alienRegistrationNumber: string;
    passportNumber: string;
    schoolName: string;
    studentIdNumber: string;
};

export default function ClientSignupScreen({ navigation }: ClientSignupScreenProps) {
    const [formData, setFormData] = useState<ClientFormData>({
        firstName: '',
        lastName: '',
        countryOfBirth: '',
        birthDate: '',
        password: '',
        nationality: '',
        alienRegistrationNumber: '',
        passportNumber: '',
        schoolName: '',
        studentIdNumber: '',
    });

    const [errors, setErrors] = useState<Partial<ClientFormData>>({});
    const [loading, setLoading] = useState(false);
    const [isFormValid, setIsFormValid] = useState(false);
    const [touchedFields, setTouchedFields] = useState<Record<string, boolean>>({});

    // Validate form whenever input changes
    useEffect(() => {
        validateForm();
    }, [formData]);

    const validateForm = (): boolean => {
        const newErrors: Partial<ClientFormData> = {};

        // Required fields validation
        if (!formData.firstName.trim()) newErrors.firstName = 'First name is required';
        if (!formData.lastName.trim()) newErrors.lastName = 'Last name is required';
        if (!formData.countryOfBirth.trim()) newErrors.countryOfBirth = 'Country of birth is required';

        // Birth date validation (YYYY-MM-DD format)
        const dateRegex = /^\d{4}-\d{2}-\d{2}$/;
        if (!formData.birthDate.trim()) {
            newErrors.birthDate = 'Birth date is required';
        } else if (!dateRegex.test(formData.birthDate)) {
            newErrors.birthDate = 'Birth date must be in YYYY-MM-DD format';
        } else {
            // Additional validation for reasonable birth date
            const birthYear = parseInt(formData.birthDate.split('-')[0]);
            const currentYear = new Date().getFullYear();
            if (birthYear < 1900 || birthYear > currentYear - 13) {
                newErrors.birthDate = 'Please enter a valid birth date';
            }
        }

        // Password validation
        if (!formData.password.trim()) {
            newErrors.password = 'Password is required';
        } else if (formData.password.length < 8) {
            newErrors.password = 'Password must be at least 8 characters long';
        }

        // Optional field format validation (only if provided)
        if (formData.alienRegistrationNumber.trim() && !/^A\d{8,9}$/.test(formData.alienRegistrationNumber)) {
            newErrors.alienRegistrationNumber = 'A-Number must be in format A12345678 or A123456789';
        }

        setErrors(newErrors);
        const valid = Object.keys(newErrors).length === 0;
        setIsFormValid(valid);
        return valid;
    };

    const handleSignup = async () => {
        // Mark all required fields as touched when attempting to submit
        const requiredFields = ['firstName', 'lastName', 'countryOfBirth', 'birthDate', 'password'];
        const touchedRequired = requiredFields.reduce((acc, key) => {
            acc[key] = true;
            return acc;
        }, {} as Record<string, boolean>);
        setTouchedFields({ ...touchedFields, ...touchedRequired });

        if (!validateForm()) return;

        try {
            setLoading(true);

            // Prepare data for API call, filtering out empty optional fields
            const clientData = {
                firstName: formData.firstName,
                lastName: formData.lastName,
                countryOfBirth: formData.countryOfBirth,
                birthDate: formData.birthDate,
                password: formData.password,
                // Only include optional fields if they have values
                ...(formData.nationality.trim() && { nationality: formData.nationality }),
                ...(formData.alienRegistrationNumber.trim() && { alienRegistrationNumber: formData.alienRegistrationNumber }),
                ...(formData.passportNumber.trim() && { passportNumber: formData.passportNumber }),
                ...(formData.schoolName.trim() && { schoolName: formData.schoolName }),
                ...(formData.studentIdNumber.trim() && { studentIdNumber: formData.studentIdNumber }),
            };

            const response = await api.registerClient(clientData);

            console.log('Client registration successful:', response);
            alert('Signup successful! Your client account has been created.');
            navigation.navigate('Home');
        } catch (error: unknown) {
            console.error('Error during client signup:', error);

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
                    if (detail.includes('already exists')) {
                        errorMessage = 'A client with this information already exists. Please check your details or contact support.';
                    } else {
                        errorMessage = detail;
                    }
                } else if (status === 422) {
                    errorMessage = 'Please check your information and ensure all required fields are filled correctly.';
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
            <Text style={styles.title}>Client Registration</Text>
            <Text style={styles.description}>
                Register to receive legal assistance
            </Text>

            <View style={styles.formContainer}>
                {/* Required Fields Section */}
                <Text style={styles.sectionTitle}>Required Information</Text>

                <View style={styles.inputGroup}>
                    <Text style={styles.label}>First Name</Text>
                    <TextInput
                        style={styles.input}
                        value={formData.firstName}
                        onChangeText={(text) => setFormData({ ...formData, firstName: text })}
                        onBlur={() => setTouchedFields({ ...touchedFields, firstName: true })}
                        placeholder="Enter your first name"
                    />
                    {touchedFields.firstName && errors.firstName && <Text style={styles.errorText}>{errors.firstName}</Text>}
                </View>

                <View style={styles.inputGroup}>
                    <Text style={styles.label}>Last Name</Text>
                    <TextInput
                        style={styles.input}
                        value={formData.lastName}
                        onChangeText={(text) => setFormData({ ...formData, lastName: text })}
                        onBlur={() => setTouchedFields({ ...touchedFields, lastName: true })}
                        placeholder="Enter your last name"
                    />
                    {touchedFields.lastName && errors.lastName && <Text style={styles.errorText}>{errors.lastName}</Text>}
                </View>

                <View style={styles.inputGroup}>
                    <Text style={styles.label}>Country of Birth</Text>
                    <TextInput
                        style={styles.input}
                        value={formData.countryOfBirth}
                        onChangeText={(text) => setFormData({ ...formData, countryOfBirth: text })}
                        onBlur={() => setTouchedFields({ ...touchedFields, countryOfBirth: true })}
                        placeholder="Enter your country of birth"
                    />
                    {touchedFields.countryOfBirth && errors.countryOfBirth && <Text style={styles.errorText}>{errors.countryOfBirth}</Text>}
                </View>

                <View style={styles.inputGroup}>
                    <Text style={styles.label}>Birth Date</Text>
                    <TextInput
                        style={styles.input}
                        value={formData.birthDate}
                        onChangeText={(text) => setFormData({ ...formData, birthDate: text })}
                        onBlur={() => setTouchedFields({ ...touchedFields, birthDate: true })}
                        placeholder="YYYY-MM-DD (e.g., 1990-01-15)"
                        keyboardType="numeric"
                    />
                    {touchedFields.birthDate && errors.birthDate && <Text style={styles.errorText}>{errors.birthDate}</Text>}
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

                {/* Optional Fields Section */}
                <Text style={styles.sectionTitle}>Additional Information (Optional)</Text>

                <View style={styles.inputGroup}>
                    <Text style={styles.label}>Nationality</Text>
                    <TextInput
                        style={styles.input}
                        value={formData.nationality}
                        onChangeText={(text) => setFormData({ ...formData, nationality: text })}
                        placeholder="Enter your nationality"
                    />
                </View>

                <View style={styles.inputGroup}>
                    <Text style={styles.label}>Alien Registration Number (A-Number)</Text>
                    <TextInput
                        style={styles.input}
                        value={formData.alienRegistrationNumber}
                        onChangeText={(text) => setFormData({ ...formData, alienRegistrationNumber: text })}
                        onBlur={() => setTouchedFields({ ...touchedFields, alienRegistrationNumber: true })}
                        placeholder="A12345678"
                        autoCapitalize="characters"
                    />
                    {touchedFields.alienRegistrationNumber && errors.alienRegistrationNumber &&
                        <Text style={styles.errorText}>{errors.alienRegistrationNumber}</Text>}
                </View>

                <View style={styles.inputGroup}>
                    <Text style={styles.label}>Passport Number</Text>
                    <TextInput
                        style={styles.input}
                        value={formData.passportNumber}
                        onChangeText={(text) => setFormData({ ...formData, passportNumber: text })}
                        placeholder="Enter your passport number"
                        autoCapitalize="characters"
                    />
                </View>

                <View style={styles.inputGroup}>
                    <Text style={styles.label}>School Name</Text>
                    <TextInput
                        style={styles.input}
                        value={formData.schoolName}
                        onChangeText={(text) => setFormData({ ...formData, schoolName: text })}
                        placeholder="Enter your school name"
                    />
                </View>

                <View style={styles.inputGroup}>
                    <Text style={styles.label}>Student ID Number</Text>
                    <TextInput
                        style={styles.input}
                        value={formData.studentIdNumber}
                        onChangeText={(text) => setFormData({ ...formData, studentIdNumber: text })}
                        placeholder="Enter your student ID"
                    />
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
        backgroundColor: '#28a745',
        borderRadius: 5,
        height: 50,
        justifyContent: 'center',
        marginTop: 20,
    },
    buttonDisabled: {
        backgroundColor: '#8cc8a5', // lighter green color
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
    sectionTitle: {
        color: '#333',
        fontSize: 18,
        fontWeight: 'bold',
        marginBottom: 15,
        marginTop: 10,
    },
    title: {
        fontSize: 24,
        fontWeight: 'bold',
        marginBottom: 16,
        marginTop: 40,
        textAlign: 'center',
    },
});
