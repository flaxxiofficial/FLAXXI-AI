import os
import sqlite3

DATABASE = os.getenv("DATABASE_PATH","flaxxi.db")


def initialize_memory():

    with sqlite3.connect(DATABASE) as db:

        db.execute("""
        CREATE TABLE IF NOT EXISTS chats(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            role TEXT NOT NULL,
            message TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)


def save_message(user,role,message):

    with sqlite3.connect(DATABASE) as db:

        db.execute(
            """
            INSERT INTO chats(user_id,role,message)
            VALUES(?,?,?)
            """,
            (user,role,message)
        )


def get_history(user,limit=30):

    with sqlite3.connect(DATABASE) as db:

        rows = db.execute(
            """
            SELECT role,message
            FROM chats
            WHERE user_id=?
            ORDER BY id DESC
            LIMIT ?
            """,
            (user,limit)
        ).fetchall()

    rows.reverse()

    return [
        {"role":role,"content":message}
        for role,message in rows
    ]


def clear_history(user):

    with sqlite3.connect(DATABASE) as db:

        db.execute(
            "DELETE FROM chats WHERE user_id=?",
            (user,)
        )
