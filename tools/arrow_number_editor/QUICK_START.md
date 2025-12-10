# Quick Start: Using Your JSON File

## Step 1: Process Your JSON

After exporting from the HTML editor, process it:

```bash
cd tools/arrow_number_editor
python process_arrow_numbers.py arrow_number_placement.json ../svg_generator/output/ka_extracted.svg ka_arrow_numbers.json ka_arrow_numbers.dart ka
```

This creates `ka_arrow_numbers.json` - **this is the file you'll use in the app**.

## Step 2: Place the JSON File

Copy `ka_arrow_numbers.json` to:

```
lib/assets/arrow_number_positions/ka_arrow_numbers.json
```

**Important:** Create the `arrow_number_positions` folder if it doesn't exist.

## Step 3: Update pubspec.yaml

Add the folder to assets (if not already there):

```yaml
flutter:
  assets:
    - lib/assets/arrow_number_positions/
```

## Step 4: The App Will Use It Automatically

Once the integration is complete, the app will:
- ✅ Automatically load custom positions if JSON exists
- ✅ Fall back to auto-calculated positions if JSON is missing
- ✅ Show your custom arrows and numbers exactly as you placed them

## Current Status

**Integration in progress.** The model and painter updates are being added. Once complete, your JSON files will work automatically!

## File Structure

```
lib/assets/
  └── arrow_number_positions/
      ├── ka_arrow_numbers.json
      ├── ja_arrow_numbers.json
      └── ... (other letters)
```

