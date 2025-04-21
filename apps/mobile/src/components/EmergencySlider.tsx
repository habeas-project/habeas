import React, { useState, useRef, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  PanResponder,
  Animated,
  Dimensions,
  Vibration
} from 'react-native';

const SLIDER_WIDTH = Dimensions.get('window').width - 60; // Padding on both sides
const SLIDER_HEIGHT = 72;
const THUMB_SIZE = 60;

interface EmergencySliderProps {
  onEmergencyActivated: () => void;
  disabled?: boolean;
}

const EmergencySlider: React.FC<EmergencySliderProps> = ({
  onEmergencyActivated,
  disabled = false
}) => {
  const [isUnlocked, setIsUnlocked] = useState(false);
  const [isActivating, setIsActivating] = useState(false);
  const translateX = useRef(new Animated.Value(0)).current;
  const countdown = useRef(new Animated.Value(0)).current;
  const countdownRef = useRef<number>(0);

  // Reset when disabled changes
  useEffect(() => {
    if (disabled) {
      resetSlider();
    }
  }, [disabled]);

  // Create countdown animation
  useEffect(() => {
    countdown.addListener(({ value }) => {
      countdownRef.current = value;

      // If countdown reaches 100, trigger emergency
      if (value >= 100 && isActivating) {
        Vibration.vibrate(500);
        setIsActivating(false);
        setIsUnlocked(true);
        onEmergencyActivated();
      }
    });

    return () => {
      countdown.removeAllListeners();
    };
  }, [countdown, isActivating, onEmergencyActivated]);

  const resetSlider = () => {
    setIsUnlocked(false);
    setIsActivating(false);
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
    Animated.timing(countdown, {
      toValue: 0,
      duration: 200,
      useNativeDriver: false,
    }).start();
  };

  const panResponder = useRef(
    PanResponder.create({
      onStartShouldSetPanResponder: () => !disabled && !isUnlocked,
      onMoveShouldSetPanResponder: () => !disabled && !isUnlocked,
      onPanResponderGrant: () => {
        // Vibrate when touched
        Vibration.vibrate(50);
      },
      onPanResponderMove: (_, gestureState) => {
        const { dx } = gestureState;
        const maxX = SLIDER_WIDTH - THUMB_SIZE;
        const newX = Math.max(0, Math.min(dx, maxX));
        translateX.setValue(newX);

        // If slider is moved to more than 90% of the way, start the emergency countdown
        if (newX > maxX * 0.9) {
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

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Emergency Slider</Text>
      <Text style={styles.instruction}>
        {isActivating
          ? 'Hold for 3 seconds to activate emergency protocol'
          : 'Slide and hold to activate emergency protocol'}
      </Text>

      <View
        style={[
          styles.sliderContainer,
          disabled ? styles.disabledSlider : null
        ]}
      >
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
            <Text style={styles.thumbText}>{isActivating ? '⚠️' : '→'}</Text>
          </Animated.View>

          <Text style={styles.trackText}>
            {isActivating ? 'HOLD' : 'EMERGENCY'}
          </Text>
        </View>
      </View>
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
  instruction: {
    color: '#666',
    fontSize: 14,
    marginBottom: 15,
    textAlign: 'center',
  },
  progressBar: {
    backgroundColor: 'rgba(255, 0, 0, 0.3)',
    bottom: 0,
    left: 0,
    position: 'absolute',
    top: 0,
    zIndex: 1,
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
    fontSize: 20,
    fontWeight: 'bold',
    marginBottom: 5,
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
});

export default EmergencySlider;