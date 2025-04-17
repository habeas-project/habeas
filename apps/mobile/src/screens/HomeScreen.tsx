import React, { useEffect, useState } from 'react';
import { View, Text, StyleSheet, FlatList, ActivityIndicator, TouchableOpacity } from 'react-native';
import api from '../api/client';


export default function HomeScreen({ navigation }: any) {


    return (
        <View style={styles.container}>
            <Text style={styles.title}>Welcome to Habeas</Text>
            <Text style={styles.description}>
                Connecting detained individuals with legal representatives
            </Text>

            <TouchableOpacity
                style={styles.signupButton}
                onPress={() => navigation.navigate('AttorneySignup')}
            >
                <Text style={styles.signupButtonText}>Register as an Attorney</Text>
            </TouchableOpacity>

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
        marginBottom: 20,
    },
    signupButton: {
        backgroundColor: '#4a90e2',
        padding: 15,
        borderRadius: 5,
        alignItems: 'center',
        marginBottom: 30,
        textAlign: 'center',
    },
    signupButtonText: {
        color: '#fff',
        fontSize: 16,
        fontWeight: '600',
    },
    loader: {
        marginTop: 20,
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
