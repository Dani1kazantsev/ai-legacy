from unittest.mock import MagicMock, patch
from ai_legacy.llm import LLMClient


def test_generate_calls_anthropic_with_correct_params():
    with patch("ai_legacy.llm.Anthropic") as MockAnthropic:
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.content = [MagicMock(text="Норм")]
        mock_client.messages.create.return_value = mock_response
        MockAnthropic.return_value = mock_client

        llm = LLMClient(api_key="fake-key", model="claude-opus-4-7")
        history = [
            {"role": "user", "content": "Привет"},
            {"role": "assistant", "content": "Йо"},
            {"role": "user", "content": "Как дела?"},
        ]
        result = llm.generate(system_prompt="Ты копия", history=history)

        assert result == "Норм"
        call_kwargs = mock_client.messages.create.call_args.kwargs
        assert call_kwargs["model"] == "claude-opus-4-7"
        assert call_kwargs["system"] == "Ты копия"
        assert call_kwargs["messages"] == history
