import React, { useEffect, useState } from 'react';
import {
    View,
    Text,
    StyleSheet,
    ScrollView,
    Switch,
    TextInput,
    TouchableOpacity,
    Alert,
    ActivityIndicator,
    KeyboardAvoidingView,
    Platform,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useNavigation } from '@react-navigation/native';
import { NativeStackNavigationProp } from '@react-navigation/native-stack';

import { useAuth } from '../contexts/AuthContext';
import { RootStackParamList } from '../App';
import {
    getAttorneyNotificationPreferences,
    updateAttorneyNotificationPreferences,
    AttorneyNotificationPreferencesRequest,
} from '../api/client';

// Navigation type
type NotificationPreferencesNavigationProp = NativeStackNavigationProp<
    RootStackParamList,
    'NotificationPreferences'
>;

const NotificationPreferencesScreen: React.FC = () => {
    const navigation = useNavigation<NotificationPreferencesNavigationProp>();
    const { user, isAttorney } = useAuth();
    const [loading, setLoading] = useState(true);
    const [saving, setSaving] = useState(false);
    const [hasChanges, setHasChanges] = useState(false);

    // Notification preferences state
    const [preferences, setPreferences] = useState<AttorneyNotificationPreferencesRequest>({
        email_enabled: true,
        sms_enabled: true,
        push_enabled: true,
        sms_phone_number: '',
        daily_digest_enabled: true,
        escalated_notifications_enabled: true,
    });

    // Store original preferences to detect changes
    const [originalPreferences, setOriginalPreferences] = useState<AttorneyNotificationPreferencesRequest | null>(null);

    // Redirect non-attorneys
    useEffect(() => {
        if (!isAttorney()) {
            Alert.alert(
                'Access Denied',
                'This section is only available to attorneys.',
                [{ text: 'OK', onPress: () => navigation.goBack() }]
            );
            return;
        }
    }, [isAttorney, navigation]);

    // Load current preferences
    useEffect(() => {
        const loadPreferences = async () => {
            if (!user?.attorney_id) {
                console.error('No attorney ID found');
                setLoading(false);
                return;
            }

            try {
                const response = await getAttorneyNotificationPreferences(user.attorney_id);
                const prefs: AttorneyNotificationPreferencesRequest = {
                    email_enabled: response.email_enabled,
                    sms_enabled: response.sms_enabled,
                    push_enabled: response.push_enabled,
                    sms_phone_number: response.sms_phone_number || '',
                    daily_digest_enabled: response.daily_digest_enabled,
                    escalated_notifications_enabled: response.escalated_notifications_enabled,
                };
                setPreferences(prefs);
                setOriginalPreferences(prefs);
            } catch (error) {
                console.error('Failed to load notification preferences:', error);
                Alert.alert(
                    'Error',
                    'Failed to load notification preferences. Please try again.',
                    [{ text: 'OK' }]
                );
            } finally {
                setLoading(false);
            }
        };

        loadPreferences();
    }, [user?.attorney_id]);

    // Check if preferences have changed
    useEffect(() => {
        if (!originalPreferences) return;

        const changed = JSON.stringify(preferences) !== JSON.stringify(originalPreferences);
        setHasChanges(changed);
    }, [preferences, originalPreferences]);

    // Handle preference changes
    const handleToggle = (key: keyof AttorneyNotificationPreferencesRequest, value: boolean) => {
        setPreferences(prev => ({ ...prev, [key]: value }));
    };

    const handlePhoneChange = (phone: string) => {
        setPreferences(prev => ({ ...prev, sms_phone_number: phone }));
    };

    // Save preferences
    const handleSave = async () => {
        if (!user?.attorney_id) {
            Alert.alert('Error', 'Attorney ID not found');
            return;
        }

        // Validate phone number if SMS is enabled
        if (preferences.sms_enabled && !preferences.sms_phone_number?.trim()) {
            Alert.alert(
                'Phone Number Required',
                'Please enter a phone number for SMS notifications or disable SMS notifications.',
                [{ text: 'OK' }]
            );
            return;
        }

        setSaving(true);
        try {
            await updateAttorneyNotificationPreferences(user.attorney_id, preferences);

            // Update original preferences to reflect saved state
            setOriginalPreferences(preferences);
            setHasChanges(false);

            Alert.alert(
                'Success',
                'Your notification preferences have been saved.',
                [{ text: 'OK' }]
            );
        } catch (error) {
            console.error('Failed to save notification preferences:', error);
            Alert.alert(
                'Error',
                'Failed to save notification preferences. Please try again.',
                [{ text: 'OK' }]
            );
        } finally {
            setSaving(false);
        }
    };

    // Reset to original preferences
    const handleReset = () => {
        if (!originalPreferences) return;

        Alert.alert(
            'Reset Changes',
            'Are you sure you want to discard your changes?',
            [
                { text: 'Cancel', style: 'cancel' },
                {
                    text: 'Reset',
                    style: 'destructive',
                    onPress: () => {
                        setPreferences(originalPreferences);
                        setHasChanges(false);
                    },
                },
            ]
        );
    };

    if (loading) {
        return (
            <SafeAreaView style={styles.container}>
                <View style={styles.loadingContainer}>
                    <ActivityIndicator size="large" color="#007AFF" />
                    <Text style={styles.loadingText}>Loading notification preferences...</Text>
                </View>
            </SafeAreaView>
        );
    }

    return (
        <SafeAreaView style={styles.container}>
            <KeyboardAvoidingView
                style={styles.keyboardAvoidingView}
                behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
            >
                <ScrollView style={styles.scrollView} showsVerticalScrollIndicator={false}>
                    {/* Header */}
                    <View style={styles.header}>
                        <Text style={styles.title}>Notification Preferences</Text>
                        <Text style={styles.subtitle}>
                            Manage how you receive emergency case notifications
                        </Text>
                    </View>

                    {/* Notification Channels */}
                    <View style={styles.section}>
                        <Text style={styles.sectionTitle}>Notification Channels</Text>
                        <Text style={styles.sectionDescription}>
                            Choose how you want to receive notifications about new emergency cases
                        </Text>

                        <View style={styles.preferenceItem}>
                            <View style={styles.preferenceContent}>
                                <Text style={styles.preferenceTitle}>Email Notifications</Text>
                                <Text style={styles.preferenceDescription}>
                                    Receive detailed case information via email
                                </Text>
                            </View>
                            <Switch
                                value={preferences.email_enabled}
                                onValueChange={(value) => handleToggle('email_enabled', value)}
                                trackColor={{ false: '#767577', true: '#007AFF' }}
                                thumbColor={preferences.email_enabled ? '#FFFFFF' : '#f4f3f4'}
                            />
                        </View>

                        <View style={styles.preferenceItem}>
                            <View style={styles.preferenceContent}>
                                <Text style={styles.preferenceTitle}>SMS Notifications</Text>
                                <Text style={styles.preferenceDescription}>
                                    Receive urgent case alerts via text message
                                </Text>
                            </View>
                            <Switch
                                value={preferences.sms_enabled}
                                onValueChange={(value) => handleToggle('sms_enabled', value)}
                                trackColor={{ false: '#767577', true: '#007AFF' }}
                                thumbColor={preferences.sms_enabled ? '#FFFFFF' : '#f4f3f4'}
                            />
                        </View>

                        {preferences.sms_enabled && (
                            <View style={styles.phoneNumberContainer}>
                                <Text style={styles.phoneNumberLabel}>SMS Phone Number</Text>
                                <TextInput
                                    style={styles.phoneNumberInput}
                                    value={preferences.sms_phone_number}
                                    onChangeText={handlePhoneChange}
                                    placeholder="Enter phone number (e.g., +1234567890)"
                                    placeholderTextColor="#999"
                                    keyboardType="phone-pad"
                                    autoCapitalize="none"
                                    autoCorrect={false}
                                />
                            </View>
                        )}

                        <View style={styles.preferenceItem}>
                            <View style={styles.preferenceContent}>
                                <Text style={styles.preferenceTitle}>Push Notifications</Text>
                                <Text style={styles.preferenceDescription}>
                                    Receive instant notifications on your mobile device
                                </Text>
                            </View>
                            <Switch
                                value={preferences.push_enabled}
                                onValueChange={(value) => handleToggle('push_enabled', value)}
                                trackColor={{ false: '#767577', true: '#007AFF' }}
                                thumbColor={preferences.push_enabled ? '#FFFFFF' : '#f4f3f4'}
                            />
                        </View>
                    </View>

                    {/* Notification Timing */}
                    <View style={styles.section}>
                        <Text style={styles.sectionTitle}>Notification Timing</Text>
                        <Text style={styles.sectionDescription}>
                            Control when and how often you receive notifications
                        </Text>

                        <View style={styles.preferenceItem}>
                            <View style={styles.preferenceContent}>
                                <Text style={styles.preferenceTitle}>Daily Digest</Text>
                                <Text style={styles.preferenceDescription}>
                                    Receive a daily summary of unassigned cases
                                </Text>
                            </View>
                            <Switch
                                value={preferences.daily_digest_enabled}
                                onValueChange={(value) => handleToggle('daily_digest_enabled', value)}
                                trackColor={{ false: '#767577', true: '#007AFF' }}
                                thumbColor={preferences.daily_digest_enabled ? '#FFFFFF' : '#f4f3f4'}
                            />
                        </View>

                        <View style={styles.preferenceItem}>
                            <View style={styles.preferenceContent}>
                                <Text style={styles.preferenceTitle}>Escalated Notifications</Text>
                                <Text style={styles.preferenceDescription}>
                                    Receive follow-up notifications for unaccepted cases after 1 hour
                                </Text>
                            </View>
                            <Switch
                                value={preferences.escalated_notifications_enabled}
                                onValueChange={(value) => handleToggle('escalated_notifications_enabled', value)}
                                trackColor={{ false: '#767577', true: '#007AFF' }}
                                thumbColor={preferences.escalated_notifications_enabled ? '#FFFFFF' : '#f4f3f4'}
                            />
                        </View>
                    </View>

                    {/* Information Section */}
                    <View style={styles.infoSection}>
                        <Text style={styles.infoTitle}>How Notifications Work</Text>
                        <Text style={styles.infoText}>
                            • <Text style={styles.infoBold}>Immediate:</Text> Receive notifications as soon as new cases are posted in your court districts
                        </Text>
                        <Text style={styles.infoText}>
                            • <Text style={styles.infoBold}>Escalated:</Text> If a case remains unaccepted after 1 hour, you&apos;ll receive a second notification
                        </Text>
                        <Text style={styles.infoText}>
                            • <Text style={styles.infoBold}>Daily Digest:</Text> Every morning, receive a summary of all unassigned cases across all districts
                        </Text>
                        <Text style={styles.infoText}>
                            • You can disable any notification type at any time
                        </Text>
                    </View>
                </ScrollView>

                {/* Action Buttons */}
                {hasChanges && (
                    <View style={styles.actionButtons}>
                        <TouchableOpacity
                            style={[styles.actionButton, styles.resetButton]}
                            onPress={handleReset}
                            disabled={saving}
                        >
                            <Text style={styles.resetButtonText}>Reset</Text>
                        </TouchableOpacity>

                        <TouchableOpacity
                            style={[styles.actionButton, styles.saveButton]}
                            onPress={handleSave}
                            disabled={saving}
                        >
                            {saving ? (
                                <ActivityIndicator size="small" color="#FFFFFF" />
                            ) : (
                                <Text style={styles.saveButtonText}>Save Changes</Text>
                            )}
                        </TouchableOpacity>
                    </View>
                )}
            </KeyboardAvoidingView>
        </SafeAreaView>
    );
};

const styles = StyleSheet.create({
    actionButton: {
        alignItems: 'center',
        borderRadius: 8,
        flex: 1,
        justifyContent: 'center',
        minHeight: 48,
        paddingVertical: 12,
    },
    actionButtons: {
        backgroundColor: '#FFFFFF',
        borderTopColor: '#e0e0e0',
        borderTopWidth: 1,
        flexDirection: 'row',
        gap: 10,
        paddingHorizontal: 20,
        paddingVertical: 15,
    },
    container: {
        backgroundColor: '#f8f9fa',
        flex: 1,
    },
    header: {
        padding: 20,
        paddingBottom: 10,
    },
    infoBold: {
        color: '#1a1a1a',
        fontWeight: '600',
    },
    infoSection: {
        backgroundColor: '#f0f7ff',
        borderColor: '#e0f0ff',
        borderRadius: 12,
        borderWidth: 1,
        marginBottom: 20,
        marginHorizontal: 20,
        padding: 20,
    },
    infoText: {
        color: '#333',
        fontSize: 14,
        lineHeight: 20,
        marginBottom: 8,
    },
    infoTitle: {
        color: '#1a1a1a',
        fontSize: 16,
        fontWeight: '600',
        marginBottom: 12,
    },
    keyboardAvoidingView: {
        flex: 1,
    },
    loadingContainer: {
        alignItems: 'center',
        flex: 1,
        justifyContent: 'center',
        padding: 20,
    },
    loadingText: {
        color: '#666',
        fontSize: 16,
        marginTop: 10,
        textAlign: 'center',
    },
    phoneNumberContainer: {
        borderTopColor: '#f0f0f0',
        borderTopWidth: 1,
        marginBottom: 10,
        marginTop: 10,
        paddingTop: 15,
    },
    phoneNumberInput: {
        backgroundColor: '#f9f9f9',
        borderColor: '#ddd',
        borderRadius: 8,
        borderWidth: 1,
        color: '#1a1a1a',
        fontSize: 16,
        padding: 12,
    },
    phoneNumberLabel: {
        color: '#1a1a1a',
        fontSize: 14,
        fontWeight: '500',
        marginBottom: 8,
    },
    preferenceContent: {
        flex: 1,
        marginRight: 15,
    },
    preferenceDescription: {
        color: '#666',
        fontSize: 14,
        lineHeight: 18,
    },
    preferenceItem: {
        alignItems: 'center',
        borderBottomColor: '#f0f0f0',
        borderBottomWidth: 1,
        flexDirection: 'row',
        paddingVertical: 15,
    },
    preferenceTitle: {
        color: '#1a1a1a',
        fontSize: 16,
        fontWeight: '500',
        marginBottom: 3,
    },
    resetButton: {
        backgroundColor: '#f5f5f5',
        borderColor: '#ddd',
        borderWidth: 1,
    },
    resetButtonText: {
        color: '#666',
        fontSize: 16,
        fontWeight: '500',
    },
    saveButton: {
        backgroundColor: '#007AFF',
    },
    saveButtonText: {
        color: '#FFFFFF',
        fontSize: 16,
        fontWeight: '600',
    },
    scrollView: {
        flex: 1,
    },
    section: {
        backgroundColor: '#FFFFFF',
        borderRadius: 12,
        elevation: 3,
        marginBottom: 20,
        marginHorizontal: 20,
        padding: 20,
        shadowColor: '#000',
        shadowOffset: { width: 0, height: 2 },
        shadowOpacity: 0.1,
        shadowRadius: 8,
    },
    sectionDescription: {
        color: '#666',
        fontSize: 14,
        lineHeight: 20,
        marginBottom: 20,
    },
    sectionTitle: {
        color: '#1a1a1a',
        fontSize: 20,
        fontWeight: '600',
        marginBottom: 5,
    },
    subtitle: {
        color: '#666',
        fontSize: 16,
        lineHeight: 22,
    },
    title: {
        color: '#1a1a1a',
        fontSize: 28,
        fontWeight: '700',
        marginBottom: 5,
    },
});

export default NotificationPreferencesScreen;
