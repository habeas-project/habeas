import React, { useState } from 'react';
import {
    View,
    Text,
    StyleSheet,
    TouchableOpacity,
    ScrollView,
    SafeAreaView,
} from 'react-native';
import { NativeStackNavigationProp } from '@react-navigation/native-stack';
import { RootStackParamList } from '../App';

type WelcomeScreenProps = {
    navigation: NativeStackNavigationProp<RootStackParamList, 'Welcome'>;
};

// Screen width available if needed for responsive design
// const { width: screenWidth } = Dimensions.get('window');

interface OnboardingStep {
    title: string;
    subtitle: string;
    description: string;
    icon: string;
    highlight: string;
}

const onboardingSteps: OnboardingStep[] = [
    {
        title: "Welcome to Habeas",
        subtitle: "Your Bridge to Legal Protection",
        description: "We connect people facing immigration detention with experienced attorneys who can file habeas corpus petitions to protect their rights.",
        icon: "⚖️",
        highlight: "No one should face detention alone"
    },
    {
        title: "How It Works",
        subtitle: "Simple, Secure, Effective",
        description: "Whether you need legal help or you're an attorney ready to serve, our platform guides you through every step with care and expertise.",
        icon: "🤝",
        highlight: "Connect • Protect • Prevail"
    },
    {
        title: "Family First",
        subtitle: "Help Multiple Loved Ones",
        description: "Create profiles for multiple family members, manage their cases, and coordinate legal support from a single, secure account.",
        icon: "👨‍👩‍👧‍👦",
        highlight: "One account, unlimited support"
    },
    {
        title: "Emergency Ready",
        subtitle: "Immediate Response Available",
        description: "In urgent situations, our emergency system can instantly alert your chosen contacts and connect you with legal assistance.",
        icon: "🚨",
        highlight: "Help is always just a swipe away"
    }
];

export default function WelcomeScreen({ navigation }: WelcomeScreenProps) {
    const [currentStep, setCurrentStep] = useState(0);

    const handleNext = () => {
        if (currentStep < onboardingSteps.length - 1) {
            setCurrentStep(currentStep + 1);
        } else {
            // Navigate to home screen
            navigation.replace('Home');
        }
    };

    const handleSkip = () => {
        navigation.replace('Home');
    };

    const currentStepData = onboardingSteps[currentStep];
    const isLastStep = currentStep === onboardingSteps.length - 1;

    return (
        <SafeAreaView style={styles.container}>
            <ScrollView contentContainerStyle={styles.scrollContent} showsVerticalScrollIndicator={false}>
                {/* Header */}
                <View style={styles.header}>
                    <TouchableOpacity style={styles.skipButton} onPress={handleSkip}>
                        <Text style={styles.skipText}>Skip</Text>
                    </TouchableOpacity>
                </View>

                {/* Content */}
                <View style={styles.content}>
                    <View style={styles.iconContainer}>
                        <Text style={styles.icon}>{currentStepData.icon}</Text>
                    </View>

                    <Text style={styles.title}>{currentStepData.title}</Text>
                    <Text style={styles.subtitle}>{currentStepData.subtitle}</Text>

                    <View style={styles.descriptionContainer}>
                        <Text style={styles.description}>{currentStepData.description}</Text>
                    </View>

                    <View style={styles.highlightContainer}>
                        <Text style={styles.highlight}>{currentStepData.highlight}</Text>
                    </View>
                </View>

                {/* Navigation */}
                <View style={styles.navigation}>
                    {/* Step Indicators */}
                    <View style={styles.stepIndicators}>
                        {onboardingSteps.map((_, index) => (
                            <View
                                key={index}
                                style={[
                                    styles.stepDot,
                                    index === currentStep ? styles.stepDotActive : styles.stepDotInactive
                                ]}
                            />
                        ))}
                    </View>

                    {/* Action Buttons */}
                    <View style={styles.actionButtons}>
                        {currentStep > 0 && (
                            <TouchableOpacity
                                style={styles.backButton}
                                onPress={() => setCurrentStep(currentStep - 1)}
                            >
                                <Text style={styles.backButtonText}>← Back</Text>
                            </TouchableOpacity>
                        )}

                        <TouchableOpacity
                            style={[styles.nextButton, isLastStep && styles.getStartedButton]}
                            onPress={handleNext}
                        >
                            <Text style={[styles.nextButtonText, isLastStep && styles.getStartedButtonText]}>
                                {isLastStep ? 'Get Started' : 'Next →'}
                            </Text>
                        </TouchableOpacity>
                    </View>

                    {/* Login Option */}
                    {isLastStep && (
                        <View style={styles.loginSection}>
                            <Text style={styles.loginPrompt}>Already have an account?</Text>
                            <TouchableOpacity
                                style={styles.loginButton}
                                onPress={() => navigation.navigate('Login')}
                            >
                                <Text style={styles.loginButtonText}>Sign In</Text>
                            </TouchableOpacity>
                        </View>
                    )}
                </View>
            </ScrollView>
        </SafeAreaView>
    );
}

const styles = StyleSheet.create({
    actionButtons: {
        alignItems: 'center',
        flexDirection: 'row',
        justifyContent: 'space-between',
    },
    backButton: {
        backgroundColor: '#f7fafc',
        borderColor: '#e2e8f0',
        borderRadius: 8,
        borderWidth: 1,
        paddingHorizontal: 24,
        paddingVertical: 12,
    },
    backButtonText: {
        color: '#4a5568',
        fontSize: 16,
        fontWeight: '500',
    },
    container: {
        backgroundColor: '#ffffff',
        flex: 1,
    },
    content: {
        alignItems: 'center',
        flex: 1,
        justifyContent: 'center',
        paddingHorizontal: 16,
    },
    description: {
        color: '#4a5568',
        fontSize: 17,
        lineHeight: 26,
        textAlign: 'center',
    },
    descriptionContainer: {
        marginBottom: 32,
        paddingHorizontal: 8,
    },
    getStartedButton: {
        backgroundColor: '#38a169',
        elevation: 8,
        shadowColor: '#38a169',
        shadowOffset: { width: 0, height: 4 },
        shadowOpacity: 0.3,
        shadowRadius: 8,
    },
    getStartedButtonText: {
        fontSize: 18,
        fontWeight: '700',
    },
    header: {
        flexDirection: 'row',
        justifyContent: 'flex-end',
        paddingBottom: 20,
        paddingTop: 16,
    },
    highlight: {
        color: '#2c5282',
        fontSize: 16,
        fontStyle: 'italic',
        fontWeight: '600',
        textAlign: 'center',
    },
    highlightContainer: {
        backgroundColor: '#ebf8ff',
        borderColor: '#bee3f8',
        borderRadius: 12,
        borderWidth: 1,
        paddingHorizontal: 20,
        paddingVertical: 12,
    },
    icon: {
        fontSize: 48,
    },
    iconContainer: {
        alignItems: 'center',
        backgroundColor: '#ebf8ff',
        borderRadius: 60,
        height: 120,
        justifyContent: 'center',
        marginBottom: 32,
        width: 120,
    },
    loginButton: {
        backgroundColor: 'transparent',
        borderColor: '#3182ce',
        borderRadius: 8,
        borderWidth: 1,
        paddingHorizontal: 24,
        paddingVertical: 12,
    },
    loginButtonText: {
        color: '#3182ce',
        fontSize: 16,
        fontWeight: '600',
        textAlign: 'center',
    },
    loginPrompt: {
        color: '#4a5568',
        fontSize: 16,
        marginBottom: 12,
        textAlign: 'center',
    },
    loginSection: {
        alignItems: 'center',
        borderTopColor: '#e2e8f0',
        borderTopWidth: 1,
        marginTop: 24,
        paddingTop: 24,
    },
    navigation: {
        paddingBottom: 40,
        paddingTop: 32,
    },
    nextButton: {
        alignItems: 'center',
        backgroundColor: '#3182ce',
        borderRadius: 8,
        flex: 1,
        marginLeft: 16,
        paddingHorizontal: 24,
        paddingVertical: 12,
    },
    nextButtonText: {
        color: '#ffffff',
        fontSize: 16,
        fontWeight: '600',
    },
    scrollContent: {
        flexGrow: 1,
        paddingHorizontal: 24,
    },
    skipButton: {
        paddingHorizontal: 16,
        paddingVertical: 8,
    },
    skipText: {
        color: '#718096',
        fontSize: 16,
        fontWeight: '500',
    },
    stepDot: {
        borderRadius: 6,
        height: 12,
        marginHorizontal: 6,
        width: 12,
    },
    stepDotActive: {
        backgroundColor: '#3182ce',
    },
    stepDotInactive: {
        backgroundColor: '#cbd5e0',
    },
    stepIndicators: {
        alignItems: 'center',
        flexDirection: 'row',
        justifyContent: 'center',
        marginBottom: 32,
    },
    subtitle: {
        color: '#3182ce',
        fontSize: 20,
        fontWeight: '600',
        marginBottom: 24,
        textAlign: 'center',
    },
    title: {
        color: '#1a365d',
        fontSize: 28,
        fontWeight: '700',
        letterSpacing: -0.5,
        marginBottom: 8,
        textAlign: 'center',
    },
});
