"""Тонкая обёртка над OpenAI-совместимым API.

Используется с Groq (https://api.groq.com/openai/v1). Совместимо с любым
провайдером, реализующим OpenAI Chat Completions API: OpenAI, Groq,
Together AI, Fireworks, локальный Ollama и т.п. — достаточно поменять base_url.
"""

from openai import OpenAI


class LLMClient:
    def __init__(self, api_key: str, model: str, base_url: str, max_tokens: int = 1024):
        self._client = OpenAI(api_key=api_key, base_url=base_url)
        self._model = model
        self._max_tokens = max_tokens

    def generate(self, system_prompt: str, history: list[dict]) -> str:
        """Шлёт запрос в LLM. history — список {role, content}.

        OpenAI Chat Completions ожидает system как первое сообщение в messages,
        в отличие от Anthropic, где он отдельным параметром. Переупаковываем.
        """
        messages = [{"role": "system", "content": system_prompt}] + history

        response = self._client.chat.completions.create(
            model=self._model,
            max_tokens=self._max_tokens,
            messages=messages,
        )

        choice = response.choices[0]
        return choice.message.content or ""
