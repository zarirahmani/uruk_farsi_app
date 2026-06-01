import 'dart:typed_data';
import 'dart:convert';

import 'package:http/http.dart' as http;

import '../models/handwriting.dart';

class ApiService {
  // Use 10.0.2.2 for Android emulator.
  // static const String baseUrl = 'http://10.0.2.2:8000';
  // Use 127.0.0.1 for iOS simulator or desktop.
  static const String baseUrl = 'http://127.0.0.1:8000';

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
      throw Exception('Backend error: ${response.statusCode} ${response.body}');
    }

    final jsonData = jsonDecode(response.body);
    return HandwritingResult.fromJson(jsonData);
  }
}

