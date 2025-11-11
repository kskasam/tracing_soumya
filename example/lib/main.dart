import 'package:flutter/material.dart';
import 'package:tracing_game/tracing_game.dart';

void main() {
  runApp(const MyApp());
}

class MyApp extends StatefulWidget {
  const MyApp({super.key});

  @override
  State<MyApp> createState() => _MyAppState();
}

class _MyAppState extends State<MyApp> {
  @override
  void initState() {
    super.initState();
  }

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      home: Scaffold(
        appBar: AppBar(
          title: const Text('Tracing Game'),
        ),
        body: Column(
          // spacing: 3,
          children: [
            Expanded(
              child: TracingCharsGame(
                showAnchor: true,
                // Test with Telugu letters
                traceShapeModel: [
                  // First screen: Vowels
                  TraceCharsModel(chars: [
                    TraceCharModel(
                      char: 'అ', // a
                      traceShapeOptions: const TraceShapeOptions(
                        innerPaintColor: Colors.orange,
                      ),
                    ),
                    TraceCharModel(
                      char: 'ఆ', // aa
                      traceShapeOptions: const TraceShapeOptions(
                        innerPaintColor: Colors.blue,
                      ),
                    ),
                  ]),
                  // Second screen: More vowels
                  TraceCharsModel(chars: [
                    TraceCharModel(
                      char: 'ఇ', // i
                      traceShapeOptions: const TraceShapeOptions(
                        innerPaintColor: Colors.green,
                      ),
                    ),
                    TraceCharModel(
                      char: 'ఈ', // ii
                      traceShapeOptions: const TraceShapeOptions(
                        innerPaintColor: Colors.purple,
                      ),
                    ),
                  ]),
                  // Third screen: Consonants
                  TraceCharsModel(chars: [
                    TraceCharModel(
                      char: 'క', // ka
                      traceShapeOptions: const TraceShapeOptions(
                        innerPaintColor: Colors.red,
                      ),
                    ),
                    TraceCharModel(
                      char: 'గ', // ga
                      traceShapeOptions: const TraceShapeOptions(
                        innerPaintColor: Colors.teal,
                      ),
                    ),
                  ]),
                ],
                onTracingUpdated: (int currentTracingIndex) async {
                  print('/////onTracingUpdated:' +
                      currentTracingIndex.toString());
                },
                onGameFinished: (int screenIndex) async {
                  print('/////onGameFinished:' + screenIndex.toString());
                },
                onCurrentTracingScreenFinished: (int currentScreenIndex) async {
                  print('/////onCurrentTracingScreenFinished:' +
                      currentScreenIndex.toString());
                },
              ),
            ),
            Expanded(
              child: TracingGeometricShapesGame(
                traceGeoMetricShapeModels: [
                  TraceGeoMetricShapeModel(shapes: [
                    MathShapeWithOption(
                        shape: MathShapes.circle,
                        traceShapeOptions: const TraceShapeOptions(
                            innerPaintColor: Colors.orange)),
                    MathShapeWithOption(
                        shape: MathShapes.triangle1,
                        traceShapeOptions: const TraceShapeOptions(
                            innerPaintColor: Colors.orange))
                  ]),
                  TraceGeoMetricShapeModel(shapes: [
                    MathShapeWithOption(
                        shape: MathShapes.triangle3,
                        traceShapeOptions: const TraceShapeOptions(
                            innerPaintColor: Colors.orange)),
                    MathShapeWithOption(
                        shape: MathShapes.triangle2,
                        traceShapeOptions: const TraceShapeOptions(
                            innerPaintColor: Colors.orange))
                  ]),
                ],
              ),
            ),
            Expanded(
              child: TracingWordGame(
                words: [
                  // Test English words
                  TraceWordModel(
                      word: 'I Love',
                      traceShapeOptions:
                          const TraceShapeOptions(indexColor: Colors.green)),
                  // Test Telugu words (mixed with English)
                  TraceWordModel(
                      word: 'కమల', // kamala (lotus)
                      traceShapeOptions:
                          const TraceShapeOptions(indexColor: Colors.orange)),
                  TraceWordModel(
                      word: 'నమస్తే', // namaste
                      traceShapeOptions:
                          const TraceShapeOptions(indexColor: Colors.blue)),
                ],
                onTracingUpdated: (int currentTracingIndex) async {
                  print('/////onTracingUpdated:' +
                      currentTracingIndex.toString());
                },
                onGameFinished: (int screenIndex) async {
                  print('/////onGameFinished:' + screenIndex.toString());
                },
                onCurrentTracingScreenFinished: (int currentScreenIndex) async {
                  print('/////onCurrentTracingScreenFinished:' +
                      currentScreenIndex.toString());
                },
              ),
            ),
          ],
        ),
      ),
    );
  }
}
