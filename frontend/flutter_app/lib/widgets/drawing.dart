// import 'dart:typed_data';
// import 'dart:ui' as ui;

// import 'package:flutter/material.dart';
//import 'package:flutter/rendering.dart';

// class DrawingCanvas extends StatefulWidget {
//  final GlobalKey repaintKey;
//  final ValueChanged<List<Offset?>> onChanged;

//  const DrawingCanvas({
//    super.key,
//    required this.repaintKey,
//    required this.onChanged,
//  });

//  @override
//  State<DrawingCanvas> createState() => DrawingCanvasState();
//}

//class DrawingCanvasState extends State<DrawingCanvas> {
//  final List<Offset?> points = [];

//  void clear() {
//    setState(() {
//      points.clear();
//    });

//    widget.onChanged(points);
//  }

//  Future<Uint8List> exportToPng() async {
//    final boundary = widget.repaintKey.currentContext!.findRenderObject()
//        as RenderRepaintBoundary;

//    final image = await boundary.toImage(pixelRatio: 3.0);
//    final byteData = await image.toByteData(format: ui.ImageByteFormat.png);

//    return byteData!.buffer.asUint8List();
//  }

//  @override
//  Widget build(BuildContext context) {
//    return RepaintBoundary(
//      key: widget.repaintKey,
//      child: Container(
//        width: 300,
//        height: 300,
//        decoration: BoxDecoration(
//          color: Colors.white,
//          border: Border.all(color: Colors.black26),
//          borderRadius: BorderRadius.circular(12),
//        ),
//        child: GestureDetector(
//          behavior: HitTestBehavior.opaque,
//          onPanStart: (details) {
//            final box = context.findRenderObject() as RenderBox;
//            final point = box.globalToLocal(details.globalPosition);

//            setState(() {
//              points.add(point);
//            });

//            widget.onChanged(points);
//          },
//          onPanUpdate: (details) {
//            final box = context.findRenderObject() as RenderBox;
//            final point = box.globalToLocal(details.globalPosition);

//            setState(() {
//              points.add(point);
//            });

//            widget.onChanged(points);
//          },
//          onPanUpdate: (details) {
//            final box = context.findRenderObject() as RenderBox;
//            final point = box.globalToLocal(details.globalPosition);

//            setState(() {
//              points.add(point);
//            });

//            widget.onChanged(points);
//          },
//          onPanEnd: (_) {
//            setState(() {
//              points.add(null);
//            });

//            widget.onChanged(points);
//          },
//          child: CustomPaint(
//            painter: _DrawingPainter(points),
//            child: const SizedBox(
//              width: 300,
//              height: 300,
//            ),
//          ),
//        ),
//      ),
//    );
//  }
//}

//class _DrawingPainter extends CustomPainter {
//  final List<Offset?> points;

//  _DrawingPainter(this.points);

//  @override
//  void paint(Canvas canvas, Size size) {
//    final paint = Paint()
//      ..color = Colors.black
//      ..strokeWidth = 8
//      ..strokeCap = StrokeCap.round;

//    for (int i = 0; i < points.length - 1; i++) {
//      final current = points[i];
//      final next = points[i + 1];

//      if (current != null && next != null) {
//        canvas.drawLine(current, next, paint);
//      }
//    }
//  }

//  @override
//  bool shouldRepaint(_DrawingPainter oldDelegate) {
//    return oldDelegate.points != points;
//  }
//}

import 'dart:typed_data';
import 'dart:ui' as ui;

import 'package:flutter/material.dart';
import 'package:flutter/rendering.dart';

class DrawingCanvas extends StatefulWidget {
  final GlobalKey repaintKey;
  final ValueChanged<List<Offset?>> onChanged;

  const DrawingCanvas({
    super.key,
    required this.repaintKey,
    required this.onChanged,
  });

  @override
  State<DrawingCanvas> createState() => DrawingCanvasState();
}

class DrawingCanvasState extends State<DrawingCanvas> {
  final List<Offset?> points = [];

  void clear() {
    setState(() {
      points.clear();
    });

    widget.onChanged(points);
  }

  Future<Uint8List> exportToPng() async {
    final boundary = widget.repaintKey.currentContext!.findRenderObject()
        as RenderRepaintBoundary;

    final image = await boundary.toImage(pixelRatio: 3.0);
    final byteData = await image.toByteData(format: ui.ImageByteFormat.png);

    return byteData!.buffer.asUint8List();
  }

  void _addPoint(PointerEvent event) {
    final box = context.findRenderObject() as RenderBox;
    final point = box.globalToLocal(event.position);

    if (point.dx >= 0 &&
        point.dx <= 300 &&
        point.dy >= 0 &&
        point.dy <= 300) {
      setState(() {
        points.add(point);
      });

      widget.onChanged(points);
    }
  }

  @override
  Widget build(BuildContext context) {
    return RepaintBoundary(
      key: widget.repaintKey,
      child: MouseRegion(
        cursor: SystemMouseCursors.precise,
        child: Listener(
          onPointerDown: _addPoint,
          onPointerMove: _addPoint,
          onPointerUp: (_) {
            setState(() {
              points.add(null);
            });

            widget.onChanged(points);
          },
          child: Container(
            width: 300,
            height: 300,
            color: Colors.white,
            child: CustomPaint(
              painter: _DrawingPainter(points),
              child: const SizedBox(
                width: 300,
                height: 300,
              ),
            ),
          ),
        ),
      ),
    );
  }
}

class _DrawingPainter extends CustomPainter {
  final List<Offset?> points;

  _DrawingPainter(this.points);

  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()
      ..color = Colors.black
      ..strokeWidth = 8
      ..strokeCap = StrokeCap.round
      ..strokeJoin = StrokeJoin.round;

    for (int i = 0; i < points.length - 1; i++) {
      final current = points[i];
      final next = points[i + 1];

      if (current != null && next != null) {
        canvas.drawLine(current, next, paint);
      }
    }
  }

  @override
  bool shouldRepaint(_DrawingPainter oldDelegate) {
    return true;
  }
}