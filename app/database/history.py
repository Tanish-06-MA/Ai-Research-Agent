import sqlite3
import os


DB_PATH = "research_history.db"


def get_connection():
    return sqlite3.connect(DB_PATH)


def init_db():
    connection = get_connection()
    cursor = connection.cursor()  # used to execute SQL commands

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


def save_research(query, timestamp, report, sources, pdf_path):
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


def get_all_research():
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
