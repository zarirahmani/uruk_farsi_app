import sqlite3
from datetime import datetime, UTC

from database import DB_PATH, init_db


EXERCISES = [
    ("ex_001", "A1", "letter", "ا", "آب", "", "Listen and draw the letter ا"),
    ("ex_002", "A1", "letter", "ب", "بابا", "", "Listen and draw the letter ب"),
    ("ex_003", "A1", "letter", "پ", "پدر", "", "Listen and draw the letter پ"),
    ("ex_004", "A1", "letter", "ت", "توپ", "", "Listen and draw the letter ت"),
    ("ex_005", "A1", "letter", "ن", "نان", "", "Listen and draw the letter ن"),
    ("ex_006", "A1", "letter", "م", "مادر", "", "Listen and draw the letter م"),
]


def main():
    init_db()

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    for row in EXERCISES:
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
        """, (*row, 1, datetime.now(UTC).isoformat()))

    conn.commit()
    conn.close()

    print("Seeded exercises.")


if __name__ == "__main__":
    main()