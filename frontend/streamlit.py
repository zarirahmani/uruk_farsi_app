import streamlit as st
import requests
from PIL import Image
from io import BytesIO
from streamlit_drawable_canvas import st_canvas


API_URL = "http://127.0.0.1:8000"


st.set_page_config(
    page_title="Farsi Writing Tutor",
    layout="centered"
)

st.title("Farsi Writing Tutor")
st.write("Listen to the Farsi prompt, draw the letter, and receive feedback.")


st.header("1. Typed writing practice")

target_text = st.text_input("Target sentence", value="من به مدرسه رفتم.")
user_text = st.text_area("Write the Farsi sentence here")

if st.button("Check typed writing"):
    response = requests.post(
        f"{API_URL}/check-writing",
        json={
            "text": user_text,
            "target_text": target_text,
            "learner_id": "demo_user"
        }
    )

    if response.status_code == 200:
        result = response.json()
        st.metric("Score", result["score"])
        st.write("Feedback:", result["feedback"])
        st.write("Corrected text:", result["corrected_text"])
    else:
        st.error("Backend error while checking writing.")


st.divider()


st.header("2. Handwriting practice")

target_label = st.selectbox(
    "Choose the letter you heard",
    ["ا", "ب", "پ", "ت", "ن", "م"]
)

st.write(f"Target letter: **{target_label}**")

audio_map = {
    "آ": "frontend/audio/ab.wav",
    "ب": "frontend/audio/baba.wav",
    "ن": "frontend/audio/nan.wav",
}

audio_file = audio_map.get(target_label)

if audio_file:
    st.audio(audio_file)
else:
    st.warning("Audio file not found for this exercise.")

canvas_result = st_canvas(
    fill_color="rgba(255, 255, 255, 0)",
    stroke_width=8,
    stroke_color="#000000",
    background_color="#FFFFFF",
    height=300,
    width=300,
    drawing_mode="freedraw",
    key="canvas",
)

if st.button("Check handwriting"):
    if canvas_result.image_data is not None:
        image = Image.fromarray(canvas_result.image_data.astype("uint8"))
        buffer = BytesIO()
        image.save(buffer, format="PNG")
        buffer.seek(0)

        files = {
            "file": ("handwriting.png", buffer, "image/png")
        }

        data = {
            "target_label": target_label,
            "learner_id": "demo_user",
            "exercise_id": f"letter_{target_label}"
        }

        response = requests.post(
            f"{API_URL}/check-handwriting",
            files=files,
            data=data
        )

        if response.status_code == 200:
            result = response.json()

            st.metric("Confidence", result["confidence"])
            st.write("Target:", result["target_label"])
            st.write("Predicted:", result["predicted_label"])
            st.write("Correct:", result["is_correct"])
            st.write("Feedback:", result["feedback"])
            st.caption(
                f"Model: {result['model_name']} | "
                f"Version: {result['model_version']}"
            )
        else:
            st.error("Backend error while checking handwriting.")
    else:
        st.warning("Please draw the letter first.")
