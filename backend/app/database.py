import sqlite3
from pathlib import Path
from datetime import datetime


DB_PATH = Path("data/predictions.db")
DB_PATH.parent.mkdir(exist_ok=True)


def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS predictions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        learner_id TEXT,
        exercise_id TEXT,
        target_label TEXT,
        predicted_label TEXT,
        confidence REAL,
        is_correct INTEGER,
        model_name TEXT,
        model_version TEXT,
        created_at TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS evaluation_metrics (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        model_name TEXT,
        model_version TEXT,
        metric_name TEXT,
        metric_value REAL,
        created_at TEXT
    )
    """)

    conn.commit()
    conn.close()


def log_prediction(
    learner_id: str,
    exercise_id: str,
    target_label: str,
    predicted_label: str,
    confidence: float,
    is_correct: bool,
    model_name: str,
    model_version: str,
):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO predictions (
        learner_id,
        exercise_id,
        target_label,
        predicted_label,
        confidence,
        is_correct,
        model_name,
        model_version,
        created_at
    )
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        learner_id,
        exercise_id,
        target_label,
        predicted_label,
        confidence,
        int(is_correct),
        model_name,
        model_version,
        datetime.utcnow().isoformat()
    ))

    conn.commit()
    conn.close()


def log_metric(model_name: str, model_version: str, metric_name: str, metric_value: float):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO evaluation_metrics (
        model_name,
        model_version,
        metric_name,
        metric_value,
        created_at
    )
    VALUES (?, ?, ?, ?, ?)
    """, (
        model_name,
        model_version,
        metric_name,
        metric_value,
        datetime.utcnow().isoformat()
    ))

    conn.commit()
    conn.close()