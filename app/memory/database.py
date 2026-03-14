import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv("config/.env")

DATABASE_URL = "postgresql://codesentinel_user:codesentinel_pass@localhost/codesentinel"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

def init_db():
    with engine.connect() as conn:
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS review_memory (
                id SERIAL PRIMARY KEY,
                developer VARCHAR(255) NOT NULL,
                repo VARCHAR(255) NOT NULL,
                suggestion TEXT NOT NULL,
                embedding vector(384),
                accepted BOOLEAN DEFAULT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """))
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS developer_profiles (
                id SERIAL PRIMARY KEY,
                developer VARCHAR(255) UNIQUE NOT NULL,
                total_reviews INTEGER DEFAULT 0,
                accepted_suggestions INTEGER DEFAULT 0,
                common_issues TEXT[],
                skill_level VARCHAR(50) DEFAULT 'intermediate',
                last_review TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """))
        conn.commit()
    print("Database initialized successfully!")

if __name__ == "__main__":
    init_db()
