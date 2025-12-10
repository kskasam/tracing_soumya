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
                  /*TraceCharsModel(chars: [
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
                  ]),*/
                  // Each letter gets its own screen, starting from ఔ
                  TraceCharsModel(chars: [
                    TraceCharModel(
                      char: 'ఔ', // Telugu vowel "au"
                      traceShapeOptions: const TraceShapeOptions(
                        innerPaintColor: Colors.deepOrange,
                      ),
                    ),
                  ]),
                  TraceCharsModel(chars: [
                    TraceCharModel(
                      char: 'ఋ', // Telugu vowel "ru"
                      traceShapeOptions: const TraceShapeOptions(
                        innerPaintColor: Colors.lime,
                      ),
                    ),
                  ]),
                  TraceCharsModel(chars: [
                    TraceCharModel(
                      char: 'అం', // Telugu combination "am"
                      traceShapeOptions: const TraceShapeOptions(
                        innerPaintColor: Colors.blueGrey,
                      ),
                    ),
                  ]),
                  TraceCharsModel(chars: [
                    TraceCharModel(
                      char: 'అః', // Telugu combination "aha"
                      traceShapeOptions: const TraceShapeOptions(
                        innerPaintColor: Colors.grey,
                      ),
                    ),
                  ]),
                  TraceCharsModel(chars: [
                    TraceCharModel(
                      char: 'క', // Telugu consonant "ka"
                      traceShapeOptions: const TraceShapeOptions(
                        innerPaintColor: Colors.orange,
                      ),
                    ),
                  ]),
                  TraceCharsModel(chars: [
                    TraceCharModel(
                      char: 'ఖ', // Telugu consonant "kha"
                      traceShapeOptions: const TraceShapeOptions(
                        innerPaintColor: Colors.blue,
                      ),
                    ),
                  ]),
                  TraceCharsModel(chars: [
                    TraceCharModel(
                      char: 'గ', // Telugu consonant "ga"
                      traceShapeOptions: const TraceShapeOptions(
                        innerPaintColor: Colors.green,
                      ),
                    ),
                  ]),
                  TraceCharsModel(chars: [
                    TraceCharModel(
                      char: 'ఘ', // Telugu consonant "gha"
                      traceShapeOptions: const TraceShapeOptions(
                        innerPaintColor: Colors.purple,
                      ),
                    ),
                  ]),
                  TraceCharsModel(chars: [
                    TraceCharModel(
                      char: 'చ', // Telugu consonant "cha"
                      traceShapeOptions: const TraceShapeOptions(
                        innerPaintColor: Colors.red,
                      ),
                    ),
                  ]),
                  TraceCharsModel(chars: [
                    TraceCharModel(
                      char: 'ఛ', // Telugu consonant "chha"
                      traceShapeOptions: const TraceShapeOptions(
                        innerPaintColor: Colors.pink,
                      ),
                    ),
                  ]),
                  TraceCharsModel(chars: [
                    TraceCharModel(
                      char: 'జ', // Telugu consonant "ja"
                      traceShapeOptions: const TraceShapeOptions(
                        innerPaintColor: Colors.teal,
                      ),
                    ),
                  ]),
                  TraceCharsModel(chars: [
                    TraceCharModel(
                      char: 'ఝ', // Telugu consonant "jha"
                      traceShapeOptions: const TraceShapeOptions(
                        innerPaintColor: Colors.cyan,
                      ),
                    ),
                  ]),
                  TraceCharsModel(chars: [
                    TraceCharModel(
                      char: 'ట', // Telugu consonant "ta"
                      traceShapeOptions: const TraceShapeOptions(
                        innerPaintColor: Colors.indigo,
                      ),
                    ),
                  ]),
                  TraceCharsModel(chars: [
                    TraceCharModel(
                      char: 'ఠ', // Telugu consonant "tha"
                      traceShapeOptions: const TraceShapeOptions(
                        innerPaintColor: Colors.brown,
                      ),
                    ),
                  ]),
                  TraceCharsModel(chars: [
                    TraceCharModel(
                      char: 'డ', // Telugu consonant "da"
                      traceShapeOptions: const TraceShapeOptions(
                        innerPaintColor: Colors.amber,
                      ),
                    ),
                  ]),
                  TraceCharsModel(chars: [
                    TraceCharModel(
                      char: 'ఢ', // Telugu consonant "dha"
                      traceShapeOptions: const TraceShapeOptions(
                        innerPaintColor: Colors.deepOrange,
                      ),
                    ),
                  ]),
                  TraceCharsModel(chars: [
                    TraceCharModel(
                      char: 'ణ', // Telugu consonant "na"
                      traceShapeOptions: const TraceShapeOptions(
                        innerPaintColor: Colors.lime,
                      ),
                    ),
                  ]),
                  TraceCharsModel(chars: [
                    TraceCharModel(
                      char: 'త', // Telugu consonant "ta2"
                      traceShapeOptions: const TraceShapeOptions(
                        innerPaintColor: Colors.blueGrey,
                      ),
                    ),
                  ]),
                  TraceCharsModel(chars: [
                    TraceCharModel(
                      char: 'థ', // Telugu consonant "tha2"
                      traceShapeOptions: const TraceShapeOptions(
                        innerPaintColor: Colors.grey,
                      ),
                    ),
                  ]),
                  TraceCharsModel(chars: [
                    TraceCharModel(
                      char: 'ద', // Telugu consonant "da2"
                      traceShapeOptions: const TraceShapeOptions(
                        innerPaintColor: Colors.orange,
                      ),
                    ),
                  ]),
                  TraceCharsModel(chars: [
                    TraceCharModel(
                      char: 'ధ', // Telugu consonant "dha2"
                      traceShapeOptions: const TraceShapeOptions(
                        innerPaintColor: Colors.blue,
                      ),
                    ),
                  ]),
                  TraceCharsModel(chars: [
                    TraceCharModel(
                      char: 'న', // Telugu consonant "na2"
                      traceShapeOptions: const TraceShapeOptions(
                        innerPaintColor: Colors.green,
                      ),
                    ),
                  ]),
                  TraceCharsModel(chars: [
                    TraceCharModel(
                      char: 'ప', // Telugu consonant "pa"
                      traceShapeOptions: const TraceShapeOptions(
                        innerPaintColor: Colors.purple,
                      ),
                    ),
                  ]),
                  TraceCharsModel(chars: [
                    TraceCharModel(
                      char: 'ఫ', // Telugu consonant "pha"
                      traceShapeOptions: const TraceShapeOptions(
                        innerPaintColor: Colors.red,
                      ),
                    ),
                  ]),
                  TraceCharsModel(chars: [
                    TraceCharModel(
                      char: 'బ', // Telugu consonant "ba"
                      traceShapeOptions: const TraceShapeOptions(
                        innerPaintColor: Colors.pink,
                      ),
                    ),
                  ]),
                  TraceCharsModel(chars: [
                    TraceCharModel(
                      char: 'భ', // Telugu consonant "bha"
                      traceShapeOptions: const TraceShapeOptions(
                        innerPaintColor: Colors.teal,
                      ),
                    ),
                  ]),
                  TraceCharsModel(chars: [
                    TraceCharModel(
                      char: 'మ', // Telugu consonant "ma"
                      traceShapeOptions: const TraceShapeOptions(
                        innerPaintColor: Colors.cyan,
                      ),
                    ),
                  ]),
                  TraceCharsModel(chars: [
                    TraceCharModel(
                      char: 'య', // Telugu consonant "ya"
                      traceShapeOptions: const TraceShapeOptions(
                        innerPaintColor: Colors.indigo,
                      ),
                    ),
                  ]),
                  TraceCharsModel(chars: [
                    TraceCharModel(
                      char: 'ర', // Telugu consonant "ra"
                      traceShapeOptions: const TraceShapeOptions(
                        innerPaintColor: Colors.brown,
                      ),
                    ),
                  ]),
                  TraceCharsModel(chars: [
                    TraceCharModel(
                      char: 'ల', // Telugu consonant "la"
                      traceShapeOptions: const TraceShapeOptions(
                        innerPaintColor: Colors.amber,
                      ),
                    ),
                  ]),
                  TraceCharsModel(chars: [
                    TraceCharModel(
                      char: 'ళ', // Telugu consonant "lla"
                      traceShapeOptions: const TraceShapeOptions(
                        innerPaintColor: Colors.deepOrange,
                      ),
                    ),
                  ]),
                  TraceCharsModel(chars: [
                    TraceCharModel(
                      char: 'వ', // Telugu consonant "va"
                      traceShapeOptions: const TraceShapeOptions(
                        innerPaintColor: Colors.lime,
                      ),
                    ),
                  ]),
                  TraceCharsModel(chars: [
                    TraceCharModel(
                      char: 'శ', // Telugu consonant "sha"
                      traceShapeOptions: const TraceShapeOptions(
                        innerPaintColor: Colors.blueGrey,
                      ),
                    ),
                  ]),
                  TraceCharsModel(chars: [
                    TraceCharModel(
                      char: 'ష', // Telugu consonant "ssa"
                      traceShapeOptions: const TraceShapeOptions(
                        innerPaintColor: Colors.grey,
                      ),
                    ),
                  ]),
                  TraceCharsModel(chars: [
                    TraceCharModel(
                      char: 'స', // Telugu consonant "sa"
                      traceShapeOptions: const TraceShapeOptions(
                        innerPaintColor: Colors.orange,
                      ),
                    ),
                  ]),
                  TraceCharsModel(chars: [
                    TraceCharModel(
                      char: 'హ', // Telugu consonant "ha"
                      traceShapeOptions: const TraceShapeOptions(
                        innerPaintColor: Colors.blue,
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
