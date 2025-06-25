import React, { useEffect, useState } from 'react';
import { View, Text, StyleSheet, TouchableOpacity, ScrollView, SafeAreaView } from 'react-native';
import EmergencySlider from '../components/EmergencySlider';
import EmergencyStatusDisplay from '../components/EmergencyStatusDisplay';
import LovedOneEmergencyModal from '../components/LovedOneEmergencyModal';
import { EmergencyHandler } from '../utils/emergencyHandler';
import { useAuth } from '../contexts/AuthContext';
import { deactivateEmergencyCase } from '../api/client';
import { NativeStackNavigationProp } from '@react-navigation/native-stack';
import { RootStackParamList } from '../App';

type HomeScreenProps = {
    navigation: NativeStackNavigationProp<RootStackParamList, 'Home'>;
};

export default function HomeScreen({ navigation }: HomeScreenProps) {
    const [emergencyActive, setEmergencyActive] = useState(false);
    const [activeCaseId, setActiveCaseId] = useState<number | undefined>(undefined);
    const [showLovedOneModal, setShowLovedOneModal] = useState(false);
    const { isAuthenticated, user, logout, emergencyStatus, checkEmergencyEligibility, refreshEmergencyStatus, isAttorney } = useAuth();

    // Check if emergency is already active on component mount
    useEffect(() => {
        checkEmergencyStatus();
    }, []);

    // Check for active emergency case from auth context
    useEffect(() => {
        if (emergencyStatus?.active_emergency_case_id) {
            setEmergencyActive(true);
            setActiveCaseId(emergencyStatus.active_emergency_case_id);
        } else {
            // Fallback to local emergency handler check
            checkEmergencyStatus();
        }
    }, [emergencyStatus]);

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

    // Handle loved one emergency creation
    const handleLovedOneEmergencyCreated = (caseId: number) => {
        setActiveCaseId(caseId);
        setEmergencyActive(true);
        setShowLovedOneModal(false);
    };

    // Handle emergency deactivation
    const handleDeactivateEmergency = async () => {
        try {
            if (activeCaseId && user) {
                // Deactivate via API if we have a case ID
                await deactivateEmergencyCase(activeCaseId, user.id, { reason: 'User deactivated' });
                await refreshEmergencyStatus();
            } else {
                // Fallback to local deactivation
                await EmergencyHandler.deactivateEmergency();
            }
            setEmergencyActive(false);
            setActiveCaseId(undefined);
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
                    {isAuthenticated ? (
                        <>
                            <Text style={styles.heroTitle}>
                                Welcome back{user?.email ? `, ${user.email.split('@')[0]}` : ''}!
                            </Text>
                            <Text style={styles.heroSubtitle}>
                                Your emergency legal support is ready when you need it.
                            </Text>
                        </>
                    ) : (
                        <>
                            <Text style={styles.heroTitle}>
                                No One Should Face Immigration Detention Alone
                            </Text>
                            <Text style={styles.heroSubtitle}>
                                Connect with experienced immigration attorneys who understand your situation and are ready to help protect your rights.
                            </Text>
                        </>
                    )}
                </View>

                {/* Attorney Dashboard Section - Only show for attorneys */}
                {isAuthenticated && isAttorney() && (
                    <View style={styles.attorneySection}>
                        <Text style={styles.attorneyTitle}>⚖️ Attorney Dashboard</Text>
                        <Text style={styles.attorneyDescription}>
                            Manage your emergency cases and notification preferences
                        </Text>
                        <TouchableOpacity
                            style={styles.attorneyButton}
                            onPress={() => navigation.navigate('AttorneyDashboard')}
                        >
                            <Text style={styles.attorneyButtonText}>Open Attorney Dashboard</Text>
                        </TouchableOpacity>
                    </View>
                )}

                {/* Emergency Section - Only show if authenticated and not attorney */}
                {isAuthenticated && !isAttorney() && (
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

                            {emergencyStatus && !emergencyStatus.can_activate_emergency && (
                                <View style={styles.setupSection}>
                                    <Text style={styles.setupText}>
                                        Complete your profile and add emergency contacts to enable emergency notifications.
                                    </Text>
                                    <TouchableOpacity
                                        style={styles.setupButton}
                                        onPress={() => navigation.navigate('EmergencySetup')}
                                    >
                                        <Text style={styles.setupButtonText}>Set Up Emergency Info</Text>
                                    </TouchableOpacity>
                                </View>
                            )}
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
                            {emergencyActive ? (
                                <EmergencyStatusDisplay
                                    caseId={activeCaseId}
                                    onDeactivate={handleDeactivateEmergency}
                                />
                            ) : (
                                <EmergencySlider
                                    onEmergencyActivated={handleEmergencyActivated}
                                    disabled={emergencyActive}
                                    visible={checkEmergencyEligibility()}
                                />
                            )}
                        </View>

                        {/* Loved One Emergency Button - Only show if authenticated and eligible */}
                        {isAuthenticated && checkEmergencyEligibility() && !emergencyActive && (
                            <View style={styles.lovedOneSection}>
                                <Text style={styles.lovedOneTitle}>Someone else detained?</Text>
                                <TouchableOpacity
                                    style={styles.lovedOneButton}
                                    onPress={() => setShowLovedOneModal(true)}
                                >
                                    <Text style={styles.lovedOneIcon}>👥</Text>
                                    <Text style={styles.lovedOneButtonText}>Report Loved One Detention</Text>
                                </TouchableOpacity>
                                <Text style={styles.lovedOneDescription}>
                                    Report if a family member or friend has been detained
                                </Text>
                            </View>
                        )}
                    </View>
                )}

                {/* Authentication Section - Only show if not authenticated */}
                {!isAuthenticated && (
                    <View style={styles.authSection}>
                        <Text style={styles.authTitle}>Sign in to access emergency features</Text>
                        <Text style={styles.authDescription}>
                            Emergency legal support requires a secure account to protect your information and connect you with attorneys.
                        </Text>
                        <TouchableOpacity
                            style={styles.authButton}
                            onPress={() => navigation.navigate('Login')}
                        >
                            <Text style={styles.authButtonText}>Sign In</Text>
                        </TouchableOpacity>
                    </View>
                )}

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
                    {isAuthenticated ? (
                        <TouchableOpacity
                            style={styles.logoutButton}
                            onPress={logout}
                        >
                            <Text style={styles.logoutButtonText}>Sign Out</Text>
                        </TouchableOpacity>
                    ) : (
                        <>
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
                        </>
                    )}
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

            {/* Loved One Emergency Modal */}
            <LovedOneEmergencyModal
                visible={showLovedOneModal}
                onClose={() => setShowLovedOneModal(false)}
                onEmergencyCreated={handleLovedOneEmergencyCreated}
            />
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
    attorneyButton: {
        backgroundColor: '#1e40af',
        borderRadius: 8,
        paddingHorizontal: 24,
        paddingVertical: 12,
    },
    attorneyButtonText: {
        color: '#ffffff',
        fontSize: 16,
        fontWeight: '600',
        textAlign: 'center',
    },
    attorneyDescription: {
        color: '#1e40af',
        fontSize: 14,
        lineHeight: 20,
        marginBottom: 16,
        textAlign: 'center',
    },
    attorneySection: {
        backgroundColor: '#f0f9ff',
        borderColor: '#bfdbfe',
        borderRadius: 16,
        borderWidth: 1,
        marginBottom: 32,
        padding: 20,
    },
    attorneyTitle: {
        color: '#1e40af',
        fontSize: 18,
        fontWeight: '600',
        marginBottom: 8,
        textAlign: 'center',
    },
    authButton: {
        backgroundColor: '#c00',
        borderRadius: 8,
        paddingHorizontal: 32,
        paddingVertical: 14,
    },
    authButtonText: {
        color: '#ffffff',
        fontSize: 16,
        fontWeight: '600',
        textAlign: 'center',
    },
    authDescription: {
        color: '#4a5568',
        fontSize: 15,
        lineHeight: 22,
        marginBottom: 24,
        textAlign: 'center',
    },
    authSection: {
        alignItems: 'center',
        backgroundColor: '#f8f9fa',
        borderRadius: 16,
        marginBottom: 32,
        paddingHorizontal: 24,
        paddingVertical: 32,
    },
    authTitle: {
        color: '#2d3748',
        fontSize: 20,
        fontWeight: '600',
        marginBottom: 12,
        textAlign: 'center',
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
    logoutButton: {
        backgroundColor: '#6c757d',
        borderRadius: 8,
        paddingHorizontal: 32,
        paddingVertical: 14,
    },
    logoutButtonText: {
        color: '#ffffff',
        fontSize: 16,
        fontWeight: '600',
        textAlign: 'center',
    },
    lovedOneButton: {
        alignItems: 'center',
        backgroundColor: '#1e40af',
        borderRadius: 12,
        flexDirection: 'row',
        justifyContent: 'center',
        marginBottom: 12,
        paddingHorizontal: 20,
        paddingVertical: 14,
        width: '100%',
    },
    lovedOneButtonText: {
        color: '#ffffff',
        fontSize: 16,
        fontWeight: '600',
    },
    lovedOneDescription: {
        color: '#6b7280',
        fontSize: 13,
        lineHeight: 18,
        textAlign: 'center',
    },
    lovedOneIcon: {
        fontSize: 20,
        marginRight: 8,
    },
    lovedOneSection: {
        alignItems: 'center',
        backgroundColor: '#fefefe',
        borderColor: '#e2e8f0',
        borderRadius: 16,
        borderWidth: 1,
        marginTop: 20,
        padding: 20,
    },
    lovedOneTitle: {
        color: '#2d3748',
        fontSize: 16,
        fontWeight: '600',
        marginBottom: 12,
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
    setupButton: {
        backgroundColor: '#3182ce',
        borderRadius: 8,
        paddingHorizontal: 20,
        paddingVertical: 12,
    },
    setupButtonText: {
        color: '#ffffff',
        fontSize: 14,
        fontWeight: '600',
        textAlign: 'center',
    },
    setupSection: {
        alignItems: 'center',
    },
    setupText: {
        backgroundColor: '#fff3cd',
        borderColor: '#ffeaa7',
        borderRadius: 8,
        borderWidth: 1,
        color: '#856404',
        fontSize: 14,
        marginBottom: 12,
        marginTop: 12,
        padding: 12,
        textAlign: 'center',
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
