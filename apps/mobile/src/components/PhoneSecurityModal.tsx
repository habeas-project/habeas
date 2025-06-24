import React from 'react';
import {
    View,
    Text,
    StyleSheet,
    TouchableOpacity,
    Modal,
    Platform,
    ScrollView,
} from 'react-native';

interface PhoneSecurityModalProps {
    visible: boolean;
    onClose: () => void;
    onConfirm: () => void;
}

const PhoneSecurityModal: React.FC<PhoneSecurityModalProps> = ({
    visible,
    onClose,
    onConfirm,
}) => {
    const isIOS = Platform.OS === 'ios';

    const getSecurityInstructions = () => {
        if (isIOS) {
            return {
                title: 'Secure Your iPhone',
                subtitle: 'Important: Use Passcode, Not Face ID or Touch ID',
                instructions: [
                    {
                        step: '1. Lock your phone immediately',
                        detail: 'Press the side button or power button to lock your screen now.',
                    },
                    {
                        step: '2. Disable biometric unlock temporarily',
                        detail: 'When you unlock next, use your 6-digit passcode instead of Face ID or Touch ID.',
                    },
                    {
                        step: '3. Multiple failed biometric attempts',
                        detail: 'If detained, intentionally fail Face ID/Touch ID 5 times to force passcode requirement.',
                    },
                    {
                        step: '4. Know your rights',
                        detail: 'Police cannot force you to provide your passcode, but they may be able to use your face or fingerprint.',
                    },
                ],
                warningText: 'Constitutional Protection: The 5th Amendment protects your passcode as "testimony." Biometrics have less legal protection.',
            };
        } else {
            return {
                title: 'Secure Your Android Phone',
                subtitle: 'Important: Use PIN/Password, Not Fingerprint or Face Unlock',
                instructions: [
                    {
                        step: '1. Lock your phone immediately',
                        detail: 'Press the power button to lock your screen now.',
                    },
                    {
                        step: '2. Disable biometric unlock temporarily',
                        detail: 'When you unlock next, use your PIN or password instead of fingerprint or face unlock.',
                    },
                    {
                        step: '3. Force PIN requirement',
                        detail: 'If detained, restart your phone (hold power + volume down) to require PIN on next unlock.',
                    },
                    {
                        step: '4. Know your rights',
                        detail: 'Police cannot force you to provide your PIN/password, but they may be able to use your fingerprint or face.',
                    },
                ],
                warningText: 'Constitutional Protection: The 5th Amendment protects your PIN/password as "testimony." Biometrics have less legal protection.',
            };
        }
    };

    const securityInfo = getSecurityInstructions();

    return (
        <Modal
            visible={visible}
            animationType="slide"
            presentationStyle="pageSheet"
            onRequestClose={onClose}
        >
            <View style={styles.container}>
                <ScrollView style={styles.scrollContainer} showsVerticalScrollIndicator={false}>
                    {/* Header */}
                    <View style={styles.header}>
                        <Text style={styles.title}>{securityInfo.title}</Text>
                        <Text style={styles.subtitle}>{securityInfo.subtitle}</Text>
                    </View>

                    {/* Emergency Status */}
                    <View style={styles.statusContainer}>
                        <Text style={styles.statusIcon}>🚨</Text>
                        <Text style={styles.statusText}>Emergency activated - Legal help is being coordinated</Text>
                    </View>

                    {/* Instructions */}
                    <View style={styles.instructionsContainer}>
                        <Text style={styles.instructionsTitle}>Follow these steps immediately:</Text>

                        {securityInfo.instructions.map((instruction, index) => (
                            <View key={index} style={styles.instructionItem}>
                                <View style={styles.stepHeader}>
                                    <Text style={styles.stepNumber}>{instruction.step}</Text>
                                </View>
                                <Text style={styles.stepDetail}>{instruction.detail}</Text>
                            </View>
                        ))}
                    </View>

                    {/* Warning */}
                    <View style={styles.warningContainer}>
                        <Text style={styles.warningIcon}>⚖️</Text>
                        <Text style={styles.warningTitle}>Legal Protection</Text>
                        <Text style={styles.warningText}>{securityInfo.warningText}</Text>
                    </View>

                    {/* Additional Tips */}
                    <View style={styles.tipsContainer}>
                        <Text style={styles.tipsTitle}>Additional Safety Tips:</Text>
                        <View style={styles.tipItem}>
                            <Text style={styles.tipBullet}>•</Text>
                            <Text style={styles.tipText}>
                                Keep your phone locked and silent during detention
                            </Text>
                        </View>
                        <View style={styles.tipItem}>
                            <Text style={styles.tipBullet}>•</Text>
                            <Text style={styles.tipText}>
                                Do not unlock your phone if asked - ask for your attorney
                            </Text>
                        </View>
                        <View style={styles.tipItem}>
                            <Text style={styles.tipBullet}>•</Text>
                            <Text style={styles.tipText}>
                                Your emergency contacts and attorney have been notified automatically
                            </Text>
                        </View>
                    </View>
                </ScrollView>

                {/* Actions */}
                <View style={styles.actionsContainer}>
                    <TouchableOpacity style={styles.lockButton} onPress={onConfirm}>
                        <Text style={styles.lockButtonText}>✓ I&apos;ve Secured My Phone</Text>
                    </TouchableOpacity>

                    <TouchableOpacity style={styles.laterButton} onPress={onClose}>
                        <Text style={styles.laterButtonText}>I&apos;ll Do This Later</Text>
                    </TouchableOpacity>
                </View>
            </View>
        </Modal>
    );
};

const styles = StyleSheet.create({
    actionsContainer: {
        borderTopColor: '#e2e8f0',
        borderTopWidth: 1,
        paddingHorizontal: 24,
        paddingVertical: 20,
    },
    container: {
        backgroundColor: '#ffffff',
        flex: 1,
    },
    header: {
        alignItems: 'center',
        paddingBottom: 24,
        paddingTop: 40,
    },
    instructionItem: {
        backgroundColor: '#f7fafc',
        borderColor: '#e2e8f0',
        borderRadius: 12,
        borderWidth: 1,
        marginBottom: 16,
        padding: 16,
    },
    instructionsContainer: {
        marginBottom: 32,
    },
    instructionsTitle: {
        color: '#2d3748',
        fontSize: 18,
        fontWeight: '600',
        marginBottom: 16,
    },
    laterButton: {
        alignItems: 'center',
        backgroundColor: 'transparent',
        borderColor: '#cbd5e0',
        borderRadius: 12,
        borderWidth: 1,
        paddingVertical: 16,
    },
    laterButtonText: {
        color: '#4a5568',
        fontSize: 16,
        fontWeight: '500',
    },
    lockButton: {
        alignItems: 'center',
        backgroundColor: '#38a169',
        borderRadius: 12,
        marginBottom: 12,
        paddingVertical: 16,
    },
    lockButtonText: {
        color: '#ffffff',
        fontSize: 16,
        fontWeight: '600',
    },
    scrollContainer: {
        flex: 1,
        paddingHorizontal: 24,
    },
    statusContainer: {
        alignItems: 'center',
        backgroundColor: '#fed7d7',
        borderColor: '#fc8181',
        borderRadius: 12,
        borderWidth: 1,
        marginBottom: 32,
        paddingVertical: 16,
    },
    statusIcon: {
        fontSize: 32,
        marginBottom: 8,
    },
    statusText: {
        color: '#c53030',
        fontSize: 16,
        fontWeight: '600',
        textAlign: 'center',
    },
    stepDetail: {
        color: '#4a5568',
        fontSize: 15,
        lineHeight: 22,
    },
    stepHeader: {
        marginBottom: 8,
    },
    stepNumber: {
        color: '#3182ce',
        fontSize: 16,
        fontWeight: '700',
    },
    subtitle: {
        color: '#744210',
        fontSize: 16,
        fontWeight: '600',
        textAlign: 'center',
    },
    tipBullet: {
        color: '#3182ce',
        fontSize: 16,
        fontWeight: '600',
        marginRight: 8,
        marginTop: 2,
    },
    tipItem: {
        alignItems: 'flex-start',
        flexDirection: 'row',
        marginBottom: 8,
    },
    tipText: {
        color: '#4a5568',
        flex: 1,
        fontSize: 14,
        lineHeight: 20,
    },
    tipsContainer: {
        marginBottom: 32,
    },
    tipsTitle: {
        color: '#2d3748',
        fontSize: 16,
        fontWeight: '600',
        marginBottom: 12,
    },
    title: {
        color: '#c53030',
        fontSize: 24,
        fontWeight: '700',
        marginBottom: 8,
        textAlign: 'center',
    },
    warningContainer: {
        alignItems: 'center',
        backgroundColor: '#fffaf0',
        borderColor: '#fed7aa',
        borderRadius: 12,
        borderWidth: 1,
        marginBottom: 32,
        padding: 20,
    },
    warningIcon: {
        fontSize: 24,
        marginBottom: 8,
    },
    warningText: {
        color: '#9c4221',
        fontSize: 14,
        lineHeight: 20,
        textAlign: 'center',
    },
    warningTitle: {
        color: '#c05621',
        fontSize: 16,
        fontWeight: '600',
        marginBottom: 8,
        textAlign: 'center',
    },
});

export default PhoneSecurityModal;
