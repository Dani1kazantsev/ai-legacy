import json
from pathlib import Path
from ai_legacy.few_shot import sample_examples


def test_returns_dialogue_pairs(tmp_path):
    chat = {
        "chat_name": "test",
        "messages": [
            {"is_owner": False, "text": "Как дела?", "type": "message"},
            {"is_owner": True, "text": "Норм", "type": "message"},
            {"is_owner": False, "text": "Что делаешь?", "type": "message"},
            {"is_owner": True, "text": "Работаю", "type": "message"},
            {"is_owner": True, "text": "Дописываю код", "type": "message"},
        ],
    }
    p = tmp_path / "chat.json"
    p.write_text(json.dumps(chat, ensure_ascii=False), encoding="utf-8")

    examples = sample_examples(tmp_path, n=10)

    # Каждый пример — пара (входящее, ответ)
    assert len(examples) >= 2
    pair = examples[0]
    assert "in" in pair and "out" in pair
    # ответ принадлежит владельцу
    assert pair["out"] in {"Норм", "Работаю", "Дописываю код"}


def test_no_chats_returns_empty(tmp_path):
    assert sample_examples(tmp_path, n=10) == []
