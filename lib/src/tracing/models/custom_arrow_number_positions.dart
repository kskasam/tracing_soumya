/// Model for custom arrow and number positions loaded from JSON
class CustomArrowNumberPositions {
  final List<CustomArrowPosition> arrows;
  final Map<int, List<CustomNumberPosition>> numbers;

  CustomArrowNumberPositions({
    required this.arrows,
    required this.numbers,
  });

  factory CustomArrowNumberPositions.fromJson(Map<String, dynamic> json) {
    final arrows = <CustomArrowPosition>[];
    final numbers = <int, List<CustomNumberPosition>>{};
    
    // Check if this is the processed format (has 'arrows' and 'numbers' keys)
    if (json['arrows'] != null && json['numbers'] != null) {
      // Processed format - already normalized
      for (var arrowJson in json['arrows']) {
        arrows.add(CustomArrowPosition.fromJson(arrowJson));
      }
      
      final numbersJson = json['numbers'] as Map<String, dynamic>;
      numbersJson.forEach((strokeNumStr, positionsJson) {
        final strokeNum = int.parse(strokeNumStr);
        final positions = <CustomNumberPosition>[];
        for (var posJson in positionsJson) {
          positions.add(CustomNumberPosition.fromJson(posJson));
        }
        numbers[strokeNum] = positions;
      });
    } 
    // Check if this is the raw HTML editor format (has 'items' array)
    else if (json['items'] != null) {
      // Raw HTML editor format - coordinates are in viewBox space
      final items = json['items'] as List<dynamic>;
      
      // Get SVG bounds for proper normalization
      double svgX = 0, svgY = 0, svgWidth = 200, svgHeight = 200;
      final svgBoundsData = json['svgBounds'];
      if (svgBoundsData != null && svgBoundsData is Map) {
        svgX = (svgBoundsData['x'] ?? 0).toDouble();
        svgY = (svgBoundsData['y'] ?? 0).toDouble();
        svgWidth = (svgBoundsData['width'] ?? 200).toDouble();
        svgHeight = (svgBoundsData['height'] ?? 200).toDouble();
      }
      
      // Normalize based on SVG bounds (not viewBox)
      // This matches the transformation applied in Flutter
      print('📐 Normalizing with SVG bounds: ($svgX, $svgY, $svgWidth, $svgHeight)');
      
      for (var item in items) {
        final itemMap = item as Map<String, dynamic>;
        final type = itemMap['type'] as String?;
        
        if (type == 'arrow' || type == 'line') {
          // For lines, use the end point (x2, y2) as the arrow position
          final x = (type == 'line' ? itemMap['x2'] : itemMap['x'])?.toDouble() ?? 0.0;
          final y = (type == 'line' ? itemMap['y2'] : itemMap['y'])?.toDouble() ?? 0.0;
          
          // Normalize based on SVG bounds (x and y are in original SVG space)
          // Normalize to 0-1 range within SVG bounds
          // Clamp to 0-1 to handle coordinates slightly outside bounds
          final normX = ((x - svgX) / svgWidth).clamp(0.0, 1.0);
          final normY = ((y - svgY) / svgHeight).clamp(0.0, 1.0);
          
          if (x < svgX || x > svgX + svgWidth || y < svgY || y > svgY + svgHeight) {
            print('⚠️ Arrow coordinate OUTSIDE SVG bounds: SVG($x, $y) vs bounds($svgX, $svgY, ${svgX + svgWidth}, ${svgY + svgHeight})');
          }
          print('📍 Arrow: SVG($x, $y) -> normalized($normX, $normY) [bounds: ($svgX, $svgY, $svgWidth, $svgHeight)]');
          
          arrows.add(CustomArrowPosition(
            x: x,
            y: y,
            normalizedX: normX,
            normalizedY: normY,
            angle: itemMap['angle']?.toDouble(),
            arrowType: itemMap['arrowType'] as String?,
          ));
        } else if (type == 'number') {
          final x = itemMap['x']?.toDouble() ?? 0.0;
          final y = itemMap['y']?.toDouble() ?? 0.0;
          final strokeNum = itemMap['strokeNumber']?.toInt() ?? 1;
          
          // Normalize based on SVG bounds (x and y are in original SVG space)
          // Clamp to 0-1 to handle coordinates slightly outside bounds
          final normX = ((x - svgX) / svgWidth).clamp(0.0, 1.0);
          final normY = ((y - svgY) / svgHeight).clamp(0.0, 1.0);
          
          if (x < svgX || x > svgX + svgWidth || y < svgY || y > svgY + svgHeight) {
            print('⚠️ Number coordinate OUTSIDE SVG bounds: SVG($x, $y) vs bounds($svgX, $svgY, ${svgX + svgWidth}, ${svgY + svgHeight})');
          }
          print('🔢 Number: SVG($x, $y) -> normalized($normX, $normY) [bounds: ($svgX, $svgY, $svgWidth, $svgHeight)]');
          
          if (!numbers.containsKey(strokeNum)) {
            numbers[strokeNum] = [];
          }
          numbers[strokeNum]!.add(CustomNumberPosition(
            x: x,
            y: y,
            normalizedX: normX,
            normalizedY: normY,
            strokeNumber: strokeNum,
          ));
        }
      }
    }

    return CustomArrowNumberPositions(arrows: arrows, numbers: numbers);
  }
}

class CustomArrowPosition {
  final double x;
  final double y;
  final double normalizedX;
  final double normalizedY;
  final double? angle;
  final String? arrowType;

  CustomArrowPosition({
    required this.x,
    required this.y,
    required this.normalizedX,
    required this.normalizedY,
    this.angle,
    this.arrowType,
  });

  factory CustomArrowPosition.fromJson(Map<String, dynamic> json) {
    return CustomArrowPosition(
      x: (json['x'] ?? json['original_x'] ?? 0.0).toDouble(),
      y: (json['y'] ?? json['original_y'] ?? 0.0).toDouble(),
      normalizedX: (json['normalized_x'] ?? json['x'] ?? 0.0).toDouble(),
      normalizedY: (json['normalized_y'] ?? json['y'] ?? 0.0).toDouble(),
      angle: json['angle']?.toDouble(),
      arrowType: json['type'] ?? json['arrowType'],
    );
  }
}

class CustomNumberPosition {
  final double x;
  final double y;
  final double normalizedX;
  final double normalizedY;
  final int strokeNumber;

  CustomNumberPosition({
    required this.x,
    required this.y,
    required this.normalizedX,
    required this.normalizedY,
    required this.strokeNumber,
  });

  factory CustomNumberPosition.fromJson(Map<String, dynamic> json) {
    return CustomNumberPosition(
      x: (json['x'] ?? json['original_x'] ?? 0.0).toDouble(),
      y: (json['y'] ?? json['original_y'] ?? 0.0).toDouble(),
      normalizedX: (json['normalized_x'] ?? json['x'] ?? 0.0).toDouble(),
      normalizedY: (json['normalized_y'] ?? json['y'] ?? 0.0).toDouble(),
      strokeNumber: json['strokeNumber'] ?? 1,
    );
  }
}

