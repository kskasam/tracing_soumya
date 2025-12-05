
import 'package:flutter/material.dart';

class TraceModel {
  final bool isSpace;
  final String letterPath;
  final String pointsJsonFile;
  // final Color pointColor;
  final String dottedPath;
  final String indexPath;
final bool? disableDividedStrokes;
  final Color outerPaintColor;
  final Color innerPaintColor;
  final Color dottedColor;
  final Color indexColor;
  final double strokeWidth;

final PaintingStyle? indexPathPaintStyle;
final PaintingStyle? dottedPathPaintStyle;

final Size? positionIndexPath;
final Size? positionDottedPath;
final double? scaleIndexPath;
final double? scaledottedPath;
final double? distanceToCheck;
final Size  letterViewSize;
final double? strokeIndex;

  // For debugging: Different color for each stroke
  final List<Color>? strokeColors;

  TraceModel({
        this.isSpace=false,

    this.letterViewSize=const Size(200,200),
    this.disableDividedStrokes,
    this.strokeIndex,
    this.distanceToCheck,
    this.scaledottedPath,
    this.scaleIndexPath,
    this.positionIndexPath,    this.positionDottedPath,

    this.indexPathPaintStyle,
    this.dottedPathPaintStyle,
    this.strokeWidth=5.625,
     this.indexColor = Colors.black,
    this.outerPaintColor = Colors.red,
    this.innerPaintColor = Colors.blue,
    this.dottedColor = Colors.amber,
    required this.dottedPath,
    required this.indexPath,
    required this.letterPath,
    required this.pointsJsonFile,
    // required this.pointColor,
    this.strokeColors,

  });

  TraceModel copyWith({
    bool? isSpace,
    String? letterPath,
    String? pointsJsonFile,
    String? dottedPath,
    String? indexPath,
    bool? disableDividedStrokes,
    Color? outerPaintColor,
    Color? innerPaintColor,
    Color? dottedColor,
    Color? indexColor,
    double? strokeWidth,
    PaintingStyle? indexPathPaintStyle,
    PaintingStyle? dottedPathPaintStyle,
    Size? positionIndexPath,
    Size? positionDottedPath,
    double? scaleIndexPath,
    double? scaledottedPath,
    double? distanceToCheck,
    Size? letterViewSize,
    double? strokeIndex,
    List<Color>? strokeColors,
  }) {
    return TraceModel(
      isSpace: isSpace ?? this.isSpace,
      letterPath: letterPath ?? this.letterPath,
      pointsJsonFile: pointsJsonFile ?? this.pointsJsonFile,
      dottedPath: dottedPath ?? this.dottedPath,
      indexPath: indexPath ?? this.indexPath,
      disableDividedStrokes: disableDividedStrokes ?? this.disableDividedStrokes,
      outerPaintColor: outerPaintColor ?? this.outerPaintColor,
      innerPaintColor: innerPaintColor ?? this.innerPaintColor,
      dottedColor: dottedColor ?? this.dottedColor,
      indexColor: indexColor ?? this.indexColor,
      strokeWidth: strokeWidth ?? this.strokeWidth,
      indexPathPaintStyle: indexPathPaintStyle ?? this.indexPathPaintStyle,
      dottedPathPaintStyle: dottedPathPaintStyle ?? this.dottedPathPaintStyle,
      positionIndexPath: positionIndexPath ?? this.positionIndexPath,
      positionDottedPath: positionDottedPath ?? this.positionDottedPath,
      scaleIndexPath: scaleIndexPath ?? this.scaleIndexPath,
      scaledottedPath: scaledottedPath ?? this.scaledottedPath,
      distanceToCheck: distanceToCheck ?? this.distanceToCheck,
      letterViewSize: letterViewSize ?? this.letterViewSize,
      strokeIndex: strokeIndex ?? this.strokeIndex,
      strokeColors: strokeColors ?? this.strokeColors,
    );
  }
}
