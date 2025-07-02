import React, { createContext, useContext, useEffect, useState, ReactNode } from 'react';
import { SecureStorage } from '../utils/secureStorage';
import { logger, LogCategory } from '../utils/logger';
import { getUserEmergencyStatus, EmergencyStatusResponse } from '../api/client';

// Storage keys
const AUTH_TOKEN_KEY = '@auth_token';
const USER_DATA_KEY = '@user_data';
const EMERGENCY_STATUS_KEY = '@emergency_status';

// User data interface
export interface UserData {
    id: number;
    email: string;
    primary_role: string;
    user_type: string;
    cognito_id?: string;
    is_active: boolean;
    created_at: string;
    updated_at: string;
    // Role-specific IDs
    attorney_id?: number;
    client_helper_id?: number;
    admin_id?: number;
}

// Mock authentication token interface
export interface AuthToken {
    access_token: string;
    token_type: string;
    expires_in: number;
    refresh_token?: string;
    expires_at: number; // Calculated expiration timestamp
}

// Authentication context interface
export interface AuthContextType {
    // Authentication state
    isAuthenticated: boolean;
    isLoading: boolean;
    user: UserData | null;
    token: AuthToken | null;

    // Emergency status
    emergencyStatus: EmergencyStatusResponse | null;
    emergencyStatusLoading: boolean;

    // Role detection methods
    isAttorney: () => boolean;
    isClient: () => boolean;
    isAdmin: () => boolean;
    getUserRole: () => 'attorney' | 'client_helper' | 'admin' | null;

    // Authentication methods
    login: (email: string, password: string) => Promise<boolean>;
    logout: () => Promise<void>;
    refreshAuth: () => Promise<boolean>;

    // Emergency methods
    refreshEmergencyStatus: () => Promise<void>;
    checkEmergencyEligibility: () => boolean;
}

// Create the context
const AuthContext = createContext<AuthContextType | undefined>(undefined);

// Provider component props
interface AuthProviderProps {
    children: ReactNode;
}

// Auth provider component
export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
    const [isAuthenticated, setIsAuthenticated] = useState(false);
    const [isLoading, setIsLoading] = useState(true);
    const [user, setUser] = useState<UserData | null>(null);
    const [token, setToken] = useState<AuthToken | null>(null);
    const [emergencyStatus, setEmergencyStatus] = useState<EmergencyStatusResponse | null>(null);
    const [emergencyStatusLoading, setEmergencyStatusLoading] = useState(false);

    // Initialize authentication state on app start
    useEffect(() => {
        initializeAuth();
    }, []);

    // Refresh emergency status when user changes
    useEffect(() => {
        if (isAuthenticated && user) {
            refreshEmergencyStatus();
        } else {
            setEmergencyStatus(null);
        }
    }, [isAuthenticated, user]);

    const initializeAuth = async () => {
        try {
            setIsLoading(true);

            // Load stored authentication data
            const [storedToken, storedUser] = await Promise.all([
                SecureStorage.loadData<AuthToken>(AUTH_TOKEN_KEY),
                SecureStorage.loadData<UserData>(USER_DATA_KEY),
            ]);

            if (storedToken && storedUser) {
                // Check if token is still valid
                if (storedToken.expires_at > Date.now()) {
                    setToken(storedToken);
                    setUser(storedUser);
                    setIsAuthenticated(true);
                } else {
                    // Token expired, try to refresh
                    logger.info(LogCategory.AUTH, 'Token expired, attempting refresh', {
                        userId: storedUser?.id,
                        lastRefresh: new Date().toISOString()
                    });
                    await clearStoredAuth();
                }
            }
        } catch (error) {
            logger.error(LogCategory.AUTH, 'Failed to initialize auth context', {}, error as Error);
            await clearStoredAuth();
        } finally {
            setIsLoading(false);
        }
    };

    const login = async (email: string, password: string): Promise<boolean> => {
        try {
            setIsLoading(true);

            // TODO: Replace with actual authentication API call
            // For now, using mock authentication
            if (email && password) {
                // Generate mock token
                const mockToken: AuthToken = {
                    access_token: `mock_token_${Date.now()}`,
                    token_type: 'Bearer',
                    expires_in: 3600, // 1 hour
                    expires_at: Date.now() + (3600 * 1000), // 1 hour from now
                };

                // Generate mock user data - determine role based on email
                const isAttorney = email.toLowerCase().includes('attorney') || email.toLowerCase().includes('lawyer');
                const role = isAttorney ? 'attorney' : 'client_helper';
                const userId = Math.floor(Math.random() * 1000); // Mock user ID

                const mockUser: UserData = {
                    id: userId,
                    email,
                    primary_role: role,
                    user_type: role,
                    is_active: true,
                    created_at: new Date().toISOString(),
                    updated_at: new Date().toISOString(),
                    // Add role-specific IDs for mock authentication
                    attorney_id: isAttorney ? userId : undefined,
                    client_helper_id: !isAttorney ? userId : undefined,
                };

                // Store authentication data
                await Promise.all([
                    SecureStorage.saveData(AUTH_TOKEN_KEY, mockToken),
                    SecureStorage.saveData(USER_DATA_KEY, mockUser),
                ]);

                setToken(mockToken);
                setUser(mockUser);
                setIsAuthenticated(true);

                return true;
            }

            return false;
        } catch (error) {
            console.error('Login failed:', error);
            return false;
        } finally {
            setIsLoading(false);
        }
    };

    const logout = async (): Promise<void> => {
        try {
            setIsLoading(true);
            await clearStoredAuth();
            setToken(null);
            setUser(null);
            setIsAuthenticated(false);
            setEmergencyStatus(null);
        } catch (error) {
            console.error('Logout failed:', error);
        } finally {
            setIsLoading(false);
        }
    };

    const refreshAuth = async (): Promise<boolean> => {
        try {
            if (!token?.refresh_token) {
                return false;
            }

            // TODO: Implement actual token refresh API call
            // For now, just extend the current token
            const refreshedToken: AuthToken = {
                ...token,
                expires_in: 3600,
                expires_at: Date.now() + (3600 * 1000),
            };

            await SecureStorage.saveData(AUTH_TOKEN_KEY, refreshedToken);
            setToken(refreshedToken);

            return true;
        } catch (error) {
            logger.error(LogCategory.AUTH, 'Token refresh failed', {
                userId: user?.id
            }, error as Error);
            await logout();
            return false;
        }
    };

    const refreshEmergencyStatus = async (): Promise<void> => {
        if (!user || !isAuthenticated) {
            return;
        }

        try {
            setEmergencyStatusLoading(true);
            const status = await getUserEmergencyStatus(user.id);
            setEmergencyStatus(status);

            // Cache the status for offline access
            await SecureStorage.saveData(EMERGENCY_STATUS_KEY, status);
        } catch (error) {
            logger.error(LogCategory.EMERGENCY, 'Failed to fetch emergency status', {
                userId: user?.id
            }, error as Error);

            // Try to load cached status
            try {
                const cachedStatus = await SecureStorage.loadData<EmergencyStatusResponse>(EMERGENCY_STATUS_KEY);
                if (cachedStatus) {
                    setEmergencyStatus(cachedStatus);
                }
            } catch (cacheError) {
                logger.error(LogCategory.STORAGE, 'Failed to load cached emergency status', {
                    userId: user?.id
                }, cacheError as Error);
            }
        } finally {
            setEmergencyStatusLoading(false);
        }
    };

    const checkEmergencyEligibility = (): boolean => {
        return emergencyStatus?.can_activate_emergency ?? false;
    };

    const clearStoredAuth = async (): Promise<void> => {
        await Promise.all([
            SecureStorage.removeData(AUTH_TOKEN_KEY),
            SecureStorage.removeData(USER_DATA_KEY),
            SecureStorage.removeData(EMERGENCY_STATUS_KEY),
        ]);
    };

    const contextValue: AuthContextType = {
        isAuthenticated,
        isLoading,
        user,
        token,
        emergencyStatus,
        emergencyStatusLoading,
        isAttorney: () => user?.primary_role === 'attorney',
        isClient: () => user?.primary_role === 'client_helper',
        isAdmin: () => user?.primary_role === 'admin',
        getUserRole: () => user?.primary_role as 'attorney' | 'client_helper' | 'admin' | null,
        login,
        logout,
        refreshAuth,
        refreshEmergencyStatus,
        checkEmergencyEligibility,
    };

    return (
        <AuthContext.Provider value={contextValue}>
            {children}
        </AuthContext.Provider>
    );
};

// Hook to use the auth context
export const useAuth = (): AuthContextType => {
    const context = useContext(AuthContext);
    if (context === undefined) {
        throw new Error('useAuth must be used within an AuthProvider');
    }
    return context;
};

export default AuthContext;
