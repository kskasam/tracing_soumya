// For JSON parsing

import 'dart:math' as math;
import 'package:flutter/material.dart';
import '../models/custom_arrow_number_positions.dart';

class PhoneticsPainter extends CustomPainter {
  final Path letterImage;
  final List<Path> paths; // List of paths for strokes
  final Path currentDrawingPath;
  final List<Offset> pathPoints;
  final Color strokeColor;
  final Size viewSize;
  final List<Offset> strokePoints;
  final double? strokeWidth;
  final Color letterColor;
  final Shader? letterShader;
  final Path? dottedPath;
  final Path? indexPath;
  final Color dottedColor;
  final Color indexColor;

  final double? strokeIndex;
  final PaintingStyle? indexPathPaintStyle;
  final PaintingStyle? dottedPathPaintStyle;
  
  // New: List of colors for each stroke (for debugging)
  final List<Color>? strokeColors;
  
  // New: JSON path visualization (for debugging alignment)
  final List<List<Offset>>? jsonPathPoints;
  final bool showJsonPath;
  
  // Arrow guidance
  final bool showArrows;
  final double arrowSpacing;
  final double arrowStartOffset; // offset from start for the single arrow
  
  // Custom arrow and number positions (from JSON)
  final CustomArrowNumberPositions? customPositions;

  // Debug: SVG bounds for visualization
  final Rect? svgBounds;
  final bool showDebugOverlays;
  
  // Cursor position for drawing the ball
  final Offset? cursorPosition;

  PhoneticsPainter({
    this.strokeIndex,
    this.indexPathPaintStyle,
    this.dottedPathPaintStyle,
    this.dottedPath,
    this.indexPath,
    required this.dottedColor,
    required this.indexColor,
    required this.strokeWidth,
    required this.strokePoints,
    required this.letterImage,
    required this.paths,
    required this.currentDrawingPath,
    required this.pathPoints,
    required this.strokeColor,
    required this.viewSize,
    required this.letterColor,
    this.letterShader,
    this.strokeColors,
    this.jsonPathPoints,
    this.showJsonPath = false,
    this.showArrows = true,
    this.arrowSpacing = 40.0,
    this.arrowStartOffset = 12.0,
    this.customPositions,
    this.svgBounds,
    this.showDebugOverlays = true,
    this.cursorPosition,
  });

  @override
  void paint(Canvas canvas, Size size) {
    // DEBUG OVERLAYS: Draw coordinate spaces and bounds FIRST (behind everything)
    if (showDebugOverlays) {
      // BLUE: ViewSize rectangle - the coordinate space used for transformations
      final viewSizePaint = Paint()
        ..color = Colors.blue.withOpacity(0.3)
        ..style = PaintingStyle.stroke
        ..strokeWidth = 2.0;
      canvas.drawRect(
        Rect.fromLTWH(0, 0, viewSize.width, viewSize.height),
        viewSizePaint,
      );
      
      // GREEN: SVG bounds (original SVG coordinate space)
      if (svgBounds != null) {
        final svgBoundsPaint = Paint()
          ..color = Colors.green.withOpacity(0.5)
          ..style = PaintingStyle.stroke
          ..strokeWidth = 2.5;
        // Draw dashed effect manually
        _drawDashedRect(canvas, svgBounds!, svgBoundsPaint, [8, 4]);
      }
      
      // ORANGE: Actual canvas size (might differ from viewSize due to FittedBox)
      final canvasSizePaint = Paint()
        ..color = Colors.orange.withOpacity(0.4)
        ..style = PaintingStyle.stroke
        ..strokeWidth = 2.0;
      _drawDashedRect(
        canvas,
        Rect.fromLTWH(0, 0, size.width, size.height),
        canvasSizePaint,
        [5, 3],
      );
      
      // PURPLE: JSON bounds (calculate from JSON points)
      if (jsonPathPoints != null && jsonPathPoints!.isNotEmpty) {
        double? minX, minY, maxX, maxY;
        for (var stroke in jsonPathPoints!) {
          for (var point in stroke) {
            minX = minX == null ? point.dx : (minX < point.dx ? minX : point.dx);
            minY = minY == null ? point.dy : (minY < point.dy ? minY : point.dy);
            maxX = maxX == null ? point.dx : (maxX > point.dx ? maxX : point.dx);
            maxY = maxY == null ? point.dy : (maxY > point.dy ? maxY : point.dy);
          }
        }
        if (minX != null && minY != null && maxX != null && maxY != null) {
          final jsonBoundsPaint = Paint()
            ..color = Colors.purple.withOpacity(0.5)
            ..style = PaintingStyle.stroke
            ..strokeWidth = 2.5;
          _drawDashedRect(
            canvas,
            Rect.fromLTRB(minX, minY, maxX, maxY),
            jsonBoundsPaint,
            [10, 5],
          );
        }
      }
      
      // CYAN/TEAL: Centerline (dotted path) bounds
      if (dottedPath != null) {
        try {
          final centerlineBounds = dottedPath!.getBounds();
          final centerlineBoundsPaint = Paint()
            ..color = Colors.cyan.withOpacity(0.5)
            ..style = PaintingStyle.stroke
            ..strokeWidth = 2.5;
          _drawDashedRect(
            canvas,
            centerlineBounds,
            centerlineBoundsPaint,
            [6, 3],
          );
          
          // Draw corner markers for centerline bounds
          final centerlineCornerPaint = Paint()
            ..color = Colors.cyan
            ..style = PaintingStyle.fill;
          canvas.drawCircle(
            Offset(centerlineBounds.left, centerlineBounds.top),
            4,
            centerlineCornerPaint,
          );
          canvas.drawCircle(
            Offset(centerlineBounds.right, centerlineBounds.bottom),
            4,
            centerlineCornerPaint,
          );
        } catch (e) {
          // If path is invalid, skip
        }
      }
      
      // Draw corner markers for (0,0) and viewSize
      final cornerPaint = Paint()
        ..color = Colors.blue
        ..style = PaintingStyle.fill;
      canvas.drawCircle(Offset(0, 0), 5, cornerPaint);
      canvas.drawCircle(Offset(viewSize.width, viewSize.height), 5, cornerPaint);
    }
    
    // Paint for the letter path - use stroke to show only outline, no fill
    final letterPaint = Paint()
      ..color = letterColor
      ..style = PaintingStyle.stroke
      ..strokeWidth = 4.0
      ..strokeCap = StrokeCap.round
      ..strokeJoin = StrokeJoin.round;

    // Apply the shader if provided
    if (letterShader != null) {
      letterPaint.shader = letterShader;
    }

    // Draw the letter path as outline only (no fill) to keep inner areas plain/transparent
    canvas.drawPath(letterImage, letterPaint);
 
    // Draw centerline (dotted path) with enhanced debugging visualization
    if (dottedPath != null) {
      // Draw centerline path with thicker stroke for visibility
      final centerlinePaint = Paint()
        ..color = dottedColor
        ..style = dottedPathPaintStyle ?? PaintingStyle.stroke
        ..strokeWidth = 3.0
        ..strokeCap = StrokeCap.round
        ..strokeJoin = StrokeJoin.round;
      // Draw as dotted/dashed line instead of solid
      // Pattern: [dashLength, gapLength] - increased gap for more spacing
      _drawDashedPath(canvas, dottedPath!, centerlinePaint, [5.0, 8.0]);
      
      // Draw centerline bounds border (CYAN) if debug overlays are enabled
      if (showDebugOverlays) {
        try {
          final centerlineBounds = dottedPath!.getBounds();
          
          // CYAN border around centerline bounds (similar to container border)
          final centerlineBorderPaint = Paint()
            ..color = Colors.cyan
            ..style = PaintingStyle.stroke
            ..strokeWidth = 2.0;
          canvas.drawRect(centerlineBounds, centerlineBorderPaint);
          
          // Show padding/margin visualization for centerline
          // Calculate "padding" - space between centerline bounds and SVG bounds
          if (svgBounds != null) {
            final paddingLeft = centerlineBounds.left - svgBounds!.left;
            final paddingTop = centerlineBounds.top - svgBounds!.top;
            final paddingRight = svgBounds!.right - centerlineBounds.right;
            final paddingBottom = svgBounds!.bottom - centerlineBounds.bottom;
            
            // Draw padding visualization (light cyan fill)
            if (paddingLeft > 0 || paddingTop > 0 || paddingRight > 0 || paddingBottom > 0) {
              final paddingPaint = Paint()
                ..color = Colors.cyan.withOpacity(0.2)
                ..style = PaintingStyle.fill;
              
              // Top padding
              if (paddingTop > 0) {
                canvas.drawRect(
                  Rect.fromLTRB(
                    svgBounds!.left,
                    svgBounds!.top,
                    svgBounds!.right,
                    centerlineBounds.top,
                  ),
                  paddingPaint,
                );
              }
              
              // Bottom padding
              if (paddingBottom > 0) {
                canvas.drawRect(
                  Rect.fromLTRB(
                    svgBounds!.left,
                    centerlineBounds.bottom,
                    svgBounds!.right,
                    svgBounds!.bottom,
                  ),
                  paddingPaint,
                );
              }
              
              // Left padding
              if (paddingLeft > 0) {
                canvas.drawRect(
                  Rect.fromLTRB(
                    svgBounds!.left,
                    centerlineBounds.top,
                    centerlineBounds.left,
                    centerlineBounds.bottom,
                  ),
                  paddingPaint,
                );
              }
              
              // Right padding
              if (paddingRight > 0) {
                canvas.drawRect(
                  Rect.fromLTRB(
                    centerlineBounds.right,
                    centerlineBounds.top,
                    svgBounds!.right,
                    centerlineBounds.bottom,
                  ),
                  paddingPaint,
                );
              }
            }
          }
        } catch (e) {
          // If path is invalid, skip
        }
      }
    }

    if (indexPath != null) {
      final debugPaint = Paint()
        ..color = indexColor
        ..style = indexPathPaintStyle ?? PaintingStyle.stroke
        ..strokeWidth = strokeIndex ?? 2.0;
      canvas.drawPath(indexPath!, debugPaint);
    }
    
    
    // Draw JSON path for debugging alignment (BEFORE clipping)
    if (showJsonPath && jsonPathPoints != null && jsonPathPoints!.isNotEmpty) {
      final jsonPathPaint = Paint()
        ..color = Colors.purple
        ..style = PaintingStyle.stroke
        ..strokeWidth = 3.0
        ..strokeCap = StrokeCap.round
        ..strokeJoin = StrokeJoin.round;
      
      // Draw each stroke from JSON
      for (var stroke in jsonPathPoints!) {
        if (stroke.isEmpty) continue;
        
        final jsonPath = Path();
        jsonPath.moveTo(stroke[0].dx, stroke[0].dy);
        for (int i = 1; i < stroke.length; i++) {
          jsonPath.lineTo(stroke[i].dx, stroke[i].dy);
        }
        canvas.drawPath(jsonPath, jsonPathPaint);
      }
      
      // Also draw points as circles for better visibility
      final pointPaint = Paint()
        ..color = Colors.purple
        ..style = PaintingStyle.fill;
      for (var stroke in jsonPathPoints!) {
        for (var point in stroke) {
          canvas.drawCircle(point, 4.0, pointPaint);
        }
      }
    }
    
    // Clip the canvas to the letter path to prevent drawing outside
    canvas.save();
    canvas.clipPath(letterImage);

    // Draw small arrows along each stroke (clipped to letter)
    if (showArrows) {
      final arrowPaint = Paint()
        ..color = dottedColor
        ..style = PaintingStyle.stroke
        ..strokeWidth = 2.0
        ..strokeJoin = StrokeJoin.round
        ..strokeCap = StrokeCap.round;

      const double arrowSize = 10.0; // slightly larger, outlined

      // Store arrow positions and directions for stroke numbering
      final List<Offset> arrowTipPositions = [];
      final List<Offset> arrowDirections = [];
      final List<int> arrowStrokeIndices = [];

      // Check if we have custom positions
      if (customPositions != null && customPositions!.arrows.isNotEmpty) {
        print('🎯 Drawing ${customPositions!.arrows.length} custom arrows, viewSize: $viewSize');
        // Coordinates are normalized to SVG bounds (0-1), need to apply same transformation as letter
        final letterBounds = letterImage.getBounds();
        print('   Letter bounds: $letterBounds');
        
        // Get original SVG bounds for transformation
        Rect? originalSvgBounds = svgBounds;
        if (originalSvgBounds == null) {
          // Fallback: assume letter bounds represent the transformed SVG
          originalSvgBounds = letterBounds;
        }
        
        for (var customArrow in customPositions!.arrows) {
          // Convert normalized coordinates (0-1 within SVG bounds) to screen coordinates
          // Apply the same transformation as the letter path
          final pos = Offset(
            letterBounds.left + customArrow.normalizedX * letterBounds.width,
            letterBounds.top + customArrow.normalizedY * letterBounds.height,
          );
          print('   Arrow at normalized(${customArrow.normalizedX}, ${customArrow.normalizedY}) -> screen(${pos.dx}, ${pos.dy})');
          
          // Use custom angle if provided, otherwise default to right (0)
          final angle = customArrow.angle ?? 0.0;
          final unit = Offset(math.cos(angle), math.sin(angle));
          final perp = Offset(-unit.dy, unit.dx);

          final baseCenter = pos - unit * arrowSize;
          final left = baseCenter + perp * (arrowSize * 0.5);
          final right = baseCenter - perp * (arrowSize * 0.5);

          final arrowPath = Path()
            ..moveTo(pos.dx, pos.dy)
            ..lineTo(left.dx, left.dy)
            ..lineTo(right.dx, right.dy)
            ..close();
          canvas.drawPath(arrowPath, arrowPaint);

          arrowTipPositions.add(pos);
          arrowDirections.add(unit);
          // For custom arrows, we'll use stroke indices from numbers if available
          arrowStrokeIndices.add(1); // Default, will be updated by numbers
        }
      } else {
        // Fall back to auto-calculated positions
        final List<Path> arrowSources = [];
        arrowSources.addAll(paths);
        if (arrowSources.isEmpty && dottedPath != null) {
          arrowSources.add(dottedPath!);
        }
        // If we have fewer paths than strokes in jsonPathPoints (e.g., after advancing strokes),
        // build temporary paths from the remaining stroke points so arrows remain visible on all strokes.
        if (jsonPathPoints != null) {
          for (int i = arrowSources.length; i < jsonPathPoints!.length; i++) {
            final pts = jsonPathPoints![i];
            if (pts.length < 2) continue;
            final p = Path()..moveTo(pts[0].dx, pts[0].dy);
            for (int k = 1; k < pts.length; k++) {
              p.lineTo(pts[k].dx, pts[k].dy);
            }
            arrowSources.add(p);
          }
        }

        for (int pathIndex = 0; pathIndex < arrowSources.length; pathIndex++) {
          final path = arrowSources[pathIndex];
          bool drawnForThisPath = false;
          for (final metric in path.computeMetrics()) {
            if (metric.length <= 1e-3) continue;

            final bool hasEnoughPoints = (jsonPathPoints != null &&
                pathIndex < jsonPathPoints!.length &&
                jsonPathPoints![pathIndex].length >= 15);
            final bool longEnough = metric.length >= 120;
            final int arrowCount = (hasEnoughPoints || longEnough) ? 2 : 1;

            for (int a = 0; a < arrowCount; a++) {
              final double target = (arrowCount == 1)
                  ? 0.25
                  : (a == 0 ? 0.25 : 0.60);
              final double dist = (metric.length * target).clamp(4.0, metric.length * 0.9);
              final tangent = metric.getTangentForOffset(dist);
              if (tangent == null) continue;
              final tip = tangent.position;
              final dir = tangent.vector;
              final len = dir.distance;
              if (len < 1e-3) continue;

              final unit = dir / len;
              final perp = Offset(-unit.dy, unit.dx);

              final baseCenter = tip - unit * arrowSize;
              final left = baseCenter + perp * (arrowSize * 0.5);
              final right = baseCenter - perp * (arrowSize * 0.5);

              final arrowPath = Path()
                ..moveTo(tip.dx, tip.dy)
                ..lineTo(left.dx, left.dy)
                ..lineTo(right.dx, right.dy)
                ..close();
              canvas.drawPath(arrowPath, arrowPaint);

              // Store arrow tip position and direction for stroke numbering
              arrowTipPositions.add(tip);
              arrowDirections.add(unit);
              arrowStrokeIndices.add(pathIndex + 1);
            }
            drawnForThisPath = true;
            break;
          }
          if (drawnForThisPath) continue;
        }
      }

      // Draw stroke numbers
      const double gapFromArrow = 12.0; // ~4mm gap (approximately 3 pixels per mm)
      const double minBadgeRadius = 6.0;
      const double maxBadgeRadius = 15.0;
      final badgePaint = Paint()
        ..color = Colors.black
        ..style = PaintingStyle.fill;

      // Check if we have custom number positions
      if (customPositions != null && customPositions!.numbers.isNotEmpty) {
        print('🔢 Drawing custom numbers for ${customPositions!.numbers.length} strokes');
        // Use custom number positions
        // Calculate badge size based on path width
        double totalWidth = 0;
        int validWidths = 0;
        final List<double> badgeWidths = [];
        
        // Get letter bounds for consistent coordinate mapping
        final letterBoundsForWidthCalc = letterImage.getBounds();
        
        for (var strokeNum in customPositions!.numbers.keys) {
          for (var customNum in customPositions!.numbers[strokeNum]!) {
            // Use letter bounds for width calculation (consistent with arrows)
            final pos = Offset(
              letterBoundsForWidthCalc.left + customNum.normalizedX * letterBoundsForWidthCalc.width,
              letterBoundsForWidthCalc.top + customNum.normalizedY * letterBoundsForWidthCalc.height,
            );
            final perp = Offset(1, 0); // Default perpendicular
            
            double availableWidth = 0;
            try {
              double leftDist = 0;
              double rightDist = 0;
              
              for (double offset = -50; offset <= 0; offset += 0.5) {
                final testPos = pos + perp * offset;
                if (letterImage.contains(testPos)) {
                  leftDist = -offset;
                } else {
                  break;
                }
              }
              
              for (double offset = 50; offset >= 0; offset -= 0.5) {
                final testPos = pos + perp * offset;
                if (letterImage.contains(testPos)) {
                  rightDist = offset;
                } else {
                  break;
                }
              }
              
              availableWidth = leftDist + rightDist;
              if (availableWidth > 0) {
                badgeWidths.add(availableWidth);
                totalWidth += availableWidth;
                validWidths++;
              }
            } catch (e) {
              // Skip
            }
          }
        }
        
        double avgPathWidth = validWidths > 0 ? (totalWidth / validWidths) : 20.0;
        double minPathWidth = badgeWidths.isNotEmpty 
            ? badgeWidths.reduce((a, b) => a < b ? a : b) 
            : avgPathWidth;
        double baseWidth = (avgPathWidth * 0.7 + minPathWidth * 0.3);
        double badgeRadius = (baseWidth * 0.55).clamp(minBadgeRadius, maxBadgeRadius);
        double fontSize = (badgeRadius * 1.1).clamp(7.0, 14.0);
        
        // Draw custom numbers
        final letterBoundsForNumbers = letterImage.getBounds();
        for (var strokeNum in customPositions!.numbers.keys) {
          for (var customNum in customPositions!.numbers[strokeNum]!) {
            final pos = Offset(
              letterBoundsForNumbers.left + customNum.normalizedX * letterBoundsForNumbers.width,
              letterBoundsForNumbers.top + customNum.normalizedY * letterBoundsForNumbers.height,
            );
            print('   Number ${customNum.strokeNumber} at normalized(${customNum.normalizedX}, ${customNum.normalizedY}) -> screen(${pos.dx}, ${pos.dy})');
            
            canvas.drawCircle(pos, badgeRadius, badgePaint);

            final textPainter = TextPainter(
              text: TextSpan(
                text: customNum.strokeNumber.toString(),
                style: TextStyle(
                  color: Colors.white,
                  fontSize: fontSize,
                  fontWeight: FontWeight.bold,
                ),
              ),
              textDirection: TextDirection.ltr,
            )..layout();
            textPainter.paint(
              canvas,
              pos - Offset(textPainter.width / 2, textPainter.height / 2),
            );
          }
        }
      } else {
        // Fall back to auto-calculated positions (using arrow positions)
        // First pass: Calculate average path width across all badge positions for consistency
        double totalWidth = 0;
        int validWidths = 0;
        final List<double> badgeWidths = [];
        
        for (int i = 0; i < arrowTipPositions.length; i++) {
          final pos = arrowTipPositions[i] + arrowDirections[i] * gapFromArrow;
          final perp = Offset(-arrowDirections[i].dy, arrowDirections[i].dx);
          
          double availableWidth = 0;
          try {
            // Find the path boundary by sampling points perpendicular to the path
            double leftDist = 0;
            double rightDist = 0;
            
            // Check left side (negative offset) - more thorough sampling
            for (double offset = -50; offset <= 0; offset += 0.5) {
              final testPos = pos + perp * offset;
              if (letterImage.contains(testPos)) {
                leftDist = -offset;
              } else {
                break;
              }
            }
            
            // Check right side (positive offset) - more thorough sampling
            for (double offset = 50; offset >= 0; offset -= 0.5) {
              final testPos = pos + perp * offset;
              if (letterImage.contains(testPos)) {
                rightDist = offset;
              } else {
                break;
              }
            }
            
            availableWidth = leftDist + rightDist;
            if (availableWidth > 0) {
              badgeWidths.add(availableWidth);
              totalWidth += availableWidth;
              validWidths++;
            }
          } catch (e) {
            // Skip this position if calculation fails
          }
        }
        
        // Calculate average and minimum path width for consistency
        double avgPathWidth = validWidths > 0 ? (totalWidth / validWidths) : 20.0;
        double minPathWidth = badgeWidths.isNotEmpty 
            ? badgeWidths.reduce((a, b) => a < b ? a : b) 
            : avgPathWidth;
        
        // Use minimum width to ensure all badges fit, but scale with average for proportion
        // This ensures consistency while still being proportional to path width
        double baseWidth = (avgPathWidth * 0.7 + minPathWidth * 0.3);
        
        // Calculate consistent badge radius for all badges in this letter
        // Use 50-55% of the base width, scaled appropriately
        double badgeRadius = (baseWidth * 0.55).clamp(minBadgeRadius, maxBadgeRadius);
        
        // Calculate consistent font size for all badges
        double fontSize = (badgeRadius * 1.1).clamp(7.0, 14.0);
        
        // Second pass: Draw badges with consistent size
        for (int i = 0; i < arrowTipPositions.length; i++) {
          // Position number forward from arrow tip with 4mm gap
          final pos = arrowTipPositions[i] + arrowDirections[i] * gapFromArrow;
          
          canvas.drawCircle(pos, badgeRadius, badgePaint);

          final textPainter = TextPainter(
            text: TextSpan(
              text: arrowStrokeIndices[i].toString(),
              style: TextStyle(
                color: Colors.white,
                fontSize: fontSize,
                fontWeight: FontWeight.bold,
              ),
            ),
            textDirection: TextDirection.ltr,
          )..layout();
          textPainter.paint(
            canvas,
            pos - Offset(textPainter.width / 2, textPainter.height / 2),
          );
        }
      }
    }

    // Paint for the strokes
    final strokePaint = Paint()
      ..color = strokeColor
      ..style = PaintingStyle.stroke
      ..strokeCap = StrokeCap.round
      ..strokeJoin = StrokeJoin.round
      ..strokeWidth = strokeWidth ?? 7.5;

    // Draw all paths with different colors if strokeColors is provided
    if (strokeColors != null && strokeColors!.isNotEmpty) {
      for (int i = 0; i < paths.length; i++) {
        // Use different color for each stroke, cycling through if needed
        final color = strokeColors![i % strokeColors!.length];
        strokePaint.color = color;
        canvas.drawPath(paths[i], strokePaint);
      }
      // Current drawing path uses the color of the current stroke
      if (paths.length < strokeColors!.length) {
        strokePaint.color = strokeColors![paths.length];
      }
    } else {
      // Default behavior: use single strokeColor for all
      for (var path in paths) {
        canvas.drawPath(path, strokePaint);
      }
    }

    // Draw the current drawing path (if needed)
    canvas.drawPath(currentDrawingPath, strokePaint);

    // Draw the cursor/ball inside the clipped area
    if (cursorPosition != null) {
      // Ball radius is slightly smaller than half the stroke width for better visibility
      final cursorRadius = ((strokeWidth ?? 7.5) / 2) * 0.8; // 20% smaller
      final fillPaint = Paint()
        ..color = strokeColor.withOpacity(0.9)
        ..style = PaintingStyle.fill;
      final borderPaint = Paint()
        ..color = Colors.white
        ..style = PaintingStyle.stroke
        ..strokeWidth = 2.0;
      canvas.drawCircle(cursorPosition!, cursorRadius, fillPaint);
      canvas.drawCircle(cursorPosition!, cursorRadius, borderPaint);
    }

    // Restore the canvas state after clipping
    canvas.restore();
  }

  @override
  bool shouldRepaint(CustomPainter oldDelegate) => true;
  
  // Helper to draw dashed rectangle
  void _drawDashedRect(Canvas canvas, Rect rect, Paint paint, List<double> dashPattern) {
    final dashWidth = dashPattern[0];
    final dashSpace = dashPattern.length > 1 ? dashPattern[1] : dashPattern[0];
    final path = Path();
    
    // Top edge
    for (double x = rect.left; x < rect.right; x += dashWidth + dashSpace) {
      path.moveTo(x, rect.top);
      path.lineTo((x + dashWidth).clamp(rect.left, rect.right), rect.top);
    }
    
    // Right edge
    for (double y = rect.top; y < rect.bottom; y += dashWidth + dashSpace) {
      path.moveTo(rect.right, y);
      path.lineTo(rect.right, (y + dashWidth).clamp(rect.top, rect.bottom));
    }
    
    // Bottom edge
    for (double x = rect.right; x > rect.left; x -= dashWidth + dashSpace) {
      path.moveTo(x, rect.bottom);
      path.lineTo((x - dashWidth).clamp(rect.left, rect.right), rect.bottom);
    }
    
    // Left edge
    for (double y = rect.bottom; y > rect.top; y -= dashWidth + dashSpace) {
      path.moveTo(rect.left, y);
      path.lineTo(rect.left, (y - dashWidth).clamp(rect.top, rect.bottom));
    }
    
    canvas.drawPath(path, paint);
  }
  
  // Helper to draw dashed/dotted path along any arbitrary path
  void _drawDashedPath(Canvas canvas, Path path, Paint paint, List<double> dashPattern) {
    final dashLength = dashPattern[0];
    final gapLength = dashPattern.length > 1 ? dashPattern[1] : dashPattern[0];
    final dashPath = Path();
    
    // Use computeMetrics to get path segments
    for (final metric in path.computeMetrics()) {
      double distance = 0.0;
      bool drawDash = true;
      
      while (distance < metric.length) {
        if (drawDash) {
          // Draw dash segment
          final endDistance = (distance + dashLength).clamp(0.0, metric.length);
          final dashSegment = metric.extractPath(distance, endDistance);
          dashPath.addPath(dashSegment, Offset.zero);
          distance = endDistance;
        } else {
          // Skip gap
          distance += gapLength;
        }
        drawDash = !drawDash;
      }
    }
    
    canvas.drawPath(dashPath, paint);
  }
}
