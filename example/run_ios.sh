#!/bin/bash
# Helper script to run Flutter app on iOS
# This script ensures all environment variables are set correctly

export FLUTTER_ROOT=/Users/santhosh/Documents/flutter
export PATH="$FLUTTER_ROOT/bin:$PATH"
export LANG=en_US.UTF-8

cd "$(dirname "$0")"

echo "Setting up iOS project..."

# Ensure CocoaPods are installed
if [ ! -d "ios/Pods" ]; then
    echo "Installing CocoaPods dependencies..."
    cd ios
    pod install
    cd ..
fi

# Get Flutter dependencies
echo "Getting Flutter dependencies..."
flutter pub get

# Run on iOS simulator
echo "Launching on iOS simulator..."
DEVICE_ID=$(flutter devices | grep -i "ios.*simulator" | head -1 | awk '{print $5}' | tr -d '()')

if [ -z "$DEVICE_ID" ]; then
    echo "No iOS simulator found. Available devices:"
    flutter devices
    exit 1
fi

echo "Running on device: $DEVICE_ID"
flutter run -d "$DEVICE_ID"

