// Run this in DartPad or as a Flutter test to see coordinate mapping
// This will help diagnose the Telugu coordinate mismatch

import 'dart:convert';
import 'package:flutter/material.dart';

void main() {
  // Simulate Telugu 'అ' coordinates
  final viewSize = Size(200, 200);
  
  // First point from a_big_PointsInfo.json
  final firstJsonPoint = "0.2378,0.5174";
  
  // Parse and convert to screen coordinates (same as _loadPointsFromJson does)
  final coords = firstJsonPoint.split(',').map((e) => double.parse(e)).toList();
  final screenPoint = Offset(
    coords[0] * viewSize.width,  // 0.2378 * 200 = 47.56
    coords[1] * viewSize.height, // 0.5174 * 200 = 103.48
  );
  
  print('JSON normalized: (${coords[0]}, ${coords[1]})');
  print('Screen coordinates: (${screenPoint.dx}, ${screenPoint.dy})');
  print('');
  print('Expected anchor (hand icon) at: $screenPoint');
  print('');
  print('If you need to click elsewhere, there is a coordinate mismatch.');
  print('');
  print('To fix: Adjust positionDottedPath or regenerate JSON with correct normalization');
}

