// Copy this file to your Flutter project and use it as a starting point
// File: lib/tracing_example.dart

import 'package:flutter/material.dart';
import 'package:tracing_game/tracing_game.dart';

/// Example screen showing how to use the tracing_game plugin
class TracingExampleScreen extends StatefulWidget {
  const TracingExampleScreen({super.key});

  @override
  State<TracingExampleScreen> createState() => _TracingExampleScreenState();
}

class _TracingExampleScreenState extends State<TracingExampleScreen> {
  int _currentTab = 0;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Tracing Game Example'),
      ),
      body: IndexedStack(
        index: _currentTab,
        children: [
          // Tab 1: Letters/Characters
          _buildLettersTab(),
          // Tab 2: Shapes
          _buildShapesTab(),
          // Tab 3: Words
          _buildWordsTab(),
        ],
      ),
      bottomNavigationBar: BottomNavigationBar(
        currentIndex: _currentTab,
        onTap: (index) {
          setState(() {
            _currentTab = index;
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

  Widget _buildLettersTab() {
    return TracingCharsGame(
      traceShapeModel: [
        TraceCharsModel(chars: [
          TraceCharModel(
            char: 'A', // English uppercase
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
          // Add Telugu example
          TraceCharModel(
            char: 'అ', // Telugu vowel
            traceShapeOptions: const TraceShapeOptions(
              innerPaintColor: Colors.orange,
            ),
          ),
        ]),
      ],
      onTracingUpdated: (int currentTracingIndex) async {
        print('Tracing progress: $currentTracingIndex');
      },
      onGameFinished: (int screenIndex) async {
        print('Game finished on screen: $screenIndex');
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Tracing completed!')),
        );
      },
      onCurrentTracingScreenFinished: (int currentScreenIndex) async {
        print('Screen $currentScreenIndex finished');
      },
    );
  }

  Widget _buildShapesTab() {
    return TracingGeometricShapesGame(
      traceGeoMetricShapeModels: [
        TraceGeoMetricShapeModel(shapes: [
          MathShapeWithOption(
            shape: MathShapes.circle,
            traceShapeOptions: const TraceShapeOptions(
              innerPaintColor: Colors.orange,
            ),
          ),
          MathShapeWithOption(
            shape: MathShapes.triangle1,
            traceShapeOptions: const TraceShapeOptions(
              innerPaintColor: Colors.blue,
            ),
          ),
        ]),
        TraceGeoMetricShapeModel(shapes: [
          MathShapeWithOption(
            shape: MathShapes.rectangle,
            traceShapeOptions: const TraceShapeOptions(
              innerPaintColor: Colors.purple,
            ),
          ),
        ]),
      ],
    );
  }

  Widget _buildWordsTab() {
    return TracingWordGame(
      traceWordModels: [
        TraceWordModel(
          word: 'Hello',
          traceShapeOptions: const TraceShapeOptions(
            innerPaintColor: Colors.purple,
          ),
        ),
        TraceWordModel(
          word: 'World',
          traceShapeOptions: const TraceShapeOptions(
            innerPaintColor: Colors.teal,
          ),
        ),
      ],
      onTracingUpdated: (int currentTracingIndex) async {
        print('Word tracing progress: $currentTracingIndex');
      },
      onGameFinished: (int screenIndex) async {
        print('Word game finished on screen: $screenIndex');
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Word tracing completed!')),
        );
      },
      onCurrentTracingScreenFinished: (int currentScreenIndex) async {
        print('Word screen $currentScreenIndex finished');
      },
    );
  }
}

/// Simple example - just letters
class SimpleTracingExample extends StatelessWidget {
  const SimpleTracingExample({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Simple Tracing'),
      ),
      body: TracingCharsGame(
        traceShapeModel: [
          TraceCharsModel(chars: [
            TraceCharModel(
              char: 'A',
              traceShapeOptions: const TraceShapeOptions(
                innerPaintColor: Colors.blue,
              ),
            ),
          ]),
        ],
        onTracingUpdated: (index) {},
        onGameFinished: (screenIndex) {},
        onCurrentTracingScreenFinished: (screenIndex) {},
      ),
    );
  }
}

