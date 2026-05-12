from unittest.mock import MagicMock
from ai_legacy.handler import MessageHandler
from ai_legacy.personality import Personality
from ai_legacy.rag import MessageIndex, Example


def _make_personality():
    return Personality(
        principles="p", opinions="o", humor="h",
        biography="b", relationships="r", phrases="ph",
        behavior="bh",
    )


def test_handle_message_persists_and_returns_response():
    db = MagicMock()
    db.get_recent_messages.return_value = []
    llm = MagicMock()
    llm.generate.return_value = "Привет, дорогой!"

    handler = MessageHandler(
        db=db,
        llm=llm,
        personality=_make_personality(),
        few_shot=[],
        owner_name="Данила",
    )

    response = handler.handle(user_id=42, message="Привет")

    assert response == "Привет, дорогой!"
    save_calls = db.add_message.call_args_list
    assert len(save_calls) == 2
    assert save_calls[0].kwargs == {"user_id": 42, "role": "user", "content": "Привет"}
    assert save_calls[1].kwargs == {"user_id": 42, "role": "assistant", "content": "Привет, дорогой!"}


def test_handle_message_includes_history_in_llm_call():
    db = MagicMock()
    db.get_recent_messages.return_value = [
        {"role": "user", "content": "Старое 1"},
        {"role": "assistant", "content": "Старое 2"},
    ]
    llm = MagicMock()
    llm.generate.return_value = "ok"

    handler = MessageHandler(
        db=db, llm=llm,
        personality=_make_personality(),
        few_shot=[], owner_name="Д",
    )

    handler.handle(user_id=1, message="Новое")

    history_passed = llm.generate.call_args.kwargs["history"]
    assert history_passed[-1] == {"role": "user", "content": "Новое"}
    assert history_passed[0] == {"role": "user", "content": "Старое 1"}


def test_handle_message_uses_rag_when_index_provided():
    db = MagicMock()
    db.get_recent_messages.return_value = []
    llm = MagicMock()
    llm.generate.return_value = "Ответ"

    rag_index = MessageIndex([
        Example(chat="Котенок", in_text="Как дела?", out_text="Нормас"),
        Example(chat="Ваня", in_text="Че там?", out_text="Базар"),
        Example(chat="Петя", in_text="Всё норм?", out_text="Да"),
        Example(chat="Маша", in_text="Привет ты как", out_text="Окей"),
    ])

    handler = MessageHandler(
        db=db, llm=llm,
        personality=_make_personality(),
        few_shot=[], owner_name="Д",
        rag_index=rag_index,
    )

    handler.handle(user_id=1, message="Как дела")

    # system prompt должен содержать RAG-блок и нужный пример
    system_prompt = llm.generate.call_args.kwargs["system_prompt"]
    assert "Нормас" in system_prompt
    assert "Котенок" in system_prompt
