import React, { useState, useEffect } from 'react';
import {
    View,
    Text,
    StyleSheet,
    TouchableOpacity,
    Modal,
    ScrollView,
    Alert,
    SafeAreaView,
} from 'react-native';
import { useAuth } from '../contexts/AuthContext';
import { createEmergencyCase, EmergencyActivationRequest } from '../api/client';
import DetentionLocationInput from './DetentionLocationInput';

interface ClientProfile {
    id: number;
    first_name: string;
    last_name: string;
    relationship: string;
}

interface LovedOneEmergencyModalProps {
    visible: boolean;
    onClose: () => void;
    onEmergencyCreated: (caseId: number) => void;
}

type ModalStep = 'profile_selection' | 'location_input' | 'creating_case';

const LovedOneEmergencyModal: React.FC<LovedOneEmergencyModalProps> = ({
    visible,
    onClose,
    onEmergencyCreated,
}) => {
    const { user } = useAuth();
    const [currentStep, setCurrentStep] = useState<ModalStep>('profile_selection');
    const [selectedProfileId, setSelectedProfileId] = useState<number | null>(null);
    const [isCreatingCase, setIsCreatingCase] = useState(false);

    // Mock client profiles data - in real app this would come from API
    const [clientProfiles] = useState<ClientProfile[]>([
        { id: 1, first_name: 'Maria', last_name: 'Rodriguez', relationship: 'Mother' },
        { id: 2, first_name: 'Carlos', last_name: 'Rodriguez', relationship: 'Father' },
        { id: 3, first_name: 'Ana', last_name: 'Rodriguez', relationship: 'Sister' },
    ]);

    // Reset modal state when it opens
    useEffect(() => {
        if (visible) {
            setCurrentStep('profile_selection');
            setSelectedProfileId(null);
            setIsCreatingCase(false);
        }
    }, [visible]);

    const handleProfileSelect = (profileId: number) => {
        setSelectedProfileId(profileId);
    };

    const handleContinueToLocation = () => {
        if (!selectedProfileId) {
            Alert.alert('Error', 'Please select a profile for your loved one');
            return;
        }
        setCurrentStep('location_input');
    };

    const handleAddNewProfile = () => {
        Alert.alert(
            'Add New Profile',
            'This will take you to the profile creation screen. Would you like to continue?',
            [
                { text: 'Cancel', style: 'cancel' },
                {
                    text: 'Continue',
                    onPress: () => {
                        // In a real app, this would navigate to profile creation
                        // For now, we'll just show a placeholder
                        Alert.alert('Feature Coming Soon', 'Profile creation will be available in the next update.');
                    }
                },
            ]
        );
    };

    const handleLocationSubmit = async (location: { description: string; zipCode?: string; city?: string; state?: string }) => {
        if (!selectedProfileId || !user) {
            Alert.alert('Error', 'Missing required information');
            return;
        }

        try {
            setIsCreatingCase(true);
            setCurrentStep('creating_case');

            const emergencyRequest: EmergencyActivationRequest = {
                client_profile_id: selectedProfileId,
                case_type: 'loved_one',
                location: location
            };

            const response = await createEmergencyCase(user.id, emergencyRequest);

            console.log('Loved one emergency case created:', response);

            Alert.alert(
                'Emergency Case Created',
                `Emergency case has been created for your loved one. ${response.attorneys_notified_count || 0} attorneys have been notified.`,
                [
                    {
                        text: 'OK',
                        onPress: () => {
                            onEmergencyCreated(response.case_id || 0);
                            onClose();
                        }
                    }
                ]
            );

        } catch (error) {
            console.error('Failed to create loved one emergency case:', error);
            Alert.alert(
                'Emergency Case Failed',
                'Failed to create emergency case for your loved one. Please try again or contact support.',
                [{ text: 'OK' }]
            );
            setCurrentStep('location_input');
        } finally {
            setIsCreatingCase(false);
        }
    };

    const handleCancel = () => {
        if (currentStep === 'location_input') {
            setCurrentStep('profile_selection');
        } else {
            onClose();
        }
    };

    const getSelectedProfile = () => {
        return clientProfiles.find(p => p.id === selectedProfileId);
    };

    const renderProfileSelection = () => (
        <View style={styles.stepContainer}>
            {/* Header */}
            <View style={styles.header}>
                <Text style={styles.title}>Loved One Emergency</Text>
                <Text style={styles.subtitle}>
                    Who has been detained? Select their profile or add a new one.
                </Text>
            </View>

            {/* Profile List */}
            <View style={styles.profilesContainer}>
                <Text style={styles.sectionTitle}>Existing Profiles:</Text>

                {clientProfiles.length > 0 ? (
                    clientProfiles.map((profile) => (
                        <TouchableOpacity
                            key={profile.id}
                            style={[
                                styles.profileItem,
                                selectedProfileId === profile.id && styles.profileItemSelected,
                            ]}
                            onPress={() => handleProfileSelect(profile.id)}
                        >
                            <View style={styles.profileInfo}>
                                <Text style={styles.profileName}>
                                    {profile.first_name} {profile.last_name}
                                </Text>
                                <Text style={styles.profileRelation}>{profile.relationship}</Text>
                            </View>
                            <View style={styles.radioButton}>
                                {selectedProfileId === profile.id && (
                                    <View style={styles.radioButtonSelected} />
                                )}
                            </View>
                        </TouchableOpacity>
                    ))
                ) : (
                    <View style={styles.noProfilesContainer}>
                        <Text style={styles.noProfilesText}>
                            No client profiles found. You&apos;ll need to add a profile for your loved one.
                        </Text>
                    </View>
                )}

                {/* Add New Profile Option */}
                <TouchableOpacity
                    style={styles.addProfileButton}
                    onPress={handleAddNewProfile}
                >
                    <Text style={styles.addProfileIcon}>+</Text>
                    <Text style={styles.addProfileText}>Add New Profile</Text>
                </TouchableOpacity>
            </View>

            {/* Action Buttons */}
            <View style={styles.actionsContainer}>
                <TouchableOpacity
                    style={[
                        styles.continueButton,
                        !selectedProfileId && styles.continueButtonDisabled,
                    ]}
                    onPress={handleContinueToLocation}
                    disabled={!selectedProfileId}
                >
                    <Text style={styles.continueButtonText}>Continue</Text>
                </TouchableOpacity>

                <TouchableOpacity style={styles.cancelButton} onPress={onClose}>
                    <Text style={styles.cancelButtonText}>Cancel</Text>
                </TouchableOpacity>
            </View>
        </View>
    );

    const renderLocationInput = () => (
        <View style={styles.stepContainer}>
            <View style={styles.selectedProfileHeader}>
                <Text style={styles.selectedProfileText}>
                    Creating emergency case for: {getSelectedProfile()?.first_name} {getSelectedProfile()?.last_name}
                </Text>
            </View>

            <DetentionLocationInput
                onLocationSubmit={handleLocationSubmit}
                onCancel={handleCancel}
                isLoading={isCreatingCase}
            />
        </View>
    );

    const renderCreatingCase = () => (
        <View style={styles.loadingContainer}>
            <Text style={styles.loadingIcon}>📡</Text>
            <Text style={styles.loadingTitle}>Creating Emergency Case</Text>
            <Text style={styles.loadingText}>
                Creating case for {getSelectedProfile()?.first_name} {getSelectedProfile()?.last_name}...
            </Text>
            <Text style={styles.loadingSubtext}>
                Determining court jurisdiction and notifying attorneys
            </Text>
        </View>
    );

    return (
        <Modal
            visible={visible}
            animationType="slide"
            presentationStyle="pageSheet"
            onRequestClose={onClose}
        >
            <SafeAreaView style={styles.container}>
                <ScrollView style={styles.scrollContainer} showsVerticalScrollIndicator={false}>
                    {currentStep === 'profile_selection' && renderProfileSelection()}
                    {currentStep === 'location_input' && renderLocationInput()}
                    {currentStep === 'creating_case' && renderCreatingCase()}
                </ScrollView>
            </SafeAreaView>
        </Modal>
    );
};

const styles = StyleSheet.create({
    actionsContainer: {
        gap: 12,
    },
    addProfileButton: {
        alignItems: 'center',
        backgroundColor: '#ffffff',
        borderColor: '#3182ce',
        borderRadius: 12,
        borderStyle: 'dashed',
        borderWidth: 2,
        flexDirection: 'row',
        justifyContent: 'center',
        paddingVertical: 20,
    },
    addProfileIcon: {
        color: '#3182ce',
        fontSize: 24,
        fontWeight: '600',
        marginRight: 8,
    },
    addProfileText: {
        color: '#3182ce',
        fontSize: 16,
        fontWeight: '600',
    },
    cancelButton: {
        alignItems: 'center',
        backgroundColor: 'transparent',
        borderColor: '#cbd5e0',
        borderRadius: 12,
        borderWidth: 1,
        paddingVertical: 16,
    },
    cancelButtonText: {
        color: '#4a5568',
        fontSize: 16,
        fontWeight: '500',
    },
    container: {
        backgroundColor: '#ffffff',
        flex: 1,
    },
    continueButton: {
        alignItems: 'center',
        backgroundColor: '#c53030',
        borderRadius: 12,
        paddingVertical: 16,
    },
    continueButtonDisabled: {
        backgroundColor: '#cbd5e0',
    },
    continueButtonText: {
        color: '#ffffff',
        fontSize: 16,
        fontWeight: '600',
    },
    header: {
        alignItems: 'center',
        marginBottom: 32,
        paddingTop: 20,
    },
    loadingContainer: {
        alignItems: 'center',
        flex: 1,
        justifyContent: 'center',
        paddingHorizontal: 32,
    },
    loadingIcon: {
        fontSize: 64,
        marginBottom: 16,
    },
    loadingSubtext: {
        color: '#6b7280',
        fontSize: 14,
        textAlign: 'center',
    },
    loadingText: {
        color: '#2d3748',
        fontSize: 16,
        marginBottom: 16,
        textAlign: 'center',
    },
    loadingTitle: {
        color: '#c53030',
        fontSize: 20,
        fontWeight: '600',
        marginBottom: 8,
        textAlign: 'center',
    },
    noProfilesContainer: {
        backgroundColor: '#fffbeb',
        borderColor: '#fbbf24',
        borderRadius: 8,
        borderWidth: 1,
        marginBottom: 16,
        padding: 16,
    },
    noProfilesText: {
        color: '#92400e',
        fontSize: 14,
        textAlign: 'center',
    },
    profileInfo: {
        flex: 1,
    },
    profileItem: {
        alignItems: 'center',
        backgroundColor: '#f7fafc',
        borderColor: '#e2e8f0',
        borderRadius: 12,
        borderWidth: 1,
        flexDirection: 'row',
        marginBottom: 12,
        padding: 16,
    },
    profileItemSelected: {
        backgroundColor: '#ebf8ff',
        borderColor: '#3182ce',
        borderWidth: 2,
    },
    profileName: {
        color: '#2d3748',
        fontSize: 16,
        fontWeight: '600',
        marginBottom: 4,
    },
    profileRelation: {
        color: '#6b7280',
        fontSize: 14,
    },
    profilesContainer: {
        marginBottom: 32,
    },
    radioButton: {
        alignItems: 'center',
        borderColor: '#cbd5e0',
        borderRadius: 10,
        borderWidth: 2,
        height: 20,
        justifyContent: 'center',
        width: 20,
    },
    radioButtonSelected: {
        backgroundColor: '#3182ce',
        borderRadius: 6,
        height: 12,
        width: 12,
    },
    scrollContainer: {
        flex: 1,
    },
    sectionTitle: {
        color: '#2d3748',
        fontSize: 18,
        fontWeight: '600',
        marginBottom: 16,
    },
    selectedProfileHeader: {
        backgroundColor: '#f0f9ff',
        borderColor: '#bae6fd',
        borderRadius: 8,
        borderWidth: 1,
        marginBottom: 24,
        padding: 12,
    },
    selectedProfileText: {
        color: '#0369a1',
        fontSize: 14,
        fontWeight: '600',
        textAlign: 'center',
    },
    stepContainer: {
        flex: 1,
        padding: 24,
    },
    subtitle: {
        color: '#4a5568',
        fontSize: 16,
        lineHeight: 24,
        textAlign: 'center',
    },
    title: {
        color: '#c53030',
        fontSize: 24,
        fontWeight: '700',
        marginBottom: 8,
        textAlign: 'center',
    },
});

export default LovedOneEmergencyModal;
