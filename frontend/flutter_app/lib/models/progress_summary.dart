
class LetterProgress {
  final String targetLabel;
  final int attempts;
  final int correct;
  final double averageConfidence;

  LetterProgress({
    required this.targetLabel,
    required this.attempts,
    required this.correct,
    required this.averageConfidence,
  });

  factory LetterProgress.fromJson(Map<String, dynamic> json) {
    return LetterProgress(
      targetLabel: json['target_label'],
      attempts: json['attempts'] ?? 0,
      correct: json['correct'] ?? 0,
      averageConfidence: (json['average_confidence'] ?? 0).toDouble(),
    );
  }
}


class ProgressSummary {
  final String learnerId;
  final int totalAttempts;
  final int correctAttempts;
  final double accuracy;
  final double averageConfidence;
  final List<LetterProgress> byLetter;

  ProgressSummary({
    required this.learnerId,
    required this.totalAttempts,
    required this.correctAttempts,
    required this.accuracy,
    required this.averageConfidence,
    required this.byLetter,
  });

  factory ProgressSummary.fromJson(Map<String, dynamic> json) {
    final letterRows = json['by_letter'] as List<dynamic>;

    return ProgressSummary(
      learnerId: json['learner_id'],
      totalAttempts: json['total_attempts'] ?? 0,
      correctAttempts: json['correct_attempts'] ?? 0,
      accuracy: (json['accuracy'] ?? 0).toDouble(),
      averageConfidence: (json['average_confidence'] ?? 0).toDouble(),
      byLetter: letterRows
          .map((row) => LetterProgress.fromJson(row))
          .toList(),
    );
  }
}