"""Оркестратор обработки одного входящего сообщения."""

from ai_legacy.personality import Personality
from ai_legacy.prompt_builder import build_system_prompt
from ai_legacy.rag import MessageIndex


class MessageHandler:
    def __init__(
        self,
        db,
        llm,
        personality: Personality,
        few_shot: list[dict],
        owner_name: str,
        history_limit: int = 30,
        rag_index: MessageIndex | None = None,
        rag_top_k: int = 8,
    ):
        self._db = db
        self._llm = llm
        self._personality = personality
        self._few_shot = few_shot
        self._owner_name = owner_name
        self._history_limit = history_limit
        self._rag_index = rag_index
        self._rag_top_k = rag_top_k

    def handle(self, user_id: int, message: str) -> str:
        """Обрабатывает входящее сообщение от user_id, возвращает текст ответа."""
        history = self._db.get_recent_messages(user_id=user_id, limit=self._history_limit)
        history.append({"role": "user", "content": message})

        # RAG retrieve по новому сообщению + последнему ответу собеседника
        rag_examples = []
        if self._rag_index is not None:
            rag_query = message
            relevant = self._rag_index.retrieve(rag_query, top_k=self._rag_top_k)
            rag_examples = [r.to_dict() for r in relevant]

        # Сборка system prompt с RAG-релевантным контекстом КАЖДЫЙ запрос
        system_prompt = build_system_prompt(
            personality=self._personality,
            few_shot=self._few_shot,
            owner_name=self._owner_name,
            rag_examples=rag_examples,
        )

        response = self._llm.generate(
            system_prompt=system_prompt,
            history=history,
        )

        self._db.add_message(user_id=user_id, role="user", content=message)
        self._db.add_message(user_id=user_id, role="assistant", content=response)

        return response
