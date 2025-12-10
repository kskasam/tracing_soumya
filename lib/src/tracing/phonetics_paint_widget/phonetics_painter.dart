// For JSON parsing

import 'package:flutter/material.dart';

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

    // Draw small arrows along each stroke (clipped to letter). No JSON fallback to avoid misplacement.
    if (showArrows) {
      final arrowPaint = Paint()
        ..color = dottedColor
        ..style = PaintingStyle.stroke
        ..strokeWidth = 2.0
        ..strokeJoin = StrokeJoin.round
        ..strokeCap = StrokeCap.round;

      const double arrowSize = 8.0; // smaller, outlined

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
          }
          drawnForThisPath = true;
          break;
        }
        if (drawnForThisPath) continue;
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
