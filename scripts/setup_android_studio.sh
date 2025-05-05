#!/bin/bash
# setup_android_studio.sh - Android Studio Setup Script for Habeas Mobile Development
# Created: $(date)

echo "Starting Android Studio setup for Habeas mobile development..."

# Install required dependencies
echo "Installing OpenJDK 11..."
sudo apt update
sudo apt install -y openjdk-11-jdk

# Download and install Android Studio
echo "Downloading Android Studio..."
wget https://redirector.gvt1.com/edgedl/android/studio/ide-zips/2022.3.1.20/android-studio-2022.3.1.20-linux.tar.gz

echo "Installing Android Studio to /opt/..."
sudo tar -xzf android-studio-*.tar.gz -C /opt/
sudo ln -sf /opt/android-studio/bin/studio.sh /usr/local/bin/android-studio

# Clean up downloaded archive
echo "Cleaning up downloaded files..."
rm android-studio-*.tar.gz

# Set up environment variables
echo "Setting up environment variables..."
cat << 'EOF' >> ~/.bashrc

# Android SDK Environment Variables
export ANDROID_HOME=$HOME/Android/Sdk
export PATH=$PATH:$ANDROID_HOME/emulator
export PATH=$PATH:$ANDROID_HOME/tools
export PATH=$PATH:$ANDROID_HOME/tools/bin
export PATH=$PATH:$ANDROID_HOME/platform-tools
EOF

echo "Applying environment variables to current shell..."
export ANDROID_HOME=$HOME/Android/Sdk
export PATH=$PATH:$ANDROID_HOME/emulator
export PATH=$PATH:$ANDROID_HOME/tools
export PATH=$PATH:$ANDROID_HOME/tools/bin
export PATH=$PATH:$ANDROID_HOME/platform-tools

# Create a detailed instruction file
echo "Creating detailed setup instructions..."
cat << 'EOF' > android_studio_manual_steps.md
# Android Studio Manual Setup Steps

This document contains instructions for the manual setup steps needed after running the automated setup script.

## 1. Launch Android Studio

```bash
android-studio
```

## 2. Complete the Android Studio Setup Wizard

- Choose "Do not import settings" if this is your first installation
- Select "Standard" installation type when prompted
- The wizard will download and install:
  - Android SDK
  - Android SDK Command-line Tools
  - Android SDK Build-Tools
  - Android Emulator
  - Android SDK Platform
- Click "Finish" when completed

## 3. Install Additional SDK Components

After the initial setup, you'll need to install specific components for React Native/Expo development:

1. Open Android Studio
2. Click on "More Actions" or "Configure" from the welcome screen
3. Select "SDK Manager"
4. In the "SDK Platforms" tab:
   - Check the box next to "Android 13 (Tiramisu)" or newer
   - Check "Show Package Details" at the bottom
   - Make sure the following are checked:
     - Android SDK Platform 33 (or latest)
     - Intel x86 Atom_64 System Image or Google APIs Intel x86 Atom System Image
5. In the "SDK Tools" tab:
   - Check "Show Package Details"
   - Under "Android SDK Build-Tools", select the latest version
   - Select "Android SDK Command-line Tools (latest)"
   - Select "Android Emulator"
   - Select "Android SDK Platform-Tools"
6. Click "Apply" to download and install

## 4. Create a Virtual Device (Emulator)

1. Open Android Studio
2. Click on "More Actions" or "Device Manager" from the welcome screen
3. Click "Create Device"
4. Select a device definition (e.g., "Pixel 6")
5. Click "Next"
6. Select a system image:
   - Select the "Recommended" tab
   - Choose the latest available release (e.g., Android 13)
   - If the desired system image isn't downloaded, click "Download" next to it
7. Click "Next"
8. Set the AVD Name (e.g., "Pixel_6_API_33") or keep the default
9. Leave other settings at their default values
10. Click "Finish"

## 5. Start the Emulator

Method 1: From Android Studio Device Manager
- Open Android Studio
- Click on "Device Manager"
- Click the play button (▶) next to your virtual device

Method 2: From Command Line
```bash
# List available emulators
emulator -list-avds

# Start a specific emulator
emulator -avd [YourEmulatorName]
```

## 6. Run Your Expo App on the Emulator

Once the emulator is running:

```bash
# Navigate to your mobile app directory
cd apps/mobile

# Start Expo on Android
npm run android
```

## 7. Troubleshooting

### Common Issues:

1. **"Failed to resolve the Android SDK path"**
   - Check that ANDROID_HOME is set correctly:
   ```bash
   echo $ANDROID_HOME
   ```
   - Verify the SDK exists at that location

2. **"Error: spawn adb ENOENT"**
   - Ensure adb is installed and in your PATH:
   ```bash
   source ~/.bashrc
   which adb
   ```

3. **Emulator is slow or crashes**
   - Ensure virtualization is enabled in your BIOS
   - For WSL2 users, consider using Android Studio directly in Windows

4. **"Unable to locate adb within SDK"**
   - Install Android SDK Platform-Tools:
   ```bash
   sdkmanager "platform-tools"
   ```

5. **"INSTALL_FAILED_UPDATE_INCOMPATIBLE"**
   - Uninstall the app from the emulator and try again

For more detailed troubleshooting, visit:
https://reactnative.dev/docs/environment-setup
EOF

echo ""
echo "======================================================================"
echo "Android Studio setup script completed!"
echo ""
echo "A detailed instruction file has been created: android_studio_manual_steps.md"
echo ""
echo "IMPORTANT: For the environment changes to take effect in your current terminal,"
echo "please run: source ~/.bashrc"
echo ""
echo "Next steps summary:"
echo "1. Launch Android Studio:        android-studio"
echo "2. Complete the setup wizard     (Choose 'Standard' installation)"
echo "3. Install additional SDK components (see instruction file)"
echo "4. Create a virtual device"
echo "5. Start the emulator"
echo "6. Run your Expo app:            cd apps/mobile && npm run android"
echo "======================================================================"
