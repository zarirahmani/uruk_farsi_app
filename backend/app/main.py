from fastapi import FastAPI, UploadFile, File, Form
from backend.app.schemas import WritingRequest, WritingResponse, HandwritingResponse
from backend.app.preprocessing import preprocess_image
from backend.app.model import HandwritingModel
from backend.app.database import init_db, log_prediction
from backend.app.logging_config import logger


app = FastAPI(
    title="Farsi Writing Tutor API",
    description="API for typed Farsi writing feedback and handwriting recognition.",
    version="0.1.0"
)

handwriting_model = HandwritingModel()


@app.on_event("startup")
def startup_event():
    init_db()
    logger.info("Database initialized.")
    logger.info(
        f"Loaded model: {handwriting_model.model_name} "
        f"{handwriting_model.model_version}"
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
    image_array = preprocess_image(image_bytes)

    predicted_label, confidence = handwriting_model.predict(image_array)
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

    logger.info(
        f"Prediction logged | target={target_label} | "
        f"predicted={predicted_label} | correct={is_correct}"
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