import React from 'react';
import {
    View,
    Text,
    StyleSheet,
    TouchableOpacity,
    ScrollView,
    SafeAreaView,
} from 'react-native';
import { NativeStackNavigationProp } from '@react-navigation/native-stack';
import { RootStackParamList } from '../App';

type EmergencySetupScreenProps = {
    navigation: NativeStackNavigationProp<RootStackParamList, 'EmergencySetup'>;
};

export default function EmergencySetupScreen({ navigation }: EmergencySetupScreenProps) {
    const handleSetupEmergencyContacts = () => {
        // Navigate to emergency contact setup
        // This would typically go to a dedicated emergency contact form
        console.log('Navigate to emergency contact setup');
    };

    const handleSetupClientProfile = () => {
        // Navigate to client profile setup
        // This would typically go to the unified signup flow
        navigation.navigate('UnifiedSignup');
    };

    return (
        <SafeAreaView style={styles.container}>
            <ScrollView style={styles.scrollContainer} showsVerticalScrollIndicator={false}>
                {/* Header */}
                <View style={styles.header}>
                    <Text style={styles.title}>Emergency Setup Required</Text>
                    <Text style={styles.subtitle}>
                        To use the emergency slider, you need to complete your emergency information
                    </Text>
                </View>

                {/* Emergency Icon */}
                <View style={styles.iconContainer}>
                    <Text style={styles.emergencyIcon}>🚨</Text>
                    <Text style={styles.iconSubtext}>Emergency Feature</Text>
                </View>

                {/* Requirements List */}
                <View style={styles.requirementsContainer}>
                    <Text style={styles.requirementsTitle}>What you need to set up:</Text>

                    <View style={styles.requirementItem}>
                        <View style={styles.requirementIcon}>
                            <Text style={styles.checkIcon}>👤</Text>
                        </View>
                        <View style={styles.requirementContent}>
                            <Text style={styles.requirementTitle}>Client Profile</Text>
                            <Text style={styles.requirementDescription}>
                                Basic information about yourself or your loved one who might need emergency assistance
                            </Text>
                        </View>
                    </View>

                    <View style={styles.requirementItem}>
                        <View style={styles.requirementIcon}>
                            <Text style={styles.checkIcon}>📱</Text>
                        </View>
                        <View style={styles.requirementContent}>
                            <Text style={styles.requirementTitle}>Emergency Contacts</Text>
                            <Text style={styles.requirementDescription}>
                                Family or friends who should be notified during an emergency situation
                            </Text>
                        </View>
                    </View>
                </View>

                {/* How It Works */}
                <View style={styles.howItWorksContainer}>
                    <Text style={styles.howItWorksTitle}>How Emergency Help Works:</Text>

                    <View style={styles.stepContainer}>
                        <View style={styles.stepNumber}>
                            <Text style={styles.stepNumberText}>1</Text>
                        </View>
                        <Text style={styles.stepText}>
                            Use the emergency slider when detention is imminent
                        </Text>
                    </View>

                    <View style={styles.stepContainer}>
                        <View style={styles.stepNumber}>
                            <Text style={styles.stepNumberText}>2</Text>
                        </View>
                        <Text style={styles.stepText}>
                            Your location is captured and matched to the appropriate federal district court
                        </Text>
                    </View>

                    <View style={styles.stepContainer}>
                        <View style={styles.stepNumber}>
                            <Text style={styles.stepNumberText}>3</Text>
                        </View>
                        <Text style={styles.stepText}>
                            Attorneys admitted to that court are immediately notified via multiple channels
                        </Text>
                    </View>

                    <View style={styles.stepContainer}>
                        <View style={styles.stepNumber}>
                            <Text style={styles.stepNumberText}>4</Text>
                        </View>
                        <Text style={styles.stepText}>
                            An attorney accepts your case and contacts you or your emergency contacts
                        </Text>
                    </View>
                </View>

                {/* Action Buttons */}
                <View style={styles.actionsContainer}>
                    <TouchableOpacity
                        style={styles.primaryButton}
                        onPress={handleSetupClientProfile}
                    >
                        <Text style={styles.primaryButtonText}>Set Up Client Profile</Text>
                    </TouchableOpacity>

                    <TouchableOpacity
                        style={styles.secondaryButton}
                        onPress={handleSetupEmergencyContacts}
                    >
                        <Text style={styles.secondaryButtonText}>Add Emergency Contacts</Text>
                    </TouchableOpacity>

                    <TouchableOpacity
                        style={styles.skipButton}
                        onPress={() => navigation.goBack()}
                    >
                        <Text style={styles.skipButtonText}>Skip for Now</Text>
                    </TouchableOpacity>
                </View>

                {/* Legal Notice */}
                <View style={styles.legalContainer}>
                    <Text style={styles.legalTitle}>Important Legal Notice</Text>
                    <Text style={styles.legalText}>
                        This emergency feature connects you with volunteer attorneys for immigration-related
                        detention. For other legal emergencies, call 911. This service does not guarantee
                        attorney availability or immediate response.
                    </Text>
                </View>
            </ScrollView>
        </SafeAreaView>
    );
}

const styles = StyleSheet.create({
    actionsContainer: {
        marginBottom: 32,
    },
    checkIcon: {
        fontSize: 18,
    },
    container: {
        backgroundColor: '#ffffff',
        flex: 1,
    },
    emergencyIcon: {
        fontSize: 64,
        marginBottom: 8,
    },
    header: {
        alignItems: 'center',
        paddingVertical: 32,
    },
    howItWorksContainer: {
        marginBottom: 32,
    },
    howItWorksTitle: {
        color: '#2d3748',
        fontSize: 18,
        fontWeight: '600',
        marginBottom: 16,
    },
    iconContainer: {
        alignItems: 'center',
        marginBottom: 32,
    },
    iconSubtext: {
        color: '#6b7280',
        fontSize: 14,
        fontWeight: '500',
    },
    legalContainer: {
        backgroundColor: '#fefefe',
        borderColor: '#e2e8f0',
        borderRadius: 8,
        borderWidth: 1,
        marginBottom: 32,
        padding: 16,
    },
    legalText: {
        color: '#6b7280',
        fontSize: 12,
        lineHeight: 18,
    },
    legalTitle: {
        color: '#2d3748',
        fontSize: 14,
        fontWeight: '600',
        marginBottom: 8,
    },
    primaryButton: {
        alignItems: 'center',
        backgroundColor: '#3182ce',
        borderRadius: 12,
        marginBottom: 12,
        paddingVertical: 16,
    },
    primaryButtonText: {
        color: '#ffffff',
        fontSize: 16,
        fontWeight: '600',
    },
    requirementContent: {
        flex: 1,
    },
    requirementDescription: {
        color: '#4a5568',
        fontSize: 14,
        lineHeight: 20,
    },
    requirementIcon: {
        alignItems: 'center',
        backgroundColor: '#ffffff',
        borderColor: '#cbd5e0',
        borderRadius: 20,
        borderWidth: 1,
        height: 40,
        justifyContent: 'center',
        marginRight: 12,
        width: 40,
    },
    requirementItem: {
        alignItems: 'flex-start',
        backgroundColor: '#f7fafc',
        borderColor: '#e2e8f0',
        borderRadius: 12,
        borderWidth: 1,
        flexDirection: 'row',
        marginBottom: 12,
        padding: 16,
    },
    requirementTitle: {
        color: '#2d3748',
        fontSize: 16,
        fontWeight: '600',
        marginBottom: 4,
    },
    requirementsContainer: {
        marginBottom: 32,
    },
    requirementsTitle: {
        color: '#2d3748',
        fontSize: 18,
        fontWeight: '600',
        marginBottom: 16,
    },
    scrollContainer: {
        flex: 1,
        paddingHorizontal: 24,
    },
    secondaryButton: {
        alignItems: 'center',
        backgroundColor: '#38a169',
        borderRadius: 12,
        marginBottom: 12,
        paddingVertical: 16,
    },
    secondaryButtonText: {
        color: '#ffffff',
        fontSize: 16,
        fontWeight: '600',
    },
    skipButton: {
        alignItems: 'center',
        backgroundColor: 'transparent',
        borderColor: '#cbd5e0',
        borderRadius: 12,
        borderWidth: 1,
        paddingVertical: 16,
    },
    skipButtonText: {
        color: '#4a5568',
        fontSize: 16,
        fontWeight: '500',
    },
    stepContainer: {
        alignItems: 'flex-start',
        flexDirection: 'row',
        marginBottom: 16,
    },
    stepNumber: {
        alignItems: 'center',
        backgroundColor: '#3182ce',
        borderRadius: 12,
        height: 24,
        justifyContent: 'center',
        marginRight: 12,
        width: 24,
    },
    stepNumberText: {
        color: '#ffffff',
        fontSize: 12,
        fontWeight: '600',
    },
    stepText: {
        color: '#4a5568',
        flex: 1,
        fontSize: 14,
        lineHeight: 20,
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
