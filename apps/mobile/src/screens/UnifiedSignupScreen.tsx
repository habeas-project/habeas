import React, { useState } from 'react';
import {
    View,
    Text,
    TextInput,
    TouchableOpacity,
    StyleSheet,
    ScrollView,
    Alert,
    KeyboardAvoidingView,
    Platform,
} from 'react-native';
import { NativeStackNavigationProp } from '@react-navigation/native-stack';
import { RouteProp } from '@react-navigation/native';
import { RootStackParamList } from '../App';
import {
    registerUnified,
    UnifiedSignupData,
    RoleSpecificData,
    ClientProfileData,
} from '../api/client';

// Import the interface directly from the client file
interface AttorneyRegistrationData {
    name: string;
    phoneNumber: string;
    email: string;
    zipCode: string;
    jurisdiction: string;
    password?: string;
}

type UnifiedSignupScreenNavigationProp = NativeStackNavigationProp<RootStackParamList, 'UnifiedSignup'>;
type UnifiedSignupScreenRouteProp = RouteProp<RootStackParamList, 'UnifiedSignup'>;

interface Props {
    navigation: UnifiedSignupScreenNavigationProp;
    route: UnifiedSignupScreenRouteProp;
}

type UserIntent = 'help_needed' | 'attorney' | null;
type SignupStep = 'intent' | 'account' | 'details' | 'confirmation';

interface FormData {
    // Account info
    email: string;
    password: string;
    confirmPassword: string;

    // Client helper data
    profileName: string;
    isSelf: boolean;
    firstName: string;
    lastName: string;
    countryOfBirth: string;
    birthDate: string;
    nationality?: string;
    alienRegistrationNumber?: string;
    passportNumber?: string;
    schoolName?: string;
    studentIdNumber?: string;

    // Attorney data
    attorneyName: string;
    phoneNumber: string;
    zipCode: string;
    state: string;
}

const UnifiedSignupScreen: React.FC<Props> = ({ navigation }) => {
    const [currentStep, setCurrentStep] = useState<SignupStep>('intent');
    const [userIntent, setUserIntent] = useState<UserIntent>(null);
    const [isLoading, setIsLoading] = useState(false);
    const [formData, setFormData] = useState<FormData>({
        email: '',
        password: '',
        confirmPassword: '',
        profileName: '',
        isSelf: true,
        firstName: '',
        lastName: '',
        countryOfBirth: '',
        birthDate: '',
        nationality: '',
        alienRegistrationNumber: '',
        passportNumber: '',
        schoolName: '',
        studentIdNumber: '',
        attorneyName: '',
        phoneNumber: '',
        zipCode: '',
        state: '',
    });

    const updateFormData = (field: keyof FormData, value: string | boolean) => {
        setFormData(prev => ({ ...prev, [field]: value }));
    };

    const validateEmail = (email: string): boolean => {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(email);
    };

    const validatePassword = (password: string): boolean => {
        return password.length >= 8;
    };

    const validatePhoneNumber = (phone: string): boolean => {
        // E.164 format validation
        const phoneRegex = /^\+[1-9]\d{1,14}$/;
        return phoneRegex.test(phone);
    };

    const handleIntentSelection = (intent: UserIntent) => {
        setUserIntent(intent);
        setCurrentStep('account');
    };

    const handleAccountNext = () => {
        // Validate account info
        if (!validateEmail(formData.email)) {
            Alert.alert('Invalid Email', 'Please enter a valid email address.');
            return;
        }

        if (!validatePassword(formData.password)) {
            Alert.alert('Weak Password', 'Password must be at least 8 characters long.');
            return;
        }

        if (formData.password !== formData.confirmPassword) {
            Alert.alert('Password Mismatch', 'Passwords do not match.');
            return;
        }

        setCurrentStep('details');
    };

    const handleDetailsNext = () => {
        // Validate details based on user intent
        if (userIntent === 'help_needed') {
            if (!formData.firstName || !formData.lastName || !formData.countryOfBirth || !formData.birthDate) {
                Alert.alert('Missing Information', 'Please fill in all required fields.');
                return;
            }

            // Auto-generate profile name if not provided
            if (!formData.profileName) {
                updateFormData('profileName', `${formData.firstName} ${formData.lastName}`);
            }
        } else if (userIntent === 'attorney') {
            if (!formData.attorneyName || !formData.phoneNumber || !formData.zipCode || !formData.state) {
                Alert.alert('Missing Information', 'Please fill in all required fields.');
                return;
            }

            if (!validatePhoneNumber(formData.phoneNumber)) {
                Alert.alert('Invalid Phone', 'Please enter a valid phone number with country code (e.g., +1234567890).');
                return;
            }
        }

        setCurrentStep('confirmation');
    };

    const handleSignup = async () => {
        setIsLoading(true);

        try {
            const signupData: UnifiedSignupData = {
                email: formData.email,
                password: formData.password,
                primary_role: userIntent === 'attorney' ? 'attorney' : 'client_helper',
            };

            const roleData: RoleSpecificData = {};

            if (userIntent === 'attorney') {
                const attorneyData: AttorneyRegistrationData = {
                    name: formData.attorneyName,
                    phoneNumber: formData.phoneNumber,
                    email: formData.email,
                    zipCode: formData.zipCode,
                    jurisdiction: formData.state,
                };
                roleData.attorney_data = attorneyData;
            } else if (userIntent === 'help_needed') {
                const clientProfileData: ClientProfileData = {
                    profile_name: formData.profileName || `${formData.firstName} ${formData.lastName}`,
                    is_self: formData.isSelf,
                    first_name: formData.firstName,
                    last_name: formData.lastName,
                    country_of_birth: formData.countryOfBirth,
                    birth_date: formData.birthDate,
                    nationality: formData.nationality || undefined,
                    alien_registration_number: formData.alienRegistrationNumber || undefined,
                    passport_number: formData.passportNumber || undefined,
                    school_name: formData.schoolName || undefined,
                    student_id_number: formData.studentIdNumber || undefined,
                };
                roleData.client_profile_data = clientProfileData;
            }

            await registerUnified(signupData, roleData);

            Alert.alert(
                'Success!',
                'Your account has been created successfully.',
                [
                    {
                        text: 'OK',
                        onPress: () => navigation.navigate('Home'),
                    },
                ]
            );

        } catch (error: unknown) {
            console.error('Signup failed:', error);
            const errorMessage = (error as { response?: { data?: { detail?: string } } }).response?.data?.detail || 'An error occurred during signup. Please try again.';
            Alert.alert(
                'Signup Failed',
                errorMessage
            );
        } finally {
            setIsLoading(false);
        }
    };

    const renderIntentStep = () => (
        <View style={styles.stepContainer}>
            <Text style={styles.title}>How can we help you?</Text>
            <Text style={styles.subtitle}>
                Habeas connects people facing immigration detention with legal help.
            </Text>

            <TouchableOpacity
                style={styles.intentButton}
                onPress={() => handleIntentSelection('help_needed')}
            >
                <Text style={styles.intentButtonTitle}>
                    I&apos;m worried that ICE may detain me or a loved one
                </Text>
                <Text style={styles.intentButtonSubtitle}>
                    Get connected with legal help and prepare for potential detention
                </Text>
            </TouchableOpacity>

            <TouchableOpacity
                style={styles.intentButton}
                onPress={() => handleIntentSelection('attorney')}
            >
                <Text style={styles.intentButtonTitle}>
                    I am an attorney willing to file a habeas petition
                </Text>
                <Text style={styles.intentButtonSubtitle}>
                    Join our network of attorneys helping people in immigration detention
                </Text>
            </TouchableOpacity>
        </View>
    );

    const renderAccountStep = () => (
        <View style={styles.stepContainer}>
            <Text style={styles.title}>Create Your Account</Text>
            <Text style={styles.subtitle}>
                We&apos;ll need some basic information to get you started.
            </Text>

            <View style={styles.inputGroup}>
                <Text style={styles.label}>Email Address</Text>
                <TextInput
                    style={styles.input}
                    value={formData.email}
                    onChangeText={(text) => updateFormData('email', text)}
                    placeholder="your.email@example.com"
                    keyboardType="email-address"
                    autoCapitalize="none"
                    autoCorrect={false}
                />
            </View>

            <View style={styles.inputGroup}>
                <Text style={styles.label}>Password</Text>
                <TextInput
                    style={styles.input}
                    value={formData.password}
                    onChangeText={(text) => updateFormData('password', text)}
                    placeholder="At least 8 characters"
                    secureTextEntry
                    autoCapitalize="none"
                />
            </View>

            <View style={styles.inputGroup}>
                <Text style={styles.label}>Confirm Password</Text>
                <TextInput
                    style={styles.input}
                    value={formData.confirmPassword}
                    onChangeText={(text) => updateFormData('confirmPassword', text)}
                    placeholder="Re-enter your password"
                    secureTextEntry
                    autoCapitalize="none"
                />
            </View>

            <TouchableOpacity style={styles.primaryButton} onPress={handleAccountNext}>
                <Text style={styles.primaryButtonText}>Continue</Text>
            </TouchableOpacity>

            <TouchableOpacity style={styles.backButton} onPress={() => setCurrentStep('intent')}>
                <Text style={styles.backButtonText}>Back</Text>
            </TouchableOpacity>
        </View>
    );

    const renderDetailsStep = () => {
        if (userIntent === 'help_needed') {
            return renderClientDetailsStep();
        } else if (userIntent === 'attorney') {
            return renderAttorneyDetailsStep();
        }
        return null;
    };

    const renderClientDetailsStep = () => (
        <View style={styles.stepContainer}>
            <Text style={styles.title}>Tell Us About Yourself</Text>
            <Text style={styles.subtitle}>
                This information helps us connect you with the right legal resources.
            </Text>

            <View style={styles.inputGroup}>
                <Text style={styles.label}>First Name *</Text>
                <TextInput
                    style={styles.input}
                    value={formData.firstName}
                    onChangeText={(text) => updateFormData('firstName', text)}
                    placeholder="Your first name"
                />
            </View>

            <View style={styles.inputGroup}>
                <Text style={styles.label}>Last Name *</Text>
                <TextInput
                    style={styles.input}
                    value={formData.lastName}
                    onChangeText={(text) => updateFormData('lastName', text)}
                    placeholder="Your last name"
                />
            </View>

            <View style={styles.inputGroup}>
                <Text style={styles.label}>Country of Birth *</Text>
                <TextInput
                    style={styles.input}
                    value={formData.countryOfBirth}
                    onChangeText={(text) => updateFormData('countryOfBirth', text)}
                    placeholder="e.g., Mexico, Guatemala, etc."
                />
            </View>

            <View style={styles.inputGroup}>
                <Text style={styles.label}>Date of Birth *</Text>
                <TextInput
                    style={styles.input}
                    value={formData.birthDate}
                    onChangeText={(text) => updateFormData('birthDate', text)}
                    placeholder="YYYY-MM-DD"
                />
            </View>

            <View style={styles.inputGroup}>
                <Text style={styles.label}>A-Number (if you have one)</Text>
                <TextInput
                    style={styles.input}
                    value={formData.alienRegistrationNumber}
                    onChangeText={(text) => updateFormData('alienRegistrationNumber', text)}
                    placeholder="A123456789"
                />
            </View>

            <TouchableOpacity style={styles.primaryButton} onPress={handleDetailsNext}>
                <Text style={styles.primaryButtonText}>Continue</Text>
            </TouchableOpacity>

            <TouchableOpacity style={styles.backButton} onPress={() => setCurrentStep('account')}>
                <Text style={styles.backButtonText}>Back</Text>
            </TouchableOpacity>
        </View>
    );

    const renderAttorneyDetailsStep = () => (
        <View style={styles.stepContainer}>
            <Text style={styles.title}>Attorney Information</Text>
            <Text style={styles.subtitle}>
                Help us verify your credentials and connect you with cases.
            </Text>

            <View style={styles.inputGroup}>
                <Text style={styles.label}>Full Name *</Text>
                <TextInput
                    style={styles.input}
                    value={formData.attorneyName}
                    onChangeText={(text) => updateFormData('attorneyName', text)}
                    placeholder="Your full professional name"
                />
            </View>

            <View style={styles.inputGroup}>
                <Text style={styles.label}>Phone Number *</Text>
                <TextInput
                    style={styles.input}
                    value={formData.phoneNumber}
                    onChangeText={(text) => updateFormData('phoneNumber', text)}
                    placeholder="+1234567890"
                    keyboardType="phone-pad"
                />
            </View>

            <View style={styles.inputGroup}>
                <Text style={styles.label}>ZIP Code *</Text>
                <TextInput
                    style={styles.input}
                    value={formData.zipCode}
                    onChangeText={(text) => updateFormData('zipCode', text)}
                    placeholder="12345"
                    keyboardType="numeric"
                />
            </View>

            <View style={styles.inputGroup}>
                <Text style={styles.label}>State *</Text>
                <TextInput
                    style={styles.input}
                    value={formData.state}
                    onChangeText={(text) => updateFormData('state', text.toUpperCase())}
                    placeholder="CA"
                    maxLength={2}
                    autoCapitalize="characters"
                />
            </View>

            <TouchableOpacity style={styles.primaryButton} onPress={handleDetailsNext}>
                <Text style={styles.primaryButtonText}>Continue</Text>
            </TouchableOpacity>

            <TouchableOpacity style={styles.backButton} onPress={() => setCurrentStep('account')}>
                <Text style={styles.backButtonText}>Back</Text>
            </TouchableOpacity>
        </View>
    );

    const renderConfirmationStep = () => (
        <View style={styles.stepContainer}>
            <Text style={styles.title}>Review Your Information</Text>
            <Text style={styles.subtitle}>
                Please confirm your details before creating your account.
            </Text>

            <View style={styles.summaryContainer}>
                <Text style={styles.summaryTitle}>Account Type:</Text>
                <Text style={styles.summaryText}>
                    {userIntent === 'attorney' ? 'Attorney' : 'Person Seeking Help'}
                </Text>

                <Text style={styles.summaryTitle}>Email:</Text>
                <Text style={styles.summaryText}>{formData.email}</Text>

                {userIntent === 'help_needed' && (
                    <>
                        <Text style={styles.summaryTitle}>Name:</Text>
                        <Text style={styles.summaryText}>{formData.firstName} {formData.lastName}</Text>

                        <Text style={styles.summaryTitle}>Country of Birth:</Text>
                        <Text style={styles.summaryText}>{formData.countryOfBirth}</Text>
                    </>
                )}

                {userIntent === 'attorney' && (
                    <>
                        <Text style={styles.summaryTitle}>Name:</Text>
                        <Text style={styles.summaryText}>{formData.attorneyName}</Text>

                        <Text style={styles.summaryTitle}>Location:</Text>
                        <Text style={styles.summaryText}>{formData.zipCode}, {formData.state}</Text>
                    </>
                )}
            </View>

            <TouchableOpacity
                style={[styles.primaryButton, isLoading && styles.disabledButton]}
                onPress={handleSignup}
                disabled={isLoading}
            >
                <Text style={styles.primaryButtonText}>
                    {isLoading ? 'Creating Account...' : 'Create Account'}
                </Text>
            </TouchableOpacity>

            <TouchableOpacity style={styles.backButton} onPress={() => setCurrentStep('details')}>
                <Text style={styles.backButtonText}>Back</Text>
            </TouchableOpacity>
        </View>
    );

    const renderCurrentStep = () => {
        switch (currentStep) {
            case 'intent':
                return renderIntentStep();
            case 'account':
                return renderAccountStep();
            case 'details':
                return renderDetailsStep();
            case 'confirmation':
                return renderConfirmationStep();
            default:
                return renderIntentStep();
        }
    };

    return (
        <KeyboardAvoidingView
            style={styles.container}
            behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
        >
            <ScrollView contentContainerStyle={styles.scrollContent}>
                {renderCurrentStep()}
            </ScrollView>
        </KeyboardAvoidingView>
    );
};

const styles = StyleSheet.create({
    backButton: {
        alignItems: 'center',
        marginTop: 10,
        padding: 15,
    },
    backButtonText: {
        color: '#6c757d',
        fontSize: 16,
    },
    container: {
        backgroundColor: '#f8f9fa',
        flex: 1,
    },
    disabledButton: {
        backgroundColor: '#6c757d',
    },
    input: {
        backgroundColor: '#fff',
        borderColor: '#dee2e6',
        borderRadius: 8,
        borderWidth: 1,
        fontSize: 16,
        padding: 12,
    },
    inputGroup: {
        marginBottom: 20,
    },
    intentButton: {
        backgroundColor: '#fff',
        borderColor: '#e9ecef',
        borderRadius: 12,
        borderWidth: 2,
        elevation: 3,
        marginBottom: 15,
        padding: 20,
        shadowColor: '#000',
        shadowOffset: { width: 0, height: 2 },
        shadowOpacity: 0.1,
        shadowRadius: 4,
    },
    intentButtonSubtitle: {
        color: '#6c757d',
        fontSize: 14,
        lineHeight: 20,
    },
    intentButtonTitle: {
        color: '#2c3e50',
        fontSize: 18,
        fontWeight: '600',
        marginBottom: 8,
    },
    label: {
        color: '#2c3e50',
        fontSize: 16,
        fontWeight: '600',
        marginBottom: 8,
    },
    primaryButton: {
        alignItems: 'center',
        backgroundColor: '#007bff',
        borderRadius: 8,
        marginTop: 20,
        padding: 15,
    },
    primaryButtonText: {
        color: '#fff',
        fontSize: 18,
        fontWeight: '600',
    },
    scrollContent: {
        flexGrow: 1,
        padding: 20,
    },
    stepContainer: {
        flex: 1,
        justifyContent: 'center',
    },
    subtitle: {
        color: '#7f8c8d',
        fontSize: 16,
        lineHeight: 22,
        marginBottom: 30,
        textAlign: 'center',
    },
    summaryContainer: {
        backgroundColor: '#fff',
        borderRadius: 12,
        marginBottom: 20,
        padding: 20,
    },
    summaryText: {
        color: '#495057',
        fontSize: 16,
        marginBottom: 10,
    },
    summaryTitle: {
        color: '#2c3e50',
        fontSize: 16,
        fontWeight: '600',
        marginBottom: 5,
        marginTop: 10,
    },
    title: {
        color: '#2c3e50',
        fontSize: 28,
        fontWeight: 'bold',
        marginBottom: 10,
        textAlign: 'center',
    },
});

export default UnifiedSignupScreen;
