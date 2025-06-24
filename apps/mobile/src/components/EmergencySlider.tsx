import React, { useState, useRef, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  PanResponder,
  Animated,
  Dimensions,
  Vibration,
  Alert,
  Modal,
  TouchableOpacity,
  AccessibilityInfo,
} from 'react-native';
import { useAuth } from '../contexts/AuthContext';
import { createEmergencyCase, getCurrentLocation, EmergencyActivationRequest } from '../api/client';
import PhoneSecurityModal from './PhoneSecurityModal';
import LocationPermissionModal from './LocationPermissionModal';
import DetentionLocationInput from './DetentionLocationInput';

const SLIDER_WIDTH = Dimensions.get('window').width - 60; // Padding on both sides
const SLIDER_HEIGHT = 80; // Increased height for urgency
const THUMB_SIZE = 70; // Larger thumb

interface EmergencySliderProps {
  onEmergencyActivated: () => void;
  disabled?: boolean;
  visible?: boolean; // Controls visibility based on authentication and emergency status
}

const EmergencySlider: React.FC<EmergencySliderProps> = ({
  onEmergencyActivated,
  disabled = false,
  visible = true
}) => {
  const { isAuthenticated, checkEmergencyEligibility, emergencyStatus, emergencyStatusLoading, user } = useAuth();
  const [isUnlocked, setIsUnlocked] = useState(false);
  const [isActivating, setIsActivating] = useState(false);
  const [showSecurityModal, setShowSecurityModal] = useState(false);
  const [isCreatingCase, setIsCreatingCase] = useState(false);
  const [showLocationPermissionModal, setShowLocationPermissionModal] = useState(false);
  const [showManualLocationEntry, setShowManualLocationEntry] = useState(false);
  const [isCapturingLocation, setIsCapturingLocation] = useState(false);
  const [showSetupPrompt, setShowSetupPrompt] = useState(false);
  const [countdownValue, setCountdownValue] = useState(3);
  const translateX = useRef(new Animated.Value(0)).current;
  const countdown = useRef(new Animated.Value(0)).current;
  const countdownRef = useRef<number>(0);
  const pulseAnimation = useRef(new Animated.Value(1)).current;
  const glowAnimation = useRef(new Animated.Value(0)).current;

  // Reset when disabled changes
  useEffect(() => {
    if (disabled) {
      resetSlider();
    }
  }, [disabled]);

  // Pulse and glow animations for urgent state
  useEffect(() => {
    if (visible && !disabled && checkEmergencyEligibility()) {
      // Start pulse animation
      const pulse = () => {
        Animated.sequence([
          Animated.timing(pulseAnimation, {
            toValue: 1.05,
            duration: 1500,
            useNativeDriver: true,
          }),
          Animated.timing(pulseAnimation, {
            toValue: 1,
            duration: 1500,
            useNativeDriver: true,
          }),
        ]).start(() => pulse());
      };
      pulse();

      // Start glow animation
      const glow = () => {
        Animated.sequence([
          Animated.timing(glowAnimation, {
            toValue: 1,
            duration: 2000,
            useNativeDriver: false,
          }),
          Animated.timing(glowAnimation, {
            toValue: 0,
            duration: 2000,
            useNativeDriver: false,
          }),
        ]).start(() => glow());
      };
      glow();
    }
  }, [visible, disabled, checkEmergencyEligibility]);

  // Create countdown animation
  useEffect(() => {
    countdown.addListener(({ value }) => {
      countdownRef.current = value;
      setCountdownValue(Math.ceil(3 - (value / 100) * 3));

      // If countdown reaches 100, trigger emergency
      if (value >= 100 && isActivating) {
        handleEmergencyCountdownComplete();
      }
    });

    return () => {
      countdown.removeAllListeners();
    };
  }, [countdown, isActivating]);

  // Accessibility announcements
  useEffect(() => {
    if (isActivating) {
      AccessibilityInfo.announceForAccessibility(`Emergency activation in ${countdownValue} seconds`);
    }
  }, [countdownValue, isActivating]);

  const resetSlider = () => {
    setIsUnlocked(false);
    setIsActivating(false);
    setCountdownValue(3);
    Animated.spring(translateX, {
      toValue: 0,
      useNativeDriver: true,
      friction: 6,
    }).start();
    Animated.timing(countdown, {
      toValue: 0,
      duration: 200,
      useNativeDriver: false,
    }).start();
  };

  const startEmergencyCountdown = () => {
    setIsActivating(true);

    // Strong vibration for urgent activation
    Vibration.vibrate([200, 100, 200]);

    // Accessibility announcement
    AccessibilityInfo.announceForAccessibility('Emergency activation started. Hold to confirm.');

    // Start the countdown animation
    Animated.timing(countdown, {
      toValue: 100,
      duration: 3000, // 3 seconds
      useNativeDriver: false,
    }).start(({ finished }) => {
      // If animation is interrupted, reset
      if (!finished) {
        resetCountdown();
      }
    });
  };

  const resetCountdown = () => {
    setIsActivating(false);
    setCountdownValue(3);
    Animated.timing(countdown, {
      toValue: 0,
      duration: 200,
      useNativeDriver: false,
    }).start();
  };

  const handleEmergencyCountdownComplete = async () => {
    // Strong completion vibration
    Vibration.vibrate(500);
    setIsActivating(false);
    setIsUnlocked(true);

    // Accessibility announcement
    AccessibilityInfo.announceForAccessibility('Emergency activated. Setting up location and contacts.');

    // Show location permission modal first
    setShowLocationPermissionModal(true);
  };

  const handleSetupRequired = () => {
    setShowSetupPrompt(true);
  };

  const handleSetupPromptClose = () => {
    setShowSetupPrompt(false);
  };

  const handleSecurityModalConfirm = async () => {
    setShowSecurityModal(false);
    await handleCreateEmergencyCase();
  };

  const handleSecurityModalClose = async () => {
    setShowSecurityModal(false);
    await handleCreateEmergencyCase();
  };

  const handleLocationPermissionGranted = async () => {
    setShowLocationPermissionModal(false);
    setIsCapturingLocation(true);

    try {
      // Try to get GPS location
      const location = await getCurrentLocation();
      setIsCapturingLocation(false);

      if (location) {
        // Location captured successfully, proceed to phone security
        setShowSecurityModal(true);
      } else {
        // GPS failed, fall back to manual entry
        setShowManualLocationEntry(true);
      }
    } catch (error) {
      console.error('Location capture failed:', error);
      setIsCapturingLocation(false);
      setShowManualLocationEntry(true);
    }
  };

  const handleLocationManualEntry = () => {
    setShowLocationPermissionModal(false);
    setShowManualLocationEntry(true);
  };

  const handleManualLocationSubmit = (_locationData: { description: string; zipCode?: string; city?: string; state?: string }) => {
    setShowManualLocationEntry(false);
    // Store the manual location data for later use
    // For now, proceed to phone security modal
    setShowSecurityModal(true);
  };

  const handleManualLocationCancel = () => {
    setShowManualLocationEntry(false);
    // Reset the slider state
    resetSlider();
  };

  const handleCreateEmergencyCase = async () => {
    if (!user) {
      Alert.alert('Error', 'User not authenticated');
      return;
    }

    try {
      setIsCreatingCase(true);

      // Get current location
      const location = await getCurrentLocation();

      // For now, we'll use the first client profile if available
      // In a real app, you might want to let the user select which profile this is for
      const clientProfileId = emergencyStatus?.has_client_profiles ? 1 : 1; // This should be dynamic

      const emergencyRequest: EmergencyActivationRequest = {
        client_profile_id: clientProfileId,
        case_type: 'self', // Default to self, could be made configurable
        location: location || {
          description: 'Location not available'
        }
      };

      const response = await createEmergencyCase(user.id, emergencyRequest);

      console.log('Emergency case created:', response);

      // Call the parent callback
      onEmergencyActivated();

      Alert.alert(
        '🚨 Emergency Activated',
        `Case #${response.case_id} created successfully!\n\n` +
        `✅ ${response.attorneys_notified_count} attorneys notified\n` +
        `📍 Location: ${response.assigned_court_name}\n\n` +
        `Keep your phone charged and accessible. You will be contacted soon.`,
        [{ text: 'OK' }]
      );

    } catch (error) {
      console.error('Failed to create emergency case:', error);
      Alert.alert(
        'Emergency Activation Failed',
        'Failed to create emergency case. Please try again or contact support.',
        [{ text: 'OK' }]
      );
    } finally {
      setIsCreatingCase(false);
    }
  };

  const panResponder = useRef(
    PanResponder.create({
      onStartShouldSetPanResponder: () => !disabled && !isUnlocked,
      onMoveShouldSetPanResponder: () => !disabled && !isUnlocked,
      onPanResponderGrant: () => {
        // Stronger vibration when touched for urgency
        Vibration.vibrate(100);
        AccessibilityInfo.announceForAccessibility('Emergency slider activated. Slide to the right and hold to confirm.');
      },
      onPanResponderMove: (_, gestureState) => {
        const { dx } = gestureState;
        const maxX = SLIDER_WIDTH - THUMB_SIZE;
        const newX = Math.max(0, Math.min(dx, maxX));
        translateX.setValue(newX);

        // If slider is moved to more than 85% of the way, start the emergency countdown
        if (newX > maxX * 0.85) {
          if (!isActivating) {
            startEmergencyCountdown();
          }
        } else {
          // If slider is moved back before activation, cancel the countdown
          if (isActivating) {
            resetCountdown();
          }
        }
      },
      onPanResponderRelease: () => {
        // If not activating, snap back to start
        if (!isActivating) {
          resetSlider();
        }
      },
      onPanResponderTerminate: () => {
        if (!isActivating) {
          resetSlider();
        }
      },
    })
  ).current;

  // Interpolate countdown to width
  const progressWidth = countdown.interpolate({
    inputRange: [0, 100],
    outputRange: ['0%', '100%']
  });

  // Glow effect interpolation
  const glowOpacity = glowAnimation.interpolate({
    inputRange: [0, 1],
    outputRange: [0.3, 0.8]
  });

  // Check if setup is required
  const needsSetup = !checkEmergencyEligibility();

  // Don't render if not visible, not authenticated
  if (!visible || !isAuthenticated) {
    return null;
  }

  return (
    <View style={styles.container}>
      <Text style={styles.title} accessibilityRole="header">
        🚨 Emergency Detention Alert
      </Text>

      {/* Setup Warning */}
      {needsSetup && (
        <View style={styles.setupWarning} accessibilityRole="alert">
          <Text style={styles.setupWarningTitle}>⚠️ Setup Required</Text>
          <Text style={styles.setupWarningText}>
            Complete your profile and add emergency contacts to enable emergency notifications
          </Text>
          <TouchableOpacity
            style={styles.setupButton}
            onPress={handleSetupRequired}
            accessibilityRole="button"
            accessibilityLabel="Complete emergency setup"
          >
            <Text style={styles.setupButtonText}>Complete Setup</Text>
          </TouchableOpacity>
        </View>
      )}

      {/* Main Instructions */}
      <Text style={styles.instruction} accessibilityLabel="Emergency slider instructions">
        {isActivating
          ? `⏱️ Hold for ${countdownValue} seconds to notify attorneys`
          : needsSetup
            ? 'Complete setup above to enable emergency notifications'
            : '⚠️ Slide and HOLD to notify attorneys of emergency detention'}
      </Text>

      {emergencyStatusLoading && (
        <Text style={styles.statusText}>Checking emergency status...</Text>
      )}

      {/* Enhanced Slider */}
      <Animated.View
        style={[
          styles.sliderContainer,
          disabled || needsSetup ? styles.disabledSlider : null,
          { transform: [{ scale: pulseAnimation }] }
        ]}
        accessibilityRole="button"
        accessibilityLabel="Emergency activation slider"
        accessibilityHint={needsSetup ? "Complete setup first" : "Slide to the right and hold for 3 seconds to activate emergency"}
        accessible={true}
      >
        {/* Glow Effect */}
        {!disabled && !needsSetup && (
          <Animated.View
            style={[
              styles.glowEffect,
              { opacity: glowOpacity }
            ]}
          />
        )}

        {/* Progress bar for countdown */}
        {isActivating && (
          <Animated.View
            style={[
              styles.progressBar,
              { width: progressWidth }
            ]}
          />
        )}

        <View style={styles.track} {...panResponder.panHandlers}>
          <Animated.View
            style={[
              styles.thumb,
              {
                transform: [{ translateX }],
              },
            ]}
          >
            <Text style={styles.thumbText}>
              {isActivating ? countdownValue : needsSetup ? '🔒' : '🚨'}
            </Text>
          </Animated.View>

          <Text style={styles.trackText}>
            {isActivating
              ? 'HOLD TO CONFIRM'
              : needsSetup
                ? 'COMPLETE SETUP'
                : 'DETENTION EMERGENCY'}
          </Text>
        </View>
      </Animated.View>

      {/* Critical Instructions */}
      {!needsSetup && !disabled && (
        <View style={styles.instructionsContainer}>
          <Text style={styles.instructionsTitle}>📋 When to Use:</Text>
          <Text style={styles.instructionsText}>
            • You are being detained by authorities{'\n'}
            • You need immediate legal assistance{'\n'}
            • You fear imminent detention{'\n'}
            • Your loved one has been detained
          </Text>

          <Text style={styles.warningText}>
            ⚠️ Only use for genuine emergencies. False alarms may delay help for others.
          </Text>
        </View>
      )}

      {/* Setup Prompt Modal */}
      <Modal
        visible={showSetupPrompt}
        animationType="slide"
        presentationStyle="pageSheet"
        transparent={false}
      >
        <View style={styles.setupModalContainer}>
          <Text style={styles.setupModalTitle}>🚨 Emergency Setup Required</Text>
          <Text style={styles.setupModalText}>
            To activate emergency notifications, you need to:
          </Text>

          <View style={styles.setupSteps}>
            <Text style={styles.setupStep}>✅ Complete your client profile</Text>
            <Text style={styles.setupStep}>✅ Add emergency contact information</Text>
            <Text style={styles.setupStep}>✅ Verify your identity</Text>
          </View>

          <Text style={styles.setupModalSubtext}>
            This ensures attorneys can reach you and your contacts during emergencies.
          </Text>

          <TouchableOpacity
            style={styles.setupModalButton}
            onPress={handleSetupPromptClose}
            accessibilityRole="button"
          >
            <Text style={styles.setupModalButtonText}>I Understand</Text>
          </TouchableOpacity>
        </View>
      </Modal>

      {/* Existing Modals */}
      <LocationPermissionModal
        visible={showLocationPermissionModal}
        onLocationGranted={handleLocationPermissionGranted}
        onManualEntry={handleLocationManualEntry}
        onClose={() => {
          setShowLocationPermissionModal(false);
          resetSlider();
        }}
      />

      <Modal
        visible={showManualLocationEntry}
        animationType="slide"
        presentationStyle="pageSheet"
      >
        <DetentionLocationInput
          onLocationSubmit={handleManualLocationSubmit}
          onCancel={handleManualLocationCancel}
          isLoading={false}
        />
      </Modal>

      <PhoneSecurityModal
        visible={showSecurityModal}
        onClose={handleSecurityModalClose}
        onConfirm={handleSecurityModalConfirm}
      />

      {/* Loading Overlays */}
      {isCapturingLocation && (
        <View style={styles.loadingOverlay}>
          <Text style={styles.loadingText}>📍 Getting your location...</Text>
          <Text style={styles.loadingSubtext}>This helps us notify the right attorneys</Text>
        </View>
      )}

      {isCreatingCase && (
        <View style={styles.loadingOverlay}>
          <Text style={styles.loadingText}>🚨 Creating emergency case...</Text>
          <Text style={styles.loadingSubtext}>Notifying attorneys in your area</Text>
        </View>
      )}
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    alignItems: 'center',
    marginVertical: 20,
    width: '100%',
  },
  disabledSlider: {
    borderColor: '#999',
    opacity: 0.5,
  },
  glowEffect: {
    backgroundColor: '#fff',
    borderRadius: (SLIDER_HEIGHT + 10) / 2,
    bottom: 0,
    left: 0,
    position: 'absolute',
    right: 0,
    top: 0,
  },
  instruction: {
    color: '#666',
    fontSize: 14,
    marginBottom: 15,
    textAlign: 'center',
  },
  instructionsContainer: {
    backgroundColor: '#fff',
    borderRadius: 10,
    marginBottom: 10,
    padding: 10,
  },
  instructionsText: {
    color: '#666',
    fontSize: 12,
  },
  instructionsTitle: {
    color: '#c00',
    fontSize: 16,
    fontWeight: 'bold',
    marginBottom: 5,
  },
  loadingOverlay: {
    alignItems: 'center',
    backgroundColor: 'rgba(0, 0, 0, 0.7)',
    borderRadius: 16,
    bottom: 0,
    justifyContent: 'center',
    left: 0,
    position: 'absolute',
    right: 0,
    top: 0,
  },
  loadingSubtext: {
    color: '#ffffff',
    fontSize: 12,
    fontWeight: '400',
  },
  loadingText: {
    color: '#ffffff',
    fontSize: 16,
    fontWeight: '600',
  },
  progressBar: {
    backgroundColor: 'rgba(255, 0, 0, 0.3)',
    bottom: 0,
    left: 0,
    position: 'absolute',
    top: 0,
    zIndex: 1,
  },
  setupButton: {
    backgroundColor: '#fff',
    borderRadius: 5,
    padding: 10,
  },
  setupButtonText: {
    color: '#c00',
    fontSize: 14,
    fontWeight: 'bold',
  },
  setupModalButton: {
    backgroundColor: '#c00',
    borderRadius: 5,
    padding: 10,
  },
  setupModalButtonText: {
    color: '#fff',
    fontSize: 14,
    fontWeight: 'bold',
  },
  setupModalContainer: {
    backgroundColor: '#fff',
    padding: 20,
  },
  setupModalSubtext: {
    color: '#666',
    fontSize: 12,
    marginBottom: 10,
  },
  setupModalText: {
    color: '#666',
    fontSize: 14,
    marginBottom: 10,
  },
  setupModalTitle: {
    color: '#c00',
    fontSize: 18,
    fontWeight: 'bold',
    marginBottom: 10,
  },
  setupStep: {
    color: '#666',
    fontSize: 12,
    marginBottom: 5,
  },
  setupSteps: {
    marginBottom: 10,
  },
  setupWarning: {
    backgroundColor: '#f60',
    borderRadius: 10,
    marginBottom: 10,
    padding: 10,
  },
  setupWarningText: {
    color: '#fff',
    fontSize: 12,
  },
  setupWarningTitle: {
    color: '#fff',
    fontSize: 16,
    fontWeight: 'bold',
    marginBottom: 5,
  },
  sliderContainer: {
    alignItems: 'center',
    backgroundColor: '#f8f8f8',
    borderColor: '#c00',
    borderRadius: (SLIDER_HEIGHT + 10) / 2,
    borderWidth: 2,
    height: SLIDER_HEIGHT + 10,
    justifyContent: 'center',
    overflow: 'hidden',
    width: SLIDER_WIDTH + 10,
  },
  statusText: {
    color: '#666',
    fontSize: 12,
    fontStyle: 'italic',
    marginBottom: 10,
    textAlign: 'center',
  },
  thumb: {
    alignItems: 'center',
    backgroundColor: '#c00',
    borderRadius: THUMB_SIZE / 2,
    elevation: 3,
    height: THUMB_SIZE,
    justifyContent: 'center',
    left: 0,
    position: 'absolute',
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 2,
    },
    shadowOpacity: 0.3,
    shadowRadius: 2,
    top: (SLIDER_HEIGHT - THUMB_SIZE) / 2,
    width: THUMB_SIZE,
    zIndex: 2,
  },
  thumbText: {
    color: '#fff',
    fontSize: 24,
  },
  title: {
    color: '#c00',
    fontSize: 18,
    fontWeight: 'bold',
    marginBottom: 8,
    textAlign: 'center',
  },
  track: {
    backgroundColor: '#fff0f0',
    borderRadius: SLIDER_HEIGHT / 2,
    height: SLIDER_HEIGHT,
    justifyContent: 'center',
    overflow: 'hidden',
    width: SLIDER_WIDTH,
  },
  trackText: {
    color: '#c00',
    fontSize: 16,
    fontWeight: 'bold',
    textAlign: 'center',
  },
  warningText: {
    color: '#f60',
    fontSize: 12,
    fontWeight: '500',
    marginBottom: 10,
    paddingHorizontal: 20,
    textAlign: 'center',
  },
});

export default EmergencySlider;
