
from fastapi.testclient import TestClient
from backend.app.main import app
from io import BytesIO
from PIL import Image


client = TestClient(app)


def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()


def test_check_writing():
    response = client.post(
        "/check-writing",
        json={
            "text": "من به مدرسه رفتم.",
            "target_text": "من به مدرسه رفتم.",
            "learner_id": "test_user"
        }
    )

    assert response.status_code == 200
    data = response.json()
    assert data["score"] == 100.0


def test_check_handwriting():
    image = Image.new("RGB", (64, 64), color="white")
    buffer = BytesIO()
    image.save(buffer, format="PNG")
    buffer.seek(0)

    response = client.post(
        "/check-handwriting",
        files={"file": ("test.png", buffer, "image/png")},
        data={
            "target_label": "ب",
            "learner_id": "test_user",
            "exercise_id": "test_exercise"
        }
    )

    assert response.status_code == 200
    data = response.json()

    assert "predicted_label" in data
    assert "confidence" in data
    assert "model_version" in data