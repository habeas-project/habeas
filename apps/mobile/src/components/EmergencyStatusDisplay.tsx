import React, { useEffect, useState } from 'react';
import {
    View,
    Text,
    StyleSheet,
    TouchableOpacity,
    ActivityIndicator,
    Animated,
    Linking,
    Alert,
    AccessibilityInfo,
} from 'react-native';
import { getEmergencyCaseStatus, pollEmergencyCaseStatus, EmergencyStatusUpdate } from '../api/client';

interface EmergencyStatusDisplayProps {
    caseId?: number;
    onDeactivate?: () => void;
}

const EmergencyStatusDisplay: React.FC<EmergencyStatusDisplayProps> = ({
    caseId,
    onDeactivate,
}) => {
    const [caseStatus, setCaseStatus] = useState<EmergencyStatusUpdate | null>(null);
    const [isLoading, setIsLoading] = useState(true);
    const [isPolling, setIsPolling] = useState(false);
    const [estimatedResponseTime, setEstimatedResponseTime] = useState<string>('');
    const [pulseAnimation] = useState(new Animated.Value(1));

    useEffect(() => {
        if (caseId) {
            loadCaseStatus();
            startPolling();
            calculateEstimatedResponseTime();
        }
    }, [caseId]);

    // Accessibility announcement for status changes
    useEffect(() => {
        if (caseStatus) {
            const message = getAccessibilityMessage(caseStatus.status);
            AccessibilityInfo.announceForAccessibility(message);
        }
    }, [caseStatus?.status]);

    // Pulse animation for active cases
    useEffect(() => {
        if (caseStatus?.status === 'active') {
            const pulse = () => {
                Animated.sequence([
                    Animated.timing(pulseAnimation, {
                        toValue: 1.2,
                        duration: 1000,
                        useNativeDriver: true,
                    }),
                    Animated.timing(pulseAnimation, {
                        toValue: 1,
                        duration: 1000,
                        useNativeDriver: true,
                    }),
                ]).start(() => pulse());
            };
            pulse();
        }
    }, [caseStatus?.status, pulseAnimation]);

    const loadCaseStatus = async () => {
        if (!caseId) return;

        try {
            const status = await getEmergencyCaseStatus(caseId);
            setCaseStatus(status);
        } catch (error) {
            console.error('Failed to load case status:', error);
        } finally {
            setIsLoading(false);
        }
    };

    const startPolling = () => {
        if (!caseId || isPolling) return;

        setIsPolling(true);
        pollEmergencyCaseStatus(
            caseId,
            (status: EmergencyStatusUpdate) => {
                setCaseStatus(status);

                // Stop polling if case is resolved or attorney assigned
                if (status.status === 'attorney_assigned' ||
                    status.status === 'resolved' ||
                    status.status === 'deactivated') {
                    setIsPolling(false);
                }
            },
            30000, // Poll every 30 seconds
            3600000 // Stop after 1 hour
        );
    };

    const calculateEstimatedResponseTime = () => {
        const now = new Date();
        const hour = now.getHours();

        // Business hours: 9 AM - 5 PM
        if (hour >= 9 && hour < 17) {
            setEstimatedResponseTime('15-30 minutes');
        } else if (hour >= 17 && hour < 22) {
            setEstimatedResponseTime('30-60 minutes');
        } else {
            setEstimatedResponseTime('1-2 hours');
        }
    };

    const getStatusIcon = (status: string) => {
        switch (status) {
            case 'active':
                return '📡';
            case 'attorney_assigned':
                return '⚖️';
            case 'resolved':
                return '✅';
            case 'deactivated':
                return '⏹️';
            default:
                return '🚨';
        }
    };

    const getStatusColor = (status: string) => {
        switch (status) {
            case 'active':
                return '#ea580c'; // More urgent orange
            case 'attorney_assigned':
                return '#059669';
            case 'resolved':
                return '#047857';
            case 'deactivated':
                return '#6b7280';
            default:
                return '#dc2626'; // Urgent red
        }
    };

    const getStatusMessage = (status: string) => {
        switch (status) {
            case 'active':
                return 'EMERGENCY ACTIVE - Attorneys Notified';
            case 'attorney_assigned':
                return `Attorney Responding: ${caseStatus?.assigned_attorney_name}`;
            case 'resolved':
                return 'Emergency Resolved';
            case 'deactivated':
                return 'Emergency Deactivated';
            default:
                return 'Emergency Processing';
        }
    };

    const getAccessibilityMessage = (status: string) => {
        switch (status) {
            case 'active':
                return 'Emergency is active. Attorneys have been notified and are reviewing your case.';
            case 'attorney_assigned':
                return `An attorney has accepted your case. They will contact you soon.`;
            case 'resolved':
                return 'Your emergency case has been resolved.';
            case 'deactivated':
                return 'Emergency has been deactivated.';
            default:
                return 'Emergency status updated.';
        }
    };

    const formatTimestamp = (timestamp: string) => {
        const date = new Date(timestamp);
        return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    };

    const formatTimeElapsed = () => {
        if (!caseStatus?.created_at) return '';

        const created = new Date(caseStatus.created_at);
        const now = new Date();
        const diffMs = now.getTime() - created.getTime();
        const diffMins = Math.floor(diffMs / 60000);

        if (diffMins < 60) {
            return `${diffMins} minutes ago`;
        } else {
            const diffHours = Math.floor(diffMins / 60);
            return `${diffHours} hour${diffHours > 1 ? 's' : ''} ago`;
        }
    };

    const handleCallAttorney = () => {
        // This would typically come from the API response
        const attorneyPhone = '+1-555-ATTORNEY'; // Placeholder

        Alert.alert(
            'Call Attorney',
            `Call ${caseStatus?.assigned_attorney_name} at ${attorneyPhone}?`,
            [
                { text: 'Cancel', style: 'cancel' },
                {
                    text: 'Call',
                    onPress: () => Linking.openURL(`tel:${attorneyPhone}`)
                }
            ]
        );
    };

    if (isLoading) {
        return (
            <View style={styles.container}>
                <ActivityIndicator size="large" color="#dc2626" />
                <Text style={styles.loadingText}>Loading emergency status...</Text>
            </View>
        );
    }

    if (!caseStatus) {
        return (
            <View style={styles.container}>
                <Text style={styles.errorText}>Unable to load emergency status</Text>
                <Text style={styles.errorSubtext}>Please check your connection and try again</Text>
            </View>
        );
    }

    const isUrgent = caseStatus.status === 'active';

    return (
        <View style={[styles.container, isUrgent && styles.urgentContainer]}>
            {/* Urgent Banner */}
            {isUrgent && (
                <Animated.View
                    style={[styles.urgentBanner, { transform: [{ scale: pulseAnimation }] }]}
                    accessibilityRole="alert"
                    accessibilityLiveRegion="assertive"
                >
                    <Text style={styles.urgentBannerText}>🚨 EMERGENCY ACTIVE 🚨</Text>
                </Animated.View>
            )}

            {/* Status Header */}
            <View style={[styles.statusHeader, { borderColor: getStatusColor(caseStatus.status) }]}>
                <Text style={styles.statusIcon}>{getStatusIcon(caseStatus.status)}</Text>
                <View style={styles.statusTextContainer}>
                    <Text
                        style={[styles.statusTitle, { color: getStatusColor(caseStatus.status) }]}
                        accessibilityRole="header"
                    >
                        {getStatusMessage(caseStatus.status)}
                    </Text>
                    <Text style={styles.caseId}>Case #{caseStatus.case_id}</Text>
                    <Text style={styles.timestamp}>
                        Started: {formatTimeElapsed()}
                    </Text>
                    <Text style={styles.lastUpdated}>
                        Last updated: {formatTimestamp(caseStatus.last_updated)}
                    </Text>
                </View>
                {isPolling && (
                    <ActivityIndicator size="small" color={getStatusColor(caseStatus.status)} />
                )}
            </View>

            {/* Critical Information for Active Cases */}
            {isUrgent && (
                <View style={styles.criticalInfoContainer}>
                    <Text style={styles.criticalInfoTitle}>⏱️ Next Steps</Text>
                    <Text style={styles.criticalInfoText}>
                        • Keep your phone charged and accessible{'\n'}
                        • Stay in a safe location if possible{'\n'}
                        • Expected attorney response: {estimatedResponseTime}{'\n'}
                        • Emergency contacts have been notified
                    </Text>
                </View>
            )}

            {/* Status Details */}
            <View style={styles.detailsContainer}>
                <Text style={styles.message} accessibilityLabel={`Status message: ${caseStatus.message}`}>
                    {caseStatus.message}
                </Text>

                {/* Court Information */}
                {caseStatus.assigned_court_name && (
                    <View style={styles.courtInfo}>
                        <Text style={styles.sectionTitle}>🏛️ Court Jurisdiction</Text>
                        <Text style={styles.courtName}>{caseStatus.assigned_court_name}</Text>
                        <Text style={styles.courtDetails}>
                            District attorneys in this jurisdiction have been notified
                        </Text>
                        {isUrgent && (
                            <Text style={styles.responseTime}>
                                Expected response time: {estimatedResponseTime}
                            </Text>
                        )}
                    </View>
                )}

                {/* Attorney Information */}
                {caseStatus.assigned_attorney_name && (
                    <View style={styles.attorneyInfo}>
                        <Text style={styles.sectionTitle}>👨‍💼 Assigned Attorney</Text>
                        <Text style={styles.attorneyName}>{caseStatus.assigned_attorney_name}</Text>
                        <Text style={styles.attorneyDetails}>
                            Licensed to practice in your district court
                        </Text>
                        <TouchableOpacity
                            style={styles.contactButton}
                            onPress={handleCallAttorney}
                            accessibilityRole="button"
                            accessibilityLabel={`Call attorney ${caseStatus.assigned_attorney_name}`}
                        >
                            <Text style={styles.contactButtonText}>📞 Contact Attorney</Text>
                        </TouchableOpacity>
                    </View>
                )}
            </View>

            {/* Enhanced Progress Indicators */}
            <View style={styles.progressContainer}>
                <Text style={styles.progressTitle}>Case Progress</Text>

                <View style={styles.progressSteps}>
                    <View style={styles.progressStep}>
                        <View style={[styles.progressDot, styles.progressDotComplete]} />
                        <Text style={styles.progressLabel}>Emergency Posted</Text>
                        <Text style={styles.progressTime}>{formatTimeElapsed()}</Text>
                    </View>

                    <View style={[
                        styles.progressLine,
                        caseStatus.status === 'attorney_assigned' && styles.progressLineComplete
                    ]} />

                    <View style={styles.progressStep}>
                        <View style={[
                            styles.progressDot,
                            caseStatus.status === 'attorney_assigned' || caseStatus.status === 'resolved'
                                ? styles.progressDotComplete
                                : styles.progressDotPending
                        ]} />
                        <Text style={styles.progressLabel}>Attorney Assigned</Text>
                        {caseStatus.status === 'attorney_assigned' && (
                            <Text style={styles.progressTime}>Just now</Text>
                        )}
                    </View>

                    <View style={[
                        styles.progressLine,
                        caseStatus.status === 'resolved' && styles.progressLineComplete
                    ]} />

                    <View style={styles.progressStep}>
                        <View style={[
                            styles.progressDot,
                            caseStatus.status === 'resolved' ? styles.progressDotComplete : styles.progressDotPending
                        ]} />
                        <Text style={styles.progressLabel}>Case Resolved</Text>
                    </View>
                </View>
            </View>

            {/* Actions */}
            {caseStatus.status === 'active' && onDeactivate && (
                <TouchableOpacity
                    style={styles.deactivateButton}
                    onPress={onDeactivate}
                    accessibilityRole="button"
                    accessibilityLabel="Deactivate emergency"
                    accessibilityHint="This will cancel the emergency and stop attorney notifications"
                >
                    <Text style={styles.deactivateButtonText}>⏹️ Deactivate Emergency</Text>
                </TouchableOpacity>
            )}

            {/* Enhanced Help Text */}
            <View style={[styles.helpContainer, isUrgent && styles.urgentHelpContainer]}>
                <Text style={[styles.helpText, isUrgent && styles.urgentHelpText]}>
                    {caseStatus.status === 'active'
                        ? `🔔 ${caseStatus.attorneys_notified_count || 'Multiple'} attorneys in your district court have been notified. You will receive an update when someone accepts your case. Keep your phone accessible.`
                        : caseStatus.status === 'attorney_assigned'
                            ? '📞 An attorney has accepted your case and will contact you or your emergency contacts within the next 30 minutes. Please keep your phone accessible.'
                            : '✅ Your emergency case has been processed. If you need additional assistance, you can create a new emergency case.'
                    }
                </Text>

                {isUrgent && (
                    <Text style={styles.emergencyTip}>
                        💡 Tip: If detained, you have the right to remain silent and request an attorney. Show this screen to officers if needed.
                    </Text>
                )}
            </View>
        </View>
    );
};

const styles = StyleSheet.create({
    attorneyDetails: {
        color: '#6b7280',
        fontSize: 14,
        lineHeight: 20,
    },
    attorneyInfo: {
        backgroundColor: '#ecfdf5',
        borderRadius: 8,
        padding: 12,
    },

    attorneyName: {
        color: '#047857',
        fontSize: 14,
        fontWeight: '600',
    },
    caseId: {
        color: '#6b7280',
        fontSize: 14,
        fontWeight: '500',
    },
    contactButton: {
        backgroundColor: '#059669',
        borderRadius: 8,
        marginTop: 8,
        paddingVertical: 12,
    },
    contactButtonText: {
        color: '#ffffff',
        fontSize: 14,
        fontWeight: '600',
        textAlign: 'center',
    },
    container: {
        backgroundColor: '#ffffff',
        borderColor: '#e2e8f0',
        borderRadius: 16,
        borderWidth: 1,
        marginVertical: 20,
        padding: 20,
        width: '100%',
    },
    courtDetails: {
        color: '#6b7280',
        fontSize: 14,
        lineHeight: 20,
    },
    courtInfo: {
        backgroundColor: '#f9fafb',
        borderRadius: 8,
        marginBottom: 8,
        padding: 12,
    },

    courtName: {
        color: '#111827',
        fontSize: 14,
        fontWeight: '600',
    },
    criticalInfoContainer: {
        backgroundColor: '#f9fafb',
        borderRadius: 8,
        marginBottom: 20,
        padding: 12,
    },
    criticalInfoText: {
        color: '#6b7280',
        fontSize: 14,
        lineHeight: 20,
    },
    criticalInfoTitle: {
        color: '#111827',
        fontSize: 18,
        fontWeight: '600',
        marginBottom: 8,
    },
    deactivateButton: {
        backgroundColor: '#dc2626',
        borderRadius: 8,
        marginBottom: 16,
        paddingVertical: 12,
    },
    deactivateButtonText: {
        color: '#ffffff',
        fontSize: 14,
        fontWeight: '600',
        textAlign: 'center',
    },
    detailsContainer: {
        marginBottom: 20,
    },
    emergencyTip: {
        color: '#6b7280',
        fontSize: 12,
        marginTop: 8,
    },
    errorSubtext: {
        color: '#6b7280',
        fontSize: 12,
        textAlign: 'center',
    },
    errorText: {
        color: '#dc2626',
        fontSize: 14,
        textAlign: 'center',
    },
    helpContainer: {
        backgroundColor: '#f0f9ff',
        borderColor: '#bae6fd',
        borderRadius: 8,
        borderWidth: 1,
        padding: 12,
    },
    helpText: {
        color: '#0369a1',
        fontSize: 13,
        lineHeight: 18,
        textAlign: 'center',
    },
    lastUpdated: {
        color: '#9ca3af',
        fontSize: 12,
        marginTop: 2,
    },
    loadingText: {
        color: '#6b7280',
        fontSize: 14,
        marginTop: 12,
        textAlign: 'center',
    },
    message: {
        color: '#374151',
        fontSize: 14,
        lineHeight: 20,
        marginBottom: 12,
    },
    progressContainer: {
        alignItems: 'center',
        flexDirection: 'row',
        justifyContent: 'space-between',
        marginBottom: 20,
    },
    progressDot: {
        borderRadius: 8,
        height: 16,
        marginBottom: 8,
        width: 16,
    },
    progressDotComplete: {
        backgroundColor: '#10b981',
    },
    progressDotPending: {
        backgroundColor: '#d1d5db',
    },
    progressLabel: {
        color: '#6b7280',
        fontSize: 10,
        textAlign: 'center',
    },
    progressLine: {
        backgroundColor: '#d1d5db',
        flex: 2,
        height: 2,
        marginHorizontal: 8,
    },
    progressLineComplete: {
        backgroundColor: '#10b981',
    },
    progressStep: {
        alignItems: 'center',
        flex: 1,
    },
    progressSteps: {
        alignItems: 'center',
        flexDirection: 'row',
        justifyContent: 'space-between',
        width: '100%',
    },
    progressTime: {
        color: '#6b7280',
        fontSize: 12,
        marginTop: 2,
    },
    progressTitle: {
        color: '#6b7280',
        fontSize: 18,
        fontWeight: '600',
        marginBottom: 12,
    },
    responseTime: {
        color: '#047857',
        fontSize: 14,
        fontWeight: '600',
        marginTop: 8,
    },
    sectionTitle: {
        color: '#111827',
        fontSize: 18,
        fontWeight: '600',
        marginBottom: 8,
    },
    statusHeader: {
        alignItems: 'center',
        borderBottomWidth: 1,
        borderRadius: 12,
        flexDirection: 'row',
        marginBottom: 16,
        paddingBottom: 16,
    },
    statusIcon: {
        fontSize: 32,
        marginRight: 12,
    },
    statusTextContainer: {
        flex: 1,
    },
    statusTitle: {
        fontSize: 18,
        fontWeight: '600',
        marginBottom: 4,
    },
    timestamp: {
        color: '#9ca3af',
        fontSize: 12,
        marginTop: 2,
    },
    urgentBanner: {
        backgroundColor: '#dc2626',
        borderRadius: 8,
        marginBottom: 20,
        padding: 12,
    },
    urgentBannerText: {
        color: '#ffffff',
        fontSize: 18,
        fontWeight: '600',
        textAlign: 'center',
    },
    urgentContainer: {
        backgroundColor: '#fef2f2',
    },
    urgentHelpContainer: {
        backgroundColor: '#fef2f2',
    },
    urgentHelpText: {
        color: '#dc2626',
    },
});

export default EmergencyStatusDisplay;
