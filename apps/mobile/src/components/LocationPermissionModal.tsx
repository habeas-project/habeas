import React from 'react';
import {
    View,
    Text,
    StyleSheet,
    Modal,
    TouchableOpacity,
    Alert,
} from 'react-native';
import { requestLocationPermission } from '../api/client';

interface LocationPermissionModalProps {
    visible: boolean;
    onLocationGranted: () => void;
    onManualEntry: () => void;
    onClose: () => void;
}

const LocationPermissionModal: React.FC<LocationPermissionModalProps> = ({
    visible,
    onLocationGranted,
    onManualEntry,
    onClose,
}) => {
    const handleAllowLocation = async () => {
        try {
            const granted = await requestLocationPermission();
            if (granted) {
                onLocationGranted();
            } else {
                Alert.alert(
                    'Location Permission Denied',
                    'You can still proceed by entering your location manually.',
                    [
                        { text: 'Enter Manually', onPress: onManualEntry },
                        { text: 'Try Again', onPress: handleAllowLocation },
                    ]
                );
            }
        } catch (error) {
            console.error('Error requesting location permission:', error);
            Alert.alert(
                'Error',
                'Failed to request location permission. Please enter your location manually.',
                [{ text: 'OK', onPress: onManualEntry }]
            );
        }
    };

    return (
        <Modal
            visible={visible}
            transparent
            animationType="slide"
            onRequestClose={onClose}
        >
            <View style={styles.overlay}>
                <View style={styles.modal}>
                    <Text style={styles.title}>Location Access Required</Text>

                    <Text style={styles.description}>
                        We need your location to connect you with attorneys who can help in your area.
                        This helps us determine the correct court jurisdiction for your case.
                    </Text>

                    <Text style={styles.subtitle}>Why we need location:</Text>
                    <Text style={styles.bulletPoint}>• Find attorneys admitted to your local federal court</Text>
                    <Text style={styles.bulletPoint}>• Ensure proper legal jurisdiction</Text>
                    <Text style={styles.bulletPoint}>• Speed up the attorney matching process</Text>

                    <Text style={styles.privacyNote}>
                        Your location is only used during emergencies and is not stored or shared.
                    </Text>

                    <View style={styles.buttonContainer}>
                        <TouchableOpacity
                            style={[styles.button, styles.primaryButton]}
                            onPress={handleAllowLocation}
                        >
                            <Text style={styles.primaryButtonText}>Allow Location</Text>
                        </TouchableOpacity>

                        <TouchableOpacity
                            style={[styles.button, styles.secondaryButton]}
                            onPress={onManualEntry}
                        >
                            <Text style={styles.secondaryButtonText}>Enter Manually</Text>
                        </TouchableOpacity>
                    </View>
                </View>
            </View>
        </Modal>
    );
};

const styles = StyleSheet.create({
    bulletPoint: {
        color: '#555',
        fontSize: 14,
        lineHeight: 20,
        marginBottom: 4,
    },
    button: {
        alignItems: 'center',
        borderRadius: 8,
        paddingHorizontal: 20,
        paddingVertical: 14,
    },
    buttonContainer: {
        gap: 12,
    },
    description: {
        color: '#333',
        fontSize: 16,
        lineHeight: 22,
        marginBottom: 20,
        textAlign: 'center',
    },
    modal: {
        backgroundColor: 'white',
        borderRadius: 12,
        elevation: 5,
        maxWidth: 400,
        padding: 24,
        shadowColor: '#000',
        shadowOffset: { width: 0, height: 2 },
        shadowOpacity: 0.25,
        shadowRadius: 4,
        width: '100%',
    },
    overlay: {
        alignItems: 'center',
        backgroundColor: 'rgba(0, 0, 0, 0.5)',
        flex: 1,
        justifyContent: 'center',
        padding: 20,
    },
    primaryButton: {
        backgroundColor: '#007AFF',
    },
    primaryButtonText: {
        color: 'white',
        fontSize: 16,
        fontWeight: '600',
    },
    privacyNote: {
        color: '#666',
        fontSize: 12,
        fontStyle: 'italic',
        marginBottom: 24,
        marginTop: 16,
        textAlign: 'center',
    },
    secondaryButton: {
        backgroundColor: 'transparent',
        borderColor: '#007AFF',
        borderWidth: 1,
    },
    secondaryButtonText: {
        color: '#007AFF',
        fontSize: 16,
        fontWeight: '600',
    },
    subtitle: {
        color: '#1a1a1a',
        fontSize: 16,
        fontWeight: '600',
        marginBottom: 8,
    },
    title: {
        color: '#1a1a1a',
        fontSize: 20,
        fontWeight: 'bold',
        marginBottom: 16,
        textAlign: 'center',
    },
});

export default LocationPermissionModal;
