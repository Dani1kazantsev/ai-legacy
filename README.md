# AI Legacy

ИИ-копия личности владельца, активируемая после его смерти.
См. `docs/superpowers/specs/2026-05-12-ai-legacy-copy-design.md`.

## Установка

```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
cp .env.example .env  # заполнить значения
```

## Запуск

```bash
python -m ai_legacy.bot
```

## Тесты

```bash
pytest
```
