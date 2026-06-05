import 'package:flutter/material.dart';

import '../models/exercise.dart';
import '../services/api.dart';

class AdminDashboardScreen extends StatefulWidget {
  const AdminDashboardScreen({super.key});

  @override
  State<AdminDashboardScreen> createState() => _AdminDashboardScreenState();
}

class _AdminDashboardScreenState extends State<AdminDashboardScreen> {
  final ApiService apiService = ApiService();

  final exerciseIdController = TextEditingController();
  final targetLabelController = TextEditingController();
  final targetWordController = TextEditingController();
  final audioPathController = TextEditingController();
  final instructionController = TextEditingController();

  String level = 'A1';
  String exerciseType = 'letter';

  late Future<List<Exercise>> exercisesFuture;

  @override
  void initState() {
    super.initState();
    refreshExercises();
  }

  void refreshExercises() {
    exercisesFuture = apiService.getExercises();
  }

  Future<void> addExercise() async {
    String? nullable(String s) => s.isEmpty ? null : s;

    final exercise = Exercise(
      exerciseId: exerciseIdController.text.trim(),
      level: level,
      exerciseType: exerciseType,
      targetLabel: nullable(targetLabelController.text.trim()),
      targetWord: nullable(targetWordController.text.trim()),
      audioPath: nullable(audioPathController.text.trim()),
      instruction: instructionController.text.trim(),
    );

    await apiService.createExercise(exercise);

    exerciseIdController.clear();
    targetLabelController.clear();
    targetWordController.clear();
    audioPathController.clear();
    instructionController.clear();

    setState(() {
      refreshExercises();
    });
  }

  Future<void> deleteExercise(String exerciseId) async {
    await apiService.deleteExercise(exerciseId);

    setState(() {
      refreshExercises();
    });
  }

  @override
  void dispose() {
    exerciseIdController.dispose();
    targetLabelController.dispose();
    targetWordController.dispose();
    audioPathController.dispose();
    instructionController.dispose();
    super.dispose();
  }

  Widget textField(String label, TextEditingController controller) {
    return TextField(
      controller: controller,
      decoration: InputDecoration(labelText: label),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Admin Dashboard'),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(20),
        child: Column(
          children: [
            const Text(
              'Add New Exercise',
              style: TextStyle(fontSize: 22, fontWeight: FontWeight.bold),
            ),

            textField('Exercise ID', exerciseIdController),

            DropdownButton<String>(
              value: level,
              items: ['A1', 'A2', 'B1'].map((item) {
                return DropdownMenuItem(
                  value: item,
                  child: Text(item),
                );
              }).toList(),
              onChanged: (value) {
                if (value != null) {
                  setState(() {
                    level = value;
                  });
                }
              },
            ),

            DropdownButton<String>(
              value: exerciseType,
              items: ['letter', 'word', 'sentence'].map((item) {
                return DropdownMenuItem(
                  value: item,
                  child: Text(item),
                );
              }).toList(),
              onChanged: (value) {
                if (value != null) {
                  setState(() {
                    exerciseType = value;
                  });
                }
              },
            ),

            textField('Target Letter', targetLabelController),
            textField('Target Word', targetWordController),
            textField('Audio Path', audioPathController),
            textField('Instruction', instructionController),

            const SizedBox(height: 16),

            ElevatedButton(
              onPressed: addExercise,
              child: const Text('Save Exercise'),
            ),

            const Divider(height: 40),

            const Text(
              'Existing Exercises',
              style: TextStyle(fontSize: 22, fontWeight: FontWeight.bold),
            ),

            FutureBuilder<List<Exercise>>(
              future: exercisesFuture,
              builder: (context, snapshot) {
                if (snapshot.connectionState == ConnectionState.waiting) {
                  return const CircularProgressIndicator();
                }

                if (snapshot.hasError) {
                  return Text('Error: ${snapshot.error}');
                }

                final exercises = snapshot.data ?? [];

                return Column(
                  children: exercises.map((exercise) {
                    return Card(
                      child: ListTile(
                        title: Text(
                          '${exercise.exerciseId} — ${exercise.targetLabel ?? exercise.targetWord ?? ""}',
                        ),
                        subtitle: Text(exercise.instruction),
                        trailing: IconButton(
                          icon: const Icon(Icons.delete),
                          onPressed: () => deleteExercise(exercise.exerciseId),
                        ),
                      ),
                    );
                  }).toList(),
                );
              },
            ),
          ],
        ),
      ),
    );
  }
}