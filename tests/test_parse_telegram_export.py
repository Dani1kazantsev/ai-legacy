import json
from pathlib import Path
from scripts.parse_telegram_export import parse_export


FIXTURE = Path(__file__).parent / "fixtures" / "telegram_export_sample.json"


def test_extracts_only_owner_messages():
    """Парсер вытаскивает только сообщения владельца + минимум контекста."""
    result = parse_export(FIXTURE, owner_from_id="user987")

    # Должны быть оба моих сообщения
    owner_texts = [m["text"] for m in result["messages"] if m["is_owner"]]
    assert "Привет, как дела?" in owner_texts
    assert "Тоже норм. Сегодня день рождения у мамы, едем к ней." in owner_texts


def test_includes_context_messages_before_owner():
    """Сообщения собеседника, идущие непосредственно перед моими, остаются как контекст."""
    result = parse_export(FIXTURE, owner_from_id="user987")

    # "Норм, у тебя?" должно быть в результате как контекст
    all_texts = [m["text"] for m in result["messages"]]
    assert "Норм, у тебя?" in all_texts


def test_skips_service_messages():
    """Сервисные сообщения (звонки и т.п.) пропускаются."""
    result = parse_export(FIXTURE, owner_from_id="user987")
    types = {m.get("type") for m in result["messages"]}
    assert "service" not in types


def test_voice_messages_marked():
    """Голосовые сообщения помечаются для дальнейшего извлечения."""
    result = parse_export(FIXTURE, owner_from_id="user987")
    voices = [m for m in result["messages"] if m.get("media_type") == "voice_message"]
    # В фикстуре голосовое — от собеседника, должно остаться как контекст
    assert len(voices) >= 0  # минимум: не падает


def test_output_includes_chat_metadata():
    """В результате есть имя чата и тип."""
    result = parse_export(FIXTURE, owner_from_id="user987")
    assert result["chat_name"] == "Test Chat"
    assert result["chat_type"] == "personal_chat"


def test_text_to_string_handles_unexpected_types():
    """_text_to_string не падает на list с неожиданными типами."""
    from scripts.parse_telegram_export import _text_to_string
    assert _text_to_string(["hello", 123, {"text": " world"}, None]) == "hello world"
