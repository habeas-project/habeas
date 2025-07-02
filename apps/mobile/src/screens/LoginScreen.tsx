import React, { useState } from 'react';
import {
    View,
    Text,
    TextInput,
    TouchableOpacity,
    StyleSheet,
    Alert,
    ActivityIndicator,
    KeyboardAvoidingView,
    Platform,
} from 'react-native';
import { useAuth } from '../contexts/AuthContext';

interface LoginScreenProps {
    navigation: {
        navigate: (screen: string) => void;
    };
}

const LoginScreen: React.FC<LoginScreenProps> = ({ navigation }) => {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const { login } = useAuth();

    const handleLogin = async () => {
        if (!email || !password) {
            Alert.alert('Error', 'Please enter both email and password');
            return;
        }

        setIsLoading(true);
        try {
            const success = await login(email, password);
            if (success) {
                // Navigation will be handled by the auth state change
                navigation.navigate('Home');
            } else {
                Alert.alert('Login Failed', 'Invalid credentials. Please try again.');
            }
        } catch (error) {
            console.error('Login error:', error);
            Alert.alert('Login Error', 'An error occurred during login. Please try again.');
        } finally {
            setIsLoading(false);
        }
    };

    const navigateToSignup = () => {
        navigation.navigate('UnifiedSignup');
    };

    return (
        <KeyboardAvoidingView
            style={styles.container}
            behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
        >
            <View style={styles.content}>
                <Text style={styles.title}>Habeas</Text>
                <Text style={styles.subtitle}>Emergency Legal Support</Text>

                <View style={styles.form}>
                    <TextInput
                        style={styles.input}
                        placeholder="Email"
                        value={email}
                        onChangeText={setEmail}
                        keyboardType="email-address"
                        autoCapitalize="none"
                        autoCorrect={false}
                        editable={!isLoading}
                    />

                    <TextInput
                        style={styles.input}
                        placeholder="Password"
                        value={password}
                        onChangeText={setPassword}
                        secureTextEntry
                        editable={!isLoading}
                    />

                    <TouchableOpacity
                        style={[styles.loginButton, isLoading && styles.disabledButton]}
                        onPress={handleLogin}
                        disabled={isLoading}
                    >
                        {isLoading ? (
                            <ActivityIndicator color="#ffffff" />
                        ) : (
                            <Text style={styles.loginButtonText}>Sign In</Text>
                        )}
                    </TouchableOpacity>

                    <TouchableOpacity
                        style={styles.signupButton}
                        onPress={navigateToSignup}
                        disabled={isLoading}
                    >
                        <Text style={styles.signupButtonText}>
                            Don&apos;t have an account? Get Help
                        </Text>
                    </TouchableOpacity>
                </View>

                <View style={styles.demoSection}>
                    <Text style={styles.demoTitle}>Demo Credentials:</Text>
                    <Text style={styles.demoText}>Email: demo@example.com</Text>
                    <Text style={styles.demoText}>Password: password123</Text>
                </View>
            </View>
        </KeyboardAvoidingView>
    );
};

const styles = StyleSheet.create({
    container: {
        backgroundColor: '#f5f5f5',
        flex: 1,
    },
    content: {
        flex: 1,
        justifyContent: 'center',
        paddingHorizontal: 30,
    },
    demoSection: {
        backgroundColor: '#ffffff',
        borderLeftColor: '#c00',
        borderLeftWidth: 4,
        borderRadius: 8,
        padding: 16,
    },
    demoText: {
        color: '#666',
        fontFamily: 'monospace',
        fontSize: 12,
    },
    demoTitle: {
        color: '#333',
        fontSize: 14,
        fontWeight: '600',
        marginBottom: 8,
    },
    disabledButton: {
        opacity: 0.6,
    },
    form: {
        marginBottom: 30,
    },
    input: {
        backgroundColor: '#ffffff',
        borderColor: '#ddd',
        borderRadius: 8,
        borderWidth: 1,
        fontSize: 16,
        marginBottom: 16,
        paddingHorizontal: 16,
        paddingVertical: 12,
    },
    loginButton: {
        alignItems: 'center',
        backgroundColor: '#c00',
        borderRadius: 8,
        marginBottom: 16,
        paddingVertical: 14,
    },
    loginButtonText: {
        color: '#ffffff',
        fontSize: 16,
        fontWeight: '600',
    },
    signupButton: {
        alignItems: 'center',
        paddingVertical: 10,
    },
    signupButtonText: {
        color: '#c00',
        fontSize: 14,
        fontWeight: '500',
    },
    subtitle: {
        color: '#666',
        fontSize: 16,
        marginBottom: 40,
        textAlign: 'center',
    },
    title: {
        color: '#c00',
        fontSize: 32,
        fontWeight: 'bold',
        marginBottom: 8,
        textAlign: 'center',
    },
});

export default LoginScreen;
