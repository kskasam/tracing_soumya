#!/bin/bash
# Helper script to run Flutter app on mobile devices
# Usage: ./run_mobile.sh [ios|android|device-name]

export FLUTTER_ROOT=/Users/santhosh/Documents/flutter
export PATH="$FLUTTER_ROOT/bin:$PATH"
export LANG=en_US.UTF-8

cd "$(dirname "$0")"

# Check if iOS pods need to be installed
if [ ! -d "ios/Pods" ]; then
    echo "Installing CocoaPods dependencies..."
    cd ios
    pod install
    cd ..
fi

# Get device preference from argument or default to iOS
DEVICE_TYPE="${1:-ios}"

if [ "$DEVICE_TYPE" = "ios" ]; then
    # List iOS devices and use the first available simulator
    DEVICE=$(flutter devices | grep -i "ios.*simulator" | head -1 | awk '{print $5}' | tr -d '()')
    if [ -z "$DEVICE" ]; then
        echo "No iOS simulator found. Available devices:"
        flutter devices
        exit 1
    fi
    echo "Running on iOS device: $DEVICE"
    flutter run -d "$DEVICE"
elif [ "$DEVICE_TYPE" = "android" ]; then
    echo "Running on Android device..."
    flutter run -d android
else
    # Use the device name/ID provided
    echo "Running on device: $DEVICE_TYPE"
    flutter run -d "$DEVICE_TYPE"
fi

