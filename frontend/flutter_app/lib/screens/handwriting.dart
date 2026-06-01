import 'package:flutter/material.dart';

import '../services/api.dart';
import '../widgets/drawing.dart';
import 'feedback.dart';

class HandwritingScreen extends StatefulWidget {
  const HandwritingScreen({super.key});

  @override
  State<HandwritingScreen> createState() => _HandwritingScreenState();
}

class _HandwritingScreenState extends State<HandwritingScreen> {
  final GlobalKey repaintKey = GlobalKey();
  final GlobalKey<DrawingCanvasState> canvasKey = GlobalKey<DrawingCanvasState>();

  final ApiService apiService = ApiService();

  String targetLabel = 'ب';
  bool isLoading = false;
  bool hasDrawing = false;

  final List<String> labels = ['آ', 'ا', 'ب', 'پ', 'ت', 'ن', 'م'];

  Future<void> submitDrawing() async {
    if (!hasDrawing) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Please draw the letter first.')),
      );
      return;
    }

    setState(() {
      isLoading = true;
    });

    try {
      final imageBytes = await canvasKey.currentState!.exportToPng();

      final result = await apiService.checkHandwriting(
        imageBytes: imageBytes,
        targetLabel: targetLabel,
        learnerId: 'demo_user',
        exerciseId: 'letter_$targetLabel',
      );

      if (!mounted) return;

      Navigator.push(
        context,
        MaterialPageRoute(
          builder: (_) => FeedbackScreen(result: result),
        ),
      );
    } catch (error) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Error: $error')),
      );
    } finally {
      if (mounted) {
        setState(() {
          isLoading = false;
        });
      }
    }
  }

  void clearCanvas() {
    canvasKey.currentState?.clear();
    setState(() {
      hasDrawing = false;
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Handwriting Practice'),
      ),
      body: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          children: [
            const Text(
              'Choose the letter you hear, then draw it.',
              style: TextStyle(fontSize: 18),
            ),
            const SizedBox(height: 16),

            DropdownButton<String>(
              value: targetLabel,
              items: labels.map((label) {
                return DropdownMenuItem(
                  value: label,
                  child: Text(
                    label,
                    style: const TextStyle(fontSize: 28),
                  ),
                );
              }).toList(),
              onChanged: (value) {
                if (value != null) {
                  setState(() {
                    targetLabel = value;
                  });
                }
              },
            ),

            const SizedBox(height: 16),

            Text(
              'Draw: $targetLabel',
              style: const TextStyle(fontSize: 32),
            ),

            const SizedBox(height: 16),

            DrawingCanvas(
              key: canvasKey,
              repaintKey: repaintKey,
              onChanged: (points) {
                setState(() {
                  hasDrawing = points.whereType<Offset>().isNotEmpty;
                });
              },
            ),

            const SizedBox(height: 16),

            Row(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                OutlinedButton(
                  onPressed: clearCanvas,
                  child: const Text('Clear'),
                ),
                const SizedBox(width: 12),
                ElevatedButton(
                  onPressed: isLoading ? null : submitDrawing,
                  child: isLoading
                      ? const CircularProgressIndicator()
                      : const Text('Check'),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }
}

