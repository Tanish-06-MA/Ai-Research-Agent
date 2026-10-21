import sqlite3
import os


DB_PATH = "research_history.db"


def get_connection():
    """Get a connection to the SQLite database."""
    return sqlite3.connect(DB_PATH)


def init_db():
    """
    Initialize the database and create the research_history table if needed.
    """
    try:
        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS research_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                query TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                report TEXT NOT NULL,
                sources TEXT,
                pdf_path TEXT
            )
        """)
        connection.commit()
        connection.close()
    except Exception as e:
        print(f"[ERROR] Database initialization failed: {e}")


def save_research(query, timestamp, report, sources, pdf_path):
    """
    Save a research result to the database.

    Args:
        query:     The user's original query.
        timestamp: ISO format timestamp.
        report:    The generated research report.
        sources:   String representation of sources list.
        pdf_path:  Path to the generated PDF file.
    """
    try:
        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute(
            """
            INSERT INTO research_history
            (query, timestamp, report, sources, pdf_path)
            VALUES (?, ?, ?, ?, ?)
        """,
            (query, timestamp, report, sources, pdf_path),
        )

        connection.commit()
        connection.close()
    except Exception as e:
        print(f"[ERROR] Failed to save research history: {e}")


def get_all_research():
    """
    Retrieve all research history entries, most recent first.

    Returns a list of tuples: (id, query, timestamp, pdf_path).
    """
    try:
        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute("""
            SELECT id, query, timestamp, pdf_path
            FROM research_history
            ORDER BY id DESC
        """)

        rows = cursor.fetchall()
        connection.close()
        return rows
    except Exception as e:
        print(f"[ERROR] Failed to retrieve research history: {e}")
        return []


def check_cache(query: str):
    """
    Check if a report already exists for the trimmed, case-insensitive query.
    Returns a tuple (report, sources, pdf_path) or None.
    """
    try:
        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute("""
            SELECT report, sources, pdf_path
            FROM research_history
            WHERE LOWER(TRIM(query)) = LOWER(TRIM(?))
            ORDER BY id DESC
            LIMIT 1
        """, (query,))

        row = cursor.fetchone()
        connection.close()
        return row
    except Exception as e:
        print(f"[ERROR] Cache check failed: {e}")
        return None

