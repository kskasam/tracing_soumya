# Running the App on Mobile (iOS)

## Prerequisites
1. Flutter SDK installed at `/Users/santhosh/Documents/flutter`
2. Xcode installed (for iOS development)
3. CocoaPods installed

## Step-by-Step Instructions

### Step 1: Navigate to the example directory
```bash
cd /Users/santhosh/Documents/tracing_soumya/tracing_soumya/example
```

### Step 2: Set Flutter environment (if needed)
```bash
export FLUTTER_ROOT=/Users/santhosh/Documents/flutter
export PATH="$FLUTTER_ROOT/bin:$PATH"
```

### Step 3: Install Flutter dependencies
```bash
flutter pub get
```

### Step 4: Install CocoaPods dependencies (iOS only)
```bash
cd ios
export LANG=en_US.UTF-8
pod install
cd ..
```

**Note:** If you get encoding errors, make sure to set `export LANG=en_US.UTF-8` before running `pod install`.

### Step 5: Check available devices
```bash
flutter devices
```

You should see your iOS simulator listed.

### Step 6: Run on iOS simulator
```bash
flutter run -d "iPhone 16 Pro"
```

Or use the device ID:
```bash
flutter run -d 68E56D2C-3EE7-47EF-838D-4F7205934995
```

### Alternative: Use the helper script
```bash
./run_mobile.sh ios
```

## Troubleshooting

### If you see "No devices found" or "not supported by this project":
1. Run `flutter create . --platforms=ios` to regenerate iOS project files
2. Make sure CocoaPods are installed: `pod install` in the `ios` directory
3. Run `flutter clean` and then `flutter pub get`

### If CocoaPods installation fails:
1. Set encoding: `export LANG=en_US.UTF-8`
2. Try: `pod deintegrate && pod install`

### If permission errors occur:
1. Run `chmod -R u+w .` in the example directory
2. Make sure Flutter SDK has proper permissions
3. Check that all parent directories are accessible

## Quick Command Reference

```bash
# Full setup (run once)
cd /Users/santhosh/Documents/tracing_soumya/tracing_soumya/example
export FLUTTER_ROOT=/Users/santhosh/Documents/flutter
export PATH="$FLUTTER_ROOT/bin:$PATH"
flutter pub get
cd ios && export LANG=en_US.UTF-8 && pod install && cd ..

# Run on iOS (after setup)
flutter run -d "iPhone 16 Pro"
```

