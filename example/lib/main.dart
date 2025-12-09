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
                  // Page 8: క (ka), ఖ (kha), గ (ga), ఘ (gha)
                  TraceCharsModel(chars: [
                    TraceCharModel(
                      char: 'క', // Telugu consonant "ka"
                      traceShapeOptions: const TraceShapeOptions(
                        innerPaintColor: Colors.orange,
                      ),
                    ),
                    TraceCharModel(
                      char: 'ఖ', // Telugu consonant "kha"
                      traceShapeOptions: const TraceShapeOptions(
                        innerPaintColor: Colors.blue,
                      ),
                    ),
                    TraceCharModel(
                      char: 'గ', // Telugu consonant "ga"
                      traceShapeOptions: const TraceShapeOptions(
                        innerPaintColor: Colors.green,
                      ),
                    ),
                    TraceCharModel(
                      char: 'ఘ', // Telugu consonant "gha"
                      traceShapeOptions: const TraceShapeOptions(
                        innerPaintColor: Colors.purple,
                      ),
                    ),
                  ]),
                  // Page 9: చ (cha), ఛ (chha), జ (ja), ఝ (jha)
                  TraceCharsModel(chars: [
                    TraceCharModel(
                      char: 'చ', // Telugu consonant "cha"
                      traceShapeOptions: const TraceShapeOptions(
                        innerPaintColor: Colors.red,
                      ),
                    ),
                    TraceCharModel(
                      char: 'ఛ', // Telugu consonant "chha"
                      traceShapeOptions: const TraceShapeOptions(
                        innerPaintColor: Colors.pink,
                      ),
                    ),
                    TraceCharModel(
                      char: 'జ', // Telugu consonant "ja"
                      traceShapeOptions: const TraceShapeOptions(
                        innerPaintColor: Colors.teal,
                      ),
                    ),
                    TraceCharModel(
                      char: 'ఝ', // Telugu consonant "jha"
                      traceShapeOptions: const TraceShapeOptions(
                        innerPaintColor: Colors.cyan,
                      ),
                    ),
                  ]),
                  // Page 10: ట (ta), ఠ (tha), డ (da), ఢ (dha), ణ (na)
                  TraceCharsModel(chars: [
                    TraceCharModel(
                      char: 'ట', // Telugu consonant "ta"
                      traceShapeOptions: const TraceShapeOptions(
                        innerPaintColor: Colors.indigo,
                      ),
                    ),
                    TraceCharModel(
                      char: 'ఠ', // Telugu consonant "tha"
                      traceShapeOptions: const TraceShapeOptions(
                        innerPaintColor: Colors.brown,
                      ),
                    ),
                    TraceCharModel(
                      char: 'డ', // Telugu consonant "da"
                      traceShapeOptions: const TraceShapeOptions(
                        innerPaintColor: Colors.amber,
                      ),
                    ),
                    TraceCharModel(
                      char: 'ఢ', // Telugu consonant "dha"
                      traceShapeOptions: const TraceShapeOptions(
                        innerPaintColor: Colors.deepOrange,
                      ),
                    ),
                    TraceCharModel(
                      char: 'ణ', // Telugu consonant "na"
                      traceShapeOptions: const TraceShapeOptions(
                        innerPaintColor: Colors.lime,
                      ),
                    ),
                  ]),
                  // Page 11: త (ta2), థ (tha2), ద (da2), ధ (dha2), న (na2)
                  TraceCharsModel(chars: [
                    TraceCharModel(
                      char: 'త', // Telugu consonant "ta2"
                      traceShapeOptions: const TraceShapeOptions(
                        innerPaintColor: Colors.blueGrey,
                      ),
                    ),
                    TraceCharModel(
                      char: 'థ', // Telugu consonant "tha2"
                      traceShapeOptions: const TraceShapeOptions(
                        innerPaintColor: Colors.grey,
                      ),
                    ),
                    TraceCharModel(
                      char: 'ద', // Telugu consonant "da2"
                      traceShapeOptions: const TraceShapeOptions(
                        innerPaintColor: Colors.orange,
                      ),
                    ),
                    TraceCharModel(
                      char: 'ధ', // Telugu consonant "dha2"
                      traceShapeOptions: const TraceShapeOptions(
                        innerPaintColor: Colors.blue,
                      ),
                    ),
                    TraceCharModel(
                      char: 'న', // Telugu consonant "na2"
                      traceShapeOptions: const TraceShapeOptions(
                        innerPaintColor: Colors.green,
                      ),
                    ),
                  ]),
                  // Page 12: ప (pa), ఫ (pha), బ (ba), భ (bha), మ (ma)
                  TraceCharsModel(chars: [
                    TraceCharModel(
                      char: 'ప', // Telugu consonant "pa"
                      traceShapeOptions: const TraceShapeOptions(
                        innerPaintColor: Colors.purple,
                      ),
                    ),
                    TraceCharModel(
                      char: 'ఫ', // Telugu consonant "pha"
                      traceShapeOptions: const TraceShapeOptions(
                        innerPaintColor: Colors.red,
                      ),
                    ),
                    TraceCharModel(
                      char: 'బ', // Telugu consonant "ba"
                      traceShapeOptions: const TraceShapeOptions(
                        innerPaintColor: Colors.pink,
                      ),
                    ),
                    TraceCharModel(
                      char: 'భ', // Telugu consonant "bha"
                      traceShapeOptions: const TraceShapeOptions(
                        innerPaintColor: Colors.teal,
                      ),
                    ),
                    TraceCharModel(
                      char: 'మ', // Telugu consonant "ma"
                      traceShapeOptions: const TraceShapeOptions(
                        innerPaintColor: Colors.cyan,
                      ),
                    ),
                  ]),
                  // Page 13: య (ya), ర (ra), ల (la), ళ (lla), వ (va)
                  TraceCharsModel(chars: [
                    TraceCharModel(
                      char: 'య', // Telugu consonant "ya"
                      traceShapeOptions: const TraceShapeOptions(
                        innerPaintColor: Colors.indigo,
                      ),
                    ),
                    TraceCharModel(
                      char: 'ర', // Telugu consonant "ra"
                      traceShapeOptions: const TraceShapeOptions(
                        innerPaintColor: Colors.brown,
                      ),
                    ),
                    TraceCharModel(
                      char: 'ల', // Telugu consonant "la"
                      traceShapeOptions: const TraceShapeOptions(
                        innerPaintColor: Colors.amber,
                      ),
                    ),
                    TraceCharModel(
                      char: 'ళ', // Telugu consonant "lla"
                      traceShapeOptions: const TraceShapeOptions(
                        innerPaintColor: Colors.deepOrange,
                      ),
                    ),
                    TraceCharModel(
                      char: 'వ', // Telugu consonant "va"
                      traceShapeOptions: const TraceShapeOptions(
                        innerPaintColor: Colors.lime,
                      ),
                    ),
                  ]),
                  // Page 14: శ (sha), ష (ssa), స (sa), హ (ha)
                  TraceCharsModel(chars: [
                    TraceCharModel(
                      char: 'శ', // Telugu consonant "sha"
                      traceShapeOptions: const TraceShapeOptions(
                        innerPaintColor: Colors.blueGrey,
                      ),
                    ),
                    TraceCharModel(
                      char: 'ష', // Telugu consonant "ssa"
                      traceShapeOptions: const TraceShapeOptions(
                        innerPaintColor: Colors.grey,
                      ),
                    ),
                    TraceCharModel(
                      char: 'స', // Telugu consonant "sa"
                      traceShapeOptions: const TraceShapeOptions(
                        innerPaintColor: Colors.orange,
                      ),
                    ),
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
