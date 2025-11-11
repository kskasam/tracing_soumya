# Flutter Tracing Game - Architecture Overview

This document explains how the tracing game app works, from startup to user interaction. This was generated from a Copilot Chat discussion to help understand the codebase.

## Very Short Summary
This is a Flutter package with an example app that demonstrates character, shape, and word tracing. The example's `main()` calls `runApp`, which builds a UI containing three tracing widgets. Each tracing widget creates a TracingCubit that loads SVG and JSON stroke data, displays shapes, and responds to touch events for tracing along predefined points.

## Major Pieces and Locations
- Example app entrypoint
  - `example/lib/main.dart` — the sample app you can run. It calls `runApp(const MyApp())`.
- Public package exporter
  - `lib/tracing_game.dart` — re-exports the important classes so apps can import `package:tracing_game/tracing_game.dart`.
- Tracing UI
  - `lib/src/tracing/page/tracing_chars_game.dart` — the widget that shows letters and responds to touches.
- Tracing logic (state + asset loading)
  - `lib/src/tracing/manager/tracing_cubit.dart` — the "brain": loads assets, manages progress, and handles touch events.
- Assets (stroke JSONs and SVGs)
  - Under `lib/assets/...` (and referenced via `packages/tracing_game/...` when loaded).

## Step-by-Step Walk-through

### 1) App Start (Entrypoint)
- The example app's `main()` is in `example/lib/main.dart`.
- main() calls runApp(const MyApp()).
- `MyApp` returns a `MaterialApp` containing a `Scaffold` whose body is a `Column` of three expanded tracing widgets:
  - `TracingCharsGame` (characters),
  - `TracingGeometricShapesGame` (shapes),
  - `TracingWordGame` (words).
- These widgets are the UI the user sees and interacts with.

Why that matters: runApp sets up the visual app. Everything else (loading tracing data, responding to touches) happens inside those tracing widgets.

### 2) The Tracing Widget (example: `TracingCharsGame`)
- `TracingCharsGame` is a StatefulWidget (it stores local state and creates an object to manage tracing).
- In `initState()` the widget creates a `TracingCubit`:
  - `tracingCubit = TracingCubit(stateOfTracing: StateOfTracing.chars, traceShapeModel: widget.traceShapeModel);`
- The widget uses `BlocProvider` and `BlocConsumer` to connect UI to the cubit's state:
  - BlocProvider makes the cubit available to widgets below.
  - BlocConsumer watches the cubit's state and rebuilds UI or calls listeners when state changes.
- The UI shows one or more letter areas (one per letter/model). For the active letter:
  - It draws the letter using a `CustomPaint` (with `PhoneticsPainter`).
  - It wraps the drawing area in a `GestureDetector` that listens for touch gestures (pan start and pan update).

Simple analogy: the widget is the stage; the cubit is the stage manager; the painter paints things on the stage; the GestureDetector listens for the user's finger.

### 3) What the TracingCubit Does (Core Responsibilities)
- Holds the app state (how many screens, which letter is active, drawing progress).
- On creation it calls `updateTheTraceLetter()` which:
  - Converts the public input models (characters/shapes/words) into internal tracing items.
  - Calls `loadAssets()` to prepare drawing data.
- loadAssets():
  - For each letter/shape it:
    - Parses SVG path strings (using `svg_path_parser`) to get drawable Path objects.
    - Applies transforms to scale/center the path into a fixed view size (the code uses `viewSize = Size(200, 200)`).
    - Loads stroke-point sequences from JSON files via `rootBundle.loadString('packages/tracing_game/$path')`.
      - JSON contains strokes: each stroke is a list of points given as "x,y" where x and y are normalized (0..1).
      - The cubit multiplies those normalized numbers by the `viewSize` to get actual pixel coordinates (Offsets).
    - Constructs `LetterPathsModel` entries with:
      - the transformed letter Path,
      - arrays of stroke points (a list of lists of Offsets),
      - index/dotted paths for hint drawing,
      - colors, stroke width, and an anchor position.
  - After all items are prepared it emits state with `DrawingStates.loaded`.

Why this matters: the cubit precomputes everything the painter needs — shapes and the exact trace points the user should follow.

### 4) How Drawing / Gestures Work (Touch -> Cubit -> Painter)
- GestureDetector on each letter area calls:
  - `onPanStart(details.localPosition)` → `tracingCubit.handlePanStart(position)`
  - `onPanUpdate(details.localPosition)` → `tracingCubit.handlePanUpdate(position)`
- handlePanStart(position):
  - Checks if the position is an allowed start point using `isTracingStartPoint(position)`:
    - If the stroke is only a single point, it usually accepts any start.
    - Otherwise it looks for being near the "anchor" point (the expected start), in a small rectangle.
  - If the start is valid, it sets state to `DrawingStates.tracing` and prepares a new `Path` for the current stroke (a Path.moveTo to the anchor point).
  - For single-point strokes it may directly complete the stroke.
- handlePanUpdate(position):
  - Finds the next expected point in the current stroke's point array.
  - If the user's finger is close enough to that expected point (within a distance threshold, default ~30 px), the cubit:
    - appends that expected point to the current drawing Path,
    - advances the current stroke progress counter,
    - emits a new state to cause a redraw.
  - When the user reaches the end of the stroke (progress >= stroke length) it calls `completeStroke()`.
- completeStroke():
  - Saves the finished stroke (adds it to `paths`).
  - Moves to the next stroke for the same letter or marks the letter finished.
  - If the entire letter and then the screen are done, it emits either `finishedCurrentScreen` or `gameFinished`.
- The widget's `BlocConsumer` listens for those state changes and can call user-supplied callbacks like `onTracingUpdated`, `onCurrentTracingScreenFinished`, and `onGameFinished`.

Simple description: the code checks if you're near the next correct point. If you are, it "accepts" that step and draws it; if you finish all steps it moves to the next part.

### 5) How the Painter Shows Progress
- A `CustomPaint` uses `PhoneticsPainter` that receives:
  - the base letter Path (the static outline),
  - dotted/index paths (hint visuals),
  - the currentDrawingPath (what the user has drawn so far),
  - `strokePoints` and `pathPoints` (for painting dots or other hints),
  - colors and stroke width.
- When the cubit emits new state (e.g., a new `currentDrawingPath`), Flutter rebuilds and the painter redraws showing the user's progress along the path.

### 6) Assets and Data Format
- Stroke JSON files are loaded like:
  - `final jsonString = await rootBundle.loadString('packages/tracing_game/$path');`
- The JSON structure (simplified) looks like:
  - { "strokes": [ { "points": ["0.1,0.2","0.11,0.21", ...] }, { "points": [...] } ] }
  - Each point is a string "x,y" with normalized values 0..1. The code multiplies by view width/height.
- SVG path strings are stored in other models and parsed with `parseSvgPath(...)`.

Why normalize: storing 0..1 coordinates lets the code scale shapes to different device sizes safely.

### 7) Where to Look Next (Key Files)
- `example/lib/main.dart` — shows how the library is used and prints callbacks (great starting point).
- `lib/src/tracing/page/tracing_chars_game.dart` — the visual widget + GestureDetector wiring.
- `lib/src/tracing/manager/tracing_cubit.dart` — the business logic: loadAssets(), handlePanStart/Update, completeStroke.
- `lib/src/tracing/phonetics_paint_widget/phonetics_painter.dart` — how drawing happens (what is painted).
- `lib/assets/` — look for JSON and SVG assets (stroke definitions and images).

## How to Run the Example
Open a terminal in the project root and run:

```bash
# fetch Dart/Flutter dependencies
flutter pub get

# run the example app on the current device (simulator or connected phone)
flutter run --target=example/lib/main.dart
```

## Simple Analogies for Beginners
- Flutter app = a tree of widgets (UI building blocks).
- main() + runApp = "turn on the app".
- A StatefulWidget is like a screen that can change (it has an inner object that manages things).
- TracingCubit = the controller that:
  - loads shape data and stroke points,
  - watches for touches,
  - checks if the touch is close to the expected point,
  - tracks progress and tells the painting layer to update.
- Painter = an artist that draws the base shape and the user's traced strokes.

## Next Steps for Learning
1. Open `example/lib/main.dart` and change one letter or color, then re-run to see the effect.
2. Add print statements in `TracingCubit.handlePanUpdate` to see the coordinates the app checks.
3. Read simple Flutter tutorials about:
   - "main, runApp, MaterialApp"
   - "StatelessWidget vs StatefulWidget"
   - "GestureDetector basics"
   - "CustomPaint and CustomPainter"