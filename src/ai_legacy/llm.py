"""Тонкая обёртка над Anthropic SDK."""

from anthropic import Anthropic


class LLMClient:
    def __init__(self, api_key: str, model: str, max_tokens: int = 1024):
        self._client = Anthropic(api_key=api_key)
        self._model = model
        self._max_tokens = max_tokens

    def generate(self, system_prompt: str, history: list[dict]) -> str:
        """Шлёт запрос в Claude. history — список {role, content}.

        Возвращает текст ответа.
        """
        response = self._client.messages.create(
            model=self._model,
            max_tokens=self._max_tokens,
            system=system_prompt,
            messages=history,
        )
        # Anthropic возвращает content как list[TextBlock]
        parts = [block.text for block in response.content if hasattr(block, "text")]
        return "".join(parts)
