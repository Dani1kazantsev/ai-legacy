from unittest.mock import MagicMock, patch
from ai_legacy.llm import LLMClient


def test_generate_calls_openai_compatible_api_with_correct_params():
    with patch("ai_legacy.llm.OpenAI") as MockOpenAI:
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.choices = [MagicMock(message=MagicMock(content="Норм"))]
        mock_client.chat.completions.create.return_value = mock_response
        MockOpenAI.return_value = mock_client

        llm = LLMClient(
            api_key="fake-key",
            model="llama-3.3-70b-versatile",
            base_url="https://api.groq.com/openai/v1",
        )
        history = [
            {"role": "user", "content": "Привет"},
            {"role": "assistant", "content": "Йо"},
            {"role": "user", "content": "Как дела?"},
        ]
        result = llm.generate(system_prompt="Ты копия", history=history)

        assert result == "Норм"
        # Проверяем что system был добавлен в начало messages
        call_kwargs = mock_client.chat.completions.create.call_args.kwargs
        assert call_kwargs["model"] == "llama-3.3-70b-versatile"
        messages = call_kwargs["messages"]
        assert messages[0] == {"role": "system", "content": "Ты копия"}
        assert messages[1:] == history


def test_generate_handles_empty_content():
    """Если LLM вернул None в content — отдаём пустую строку, не падаем."""
    with patch("ai_legacy.llm.OpenAI") as MockOpenAI:
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.choices = [MagicMock(message=MagicMock(content=None))]
        mock_client.chat.completions.create.return_value = mock_response
        MockOpenAI.return_value = mock_client

        llm = LLMClient(api_key="k", model="m", base_url="https://x")
        result = llm.generate(system_prompt="s", history=[{"role": "user", "content": "hi"}])
        assert result == ""
