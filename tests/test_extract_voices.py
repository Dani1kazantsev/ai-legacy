import json
from pathlib import Path
from scripts.extract_voices import list_voice_files


def test_lists_owner_voice_files(tmp_path):
    """Возвращает список путей к voice-файлам, принадлежащим владельцу."""
    export = {
        "messages": [
            {"type": "message", "from_id": "user987", "media_type": "voice_message", "file": "voice/a.ogg"},
            {"type": "message", "from_id": "user123", "media_type": "voice_message", "file": "voice/b.ogg"},
            {"type": "message", "from_id": "user987", "media_type": "voice_message", "file": "voice/c.ogg"},
            {"type": "message", "from_id": "user987", "text": "просто текст"},
        ]
    }
    p = tmp_path / "export.json"
    p.write_text(json.dumps(export), encoding="utf-8")

    files = list_voice_files(p, owner_from_id="user987")
    assert files == ["voice/a.ogg", "voice/c.ogg"]


def test_handles_missing_file_field(tmp_path):
    """Сообщения без поля file пропускаются без ошибок."""
    export = {
        "messages": [
            {"type": "message", "from_id": "user987", "media_type": "voice_message"},
        ]
    }
    p = tmp_path / "export.json"
    p.write_text(json.dumps(export), encoding="utf-8")

    files = list_voice_files(p, owner_from_id="user987")
    assert files == []
