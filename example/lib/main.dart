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
                // Telugu letters with multiple pages
                traceShapeModel: [
                  // Page 1: అ (a) and ఆ (aa)
                  TraceCharsModel(chars: [
                    TraceCharModel(
                      char: 'అ', // Telugu vowel "a"
                      traceShapeOptions: const TraceShapeOptions(
                        innerPaintColor: Colors.orange,
                      ),
                    ),
                    TraceCharModel(
                      char: 'ఆ', // Telugu vowel "aa"
                      traceShapeOptions: const TraceShapeOptions(
                        innerPaintColor: Colors.blue,
                      ),
                    ),
                  ]),
                  // Page 2: ఇ (i) and ఈ (ii)
                  TraceCharsModel(chars: [
                    TraceCharModel(
                      char: 'ఇ', // Telugu vowel "i"
                      traceShapeOptions: const TraceShapeOptions(
                        innerPaintColor: Colors.green,
                      ),
                    ),
                    TraceCharModel(
                      char: 'ఈ', // Telugu vowel "ii"
                      traceShapeOptions: const TraceShapeOptions(
                        innerPaintColor: Colors.purple,
                      ),
                    ),
                  ]),
                  // Page 3: ఉ (u) and ఊ (uu)
                  TraceCharsModel(chars: [
                    TraceCharModel(
                      char: 'ఉ', // Telugu vowel "u"
                      traceShapeOptions: const TraceShapeOptions(
                        innerPaintColor: Colors.red,
                      ),
                    ),
                    TraceCharModel(
                      char: 'ఊ', // Telugu vowel "uu"
                      traceShapeOptions: const TraceShapeOptions(
                        innerPaintColor: Colors.pink,
                      ),
                    ),
                  ]),
                  // Page 4: ఎ (e) and ఏ (ee)
                  TraceCharsModel(chars: [
                    TraceCharModel(
                      char: 'ఎ', // Telugu vowel "e"
                      traceShapeOptions: const TraceShapeOptions(
                        innerPaintColor: Colors.teal,
                      ),
                    ),
                    TraceCharModel(
                      char: 'ఏ', // Telugu vowel "ee"
                      traceShapeOptions: const TraceShapeOptions(
                        innerPaintColor: Colors.cyan,
                      ),
                    ),
                  ]),
                  // Page 5: ఐ (ai), ఒ (o), and ఓ (oo)
                  TraceCharsModel(chars: [
                    TraceCharModel(
                      char: 'ఐ', // Telugu vowel "ai"
                      traceShapeOptions: const TraceShapeOptions(
                        innerPaintColor: Colors.indigo,
                      ),
                    ),
                    TraceCharModel(
                      char: 'ఒ', // Telugu vowel "o"
                      traceShapeOptions: const TraceShapeOptions(
                        innerPaintColor: Colors.brown,
                      ),
                    ),
                  ]),
                    TraceCharsModel(chars: [TraceCharModel(
                      char: 'ఓ', // Telugu vowel "oo"
                      traceShapeOptions: const TraceShapeOptions(
                        innerPaintColor: Colors.amber,
                      ),
                    ),
                  ]),
                  // Page 6: ఔ (au), ఋ (ru), and ౠ (ruu)
                  TraceCharsModel(chars: [
                    TraceCharModel(
                      char: 'ఔ', // Telugu vowel "au"
                      traceShapeOptions: const TraceShapeOptions(
                        innerPaintColor: Colors.deepOrange,
                      ),
                    ),
                    TraceCharModel(
                      char: 'ఋ', // Telugu vowel "ru"
                      traceShapeOptions: const TraceShapeOptions(
                        innerPaintColor: Colors.lime,
                      ),
                    ),
                    
                  ]),
                  // Page 7: అం (am) and అః (aha)
                  TraceCharsModel(chars: [
                    TraceCharModel(
                      char: 'అం', // Telugu combination "am"
                      traceShapeOptions: const TraceShapeOptions(
                        innerPaintColor: Colors.blueGrey,
                      ),
                    ),
                    TraceCharModel(
                      char: 'అః', // Telugu combination "aha"
                      traceShapeOptions: const TraceShapeOptions(
                        innerPaintColor: Colors.grey,
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
            /*Expanded(
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
            ),*/
            // Removed TracingWordGame with 'Hi' (H and I letters)
          ],
        ),
      ),
    );
  }
}
