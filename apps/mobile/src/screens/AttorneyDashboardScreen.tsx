import React, { useEffect, useState } from 'react';
import {
    View,
    Text,
    StyleSheet,
    ScrollView,
    TouchableOpacity,
    RefreshControl,
    Alert,
    ActivityIndicator,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useNavigation } from '@react-navigation/native';
import { NativeStackNavigationProp } from '@react-navigation/native-stack';

import { useAuth } from '../contexts/AuthContext';
import { RootStackParamList } from '../App';

// Navigation type
type AttorneyDashboardNavigationProp = NativeStackNavigationProp<
    RootStackParamList,
    'AttorneyDashboard'
>;

// Dashboard statistics interface
interface DashboardStats {
    activeCases: number;
    availableCases: number;
    courtCoverage: string[];
    responseTimeAvg: number;
    totalCasesHandled: number;
    unreadNotifications: number;
}

const AttorneyDashboardScreen: React.FC = () => {
    const navigation = useNavigation<AttorneyDashboardNavigationProp>();
    const { user, isAttorney, logout } = useAuth();
    const [stats, setStats] = useState<DashboardStats | null>(null);
    const [loading, setLoading] = useState(true);
    const [refreshing, setRefreshing] = useState(false);

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

    // Load dashboard data
    const loadDashboardData = async (): Promise<void> => {
        try {
            // TODO: Replace with actual API calls
            await new Promise(resolve => setTimeout(resolve, 1000));

            const mockStats: DashboardStats = {
                activeCases: 3,
                availableCases: 12,
                courtCoverage: ['Central District of California', 'Northern District of California'],
                responseTimeAvg: 45,
                totalCasesHandled: 28,
                unreadNotifications: 5,
            };

            setStats(mockStats);
        } catch (error) {
            console.error('Failed to load dashboard data:', error);
            Alert.alert('Error', 'Failed to load dashboard data. Please try again.');
        } finally {
            setLoading(false);
            setRefreshing(false);
        }
    };

    useEffect(() => {
        loadDashboardData();
    }, []);

    const onRefresh = (): void => {
        setRefreshing(true);
        loadDashboardData();
    };

    const handleLogout = (): void => {
        Alert.alert(
            'Sign Out',
            'Are you sure you want to sign out?',
            [
                { text: 'Cancel', style: 'cancel' },
                { text: 'Sign Out', style: 'destructive', onPress: logout },
            ]
        );
    };

    // Navigation handlers
    const navigateToAvailableCases = (): void => {
        navigation.navigate('AvailableCases', {});
    };

    const navigateToNotificationPreferences = (): void => {
        Alert.alert('Coming Soon', 'Notification Preferences screen will be implemented next.');
    };

    const navigateToDailyDigest = (): void => {
        Alert.alert('Coming Soon', 'Daily Digest screen will be implemented next.');
    };

    const navigateToProfile = (): void => {
        Alert.alert('Coming Soon', 'Attorney Profile screen will be implemented next.');
    };

    if (loading) {
        return (
            <SafeAreaView style={styles.container}>
                <View style={styles.loadingContainer}>
                    <ActivityIndicator size="large" color="#007AFF" />
                    <Text style={styles.loadingText}>Loading dashboard...</Text>
                </View>
            </SafeAreaView>
        );
    }

    return (
        <SafeAreaView style={styles.container}>
            <ScrollView
                style={styles.scrollView}
                refreshControl={
                    <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
                }
            >
                {/* Header */}
                <View style={styles.header}>
                    <View>
                        <Text style={styles.welcomeText}>Welcome back,</Text>
                        <Text style={styles.nameText}>{user?.email}</Text>
                    </View>
                    <TouchableOpacity style={styles.logoutButton} onPress={handleLogout}>
                        <Text style={styles.logoutText}>Sign Out</Text>
                    </TouchableOpacity>
                </View>

                {/* Statistics Cards */}
                <View style={styles.statsContainer}>
                    <View style={styles.statsRow}>
                        <View style={[styles.statCard, styles.primaryCard]}>
                            <Text style={[styles.statNumber, styles.whiteText]}>{stats?.activeCases || 0}</Text>
                            <Text style={[styles.statLabel, styles.whiteText]}>Active Cases</Text>
                        </View>
                        <View style={[styles.statCard, styles.secondaryCard]}>
                            <Text style={[styles.statNumber, styles.whiteText]}>{stats?.availableCases || 0}</Text>
                            <Text style={[styles.statLabel, styles.whiteText]}>Available Cases</Text>
                        </View>
                    </View>

                    <View style={styles.statsRow}>
                        <View style={styles.statCard}>
                            <Text style={styles.statNumber}>{stats?.totalCasesHandled || 0}</Text>
                            <Text style={styles.statLabel}>Total Cases</Text>
                        </View>
                        <View style={styles.statCard}>
                            <Text style={styles.statNumber}>{stats?.responseTimeAvg || 0}m</Text>
                            <Text style={styles.statLabel}>Avg Response</Text>
                        </View>
                    </View>
                </View>

                {/* Court Coverage */}
                <View style={styles.section}>
                    <Text style={styles.sectionTitle}>Court Coverage</Text>
                    {stats?.courtCoverage.map((court, index) => (
                        <View key={index} style={styles.courtItem}>
                            <Text style={styles.courtName}>{court}</Text>
                        </View>
                    ))}
                </View>

                {/* Quick Actions */}
                <View style={styles.section}>
                    <Text style={styles.sectionTitle}>Quick Actions</Text>

                    <TouchableOpacity style={styles.actionButton} onPress={navigateToAvailableCases}>
                        <Text style={styles.actionButtonText}>View Available Cases</Text>
                        <Text style={styles.actionButtonSubtext}>
                            {stats?.availableCases} cases need attorney
                        </Text>
                    </TouchableOpacity>

                    <TouchableOpacity style={styles.actionButton} onPress={navigateToDailyDigest}>
                        <Text style={styles.actionButtonText}>Daily Digest</Text>
                        <Text style={styles.actionButtonSubtext}>
                            Review unassigned cases across all districts
                        </Text>
                    </TouchableOpacity>

                    <TouchableOpacity style={styles.actionButton} onPress={navigateToNotificationPreferences}>
                        <Text style={styles.actionButtonText}>Notification Settings</Text>
                        <Text style={styles.actionButtonSubtext}>
                            {stats?.unreadNotifications} unread notifications
                        </Text>
                    </TouchableOpacity>

                    <TouchableOpacity style={styles.actionButton} onPress={navigateToProfile}>
                        <Text style={styles.actionButtonText}>Attorney Profile</Text>
                        <Text style={styles.actionButtonSubtext}>
                            Manage court admissions and profile
                        </Text>
                    </TouchableOpacity>
                </View>
            </ScrollView>
        </SafeAreaView>
    );
};

const styles = StyleSheet.create({
    actionButton: {
        backgroundColor: '#f8f9fa',
        borderLeftColor: '#007AFF',
        borderLeftWidth: 4,
        borderRadius: 8,
        marginBottom: 12,
        padding: 16,
    },
    actionButtonSubtext: {
        color: '#666',
        fontSize: 14,
    },
    actionButtonText: {
        color: '#333',
        fontSize: 16,
        fontWeight: '600',
        marginBottom: 4,
    },
    container: {
        backgroundColor: '#f5f5f5',
        flex: 1,
    },
    courtItem: {
        borderBottomColor: '#f0f0f0',
        borderBottomWidth: 1,
        paddingVertical: 8,
    },
    courtName: {
        color: '#333',
        fontSize: 16,
    },
    header: {
        alignItems: 'center',
        backgroundColor: '#fff',
        borderBottomColor: '#e0e0e0',
        borderBottomWidth: 1,
        flexDirection: 'row',
        justifyContent: 'space-between',
        padding: 20,
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
    logoutButton: {
        borderColor: '#007AFF',
        borderRadius: 6,
        borderWidth: 1,
        paddingHorizontal: 12,
        paddingVertical: 6,
    },
    logoutText: {
        color: '#007AFF',
        fontSize: 14,
    },
    nameText: {
        color: '#333',
        fontSize: 18,
        fontWeight: 'bold',
    },
    primaryCard: {
        backgroundColor: '#007AFF',
    },
    scrollView: {
        flex: 1,
    },
    secondaryCard: {
        backgroundColor: '#FF9500',
    },
    section: {
        backgroundColor: '#fff',
        borderRadius: 12,
        elevation: 5,
        margin: 16,
        marginTop: 0,
        padding: 20,
        shadowColor: '#000',
        shadowOffset: {
            width: 0,
            height: 2,
        },
        shadowOpacity: 0.1,
        shadowRadius: 3.84,
    },
    sectionTitle: {
        color: '#333',
        fontSize: 18,
        fontWeight: 'bold',
        marginBottom: 16,
    },
    statCard: {
        alignItems: 'center',
        backgroundColor: '#fff',
        borderRadius: 12,
        elevation: 5,
        flex: 1,
        padding: 20,
        shadowColor: '#000',
        shadowOffset: {
            width: 0,
            height: 2,
        },
        shadowOpacity: 0.1,
        shadowRadius: 3.84,
    },
    statLabel: {
        color: '#666',
        fontSize: 14,
        textAlign: 'center',
    },
    statNumber: {
        color: '#333',
        fontSize: 28,
        fontWeight: 'bold',
        marginBottom: 4,
    },
    statsContainer: {
        padding: 16,
    },
    statsRow: {
        flexDirection: 'row',
        gap: 12,
        marginBottom: 12,
    },
    welcomeText: {
        color: '#666',
        fontSize: 16,
    },
    whiteText: {
        color: '#fff',
    },
});

export default AttorneyDashboardScreen;
