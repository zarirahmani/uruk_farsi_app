import sqlite3
from contextlib import asynccontextmanager
from datetime import datetime

from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware

from backend.app.schemas import WritingRequest, WritingResponse, HandwritingResponse, ExerciseCreate
from backend.app.model import HandwritingModel
from backend.app.database import init_db, log_prediction, DB_PATH
from backend.app.logging_config import logger
from backend.app.data_collection import save_handwriting_image, append_metadata

handwriting_model: HandwritingModel


@asynccontextmanager
async def lifespan(app: FastAPI):
    global handwriting_model
    init_db()
    logger.info("Database initialized.")
    handwriting_model = HandwritingModel()
    logger.info(
        f"Loaded model: {handwriting_model.model_name} "
        f"{handwriting_model.model_version}"
    )
    yield


app = FastAPI(
    title="Farsi Writing Tutor API",
    description="API for typed Farsi writing feedback and handwriting recognition.",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {
        "message": "Farsi Writing Tutor API is running",
        "version": "0.1.0"
    }


@app.post("/check-writing", response_model=WritingResponse)
def check_writing(request: WritingRequest):
    """
    Minimal typed-writing endpoint.
    Later you can connect this to an LLM or grammar model.
    """

    logger.info(f"Writing check request from learner={request.learner_id}")

    if request.target_text and request.text.strip() == request.target_text.strip():
        score = 100.0
        feedback = "Excellent. Your sentence matches the target."
        corrected_text = request.text
    else:
        score = 75.0
        feedback = "Good attempt. Check spelling, spacing, or grammar."
        corrected_text = request.target_text or request.text

    return WritingResponse(
        original_text=request.text,
        corrected_text=corrected_text,
        score=score,
        feedback=feedback
    )


@app.post("/check-handwriting", response_model=HandwritingResponse)
async def check_handwriting(
    file: UploadFile = File(...),
    target_label: str = Form(...),
    learner_id: str = Form("anonymous"),
    exercise_id: str = Form("unknown_exercise")
):
    """
    Handwriting endpoint:
    - receives image from Streamlit
    - preprocesses image
    - predicts letter
    - compares prediction with target
    - logs prediction and model version
    """

    logger.info(
        f"Handwriting request | learner={learner_id} | "
        f"exercise={exercise_id} | target={target_label}"
        )

    image_bytes = await file.read()

    saved_image_path = save_handwriting_image(
        image_bytes=image_bytes,
        target_label=target_label,
        learner_id=learner_id,
        exercise_id=exercise_id,
    )

    predicted_label, confidence = handwriting_model.predict_from_bytes(image_bytes)
    confidence = round(confidence, 4)
    is_correct = predicted_label == target_label

    if is_correct:
        feedback = "Great work. Your handwriting matches the target letter."
    else:
        feedback = (
            f"This looks more like '{predicted_label}' than '{target_label}'. "
            "Try again and focus on the letter shape and dot placement."
        )

    log_prediction(
        learner_id=learner_id,
        exercise_id=exercise_id,
        target_label=target_label,
        predicted_label=predicted_label,
        confidence=confidence,
        is_correct=is_correct,
        model_name=handwriting_model.model_name,
        model_version=handwriting_model.model_version
    )
    append_metadata({
        "image_path": saved_image_path,
        "target_label": target_label,
        "predicted_label": predicted_label,
        "learner_id": learner_id,
        "exercise_id": exercise_id,
        "confidence": confidence,
        "is_correct": is_correct,
        "model_name": handwriting_model.model_name,
        "model_version": handwriting_model.model_version,
        "timestamp": datetime.utcnow().isoformat(),
    })
    
    logger.info(f"Saved handwriting image to {saved_image_path}"
                )

    return HandwritingResponse(
        target_label=target_label,
        predicted_label=predicted_label,
        confidence=confidence,
        is_correct=is_correct,
        feedback=feedback,
        model_name=handwriting_model.model_name,
        model_version=handwriting_model.model_version
    )


@app.get("/exercises")
def get_exercises():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("""
    SELECT *
    FROM exercises
    WHERE is_active = 1
    ORDER BY level, exercise_id
    """)

    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()

    return {"exercises": rows}


@app.get("/exercises/{exercise_id}")
def get_exercise(exercise_id: str):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM exercises WHERE exercise_id = ?",
        (exercise_id,),
    )

    row = cursor.fetchone()
    conn.close()

    if row is None:
        raise HTTPException(status_code=404, detail="Exercise not found")

    return dict(row)


@app.post("/exercises")
def create_exercise(exercise: ExerciseCreate):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
    INSERT OR REPLACE INTO exercises (
        exercise_id,
        level,
        exercise_type,
        target_label,
        target_word,
        audio_path,
        instruction,
        is_active,
        created_at
    )
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        exercise.exercise_id,
        exercise.level,
        exercise.exercise_type,
        exercise.target_label,
        exercise.target_word,
        exercise.audio_path,
        exercise.instruction,
        1,
        datetime.utcnow().isoformat(),
    ))

    conn.commit()
    conn.close()

    return {"message": "Exercise saved", "exercise_id": exercise.exercise_id}


@app.delete("/exercises/{exercise_id}")
def delete_exercise(exercise_id: str):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute(
        "UPDATE exercises SET is_active = 0 WHERE exercise_id = ?",
        (exercise_id,),
    )

    conn.commit()
    conn.close()

    return {"message": "Exercise deactivated"}

@app.get("/learner/{learner_id}/progress")
def get_learner_progress(learner_id: str):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("""
    SELECT
        COUNT(*) AS total_attempts,
        SUM(is_correct) AS correct_attempts,
        AVG(confidence) AS average_confidence
    FROM predictions
    WHERE learner_id = ?
    """, (learner_id,))

    summary = dict(cursor.fetchone())

    cursor.execute("""
    SELECT
        target_label,
        COUNT(*) AS attempts,
        SUM(is_correct) AS correct,
        AVG(confidence) AS average_confidence
    FROM predictions
    WHERE learner_id = ?
    GROUP BY target_label
    ORDER BY target_label
    """, (learner_id,))

    by_letter = [dict(row) for row in cursor.fetchall()]
    conn.close()

    total = summary["total_attempts"] or 0
    correct = summary["correct_attempts"] or 0

    accuracy = correct / total if total else 0

    return {
        "learner_id": learner_id,
        "total_attempts": total,
        "correct_attempts": correct,
        "accuracy": accuracy,
        "average_confidence": summary["average_confidence"] or 0,
        "by_letter": by_letter,
    }