from pathlib import Path
from ai_legacy.db import Database


def test_save_and_load_messages(tmp_path):
    db_path = tmp_path / "test.db"
    db = Database(db_path)
    db.init_schema()

    db.add_message(user_id=42, role="user", content="Привет")
    db.add_message(user_id=42, role="assistant", content="Привет, дорогой!")
    db.add_message(user_id=99, role="user", content="Это другой юзер")

    history_42 = db.get_recent_messages(user_id=42, limit=10)
    assert len(history_42) == 2
    assert history_42[0]["content"] == "Привет"
    assert history_42[1]["content"] == "Привет, дорогой!"

    history_99 = db.get_recent_messages(user_id=99, limit=10)
    assert len(history_99) == 1


def test_get_recent_messages_respects_limit(tmp_path):
    db = Database(tmp_path / "t.db")
    db.init_schema()

    for i in range(10):
        db.add_message(user_id=1, role="user", content=f"msg{i}")

    history = db.get_recent_messages(user_id=1, limit=3)
    assert len(history) == 3
    # Возвращает последние, в хронологическом порядке (старые → новые)
    assert history[0]["content"] == "msg7"
    assert history[2]["content"] == "msg9"


def test_init_schema_idempotent(tmp_path):
    db = Database(tmp_path / "t.db")
    db.init_schema()
    db.init_schema()  # не должно падать
    db.add_message(user_id=1, role="user", content="ok")
    assert len(db.get_recent_messages(user_id=1, limit=5)) == 1


def test_get_recent_messages_returns_only_role_and_content(tmp_path):
    """Регрессия: get_recent_messages не возвращает created_at или другие поля,
    т.к. результат идёт напрямую в Anthropic API, который принимает только role+content."""
    db = Database(tmp_path / "t.db")
    db.init_schema()
    db.add_message(user_id=1, role="user", content="hi")

    messages = db.get_recent_messages(user_id=1, limit=10)
    assert len(messages) == 1
    assert set(messages[0].keys()) == {"role", "content"}
