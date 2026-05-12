"""Парсер Telegram Desktop JSON-экспорта.

Использование (CLI):
    python scripts/parse_telegram_export.py <input.json> <output.json> <owner_from_id>
"""

import json
import sys
from pathlib import Path
from typing import Any


def parse_export(path: Path, owner_from_id: str) -> dict[str, Any]:
    """Парсит Telegram-экспорт, оставляя сообщения владельца + минимум контекста.

    Контекст = последнее сообщение собеседника непосредственно перед сообщением владельца.

    Returns:
        {
            "chat_name": str,
            "chat_type": str,
            "messages": [
                {"is_owner": bool, "date": str, "text": str, "media_type": str|None, "type": "message"},
                ...
            ]
        }
    """
    with path.open(encoding="utf-8") as f:
        data = json.load(f)

    raw_messages = [m for m in data.get("messages", []) if m.get("type") == "message"]

    result_messages = []
    last_other_message = None

    for m in raw_messages:
        is_owner = m.get("from_id") == owner_from_id
        # Telegram-экспорт может хранить text как строку или как массив фрагментов
        text = _text_to_string(m.get("text", ""))

        record = {
            "is_owner": is_owner,
            "date": m.get("date", ""),
            "text": text,
            "media_type": m.get("media_type"),
            "type": "message",
        }

        if is_owner:
            # Включаем контекст: последнее не-владельческое сообщение перед этим
            if last_other_message is not None:
                result_messages.append(last_other_message)
                last_other_message = None
            result_messages.append(record)
        else:
            last_other_message = record

    return {
        "chat_name": data.get("name", ""),
        "chat_type": data.get("type", ""),
        "messages": result_messages,
    }


def _text_to_string(text: Any) -> str:
    """Telegram может представлять text как str или list[str|dict]."""
    if isinstance(text, str):
        return text
    if isinstance(text, list):
        parts: list[str] = []
        for t in text:
            if isinstance(t, str):
                parts.append(t)
            elif isinstance(t, dict):
                parts.append(t.get("text", ""))
            # silently skip other types
        return "".join(parts)
    return ""


def main() -> None:
    if len(sys.argv) != 4:
        print("Usage: python parse_telegram_export.py <input.json> <output.json> <owner_from_id>")
        sys.exit(1)

    input_path = Path(sys.argv[1])
    output_path = Path(sys.argv[2])
    owner_from_id = sys.argv[3]

    result = parse_export(input_path, owner_from_id)
    with output_path.open("w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    owner_count = sum(1 for m in result["messages"] if m["is_owner"])
    print(f"Parsed: {owner_count} owner messages, {len(result['messages'])} total (owner + context)")


if __name__ == "__main__":
    main()
