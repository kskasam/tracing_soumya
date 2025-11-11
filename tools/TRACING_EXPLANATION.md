# How the Tracing Tool Captures Points and Strokes

## Overview
When you trace a letter in the interactive tool, here's exactly what happens step-by-step:

## Step-by-Step Process

### 1. **Loading the SVG Path**
```
SVG Path (e.g., "M 100 200 L 300 400 Q 500 600 700 800...")
    ↓
Tool creates an SVG <path> element
    ↓
Tool calculates the bounding box (min/max X and Y coordinates)
```

### 2. **Starting a Stroke**
When you click "Start New Stroke":
- `isTracing = true` (enables point capture)
- `currentStroke = []` (creates empty array for this stroke)
- The tool is now ready to record your clicks

### 3. **Clicking on the Path (Point Capture)**

When you click anywhere on the SVG path:

#### A. **Convert Click to SVG Coordinates**
```javascript
// Your mouse click position (screen pixels)
event.clientX, event.clientY
    ↓
// Convert to SVG coordinate system
svgPoint = convertScreenToSVG(mouseX, mouseY)
```

#### B. **Find Closest Point on Path**
The tool doesn't just use your exact click - it finds the **nearest point on the actual path**:

```javascript
// Sample points along the entire path
for (every 1 pixel along path length) {
    pathPoint = getPointAtLength(i)
    distance = calculateDistance(svgPoint, pathPoint)
    if (distance < minDistance) {
        closestPoint = pathPoint  // This is the point we'll use!
    }
}
}
```

**Why?** This ensures points are always ON the path, even if you click slightly off.

#### C. **Normalize Coordinates (0 to 1)**
The tool converts absolute SVG coordinates to normalized (0-1) values:

```javascript
// Get bounding box of the path
bbox = {
    x: 100,      // minimum X
    y: 200,      // minimum Y
    width: 600,  // width of path
    height: 800  // height of path
}

// Normalize to 0-1 range
normalizedX = (point.x - bbox.x) / bbox.width
normalizedY = (point.y - bbox.y) / bbox.height

// Example:
// If point is at (400, 600) and bbox is (100, 200) with size (600, 800):
// normalizedX = (400 - 100) / 600 = 0.5
// normalizedY = (600 - 200) / 800 = 0.5
```

**Why normalize?** 
- Makes coordinates independent of actual size
- Flutter app can scale to any size
- Matches the format used in existing JSON files

#### D. **Store the Point**
```javascript
pointData = {
    x: 0.5,              // normalized X (0-1)
    y: 0.5,              // normalized Y (0-1)
    originalX: 400,      // actual SVG X (for display)
    originalY: 600        // actual SVG Y (for display)
}

currentStroke.push(pointData)  // Add to current stroke array
```

### 4. **Visual Feedback**
- **Red circle** appears at the clicked point
- **Number label** shows the point index (0, 1, 2, ...)
- **Blue line** connects points in the order you clicked

### 5. **Finishing a Stroke**
When you click "Finish Current Stroke":
```javascript
allStrokes.push([...currentStroke])  // Save current stroke
currentStroke = []                    // Clear for next stroke
isTracing = false                     // Disable point capture
```

### 6. **Generating JSON**
When you click "Generate JSON":

```javascript
strokes = allStrokes.map(stroke => ({
    points: stroke.map(pt => `${pt.x.toFixed(4)},${pt.y.toFixed(4)}`)
}))

json = {
    strokes: [
        {
            points: ["0.1234,0.5678", "0.2345,0.6789", ...]
        },
        {
            points: ["0.3456,0.7890", ...]
        }
    ]
}
```

## Example Flow

Let's say you're tracing the letter "అ" (Telugu 'a'):

1. **Load SVG**: Path displays on screen
2. **Start Stroke 1**: Click "Start New Stroke"
3. **Click points**: 
   - Click at top-left → Point 0: (0.25, 0.14)
   - Click at top-right → Point 1: (0.31, 0.17)
   - Click at middle → Point 2: (0.33, 0.26)
   - ... (continue clicking along the path)
4. **Finish Stroke 1**: Click "Finish Current Stroke"
   - Stroke 1 saved with 9 points
5. **Start Stroke 2**: Click "Start New Stroke"
6. **Click more points**: Continue tracing...
7. **Finish Stroke 2**: Click "Finish Current Stroke"
8. **Generate JSON**: Click "Generate JSON"
   - Output:
   ```json
   {
     "strokes": [
       {
         "points": ["0.2524,0.1387", "0.3100,0.1689", ...]
       },
       {
         "points": ["0.7517,0.0000", "0.5734,0.1309", ...]
       }
     ]
   }
   ```

## Key Points

1. **Order Matters**: Points are stored in the **exact order you click**
2. **Normalized Coordinates**: All coordinates are 0-1 (not pixel values)
3. **Path Snapping**: Your clicks snap to the nearest point on the path
4. **Stroke Separation**: Each "Finish Stroke" creates a new stroke in the JSON
5. **Visual Feedback**: You see numbered points and connecting lines as you trace

## Why This Works for Flutter

The Flutter app expects:
- Normalized coordinates (0-1)
- Multiple strokes (array of stroke objects)
- Points as strings in "x,y" format

This is exactly what the tool generates! The Flutter app can then:
- Scale the 0-1 coordinates to any screen size
- Draw each stroke separately
- Show direction indicators based on point order

