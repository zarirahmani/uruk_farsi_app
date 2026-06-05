


from pydantic import BaseModel
from typing import Optional


class WritingRequest(BaseModel):
    text: str
    target_text: Optional[str] = None
    learner_id: Optional[str] = "anonymous"


class WritingResponse(BaseModel):
    original_text: str
    corrected_text: str
    score: float
    feedback: str


class HandwritingResponse(BaseModel):
    target_label: str
    predicted_label: str
    confidence: float
    is_correct: bool
    feedback: str
    model_name: str
    model_version: str


class ExerciseCreate(BaseModel):
    exercise_id: str
    level: str
    exercise_type: str
    target_label: Optional[str] = None
    target_word: Optional[str] = None
    audio_path: Optional[str] = None
    instruction: str


class ExerciseResponse(BaseModel):
    exercise_id: str
    level: str
    exercise_type: str
    target_label: Optional[str]
    target_word: Optional[str]
    audio_path: Optional[str]
    instruction: str
    is_active: int