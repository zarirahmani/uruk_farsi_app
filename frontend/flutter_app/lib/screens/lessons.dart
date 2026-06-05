import 'package:flutter/material.dart';

import '../models/exercise.dart';
import '../services/api.dart';
import 'handwriting.dart';

class LessonsScreen extends StatefulWidget {
  const LessonsScreen({super.key});

  @override
  State<LessonsScreen> createState() => _LessonsScreenState();
}

class _LessonsScreenState extends State<LessonsScreen> {
  final ApiService apiService = ApiService();

  late Future<List<Exercise>> exercisesFuture;

  @override
  void initState() {
    super.initState();
    exercisesFuture = apiService.getExercises();
  }

  void openExercise(Exercise exercise) {
    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (_) => HandwritingScreen(exercise: exercise),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Lessons'),
      ),
      body: FutureBuilder<List<Exercise>>(
        future: exercisesFuture,
        builder: (context, snapshot) {
          if (snapshot.connectionState == ConnectionState.waiting) {
            return const Center(child: CircularProgressIndicator());
          }

          if (snapshot.hasError) {
            return Center(
              child: Text('Error: ${snapshot.error}'),
            );
          }

          final exercises = snapshot.data ?? [];

          if (exercises.isEmpty) {
            return const Center(
              child: Text('No exercises yet. Add some in Admin Dashboard.'),
            );
          }

          return ListView.builder(
            itemCount: exercises.length,
            itemBuilder: (context, index) {
              final exercise = exercises[index];

              return Card(
                margin: const EdgeInsets.all(12),
                child: ListTile(
                  title: Text(
                    exercise.targetLabel ?? exercise.targetWord ?? exercise.exerciseId,
                    style: const TextStyle(fontSize: 24),
                  ),
                  subtitle: Text(
                    '${exercise.level} • ${exercise.instruction}',
                  ),
                  trailing: const Icon(Icons.arrow_forward_ios),
                  onTap: () => openExercise(exercise),
                ),
              );
            },
          );
        },
      ),
    );
  }
}