import os
from sentence_transformers import SentenceTransformer
from sqlalchemy import text
from app.memory.database import SessionLocal, engine
import numpy as np

model = SentenceTransformer('all-MiniLM-L6-v2')

def get_embedding(text_input: str) -> list:
    embedding = model.encode(text_input)
    return embedding.tolist()

def is_duplicate_suggestion(
    developer: str,
    suggestion: str,
    threshold: float = 0.85
) -> bool:
    try:
        embedding = get_embedding(suggestion)
        embedding_str = "[" + ",".join(map(str, embedding)) + "]"

        with engine.connect() as conn:
            result = conn.execute(text(f"""
                SELECT suggestion
                FROM review_memory
                WHERE developer = :developer
                AND 1 - (embedding <=> '{embedding_str}'::vector) > :threshold
                LIMIT 1
            """), {
                "developer": developer,
                "threshold": threshold
            })
            row = result.fetchone()
            return row is not None
    except Exception as e:
        print(f"Memory check error: {e}")
        return False

def save_suggestion(
    developer: str,
    repo: str,
    suggestion: str
) -> bool:
    try:
        if is_duplicate_suggestion(developer, suggestion):
            print(f"Skipping duplicate suggestion for {developer}")
            return False

        embedding = get_embedding(suggestion)
        embedding_str = "[" + ",".join(map(str, embedding)) + "]"

        with engine.connect() as conn:
            conn.execute(text(f"""
                INSERT INTO review_memory
                (developer, repo, suggestion, embedding)
                VALUES (:developer, :repo, :suggestion, '{embedding_str}'::vector)
            """), {
                "developer": developer,
                "repo": repo,
                "suggestion": suggestion
            })
            conn.commit()
        return True
    except Exception as e:
        print(f"Save suggestion error: {e}")
        return False

def get_developer_profile(developer: str) -> dict:
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT * FROM developer_profiles
            WHERE developer = :developer
        """), {"developer": developer})
        row = result.fetchone()

        if row:
            return {
                "developer": row.developer,
                "total_reviews": row.total_reviews,
                "accepted_suggestions": row.accepted_suggestions,
                "skill_level": row.skill_level
            }

        conn.execute(text("""
            INSERT INTO developer_profiles (developer)
            VALUES (:developer)
            ON CONFLICT (developer) DO NOTHING
        """), {"developer": developer})
        conn.commit()

        return {
            "developer": developer,
            "total_reviews": 0,
            "accepted_suggestions": 0,
            "skill_level": "intermediate"
        }

def update_developer_profile(developer: str) -> None:
    with engine.connect() as conn:
        conn.execute(text("""
            INSERT INTO developer_profiles (developer, total_reviews)
            VALUES (:developer, 1)
            ON CONFLICT (developer)
            DO UPDATE SET
                total_reviews = developer_profiles.total_reviews + 1,
                last_review = CURRENT_TIMESTAMP
        """), {"developer": developer})
        conn.commit()
