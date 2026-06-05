class Exercise {
  final String exerciseId;
  final String level;
  final String exerciseType;
  final String? targetLabel;
  final String? targetWord;
  final String? audioPath;
  final String instruction;

  Exercise({
    required this.exerciseId,
    required this.level,
    required this.exerciseType,
    this.targetLabel,
    this.targetWord,
    this.audioPath,
    required this.instruction,
  });

  factory Exercise.fromJson(Map<String, dynamic> json) {
    return Exercise(
      exerciseId: json['exercise_id'],
      level: json['level'],
      exerciseType: json['exercise_type'],
      targetLabel: json['target_label'],
      targetWord: json['target_word'],
      audioPath: json['audio_path'],
      instruction: json['instruction'],
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'exercise_id': exerciseId,
      'level': level,
      'exercise_type': exerciseType,
      'target_label': targetLabel,
      'target_word': targetWord,
      'audio_path': audioPath,
      'instruction': instruction,
    };
  }
}