import React, { useState } from 'react';
import {
    View,
    Text,
    StyleSheet,
    TextInput,
    TouchableOpacity,
    Alert,
} from 'react-native';

interface DetentionLocationInputProps {
    onLocationSubmit: (location: { description: string; zipCode?: string; city?: string; state?: string }) => void;
    onCancel: () => void;
    isLoading?: boolean;
}

const DetentionLocationInput: React.FC<DetentionLocationInputProps> = ({
    onLocationSubmit,
    onCancel,
    isLoading = false,
}) => {
    const [inputMethod, setInputMethod] = useState<'zipcode' | 'citystate'>('zipcode');
    const [zipCode, setZipCode] = useState('');
    const [city, setCity] = useState('');
    const [state, setState] = useState('');

    const validateAndSubmit = () => {
        if (inputMethod === 'zipcode') {
            if (!zipCode.trim()) {
                Alert.alert('Error', 'Please enter a zip code');
                return;
            }

            // Basic US zip code validation
            const zipRegex = /^\d{5}(-\d{4})?$/;
            if (!zipRegex.test(zipCode.trim())) {
                Alert.alert('Error', 'Please enter a valid US zip code (e.g., 12345 or 12345-6789)');
                return;
            }

            onLocationSubmit({
                description: `Zip Code: ${zipCode.trim()}`,
                zipCode: zipCode.trim(),
            });
        } else {
            if (!city.trim() || !state.trim()) {
                Alert.alert('Error', 'Please enter both city and state');
                return;
            }

            onLocationSubmit({
                description: `${city.trim()}, ${state.trim()}`,
                city: city.trim(),
                state: state.trim(),
            });
        }
    };

    return (
        <View style={styles.container}>
            {/* Header */}
            <View style={styles.header}>
                <Text style={styles.title}>Detention Location</Text>
                <Text style={styles.subtitle}>
                    Where approximately was your loved one detained?
                </Text>
            </View>

            {/* Input Method Selection */}
            <View style={styles.methodSelection}>
                <TouchableOpacity
                    style={[
                        styles.methodButton,
                        inputMethod === 'zipcode' && styles.methodButtonActive,
                    ]}
                    onPress={() => setInputMethod('zipcode')}
                >
                    <Text
                        style={[
                            styles.methodButtonText,
                            inputMethod === 'zipcode' && styles.methodButtonTextActive,
                        ]}
                    >
                        Zip Code
                    </Text>
                </TouchableOpacity>

                <TouchableOpacity
                    style={[
                        styles.methodButton,
                        inputMethod === 'citystate' && styles.methodButtonActive,
                    ]}
                    onPress={() => setInputMethod('citystate')}
                >
                    <Text
                        style={[
                            styles.methodButtonText,
                            inputMethod === 'citystate' && styles.methodButtonTextActive,
                        ]}
                    >
                        City & State
                    </Text>
                </TouchableOpacity>
            </View>

            {/* Input Fields */}
            {inputMethod === 'zipcode' ? (
                <View style={styles.inputContainer}>
                    <Text style={styles.inputLabel}>Zip Code</Text>
                    <TextInput
                        style={styles.textInput}
                        value={zipCode}
                        onChangeText={setZipCode}
                        placeholder="e.g., 12345"
                        keyboardType="numeric"
                        maxLength={10}
                        autoCapitalize="none"
                        autoCorrect={false}
                    />
                    <Text style={styles.inputHint}>
                        Enter the 5-digit zip code where the detention occurred
                    </Text>
                </View>
            ) : (
                <View style={styles.inputContainer}>
                    <View style={styles.cityStateContainer}>
                        <View style={styles.cityInputContainer}>
                            <Text style={styles.inputLabel}>City</Text>
                            <TextInput
                                style={styles.textInput}
                                value={city}
                                onChangeText={setCity}
                                placeholder="e.g., Los Angeles"
                                autoCapitalize="words"
                                autoCorrect={false}
                            />
                        </View>

                        <View style={styles.stateInputContainer}>
                            <Text style={styles.inputLabel}>State</Text>
                            <TextInput
                                style={styles.textInput}
                                value={state}
                                onChangeText={setState}
                                placeholder="e.g., CA"
                                maxLength={2}
                                autoCapitalize="characters"
                                autoCorrect={false}
                            />
                        </View>
                    </View>
                    <Text style={styles.inputHint}>
                        Enter the city and state abbreviation (e.g., CA, NY, TX)
                    </Text>
                </View>
            )}

            {/* Examples */}
            <View style={styles.examplesContainer}>
                <Text style={styles.examplesTitle}>Why we need this:</Text>
                <Text style={styles.examplesText}>
                    • Determines which federal district court has jurisdiction{'\n'}
                    • Notifies attorneys admitted to practice in that district{'\n'}
                    • Helps coordinate local legal resources
                </Text>
            </View>

            {/* Action Buttons */}
            <View style={styles.actionsContainer}>
                <TouchableOpacity
                    style={styles.submitButton}
                    onPress={validateAndSubmit}
                    disabled={isLoading}
                >
                    <Text style={styles.submitButtonText}>
                        {isLoading ? 'Creating Case...' : 'Submit Location'}
                    </Text>
                </TouchableOpacity>

                <TouchableOpacity
                    style={styles.cancelButton}
                    onPress={onCancel}
                    disabled={isLoading}
                >
                    <Text style={styles.cancelButtonText}>Cancel</Text>
                </TouchableOpacity>
            </View>
        </View>
    );
};

const styles = StyleSheet.create({
    actionsContainer: {
        gap: 12,
    },
    cancelButton: {
        alignItems: 'center',
        backgroundColor: 'transparent',
        borderColor: '#cbd5e0',
        borderRadius: 12,
        borderWidth: 1,
        paddingVertical: 16,
    },
    cancelButtonText: {
        color: '#4a5568',
        fontSize: 16,
        fontWeight: '500',
    },
    cityInputContainer: {
        flex: 2,
    },
    cityStateContainer: {
        flexDirection: 'row',
        gap: 12,
    },
    container: {
        backgroundColor: '#ffffff',
        padding: 24,
    },
    examplesContainer: {
        backgroundColor: '#f0f9ff',
        borderColor: '#bae6fd',
        borderRadius: 8,
        borderWidth: 1,
        marginBottom: 24,
        padding: 16,
    },
    examplesText: {
        color: '#0c4a6e',
        fontSize: 13,
        lineHeight: 18,
    },
    examplesTitle: {
        color: '#0369a1',
        fontSize: 14,
        fontWeight: '600',
        marginBottom: 8,
    },
    header: {
        alignItems: 'center',
        marginBottom: 24,
    },
    inputContainer: {
        marginBottom: 24,
    },
    inputHint: {
        color: '#6b7280',
        fontSize: 12,
        marginTop: 4,
    },
    inputLabel: {
        color: '#2d3748',
        fontSize: 14,
        fontWeight: '600',
        marginBottom: 8,
    },
    methodButton: {
        backgroundColor: '#f7fafc',
        borderColor: '#e2e8f0',
        borderRadius: 8,
        borderWidth: 1,
        flex: 1,
        marginHorizontal: 4,
        paddingVertical: 12,
    },
    methodButtonActive: {
        backgroundColor: '#3182ce',
        borderColor: '#3182ce',
    },
    methodButtonText: {
        color: '#4a5568',
        fontSize: 14,
        fontWeight: '600',
        textAlign: 'center',
    },
    methodButtonTextActive: {
        color: '#ffffff',
    },
    methodSelection: {
        flexDirection: 'row',
        marginBottom: 24,
    },
    stateInputContainer: {
        flex: 1,
    },
    submitButton: {
        alignItems: 'center',
        backgroundColor: '#c53030',
        borderRadius: 12,
        paddingVertical: 16,
    },
    submitButtonText: {
        color: '#ffffff',
        fontSize: 16,
        fontWeight: '600',
    },
    subtitle: {
        color: '#4a5568',
        fontSize: 16,
        lineHeight: 22,
        textAlign: 'center',
    },
    textInput: {
        backgroundColor: '#ffffff',
        borderColor: '#cbd5e0',
        borderRadius: 8,
        borderWidth: 1,
        fontSize: 16,
        paddingHorizontal: 12,
        paddingVertical: 12,
    },
    title: {
        color: '#c53030',
        fontSize: 20,
        fontWeight: '700',
        marginBottom: 8,
        textAlign: 'center',
    },
});

export default DetentionLocationInput;
