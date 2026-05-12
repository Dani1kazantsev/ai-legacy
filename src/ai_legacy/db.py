"""SQLite-хранилище истории диалогов per-пользователь."""

import sqlite3
from pathlib import Path
from typing import Literal


Role = Literal["user", "assistant"]


class Database:
    def __init__(self, path: Path):
        self.path = path

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.path)
        conn.row_factory = sqlite3.Row
        return conn

    def init_schema(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    role TEXT NOT NULL CHECK(role IN ('user', 'assistant')),
                    content TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
            conn.execute("CREATE INDEX IF NOT EXISTS idx_messages_user_id ON messages(user_id, id)")

    def add_message(self, user_id: int, role: Role, content: str) -> None:
        with self._connect() as conn:
            conn.execute(
                "INSERT INTO messages (user_id, role, content) VALUES (?, ?, ?)",
                (user_id, role, content),
            )

    def get_recent_messages(self, user_id: int, limit: int = 30) -> list[dict]:
        """Возвращает последние сообщения для user_id, в хронологическом порядке (старые → новые).

        Каждое сообщение: {"role": str, "content": str} — формат, готовый для Anthropic API.
        """
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT role, content
                FROM messages
                WHERE user_id = ?
                ORDER BY id DESC
                LIMIT ?
                """,
                (user_id, limit),
            ).fetchall()
        # Перевернуть в хронологический порядок
        return [{"role": r["role"], "content": r["content"]} for r in reversed(rows)]
