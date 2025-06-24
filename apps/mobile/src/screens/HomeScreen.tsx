import React, { useEffect, useState } from 'react';
import { View, Text, StyleSheet, TouchableOpacity, ScrollView, SafeAreaView } from 'react-native';
import EmergencySlider from '../components/EmergencySlider';
import { EmergencyHandler } from '../utils/emergencyHandler';
import { NativeStackNavigationProp } from '@react-navigation/native-stack';
import { RootStackParamList } from '../App';

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
        <SafeAreaView style={styles.container}>
            <ScrollView contentContainerStyle={styles.scrollContent} showsVerticalScrollIndicator={false}>
                {/* Hero Section */}
                <View style={styles.heroSection}>
                    <Text style={styles.appName}>Habeas</Text>
                    <Text style={styles.heroTitle}>
                        No One Should Face Immigration Detention Alone
                    </Text>
                    <Text style={styles.heroSubtitle}>
                        Connect with experienced immigration attorneys who understand your situation and are ready to help protect your rights.
                    </Text>
                </View>

                {/* Emergency Section */}
                <View style={styles.emergencySection}>
                    <View style={styles.emergencyHeader}>
                        <Text style={styles.emergencyTitle}>
                            {emergencyActive ? '🚨 Emergency Mode Active' : '⚡ Emergency Situation?'}
                        </Text>
                        <Text style={styles.emergencyDescription}>
                            {emergencyActive
                                ? 'Your emergency contacts have been notified. Legal help is being coordinated.'
                                : 'If you or someone you know has been detained, use the emergency slider below for immediate assistance.'
                            }
                        </Text>
                    </View>

                    {emergencyActive && (
                        <TouchableOpacity
                            style={styles.deactivateButton}
                            onPress={handleDeactivateEmergency}
                        >
                            <Text style={styles.deactivateButtonText}>Deactivate Emergency Mode</Text>
                        </TouchableOpacity>
                    )}

                    <View style={styles.sliderContainer}>
                        <EmergencySlider
                            onEmergencyActivated={handleEmergencyActivated}
                            disabled={emergencyActive}
                        />
                    </View>
                </View>

                {/* Value Propositions */}
                <View style={styles.benefitsSection}>
                    <View style={styles.benefitItem}>
                        <Text style={styles.benefitIcon}>⚖️</Text>
                        <View style={styles.benefitText}>
                            <Text style={styles.benefitTitle}>Expert Legal Help</Text>
                            <Text style={styles.benefitDescription}>
                                Connect with qualified immigration attorneys experienced in habeas corpus petitions
                            </Text>
                        </View>
                    </View>

                    <View style={styles.benefitItem}>
                        <Text style={styles.benefitIcon}>🤝</Text>
                        <View style={styles.benefitText}>
                            <Text style={styles.benefitTitle}>Family Support</Text>
                            <Text style={styles.benefitDescription}>
                                Help multiple family members and loved ones from a single account
                            </Text>
                        </View>
                    </View>

                    <View style={styles.benefitItem}>
                        <Text style={styles.benefitIcon}>🔒</Text>
                        <View style={styles.benefitText}>
                            <Text style={styles.benefitTitle}>Secure & Confidential</Text>
                            <Text style={styles.benefitDescription}>
                                Your personal information is protected with bank-level security
                            </Text>
                        </View>
                    </View>
                </View>

                {/* Call to Action */}
                <View style={styles.ctaSection}>
                    <TouchableOpacity
                        style={styles.primaryButton}
                        onPress={() => navigation.navigate('UnifiedSignup')}
                    >
                        <Text style={styles.primaryButtonText}>Get Started</Text>
                        <Text style={styles.primaryButtonSubtext}>
                            Free to create an account &bull; Takes 2 minutes
                        </Text>
                    </TouchableOpacity>

                    <Text style={styles.supportText}>
                        Whether you need legal help or you&apos;re an attorney ready to serve, we&apos;ll guide you through the right steps.
                    </Text>
                </View>

                {/* Secondary Actions */}
                <View style={styles.secondarySection}>
                    <TouchableOpacity
                        style={styles.secondaryButton}
                        onPress={() => navigation.navigate('PersonalInfo')}
                    >
                        <Text style={styles.secondaryButtonText}>View Personal Information</Text>
                    </TouchableOpacity>
                </View>
            </ScrollView>
        </SafeAreaView>
    );
}

const styles = StyleSheet.create({
    appName: {
        color: '#1a365d',
        fontSize: 32,
        fontWeight: '700',
        letterSpacing: -0.5,
        marginBottom: 16,
    },
    benefitDescription: {
        color: '#4a5568',
        fontSize: 15,
        lineHeight: 22,
    },
    benefitIcon: {
        fontSize: 24,
        marginRight: 16,
        marginTop: 2,
    },
    benefitItem: {
        alignItems: 'flex-start',
        flexDirection: 'row',
        marginBottom: 24,
        paddingHorizontal: 4,
    },
    benefitText: {
        flex: 1,
    },
    benefitTitle: {
        color: '#2d3748',
        fontSize: 18,
        fontWeight: '600',
        marginBottom: 4,
    },
    benefitsSection: {
        marginBottom: 32,
    },
    container: {
        backgroundColor: '#ffffff',
        flex: 1,
    },
    ctaSection: {
        alignItems: 'center',
        marginBottom: 32,
    },
    deactivateButton: {
        alignSelf: 'center',
        backgroundColor: '#c53030',
        borderRadius: 8,
        marginBottom: 16,
        paddingHorizontal: 24,
        paddingVertical: 12,
    },
    deactivateButtonText: {
        color: '#ffffff',
        fontSize: 16,
        fontWeight: '600',
    },
    emergencyDescription: {
        color: '#744210',
        fontSize: 14,
        lineHeight: 20,
        textAlign: 'center',
    },
    emergencyHeader: {
        marginBottom: 16,
    },
    emergencySection: {
        backgroundColor: '#fff5f5',
        borderColor: '#fed7d7',
        borderRadius: 16,
        borderWidth: 1,
        marginBottom: 32,
        padding: 20,
    },
    emergencyTitle: {
        color: '#c53030',
        fontSize: 18,
        fontWeight: '600',
        marginBottom: 8,
        textAlign: 'center',
    },
    heroSection: {
        alignItems: 'center',
        paddingBottom: 40,
        paddingTop: 20,
    },
    heroSubtitle: {
        color: '#4a5568',
        fontSize: 18,
        lineHeight: 26,
        marginHorizontal: 8,
        textAlign: 'center',
    },
    heroTitle: {
        color: '#2d3748',
        fontSize: 28,
        fontWeight: '600',
        lineHeight: 36,
        marginBottom: 16,
        textAlign: 'center',
    },
    primaryButton: {
        alignItems: 'center',
        backgroundColor: '#3182ce',
        borderRadius: 12,
        elevation: 8,
        marginBottom: 16,
        paddingHorizontal: 32,
        paddingVertical: 18,
        shadowColor: '#3182ce',
        shadowOffset: { width: 0, height: 4 },
        shadowOpacity: 0.3,
        shadowRadius: 8,
        width: '100%',
    },
    primaryButtonSubtext: {
        color: '#bee3f8',
        fontSize: 14,
        fontWeight: '500',
    },
    primaryButtonText: {
        color: '#ffffff',
        fontSize: 20,
        fontWeight: '700',
        marginBottom: 4,
    },
    scrollContent: {
        paddingBottom: 40,
        paddingHorizontal: 24,
    },
    secondaryButton: {
        backgroundColor: '#f7fafc',
        borderColor: '#e2e8f0',
        borderRadius: 8,
        borderWidth: 1,
        paddingHorizontal: 24,
        paddingVertical: 14,
    },
    secondaryButtonText: {
        color: '#4a5568',
        fontSize: 16,
        fontWeight: '500',
    },
    secondarySection: {
        alignItems: 'center',
    },
    sliderContainer: {
        marginTop: 8,
    },
    supportText: {
        color: '#4a5568',
        fontSize: 16,
        lineHeight: 24,
        marginHorizontal: 8,
        textAlign: 'center',
    },
});
