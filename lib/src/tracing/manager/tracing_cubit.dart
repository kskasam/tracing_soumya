import 'dart:async';
import 'dart:convert';
import 'dart:math' as math;

import 'package:bloc/bloc.dart';
import 'package:equatable/equatable.dart';
import 'package:flutter/cupertino.dart';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:svg_path_parser/svg_path_parser.dart';
import 'package:tracing_game/src/tracing/model/letter_paths_model.dart';
import 'package:tracing_game/src/tracing/model/trace_model.dart';
import 'package:tracing_game/tracing_game.dart';

import '../../get_shape_helper/enum_of_arabic_and_numbers_letters.dart';

part 'tracing_state.dart';

class TracingCubit extends Cubit<TracingState> {
  TracingCubit({
    List<TraceWordModel>? traceWordModels,
    List<TraceGeoMetricShapeModel>? traceGeoMetricShapeModel,
    List<TraceCharsModel>? traceShapeModel,
    required StateOfTracing stateOfTracing,
  }) : super(TracingState(
          numberOfScreens: stateOfTracing == StateOfTracing.chars
              ? traceShapeModel!.length
              : stateOfTracing == StateOfTracing.traceShapes
                  ? traceGeoMetricShapeModel!.length
                  : stateOfTracing == StateOfTracing.traceWords
                      ? traceWordModels!.length
                      : 0,
          traceWordModels: traceWordModels,
          traceGeoMetricShapes: traceGeoMetricShapeModel,
          traceShapeModel: traceShapeModel,
          index: 0,
          stateOfTracing: stateOfTracing,
          traceLetter: const [],
          letterPathsModels: const [],
        )) {
    updateTheTraceLetter();
  }
  updateIndex() {
    int index = state.index;
    index++;
    if (index < state.numberOfScreens) {
      emit(state.copyWith(index: index, drawingStates: DrawingStates.loaded));
      updateTheTraceLetter();
    }
  }

  updateTheTraceLetter() async {
    emit(state.clearData());
    emit(state.copyWith(
        activeIndex: 0,
        stateOfTracing: state.stateOfTracing,
        traceLetter: TypeExtensionTracking().getTracingData(
            geometryShapes: state.stateOfTracing == StateOfTracing.traceShapes &&  state.traceGeoMetricShapes!.isNotEmpty
                ? state.traceGeoMetricShapes![state.index].shapes
                : null,
            chars: state.stateOfTracing == StateOfTracing.chars &&  state.traceShapeModel!.isNotEmpty
                ? state.traceShapeModel![state.index].chars
                : null,
                word:state.stateOfTracing == StateOfTracing.traceWords &&  state.traceWordModels!.isNotEmpty
                ? state.traceWordModels![state.index]
                : null ,
            currentOfTracking: state.stateOfTracing)));
    await loadAssets();
  }

  final viewSize = const Size(200, 200);
  Future<void> loadAssets() async {
    emit(state.copyWith(drawingStates: DrawingStates.loading));

    List<LetterPathsModel> model = [];
    for (var e in state.traceLetter) {
      final letterModel = e;
      final parsedPath = parseSvgPath(letterModel.letterPath);

      final dottedIndexPath = parseSvgPath(letterModel.indexPath);
      final dottedPath = parseSvgPath(letterModel.dottedPath);

      final transformedPath = _applyTransformation(
        parsedPath,
        letterModel.letterViewSize, // Use letterViewSize instead of hardcoded viewSize
      );

      // Get the original SVG bounds to use for centerline transformation
      final originalSvgBounds = parsedPath.getBounds();

      final dottedPathTransformed = _applyTransformationForOtherPathsDotted(
          dottedPath,
          letterModel.letterViewSize, // Use letterViewSize
          letterModel.positionDottedPath,
          letterModel.scaledottedPath,
          originalSvgBounds); // Pass main SVG bounds
      final indexPathTransformed = _applyTransformationForOtherPathsIndex(
          dottedIndexPath,
          letterModel.letterViewSize, // Use letterViewSize
          letterModel.positionIndexPath,
          letterModel.scaleIndexPath);

      final allStrokePoints = await _loadPointsFromJson(
        letterModel.pointsJsonFile,
        letterModel.letterViewSize, // Use letterViewSize instead of hardcoded viewSize
        parsedPath, // Pass the SVG path for proper transformation
      );
      final anchorPos =
          allStrokePoints.isNotEmpty ? allStrokePoints[0][0] : Offset.zero;
      
      // Debug Telugu coordinates (originalSvgBounds already declared above)
      if (letterModel.pointsJsonFile.contains('telugu')) {
        print('=== Telugu Debug ===');
        print('Letter: ${letterModel.pointsJsonFile}');
        print('letterViewSize: ${letterModel.letterViewSize}');
        print('SVG bounds: $originalSvgBounds');
        print('First JSON point AFTER transformation: ${allStrokePoints.isNotEmpty ? allStrokePoints[0][0] : "none"}');
        print('anchorPos: $anchorPos');
        print('==================');
      }

      model.add(LetterPathsModel(
          isSpace: letterModel.isSpace,
          viewSize: letterModel.letterViewSize,
          disableDivededStrokes: letterModel.disableDividedStrokes,
          strokeIndex: letterModel.strokeIndex,
          strokeWidth: letterModel.strokeWidth,
          dottedIndex: dottedPathTransformed,
          letterIndex: indexPathTransformed,
          dottedColor: letterModel.dottedColor,
          indexColor: letterModel.indexColor,
          innerPaintColor: letterModel.innerPaintColor,
          outerPaintColor: letterModel.outerPaintColor,
          allStrokePoints: allStrokePoints,
          letterImage: transformedPath,
          anchorPos: anchorPos,
          cursorPosition: anchorPos,
          distanceToCheck: letterModel.distanceToCheck,
          indexPathPaintStyle: letterModel.indexPathPaintStyle,
          dottedPathPaintStyle: letterModel.dottedPathPaintStyle,
          strokeColors: letterModel.strokeColors,
          svgBounds: originalSvgBounds));
    }

    emit(state.copyWith(
      letterPathsModels: model,
      drawingStates: DrawingStates.loaded,
    ));
  }

  Path _applyTransformation(
    Path path,
    Size viewSize,
  ) {
    // Get the bounds of the original path
    final Rect originalBounds = path.getBounds();
    final Size originalSize = Size(originalBounds.width, originalBounds.height);

    // Calculate the scale factor to fit the SVG within the view size
    final double scaleX = viewSize.width / originalSize.width;
    final double scaleY = viewSize.height / originalSize.height;
    double scale = math.min(scaleX, scaleY);
    
    // FIXED: Transform in correct order:
    // 1. Translate path so its top-left is at (0,0) - removes SVG offset
    // 2. Scale the path
    // 3. Translate to center within viewSize
    
    // Step 1: Translate to origin (remove SVG's offset)
    final double offsetX = -originalBounds.left;
    final double offsetY = -originalBounds.top;
    
    // Step 2: Scale
    // (scale is already calculated)
    
    // Step 3: Center within viewSize
    final double centerX = (viewSize.width - originalSize.width * scale) / 2;
    final double centerY = (viewSize.height - originalSize.height * scale) / 2;
    
    // Combined transformation: translate to origin, scale, then center
    // Matrix4 applies operations in reverse order (right to left):
    // translate(center) * scale * translate(offset)
    // So we write: translate(offset) then scale then translate(center)
    Matrix4 matrix = Matrix4.identity()
      ..translate(centerX, centerY)  // Step 3: Center (applied last)
      ..scale(scale, scale)          // Step 2: Scale (applied second)
      ..translate(offsetX, offsetY); // Step 1: Move to origin (applied first)

    // Apply the transformation to the path
    return path.transform(matrix.storage);
  }

  Path _applyTransformationForOtherPathsIndex(
      Path path, Size viewSize, Size? size, double? pathscale) {
    final Rect originalBounds = path.getBounds();
    final Size originalSize = Size(originalBounds.width, originalBounds.height);

    // Calculate the scale factor to fit the path within the view size
    final double scaleX = viewSize.width / originalSize.width;
    final double scaleY = viewSize.height / originalSize.height;

    double scale = math.min(scaleX, scaleY);
    scale = pathscale == null ? scale : scale * pathscale;

    // FIXED: Use the same 3-step transformation as main SVG path
    // 1. Translate to origin (remove path's offset)
    // 2. Scale the path
    // 3. Center within viewSize (or apply additional position offset if size is provided)
    
    // Step 1: Translate to origin (remove path's offset)
    final double offsetX = -originalBounds.left;
    final double offsetY = -originalBounds.top;
    
    // Step 2: Scale (already calculated)
    
    // Step 3: Center within viewSize
    double centerX = (viewSize.width - originalSize.width * scale) / 2;
    double centerY = (viewSize.height - originalSize.height * scale) / 2;
    
    // Apply additional position offset if provided
    if (size != null) {
      centerX += size.width;
      centerY += size.height;
    }
    
    // Combined transformation: translate to origin, scale, then center
    // Matrix4 applies operations in reverse order (right to left):
    Matrix4 matrix = Matrix4.identity()
      ..translate(centerX, centerY)  // Step 3: Center (applied last)
      ..scale(scale, scale)          // Step 2: Scale (applied second)
      ..translate(offsetX, offsetY); // Step 1: Move to origin (applied first)
    // Apply the transformation to the path
    return path.transform(matrix.storage);
  }

  Path _applyTransformationForOtherPathsDotted(
      Path path, Size viewSize, Size? size, double? pathscale, Rect? svgBounds) {
    // IMPORTANT: Use the main SVG's bounds for transformation, not the centerline's own bounds
    // This ensures the centerline aligns with the main SVG path
    final Rect originalBounds = svgBounds ?? path.getBounds();
    final Size originalSize = Size(originalBounds.width, originalBounds.height);

    // Calculate the scale factor to fit the SVG within the view size
    final double scaleX = viewSize.width / originalSize.width;
    final double scaleY = viewSize.height / originalSize.height;
    double scale = math.min(scaleX, scaleY);
    scale = pathscale == null ? scale : scale * pathscale;

    // FIXED: Use the same 3-step transformation as main SVG path
    // 1. Translate to origin (remove SVG's offset)
    // 2. Scale the path
    // 3. Center within viewSize (or apply additional position offset if size is provided)
    
    // Step 1: Translate to origin (remove SVG's offset)
    final double offsetX = -originalBounds.left;
    final double offsetY = -originalBounds.top;
    
    // Step 2: Scale (already calculated)
    
    // Step 3: Center within viewSize
    double centerX = (viewSize.width - originalSize.width * scale) / 2;
    double centerY = (viewSize.height - originalSize.height * scale) / 2;
    
    // Apply additional position offset if provided
    if (size != null) {
      centerX += size.width;
      centerY += size.height;
    }
    
    // Combined transformation: translate to origin, scale, then center
    // Matrix4 applies operations in reverse order (right to left):
    Matrix4 matrix = Matrix4.identity()
      ..translate(centerX, centerY)  // Step 3: Center (applied last)
      ..scale(scale, scale)          // Step 2: Scale (applied second)
      ..translate(offsetX, offsetY); // Step 1: Move to origin (applied first)
    
    // Apply the transformation to the path
    return path.transform(matrix.storage);
  }

  Future<List<List<Offset>>> _loadPointsFromJson(
      String path, Size viewSize, Path svgPath) async {
    final jsonString = await rootBundle.loadString('packages/tracing_game/$path');

    final jsonData = jsonDecode(jsonString);
    final List<List<Offset>> strokePointsList = [];

    // Get SVG transformation parameters (same as _applyTransformation)
    final Rect originalBounds = svgPath.getBounds();
    final Size originalSize = Size(originalBounds.width, originalBounds.height);
    final double scaleX = viewSize.width / originalSize.width;
    final double scaleY = viewSize.height / originalSize.height;
    final double scale = math.min(scaleX, scaleY);
    
    // Calculate center offset (same as in _applyTransformation)
    final double centerX = (viewSize.width - originalSize.width * scale) / 2;
    final double centerY = (viewSize.height - originalSize.height * scale) / 2;

    for (var stroke in jsonData['strokes']) {
      final List<dynamic> strokePointsData = stroke['points'];
      final points = strokePointsData.map<Offset>((pointString) {
        final coords =
            pointString.split(',').map((e) => double.parse(e)).toList();
        
        // CRITICAL FIX: Apply SAME transformation as SVG!
        // Transformation order: translate to origin -> scale -> center
        
        // Step 1: Map normalized coords (0-1) to SVG coordinate space
        final svgX = originalBounds.left + coords[0] * originalSize.width;
        final svgY = originalBounds.top + coords[1] * originalSize.height;
        
        // Step 2: Apply the same transformation as SVG path:
        // 1. Translate to origin (remove SVG offset)
        final offsetX = -originalBounds.left;
        final offsetY = -originalBounds.top;
        final centeredX = svgX + offsetX;  // Now at (0,0) relative to bounds
        final centeredY = svgY + offsetY;
        
        // 2. Scale
        final scaledX = centeredX * scale;
        final scaledY = centeredY * scale;
        
        // 3. Center within viewSize (use pre-calculated centerX/centerY)
        final transformedX = scaledX + centerX;
        final transformedY = scaledY + centerY;
        
        return Offset(transformedX, transformedY);
      }).toList();
      strokePointsList.add(points);
    }

    return strokePointsList;
  }

  void handlePanStart(Offset position) {
    if (!isTracingStartPoint(position)) {
      return;
    }
emit(state.copyWith(drawingStates: DrawingStates.tracing));
    final currentStrokePoints =
        state.letterPathsModels[state.activeIndex].allStrokePoints[
            state.letterPathsModels[state.activeIndex].currentStroke];

    if (state.letterPathsModels[state.activeIndex].currentStrokeProgress >= 0 &&
        state.letterPathsModels[state.activeIndex].currentStrokeProgress <
            currentStrokePoints.length) {
      if (currentStrokePoints.length == 1) {
        final singlePoint = currentStrokePoints[0];
        if (isValidPoint(singlePoint, position,
            state.letterPathsModels[state.activeIndex].distanceToCheck)) {
          final newDrawingPath = Path()
            ..moveTo(singlePoint.dx, singlePoint.dy)
            ..lineTo(
                currentStrokePoints.first.dx, currentStrokePoints.first.dy);

          state.letterPathsModels[state.activeIndex].anchorPos = singlePoint;
          state.letterPathsModels[state.activeIndex].cursorPosition = singlePoint;
          state.letterPathsModels[state.activeIndex].currentDrawingPath =
              newDrawingPath;

          completeStroke();
          return;
        }
      }
    } else if (state
            .letterPathsModels[state.activeIndex].currentStrokeProgress ==
        -1) {
      final currentStrokePoints =
          state.letterPathsModels[state.activeIndex].allStrokePoints[
              state.letterPathsModels[state.activeIndex].currentStroke];

      if (currentStrokePoints.length == 1) {
        final singlePoint = currentStrokePoints[0];
        if (isValidPoint(singlePoint, position,
            state.letterPathsModels[state.activeIndex].distanceToCheck)) {
          final newDrawingPath = Path()..moveTo(singlePoint.dx, singlePoint.dy);
          state.letterPathsModels[state.activeIndex].currentDrawingPath =
              newDrawingPath..lineTo(singlePoint.dx, singlePoint.dy);
          state.letterPathsModels[state.activeIndex].currentStrokeProgress = 1;
          completeStroke();
        } else {}
      } else {
        if (state.letterPathsModels[state.activeIndex].anchorPos != null) {
          final newDrawingPath = Path()
            ..moveTo(state.letterPathsModels[state.activeIndex].anchorPos!.dx,
                state.letterPathsModels[state.activeIndex].anchorPos!.dy);

          state.letterPathsModels[state.activeIndex].currentDrawingPath =
              newDrawingPath;
          state.letterPathsModels[state.activeIndex].currentStrokeProgress = 1;
          emit(state.copyWith(
            letterPathsModels: state.letterPathsModels,
          ));
        } 
      }
    }
  }

  void handlePanUpdate(Offset position) {
    final currentModel = state.letterPathsModels[state.activeIndex];
    final currentStrokePoints = currentModel.allStrokePoints[currentModel.currentStroke];

    // If stroke hasn't started yet (progress == -1), try to start it
    if (currentModel.currentStrokeProgress == -1) {
      // Check if position is near the first point
      if (currentStrokePoints.isNotEmpty) {
        final firstPoint = currentStrokePoints[0];
        final distanceToFirst = (position - firstPoint).distance;
        final distanceThreshold = currentModel.distanceToCheck ?? 50.0;
        
        // If close to first point, initialize the stroke
        if (distanceToFirst < distanceThreshold) {
          final newDrawingPath = Path()..moveTo(firstPoint.dx, firstPoint.dy);
          currentModel.currentDrawingPath = newDrawingPath;
          currentModel.currentStrokeProgress = 0; // Start at index 0
          currentModel.anchorPos = firstPoint;
          currentModel.cursorPosition = firstPoint;
          emit(state.copyWith(letterPathsModels: state.letterPathsModels));
        }
      }
      // If we couldn't start, return early
      if (currentModel.currentStrokeProgress == -1) {
        return;
      }
    }

    if (currentModel.currentStrokeProgress >= 0 &&
        currentModel.currentStrokeProgress < currentStrokePoints.length) {
      
      // BALL-ON-RAILS: Find the nearest point on the current stroke that user is dragging toward
      final currentProgress = currentModel.currentStrokeProgress;
      
      // Get current ball position
      final currentBallPos = currentModel.cursorPosition ?? 
                             (currentProgress > 0 && currentProgress <= currentStrokePoints.length 
                              ? currentStrokePoints[currentProgress - 1] 
                              : currentStrokePoints[0]);
      
      // Check if cursor has moved too far from current ball position (prevents jumps at curves)
      // Increased tolerance for better user experience
      final maxLateralDistance = 60.0; // Maximum distance cursor can be from ball (increased from 45)
      final cursorDistanceFromBall = (position - currentBallPos).distance;
      
      // If cursor is too far from ball, don't move the ball (user moved cursor off path)
      // But allow if we're at the very beginning (progress 0 or 1)
      if (cursorDistanceFromBall > maxLateralDistance && currentProgress > 1) {
        return;
      }
      
      int? bestPointIndex;
      double minDistance = double.infinity;
      final distanceThreshold = currentModel.distanceToCheck ?? 50.0;
      
      // Limit how many points ahead we can jump in one update to prevent sudden jumps at curves
      // This ensures smooth progression along the path
      final maxLookAhead = 5; // Only check next 5 points for even smoother movement
      final endIndex = (currentProgress + maxLookAhead).clamp(0, currentStrokePoints.length);
      
      // Check points ahead of current progress (allow moving forward along the path)
      for (int i = currentProgress; i < endIndex; i++) {
        final point = currentStrokePoints[i];
        final distance = (point - position).distance;
        
        // Only consider points that are close enough (within distanceToCheck)
        if (distance < distanceThreshold && distance < minDistance) {
          minDistance = distance;
          bestPointIndex = i;
        }
      }
      
      // NEW: Also check if position is close to any point in previously completed strokes
      // that also exists in the current stroke (allows tracing over overlaps)
      // This enables tracing over parts of completed strokes when the current stroke overlaps
      if (bestPointIndex == null && currentModel.currentStroke > 0) {
        // Check all completed strokes
        for (int completedStrokeIdx = 0; completedStrokeIdx < currentModel.currentStroke; completedStrokeIdx++) {
          final completedStrokePoints = currentModel.allStrokePoints[completedStrokeIdx];
          
          // Find closest point in completed stroke
          for (int completedPointIdx = 0; completedPointIdx < completedStrokePoints.length; completedPointIdx++) {
            final completedPoint = completedStrokePoints[completedPointIdx];
            final distanceToCompleted = (position - completedPoint).distance;
            
            // If close to a completed stroke point, check if it exists in current stroke
            if (distanceToCompleted < distanceThreshold) {
              // Find matching point in current stroke (with tolerance for floating point differences)
              // Use a small tolerance (2 pixels) to account for floating point precision
              const pointMatchTolerance = 2.0;
              for (int currentIdx = currentProgress; currentIdx < currentStrokePoints.length; currentIdx++) {
                final currentPoint = currentStrokePoints[currentIdx];
                final pointDistance = (currentPoint - completedPoint).distance;
                
                // If points match (within tolerance), allow tracing to this point
                if (pointDistance < pointMatchTolerance && currentIdx >= currentProgress) {
                  if (distanceToCompleted < minDistance) {
                    minDistance = distanceToCompleted;
                    bestPointIndex = currentIdx;
                    break; // Found match in this completed stroke, check next completed stroke
                  }
                }
              }
              // If we found a match, we can break early (best match found)
              if (bestPointIndex != null) break;
            }
          }
          // If we found a match, no need to check other completed strokes
          if (bestPointIndex != null) break;
        }
      }
      
      // Only move if we found a point and it's not too small of a movement
      if (bestPointIndex != null && bestPointIndex >= currentProgress) {
        // Prevent tiny movements (similar to _progressEpsilon in flutter_tracing)
        if (bestPointIndex == currentProgress) {
          return; // Don't move if still at same point
        }
        // Update progress to this point
        currentModel.currentStrokeProgress = bestPointIndex + 1;
        
        // Rebuild the drawing path up to this point
        final newDrawingPath = Path();
        if (currentStrokePoints.isNotEmpty) {
          newDrawingPath.moveTo(currentStrokePoints[0].dx, currentStrokePoints[0].dy);
          for (int i = 0; i <= bestPointIndex; i++) {
            newDrawingPath.lineTo(currentStrokePoints[i].dx, currentStrokePoints[i].dy);
          }
        }
        
        // Update ball position (anchor) to the found point
        currentModel.anchorPos = currentStrokePoints[bestPointIndex];
        currentModel.cursorPosition = currentStrokePoints[bestPointIndex];
        currentModel.currentDrawingPath = newDrawingPath;
        
        emit(state.copyWith(letterPathsModels: state.letterPathsModels));
      }
    }

    // Check if stroke is complete
    if (currentModel.currentStrokeProgress >= currentStrokePoints.length) {
      completeStroke();
      return;
    }
    
    // Additional lenient check: If we're at or near the last point, complete the stroke
    // This helps when the user is very close to the end but hasn't reached the exact last point
    if (currentStrokePoints.isNotEmpty && 
        currentModel.currentStrokeProgress >= currentStrokePoints.length - 1) {
      final lastPoint = currentStrokePoints.last;
      final distanceToLast = (position - lastPoint).distance;
      final distanceThreshold = currentModel.distanceToCheck ?? 50.0;
      
      // If within 1.5x threshold of last point and we're at second-to-last or last point, complete
      if (distanceToLast < distanceThreshold * 1.5) {
        // Force completion by setting progress to the end
        currentModel.currentStrokeProgress = currentStrokePoints.length;
        
        // Rebuild the drawing path to include all points
        final newDrawingPath = Path();
        if (currentStrokePoints.isNotEmpty) {
          newDrawingPath.moveTo(currentStrokePoints[0].dx, currentStrokePoints[0].dy);
          for (int i = 0; i < currentStrokePoints.length; i++) {
            newDrawingPath.lineTo(currentStrokePoints[i].dx, currentStrokePoints[i].dy);
          }
        }
        currentModel.currentDrawingPath = newDrawingPath;
        currentModel.anchorPos = lastPoint;
        currentModel.cursorPosition = lastPoint;
        
        emit(state.copyWith(letterPathsModels: state.letterPathsModels));
        completeStroke();
        return;
      }
    }
  }

  void completeStroke() {
    final currentModel = state.letterPathsModels[state.activeIndex];
    final currentStrokeIndex = currentModel.currentStroke;

    if (currentStrokeIndex < currentModel.allStrokePoints.length - 1) {
      currentModel.paths.add(currentModel.currentDrawingPath);

      currentModel.currentStroke = currentStrokeIndex + 1;
      // Set to -1 to indicate stroke hasn't started yet (allows handlePanStart to initialize it)
      currentModel.currentStrokeProgress = -1;

      // Initialize anchor and cursor to first point of new stroke
      final nextStrokePoints = currentModel.allStrokePoints[currentModel.currentStroke];
      if (nextStrokePoints.isNotEmpty) {
        currentModel.anchorPos = nextStrokePoints[0];
        currentModel.cursorPosition = nextStrokePoints[0];
        // Initialize drawing path with first point (will be properly set in handlePanStart)
        currentModel.currentDrawingPath = Path()..moveTo(nextStrokePoints[0].dx, nextStrokePoints[0].dy);
      }
      emit(state.copyWith(letterPathsModels: state.letterPathsModels));
    } else if (!currentModel.letterTracingFinished) {
      // IMPORTANT: Add the last stroke's path before marking letter as finished
      currentModel.paths.add(currentModel.currentDrawingPath);
      
      currentModel.letterTracingFinished = true;
      currentModel.hasFinishedOneStroke = true;
      if (state.activeIndex < state.letterPathsModels.length - 1) {
        // Move to next letter and ensure it's properly initialized
        final nextIndex = state.activeIndex + 1;
        final nextModel = state.letterPathsModels[nextIndex];
        
        // Ensure next letter's stroke progress is reset and anchor is set
        if (nextModel.allStrokePoints.isNotEmpty && nextModel.allStrokePoints[0].isNotEmpty) {
          nextModel.currentStroke = 0;
          nextModel.currentStrokeProgress = -1;
          nextModel.anchorPos = nextModel.allStrokePoints[0][0];
          nextModel.cursorPosition = nextModel.allStrokePoints[0][0];
          nextModel.currentDrawingPath = Path()..moveTo(nextModel.allStrokePoints[0][0].dx, nextModel.allStrokePoints[0][0].dy);
        }
        
        emit(state.copyWith(
          activeIndex: nextIndex,
          letterPathsModels: state.letterPathsModels,
        ));
      } else if (state.index == state.numberOfScreens-1 ) {
    
        emit(state.copyWith(
            activeIndex: (state.activeIndex),
            letterPathsModels: state.letterPathsModels,
            drawingStates: DrawingStates.gameFinished));
      } else {
        emit(state.copyWith(
            activeIndex: (state.activeIndex),
            letterPathsModels: state.letterPathsModels,
            drawingStates: DrawingStates.finishedCurrentScreen));
      }
    }
  }

  bool isTracingStartPoint(Offset position) {
    final currentModel = state.letterPathsModels[state.activeIndex];
    final currentStrokePoints = currentModel.allStrokePoints[currentModel.currentStroke];

    // If stroke has only one point, allow starting anywhere
    if (currentStrokePoints.length == 1) {
      return true;
    }
    
    // If anchor position is set, check if position is near it
    if (currentModel.anchorPos != null) {
      final anchorRect = Rect.fromCenter(
          center: currentModel.anchorPos!,
          width: 50,
          height: 50);
      if (anchorRect.contains(position)) {
        return true;
      }
    }
    
    // NEW: Also allow starting if position is close to the first point of current stroke
    // This helps when transitioning to a new letter where anchorPos might not be perfectly set
    if (currentStrokePoints.isNotEmpty) {
      final firstPoint = currentStrokePoints[0];
      final distanceToFirst = (position - firstPoint).distance;
      final distanceThreshold = currentModel.distanceToCheck ?? 50.0;
      
      // If within threshold of first point and stroke hasn't started yet, allow starting
      if (distanceToFirst < distanceThreshold && currentModel.currentStrokeProgress == -1) {
        return true;
      }
    }
    
    return false;
  }

  bool isValidPoint(Offset point, Offset position, double? distanceToCheck) {
    final validArea = distanceToCheck ?? 30.0;
    bool isValid = (position - point).distance < validArea;
    return isValid;
  }
}
