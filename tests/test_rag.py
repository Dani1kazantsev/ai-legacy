import json
from pathlib import Path
from ai_legacy.rag import MessageIndex, Example, build_index_from_messages, _tokenize


def test_tokenizer_lowercases_and_keeps_cyrillic():
    assert _tokenize("Привет, Как Дела?") == ["привет", "как", "дела"]


def test_index_retrieves_relevant_pair():
    examples = [
        Example(chat="A", in_text="Как дела?", out_text="Норм"),
        Example(chat="B", in_text="Что делаешь?", out_text="Работаю"),
        Example(chat="C", in_text="Когда придёшь?", out_text="Скоро"),
    ]
    idx = MessageIndex(examples)
    result = idx.retrieve("как дела сегодня", top_k=2)
    # First result should be the "Как дела?" example
    assert len(result) >= 1
    assert result[0].in_text == "Как дела?"


def test_empty_query_returns_empty():
    idx = MessageIndex([Example(chat="A", in_text="x", out_text="y")])
    assert idx.retrieve("", top_k=5) == []
    assert idx.retrieve("   ", top_k=5) == []


def test_build_index_from_messages(tmp_path):
    chat_data = {
        "chat_name": "Test",
        "messages": [
            {"is_owner": False, "text": "Привет"},
            {"is_owner": True, "text": "Здарова"},
            {"is_owner": False, "text": "Как ты?"},
            {"is_owner": True, "text": "Нормас"},
        ],
    }
    (tmp_path / "chat.json").write_text(json.dumps(chat_data, ensure_ascii=False), encoding="utf-8")

    idx = build_index_from_messages(tmp_path)
    assert len(idx) == 2  # two owner-with-context pairs


def test_empty_dir_produces_empty_index(tmp_path):
    idx = build_index_from_messages(tmp_path)
    assert len(idx) == 0
    assert idx.retrieve("anything", top_k=5) == []
