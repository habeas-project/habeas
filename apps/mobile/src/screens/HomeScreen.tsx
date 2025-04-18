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

            <TouchableOpacity
                style={styles.personalInfoButton}
                onPress={() => navigation.navigate('PersonalInfo')}
            >
                <Text style={styles.buttonText}>Personal Information</Text>
            </TouchableOpacity>

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
        marginBottom: 20,
    },
    signupButton: {
        backgroundColor: '#4a90e2',
        padding: 15,
        borderRadius: 5,
        alignItems: 'center',
        marginBottom: 30,
    },
    signupButtonText: {
        color: '#fff',
        fontSize: 16,
        fontWeight: '600',
    },
    personalInfoButton: {
        backgroundColor: '#28a745',
        padding: 15,
        borderRadius: 5,
        alignItems: 'center',
        marginBottom: 30,
    },
    buttonText: {
        color: '#fff',
        fontSize: 16,
        fontWeight: '600',
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