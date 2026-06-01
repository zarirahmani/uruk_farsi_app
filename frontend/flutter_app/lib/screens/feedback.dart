import 'package:flutter/material.dart';
import '../models/handwriting.dart';

class FeedbackScreen extends StatelessWidget {
  final HandwritingResult result;

  const FeedbackScreen({
    super.key,
    required this.result,
  });

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Feedback'),
      ),
      body: Padding(
        padding: const EdgeInsets.all(24),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.center,
          children: [
            Icon(
              result.isCorrect ? Icons.check_circle : Icons.cancel,
              color: result.isCorrect ? Colors.green : Colors.red,
              size: 80,
            ),
            const SizedBox(height: 20),

            Text(
              result.isCorrect ? 'Correct!' : 'Try again',
              style: const TextStyle(fontSize: 28, fontWeight: FontWeight.bold),
            ),

            const SizedBox(height: 20),

            Text(
              result.feedback,
              textAlign: TextAlign.center,
              style: const TextStyle(fontSize: 18),
            ),

            const SizedBox(height: 30),

            Card(
              child: Padding(
                padding: const EdgeInsets.all(16),
                child: Column(
                  children: [
                    Text('Target: ${result.targetLabel}'),
                    Text('Predicted: ${result.predictedLabel}'),
                    Text('Confidence: ${result.confidence.toStringAsFixed(3)}'),
                    Text('Model: ${result.modelName}'),
                    Text('Version: ${result.modelVersion}'),
                  ],
                ),
              ),
            ),

            const Spacer(),

            ElevatedButton(
              onPressed: () {
                Navigator.pop(context);
              },
              child: const Text('Practice again'),
            ),
          ],
        ),
      ),
    );
  }
}