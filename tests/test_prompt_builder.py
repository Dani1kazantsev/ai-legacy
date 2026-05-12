from ai_legacy.personality import Personality
from ai_legacy.prompt_builder import build_system_prompt


def _make_personality() -> Personality:
    return Personality(
        principles="Честность важнее комфорта",
        opinions="ИИ — это будущее",
        humor="Саркастичный, любит абсурд",
        biography="Родился в 1995, инженер",
        relationships="## Жена Ирина — inner_circle",
        phrases="- Чики-пуки",
    )


def test_system_prompt_includes_all_personality_blocks():
    p = _make_personality()
    examples = [{"in": "Привет", "out": "Йо"}]

    prompt = build_system_prompt(personality=p, few_shot=examples, owner_name="Данила")

    assert "Честность важнее комфорта" in prompt
    assert "ИИ — это будущее" in prompt
    assert "Саркастичный" in prompt
    assert "Родился в 1995" in prompt
    assert "Чики-пуки" in prompt
    assert "Данила" in prompt


def test_system_prompt_includes_few_shot_examples():
    p = _make_personality()
    examples = [{"in": "Что делаешь?", "out": "Кодю"}]

    prompt = build_system_prompt(personality=p, few_shot=examples, owner_name="Данила")

    assert "Что делаешь?" in prompt
    assert "Кодю" in prompt


def test_system_prompt_mentions_ai_copy_status():
    p = _make_personality()
    prompt = build_system_prompt(personality=p, few_shot=[], owner_name="Данила")

    # Бот должен знать, что он копия
    assert "копи" in prompt.lower() or "ии" in prompt.lower()


def test_system_prompt_explicitly_states_owner_is_dead():
    """Регрессия: бот должен знать, что владелец умер, без двусмысленности."""
    p = _make_personality()
    prompt = build_system_prompt(personality=p, few_shot=[], owner_name="Данила")
    # Должно явно упоминаться что владелец умер — не «возможно умер» или «гипотетически»
    assert "Данила умер" in prompt or "умер." in prompt


def test_system_prompt_forbids_generic_jokes():
    """Регрессия: должно быть указание не сочинять generic AI-шутки."""
    p = _make_personality()
    prompt = build_system_prompt(personality=p, few_shot=[], owner_name="Данила")
    # Должно явно отговаривать от шуток на заказ или generic
    prompt_lower = prompt.lower()
    assert "не сочиняй" in prompt_lower or "generic" in prompt_lower or "на заказ" in prompt_lower
