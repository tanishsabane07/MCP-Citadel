# backend/services/history_db.py
import sqlite3
import json
from datetime import datetime
from typing import Dict, Any

DB_PATH = "data/query_logs.db"  # can be an absolute path if you prefer


def init_db():
    """Initialize the database and table if not exists."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            query TEXT NOT NULL,
            classification TEXT,
            cvss_score REAL,
            explanation TEXT,
            remediation TEXT
        )
    """)
    conn.commit()
    conn.close()


def log_query(data: Dict[str, Any]):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    remediation_value = data.get("remediation")
    # Convert remediation list → multiline string safely
    if isinstance(remediation_value, list):
        remediation_value = "\n".join(map(str, remediation_value))
    elif remediation_value is None:
        remediation_value = ""

    explanation_value = data.get("explanation")
    if isinstance(explanation_value, list):
        explanation_value = "\n".join(map(str, explanation_value))
    elif explanation_value is None:
        explanation_value = ""

    c.execute("""
        INSERT INTO history (
            timestamp, query, classification, cvss_score, explanation, remediation
        ) VALUES (?, ?, ?, ?, ?, ?)
    """, (
        datetime.utcnow().isoformat(),
        data["query"],
        data.get("classification"),
        data.get("cvss_score"),
        explanation_value,
        remediation_value
    ))

    conn.commit()
    conn.close()


def fetch_history(limit: int = 50):
    """Fetch the last N queries from the database."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT * FROM history ORDER BY id DESC LIMIT ?", (limit,))
    rows = c.fetchall()
    conn.close()
    return rows
