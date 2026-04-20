import hashlib
import json
import os
import secrets
import sqlite3
from pathlib import Path

_DB_PATH: Path | None = None

DEFAULT_COLUMNS = json.dumps([
    {"id": "col-1", "title": "Intake", "cards": []},
    {"id": "col-2", "title": "Ready", "cards": []},
    {"id": "col-3", "title": "In Progress", "cards": []},
    {"id": "col-4", "title": "Review", "cards": []},
    {"id": "col-5", "title": "Done", "cards": []},
])

MVP_USERNAME = "user"
MVP_PASSWORD = "password"


def _hash_password(password: str, salt: str) -> str:
    return hashlib.sha256((salt + password).encode()).hexdigest()


def _resolve_db_path() -> Path:
    configured = os.getenv("PM_DB_PATH")
    if configured:
        return Path(configured)
    project_root = os.getenv("PROJECT_ROOT")
    if project_root:
        return Path(project_root) / "data" / "pm.db"
    return Path.cwd() / "data" / "pm.db"


def get_db_path() -> Path:
    global _DB_PATH
    if _DB_PATH is None:
        _DB_PATH = _resolve_db_path()
    return _DB_PATH


def set_db_path(path: Path) -> None:
    global _DB_PATH
    _DB_PATH = path


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(str(get_db_path()))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def init_db() -> None:
    db_path = get_db_path()
    db_path.parent.mkdir(parents=True, exist_ok=True)

    conn = get_connection()
    try:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                salt TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS boards (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL REFERENCES users(id),
                name TEXT NOT NULL DEFAULT 'Product Delivery Board',
                columns_json TEXT NOT NULL DEFAULT '[]'
            );
        """)
        # Seed MVP user if not present
        row = conn.execute(
            "SELECT id FROM users WHERE username = ?", (MVP_USERNAME,)
        ).fetchone()
        if row is None:
            salt = secrets.token_hex(16)
            pw_hash = _hash_password(MVP_PASSWORD, salt)
            conn.execute(
                "INSERT INTO users (username, password_hash, salt) VALUES (?, ?, ?)",
                (MVP_USERNAME, pw_hash, salt),
            )
            user_id = conn.execute(
                "SELECT id FROM users WHERE username = ?", (MVP_USERNAME,)
            ).fetchone()["id"]
            conn.execute(
                "INSERT INTO boards (user_id, columns_json) VALUES (?, ?)",
                (user_id, DEFAULT_COLUMNS),
            )
            conn.commit()
    finally:
        conn.close()


def verify_user(username: str, password: str) -> int | None:
    conn = get_connection()
    try:
        row = conn.execute(
            "SELECT id, password_hash, salt FROM users WHERE username = ?",
            (username,),
        ).fetchone()
        if row is None:
            return None
        if _hash_password(password, row["salt"]) != row["password_hash"]:
            return None
        return row["id"]
    finally:
        conn.close()


def get_board(user_id: int) -> dict | None:
    conn = get_connection()
    try:
        row = conn.execute(
            "SELECT id, name, columns_json FROM boards WHERE user_id = ?",
            (user_id,),
        ).fetchone()
        if row is None:
            return None
        return {
            "id": row["id"],
            "name": row["name"],
            "columns": json.loads(row["columns_json"]),
        }
    finally:
        conn.close()


def update_board(user_id: int, columns: list, name: str | None = None) -> dict | None:
    conn = get_connection()
    try:
        row = conn.execute(
            "SELECT id FROM boards WHERE user_id = ?", (user_id,)
        ).fetchone()
        if row is None:
            return None
        board_id = row["id"]
        if name is not None:
            conn.execute(
                "UPDATE boards SET columns_json = ?, name = ? WHERE id = ?",
                (json.dumps(columns), name, board_id),
            )
        else:
            conn.execute(
                "UPDATE boards SET columns_json = ? WHERE id = ?",
                (json.dumps(columns), board_id),
            )
        conn.commit()
        return get_board(user_id)
    finally:
        conn.close()
