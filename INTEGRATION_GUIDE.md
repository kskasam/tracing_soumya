# Integration Guide: Adding Tracing Game Plugin to Your Flutter Project

This guide will help you integrate the `tracing_game` plugin into your existing Flutter project.

## Prerequisites

- Flutter SDK (>=3.0.0)
- Dart SDK (>=3.0.0)
- An existing Flutter project

## Step 1: Add the Plugin as a Dependency

### Option A: Using Local Path (Recommended for Development)

1. **Copy or reference the plugin directory**

   If the plugin is in a local directory, add it to your `pubspec.yaml`:

   ```yaml
   dependencies:
     flutter:
       sdk: flutter
     
     tracing_game:
       path: ../tracing_soumya/tracing_soumya
       # Or use absolute path:
       # path: /Users/santhosh/Documents/tracing_soumya/tracing_soumya
   ```

### Option B: Using Git Repository

   ```yaml
   dependencies:
     tracing_game:
       git:
         url: https://github.com/your-username/tracing_game.git
         ref: main  # or specific branch/tag
   ```

### Option C: Using pub.dev (if published)

   ```yaml
   dependencies:
     tracing_game: ^0.0.4
   ```

## Step 2: Install Dependencies

Run the following command in your project root:

```bash
flutter pub get
```

## Step 3: Platform-Specific Setup

### iOS Setup

1. **Navigate to iOS directory:**
   ```bash
   cd ios
   ```

2. **Install CocoaPods dependencies:**
   ```bash
   export LANG=en_US.UTF-8
   pod install
   cd ..
   ```

### Android Setup

No additional setup required for Android. The plugin will work automatically.

## Step 4: Import and Use the Plugin

### Basic Usage Example

Create a new file or modify an existing one in your `lib/` directory:

```dart
import 'package:flutter/material.dart';
import 'package:tracing_game/tracing_game.dart';

class TracingScreen extends StatefulWidget {
  const TracingScreen({super.key});

  @override
  State<TracingScreen> createState() => _TracingScreenState();
}

class _TracingScreenState extends State<TracingScreen> {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Tracing Game'),
      ),
      body: TracingCharsGame(
        traceShapeModel: [
          TraceCharsModel(chars: [
            TraceCharModel(
              char: 'A', // English letter
              traceShapeOptions: const TraceShapeOptions(
                innerPaintColor: Colors.blue,
              ),
            ),
            TraceCharModel(
              char: 'B',
              traceShapeOptions: const TraceShapeOptions(
                innerPaintColor: Colors.green,
              ),
            ),
          ]),
        ],
        onTracingUpdated: (int currentTracingIndex) async {
          print('Tracing progress: $currentTracingIndex');
        },
        onGameFinished: (int screenIndex) async {
          print('Game finished on screen: $screenIndex');
        },
        onCurrentTracingScreenFinished: (int currentScreenIndex) async {
          print('Screen finished: $currentScreenIndex');
        },
      ),
    );
  }
}
```

## Step 5: Available Components

The plugin provides three main components:

### 1. TracingCharsGame - For Letters/Characters

```dart
TracingCharsGame(
  traceShapeModel: [
    TraceCharsModel(chars: [
      TraceCharModel(
        char: 'A', // Supports: English, Telugu, Arabic
        traceShapeOptions: TraceShapeOptions(
          innerPaintColor: Colors.blue,
        ),
      ),
    ]),
  ],
  onTracingUpdated: (int index) {},
  onGameFinished: (int screenIndex) {},
  onCurrentTracingScreenFinished: (int screenIndex) {},
)
```

### 2. TracingGeometricShapesGame - For Shapes

```dart
TracingGeometricShapesGame(
  traceGeoMetricShapeModels: [
    TraceGeoMetricShapeModel(shapes: [
      MathShapeWithOption(
        shape: MathShapes.circle,
        traceShapeOptions: TraceShapeOptions(
          innerPaintColor: Colors.orange,
        ),
      ),
      MathShapeWithOption(
        shape: MathShapes.triangle1,
        traceShapeOptions: TraceShapeOptions(
          innerPaintColor: Colors.blue,
        ),
      ),
    ]),
  ],
)
```

### 3. TracingWordGame - For Words

```dart
TracingWordGame(
  traceWordModels: [
    TraceWordModel(
      word: 'Hello',
      traceShapeOptions: TraceShapeOptions(
        innerPaintColor: Colors.purple,
      ),
    ),
  ],
  onTracingUpdated: (int index) {},
  onGameFinished: (int screenIndex) {},
  onCurrentTracingScreenFinished: (int screenIndex) {},
)
```

## Step 6: Supported Characters and Shapes

### Supported Languages:
- **English** (uppercase and lowercase)
- **Telugu** (all vowels and consonants)
- **Arabic** (various letters)
- **Numbers** (0-10)

### Supported Shapes:
- `MathShapes.circle`
- `MathShapes.rectangle`
- `MathShapes.triangle1`
- `MathShapes.triangle2`
- `MathShapes.triangle3`
- `MathShapes.triangle4`

## Step 7: Customization Options

### TraceShapeOptions

```dart
TraceShapeOptions(
  innerPaintColor: Colors.blue,      // Color for tracing
  outerPaintColor: Colors.grey,      // Color for outline
  strokeWidth: 5.0,                  // Stroke width
  // Add other customization options as needed
)
```

## Step 8: Complete Example App

Here's a complete example showing all three components:

```dart
import 'package:flutter/material.dart';
import 'package:tracing_game/tracing_game.dart';

void main() {
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Tracing Game Demo',
      theme: ThemeData(
        primarySwatch: Colors.blue,
      ),
      home: const TracingDemo(),
    );
  }
}

class TracingDemo extends StatefulWidget {
  const TracingDemo({super.key});

  @override
  State<TracingDemo> createState() => _TracingDemoState();
}

class _TracingDemoState extends State<TracingDemo> {
  int _currentIndex = 0;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Tracing Game Demo'),
      ),
      body: IndexedStack(
        index: _currentIndex,
        children: [
          // Letters/Characters
          TracingCharsGame(
            traceShapeModel: [
              TraceCharsModel(chars: [
                TraceCharModel(
                  char: 'A',
                  traceShapeOptions: const TraceShapeOptions(
                    innerPaintColor: Colors.blue,
                  ),
                ),
                TraceCharModel(
                  char: 'B',
                  traceShapeOptions: const TraceShapeOptions(
                    innerPaintColor: Colors.green,
                  ),
                ),
              ]),
            ],
            onTracingUpdated: (index) {
              print('Tracing updated: $index');
            },
            onGameFinished: (screenIndex) {
              print('Game finished: $screenIndex');
            },
            onCurrentTracingScreenFinished: (screenIndex) {
              print('Screen finished: $screenIndex');
            },
          ),
          // Geometric Shapes
          TracingGeometricShapesGame(
            traceGeoMetricShapeModels: [
              TraceGeoMetricShapeModel(shapes: [
                MathShapeWithOption(
                  shape: MathShapes.circle,
                  traceShapeOptions: const TraceShapeOptions(
                    innerPaintColor: Colors.orange,
                  ),
                ),
              ]),
            ],
          ),
          // Words
          TracingWordGame(
            traceWordModels: [
              TraceWordModel(
                word: 'Hello',
                traceShapeOptions: const TraceShapeOptions(
                  innerPaintColor: Colors.purple,
                ),
              ),
            ],
            onTracingUpdated: (index) {},
            onGameFinished: (screenIndex) {},
            onCurrentTracingScreenFinished: (screenIndex) {},
          ),
        ],
      ),
      bottomNavigationBar: BottomNavigationBar(
        currentIndex: _currentIndex,
        onTap: (index) {
          setState(() {
            _currentIndex = index;
          });
        },
        items: const [
          BottomNavigationBarItem(
            icon: Icon(Icons.text_fields),
            label: 'Letters',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.shape_line),
            label: 'Shapes',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.text_snippet),
            label: 'Words',
          ),
        ],
      ),
    );
  }
}
```

## Troubleshooting

### Issue: Plugin not found
**Solution:** Make sure the path in `pubspec.yaml` is correct and run `flutter pub get`

### Issue: iOS build fails
**Solution:** 
1. Navigate to `ios/` directory
2. Run `pod install` with `export LANG=en_US.UTF-8`
3. Clean and rebuild: `flutter clean && flutter pub get`

### Issue: Assets not loading
**Solution:** The plugin includes all assets automatically. If issues persist, ensure you've run `flutter pub get` after adding the dependency.

### Issue: Permission errors
**Solution:** 
1. Set `FLUTTER_ROOT` environment variable
2. Run `chmod -R u+w .` in your project directory
3. Clean and rebuild

## Additional Resources

- Check the `example/` directory in the plugin for more examples
- See `lib/tracing_game.dart` for all exported classes and functions
- Review `ARCHITECTURE.md` for detailed implementation details

## Next Steps

1. Add the dependency to your `pubspec.yaml`
2. Run `flutter pub get`
3. Import the package: `import 'package:tracing_game/tracing_game.dart';`
4. Start using the tracing components in your app!

Happy tracing! 🎨

