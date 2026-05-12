"""Оркестратор обработки одного входящего сообщения."""

from ai_legacy.personality import Personality
from ai_legacy.prompt_builder import build_system_prompt


class MessageHandler:
    def __init__(
        self,
        db,
        llm,
        personality: Personality,
        few_shot: list[dict],
        owner_name: str,
        history_limit: int = 30,
    ):
        self._db = db
        self._llm = llm
        self._personality = personality
        self._few_shot = few_shot
        self._owner_name = owner_name
        self._history_limit = history_limit
        self._system_prompt = build_system_prompt(
            personality=personality,
            few_shot=few_shot,
            owner_name=owner_name,
        )

    def handle(self, user_id: int, message: str) -> str:
        """Обрабатывает входящее сообщение от user_id, возвращает текст ответа."""
        history = self._db.get_recent_messages(user_id=user_id, limit=self._history_limit)
        history.append({"role": "user", "content": message})

        response = self._llm.generate(
            system_prompt=self._system_prompt,
            history=history,
        )

        self._db.add_message(user_id=user_id, role="user", content=message)
        self._db.add_message(user_id=user_id, role="assistant", content=response)

        return response
