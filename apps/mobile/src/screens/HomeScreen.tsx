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
    description: {
        color: '#555',
        fontSize: 16,
        marginBottom: 30,
        textAlign: 'center',
    },
    emptyMessage: {
        color: '#666',
        fontStyle: 'italic',
        textAlign: 'center',
    },
    error: {
        color: 'red',
        marginTop: 20,
        textAlign: 'center',
    },
    exampleDescription: {
        color: '#666',
        fontSize: 14,
        marginTop: 5,
    },
    exampleItem: {
        backgroundColor: '#f5f5f5',
        borderRadius: 5,
        marginBottom: 10,
        padding: 15,
    },
    exampleName: {
        fontSize: 16,
        fontWeight: 'bold',
    },
    examplesContainer: {
        flex: 1,
    },
    loader: {
        marginTop: 20,
    },
    sectionTitle: {
        fontSize: 18,
        fontWeight: 'bold',
        marginBottom: 10,
    },
    title: {
        fontSize: 24,
        fontWeight: 'bold',
        marginBottom: 16,
        marginTop: 40,
        textAlign: 'center',
    },
});
