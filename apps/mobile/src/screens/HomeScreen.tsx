import React, { useEffect, useState } from 'react';
import { View, Text, StyleSheet, TouchableOpacity } from 'react-native';
import EmergencySlider from '../components/EmergencySlider';
import { EmergencyHandler } from '../utils/emergencyHandler';
import { NativeStackNavigationProp } from '@react-navigation/native-stack';

// Define a simple navigation parameter list
type RootStackParamList = {
    Home: undefined;
    AttorneySignup: undefined;
    PersonalInfo: undefined;
};

type HomeScreenProps = {
    navigation: NativeStackNavigationProp<RootStackParamList, 'Home'>;
};

export default function HomeScreen({ navigation }: HomeScreenProps) {
    const [emergencyActive, setEmergencyActive] = useState(false);

    // Check if emergency is already active on component mount
    useEffect(() => {
        checkEmergencyStatus();
    }, []);

    // Function to check current emergency status
    const checkEmergencyStatus = async () => {
        try {
            const emergencyState = await EmergencyHandler.getEmergencyState();
            setEmergencyActive(emergencyState.activated);
        } catch (error) {
            console.error('Failed to check emergency status:', error);
        }
    };

    // Handle emergency activation
    const handleEmergencyActivated = async () => {
        try {
            await EmergencyHandler.activateEmergency();
            setEmergencyActive(true);
        } catch (error) {
            console.error('Failed to handle emergency activation:', error);
        }
    };

    // Handle emergency deactivation
    const handleDeactivateEmergency = async () => {
        try {
            await EmergencyHandler.deactivateEmergency();
            setEmergencyActive(false);
        } catch (error) {
            console.error('Failed to deactivate emergency:', error);
        }
    };

    return (
        <View style={styles.container}>
            {/* Header Section */}
            <View style={styles.headerSection}>
                <Text style={styles.headerTitle}>Welcome to Habeas</Text>
                <Text style={styles.description}>
                    Connecting detained individuals with legal representatives
                </Text>
            </View>

            {/* Emergency Section - Fixed Height */}
            <View style={styles.emergencySection}>
                {/* Emergency Status Banner - Always reserved space, only content changes */}
                <View style={[
                    styles.emergencyBannerContainer,
                    emergencyActive ? styles.emergencyActive : styles.emergencyInactive
                ]}>
                    {emergencyActive ? (
                        <>
                            <Text style={styles.emergencyText}>
                                Emergency Mode Active
                            </Text>
                            <TouchableOpacity
                                style={styles.deactivateButton}
                                onPress={handleDeactivateEmergency}
                            >
                                <Text style={styles.deactivateText}>Deactivate</Text>
                            </TouchableOpacity>
                        </>
                    ) : (
                        <Text style={styles.emergencyInactiveText}>
                            Use the slider below in case of emergency
                        </Text>
                    )}
                </View>

                {/* Emergency Slider */}
                <EmergencySlider
                    onEmergencyActivated={handleEmergencyActivated}
                    disabled={emergencyActive}
                />
            </View>

            {/* Navigation Buttons Section */}
            <View style={styles.buttonsSection}>
                <View style={styles.separator} />

                <TouchableOpacity
                    style={styles.signupButton}
                    onPress={() => navigation.navigate('AttorneySignup')}
                >
                    <Text style={styles.signupButtonText}>Register as an Attorney</Text>
                </TouchableOpacity>

                <TouchableOpacity
                    style={styles.personalInfoButton}
                    onPress={() => navigation.navigate('PersonalInfo')}
                >
                    <Text style={styles.buttonText}>Personal Information</Text>
                </TouchableOpacity>
            </View>
        </View>
    );
}

const styles = StyleSheet.create({
    buttonText: {
        color: '#fff',
        fontSize: 16,
        fontWeight: '600',
    },
    buttonsSection: {
        marginTop: 20,
    },
    container: {
        flex: 1,
        padding: 20,
    },
    deactivateButton: {
        backgroundColor: 'white',
        borderRadius: 4,
        paddingHorizontal: 12,
        paddingVertical: 6,
    },
    deactivateText: {
        color: '#c00',
        fontWeight: 'bold',
    },
    description: {
        color: '#555',
    },
    emergencyActive: {
        backgroundColor: '#c00',
    },
    emergencyBannerContainer: {
        alignItems: 'center',
        borderRadius: 8,
        flexDirection: 'row',
        height: 60,
        justifyContent: 'space-between',
        marginBottom: 15,
        padding: 15,
    },
    emergencyInactive: {
        backgroundColor: '#f8f8f8',
        borderColor: '#ddd',
        borderWidth: 1,
    },
    emergencyInactiveText: {
        color: '#666',
        fontSize: 14,
        textAlign: 'center',
        width: '100%',
    },
    emergencySection: {
        height: 205,
        marginBottom: 30,
    },
    emergencyText: {
        color: 'white',
        fontSize: 16,
        fontWeight: 'bold',
    },
    headerSection: {
        marginBottom: 20,
        marginTop: 40,
    },
    headerTitle: {
        fontSize: 24,
        fontWeight: 'bold',
        marginBottom: 16,
        textAlign: 'center',
    },
    personalInfoButton: {
        alignItems: 'center',
        backgroundColor: '#28a745',
        borderRadius: 5,
        marginBottom: 30,
        padding: 15,
    },
    separator: {
        backgroundColor: '#e0e0e0',
        height: 1,
        marginBottom: 25,
        width: '100%',
    },
    signupButton: {
        alignItems: 'center',
        backgroundColor: '#4a90e2',
        borderRadius: 5,
        marginBottom: 30,
        padding: 15,
        textAlign: 'center',
    },
    signupButtonText: {
        color: '#fff',
        fontSize: 16,
        fontWeight: '600',
    },
});
