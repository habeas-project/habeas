import React, { useState, useEffect } from 'react';
import {
    View,
    Text,
    StyleSheet,
    ScrollView,
    TouchableOpacity,
    Alert,
    RefreshControl,
    Switch,
    ActivityIndicator,
    Modal,
} from 'react-native';
import { useAuth } from '../contexts/AuthContext';

// Mock interfaces - these would typically come from the API client
interface EmergencyCase {
    id: number;
    client_name: string;
    case_type: 'self' | 'loved_one';
    location: string;
    urgency_level: 'high' | 'medium' | 'low';
    created_at: string;
    status: 'active' | 'assigned' | 'resolved';
    estimated_response_time: string;
    court_jurisdiction: string;
}

interface CoverageStats {
    district_name: string;
    total_cases_handled: number;
    average_response_time: string;
    success_rate: number;
    coverage_percentage: number;
    active_attorneys: number;
}

interface NotificationPreferences {
    email_notifications: boolean;
    sms_notifications: boolean;
    push_notifications: boolean;
    urgent_only: boolean;
    daily_digest: boolean;
    weekly_summary: boolean;
    quiet_hours_start: string;
    quiet_hours_end: string;
}

const AttorneyDashboardScreen: React.FC = () => {
    const { user, isAuthenticated } = useAuth();
    const [activeCases, setActiveCases] = useState<EmergencyCase[]>([]);
    const [recentCases, setRecentCases] = useState<EmergencyCase[]>([]);
    const [coverageStats, setCoverageStats] = useState<CoverageStats | null>(null);
    const [preferences, setPreferences] = useState<NotificationPreferences>({
        email_notifications: true,
        sms_notifications: true,
        push_notifications: true,
        urgent_only: false,
        daily_digest: true,
        weekly_summary: true,
        quiet_hours_start: '22:00',
        quiet_hours_end: '07:00',
    });
    const [isLoading, setIsLoading] = useState(true);
    const [refreshing, setRefreshing] = useState(false);
    const [showPreferences, setShowPreferences] = useState(false);
    const [showCaseDetails, setShowCaseDetails] = useState<EmergencyCase | null>(null);

    useEffect(() => {
        if (isAuthenticated && user) {
            loadDashboardData();
        }
    }, [isAuthenticated, user]);

    const loadDashboardData = async () => {
        try {
            setIsLoading(true);
            // Mock data - replace with actual API calls
            await loadActiveCases();
            await loadRecentCases();
            await loadCoverageStats();
            await loadNotificationPreferences();
        } catch (error) {
            console.error('Failed to load dashboard data:', error);
            Alert.alert('Error', 'Failed to load dashboard data');
        } finally {
            setIsLoading(false);
        }
    };

    const loadActiveCases = async () => {
        // Mock active cases
        const mockActiveCases: EmergencyCase[] = [
            {
                id: 1,
                client_name: 'Maria Rodriguez',
                case_type: 'self',
                location: 'Downtown Detention Center',
                urgency_level: 'high',
                created_at: new Date(Date.now() - 1800000).toISOString(), // 30 minutes ago
                status: 'active',
                estimated_response_time: '15-30 minutes',
                court_jurisdiction: 'Central District Court',
            },
            {
                id: 2,
                client_name: 'Ahmed Hassan',
                case_type: 'loved_one',
                location: 'Airport ICE Facility',
                urgency_level: 'high',
                created_at: new Date(Date.now() - 3600000).toISOString(), // 1 hour ago
                status: 'active',
                estimated_response_time: '30-60 minutes',
                court_jurisdiction: 'Federal Immigration Court',
            },
            {
                id: 3,
                client_name: 'Carlos Mendez',
                case_type: 'self',
                location: 'City Police Station',
                urgency_level: 'medium',
                created_at: new Date(Date.now() - 7200000).toISOString(), // 2 hours ago
                status: 'assigned',
                estimated_response_time: 'Assigned',
                court_jurisdiction: 'Municipal Court',
            },
        ];
        setActiveCases(mockActiveCases);
    };

    const loadRecentCases = async () => {
        // Mock recent cases
        const mockRecentCases: EmergencyCase[] = [
            {
                id: 4,
                client_name: 'Lisa Chen',
                case_type: 'self',
                location: 'County Jail',
                urgency_level: 'medium',
                created_at: new Date(Date.now() - 86400000).toISOString(), // 1 day ago
                status: 'resolved',
                estimated_response_time: 'Resolved',
                court_jurisdiction: 'County Court',
            },
            {
                id: 5,
                client_name: 'James Wilson',
                case_type: 'loved_one',
                location: 'Border Patrol Station',
                urgency_level: 'high',
                created_at: new Date(Date.now() - 172800000).toISOString(), // 2 days ago
                status: 'resolved',
                estimated_response_time: 'Resolved',
                court_jurisdiction: 'Federal District Court',
            },
        ];
        setRecentCases(mockRecentCases);
    };

    const loadCoverageStats = async () => {
        // Mock coverage statistics
        const mockStats: CoverageStats = {
            district_name: 'Central District',
            total_cases_handled: 47,
            average_response_time: '22 minutes',
            success_rate: 94.7,
            coverage_percentage: 87.3,
            active_attorneys: 12,
        };
        setCoverageStats(mockStats);
    };

    const loadNotificationPreferences = async () => {
        // Mock preferences loading - would typically fetch from API
        // Current preferences are already set in state
    };

    const handleAcceptCase = async (caseId: number) => {
        Alert.alert(
            'Accept Emergency Case',
            'Are you sure you want to accept this emergency case? You will be responsible for contacting the client within 30 minutes.',
            [
                { text: 'Cancel', style: 'cancel' },
                {
                    text: 'Accept Case',
                    style: 'default',
                    onPress: async () => {
                        try {
                            // API call to accept case
                            console.log('Accepting case:', caseId);

                            // Update local state
                            setActiveCases(prev =>
                                prev.map(c =>
                                    c.id === caseId
                                        ? { ...c, status: 'assigned' as const, estimated_response_time: 'Assigned' }
                                        : c
                                )
                            );

                            Alert.alert(
                                'Case Accepted',
                                'You have successfully accepted this emergency case. Please contact the client or their emergency contacts within 30 minutes.',
                                [{ text: 'OK' }]
                            );
                        } catch {
                            Alert.alert('Error', 'Failed to accept case. Please try again.');
                        }
                    }
                }
            ]
        );
    };

    const handleUpdatePreferences = async (newPreferences: NotificationPreferences) => {
        try {
            // API call to update preferences
            console.log('Updating preferences:', newPreferences);
            setPreferences(newPreferences);
            Alert.alert('Success', 'Notification preferences updated successfully');
        } catch {
            Alert.alert('Error', 'Failed to update preferences');
        }
    };

    const onRefresh = async () => {
        setRefreshing(true);
        await loadDashboardData();
        setRefreshing(false);
    };

    const formatTimeAgo = (dateString: string) => {
        const date = new Date(dateString);
        const now = new Date();
        const diffMs = now.getTime() - date.getTime();
        const diffMins = Math.floor(diffMs / 60000);

        if (diffMins < 60) {
            return `${diffMins}m ago`;
        } else {
            const diffHours = Math.floor(diffMins / 60);
            return `${diffHours}h ago`;
        }
    };

    const getUrgencyColor = (level: string) => {
        switch (level) {
            case 'high': return '#dc2626';
            case 'medium': return '#f59e0b';
            case 'low': return '#10b981';
            default: return '#6b7280';
        }
    };

    const getStatusColor = (status: string) => {
        switch (status) {
            case 'active': return '#dc2626';
            case 'assigned': return '#f59e0b';
            case 'resolved': return '#10b981';
            default: return '#6b7280';
        }
    };

    const renderCaseCard = (item: EmergencyCase, showActions: boolean = false) => (
        <TouchableOpacity
            style={styles.caseCard}
            onPress={() => setShowCaseDetails(item)}
            accessibilityRole="button"
            accessibilityLabel={`Emergency case for ${item.client_name}`}
        >
            <View style={styles.caseHeader}>
                <View style={styles.caseTitle}>
                    <Text style={styles.clientName}>{item.client_name}</Text>
                    <View style={[styles.urgencyBadge, { backgroundColor: getUrgencyColor(item.urgency_level) }]}>
                        <Text style={styles.urgencyText}>{item.urgency_level.toUpperCase()}</Text>
                    </View>
                </View>
                <Text style={styles.timeAgo}>{formatTimeAgo(item.created_at)}</Text>
            </View>

            <View style={styles.caseDetails}>
                <Text style={styles.location}>📍 {item.location}</Text>
                <Text style={styles.jurisdiction}>🏛️ {item.court_jurisdiction}</Text>
                <Text style={styles.caseType}>👤 {item.case_type === 'self' ? 'Self' : 'Loved One'}</Text>
            </View>

            <View style={styles.caseFooter}>
                <View style={[styles.statusBadge, { backgroundColor: getStatusColor(item.status) }]}>
                    <Text style={styles.statusText}>{item.status.toUpperCase()}</Text>
                </View>
                <Text style={styles.responseTime}>{item.estimated_response_time}</Text>
            </View>

            {showActions && item.status === 'active' && (
                <TouchableOpacity
                    style={styles.acceptButton}
                    onPress={() => handleAcceptCase(item.id)}
                    accessibilityRole="button"
                    accessibilityLabel={`Accept case for ${item.client_name}`}
                >
                    <Text style={styles.acceptButtonText}>Accept Case</Text>
                </TouchableOpacity>
            )}
        </TouchableOpacity>
    );

    if (!isAuthenticated || !user) {
        return (
            <View style={styles.container}>
                <Text style={styles.errorText}>Please log in to view attorney dashboard</Text>
            </View>
        );
    }

    if (isLoading) {
        return (
            <View style={styles.loadingContainer}>
                <ActivityIndicator size="large" color="#dc2626" />
                <Text style={styles.loadingText}>Loading attorney dashboard...</Text>
            </View>
        );
    }

    return (
        <ScrollView
            style={styles.container}
            refreshControl={
                <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
            }
        >
            {/* Header */}
            <View style={styles.header}>
                <Text style={styles.headerTitle}>Attorney Dashboard</Text>
                <Text style={styles.headerSubtitle}>Emergency Case Management</Text>
            </View>

            {/* Coverage Statistics */}
            {coverageStats && (
                <View style={styles.statsContainer}>
                    <Text style={styles.sectionTitle}>📊 District Coverage Statistics</Text>
                    <View style={styles.statsGrid}>
                        <View style={styles.statCard}>
                            <Text style={styles.statNumber}>{coverageStats.total_cases_handled}</Text>
                            <Text style={styles.statLabel}>Cases Handled</Text>
                        </View>
                        <View style={styles.statCard}>
                            <Text style={styles.statNumber}>{coverageStats.average_response_time}</Text>
                            <Text style={styles.statLabel}>Avg Response</Text>
                        </View>
                        <View style={styles.statCard}>
                            <Text style={styles.statNumber}>{coverageStats.success_rate}%</Text>
                            <Text style={styles.statLabel}>Success Rate</Text>
                        </View>
                        <View style={styles.statCard}>
                            <Text style={styles.statNumber}>{coverageStats.coverage_percentage}%</Text>
                            <Text style={styles.statLabel}>Coverage</Text>
                        </View>
                    </View>
                    <Text style={styles.districtInfo}>
                        {coverageStats.district_name} • {coverageStats.active_attorneys} Active Attorneys
                    </Text>
                </View>
            )}

            {/* Active Emergency Cases */}
            <View style={styles.section}>
                <View style={styles.sectionHeader}>
                    <Text style={styles.sectionTitle}>🚨 Active Emergency Cases</Text>
                    <View style={styles.caseBadge}>
                        <Text style={styles.caseBadgeText}>{activeCases.length}</Text>
                    </View>
                </View>

                {activeCases.length === 0 ? (
                    <View style={styles.emptyCases}>
                        <Text style={styles.emptyCasesText}>No active emergency cases</Text>
                        <Text style={styles.emptyCasesSubtext}>You&apos;ll be notified when new cases are available</Text>
                    </View>
                ) : (
                    activeCases.map(item => (
                        <View key={item.id}>
                            {renderCaseCard(item, true)}
                        </View>
                    ))
                )}
            </View>

            {/* Recent Cases */}
            <View style={styles.section}>
                <Text style={styles.sectionTitle}>📋 Recent Cases</Text>
                {recentCases.map(item => (
                    <View key={item.id}>
                        {renderCaseCard(item, false)}
                    </View>
                ))}
            </View>

            {/* Notification Preferences Button */}
            <TouchableOpacity
                style={styles.preferencesButton}
                onPress={() => setShowPreferences(true)}
                accessibilityRole="button"
                accessibilityLabel="Open notification preferences"
            >
                <Text style={styles.preferencesButtonText}>⚙️ Notification Preferences</Text>
            </TouchableOpacity>

            {/* Notification Preferences Modal */}
            <Modal
                visible={showPreferences}
                animationType="slide"
                presentationStyle="pageSheet"
            >
                <View style={styles.modalContainer}>
                    <View style={styles.modalHeader}>
                        <Text style={styles.modalTitle}>Notification Preferences</Text>
                        <TouchableOpacity
                            onPress={() => setShowPreferences(false)}
                            accessibilityRole="button"
                            accessibilityLabel="Close preferences"
                        >
                            <Text style={styles.closeButton}>✖️</Text>
                        </TouchableOpacity>
                    </View>

                    <ScrollView style={styles.modalContent}>
                        <View style={styles.preferenceSection}>
                            <Text style={styles.preferenceSectionTitle}>Notification Methods</Text>

                            <View style={styles.preferenceItem}>
                                <Text style={styles.preferenceLabel}>Email Notifications</Text>
                                <Switch
                                    value={preferences.email_notifications}
                                    onValueChange={(value) =>
                                        setPreferences(prev => ({ ...prev, email_notifications: value }))
                                    }
                                />
                            </View>

                            <View style={styles.preferenceItem}>
                                <Text style={styles.preferenceLabel}>SMS Notifications</Text>
                                <Switch
                                    value={preferences.sms_notifications}
                                    onValueChange={(value) =>
                                        setPreferences(prev => ({ ...prev, sms_notifications: value }))
                                    }
                                />
                            </View>

                            <View style={styles.preferenceItem}>
                                <Text style={styles.preferenceLabel}>Push Notifications</Text>
                                <Switch
                                    value={preferences.push_notifications}
                                    onValueChange={(value) =>
                                        setPreferences(prev => ({ ...prev, push_notifications: value }))
                                    }
                                />
                            </View>
                        </View>

                        <View style={styles.preferenceSection}>
                            <Text style={styles.preferenceSectionTitle}>Frequency Settings</Text>

                            <View style={styles.preferenceItem}>
                                <Text style={styles.preferenceLabel}>Urgent Cases Only</Text>
                                <Switch
                                    value={preferences.urgent_only}
                                    onValueChange={(value) =>
                                        setPreferences(prev => ({ ...prev, urgent_only: value }))
                                    }
                                />
                            </View>

                            <View style={styles.preferenceItem}>
                                <Text style={styles.preferenceLabel}>Daily Digest</Text>
                                <Switch
                                    value={preferences.daily_digest}
                                    onValueChange={(value) =>
                                        setPreferences(prev => ({ ...prev, daily_digest: value }))
                                    }
                                />
                            </View>

                            <View style={styles.preferenceItem}>
                                <Text style={styles.preferenceLabel}>Weekly Summary</Text>
                                <Switch
                                    value={preferences.weekly_summary}
                                    onValueChange={(value) =>
                                        setPreferences(prev => ({ ...prev, weekly_summary: value }))
                                    }
                                />
                            </View>
                        </View>

                        <View style={styles.preferenceSection}>
                            <Text style={styles.preferenceSectionTitle}>Quiet Hours</Text>
                            <Text style={styles.preferenceSectionSubtitle}>
                                Set hours when you don&apos;t want to receive non-urgent notifications
                            </Text>

                            <View style={styles.quietHours}>
                                <View style={styles.timeInput}>
                                    <Text style={styles.timeLabel}>Start:</Text>
                                    <Text style={styles.timeValue}>{preferences.quiet_hours_start}</Text>
                                </View>
                                <View style={styles.timeInput}>
                                    <Text style={styles.timeLabel}>End:</Text>
                                    <Text style={styles.timeValue}>{preferences.quiet_hours_end}</Text>
                                </View>
                            </View>
                        </View>
                    </ScrollView>

                    <TouchableOpacity
                        style={styles.saveButton}
                        onPress={() => {
                            handleUpdatePreferences(preferences);
                            setShowPreferences(false);
                        }}
                        accessibilityRole="button"
                    >
                        <Text style={styles.saveButtonText}>Save Preferences</Text>
                    </TouchableOpacity>
                </View>
            </Modal>

            {/* Case Details Modal */}
            <Modal
                visible={!!showCaseDetails}
                animationType="slide"
                presentationStyle="pageSheet"
            >
                {showCaseDetails && (
                    <View style={styles.modalContainer}>
                        <View style={styles.modalHeader}>
                            <Text style={styles.modalTitle}>Case Details</Text>
                            <TouchableOpacity
                                onPress={() => setShowCaseDetails(null)}
                                accessibilityRole="button"
                            >
                                <Text style={styles.closeButton}>✖️</Text>
                            </TouchableOpacity>
                        </View>

                        <ScrollView style={styles.modalContent}>
                            <View style={styles.caseDetailSection}>
                                <Text style={styles.caseDetailTitle}>{showCaseDetails.client_name}</Text>
                                <Text style={styles.caseDetailSubtitle}>Case #{showCaseDetails.id}</Text>
                            </View>

                            <View style={styles.caseDetailSection}>
                                <Text style={styles.detailLabel}>Location:</Text>
                                <Text style={styles.detailValue}>{showCaseDetails.location}</Text>
                            </View>

                            <View style={styles.caseDetailSection}>
                                <Text style={styles.detailLabel}>Court Jurisdiction:</Text>
                                <Text style={styles.detailValue}>{showCaseDetails.court_jurisdiction}</Text>
                            </View>

                            <View style={styles.caseDetailSection}>
                                <Text style={styles.detailLabel}>Case Type:</Text>
                                <Text style={styles.detailValue}>
                                    {showCaseDetails.case_type === 'self' ? 'Self-reported' : 'Loved one reported'}
                                </Text>
                            </View>

                            <View style={styles.caseDetailSection}>
                                <Text style={styles.detailLabel}>Urgency Level:</Text>
                                <Text style={[styles.detailValue, { color: getUrgencyColor(showCaseDetails.urgency_level) }]}>
                                    {showCaseDetails.urgency_level.toUpperCase()}
                                </Text>
                            </View>

                            <View style={styles.caseDetailSection}>
                                <Text style={styles.detailLabel}>Created:</Text>
                                <Text style={styles.detailValue}>
                                    {new Date(showCaseDetails.created_at).toLocaleString()}
                                </Text>
                            </View>

                            {showCaseDetails.status === 'active' && (
                                <TouchableOpacity
                                    style={styles.acceptCaseButton}
                                    onPress={() => {
                                        setShowCaseDetails(null);
                                        handleAcceptCase(showCaseDetails.id);
                                    }}
                                    accessibilityRole="button"
                                >
                                    <Text style={styles.acceptCaseButtonText}>Accept This Case</Text>
                                </TouchableOpacity>
                            )}
                        </ScrollView>
                    </View>
                )}
            </Modal>
        </ScrollView>
    );
};

const styles = StyleSheet.create({
    acceptButton: {
        backgroundColor: '#dc2626',
        borderRadius: 8,
        marginTop: 12,
        paddingVertical: 12,
    },
    acceptButtonText: {
        color: '#fff',
        fontSize: 14,
        fontWeight: 'bold',
        textAlign: 'center',
    },
    acceptCaseButton: {
        backgroundColor: '#dc2626',
        borderRadius: 8,
        marginTop: 24,
        paddingVertical: 16,
    },
    acceptCaseButtonText: {
        color: '#fff',
        fontSize: 16,
        fontWeight: 'bold',
        textAlign: 'center',
    },
    caseBadge: {
        backgroundColor: '#dc2626',
        borderRadius: 12,
        paddingHorizontal: 8,
        paddingVertical: 4,
    },
    caseBadgeText: {
        color: '#fff',
        fontSize: 12,
        fontWeight: 'bold',
    },
    caseCard: {
        backgroundColor: '#fff',
        borderRadius: 12,
        elevation: 3,
        marginBottom: 12,
        padding: 16,
        shadowColor: '#000',
        shadowOffset: { width: 0, height: 2 },
        shadowOpacity: 0.1,
        shadowRadius: 4,
    },
    caseDetailSection: {
        marginBottom: 16,
    },
    caseDetailSubtitle: {
        color: '#6b7280',
        fontSize: 14,
        marginTop: 4,
    },
    caseDetailTitle: {
        color: '#111827',
        fontSize: 20,
        fontWeight: 'bold',
    },
    caseDetails: {
        marginBottom: 12,
    },
    caseFooter: {
        alignItems: 'center',
        flexDirection: 'row',
        justifyContent: 'space-between',
    },
    caseHeader: {
        alignItems: 'center',
        flexDirection: 'row',
        justifyContent: 'space-between',
        marginBottom: 12,
    },
    caseTitle: {
        alignItems: 'center',
        flexDirection: 'row',
        flex: 1,
    },
    caseType: {
        color: '#374151',
        fontSize: 14,
    },
    clientName: {
        color: '#111827',
        fontSize: 16,
        fontWeight: 'bold',
        marginRight: 8,
    },
    closeButton: {
        color: '#6b7280',
        fontSize: 18,
    },
    container: {
        backgroundColor: '#f8fafc',
        flex: 1,
    },
    detailLabel: {
        color: '#6b7280',
        fontSize: 12,
        marginBottom: 4,
    },
    detailValue: {
        color: '#111827',
        fontSize: 14,
    },
    districtInfo: {
        color: '#6b7280',
        fontSize: 12,
        marginTop: 12,
        textAlign: 'center',
    },
    emptyCases: {
        alignItems: 'center',
        backgroundColor: '#fff',
        borderRadius: 12,
        padding: 24,
    },
    emptyCasesSubtext: {
        color: '#9ca3af',
        fontSize: 12,
        marginTop: 4,
    },
    emptyCasesText: {
        color: '#6b7280',
        fontSize: 14,
        fontWeight: '500',
    },
    errorText: {
        color: '#dc2626',
        fontSize: 16,
        marginTop: 50,
        textAlign: 'center',
    },
    header: {
        backgroundColor: '#fff',
        borderBottomColor: '#e5e7eb',
        borderBottomWidth: 1,
        padding: 20,
    },
    headerSubtitle: {
        color: '#6b7280',
        fontSize: 14,
        marginTop: 4,
    },
    headerTitle: {
        color: '#111827',
        fontSize: 24,
        fontWeight: 'bold',
    },
    jurisdiction: {
        color: '#374151',
        fontSize: 14,
        marginBottom: 4,
    },
    loadingContainer: {
        alignItems: 'center',
        backgroundColor: '#f8fafc',
        flex: 1,
        justifyContent: 'center',
    },
    loadingText: {
        color: '#6b7280',
        fontSize: 16,
        marginTop: 12,
    },
    location: {
        color: '#374151',
        fontSize: 14,
        marginBottom: 4,
    },
    modalContainer: {
        backgroundColor: '#fff',
        flex: 1,
    },
    modalContent: {
        flex: 1,
        padding: 20,
    },
    modalHeader: {
        alignItems: 'center',
        borderBottomColor: '#e5e7eb',
        borderBottomWidth: 1,
        flexDirection: 'row',
        justifyContent: 'space-between',
        padding: 20,
    },
    modalTitle: {
        color: '#111827',
        fontSize: 18,
        fontWeight: 'bold',
    },
    preferenceItem: {
        alignItems: 'center',
        borderBottomColor: '#f3f4f6',
        borderBottomWidth: 1,
        flexDirection: 'row',
        justifyContent: 'space-between',
        paddingVertical: 12,
    },
    preferenceLabel: {
        color: '#374151',
        fontSize: 14,
    },
    preferenceSection: {
        marginBottom: 24,
    },
    preferenceSectionSubtitle: {
        color: '#6b7280',
        fontSize: 12,
        marginBottom: 12,
    },
    preferenceSectionTitle: {
        color: '#111827',
        fontSize: 16,
        fontWeight: 'bold',
        marginBottom: 12,
    },
    preferencesButton: {
        backgroundColor: '#fff',
        borderRadius: 12,
        elevation: 3,
        margin: 16,
        padding: 16,
        shadowColor: '#000',
        shadowOffset: { width: 0, height: 2 },
        shadowOpacity: 0.1,
        shadowRadius: 4,
    },
    preferencesButtonText: {
        color: '#111827',
        fontSize: 16,
        fontWeight: 'bold',
        textAlign: 'center',
    },
    quietHours: {
        flexDirection: 'row',
        justifyContent: 'space-around',
        marginTop: 12,
    },
    responseTime: {
        color: '#6b7280',
        fontSize: 12,
    },
    saveButton: {
        backgroundColor: '#dc2626',
        borderRadius: 8,
        margin: 20,
        padding: 16,
    },
    saveButtonText: {
        color: '#fff',
        fontSize: 16,
        fontWeight: 'bold',
        textAlign: 'center',
    },
    section: {
        margin: 16,
    },
    sectionHeader: {
        alignItems: 'center',
        flexDirection: 'row',
        justifyContent: 'space-between',
        marginBottom: 12,
    },
    sectionTitle: {
        color: '#111827',
        fontSize: 18,
        fontWeight: 'bold',
    },
    statCard: {
        alignItems: 'center',
        backgroundColor: '#f9fafb',
        borderRadius: 8,
        marginBottom: 8,
        padding: 12,
        width: '48%',
    },
    statLabel: {
        color: '#6b7280',
        fontSize: 12,
        marginTop: 4,
    },
    statNumber: {
        color: '#dc2626',
        fontSize: 20,
        fontWeight: 'bold',
    },
    statsContainer: {
        backgroundColor: '#fff',
        borderRadius: 12,
        elevation: 3,
        margin: 16,
        padding: 16,
        shadowColor: '#000',
        shadowOffset: { width: 0, height: 2 },
        shadowOpacity: 0.1,
        shadowRadius: 4,
    },
    statsGrid: {
        flexDirection: 'row',
        flexWrap: 'wrap',
        justifyContent: 'space-between',
        marginTop: 12,
    },
    statusBadge: {
        borderRadius: 4,
        paddingHorizontal: 8,
        paddingVertical: 4,
    },
    statusText: {
        color: '#fff',
        fontSize: 10,
        fontWeight: 'bold',
    },
    timeAgo: {
        color: '#6b7280',
        fontSize: 12,
    },
    timeInput: {
        alignItems: 'center',
    },
    timeLabel: {
        color: '#6b7280',
        fontSize: 12,
        marginBottom: 4,
    },
    timeValue: {
        color: '#111827',
        fontSize: 16,
        fontWeight: 'bold',
    },
    urgencyBadge: {
        borderRadius: 4,
        paddingHorizontal: 8,
        paddingVertical: 4,
    },
    urgencyText: {
        color: '#fff',
        fontSize: 10,
        fontWeight: 'bold',
    },
});

export default AttorneyDashboardScreen;
