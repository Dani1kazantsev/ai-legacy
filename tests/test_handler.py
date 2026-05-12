from unittest.mock import MagicMock
from ai_legacy.handler import MessageHandler
from ai_legacy.personality import Personality


def _make_personality():
    return Personality(
        principles="p", opinions="o", humor="h",
        biography="b", relationships="r", phrases="ph",
    )


def test_handle_message_persists_and_returns_response():
    db = MagicMock()
    db.get_recent_messages.return_value = []  # история пустая
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
    # Сохранили вход и выход
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
    # История + новое сообщение
    assert history_passed[-1] == {"role": "user", "content": "Новое"}
    assert history_passed[0] == {"role": "user", "content": "Старое 1"}
