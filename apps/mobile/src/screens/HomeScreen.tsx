import React, { useEffect, useState } from 'react';
import { View, Text, StyleSheet, FlatList, ActivityIndicator } from 'react-native';
import api from '../api/client';

// Define the Example type based on our API schema
type Example = {
    id: number;
    name: string;
    description?: string;
};

export default function HomeScreen() {
    const [examples, setExamples] = useState<Example[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');

    useEffect(() => {
        const fetchExamples = async () => {
            try {
                setLoading(true);
                const data = await api.getExamples();
                setExamples(data);
                setError('');
            } catch (err) {
                console.error('Error fetching examples:', err);
                setError('Failed to fetch examples. The API might not be running.');
            } finally {
                setLoading(false);
            }
        };

        fetchExamples();
    }, []);

    return (
        <View style={styles.container}>
            <Text style={styles.title}>Welcome to Habeas</Text>
            <Text style={styles.description}>
                Connecting detained individuals with legal representatives
            </Text>

            {loading ? (
                <ActivityIndicator size="large" color="#0000ff" style={styles.loader} />
            ) : error ? (
                <Text style={styles.error}>{error}</Text>
            ) : (
                <View style={styles.examplesContainer}>
                    <Text style={styles.sectionTitle}>Examples from API:</Text>
                    <FlatList
                        data={examples}
                        keyExtractor={(item) => item.id.toString()}
                        renderItem={({ item }) => (
                            <View style={styles.exampleItem}>
                                <Text style={styles.exampleName}>{item.name}</Text>
                                {item.description && (
                                    <Text style={styles.exampleDescription}>{item.description}</Text>
                                )}
                            </View>
                        )}
                        ListEmptyComponent={
                            <Text style={styles.emptyMessage}>No examples found</Text>
                        }
                    />
                </View>
            )}
        </View>
    );
}

const styles = StyleSheet.create({
    container: {
        flex: 1,
        padding: 20,
    },
    title: {
        fontSize: 24,
        fontWeight: 'bold',
        marginTop: 40,
        marginBottom: 16,
        textAlign: 'center',
    },
    description: {
        fontSize: 16,
        textAlign: 'center',
        color: '#555',
        marginBottom: 30,
    },
    loader: {
        marginTop: 20,
    },
    error: {
        color: 'red',
        textAlign: 'center',
        marginTop: 20,
    },
    examplesContainer: {
        flex: 1,
    },
    sectionTitle: {
        fontSize: 18,
        fontWeight: 'bold',
        marginBottom: 10,
    },
    exampleItem: {
        backgroundColor: '#f5f5f5',
        padding: 15,
        borderRadius: 5,
        marginBottom: 10,
    },
    exampleName: {
        fontSize: 16,
        fontWeight: 'bold',
    },
    exampleDescription: {
        fontSize: 14,
        color: '#666',
        marginTop: 5,
    },
    emptyMessage: {
        textAlign: 'center',
        color: '#666',
        fontStyle: 'italic',
    },
}); 