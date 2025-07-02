import { config } from 'dotenv';
import { resolve } from 'path';
import { execSync } from 'child_process';
import { networkInterfaces } from 'os';

// Load .env from project root (not mobile directory)
config({ path: resolve(__dirname, '../../.env') });

// Function to dynamically detect WSL IP
function getWSLIP() {
    try {
        // First try to get WSL IP using the same method as the update script
        const wslIP = execSync('hostname -I | awk \'{print $1}\'', { encoding: 'utf8' }).trim();
        if (wslIP && wslIP !== '127.0.0.1') {
            return wslIP;
        }
    } catch (error) {
        console.warn('Could not detect WSL IP via hostname command:', error.message);
    }

    try {
        // Fallback: Try to find the WSL network interface
        const interfaces = networkInterfaces();
        for (const [, addresses] of Object.entries(interfaces)) {
            if (addresses) {
                for (const addr of addresses) {
                    // Look for IPv4 addresses that are not localhost and not in common Docker ranges
                    if (addr.family === 'IPv4' &&
                        !addr.internal &&
                        !addr.address.startsWith('127.') &&
                        !addr.address.startsWith('172.17.') && // Docker default bridge
                        !addr.address.startsWith('172.18.')) { // Docker compose networks
                        return addr.address;
                    }
                }
            }
        }
    } catch (error) {
        console.warn('Could not detect IP via network interfaces:', error.message);
    }

    // Final fallback
    return 'localhost';
}

// Get the dynamic API base URL
const dynamicIP = getWSLIP();
const apiBaseUrl = process.env.EXPO_PUBLIC_API_BASE_URL || `http://${dynamicIP}:8000`;

console.log(`🔗 Expo Config: Detected WSL IP: ${dynamicIP}`);
console.log(`🌐 Expo Config: API Base URL: ${apiBaseUrl}`);

export default {
    expo: {
        name: "Habeas",
        slug: "habeas",
        version: "1.0.0",
        orientation: "portrait",
        icon: "./assets/icon.png",
        splash: {
            image: "./assets/splash.png",
            resizeMode: "contain",
            backgroundColor: "#ffffff"
        },
        updates: {
            fallbackToCacheTimeout: 0
        },
        assetBundlePatterns: [
            "**/*"
        ],
        ios: {
            supportsTablet: true
        },
        android: {
            adaptiveIcon: {
                foregroundImage: "./assets/icon.png",
                backgroundColor: "#ffffff"
            }
        },
        web: {
            favicon: "./assets/favicon.png"
        },
        newArchEnabled: true,
        plugins: [
            "expo-secure-store",
            [
                "expo-location",
                {
                    locationAlwaysAndWhenInUsePermission: "This app needs access to location to connect you with attorneys in your area during emergencies.",
                    locationAlwaysPermission: "This app needs access to location to connect you with attorneys in your area during emergencies.",
                    locationWhenInUsePermission: "This app needs access to location to connect you with attorneys in your area during emergencies.",
                    isIosBackgroundLocationEnabled: false,
                    isAndroidBackgroundLocationEnabled: false,
                    isAndroidForegroundServiceEnabled: false
                }
            ]
        ],
        extra: {
            eas: {
                projectId: "YOUR_EAS_PROJECT_ID"
            },
            // Environment variables for the app (dynamically detected)
            EXPO_PUBLIC_API_BASE_URL: apiBaseUrl,
            EXPO_PUBLIC_AUTH_MODE: process.env.EXPO_PUBLIC_AUTH_MODE || "mock"
        }
    }
};
