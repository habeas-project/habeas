import React, { useEffect, useState, useCallback } from 'react';
import {
    View,
    Text,
    StyleSheet,
    FlatList,
    TouchableOpacity,
    RefreshControl,
    Alert,
    ActivityIndicator,
    TextInput,
    Modal,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useNavigation, useRoute, RouteProp } from '@react-navigation/native';
import { NativeStackNavigationProp } from '@react-navigation/native-stack';

import { useAuth } from '../contexts/AuthContext';
import { RootStackParamList } from '../App';
import CaseDetailModal from '../components/CaseDetailModal';

// Navigation types
type AvailableCasesNavigationProp = NativeStackNavigationProp<
    RootStackParamList,
    'AvailableCases'
>;

type AvailableCasesRouteProp = RouteProp<RootStackParamList, 'AvailableCases'>;

// Case interfaces
interface EmergencyCase {
    id: number;
    case_type: 'self' | 'loved_one';
    status: 'active' | 'attorney_assigned' | 'resolved';
    created_at: string;
    updated_at: string;
    urgency_level: 'urgent' | 'high' | 'medium' | 'low';
    detention_location: {
        description: string;
        city?: string;
        state?: string;
    };
    court_info: {
        court_name: string;
        court_abbreviation: string;
    };
    client_info: {
        first_name: string;
        last_name: string;
        case_type: 'self' | 'loved_one';
    };
    time_since_created: string;
    attorneys_notified_count: number;
}

interface CaseFilters {
    urgencyLevel: 'urgent' | 'high' | 'medium' | 'low' | 'all';
    caseType: 'self' | 'loved_one' | 'all';
    searchText: string;
}

const AvailableCasesScreen: React.FC = () => {
    const navigation = useNavigation<AvailableCasesNavigationProp>();
    const route = useRoute<AvailableCasesRouteProp>();
    const { isAttorney } = useAuth();

    const [cases, setCases] = useState<EmergencyCase[]>([]);
    const [loading, setLoading] = useState(true);
    const [refreshing, setRefreshing] = useState(false);
    const [showFilters, setShowFilters] = useState(false);
    const [selectedCaseId, setSelectedCaseId] = useState<number | null>(null);
    const [showCaseDetail, setShowCaseDetail] = useState(false);
    const [filters, setFilters] = useState<CaseFilters>({
        urgencyLevel: 'all',
        caseType: 'all',
        searchText: '',
    });

    // Redirect non-attorneys
    useEffect(() => {
        if (!isAttorney()) {
            Alert.alert(
                'Access Denied',
                'This section is only available to attorneys.',
                [{ text: 'OK', onPress: () => navigation.navigate('Home') }]
            );
        }
    }, [isAttorney, navigation]);

    // Load available cases
    const loadAvailableCases = useCallback(async (): Promise<void> => {
        try {
            // TODO: Replace with actual API call to /emergency/cases/available/{court_id}
            await new Promise(resolve => setTimeout(resolve, 1000));

            const mockCases: EmergencyCase[] = [
                {
                    id: 1,
                    case_type: 'self',
                    status: 'active',
                    created_at: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString(),
                    updated_at: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString(),
                    urgency_level: 'urgent',
                    detention_location: {
                        description: 'Los Angeles, CA',
                        city: 'Los Angeles',
                        state: 'CA',
                    },
                    court_info: {
                        court_name: 'Central District of California',
                        court_abbreviation: 'CD CA',
                    },
                    client_info: {
                        first_name: 'Maria',
                        last_name: 'G.',
                        case_type: 'self',
                    },
                    time_since_created: '2 hours ago',
                    attorneys_notified_count: 15,
                },
                {
                    id: 2,
                    case_type: 'loved_one',
                    status: 'active',
                    created_at: new Date(Date.now() - 5 * 60 * 60 * 1000).toISOString(),
                    updated_at: new Date(Date.now() - 5 * 60 * 60 * 1000).toISOString(),
                    urgency_level: 'high',
                    detention_location: {
                        description: 'San Francisco, CA',
                        city: 'San Francisco',
                        state: 'CA',
                    },
                    court_info: {
                        court_name: 'Northern District of California',
                        court_abbreviation: 'ND CA',
                    },
                    client_info: {
                        first_name: 'Carlos',
                        last_name: 'R.',
                        case_type: 'loved_one',
                    },
                    time_since_created: '5 hours ago',
                    attorneys_notified_count: 8,
                },
                {
                    id: 3,
                    case_type: 'self',
                    status: 'active',
                    created_at: new Date(Date.now() - 1 * 60 * 60 * 1000).toISOString(),
                    updated_at: new Date(Date.now() - 1 * 60 * 60 * 1000).toISOString(),
                    urgency_level: 'medium',
                    detention_location: {
                        description: 'San Diego, CA',
                        city: 'San Diego',
                        state: 'CA',
                    },
                    court_info: {
                        court_name: 'Southern District of California',
                        court_abbreviation: 'SD CA',
                    },
                    client_info: {
                        first_name: 'Ana',
                        last_name: 'M.',
                        case_type: 'self',
                    },
                    time_since_created: '1 hour ago',
                    attorneys_notified_count: 12,
                },
            ];

            setCases(mockCases);
        } catch (error) {
            console.error('Failed to load available cases:', error);
            Alert.alert('Error', 'Failed to load cases. Please try again.');
        } finally {
            setLoading(false);
            setRefreshing(false);
        }
    }, []);

    useEffect(() => {
        loadAvailableCases();
    }, [loadAvailableCases]);

    const onRefresh = (): void => {
        setRefreshing(true);
        loadAvailableCases();
    };

    // Filter cases
    const filteredCases = cases.filter(case_ => {
        if (filters.urgencyLevel !== 'all' && case_.urgency_level !== filters.urgencyLevel) {
            return false;
        }
        if (filters.caseType !== 'all' && case_.case_type !== filters.caseType) {
            return false;
        }
        if (filters.searchText) {
            const searchLower = filters.searchText.toLowerCase();
            return (
                case_.client_info.first_name.toLowerCase().includes(searchLower) ||
                case_.client_info.last_name.toLowerCase().includes(searchLower) ||
                case_.detention_location.description.toLowerCase().includes(searchLower) ||
                case_.court_info.court_name.toLowerCase().includes(searchLower)
            );
        }
        return true;
    });

    // Handle case detail view
    const handleViewCase = (caseId: number): void => {
        setSelectedCaseId(caseId);
        setShowCaseDetail(true);
    };

    const handleCloseCaseDetail = (): void => {
        setShowCaseDetail(false);
        setSelectedCaseId(null);
    };

    // Handle case acceptance from modal
    const handleAcceptCaseFromModal = async (caseId: number): Promise<void> => {
        try {
            // Remove the case from the list since it's now accepted
            setCases(prevCases => prevCases.filter(case_ => case_.id !== caseId));
            // Refresh the list to get updated data
            loadAvailableCases();
        } catch (error) {
            console.error('Failed to refresh cases after acceptance:', error);
        }
    };

    // Handle case acceptance (quick accept from list)
    const handleAcceptCase = (caseId: number): void => {
        Alert.alert(
            'Accept Case',
            'Are you sure you want to accept this emergency case?',
            [
                { text: 'Cancel', style: 'cancel' },
                {
                    text: 'View Details',
                    style: 'default',
                    onPress: () => handleViewCase(caseId),
                },
                {
                    text: 'Quick Accept',
                    style: 'default',
                    onPress: () => acceptCase(caseId),
                },
            ]
        );
    };

    const acceptCase = async (caseId: number): Promise<void> => {
        try {
            // TODO: Replace with actual API call to /emergency/cases/{case_id}/accept
            Alert.alert('Case Accepted', 'You have successfully accepted this case.');
            await handleAcceptCaseFromModal(caseId);
        } catch (error) {
            console.error('Failed to accept case:', error);
            Alert.alert('Error', 'Failed to accept case. Please try again.');
        }
    };

    // Get urgency color
    const getUrgencyColor = (urgency: string): string => {
        switch (urgency) {
            case 'urgent': return '#dc2626';
            case 'high': return '#ea580c';
            case 'medium': return '#d97706';
            case 'low': return '#65a30d';
            default: return '#6b7280';
        }
    };

    // Render case item
    const renderCaseItem = ({ item }: { item: EmergencyCase }) => (
        <TouchableOpacity
            style={styles.caseCard}
            onPress={() => handleViewCase(item.id)}
            activeOpacity={0.7}
        >
            <View style={styles.caseHeader}>
                <View style={styles.caseHeaderLeft}>
                    <View style={[styles.urgencyBadge, { backgroundColor: getUrgencyColor(item.urgency_level) }]}>
                        <Text style={styles.urgencyText}>{item.urgency_level.toUpperCase()}</Text>
                    </View>
                    <Text style={styles.caseType}>
                        {item.case_type === 'self' ? '👤 Self' : '👥 Loved One'}
                    </Text>
                </View>
                <Text style={styles.timeAgo}>{item.time_since_created}</Text>
            </View>

            <View style={styles.caseBody}>
                <Text style={styles.clientName}>
                    {item.client_info.first_name} {item.client_info.last_name}
                </Text>
                <Text style={styles.location}>📍 {item.detention_location.description}</Text>
                <Text style={styles.court}>⚖️ {item.court_info.court_name}</Text>
                <Text style={styles.notificationCount}>
                    📧 {item.attorneys_notified_count} attorneys notified
                </Text>
            </View>

            <TouchableOpacity
                style={styles.acceptButton}
                onPress={() => handleAcceptCase(item.id)}
            >
                <Text style={styles.acceptButtonText}>Accept Case</Text>
            </TouchableOpacity>
        </TouchableOpacity>
    );

    if (loading) {
        return (
            <SafeAreaView style={styles.container}>
                <View style={styles.loadingContainer}>
                    <ActivityIndicator size="large" color="#007AFF" />
                    <Text style={styles.loadingText}>Loading available cases...</Text>
                </View>
            </SafeAreaView>
        );
    }

    return (
        <SafeAreaView style={styles.container}>
            {/* Header */}
            <View style={styles.header}>
                <Text style={styles.headerTitle}>Available Cases ({filteredCases.length})</Text>
                <TouchableOpacity
                    style={styles.filterButton}
                    onPress={() => setShowFilters(true)}
                >
                    <Text style={styles.filterButtonText}>Filter</Text>
                </TouchableOpacity>
            </View>

            {/* Cases List */}
            <FlatList
                data={filteredCases}
                renderItem={renderCaseItem}
                keyExtractor={(item) => item.id.toString()}
                contentContainerStyle={styles.listContainer}
                refreshControl={
                    <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
                }
                ListEmptyComponent={
                    <View style={styles.emptyContainer}>
                        <Text style={styles.emptyText}>No cases available</Text>
                        <Text style={styles.emptySubtext}>
                            Pull to refresh or adjust your filters
                        </Text>
                    </View>
                }
            />

            {/* Filters Modal */}
            <Modal
                visible={showFilters}
                animationType="slide"
                presentationStyle="pageSheet"
                onRequestClose={() => setShowFilters(false)}
            >
                <SafeAreaView style={styles.filtersContainer}>
                    <View style={styles.filtersHeader}>
                        <Text style={styles.filtersTitle}>Filter Cases</Text>
                        <TouchableOpacity onPress={() => setShowFilters(false)}>
                            <Text style={styles.filtersClose}>Done</Text>
                        </TouchableOpacity>
                    </View>

                    <View style={styles.filtersContent}>
                        {/* Search */}
                        <View style={styles.filterSection}>
                            <Text style={styles.filterLabel}>Search</Text>
                            <TextInput
                                style={styles.searchInput}
                                placeholder="Search by name, location, or court..."
                                value={filters.searchText}
                                onChangeText={(text) => setFilters(prev => ({ ...prev, searchText: text }))}
                            />
                        </View>

                        {/* Urgency Level */}
                        <View style={styles.filterSection}>
                            <Text style={styles.filterLabel}>Urgency Level</Text>
                            <View style={styles.filterOptions}>
                                {['all', 'urgent', 'high', 'medium', 'low'].map((level) => (
                                    <TouchableOpacity
                                        key={level}
                                        style={[
                                            styles.filterOption,
                                            filters.urgencyLevel === level && styles.filterOptionSelected,
                                        ]}
                                        onPress={() => setFilters(prev => ({
                                            ...prev,
                                            urgencyLevel: level as CaseFilters['urgencyLevel'],
                                        }))}
                                    >
                                        <Text
                                            style={[
                                                styles.filterOptionText,
                                                filters.urgencyLevel === level && styles.filterOptionTextSelected,
                                            ]}
                                        >
                                            {level === 'all' ? 'All' : level.charAt(0).toUpperCase() + level.slice(1)}
                                        </Text>
                                    </TouchableOpacity>
                                ))}
                            </View>
                        </View>

                        {/* Case Type */}
                        <View style={styles.filterSection}>
                            <Text style={styles.filterLabel}>Case Type</Text>
                            <View style={styles.filterOptions}>
                                {[
                                    { key: 'all', label: 'All' },
                                    { key: 'self', label: 'Self' },
                                    { key: 'loved_one', label: 'Loved One' },
                                ].map((type) => (
                                    <TouchableOpacity
                                        key={type.key}
                                        style={[
                                            styles.filterOption,
                                            filters.caseType === type.key && styles.filterOptionSelected,
                                        ]}
                                        onPress={() => setFilters(prev => ({
                                            ...prev,
                                            caseType: type.key as CaseFilters['caseType'],
                                        }))}
                                    >
                                        <Text
                                            style={[
                                                styles.filterOptionText,
                                                filters.caseType === type.key && styles.filterOptionTextSelected,
                                            ]}
                                        >
                                            {type.label}
                                        </Text>
                                    </TouchableOpacity>
                                ))}
                            </View>
                        </View>
                    </View>
                </SafeAreaView>
            </Modal>

            {/* Case Detail Modal */}
            <CaseDetailModal
                visible={showCaseDetail}
                caseId={selectedCaseId}
                onClose={handleCloseCaseDetail}
                onAccept={handleAcceptCaseFromModal}
            />
        </SafeAreaView>
    );
};

const styles = StyleSheet.create({
    acceptButton: {
        alignItems: 'center',
        backgroundColor: '#007AFF',
        borderRadius: 8,
        paddingVertical: 12,
    },
    acceptButtonText: {
        color: '#fff',
        fontSize: 16,
        fontWeight: '600',
    },
    caseBody: {
        marginBottom: 16,
    },
    caseCard: {
        backgroundColor: '#fff',
        borderRadius: 12,
        elevation: 5,
        marginBottom: 16,
        padding: 16,
        shadowColor: '#000',
        shadowOffset: { width: 0, height: 2 },
        shadowOpacity: 0.1,
        shadowRadius: 3.84,
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
        gap: 8,
    },
    caseType: {
        color: '#666',
        fontSize: 14,
        fontWeight: '500',
    },
    clientName: {
        color: '#333',
        fontSize: 18,
        fontWeight: 'bold',
        marginBottom: 8,
    },
    container: {
        backgroundColor: '#f5f5f5',
        flex: 1,
    },
    court: {
        color: '#666',
        fontSize: 14,
        marginBottom: 4,
    },
    emptyContainer: {
        alignItems: 'center',
        flex: 1,
        justifyContent: 'center',
        paddingVertical: 60,
    },
    emptySubtext: {
        color: '#999',
        fontSize: 14,
        textAlign: 'center',
    },
    emptyText: {
        color: '#666',
        fontSize: 18,
        fontWeight: '600',
        marginBottom: 8,
    },
    filterButton: {
        backgroundColor: '#007AFF',
        borderRadius: 6,
        paddingHorizontal: 16,
        paddingVertical: 8,
    },
    filterButtonText: {
        color: '#fff',
        fontSize: 14,
        fontWeight: '600',
    },
    filterLabel: {
        color: '#333',
        fontSize: 16,
        fontWeight: '600',
        marginBottom: 12,
    },
    filterOption: {
        backgroundColor: '#fff',
        borderColor: '#e0e0e0',
        borderRadius: 8,
        borderWidth: 1,
        paddingHorizontal: 16,
        paddingVertical: 8,
    },
    filterOptionSelected: {
        backgroundColor: '#007AFF',
        borderColor: '#007AFF',
    },
    filterOptionText: {
        color: '#333',
        fontSize: 14,
        fontWeight: '500',
    },
    filterOptionTextSelected: {
        color: '#fff',
    },
    filterOptions: {
        flexDirection: 'row',
        flexWrap: 'wrap',
        gap: 8,
    },
    filterSection: {
        marginBottom: 24,
    },
    filtersClose: {
        color: '#007AFF',
        fontSize: 16,
        fontWeight: '600',
    },
    filtersContainer: {
        backgroundColor: '#f5f5f5',
        flex: 1,
    },
    filtersContent: {
        flex: 1,
        padding: 16,
    },
    filtersHeader: {
        alignItems: 'center',
        backgroundColor: '#fff',
        borderBottomColor: '#e0e0e0',
        borderBottomWidth: 1,
        flexDirection: 'row',
        justifyContent: 'space-between',
        padding: 16,
    },
    filtersTitle: {
        color: '#333',
        fontSize: 18,
        fontWeight: 'bold',
    },
    header: {
        alignItems: 'center',
        backgroundColor: '#fff',
        borderBottomColor: '#e0e0e0',
        borderBottomWidth: 1,
        flexDirection: 'row',
        justifyContent: 'space-between',
        padding: 16,
    },
    headerTitle: {
        color: '#333',
        fontSize: 20,
        fontWeight: 'bold',
    },
    listContainer: {
        padding: 16,
    },
    loadingContainer: {
        alignItems: 'center',
        flex: 1,
        justifyContent: 'center',
    },
    loadingText: {
        color: '#666',
        fontSize: 16,
        marginTop: 10,
    },
    location: {
        color: '#666',
        fontSize: 14,
        marginBottom: 4,
    },
    notificationCount: {
        color: '#999',
        fontSize: 12,
    },
    searchInput: {
        backgroundColor: '#fff',
        borderColor: '#e0e0e0',
        borderRadius: 8,
        borderWidth: 1,
        fontSize: 16,
        padding: 12,
    },
    timeAgo: {
        color: '#999',
        fontSize: 12,
    },
    urgencyBadge: {
        borderRadius: 4,
        paddingHorizontal: 8,
        paddingVertical: 4,
    },
    urgencyText: {
        color: '#fff',
        fontSize: 12,
        fontWeight: 'bold',
    },
});

export default AvailableCasesScreen;
