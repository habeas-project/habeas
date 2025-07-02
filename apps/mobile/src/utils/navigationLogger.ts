/**
 * Navigation and User Interaction Logger
 * Specialized logging for screen transitions, user interactions, and UX analytics
 */

import { logger, LogCategory } from './logger';

export interface ScreenTransition {
    fromScreen?: string;
    toScreen: string;
    transitionType: 'navigate' | 'replace' | 'goBack' | 'reset';
    params?: Record<string, unknown>;
}

export interface UserInteraction {
    elementType: 'button' | 'input' | 'modal' | 'slider' | 'picker' | 'link' | 'tab';
    action: 'tap' | 'long_press' | 'swipe' | 'scroll' | 'type' | 'select' | 'toggle';
    elementId?: string;
    elementText?: string;
    value?: unknown;
    metadata?: Record<string, unknown>;
}

export interface FormSubmission {
    formName: string;
    fields: string[];
    validationErrors?: string[];
    isSuccessful: boolean;
    submissionTime: number;
}

class NavigationLogger {
    private currentScreen?: string;
    private screenStartTime?: number;
    private interactionCounts: Record<string, number> = {};

    /**
     * Track screen entry and measure time on previous screen
     */
    public logScreenEntry(
        screenName: string,
        params?: Record<string, unknown>,
        transitionType: ScreenTransition['transitionType'] = 'navigate'
    ): void {
        const now = performance.now();

        // Log time spent on previous screen
        if (this.currentScreen && this.screenStartTime) {
            const timeOnScreen = now - this.screenStartTime;
            logger.logPerformance(
                `screen_time_${this.currentScreen}`,
                this.screenStartTime,
                now,
                {
                    screenName: this.currentScreen,
                    timeSpentMs: timeOnScreen,
                }
            );
        }

        // Log screen transition
        const transition: ScreenTransition = {
            fromScreen: this.currentScreen,
            toScreen: screenName,
            transitionType,
            params,
        };

        logger.logScreenView(screenName, {
            transition,
            timestamp: new Date().toISOString(),
            previousScreen: this.currentScreen,
        });

        // Update current screen tracking
        this.currentScreen = screenName;
        this.screenStartTime = now;
    }

    /**
     * Track user interactions with UI elements
     */
    public logUserInteraction(
        screen: string,
        interaction: UserInteraction
    ): void {
        const interactionKey = `${screen}_${interaction.elementType}_${interaction.action}`;
        this.interactionCounts[interactionKey] = (this.interactionCounts[interactionKey] || 0) + 1;

        logger.logUserInteraction(
            interaction.elementType,
            interaction.action,
            screen,
            interaction.elementId,
            {
                elementText: interaction.elementText,
                value: interaction.value,
                interactionCount: this.interactionCounts[interactionKey],
                ...interaction.metadata,
            }
        );
    }

    /**
     * Track form submissions with validation results
     */
    public logFormSubmission(
        screen: string,
        submission: FormSubmission
    ): void {
        logger.info(LogCategory.USER_INTERACTION, `Form submission: ${submission.formName}`, {
            screen,
            formName: submission.formName,
            fieldCount: submission.fields.length,
            fields: submission.fields,
            isSuccessful: submission.isSuccessful,
            validationErrorCount: submission.validationErrors?.length || 0,
            validationErrors: submission.validationErrors,
            submissionTimeMs: submission.submissionTime,
        });
    }

    /**
     * Track error states and user recovery actions
     */
    public logErrorRecovery(
        screen: string,
        errorType: string,
        recoveryAction: string,
        wasSuccessful: boolean
    ): void {
        logger.info(LogCategory.ERROR, `Error recovery attempt: ${errorType}`, {
            screen,
            errorType,
            recoveryAction,
            wasSuccessful,
            timestamp: new Date().toISOString(),
        });
    }

    /**
     * Track feature usage patterns
     */
    public logFeatureUsage(
        feature: string,
        action: string,
        context: Record<string, unknown> = {}
    ): void {
        logger.info(LogCategory.USER_INTERACTION, `Feature usage: ${feature}`, {
            feature,
            action,
            screen: this.currentScreen,
            ...context,
        });
    }

    /**
     * Track onboarding progress
     */
    public logOnboardingStep(
        step: string,
        stepNumber: number,
        totalSteps: number,
        isCompleted: boolean,
        timeSpent?: number
    ): void {
        logger.info(LogCategory.USER_INTERACTION, `Onboarding step: ${step}`, {
            step,
            stepNumber,
            totalSteps,
            progress: stepNumber / totalSteps,
            isCompleted,
            timeSpentMs: timeSpent,
            screen: this.currentScreen,
        });
    }

    /**
     * Track search and filter usage
     */
    public logSearchAction(
        searchType: string,
        query?: string,
        resultCount?: number,
        filters?: Record<string, unknown>
    ): void {
        logger.info(LogCategory.USER_INTERACTION, `Search action: ${searchType}`, {
            searchType,
            hasQuery: !!query,
            queryLength: query?.length,
            resultCount,
            filters,
            screen: this.currentScreen,
        });
    }

    /**
     * Track modal and dialog interactions
     */
    public logModalInteraction(
        modalName: string,
        action: 'open' | 'close' | 'confirm' | 'cancel' | 'dismiss',
        context?: Record<string, unknown>
    ): void {
        logger.logUserInteraction(
            'modal',
            action,
            this.currentScreen || 'unknown',
            modalName,
            {
                modalName,
                ...context,
            }
        );
    }

    /**
     * Get interaction summary for current session
     */
    public getInteractionSummary(): Record<string, number> {
        return { ...this.interactionCounts };
    }

    /**
     * Reset interaction tracking (useful for new sessions)
     */
    public resetTracking(): void {
        this.currentScreen = undefined;
        this.screenStartTime = undefined;
        this.interactionCounts = {};
    }
}

// Export singleton instance
export const navigationLogger = new NavigationLogger();

// Convenience functions for common interactions
export const logButtonTap = (buttonId: string, screen: string, metadata?: Record<string, unknown>) => {
    navigationLogger.logUserInteraction(screen, {
        elementType: 'button',
        action: 'tap',
        elementId: buttonId,
        metadata,
    });
};

export const logInputChange = (inputId: string, screen: string, value: unknown) => {
    navigationLogger.logUserInteraction(screen, {
        elementType: 'input',
        action: 'type',
        elementId: inputId,
        value: typeof value === 'string' ? value.length : value,
    });
};

export const logModalOpen = (modalName: string, context?: Record<string, unknown>) => {
    navigationLogger.logModalInteraction(modalName, 'open', context);
};

export const logModalClose = (modalName: string, context?: Record<string, unknown>) => {
    navigationLogger.logModalInteraction(modalName, 'close', context);
};
