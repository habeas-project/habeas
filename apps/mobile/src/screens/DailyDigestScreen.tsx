import React, { useEffect, useState, useMemo } from 'react';
import {
    View,
    Text,
    StyleSheet,
    ScrollView,
    TouchableOpacity,
    TextInput,
    RefreshControl,
    Alert,
    ActivityIndicator,
    StatusBar,
    Modal,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useNavigation } from '@react-navigation/native';
import { NativeStackNavigationProp } from '@react-navigation/native-stack';

import { useAuth } from '../contexts/AuthContext';
import { RootStackParamList } from '../App';
import {
    getDailyDigest,
    acceptCase,
    DailyDigestResponse,
    AvailableCaseResponse,
    CourtCoverageStats,
    AttorneyCaseAcceptanceRequest,
} from '../api/client';

// Navigation type
type DailyDigestNavigationProp = NativeStackNavigationProp<
    RootStackParamList,
    'DailyDigest'
>;

// Filter options
type UrgencyFilter = 'all' | 'urgent' | 'high' | 'medium' | 'low';
type CaseTypeFilter = 'all' | 'self' | 'loved_one';

// Case acceptance modal state
interface CaseAcceptanceModal {
    visible: boolean;
    case: AvailableCaseResponse | null;
    accepting: boolean;
}

const DailyDigestScreen: React.FC = () => {
    const navigation = useNavigation<DailyDigestNavigationProp>();
    const { user, isAttorney } = useAuth();
    const [loading, setLoading] = useState(true);
    const [refreshing, setRefreshing] = useState(false);
    const [digestData, setDigestData] = useState<DailyDigestResponse | null>(null);

    // Filtering and search states
    const [searchText, setSearchText] = useState('');
    const [urgencyFilter, setUrgencyFilter] = useState<UrgencyFilter>('all');
    const [caseTypeFilter, setCaseTypeFilter] = useState<CaseTypeFilter>('all');
    const [selectedCourt, setSelectedCourt] = useState<string>('all');

    // Case acceptance modal
    const [acceptanceModal, setAcceptanceModal] = useState<CaseAcceptanceModal>({
        visible: false,
        case: null,
        accepting: false,
    });

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

    // Load daily digest data
    const loadDigestData = async (): Promise<void> => {
        try {
            const response = await getDailyDigest();
            setDigestData(response);
        } catch (error) {
            console.error('Failed to load daily digest:', error);
            Alert.alert(
                'Error',
                'Failed to load daily digest. Please check your connection and try again.',
                [{ text: 'OK' }]
            );
        } finally {
            setLoading(false);
            setRefreshing(false);
        }
    };

    useEffect(() => {
        loadDigestData();
    }, []);

    const onRefresh = (): void => {
        setRefreshing(true);
        loadDigestData();
    };

    // Filter and search cases
    const filteredCases = useMemo(() => {
        if (!digestData?.unassigned_cases) return [];

        return digestData.unassigned_cases.filter(case_ => {
            // Search filter
            const searchMatch = !searchText ||
                case_.location_description.toLowerCase().includes(searchText.toLowerCase()) ||
                case_.court_name.toLowerCase().includes(searchText.toLowerCase());

            // Urgency filter
            const urgencyMatch = urgencyFilter === 'all' || case_.urgency_level === urgencyFilter;

            // Case type filter
            const typeMatch = caseTypeFilter === 'all' || case_.case_type === caseTypeFilter;

            // Court filter
            const courtMatch = selectedCourt === 'all' || case_.court_name === selectedCourt;

            return searchMatch && urgencyMatch && typeMatch && courtMatch;
        });
    }, [digestData?.unassigned_cases, searchText, urgencyFilter, caseTypeFilter, selectedCourt]);

    // Get unique courts for filter dropdown
    const availableCourts = useMemo(() => {
        if (!digestData?.unassigned_cases) return [];
        const courts = new Set(digestData.unassigned_cases.map(case_ => case_.court_name));
        return Array.from(courts).sort();
    }, [digestData?.unassigned_cases]);

    // Format time since created
    const getTimeSinceCreated = (createdAt: string): string => {
        const created = new Date(createdAt);
        const now = new Date();
        const hoursElapsed = (now.getTime() - created.getTime()) / (1000 * 60 * 60);

        if (hoursElapsed < 1) {
            return `${Math.round(hoursElapsed * 60)} minutes ago`;
        } else if (hoursElapsed < 24) {
            return `${Math.round(hoursElapsed)} hours ago`;
        } else {
            return `${Math.round(hoursElapsed / 24)} days ago`;
        }
    };

    // Get urgency color
    const getUrgencyColor = (urgency: string): string => {
        switch (urgency) {
            case 'urgent': return '#FF3B30';
            case 'high': return '#FF9500';
            case 'medium': return '#FFCC00';
            case 'low': return '#34C759';
            default: return '#8E8E93';
        }
    };

    // Handle quick case acceptance
    const handleQuickAccept = (case_: AvailableCaseResponse): void => {
        setAcceptanceModal({
            visible: true,
            case: case_,
            accepting: false,
        });
    };

    // Confirm case acceptance
    const confirmCaseAcceptance = async (): Promise<void> => {
        if (!acceptanceModal.case || !user?.attorney_id) return;

        setAcceptanceModal(prev => ({ ...prev, accepting: true }));

        try {
            const request: AttorneyCaseAcceptanceRequest = {
                message: 'Quick acceptance from daily digest',
            };

            await acceptCase(acceptanceModal.case.case_id, user.attorney_id, request);

            Alert.alert(
                'Case Accepted',
                'You have successfully accepted this case. You will receive the client contact information shortly.',
                [{ text: 'OK' }]
            );

            // Close modal and refresh data
            setAcceptanceModal({ visible: false, case: null, accepting: false });
            loadDigestData();
        } catch (error) {
            console.error('Failed to accept case:', error);
            Alert.alert(
                'Error',
                'Failed to accept the case. Please try again.',
                [{ text: 'OK' }]
            );
        } finally {
            setAcceptanceModal(prev => ({ ...prev, accepting: false }));
        }
    };

    // Navigate to case detail
    const handleViewCaseDetail = (caseId: number): void => {
        navigation.navigate('CaseDetail', { caseId });
    };

    // Clear all filters
    const clearFilters = (): void => {
        setSearchText('');
        setUrgencyFilter('all');
        setCaseTypeFilter('all');
        setSelectedCourt('all');
    };

    if (loading) {
        return (
            <SafeAreaView style={styles.container}>
                <StatusBar barStyle="dark-content" backgroundColor="#f8f9fa" />
                <View style={styles.loadingContainer}>
                    <ActivityIndicator size="large" color="#007AFF" />
                    <Text style={styles.loadingText}>Loading daily digest...</Text>
                </View>
            </SafeAreaView>
        );
    }

    return (
        <SafeAreaView style={styles.container}>
            <StatusBar barStyle="dark-content" backgroundColor="#f8f9fa" />

            <ScrollView
                style={styles.scrollView}
                refreshControl={
                    <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
                }
                showsVerticalScrollIndicator={false}
            >
                {/* Header */}
                <View style={styles.header}>
                    <Text style={styles.title}>Daily Digest</Text>
                    <Text style={styles.subtitle}>
                        {digestData?.total_unassigned || 0} unassigned cases across all districts
                    </Text>
                    {digestData?.digest_date && (
                        <Text style={styles.digestDate}>
                            Updated: {new Date(digestData.digest_date).toLocaleTimeString()}
                        </Text>
                    )}
                </View>

                {/* Court Coverage Statistics */}
                {digestData?.court_coverage_stats && Object.keys(digestData.court_coverage_stats).length > 0 && (
                    <View style={styles.section}>
                        <Text style={styles.sectionTitle}>Court Coverage</Text>
                        {Object.values(digestData.court_coverage_stats).map((court: CourtCoverageStats) => (
                            <View key={court.court_id} style={styles.courtStatItem}>
                                <Text style={styles.courtStatName}>{court.court_name}</Text>
                                <View style={styles.courtStatNumbers}>
                                    <Text style={styles.courtStatText}>
                                        {court.total_attorneys} attorneys • {court.unassigned_cases} unassigned
                                    </Text>
                                </View>
                            </View>
                        ))}
                    </View>
                )}

                {/* Search and Filters */}
                <View style={styles.filterSection}>
                    <TextInput
                        style={styles.searchInput}
                        placeholder="Search by location or court..."
                        value={searchText}
                        onChangeText={setSearchText}
                        placeholderTextColor="#999"
                    />

                    <ScrollView horizontal showsHorizontalScrollIndicator={false} style={styles.filterRow}>
                        {/* Urgency Filter */}
                        <View style={styles.filterGroup}>
                            <Text style={styles.filterLabel}>Urgency:</Text>
                            {(['all', 'urgent', 'high', 'medium', 'low'] as UrgencyFilter[]).map(urgency => (
                                <TouchableOpacity
                                    key={urgency}
                                    style={[
                                        styles.filterButton,
                                        urgencyFilter === urgency && styles.filterButtonActive,
                                    ]}
                                    onPress={() => setUrgencyFilter(urgency)}
                                >
                                    <Text
                                        style={[
                                            styles.filterButtonText,
                                            urgencyFilter === urgency && styles.filterButtonTextActive,
                                        ]}
                                    >
                                        {urgency === 'all' ? 'All' : urgency.charAt(0).toUpperCase() + urgency.slice(1)}
                                    </Text>
                                </TouchableOpacity>
                            ))}
                        </View>

                        {/* Case Type Filter */}
                        <View style={styles.filterGroup}>
                            <Text style={styles.filterLabel}>Type:</Text>
                            {(['all', 'self', 'loved_one'] as CaseTypeFilter[]).map(type => (
                                <TouchableOpacity
                                    key={type}
                                    style={[
                                        styles.filterButton,
                                        caseTypeFilter === type && styles.filterButtonActive,
                                    ]}
                                    onPress={() => setCaseTypeFilter(type)}
                                >
                                    <Text
                                        style={[
                                            styles.filterButtonText,
                                            caseTypeFilter === type && styles.filterButtonTextActive,
                                        ]}
                                    >
                                        {type === 'all' ? 'All' : type === 'self' ? 'Self' : 'Loved One'}
                                    </Text>
                                </TouchableOpacity>
                            ))}
                        </View>
                    </ScrollView>

                    {/* Court Filter */}
                    {availableCourts.length > 1 && (
                        <ScrollView horizontal showsHorizontalScrollIndicator={false} style={styles.courtFilterRow}>
                            <TouchableOpacity
                                style={[
                                    styles.courtFilterButton,
                                    selectedCourt === 'all' && styles.courtFilterButtonActive,
                                ]}
                                onPress={() => setSelectedCourt('all')}
                            >
                                <Text
                                    style={[
                                        styles.courtFilterButtonText,
                                        selectedCourt === 'all' && styles.courtFilterButtonTextActive,
                                    ]}
                                >
                                    All Courts
                                </Text>
                            </TouchableOpacity>
                            {availableCourts.map(court => (
                                <TouchableOpacity
                                    key={court}
                                    style={[
                                        styles.courtFilterButton,
                                        selectedCourt === court && styles.courtFilterButtonActive,
                                    ]}
                                    onPress={() => setSelectedCourt(court)}
                                >
                                    <Text
                                        style={[
                                            styles.courtFilterButtonText,
                                            selectedCourt === court && styles.courtFilterButtonTextActive,
                                        ]}
                                    >
                                        {court}
                                    </Text>
                                </TouchableOpacity>
                            ))}
                        </ScrollView>
                    )}

                    {/* Clear Filters */}
                    {(searchText || urgencyFilter !== 'all' || caseTypeFilter !== 'all' || selectedCourt !== 'all') && (
                        <TouchableOpacity style={styles.clearFiltersButton} onPress={clearFilters}>
                            <Text style={styles.clearFiltersText}>Clear All Filters</Text>
                        </TouchableOpacity>
                    )}
                </View>

                {/* Cases List */}
                <View style={styles.section}>
                    <View style={styles.sectionHeader}>
                        <Text style={styles.sectionTitle}>
                            Unassigned Cases ({filteredCases.length})
                        </Text>
                    </View>

                    {filteredCases.length === 0 ? (
                        <View style={styles.emptyState}>
                            <Text style={styles.emptyStateText}>
                                {digestData?.unassigned_cases.length === 0
                                    ? 'No unassigned cases at this time'
                                    : 'No cases match your current filters'
                                }
                            </Text>
                            {digestData?.unassigned_cases.length !== 0 && (
                                <TouchableOpacity style={styles.clearFiltersButton} onPress={clearFilters}>
                                    <Text style={styles.clearFiltersText}>Clear Filters</Text>
                                </TouchableOpacity>
                            )}
                        </View>
                    ) : (
                        filteredCases.map(case_ => (
                            <View key={case_.case_id} style={styles.caseCard}>
                                {/* Case Header */}
                                <View style={styles.caseHeader}>
                                    <View style={styles.caseHeaderLeft}>
                                        <View
                                            style={[
                                                styles.urgencyBadge,
                                                { backgroundColor: getUrgencyColor(case_.urgency_level) },
                                            ]}
                                        >
                                            <Text style={styles.urgencyBadgeText}>
                                                {case_.urgency_level.toUpperCase()}
                                            </Text>
                                        </View>
                                        <Text style={styles.caseType}>
                                            {case_.case_type === 'self' ? 'Self Detention' : 'Loved One Detention'}
                                        </Text>
                                    </View>
                                    <Text style={styles.caseTime}>
                                        {getTimeSinceCreated(case_.created_at)}
                                    </Text>
                                </View>

                                {/* Case Details */}
                                <View style={styles.caseDetails}>
                                    <Text style={styles.caseLocation}>{case_.location_description}</Text>
                                    <Text style={styles.caseCourt}>{case_.court_name}</Text>
                                </View>

                                {/* Case Actions */}
                                <View style={styles.caseActions}>
                                    <TouchableOpacity
                                        style={styles.viewDetailButton}
                                        onPress={() => handleViewCaseDetail(case_.case_id)}
                                    >
                                        <Text style={styles.viewDetailButtonText}>View Details</Text>
                                    </TouchableOpacity>
                                    <TouchableOpacity
                                        style={styles.quickAcceptButton}
                                        onPress={() => handleQuickAccept(case_)}
                                    >
                                        <Text style={styles.quickAcceptButtonText}>Quick Accept</Text>
                                    </TouchableOpacity>
                                </View>
                            </View>
                        ))
                    )}
                </View>
            </ScrollView>

            {/* Case Acceptance Modal */}
            <Modal
                visible={acceptanceModal.visible}
                transparent
                animationType="slide"
                onRequestClose={() => setAcceptanceModal({ visible: false, case: null, accepting: false })}
            >
                <View style={styles.modalOverlay}>
                    <View style={styles.modalContent}>
                        <Text style={styles.modalTitle}>Accept Case</Text>
                        {acceptanceModal.case && (
                            <>
                                <Text style={styles.modalText}>
                                    Are you sure you want to accept this case?
                                </Text>
                                <View style={styles.modalCaseInfo}>
                                    <Text style={styles.modalCaseLocation}>
                                        {acceptanceModal.case.location_description}
                                    </Text>
                                    <Text style={styles.modalCaseCourt}>
                                        {acceptanceModal.case.court_name}
                                    </Text>
                                    <Text style={styles.modalCaseType}>
                                        {acceptanceModal.case.case_type === 'self' ? 'Self Detention' : 'Loved One Detention'}
                                    </Text>
                                </View>
                                <Text style={styles.modalWarning}>
                                    Once accepted, you will receive the client&apos;s contact information and become responsible for this case.
                                </Text>
                            </>
                        )}
                        <View style={styles.modalActions}>
                            <TouchableOpacity
                                style={styles.modalCancelButton}
                                onPress={() => setAcceptanceModal({ visible: false, case: null, accepting: false })}
                                disabled={acceptanceModal.accepting}
                            >
                                <Text style={styles.modalCancelButtonText}>Cancel</Text>
                            </TouchableOpacity>
                            <TouchableOpacity
                                style={styles.modalAcceptButton}
                                onPress={confirmCaseAcceptance}
                                disabled={acceptanceModal.accepting}
                            >
                                {acceptanceModal.accepting ? (
                                    <ActivityIndicator size="small" color="#FFFFFF" />
                                ) : (
                                    <Text style={styles.modalAcceptButtonText}>Accept Case</Text>
                                )}
                            </TouchableOpacity>
                        </View>
                    </View>
                </View>
            </Modal>
        </SafeAreaView>
    );
};

const styles = StyleSheet.create({
    caseActions: {
        flexDirection: 'row',
        gap: 10,
    },
    caseCard: {
        backgroundColor: '#f9f9f9',
        borderColor: '#e0e0e0',
        borderRadius: 12,
        borderWidth: 1,
        marginBottom: 12,
        padding: 16,
    },
    caseCourt: {
        color: '#666',
        fontSize: 14,
    },
    caseDetails: {
        marginBottom: 15,
    },
    caseHeader: {
        alignItems: 'center',
        flexDirection: 'row',
        justifyContent: 'space-between',
        marginBottom: 12,
    },
    caseHeaderLeft: {
        alignItems: 'center',
        flexDirection: 'row',
    },
    caseLocation: {
        color: '#1a1a1a',
        fontSize: 16,
        fontWeight: '500',
        marginBottom: 4,
    },
    caseTime: {
        color: '#999',
        fontSize: 12,
    },
    caseType: {
        color: '#1a1a1a',
        fontSize: 14,
        fontWeight: '500',
    },
    clearFiltersButton: {
        alignSelf: 'flex-start',
        backgroundColor: '#FF3B30',
        borderRadius: 20,
        paddingHorizontal: 16,
        paddingVertical: 8,
    },
    clearFiltersText: {
        color: '#FFFFFF',
        fontSize: 14,
        fontWeight: '500',
    },
    container: {
        backgroundColor: '#f8f9fa',
        flex: 1,
    },
    courtFilterButton: {
        backgroundColor: '#f0f0f0',
        borderRadius: 20,
        marginRight: 10,
        paddingHorizontal: 14,
        paddingVertical: 8,
    },
    courtFilterButtonActive: {
        backgroundColor: '#34C759',
    },
    courtFilterButtonText: {
        color: '#666',
        fontSize: 14,
        fontWeight: '500',
    },
    courtFilterButtonTextActive: {
        color: '#FFFFFF',
    },
    courtFilterRow: {
        flexDirection: 'row',
        marginBottom: 15,
    },
    courtStatItem: {
        borderBottomColor: '#f0f0f0',
        borderBottomWidth: 1,
        paddingVertical: 12,
    },
    courtStatName: {
        color: '#1a1a1a',
        fontSize: 16,
        fontWeight: '500',
        marginBottom: 4,
    },
    courtStatNumbers: {
        alignItems: 'center',
        flexDirection: 'row',
        justifyContent: 'space-between',
    },
    courtStatText: {
        color: '#666',
        fontSize: 14,
    },
    digestDate: {
        color: '#999',
        fontSize: 14,
        marginTop: 5,
    },
    emptyState: {
        alignItems: 'center',
        padding: 40,
    },
    emptyStateText: {
        color: '#666',
        fontSize: 16,
        marginBottom: 20,
        textAlign: 'center',
    },
    filterButton: {
        backgroundColor: '#f0f0f0',
        borderRadius: 16,
        marginRight: 8,
        paddingHorizontal: 12,
        paddingVertical: 6,
    },
    filterButtonActive: {
        backgroundColor: '#007AFF',
    },
    filterButtonText: {
        color: '#666',
        fontSize: 14,
    },
    filterButtonTextActive: {
        color: '#FFFFFF',
        fontWeight: '500',
    },
    filterGroup: {
        alignItems: 'center',
        flexDirection: 'row',
        marginRight: 20,
    },
    filterLabel: {
        color: '#1a1a1a',
        fontSize: 14,
        fontWeight: '500',
        marginRight: 8,
    },
    filterRow: {
        flexDirection: 'row',
        marginBottom: 15,
    },
    filterSection: {
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
    header: {
        padding: 20,
        paddingBottom: 10,
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
    modalAcceptButton: {
        alignItems: 'center',
        backgroundColor: '#34C759',
        borderRadius: 8,
        flex: 1,
        justifyContent: 'center',
        minHeight: 48,
        paddingVertical: 12,
    },
    modalAcceptButtonText: {
        color: '#FFFFFF',
        fontSize: 16,
        fontWeight: '600',
    },
    modalActions: {
        flexDirection: 'row',
        gap: 12,
    },
    modalCancelButton: {
        alignItems: 'center',
        backgroundColor: '#f0f0f0',
        borderRadius: 8,
        flex: 1,
        paddingVertical: 12,
    },
    modalCancelButtonText: {
        color: '#666',
        fontSize: 16,
        fontWeight: '500',
    },
    modalCaseCourt: {
        color: '#666',
        fontSize: 14,
        marginBottom: 4,
    },
    modalCaseInfo: {
        backgroundColor: '#f9f9f9',
        borderRadius: 8,
        marginBottom: 16,
        padding: 16,
    },
    modalCaseLocation: {
        color: '#1a1a1a',
        fontSize: 16,
        fontWeight: '500',
        marginBottom: 4,
    },
    modalCaseType: {
        color: '#007AFF',
        fontSize: 14,
        fontWeight: '500',
    },
    modalContent: {
        backgroundColor: '#FFFFFF',
        borderRadius: 16,
        maxWidth: 400,
        padding: 24,
        width: '100%',
    },
    modalOverlay: {
        alignItems: 'center',
        backgroundColor: 'rgba(0, 0, 0, 0.5)',
        flex: 1,
        justifyContent: 'center',
        padding: 20,
    },
    modalText: {
        color: '#333',
        fontSize: 16,
        lineHeight: 22,
        marginBottom: 16,
        textAlign: 'center',
    },
    modalTitle: {
        color: '#1a1a1a',
        fontSize: 20,
        fontWeight: '600',
        marginBottom: 16,
        textAlign: 'center',
    },
    modalWarning: {
        color: '#FF3B30',
        fontSize: 14,
        lineHeight: 20,
        marginBottom: 24,
        textAlign: 'center',
    },
    quickAcceptButton: {
        alignItems: 'center',
        backgroundColor: '#34C759',
        borderRadius: 8,
        flex: 1,
        paddingVertical: 10,
    },
    quickAcceptButtonText: {
        color: '#FFFFFF',
        fontSize: 14,
        fontWeight: '600',
    },
    scrollView: {
        flex: 1,
    },
    searchInput: {
        backgroundColor: '#f9f9f9',
        borderColor: '#ddd',
        borderRadius: 8,
        borderWidth: 1,
        color: '#1a1a1a',
        fontSize: 16,
        marginBottom: 15,
        padding: 12,
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
    sectionHeader: {
        alignItems: 'center',
        flexDirection: 'row',
        justifyContent: 'space-between',
        marginBottom: 15,
    },
    sectionTitle: {
        color: '#1a1a1a',
        fontSize: 20,
        fontWeight: '600',
        marginBottom: 15,
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
    urgencyBadge: {
        borderRadius: 12,
        marginRight: 10,
        paddingHorizontal: 8,
        paddingVertical: 4,
    },
    urgencyBadgeText: {
        color: '#FFFFFF',
        fontSize: 12,
        fontWeight: '600',
    },
    viewDetailButton: {
        alignItems: 'center',
        backgroundColor: '#f0f0f0',
        borderRadius: 8,
        flex: 1,
        paddingVertical: 10,
    },
    viewDetailButtonText: {
        color: '#007AFF',
        fontSize: 14,
        fontWeight: '500',
    },
});

export default DailyDigestScreen;
