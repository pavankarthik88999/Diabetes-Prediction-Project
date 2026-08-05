"""Database helpers for the Diabetes Prediction app (Neon PostgreSQL)."""
import os

import psycopg
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.environ.get("DATABASE_URL")


def get_connection():
    """Open a new connection to the Neon PostgreSQL database."""
    if not DATABASE_URL:
        raise RuntimeError("DATABASE_URL is not set. Check your .env file.")
    return psycopg.connect(DATABASE_URL)


def init_db():
    """Create the required tables if they do not already exist."""
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS users (
                    id            SERIAL PRIMARY KEY,
                    name          TEXT NOT NULL,
                    username      TEXT NOT NULL UNIQUE,
                    password_hash TEXT NOT NULL,
                    created_at    TIMESTAMPTZ NOT NULL DEFAULT NOW()
                );
                """
            )
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS predictions (
                    id             SERIAL PRIMARY KEY,
                    user_id        INTEGER NOT NULL REFERENCES users(id),
                    pregnancies    DOUBLE PRECISION NOT NULL,
                    glucose        DOUBLE PRECISION NOT NULL,
                    blood_pressure DOUBLE PRECISION NOT NULL,
                    skin_thickness DOUBLE PRECISION NOT NULL,
                    insulin        DOUBLE PRECISION NOT NULL,
                    bmi            DOUBLE PRECISION NOT NULL,
                    dpf            DOUBLE PRECISION NOT NULL,
                    age            DOUBLE PRECISION NOT NULL,
                    prediction     INTEGER NOT NULL,
                    result_text    TEXT NOT NULL,
                    created_at     TIMESTAMPTZ NOT NULL DEFAULT NOW()
                );
                """
            )
            cur.execute(
                "ALTER TABLE predictions "
                "ADD COLUMN IF NOT EXISTS probability DOUBLE PRECISION;"
            )
        conn.commit()
