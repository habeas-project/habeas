/**
 * Log Viewer Modal - Development Tool
 * Shows captured logs for debugging purposes
 */

import React, { useState, useEffect } from 'react';
import {
    Modal,
    View,
    Text,
    ScrollView,
    TouchableOpacity,
    StyleSheet,
    SafeAreaView,
    Alert,
} from 'react-native';
import { logger, LogLevel, LogCategory, LogEntry } from '../utils/logger';

interface LogViewerModalProps {
    visible: boolean;
    onClose: () => void;
}

export const LogViewerModal: React.FC<LogViewerModalProps> = ({ visible, onClose }) => {
    const [logs, setLogs] = useState<LogEntry[]>([]);
    const [selectedCategory, setSelectedCategory] = useState<LogCategory | 'ALL'>('ALL');
    const selectedLevel = LogLevel.DEBUG;

    useEffect(() => {
        if (visible) {
            loadLogs();
        }
    }, [visible, selectedCategory]);

    const loadLogs = () => {
        const categoryFilter = selectedCategory === 'ALL' ? undefined : selectedCategory;
        const filteredLogs = logger.getLogs(categoryFilter, selectedLevel, 100);
        setLogs(filteredLogs);
    };

    const exportLogs = async () => {
        try {
            const exportData = await logger.exportLogs();
            // In a real app, you would use a file sharing API
            Alert.alert(
                'Logs Exported',
                'Log data has been prepared for export. In production, this would be saved to file or sent to analytics.',
                [{ text: 'OK' }]
            );
            console.log('EXPORT DATA:', exportData);
        } catch {
            Alert.alert('Export Failed', 'Failed to export logs');
        }
    };

    const clearLogs = () => {
        Alert.alert(
            'Clear Logs',
            'Are you sure you want to clear all logs?',
            [
                { text: 'Cancel', style: 'cancel' },
                {
                    text: 'Clear',
                    style: 'destructive',
                    onPress: () => {
                        logger.clearLogs();
                        setLogs([]);
                    },
                },
            ]
        );
    };

    const getLevelColor = (level: LogLevel): string => {
        switch (level) {
            case LogLevel.DEBUG:
                return '#666';
            case LogLevel.INFO:
                return '#007AFF';
            case LogLevel.WARN:
                return '#FF9500';
            case LogLevel.ERROR:
            case LogLevel.FATAL:
                return '#FF3B30';
            default:
                return '#000';
        }
    };

    const formatTimestamp = (timestamp: string): string => {
        return new Date(timestamp).toLocaleTimeString();
    };

    if (!__DEV__) {
        return null; // Only show in development
    }

    return (
        <Modal visible={visible} animationType="slide" presentationStyle="fullScreen">
            <SafeAreaView style={styles.container}>
                <View style={styles.header}>
                    <Text style={styles.title}>📊 App Logs</Text>
                    <TouchableOpacity onPress={onClose} style={styles.closeButton}>
                        <Text style={styles.closeButtonText}>Close</Text>
                    </TouchableOpacity>
                </View>

                <View style={styles.controls}>
                    <ScrollView horizontal showsHorizontalScrollIndicator={false}>
                        <TouchableOpacity
                            style={[
                                styles.filterButton,
                                selectedCategory === 'ALL' && styles.activeFilter,
                            ]}
                            onPress={() => setSelectedCategory('ALL')}
                        >
                            <Text style={styles.filterText}>ALL</Text>
                        </TouchableOpacity>
                        {Object.values(LogCategory).map((category) => (
                            <TouchableOpacity
                                key={category}
                                style={[
                                    styles.filterButton,
                                    selectedCategory === category && styles.activeFilter,
                                ]}
                                onPress={() => setSelectedCategory(category)}
                            >
                                <Text style={styles.filterText}>{category}</Text>
                            </TouchableOpacity>
                        ))}
                    </ScrollView>
                </View>

                <View style={styles.actions}>
                    <TouchableOpacity onPress={exportLogs} style={styles.actionButton}>
                        <Text style={styles.actionButtonText}>📤 Export</Text>
                    </TouchableOpacity>
                    <TouchableOpacity onPress={clearLogs} style={styles.actionButton}>
                        <Text style={styles.actionButtonText}>🗑️ Clear</Text>
                    </TouchableOpacity>
                    <TouchableOpacity onPress={loadLogs} style={styles.actionButton}>
                        <Text style={styles.actionButtonText}>🔄 Refresh</Text>
                    </TouchableOpacity>
                </View>

                <ScrollView style={styles.logContainer}>
                    {logs.map((log, index) => (
                        <View key={index} style={styles.logEntry}>
                            <View style={styles.logHeader}>
                                <Text style={styles.timestamp}>
                                    {formatTimestamp(log.timestamp)}
                                </Text>
                                <Text
                                    style={[
                                        styles.level,
                                        { color: getLevelColor(log.level) },
                                    ]}
                                >
                                    {LogLevel[log.level]}
                                </Text>
                                <Text style={styles.category}>{log.category}</Text>
                            </View>
                            <Text style={styles.message}>{log.message}</Text>
                            {log.context && (
                                <Text style={styles.context}>
                                    {JSON.stringify(log.context, null, 2)}
                                </Text>
                            )}
                            {log.stackTrace && (
                                <Text style={styles.stackTrace}>{log.stackTrace}</Text>
                            )}
                        </View>
                    ))}
                    {logs.length === 0 && (
                        <View style={styles.emptyState}>
                            <Text style={styles.emptyText}>No logs found</Text>
                        </View>
                    )}
                </ScrollView>
            </SafeAreaView>
        </Modal>
    );
};

const styles = StyleSheet.create({
    actionButton: {
        backgroundColor: '#444',
        borderRadius: 4,
        marginRight: 8,
        paddingHorizontal: 12,
        paddingVertical: 6,
    },
    actionButtonText: {
        color: '#fff',
        fontSize: 12,
    },
    actions: {
        borderBottomColor: '#333',
        borderBottomWidth: 1,
        flexDirection: 'row',
        padding: 16,
    },
    activeFilter: {
        backgroundColor: '#007AFF',
    },
    category: {
        color: '#999',
        fontSize: 12,
    },
    closeButton: {
        padding: 8,
    },
    closeButtonText: {
        color: '#007AFF',
        fontSize: 16,
    },
    container: {
        backgroundColor: '#000',
        flex: 1,
    },
    context: {
        backgroundColor: '#222',
        borderRadius: 4,
        color: '#ccc',
        fontFamily: 'monospace',
        fontSize: 12,
        marginTop: 4,
        padding: 8,
    },
    controls: {
        borderBottomColor: '#333',
        borderBottomWidth: 1,
        padding: 16,
    },
    emptyState: {
        alignItems: 'center',
        justifyContent: 'center',
        paddingVertical: 40,
    },
    emptyText: {
        color: '#666',
        fontSize: 16,
    },
    filterButton: {
        backgroundColor: '#333',
        borderRadius: 4,
        marginRight: 8,
        paddingHorizontal: 12,
        paddingVertical: 6,
    },
    filterText: {
        color: '#fff',
        fontSize: 12,
    },
    header: {
        alignItems: 'center',
        borderBottomColor: '#333',
        borderBottomWidth: 1,
        flexDirection: 'row',
        justifyContent: 'space-between',
        padding: 16,
    },
    level: {
        fontSize: 12,
        fontWeight: 'bold',
        marginRight: 8,
        minWidth: 50,
    },
    logContainer: {
        flex: 1,
        padding: 16,
    },
    logEntry: {
        backgroundColor: '#111',
        borderLeftColor: '#007AFF',
        borderLeftWidth: 3,
        borderRadius: 4,
        marginBottom: 12,
        padding: 12,
    },
    logHeader: {
        flexDirection: 'row',
        marginBottom: 8,
    },
    message: {
        color: '#fff',
        fontSize: 14,
        marginBottom: 4,
    },
    stackTrace: {
        color: '#f00',
        fontFamily: 'monospace',
        fontSize: 11,
        marginTop: 4,
    },
    timestamp: {
        color: '#666',
        fontSize: 12,
        marginRight: 8,
    },
    title: {
        color: '#fff',
        fontSize: 18,
        fontWeight: 'bold',
    },
});

export default LogViewerModal;
