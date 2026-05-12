"""Семплер few-shot примеров диалогов из распарсенных чатов."""

import json
import random
from pathlib import Path


def sample_examples(messages_dir: Path, n: int = 10) -> list[dict]:
    """Возвращает n пар (входящее сообщение → ответ владельца) из всех чатов.

    Каждая пара: {"in": str, "out": str}
    """
    all_pairs: list[dict] = []

    for chat_file in messages_dir.glob("*.json"):
        with chat_file.open(encoding="utf-8") as f:
            chat = json.load(f)

        messages = chat.get("messages", [])
        for i in range(1, len(messages)):
            prev = messages[i - 1]
            curr = messages[i]
            if not prev.get("is_owner") and curr.get("is_owner"):
                prev_text = prev.get("text", "").strip()
                curr_text = curr.get("text", "").strip()
                if prev_text and curr_text:
                    all_pairs.append({"in": prev_text, "out": curr_text})

    if not all_pairs:
        return []

    sample_size = min(n, len(all_pairs))
    return random.sample(all_pairs, sample_size)
