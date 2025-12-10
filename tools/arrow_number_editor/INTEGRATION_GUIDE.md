# Arrow & Number Positions Integration Guide

## Quick Start

After generating a JSON file from the HTML editor, follow these steps:

### Step 1: Place Your JSON File

Place your JSON file in the assets directory. For Telugu letters, use:
```
lib/assets/phontics_assets_points/telugu_phontics/
```

**Example:** If you created positions for the letter 'క' (ka), name it:
```
ka_custom_positions.json
```

### Step 2: Add to pubspec.yaml

Add the file path to `pubspec.yaml` in the `assets` section:

```yaml
assets:
  # ... existing assets ...
  - packages/tracing_game/assets/phontics_assets_points/telugu_phontics/ka_custom_positions.json
```

### Step 3: Add Path to TraceModel

Update the letter configuration in `lib/src/get_shape_helper/enum_of_arabic_and_numbers_letters.dart`.

Find your letter's case statement (e.g., `case 'క':`) and add `customPositionsJsonFile`:

```dart
case 'క': // ka
  list.add(_createTeluguTraceModel(
    sizeOfLetter: sizeOfLetter,
    bigPath: TeluguShapePaths.kaBig,
    smallPath: TeluguShapePaths.kaSmall,
    dottedPath: TeluguShapePaths.kaDotted,
    bigJsonFile: ShapePointsManger.teluguKaBig,
    smallJsonFile: ShapePointsManger.teluguKaSmall,
    isBig: true,
    customPositionsJsonFile: 'lib/assets/phontics_assets_points/telugu_phontics/ka_custom_positions.json', // Add this line
  ));
  break;
```

### Step 4: Update Helper Function (if needed)

If `_createTeluguTraceModel` doesn't accept `customPositionsJsonFile` yet, add it:

```dart
TraceModel _createTeluguTraceModel({
  required Size sizeOfLetter,
  required String bigPath,
  required String smallPath,
  required String dottedPath,
  required String bigJsonFile,
  required String smallJsonFile,
  bool isBig = true,
  String? customPositionsJsonFile, // Add this parameter
}) {
  return TraceModel(
    // ... existing parameters ...
    customPositionsJsonFile: customPositionsJsonFile, // Add this
  );
}
```

### Step 5: Test

1. Run `flutter pub get` to ensure assets are registered
2. Run your app
3. Navigate to the letter you configured
4. You should see your custom arrow and number positions!

## JSON Format Support

The parser supports **both formats**:

1. **Raw HTML Editor Format** (direct export):
   - Has `items` array with arrow/number/line objects
   - Automatically normalizes coordinates using `svgViewBox`

2. **Processed Format** (from Python script):
   - Has `arrows` and `numbers` keys
   - Already normalized

You can use either format - the parser will detect and handle both automatically.

## Troubleshooting

- **File not found**: Check that the path in `pubspec.yaml` matches the actual file location
- **Positions not showing**: Verify the JSON structure is valid and contains `items` or `arrows`/`numbers` keys
- **Wrong positions**: Check that the `svgViewBox` in your JSON matches the SVG you used in the editor

## Example JSON Structure

### Raw HTML Editor Format:
```json
{
  "svgViewBox": "0 0 200 200",
  "svgPath": "M 10 10 L 100 100 ...",
  "centerlinePath": "M 10 10 L 100 100 ...",
  "items": [
    {
      "type": "arrow",
      "x": 50,
      "y": 50,
      "angle": 0.5,
      "arrowType": "triangle"
    },
    {
      "type": "number",
      "x": 60,
      "y": 60,
      "strokeNumber": 1
    }
  ]
}
```

### Processed Format:
```json
{
  "arrows": [
    {
      "x": 50,
      "y": 50,
      "normalized_x": 0.25,
      "normalized_y": 0.25,
      "angle": 0.5,
      "arrowType": "triangle"
    }
  ],
  "numbers": {
    "1": [
      {
        "x": 60,
        "y": 60,
        "normalized_x": 0.30,
        "normalized_y": 0.30,
        "strokeNumber": 1
      }
    ]
  }
}
```
