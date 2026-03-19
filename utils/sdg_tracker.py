"""
ARIA — SDG 3 Impact Tracker
Simple SQLite-based counters for:
- Patients triaged fairly
- Bias cases flagged
"""

import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "database", "sdg_stats.db")


def _init_db():
    """Create the SDG stats table if it doesn't exist."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sdg_stats (
            key TEXT PRIMARY KEY,
            value INTEGER DEFAULT 0
        )
    """)
    # Initialize counters if they don't exist
    cursor.execute("INSERT OR IGNORE INTO sdg_stats (key, value) VALUES ('patients_triaged', 0)")
    cursor.execute("INSERT OR IGNORE INTO sdg_stats (key, value) VALUES ('bias_flagged', 0)")
    conn.commit()
    conn.close()


def get_stats() -> dict:
    """Get current SDG impact stats."""
    _init_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT key, value FROM sdg_stats")
    rows = cursor.fetchall()
    conn.close()
    return {row[0]: row[1] for row in rows}


def increment_triaged():
    """Increment the patients triaged counter."""
    _init_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("UPDATE sdg_stats SET value = value + 1 WHERE key = 'patients_triaged'")
    conn.commit()
    conn.close()


def increment_bias_flagged():
    """Increment the bias cases flagged counter."""
    _init_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("UPDATE sdg_stats SET value = value + 1 WHERE key = 'bias_flagged'")
    conn.commit()
    conn.close()
