import 'dart:convert';
import 'dart:typed_data';

import 'package:http/http.dart' as http;

import '../models/exercise.dart';
import '../models/handwriting.dart';
import '../models/progress_summary.dart';

class ApiService {
  // For Flutter Web / macOS / iOS simulator:
  static const String baseUrl = 'http://127.0.0.1:8000';

  // For Android emulator, use this instead:
  // static const String baseUrl = 'http://10.0.2.2:8000';

  Future<bool> checkBackendHealth() async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/'),
      );

      return response.statusCode == 200;
    } catch (_) {
      return false;
    }
  }

  Future<HandwritingResult> checkHandwriting({
    required Uint8List imageBytes,
    required String targetLabel,
    required String learnerId,
    required String exerciseId,
  }) async {
    final uri = Uri.parse('$baseUrl/check-handwriting');

    final request = http.MultipartRequest('POST', uri);

    request.fields['target_label'] = targetLabel;
    request.fields['learner_id'] = learnerId;
    request.fields['exercise_id'] = exerciseId;

    request.files.add(
      http.MultipartFile.fromBytes(
        'file',
        imageBytes,
        filename: 'handwriting.png',
      ),
    );

    final streamedResponse = await request.send();
    final response = await http.Response.fromStream(streamedResponse);

    if (response.statusCode != 200) {
      throw Exception(
        'Backend error: ${response.statusCode} ${response.body}',
      );
    }

    final jsonData = jsonDecode(response.body);
    return HandwritingResult.fromJson(jsonData);
  }

  Future<List<Exercise>> getExercises() async {
    final response = await http.get(
      Uri.parse('$baseUrl/exercises'),
    );

    if (response.statusCode != 200) {
      throw Exception('Failed to load exercises: ${response.body}');
    }

    final data = jsonDecode(response.body);
    final rows = data['exercises'] as List<dynamic>;

    return rows.map((row) => Exercise.fromJson(row)).toList();
  }

  Future<Exercise> getExercise(String exerciseId) async {
    final response = await http.get(
      Uri.parse('$baseUrl/exercises/$exerciseId'),
    );

    if (response.statusCode != 200) {
      throw Exception('Failed to load exercise: ${response.body}');
    }

    final data = jsonDecode(response.body);
    return Exercise.fromJson(data);
  }

  Future<void> createExercise(Exercise exercise) async {
    final response = await http.post(
      Uri.parse('$baseUrl/exercises'),
      headers: {
        'Content-Type': 'application/json',
      },
      body: jsonEncode(exercise.toJson()),
    );

    if (response.statusCode != 200) {
      throw Exception('Failed to create exercise: ${response.body}');
    }
  }

  Future<void> deleteExercise(String exerciseId) async {
    final response = await http.delete(
      Uri.parse('$baseUrl/exercises/$exerciseId'),
    );

    if (response.statusCode != 200) {
      throw Exception('Failed to delete exercise: ${response.body}');
    }
  }

  Future<ProgressSummary> getLearnerProgress(String learnerId) async {
    final response = await http.get(
      Uri.parse('$baseUrl/learner/$learnerId/progress'),
    );

    if (response.statusCode != 200) {
      throw Exception('Failed to load progress: ${response.body}');
    }

    final data = jsonDecode(response.body);
    return ProgressSummary.fromJson(data);
  }
}