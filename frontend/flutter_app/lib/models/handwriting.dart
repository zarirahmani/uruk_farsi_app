class HandwritingResult {
  final String targetLabel;
  final String predictedLabel;
  final double confidence;
  final bool isCorrect;
  final String feedback;
  final String modelName;
  final String modelVersion;

  HandwritingResult({
    required this.targetLabel,
    required this.predictedLabel,
    required this.confidence,
    required this.isCorrect,
    required this.feedback,
    required this.modelName,
    required this.modelVersion,
  });

  factory HandwritingResult.fromJson(Map<String, dynamic> json) {
    return HandwritingResult(
      targetLabel: json['target_label'],
      predictedLabel: json['predicted_label'],
      confidence: (json['confidence'] as num).toDouble(),
      isCorrect: json['is_correct'],
      feedback: json['feedback'],
      modelName: json['model_name'],
      modelVersion: json['model_version'],
    );
  }
}