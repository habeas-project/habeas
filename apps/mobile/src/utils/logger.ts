/**
 * Comprehensive Logging System for Habeas Mobile App
 * Captures structured logs with context, performance metrics, and user interactions
 */

import AsyncStorage from '@react-native-async-storage/async-storage';
import { Platform } from 'react-native';
import * as Device from 'expo-device';

// Log levels
export enum LogLevel {
    DEBUG = 0,
    INFO = 1,
    WARN = 2,
    ERROR = 3,
    FATAL = 4,
}

// Log categories for filtering and analysis
export enum LogCategory {
    // Core app functionality
    AUTH = 'AUTH',
    NAVIGATION = 'NAVIGATION',
    API = 'API',
    EMERGENCY = 'EMERGENCY',
    LOCATION = 'LOCATION',
    STORAGE = 'STORAGE',

    // User experience tracking
    USER_INTERACTION = 'USER_INTERACTION',
    SCREEN_VIEW = 'SCREEN_VIEW',
    PERFORMANCE = 'PERFORMANCE',

    // Error tracking
    ERROR = 'ERROR',
    CRASH = 'CRASH',
    VALIDATION = 'VALIDATION',

    // Attorney-specific features
    ATTORNEY_DASHBOARD = 'ATTORNEY_DASHBOARD',
    CASE_MANAGEMENT = 'CASE_MANAGEMENT',
    NOTIFICATIONS = 'NOTIFICATIONS',

    // System events
    SYSTEM = 'SYSTEM',
    NETWORK = 'NETWORK',
    SECURITY = 'SECURITY',
}

// Base log entry interface
interface BaseLogEntry {
    timestamp: string;
    level: LogLevel;
    category: LogCategory;
    message: string;
    context?: Record<string, unknown>;
    userId?: string;
    sessionId: string;
    deviceInfo: DeviceInfo;
    stackTrace?: string;
}

// Performance log entry
interface PerformanceLogEntry extends BaseLogEntry {
    category: LogCategory.PERFORMANCE;
    performanceData: {
        operation: string;
        startTime: number;
        endTime: number;
        duration: number;
        metadata?: Record<string, unknown>;
    };
}

// API log entry
interface ApiLogEntry extends BaseLogEntry {
    category: LogCategory.API;
    apiData: {
        method: string;
        url: string;
        statusCode?: number;
        requestId?: string;
        duration?: number;
        requestSize?: number;
        responseSize?: number;
        error?: string;
    };
}

// User interaction log entry
interface UserInteractionLogEntry extends BaseLogEntry {
    category: LogCategory.USER_INTERACTION;
    interactionData: {
        elementType: string;
        elementId?: string;
        screen: string;
        action: string;
        metadata?: Record<string, unknown>;
    };
}

// Device information
interface DeviceInfo {
    platform: string;
    osVersion: string;
    appVersion: string;
    deviceModel?: string;
    isEmulator: boolean;
    timezone: string;
    locale: string;
}

// Log entry union type
type LogEntry = BaseLogEntry | PerformanceLogEntry | ApiLogEntry | UserInteractionLogEntry;

class HabeasLogger {
    private sessionId: string;
    private deviceInfo: DeviceInfo;
    private currentUserId?: string;
    private logBuffer: LogEntry[] = [];
    private maxBufferSize = 1000;
    private minLogLevel = LogLevel.INFO;
    private persistentStorageKey = 'habeas_logs';

    constructor() {
        this.sessionId = this.generateSessionId();
        this.deviceInfo = this.getDeviceInfo();
        this.initializeLogger();
    }

    private generateSessionId(): string {
        return `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    }

    private getDeviceInfo(): DeviceInfo {
        return {
            platform: Platform.OS,
            osVersion: Platform.Version.toString(),
            appVersion: '1.0.0', // TODO: Get from app config
            deviceModel: Device.modelName || 'Unknown',
            isEmulator: !Device.isDevice,
            timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
            locale: Intl.DateTimeFormat().resolvedOptions().locale,
        };
    }

    private async initializeLogger(): Promise<void> {
        try {
            // Load any persisted logs
            await this.loadPersistedLogs();

            // Log session start
            this.info(LogCategory.SYSTEM, 'Logger initialized', {
                sessionId: this.sessionId,
                deviceInfo: this.deviceInfo,
            });

            // Set up periodic log persistence
            setInterval(() => {
                this.persistLogs();
            }, 30000); // Persist every 30 seconds

        } catch (error) {
            console.error('Failed to initialize logger:', error);
        }
    }

    public setUserId(userId: string): void {
        this.currentUserId = userId;
        this.info(LogCategory.AUTH, 'User ID set for logging', { userId });
    }

    public setLogLevel(level: LogLevel): void {
        this.minLogLevel = level;
        this.info(LogCategory.SYSTEM, 'Log level changed', { newLevel: LogLevel[level] });
    }

    // Core logging methods
    public debug(category: LogCategory, message: string, context?: Record<string, unknown>): void {
        this.log(LogLevel.DEBUG, category, message, context);
    }

    public info(category: LogCategory, message: string, context?: Record<string, unknown>): void {
        this.log(LogLevel.INFO, category, message, context);
    }

    public warn(category: LogCategory, message: string, context?: Record<string, unknown>): void {
        this.log(LogLevel.WARN, category, message, context);
    }

    public error(category: LogCategory, message: string, context?: Record<string, unknown>, error?: Error): void {
        const contextWithError = {
            ...context,
            ...(error && {
                errorName: error.name,
                errorMessage: error.message,
                errorStack: error.stack,
            }),
        };
        this.log(LogLevel.ERROR, category, message, contextWithError, error?.stack);
    }

    public fatal(category: LogCategory, message: string, context?: Record<string, unknown>, error?: Error): void {
        const contextWithError = {
            ...context,
            ...(error && {
                errorName: error.name,
                errorMessage: error.message,
                errorStack: error.stack,
            }),
        };
        this.log(LogLevel.FATAL, category, message, contextWithError, error?.stack);
    }

    // Specialized logging methods
    public logApiCall(
        method: string,
        url: string,
        statusCode?: number,
        duration?: number,
        error?: string,
        requestId?: string
    ): void {
        const apiLogEntry: ApiLogEntry = {
            timestamp: new Date().toISOString(),
            level: error ? LogLevel.ERROR : LogLevel.INFO,
            category: LogCategory.API,
            message: `API ${method.toUpperCase()} ${url}`,
            sessionId: this.sessionId,
            deviceInfo: this.deviceInfo,
            userId: this.currentUserId,
            apiData: {
                method: method.toUpperCase(),
                url,
                statusCode,
                duration,
                error,
                requestId,
            },
        };

        this.addToBuffer(apiLogEntry);
    }

    public logPerformance(
        operation: string,
        startTime: number,
        endTime: number,
        metadata?: Record<string, unknown>
    ): void {
        const duration = endTime - startTime;
        const performanceLogEntry: PerformanceLogEntry = {
            timestamp: new Date().toISOString(),
            level: LogLevel.INFO,
            category: LogCategory.PERFORMANCE,
            message: `Performance: ${operation}`,
            sessionId: this.sessionId,
            deviceInfo: this.deviceInfo,
            userId: this.currentUserId,
            performanceData: {
                operation,
                startTime,
                endTime,
                duration,
                metadata,
            },
        };

        this.addToBuffer(performanceLogEntry);
    }

    public logUserInteraction(
        elementType: string,
        action: string,
        screen: string,
        elementId?: string,
        metadata?: Record<string, unknown>
    ): void {
        const interactionLogEntry: UserInteractionLogEntry = {
            timestamp: new Date().toISOString(),
            level: LogLevel.INFO,
            category: LogCategory.USER_INTERACTION,
            message: `User ${action} ${elementType} on ${screen}`,
            sessionId: this.sessionId,
            deviceInfo: this.deviceInfo,
            userId: this.currentUserId,
            interactionData: {
                elementType,
                elementId,
                screen,
                action,
                metadata,
            },
        };

        this.addToBuffer(interactionLogEntry);
    }

    public logScreenView(screenName: string, metadata?: Record<string, unknown>): void {
        this.info(LogCategory.SCREEN_VIEW, `Screen viewed: ${screenName}`, {
            screenName,
            ...metadata,
        });
    }

    public logEmergencyEvent(event: string, context?: Record<string, unknown>): void {
        this.info(LogCategory.EMERGENCY, `Emergency event: ${event}`, context);
    }

    public logLocationEvent(event: string, context?: Record<string, unknown>): void {
        this.info(LogCategory.LOCATION, `Location event: ${event}`, context);
    }

    public logAuthEvent(event: string, context?: Record<string, unknown>): void {
        // Remove sensitive data
        const sanitizedContext = this.sanitizeAuthContext(context);
        this.info(LogCategory.AUTH, `Auth event: ${event}`, sanitizedContext);
    }

    private sanitizeAuthContext(context?: Record<string, unknown>): Record<string, unknown> | undefined {
        if (!context) return context;

        const sanitized = { ...context };
        // Remove sensitive fields
        const sensitiveFields = ['password', 'token', 'refreshToken', 'sessionToken', 'credentials'];
        sensitiveFields.forEach(field => {
            if (sanitized[field]) {
                sanitized[field] = '[REDACTED]';
            }
        });

        return sanitized;
    }

    private log(
        level: LogLevel,
        category: LogCategory,
        message: string,
        context?: Record<string, unknown>,
        stackTrace?: string
    ): void {
        if (level < this.minLogLevel) {
            return;
        }

        const logEntry: BaseLogEntry = {
            timestamp: new Date().toISOString(),
            level,
            category,
            message,
            context,
            userId: this.currentUserId,
            sessionId: this.sessionId,
            deviceInfo: this.deviceInfo,
            stackTrace,
        };

        this.addToBuffer(logEntry);

        // Also log to console for development
        if (__DEV__) {
            const logMethod = this.getConsoleMethod(level);
            const logOutput = `[${LogLevel[level]}][${category}] ${message}`;
            if (context) {
                logMethod(logOutput, context);
            } else {
                logMethod(logOutput);
            }
        }
    }

    private getConsoleMethod(level: LogLevel): (...args: unknown[]) => void {
        switch (level) {
            case LogLevel.DEBUG:
                return console.debug;
            case LogLevel.INFO:
                return console.info;
            case LogLevel.WARN:
                return console.warn;
            case LogLevel.ERROR:
            case LogLevel.FATAL:
                return console.error;
            default:
                return console.log;
        }
    }

    private addToBuffer(entry: LogEntry): void {
        this.logBuffer.push(entry);

        // Maintain buffer size
        if (this.logBuffer.length > this.maxBufferSize) {
            this.logBuffer = this.logBuffer.slice(-this.maxBufferSize);
        }
    }

    private async persistLogs(): Promise<void> {
        try {
            const logsToStore = [...this.logBuffer];
            await AsyncStorage.setItem(this.persistentStorageKey, JSON.stringify(logsToStore));
        } catch (error) {
            console.error('Failed to persist logs:', error);
        }
    }

    private async loadPersistedLogs(): Promise<void> {
        try {
            const persistedLogs = await AsyncStorage.getItem(this.persistentStorageKey);
            if (persistedLogs) {
                const logs = JSON.parse(persistedLogs) as LogEntry[];
                this.logBuffer = logs.slice(-this.maxBufferSize);
            }
        } catch (error) {
            console.error('Failed to load persisted logs:', error);
        }
    }

    // Log retrieval and analysis methods
    public getLogs(
        category?: LogCategory,
        level?: LogLevel,
        limit?: number,
        startTime?: Date,
        endTime?: Date
    ): LogEntry[] {
        let filteredLogs = [...this.logBuffer];

        if (category) {
            filteredLogs = filteredLogs.filter(log => log.category === category);
        }

        if (level !== undefined) {
            filteredLogs = filteredLogs.filter(log => log.level >= level);
        }

        if (startTime) {
            filteredLogs = filteredLogs.filter(log => new Date(log.timestamp) >= startTime);
        }

        if (endTime) {
            filteredLogs = filteredLogs.filter(log => new Date(log.timestamp) <= endTime);
        }

        if (limit) {
            filteredLogs = filteredLogs.slice(-limit);
        }

        return filteredLogs.sort((a, b) =>
            new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime()
        );
    }

    public getLogSummary(): {
        totalLogs: number;
        logsByLevel: Record<string, number>;
        logsByCategory: Record<string, number>;
        errorCount: number;
        sessionDuration: number;
    } {
        const logsByLevel: Record<string, number> = {};
        const logsByCategory: Record<string, number> = {};
        let errorCount = 0;

        this.logBuffer.forEach(log => {
            const levelName = LogLevel[log.level];
            logsByLevel[levelName] = (logsByLevel[levelName] || 0) + 1;
            logsByCategory[log.category] = (logsByCategory[log.category] || 0) + 1;

            if (log.level >= LogLevel.ERROR) {
                errorCount++;
            }
        });

        const sessionStart = this.logBuffer.length > 0 ?
            new Date(this.logBuffer[0].timestamp).getTime() : Date.now();
        const sessionDuration = Date.now() - sessionStart;

        return {
            totalLogs: this.logBuffer.length,
            logsByLevel,
            logsByCategory,
            errorCount,
            sessionDuration,
        };
    }

    public async exportLogs(): Promise<string> {
        return JSON.stringify({
            sessionId: this.sessionId,
            deviceInfo: this.deviceInfo,
            userId: this.currentUserId,
            exportTime: new Date().toISOString(),
            summary: this.getLogSummary(),
            logs: this.logBuffer,
        }, null, 2);
    }

    public clearLogs(): void {
        this.logBuffer = [];
        AsyncStorage.removeItem(this.persistentStorageKey);
        this.info(LogCategory.SYSTEM, 'Logs cleared');
    }
}

// Create singleton instance
export const logger = new HabeasLogger();

// Performance measurement utility
export class PerformanceTimer {
    private startTime: number;
    private operation: string;
    private metadata?: Record<string, unknown>;

    constructor(operation: string, metadata?: Record<string, unknown>) {
        this.operation = operation;
        this.metadata = metadata;
        this.startTime = performance.now();
    }

    public end(): number {
        const endTime = performance.now();
        logger.logPerformance(this.operation, this.startTime, endTime, this.metadata);
        return endTime - this.startTime;
    }
}

// Convenience function for performance measurement
export function measurePerformance<T>(
    operation: string,
    fn: () => T | Promise<T>,
    metadata?: Record<string, unknown>
): T | Promise<T> {
    const timer = new PerformanceTimer(operation, metadata);

    try {
        const result = fn();

        if (result instanceof Promise) {
            return result.finally(() => timer.end());
        } else {
            timer.end();
            return result;
        }
    } catch (error) {
        timer.end();
        throw error;
    }
}

// Export types for external use
export type { LogEntry, BaseLogEntry, PerformanceLogEntry, ApiLogEntry, UserInteractionLogEntry };
