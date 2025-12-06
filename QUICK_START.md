# Quick Start Guide

## Add to Your Project (3 Steps)

### 1. Add Dependency

Edit your `pubspec.yaml`:

```yaml
dependencies:
  flutter:
    sdk: flutter
  
  tracing_game:
    path: /Users/santhosh/Documents/tracing_soumya/tracing_soumya
    # Or relative path from your project:
    # path: ../tracing_soumya/tracing_soumya
```

### 2. Install Dependencies

```bash
flutter pub get

# For iOS (if building for iOS):
cd ios
export LANG=en_US.UTF-8
pod install
cd ..
```

### 3. Use in Your Code

```dart
import 'package:flutter/material.dart';
import 'package:tracing_game/tracing_game.dart';

class MyTracingPage extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('Tracing')),
      body: TracingCharsGame(
        traceShapeModel: [
          TraceCharsModel(chars: [
            TraceCharModel(
              char: 'A',
              traceShapeOptions: TraceShapeOptions(
                innerPaintColor: Colors.blue,
              ),
            ),
          ]),
        ],
        onTracingUpdated: (index) => print('Progress: $index'),
        onGameFinished: (screenIndex) => print('Done!'),
        onCurrentTracingScreenFinished: (screenIndex) {},
      ),
    );
  }
}
```

That's it! You're ready to use tracing in your app.

