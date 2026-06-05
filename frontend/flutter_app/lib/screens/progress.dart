import 'package:flutter/material.dart';

import '../models/progress_summary.dart';
import '../services/api.dart';

class ProgressScreen extends StatefulWidget {
  const ProgressScreen({super.key});

  @override
  State<ProgressScreen> createState() => _ProgressScreenState();
}

class _ProgressScreenState extends State<ProgressScreen> {
  final ApiService apiService = ApiService();

  late Future<ProgressSummary> progressFuture;

  @override
  void initState() {
    super.initState();
    progressFuture = apiService.getLearnerProgress('demo_user');
  }

  String percent(double value) {
    return '${(value * 100).toStringAsFixed(1)}%';
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Progress'),
      ),
      body: FutureBuilder<ProgressSummary>(
        future: progressFuture,
        builder: (context, snapshot) {
          if (snapshot.connectionState == ConnectionState.waiting) {
            return const Center(child: CircularProgressIndicator());
          }

          if (snapshot.hasError) {
            return Center(child: Text('Error: ${snapshot.error}'));
          }

          final progress = snapshot.data!;

          return Padding(
            padding: const EdgeInsets.all(20),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Card(
                  child: ListTile(
                    title: const Text('Overall Accuracy'),
                    trailing: Text(
                      percent(progress.accuracy),
                      style: const TextStyle(
                        fontSize: 22,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ),
                ),

                Card(
                  child: ListTile(
                    title: const Text('Total Attempts'),
                    trailing: Text('${progress.totalAttempts}'),
                  ),
                ),

                Card(
                  child: ListTile(
                    title: const Text('Average Confidence'),
                    trailing: Text(progress.averageConfidence.toStringAsFixed(3)),
                  ),
                ),

                const SizedBox(height: 20),

                const Text(
                  'Progress by Letter',
                  style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
                ),

                const SizedBox(height: 12),

                Expanded(
                  child: ListView.builder(
                    itemCount: progress.byLetter.length,
                    itemBuilder: (context, index) {
                      final row = progress.byLetter[index];
                      final accuracy = row.attempts == 0
                          ? 0.0
                          : row.correct / row.attempts;

                      return Card(
                        child: ListTile(
                          leading: Text(
                            row.targetLabel,
                            style: const TextStyle(fontSize: 28),
                          ),
                          title: Text('Accuracy: ${percent(accuracy)}'),
                          subtitle: Text(
                            'Attempts: ${row.attempts} | Correct: ${row.correct}',
                          ),
                        ),
                      );
                    },
                  ),
                ),
              ],
            ),
          );
        },
      ),
    );
  }
}