import React, { useEffect, useState } from 'react';
import { View, Text, StyleSheet, FlatList, ActivityIndicator, TouchableOpacity, Alert } from 'react-native';
import api from '../api/client';
import EmergencySlider from '../components/EmergencySlider';
import { EmergencyHandler } from '../utils/emergencyHandler';


export default function HomeScreen({ navigation }: any) {
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
                <Text style={styles.pageTitle}>Welcome to Habeas</Text>
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
    container: {
        flex: 1,
        padding: 20,
    },
    // Section containers for static layout
    headerSection: {
        marginBottom: 20,
        marginTop: 40,
    },
    emergencySection: {
        height: 205, // Fixed height to prevent layout shift
        marginBottom: 30, // Increased space between emergency section and buttons
    },
    buttonsSection: {
        marginTop: 20, // Additional margin on the button section itself
    },
    pageTitle: {
        fontSize: 24,
        fontWeight: 'bold',
        marginBottom: 16,
        textAlign: 'center',
    },
    description: {
        color: '#555',
    },
    // Emergency banner styles
    emergencyBannerContainer: {
        height: 60, // Fixed height
        padding: 15,
        borderRadius: 8,
        flexDirection: 'row',
        justifyContent: 'space-between',
        alignItems: 'center',
        marginBottom: 15,
    },
    emergencyActive: {
        backgroundColor: '#c00',
    },
    emergencyInactive: {
        backgroundColor: '#f8f8f8',
        borderColor: '#ddd',
        borderWidth: 1,
    },
    emergencyText: {
        color: 'white',
        fontSize: 16,
        fontWeight: 'bold',
    },
    emergencyInactiveText: {
        color: '#666',
        fontSize: 14,
        textAlign: 'center',
        width: '100%',
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
    personalInfoButton: {
        alignItems: 'center',
        backgroundColor: '#28a745',
        borderRadius: 5,
        marginBottom: 30,
        padding: 15,
    },
    buttonText: {
        color: '#fff',
        fontSize: 16,
        fontWeight: '600',
    },
    loaderStyle: {
        marginTop: 20,
    },
    error: {
        color: 'red',
        marginTop: 20,
        textAlign: 'center',
    },
    exampleDescription: {
        color: '#666',
        fontSize: 14,
        marginTop: 5,
    },
    exampleItem: {
        backgroundColor: '#f5f5f5',
        borderRadius: 5,
        marginBottom: 10,
        padding: 15,
    },
    exampleName: {
        fontSize: 16,
        fontWeight: 'bold',
    },
    examplesContainer: {
        flex: 1,
    },
    loadingIndicator: {
        marginTop: 20,
    },
    sectionHeading: {
        fontSize: 18,
        fontWeight: 'bold',
        marginBottom: 10,
    },
    mainTitle: {
        fontSize: 24,
        fontWeight: 'bold',
        marginBottom: 16,
        marginTop: 40,
        textAlign: 'center',
    },
});
