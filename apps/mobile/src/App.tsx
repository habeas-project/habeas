import React from 'react';
import { StatusBar } from 'expo-status-bar';
import { SafeAreaProvider } from 'react-native-safe-area-context';
import { NavigationContainer } from '@react-navigation/native';
import { createNativeStackNavigator } from '@react-navigation/native-stack';

import { AuthProvider } from './contexts/AuthContext';
import HomeScreen from './screens/HomeScreen';
import WelcomeScreen from './screens/WelcomeScreen';
import LoginScreen from './screens/LoginScreen';
import AttorneySignupScreen from './screens/AttorneySignupScreen';
import ClientSignupScreen from './screens/ClientSignupScreen';
import PersonalInfoScreen from './screens/PersonalInfoScreen';
import UnifiedSignupScreen from './screens/UnifiedSignupScreen';
import EmergencySetupScreen from './screens/EmergencySetupScreen';
import AttorneyDashboardScreen from './screens/AttorneyDashboardScreen';
import AvailableCasesScreen from './screens/AvailableCasesScreen';
import NotificationPreferencesScreen from './screens/NotificationPreferencesScreen';
import DailyDigestScreen from './screens/DailyDigestScreen';

export type RootStackParamList = {
    Welcome: undefined;
    Login: undefined;
    Home: undefined;
    AttorneySignup: undefined;
    ClientSignup: undefined;
    PersonalInfo: undefined;
    UnifiedSignup: undefined;
    EmergencySetup: undefined;

    // Attorney-specific screens
    AttorneyDashboard: undefined;
    AvailableCases: { courtId?: number };
    CaseDetail: { caseId: number };
    NotificationPreferences: undefined;
    DailyDigest: undefined;
    AttorneyProfile: undefined;
};

const Stack = createNativeStackNavigator<RootStackParamList>();

export default function App() {
    return (
        <SafeAreaProvider>
            <AuthProvider>
                <NavigationContainer>
                    <Stack.Navigator initialRouteName="Welcome">
                        <Stack.Screen
                            name="Welcome"
                            component={WelcomeScreen}
                            options={{ headerShown: false }}
                        />
                        <Stack.Screen
                            name="Login"
                            component={LoginScreen}
                            options={{ title: 'Sign In' }}
                        />
                        <Stack.Screen
                            name="Home"
                            component={HomeScreen}
                            options={{ title: 'Habeas' }}
                        />
                        <Stack.Screen
                            name="UnifiedSignup"
                            component={UnifiedSignupScreen}
                            options={{ title: 'Get Help' }}
                        />
                        <Stack.Screen
                            name="AttorneySignup"
                            component={AttorneySignupScreen}
                            options={{ title: 'Attorney Registration' }}
                        />
                        <Stack.Screen
                            name="ClientSignup"
                            component={ClientSignupScreen}
                            options={{ title: 'Client Registration' }}
                        />
                        <Stack.Screen
                            name="PersonalInfo"
                            component={PersonalInfoScreen}
                            options={{ title: 'Personal Information' }}
                        />
                        <Stack.Screen
                            name="EmergencySetup"
                            component={EmergencySetupScreen}
                            options={{ title: 'Emergency Setup' }}
                        />
                        <Stack.Screen
                            name="AttorneyDashboard"
                            component={AttorneyDashboardScreen}
                            options={{ title: 'Attorney Dashboard' }}
                        />
                        <Stack.Screen
                            name="AvailableCases"
                            component={AvailableCasesScreen}
                            options={{ title: 'Available Cases' }}
                        />
                        <Stack.Screen
                            name="NotificationPreferences"
                            component={NotificationPreferencesScreen}
                            options={{ title: 'Notification Preferences' }}
                        />
                        <Stack.Screen
                            name="DailyDigest"
                            component={DailyDigestScreen}
                            options={{ title: 'Daily Digest' }}
                        />
                    </Stack.Navigator>
                </NavigationContainer>
                <StatusBar style="auto" />
            </AuthProvider>
        </SafeAreaProvider>
    );
}
