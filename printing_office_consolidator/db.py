import json
import sqlite3
from flask import current_app, g


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(current_app.config["DATABASE"])
        g.db.row_factory = sqlite3.Row
    return g.db


def init_db(app):
    with app.app_context():
        db = get_db()
        db.execute("""
            CREATE TABLE IF NOT EXISTS merge_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                departments INTEGER NOT NULL,
                jobs INTEGER NOT NULL,
                result_json TEXT NOT NULL
            )
        """)
        db.commit()
        @app.teardown_appcontext
        def close_db(exception=None):
            db = g.pop("db", None)
            if db is not None:
                db.close()


def save_result(result):
    db = get_db()
    report = result["report"]
    cursor = db.execute(
        "INSERT INTO merge_history (departments, jobs, result_json) VALUES (?, ?, ?)",
        (report["departments_received"], report["jobs_received"],
         json.dumps(result))
    )
    db.commit()
    return cursor.lastrowid


def get_history(limit=20):
    rows = get_db().execute(
        "SELECT id, created_at, departments, jobs FROM merge_history ORDER BY id DESC LIMIT ?",
        (limit,)
    ).fetchall()
    return [dict(row) for row in rows]
