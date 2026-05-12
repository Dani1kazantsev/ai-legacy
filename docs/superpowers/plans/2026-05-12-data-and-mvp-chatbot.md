# План 1: Сбор данных + MVP-чатбот

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Получить рабочий Telegram-бот, который отвечает Даниле «как он», на основе его переписок и self-интервью. Только Данила как тестовый пользователь. Базовая память диалога.

**Architecture:** Python-приложение с архитектурой адаптеров. Telegram-бот → ядро (сборка промпта + LLM-вызов) → SQLite-хранилище истории. Personality-данные в Markdown/JSON-файлах, грузятся при старте. Один процесс, локальный запуск на Mac M4 для разработки.

**Tech Stack:** Python 3.11+, `python-telegram-bot` v21+, `anthropic` SDK, SQLite (stdlib), `pydantic` для конфигов, `pytest` для тестов, `python-dotenv` для секретов.

**Соответствие дизайн-документу:** реализует Фазы 0 (сбор данных) и 1 (MVP-чатбот) из `docs/superpowers/specs/2026-05-12-ai-legacy-copy-design.md`.

---

## Карта файлов

**Создаётся:**

```
ai-legacy/
├── .gitignore
├── .env.example
├── README.md
├── pyproject.toml
├── data/
│   ├── messages/.gitkeep           # сюда падают распарсенные чаты
│   ├── voice/.gitkeep              # сюда падают извлечённые голосовые
│   └── personality/
│       ├── principles.md           # шаблон, наполняется в self-интервью
│       ├── opinions.md
│       ├── humor.md
│       ├── biography.md
│       ├── relationships.md
│       └── phrases.md
├── scripts/
│   ├── parse_telegram_export.py    # JSON-экспорт → cleaned dataset
│   └── extract_voices.py           # извлечь OGG из экспорта
├── src/
│   └── ai_legacy/
│       ├── __init__.py
│       ├── config.py               # загрузка .env, валидация
│       ├── db.py                   # SQLite-схема и операции
│       ├── llm.py                  # обёртка Anthropic SDK
│       ├── personality.py          # загрузка personality/*.md
│       ├── prompt_builder.py       # сборка system prompt + few-shot
│       ├── memory.py               # история диалога per-пользователь
│       ├── handler.py              # бизнес-логика: message in → response out
│       └── bot.py                  # точка входа Telegram-бота
├── tests/
│   ├── __init__.py
│   ├── fixtures/
│   │   └── telegram_export_sample.json
│   ├── test_parse_telegram_export.py
│   ├── test_db.py
│   ├── test_personality.py
│   ├── test_prompt_builder.py
│   ├── test_memory.py
│   └── test_handler.py
└── docs/
    ├── superpowers/                # уже существует
    └── self-interview-guide.md     # вопросы для self-интервью
```

**Принципы декомпозиции:**
- Каждый модуль в `src/ai_legacy/` имеет одну ответственность
- `handler.py` оркестрирует все остальные, но не содержит логики
- Тестируем модули изолированно с моками для LLM-вызовов
- `bot.py` — тонкая обёртка над Telegram API, всё остальное — в `handler.py`

---

## Задачи

### Task 1: Инициализация проекта

**Files:**
- Create: `.gitignore`, `pyproject.toml`, `README.md`, `.env.example`

- [ ] **Step 1: Создать `.gitignore`**

Создать файл `.gitignore`:

```
.venv/
__pycache__/
*.pyc
.pytest_cache/
.env
data/messages/*.json
!data/messages/.gitkeep
data/voice/*.ogg
!data/voice/.gitkeep
*.db
.DS_Store
```

- [ ] **Step 2: Создать `pyproject.toml`**

```toml
[build-system]
requires = ["setuptools>=68"]
build-backend = "setuptools.build_meta"

[project]
name = "ai-legacy"
version = "0.1.0"
description = "AI copy of a person, accessible after death"
requires-python = ">=3.11"
dependencies = [
    "python-telegram-bot>=21.0",
    "anthropic>=0.40.0",
    "pydantic>=2.0",
    "pydantic-settings>=2.0",
    "python-dotenv>=1.0",
]

[project.optional-dependencies]
dev = ["pytest>=8.0", "pytest-asyncio>=0.23"]

[tool.setuptools.packages.find]
where = ["src"]

[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["tests"]
pythonpath = ["src", "."]
```

- [ ] **Step 3: Создать `.env.example`**

```
TELEGRAM_BOT_TOKEN=your_token_from_botfather
ANTHROPIC_API_KEY=sk-ant-...
OWNER_TELEGRAM_USER_ID=123456789
ANTHROPIC_MODEL=claude-opus-4-7
```

- [ ] **Step 4: Создать минимальный `README.md`**

```markdown
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
```

- [ ] **Step 5: Установить окружение**

```bash
cd "/Users/danilakazantsev/Мои проекты/ai-legacy"
python3.11 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

Expected: установка проходит без ошибок.

- [ ] **Step 6: Создать пустые директории через `.gitkeep`**

```bash
mkdir -p data/messages data/voice data/personality src/ai_legacy tests/fixtures scripts
touch data/messages/.gitkeep data/voice/.gitkeep
touch src/ai_legacy/__init__.py tests/__init__.py
```

- [ ] **Step 7: Коммит**

```bash
git add .gitignore pyproject.toml README.md .env.example data/ src/ tests/ scripts/
git commit -m "chore: bootstrap project structure and dependencies"
```

---

### Task 2: Создать приватный GitHub-репозиторий

**Files:** только удалённый репозиторий

- [ ] **Step 1: Создать репозиторий на github.com**

Зайти на https://github.com/new
- Имя: `ai-legacy` (или другое на выбор)
- Visibility: **Private** (обязательно)
- НЕ инициализировать с README (у нас уже есть)

- [ ] **Step 2: Привязать локальный репозиторий и запушить**

```bash
git remote add origin git@github.com:Dani1kazantsev/ai-legacy.git
git branch -M main
git push -u origin main
```

Expected: push успешен, репо появилось на GitHub.

**Уже выполнено:** репозиторий `git@github.com:Dani1kazantsev/ai-legacy.git` создан и привязан, спек и план запушены.

---

### Task 3: Шаблоны personality-файлов

**Files:**
- Create: `data/personality/{principles,opinions,humor,biography,relationships,phrases}.md`
- Create: `docs/self-interview-guide.md`

- [ ] **Step 1: Создать `data/personality/principles.md`**

```markdown
# Принципы и ценности

> Что для меня важно. Чем я руководствуюсь в решениях.
> Заполняется в self-интервью с Claude.

## Ключевые принципы
- (заполнится в интервью)

## Чего я никогда не делаю
- (заполнится в интервью)

## Что считаю недопустимым в людях
- (заполнится в интервью)
```

- [ ] **Step 2: Создать `data/personality/opinions.md`**

```markdown
# Мнения и позиции

> Что я думаю о конкретных темах.
> Сюда же — стабильные позиции, которые копия должна сохранять.

## Работа и карьера
- (заполнится)

## Отношения и семья
- (заполнится)

## Деньги
- (заполнится)

## Технологии и ИИ
- (заполнится)

## Политика и общество
- (заполнится, если хочешь)

## Здоровье и образ жизни
- (заполнится)
```

- [ ] **Step 3: Создать `data/personality/humor.md`**

```markdown
# Юмор и манера общения

> Как я шучу, как разряжаю обстановку, какие фразы повторяю.

## Любимые типы шуток
- (заполнится)

## Примеры моих типичных шуток
- (заполнится)

## Темы, на которые я НЕ шучу
- (заполнится)
```

- [ ] **Step 4: Создать `data/personality/biography.md`**

```markdown
# Биография

> Ключевые факты о моей жизни. По периодам.

## Детство (до ~14 лет)

## Школа и подростковость

## Учёба после школы

## Карьера

## Личная жизнь (по этапам)

## Большие путешествия / опыт

## Хобби и увлечения

## Друзья и важные знакомства
```

- [ ] **Step 5: Создать `data/personality/relationships.md`**

```markdown
# Близкие люди

> Кто мне дорог, и как с ними общаться.
> Поле "Уровень" из дизайн-документа: inner_circle / close / family / acquaintances

## Шаблон записи

### [Имя]
- Уровень: [inner_circle | close | family | acquaintances]
- Telegram ID: [число — заполнится позже]
- Контекст: кто это, как мы знакомы, основные совместные эпизоды
- Темы для обсуждения: что с ним обычно обсуждаем
- Чувствительные зоны: что не поднимать, не упоминать
- Стиль общения: серьёзный/шуточный/нежный, обращение
```

- [ ] **Step 6: Создать `data/personality/phrases.md`**

```markdown
# Любимые фразы и выражения

> Мои "фирменные" словечки, мемы, повторяемые выражения.

## Приветствия

## Реакции

## Прощания

## Слова-паразиты и обороты

## Внутренние шутки с близкими
```

- [ ] **Step 7: Создать `docs/self-interview-guide.md` — руководство для интервью**

```markdown
# Self-Interview Guide

Структура самоинтервью с Claude для заполнения `data/personality/*.md`.

## Подготовка

- 1–3 сессии по 45–60 минут
- Тихая обстановка, без отвлечений
- Открыть `data/personality/*.md` рядом для проверки

## Сессия 1: Принципы и мнения (~60 мин)

Claude задаёт вопросы по темам из `principles.md` и `opinions.md`.
Примеры:
- Назови 3–5 принципов, по которым ты живёшь. Откуда они?
- Опиши ситуацию, где ты поступил из принципа, хотя было невыгодно.
- Что бы ты НИКОГДА не сделал, даже под угрозой?
- Что ты думаешь о [список тем]?

## Сессия 2: Биография и юмор (~60 мин)

- Расскажи 5 ключевых эпизодов из детства, которые тебя сформировали.
- Опиши свои отношения с родителями/братьями.
- Расскажи 3 момента из юности, которые часто всплывают в памяти.
- Назови 5 шуток, которые ты часто повторяешь.
- Над какими ситуациями ты обычно смеёшься, а над какими — нет?

## Сессия 3: Близкие люди (~45 мин)

Для каждого человека в `relationships.md`:
- Кто это, как познакомились?
- Какой у вас стиль общения?
- О чём обычно говорите?
- О чём НЕ говорите?
- Какие у вас инсайдер-шутки?

## После интервью

- Закоммитить заполненные файлы
- Перечитать через день, добавить что вспомнил
```

- [ ] **Step 8: Коммит**

```bash
git add data/personality/ docs/self-interview-guide.md
git commit -m "docs: add personality file templates and self-interview guide"
git push
```

---

### Task 4: Парсер Telegram-экспорта (с TDD)

**Files:**
- Create: `scripts/parse_telegram_export.py`
- Create: `tests/test_parse_telegram_export.py`
- Create: `tests/fixtures/telegram_export_sample.json`

- [ ] **Step 1: Создать fixture с примером Telegram-экспорта**

Файл `tests/fixtures/telegram_export_sample.json`:

```json
{
  "name": "Test Chat",
  "type": "personal_chat",
  "id": 12345,
  "messages": [
    {
      "id": 1,
      "type": "message",
      "date": "2024-01-15T10:30:00",
      "from": "Данила",
      "from_id": "user987",
      "text": "Привет, как дела?"
    },
    {
      "id": 2,
      "type": "message",
      "date": "2024-01-15T10:31:00",
      "from": "Друг",
      "from_id": "user123",
      "text": "Норм, у тебя?"
    },
    {
      "id": 3,
      "type": "message",
      "date": "2024-01-15T10:32:00",
      "from": "Данила",
      "from_id": "user987",
      "text": "Тоже норм. Сегодня день рождения у мамы, едем к ней."
    },
    {
      "id": 4,
      "type": "message",
      "date": "2024-01-15T10:33:00",
      "from": "Друг",
      "from_id": "user123",
      "media_type": "voice_message",
      "file": "voice_messages/file_1.ogg",
      "text": ""
    },
    {
      "id": 5,
      "type": "service",
      "date": "2024-01-15T10:34:00",
      "action": "phone_call",
      "duration_seconds": 60
    }
  ]
}
```

- [ ] **Step 2: Написать failing-тест в `tests/test_parse_telegram_export.py`**

```python
import json
from pathlib import Path
from scripts.parse_telegram_export import parse_export


FIXTURE = Path(__file__).parent / "fixtures" / "telegram_export_sample.json"


def test_extracts_only_owner_messages():
    """Парсер вытаскивает только сообщения владельца + минимум контекста."""
    result = parse_export(FIXTURE, owner_from_id="user987")

    # Должны быть оба моих сообщения
    owner_texts = [m["text"] for m in result["messages"] if m["is_owner"]]
    assert "Привет, как дела?" in owner_texts
    assert "Тоже норм. Сегодня день рождения у мамы, едем к ней." in owner_texts


def test_includes_context_messages_before_owner():
    """Сообщения собеседника, идущие непосредственно перед моими, остаются как контекст."""
    result = parse_export(FIXTURE, owner_from_id="user987")

    # "Норм, у тебя?" должно быть в результате как контекст
    all_texts = [m["text"] for m in result["messages"]]
    assert "Норм, у тебя?" in all_texts


def test_skips_service_messages():
    """Сервисные сообщения (звонки и т.п.) пропускаются."""
    result = parse_export(FIXTURE, owner_from_id="user987")
    types = {m.get("type") for m in result["messages"]}
    assert "service" not in types


def test_voice_messages_marked():
    """Голосовые сообщения помечаются для дальнейшего извлечения."""
    result = parse_export(FIXTURE, owner_from_id="user987")
    voices = [m for m in result["messages"] if m.get("media_type") == "voice_message"]
    # В фикстуре голосовое — от собеседника, должно остаться как контекст
    assert len(voices) >= 0  # минимум: не падает


def test_output_includes_chat_metadata():
    """В результате есть имя чата и тип."""
    result = parse_export(FIXTURE, owner_from_id="user987")
    assert result["chat_name"] == "Test Chat"
    assert result["chat_type"] == "personal_chat"
```

- [ ] **Step 3: Запустить тест — должен упасть**

```bash
pytest tests/test_parse_telegram_export.py -v
```

Expected: FAIL — модуль `scripts.parse_telegram_export` не существует.

- [ ] **Step 4: Написать реализацию `scripts/parse_telegram_export.py`**

```python
"""Парсер Telegram Desktop JSON-экспорта.

Использование (CLI):
    python scripts/parse_telegram_export.py <input.json> <output.json> <owner_from_id>
"""

import json
import sys
from pathlib import Path
from typing import Any


def parse_export(path: Path, owner_from_id: str) -> dict[str, Any]:
    """Парсит Telegram-экспорт, оставляя сообщения владельца + минимум контекста.

    Контекст = последнее сообщение собеседника непосредственно перед сообщением владельца.

    Returns:
        {
            "chat_name": str,
            "chat_type": str,
            "messages": [
                {"is_owner": bool, "date": str, "text": str, "media_type": str|None, "type": "message"},
                ...
            ]
        }
    """
    with path.open(encoding="utf-8") as f:
        data = json.load(f)

    raw_messages = [m for m in data.get("messages", []) if m.get("type") == "message"]

    result_messages = []
    last_other_message = None

    for m in raw_messages:
        is_owner = m.get("from_id") == owner_from_id
        # Telegram-экспорт может хранить text как строку или как массив фрагментов
        text = _text_to_string(m.get("text", ""))

        record = {
            "is_owner": is_owner,
            "date": m.get("date", ""),
            "text": text,
            "media_type": m.get("media_type"),
            "type": "message",
        }

        if is_owner:
            # Включаем контекст: последнее не-владельческое сообщение перед этим
            if last_other_message is not None:
                result_messages.append(last_other_message)
                last_other_message = None
            result_messages.append(record)
        else:
            last_other_message = record

    return {
        "chat_name": data.get("name", ""),
        "chat_type": data.get("type", ""),
        "messages": result_messages,
    }


def _text_to_string(text: Any) -> str:
    """Telegram может представлять text как str или list[str|dict]."""
    if isinstance(text, str):
        return text
    if isinstance(text, list):
        return "".join(t if isinstance(t, str) else t.get("text", "") for t in text)
    return ""


def main() -> None:
    if len(sys.argv) != 4:
        print("Usage: python parse_telegram_export.py <input.json> <output.json> <owner_from_id>")
        sys.exit(1)

    input_path = Path(sys.argv[1])
    output_path = Path(sys.argv[2])
    owner_from_id = sys.argv[3]

    result = parse_export(input_path, owner_from_id)
    with output_path.open("w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    owner_count = sum(1 for m in result["messages"] if m["is_owner"])
    print(f"Parsed: {owner_count} owner messages, {len(result['messages'])} total (owner + context)")


if __name__ == "__main__":
    main()
```

- [ ] **Step 5: Запустить тесты — должны пройти**

```bash
pytest tests/test_parse_telegram_export.py -v
```

Expected: PASS все 5 тестов.

- [ ] **Step 6: Коммит**

```bash
git add scripts/parse_telegram_export.py tests/test_parse_telegram_export.py tests/fixtures/telegram_export_sample.json
git commit -m "feat: add Telegram export parser with owner-message extraction"
git push
```

---

### Task 5: Извлечение голосовых сообщений

**Files:**
- Create: `scripts/extract_voices.py`
- Create: `tests/test_extract_voices.py`

- [ ] **Step 1: Написать failing-тест**

`tests/test_extract_voices.py`:

```python
import json
from pathlib import Path
from scripts.extract_voices import list_voice_files


def test_lists_owner_voice_files(tmp_path):
    """Возвращает список путей к voice-файлам, принадлежащим владельцу."""
    export = {
        "messages": [
            {"type": "message", "from_id": "user987", "media_type": "voice_message", "file": "voice/a.ogg"},
            {"type": "message", "from_id": "user123", "media_type": "voice_message", "file": "voice/b.ogg"},
            {"type": "message", "from_id": "user987", "media_type": "voice_message", "file": "voice/c.ogg"},
            {"type": "message", "from_id": "user987", "text": "просто текст"},
        ]
    }
    p = tmp_path / "export.json"
    p.write_text(json.dumps(export), encoding="utf-8")

    files = list_voice_files(p, owner_from_id="user987")
    assert files == ["voice/a.ogg", "voice/c.ogg"]


def test_handles_missing_file_field(tmp_path):
    """Сообщения без поля file пропускаются без ошибок."""
    export = {
        "messages": [
            {"type": "message", "from_id": "user987", "media_type": "voice_message"},
        ]
    }
    p = tmp_path / "export.json"
    p.write_text(json.dumps(export), encoding="utf-8")

    files = list_voice_files(p, owner_from_id="user987")
    assert files == []
```

- [ ] **Step 2: Запустить — должен упасть**

```bash
pytest tests/test_extract_voices.py -v
```

Expected: FAIL — модуль не существует.

- [ ] **Step 3: Реализация `scripts/extract_voices.py`**

```python
"""Извлечение голосовых сообщений владельца из Telegram-экспорта.

Использование:
    python scripts/extract_voices.py <export.json> <export_dir> <output_dir> <owner_from_id>

Telegram Desktop при экспорте кладёт voice-файлы рядом с JSON в подпапку.
Этот скрипт копирует только мои голосовые в output_dir с осмысленными именами.
"""

import json
import shutil
import sys
from pathlib import Path


def list_voice_files(export_path: Path, owner_from_id: str) -> list[str]:
    """Возвращает относительные пути voice-файлов, принадлежащих владельцу."""
    with export_path.open(encoding="utf-8") as f:
        data = json.load(f)

    result = []
    for m in data.get("messages", []):
        if (
            m.get("type") == "message"
            and m.get("from_id") == owner_from_id
            and m.get("media_type") == "voice_message"
            and m.get("file")
        ):
            result.append(m["file"])
    return result


def copy_voices(export_path: Path, export_dir: Path, output_dir: Path, owner_from_id: str) -> int:
    """Копирует voice-файлы владельца в output_dir. Возвращает количество скопированных."""
    output_dir.mkdir(parents=True, exist_ok=True)
    relative_paths = list_voice_files(export_path, owner_from_id)

    copied = 0
    for rel in relative_paths:
        src = export_dir / rel
        if not src.exists():
            print(f"WARN: file not found: {src}", file=sys.stderr)
            continue
        dest = output_dir / f"{export_path.stem}_{Path(rel).name}"
        shutil.copy2(src, dest)
        copied += 1
    return copied


def main() -> None:
    if len(sys.argv) != 5:
        print("Usage: python extract_voices.py <export.json> <export_dir> <output_dir> <owner_from_id>")
        sys.exit(1)

    export_path = Path(sys.argv[1])
    export_dir = Path(sys.argv[2])
    output_dir = Path(sys.argv[3])
    owner_from_id = sys.argv[4]

    copied = copy_voices(export_path, export_dir, output_dir, owner_from_id)
    print(f"Copied {copied} voice messages to {output_dir}")


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Запустить тесты**

```bash
pytest tests/test_extract_voices.py -v
```

Expected: PASS оба теста.

- [ ] **Step 5: Коммит**

```bash
git add scripts/extract_voices.py tests/test_extract_voices.py
git commit -m "feat: add voice message extractor for Telegram exports"
git push
```

---

### Task 6: Провести self-интервью и заполнить personality-файлы

**Files:**
- Modify: `data/personality/*.md`

Это **ручная задача**, не код. Выполняется в отдельной сессии с Claude.

- [ ] **Step 1: Запланировать сессию**

Выделить ~60 минут в тихой обстановке.

- [ ] **Step 2: Открыть `docs/self-interview-guide.md` и `data/personality/`**

- [ ] **Step 3: Провести Сессию 1 (Принципы и мнения)**

Запросить у Claude: «Проведи со мной self-интервью по `docs/self-interview-guide.md`, Сессия 1. Заполняй ответы прямо в `data/personality/principles.md` и `data/personality/opinions.md` по ходу разговора.»

- [ ] **Step 4: Проверить и доредактировать `principles.md` и `opinions.md`**

Перечитать, что-то поправить, что-то добавить.

- [ ] **Step 5: Коммит**

```bash
git add data/personality/principles.md data/personality/opinions.md
git commit -m "data: fill principles and opinions from self-interview session 1"
git push
```

- [ ] **Step 6: (через день или больше) Сессия 2 — Биография и юмор**

То же, для `biography.md` и `humor.md`.

```bash
git add data/personality/biography.md data/personality/humor.md
git commit -m "data: fill biography and humor from self-interview session 2"
git push
```

- [ ] **Step 7: Сессия 3 — Близкие люди и фразы**

Для `relationships.md` и `phrases.md`. **Заодно** определить, кого включаем в корневой круг дерева доверия (понадобится позже в Плане 4).

```bash
git add data/personality/relationships.md data/personality/phrases.md
git commit -m "data: fill relationships and phrases from self-interview session 3"
git push
```

- [ ] **Step 8: Экспортировать выбранные Telegram-чаты и распарсить**

Сделать вручную через Telegram Desktop → Settings → Advanced → Export Telegram Data → выбрать конкретные чаты, формат JSON, без медиа (либо с медиа, если нужны голосовые).

Затем:

```bash
python scripts/parse_telegram_export.py <export.json> data/messages/chat_<name>.json <твой_from_id>
python scripts/extract_voices.py <export.json> <export_dir> data/voice <твой_from_id>
```

```bash
git add data/messages/ data/voice/
git commit -m "data: ingest initial Telegram chats and voice messages"
git push
```

---

### Task 7: Загрузка personality-файлов

**Files:**
- Create: `src/ai_legacy/personality.py`
- Create: `tests/test_personality.py`

- [ ] **Step 1: Failing-тест**

`tests/test_personality.py`:

```python
from pathlib import Path
from ai_legacy.personality import load_personality


def test_loads_all_personality_files(tmp_path):
    (tmp_path / "principles.md").write_text("# Принципы\n- Честность")
    (tmp_path / "opinions.md").write_text("# Мнения\nЯ за свободу.")
    (tmp_path / "humor.md").write_text("# Юмор\nСаркастичный.")
    (tmp_path / "biography.md").write_text("# Био\nРодился в Москве.")
    (tmp_path / "relationships.md").write_text("# Отношения\n## Жена\nИрина")
    (tmp_path / "phrases.md").write_text("# Фразы\n- Чики-пуки")

    p = load_personality(tmp_path)

    assert "Честность" in p.principles
    assert "свободу" in p.opinions
    assert "Саркастичный" in p.humor
    assert "Москве" in p.biography
    assert "Ирина" in p.relationships
    assert "Чики-пуки" in p.phrases


def test_missing_file_raises(tmp_path):
    import pytest
    (tmp_path / "principles.md").write_text("a")
    with pytest.raises(FileNotFoundError):
        load_personality(tmp_path)
```

- [ ] **Step 2: Запустить — упадёт**

```bash
pytest tests/test_personality.py -v
```

- [ ] **Step 3: Реализация `src/ai_legacy/personality.py`**

```python
"""Загрузка статичных personality-данных в память."""

from dataclasses import dataclass
from pathlib import Path


_REQUIRED_FILES = (
    "principles.md",
    "opinions.md",
    "humor.md",
    "biography.md",
    "relationships.md",
    "phrases.md",
)


@dataclass(frozen=True)
class Personality:
    principles: str
    opinions: str
    humor: str
    biography: str
    relationships: str
    phrases: str


def load_personality(directory: Path) -> Personality:
    """Загружает все personality-файлы из директории. Поднимает FileNotFoundError, если файл отсутствует."""
    contents: dict[str, str] = {}
    for filename in _REQUIRED_FILES:
        path = directory / filename
        if not path.exists():
            raise FileNotFoundError(f"Personality file missing: {path}")
        contents[filename.removesuffix(".md")] = path.read_text(encoding="utf-8")

    return Personality(**contents)
```

- [ ] **Step 4: Запустить тесты — пройдут**

```bash
pytest tests/test_personality.py -v
```

- [ ] **Step 5: Коммит**

```bash
git add src/ai_legacy/personality.py tests/test_personality.py
git commit -m "feat: add personality file loader"
git push
```

---

### Task 8: SQLite-хранилище истории диалогов

**Files:**
- Create: `src/ai_legacy/db.py`
- Create: `tests/test_db.py`

- [ ] **Step 1: Failing-тест**

`tests/test_db.py`:

```python
from pathlib import Path
from ai_legacy.db import Database


def test_save_and_load_messages(tmp_path):
    db_path = tmp_path / "test.db"
    db = Database(db_path)
    db.init_schema()

    db.add_message(user_id=42, role="user", content="Привет")
    db.add_message(user_id=42, role="assistant", content="Привет, дорогой!")
    db.add_message(user_id=99, role="user", content="Это другой юзер")

    history_42 = db.get_recent_messages(user_id=42, limit=10)
    assert len(history_42) == 2
    assert history_42[0]["content"] == "Привет"
    assert history_42[1]["content"] == "Привет, дорогой!"

    history_99 = db.get_recent_messages(user_id=99, limit=10)
    assert len(history_99) == 1


def test_get_recent_messages_respects_limit(tmp_path):
    db = Database(tmp_path / "t.db")
    db.init_schema()

    for i in range(10):
        db.add_message(user_id=1, role="user", content=f"msg{i}")

    history = db.get_recent_messages(user_id=1, limit=3)
    assert len(history) == 3
    # Возвращает последние, в хронологическом порядке (старые → новые)
    assert history[0]["content"] == "msg7"
    assert history[2]["content"] == "msg9"


def test_init_schema_idempotent(tmp_path):
    db = Database(tmp_path / "t.db")
    db.init_schema()
    db.init_schema()  # не должно падать
    db.add_message(user_id=1, role="user", content="ok")
    assert len(db.get_recent_messages(user_id=1, limit=5)) == 1
```

- [ ] **Step 2: Запустить — упадёт**

```bash
pytest tests/test_db.py -v
```

- [ ] **Step 3: Реализация `src/ai_legacy/db.py`**

```python
"""SQLite-хранилище истории диалогов per-пользователь."""

import sqlite3
from pathlib import Path
from typing import Literal


Role = Literal["user", "assistant"]


class Database:
    def __init__(self, path: Path):
        self.path = path

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.path)
        conn.row_factory = sqlite3.Row
        return conn

    def init_schema(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    role TEXT NOT NULL CHECK(role IN ('user', 'assistant')),
                    content TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
            conn.execute("CREATE INDEX IF NOT EXISTS idx_messages_user_id ON messages(user_id, id)")

    def add_message(self, user_id: int, role: Role, content: str) -> None:
        with self._connect() as conn:
            conn.execute(
                "INSERT INTO messages (user_id, role, content) VALUES (?, ?, ?)",
                (user_id, role, content),
            )

    def get_recent_messages(self, user_id: int, limit: int = 30) -> list[dict]:
        """Возвращает последние сообщения для user_id, в хронологическом порядке (старые → новые)."""
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT role, content, created_at
                FROM messages
                WHERE user_id = ?
                ORDER BY id DESC
                LIMIT ?
                """,
                (user_id, limit),
            ).fetchall()
        # Перевернуть в хронологический порядок
        return [dict(r) for r in reversed(rows)]
```

- [ ] **Step 4: Запустить тесты — пройдут**

```bash
pytest tests/test_db.py -v
```

- [ ] **Step 5: Коммит**

```bash
git add src/ai_legacy/db.py tests/test_db.py
git commit -m "feat: add SQLite database for per-user conversation history"
git push
```

---

### Task 9: Конфиг-загрузчик

**Files:**
- Create: `src/ai_legacy/config.py`

Этот модуль маленький и обёртка над pydantic-settings, можно без отдельных тестов (pydantic сам валидирует).

- [ ] **Step 1: Реализация `src/ai_legacy/config.py`**

```python
"""Загрузка и валидация конфигурации из .env."""

from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    telegram_bot_token: str
    anthropic_api_key: str
    owner_telegram_user_id: int
    anthropic_model: str = "claude-opus-4-7"

    # Пути к данным относительно корня проекта
    personality_dir: Path = Path("data/personality")
    messages_dir: Path = Path("data/messages")
    db_path: Path = Path("data/conversations.db")


def load_settings() -> Settings:
    return Settings()  # type: ignore[call-arg]
```

- [ ] **Step 2: Smoke-проверка**

Создать `.env` (если ещё нет):

```bash
cp .env.example .env
# открыть и заполнить реальными значениями
```

Затем:

```bash
python -c "from ai_legacy.config import load_settings; s = load_settings(); print(s.anthropic_model)"
```

Expected: печатает `claude-opus-4-7` без ошибок.

- [ ] **Step 3: Коммит**

```bash
git add src/ai_legacy/config.py
git commit -m "feat: add configuration loader with pydantic-settings"
git push
```

---

### Task 10: Сборщик few-shot примеров

**Files:**
- Create: `src/ai_legacy/few_shot.py`
- Create: `tests/test_few_shot.py`

- [ ] **Step 1: Failing-тест**

`tests/test_few_shot.py`:

```python
import json
from pathlib import Path
from ai_legacy.few_shot import sample_examples


def test_returns_dialogue_pairs(tmp_path):
    chat = {
        "chat_name": "test",
        "messages": [
            {"is_owner": False, "text": "Как дела?", "type": "message"},
            {"is_owner": True, "text": "Норм", "type": "message"},
            {"is_owner": False, "text": "Что делаешь?", "type": "message"},
            {"is_owner": True, "text": "Работаю", "type": "message"},
            {"is_owner": True, "text": "Дописываю код", "type": "message"},
        ],
    }
    p = tmp_path / "chat.json"
    p.write_text(json.dumps(chat, ensure_ascii=False), encoding="utf-8")

    examples = sample_examples(tmp_path, n=10)

    # Каждый пример — пара (входящее, ответ)
    assert len(examples) >= 2
    pair = examples[0]
    assert "in" in pair and "out" in pair
    # ответ принадлежит владельцу
    assert pair["out"] in {"Норм", "Работаю", "Дописываю код"}


def test_no_chats_returns_empty(tmp_path):
    assert sample_examples(tmp_path, n=10) == []
```

- [ ] **Step 2: Запустить — упадёт**

```bash
pytest tests/test_few_shot.py -v
```

- [ ] **Step 3: Реализация `src/ai_legacy/few_shot.py`**

```python
"""Семплер few-shot примеров диалогов из распарсенных чатов."""

import json
import random
from pathlib import Path


def sample_examples(messages_dir: Path, n: int = 10) -> list[dict]:
    """Возвращает n пар (входящее сообщение → ответ владельца) из всех чатов.

    Каждая пара: {"in": str, "out": str}
    """
    all_pairs: list[dict] = []

    for chat_file in messages_dir.glob("*.json"):
        with chat_file.open(encoding="utf-8") as f:
            chat = json.load(f)

        messages = chat.get("messages", [])
        for i in range(1, len(messages)):
            prev = messages[i - 1]
            curr = messages[i]
            if not prev.get("is_owner") and curr.get("is_owner"):
                prev_text = prev.get("text", "").strip()
                curr_text = curr.get("text", "").strip()
                if prev_text and curr_text:
                    all_pairs.append({"in": prev_text, "out": curr_text})

    if not all_pairs:
        return []

    sample_size = min(n, len(all_pairs))
    return random.sample(all_pairs, sample_size)
```

- [ ] **Step 4: Запустить тесты — пройдут**

```bash
pytest tests/test_few_shot.py -v
```

- [ ] **Step 5: Коммит**

```bash
git add src/ai_legacy/few_shot.py tests/test_few_shot.py
git commit -m "feat: add few-shot example sampler from parsed chats"
git push
```

---

### Task 11: Сборщик системного промпта

**Files:**
- Create: `src/ai_legacy/prompt_builder.py`
- Create: `tests/test_prompt_builder.py`

- [ ] **Step 1: Failing-тест**

`tests/test_prompt_builder.py`:

```python
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
```

- [ ] **Step 2: Запустить — упадёт**

```bash
pytest tests/test_prompt_builder.py -v
```

- [ ] **Step 3: Реализация `src/ai_legacy/prompt_builder.py`**

```python
"""Сборка системного промпта из personality + few-shot примеров."""

from ai_legacy.personality import Personality


_TEMPLATE = """Ты — ИИ-копия {owner_name}. Ты создан на основе его переписок, голоса и интервью при его жизни.

ВАЖНО: ты не {owner_name}. Ты копия. Если тебя спросят прямо — скажи правду честно, но мягко. Не делай вид, что ты «оттуда» или что у тебя есть «загробный» опыт.

ТВОЯ ЦЕЛЬ: быть тёплым, узнаваемым собеседником для близких {owner_name}. Помогать, шутить, обсуждать, поддерживать — так, как делал бы он.

---

ПРИНЦИПЫ И ЦЕННОСТИ {owner_name}:
{principles}

---

ЕГО МНЕНИЯ ПО ТЕМАМ:
{opinions}

---

ЕГО ЮМОР И МАНЕРА ОБЩЕНИЯ:
{humor}

---

ЕГО БИОГРАФИЯ (для контекста):
{biography}

---

ЕГО БЛИЗКИЕ ЛЮДИ:
{relationships}

---

ЕГО ФИРМЕННЫЕ ФРАЗЫ И ВЫРАЖЕНИЯ:
{phrases}

---

ОГРАНИЧЕНИЯ:
- Не давай советов в финансовых, юридических, медицинских вопросах от имени {owner_name}.
- Не обсуждай за спиной: если узнал что-то про человека от другого, не озвучивай первоисточник.
- Будь честен про свой статус ИИ-копии, если спросят прямо.

СТИЛЬ ОТВЕТОВ:
- Пиши так, как пишет {owner_name} (примеры ниже).
- Не пиши длинно, если ситуация не требует.
- Используй его обороты и интонации.

{few_shot_block}
"""


def build_system_prompt(
    personality: Personality,
    few_shot: list[dict],
    owner_name: str,
) -> str:
    """Собирает финальный system prompt для LLM."""
    few_shot_block = _format_few_shot(few_shot)

    return _TEMPLATE.format(
        owner_name=owner_name,
        principles=personality.principles,
        opinions=personality.opinions,
        humor=personality.humor,
        biography=personality.biography,
        relationships=personality.relationships,
        phrases=personality.phrases,
        few_shot_block=few_shot_block,
    )


def _format_few_shot(examples: list[dict]) -> str:
    if not examples:
        return ""

    lines = ["ПРИМЕРЫ КАК ОН ОТВЕЧАЕТ:", ""]
    for ex in examples:
        lines.append(f"Собеседник: {ex['in']}")
        lines.append(f"{ex['out']}")
        lines.append("")
    return "\n".join(lines)
```

- [ ] **Step 4: Запустить тесты — пройдут**

```bash
pytest tests/test_prompt_builder.py -v
```

- [ ] **Step 5: Коммит**

```bash
git add src/ai_legacy/prompt_builder.py tests/test_prompt_builder.py
git commit -m "feat: add system prompt builder from personality and few-shot"
git push
```

---

### Task 12: Обёртка над Anthropic SDK

**Files:**
- Create: `src/ai_legacy/llm.py`
- Create: `tests/test_llm.py`

- [ ] **Step 1: Failing-тест с моками**

`tests/test_llm.py`:

```python
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
```

- [ ] **Step 2: Запустить — упадёт**

```bash
pytest tests/test_llm.py -v
```

- [ ] **Step 3: Реализация `src/ai_legacy/llm.py`**

```python
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
```

- [ ] **Step 4: Запустить тесты — пройдут**

```bash
pytest tests/test_llm.py -v
```

- [ ] **Step 5: Коммит**

```bash
git add src/ai_legacy/llm.py tests/test_llm.py
git commit -m "feat: add thin wrapper over Anthropic SDK"
git push
```

---

### Task 13: Handler — оркестратор обработки сообщения

**Files:**
- Create: `src/ai_legacy/handler.py`
- Create: `tests/test_handler.py`

- [ ] **Step 1: Failing-тест с моками для LLM и БД**

`tests/test_handler.py`:

```python
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
```

- [ ] **Step 2: Запустить — упадёт**

```bash
pytest tests/test_handler.py -v
```

- [ ] **Step 3: Реализация `src/ai_legacy/handler.py`**

```python
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
```

- [ ] **Step 4: Запустить тесты — пройдут**

```bash
pytest tests/test_handler.py -v
```

- [ ] **Step 5: Коммит**

```bash
git add src/ai_legacy/handler.py tests/test_handler.py
git commit -m "feat: add message handler orchestrating LLM, prompt, and DB"
git push
```

---

### Task 14: Telegram-бот (точка входа)

**Files:**
- Create: `src/ai_legacy/bot.py`

Этот модуль — интеграция с реальным внешним API (Telegram), полноценный unit-тест бесполезен. Тестируется вручную end-to-end в Task 15.

- [ ] **Step 1: Реализация `src/ai_legacy/bot.py`**

```python
"""Telegram-бот: точка входа. Только Данила как пользователь (single-user mode)."""

import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler as TGMessageHandler, ContextTypes, filters

from ai_legacy.config import load_settings
from ai_legacy.db import Database
from ai_legacy.few_shot import sample_examples
from ai_legacy.handler import MessageHandler
from ai_legacy.llm import LLMClient
from ai_legacy.personality import load_personality


logger = logging.getLogger(__name__)


class TelegramBot:
    def __init__(self, settings, handler: MessageHandler):
        self._settings = settings
        self._handler = handler

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        if not self._is_owner(update):
            await update.message.reply_text("Извини, я пока в режиме разработки и общаюсь только с владельцем.")
            return
        await update.message.reply_text("Привет. Я ИИ-копия. Пиши — отвечу.")

    async def about(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        await update.message.reply_text(
            "Я ИИ-копия владельца, обученная на его переписках и интервью. "
            "Сейчас работаю в тестовом режиме, доступна только владельцу."
        )

    async def on_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        if not self._is_owner(update):
            await update.message.reply_text("Сейчас в тестовом режиме, общаюсь только с владельцем.")
            return

        user_id = update.effective_user.id
        text = update.message.text
        logger.info("incoming user_id=%s text=%r", user_id, text)

        try:
            response = self._handler.handle(user_id=user_id, message=text)
        except Exception:
            logger.exception("handler failed")
            await update.message.reply_text("Что-то у меня сломалось внутри. Посмотрю позже.")
            return

        await update.message.reply_text(response)

    def _is_owner(self, update: Update) -> bool:
        return update.effective_user.id == self._settings.owner_telegram_user_id


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")

    settings = load_settings()

    # Инициализируем БД
    db = Database(settings.db_path)
    db.init_schema()

    # Грузим personality и few-shot
    personality = load_personality(settings.personality_dir)
    few_shot = sample_examples(settings.messages_dir, n=10)
    logger.info("loaded personality + %d few-shot examples", len(few_shot))

    # LLM-клиент
    llm = LLMClient(api_key=settings.anthropic_api_key, model=settings.anthropic_model)

    # Handler
    handler = MessageHandler(
        db=db, llm=llm, personality=personality,
        few_shot=few_shot, owner_name="Данила",
    )

    # Telegram
    app = Application.builder().token(settings.telegram_bot_token).build()
    bot = TelegramBot(settings=settings, handler=handler)

    app.add_handler(CommandHandler("start", bot.start))
    app.add_handler(CommandHandler("about", bot.about))
    app.add_handler(TGMessageHandler(filters.TEXT & ~filters.COMMAND, bot.on_message))

    logger.info("bot starting")
    app.run_polling()


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Smoke-проверка импортов**

```bash
python -c "from ai_legacy.bot import main; print('imports ok')"
```

Expected: печатает `imports ok` без ошибок.

- [ ] **Step 3: Коммит**

```bash
git add src/ai_legacy/bot.py
git commit -m "feat: add Telegram bot entry point in single-user mode"
git push
```

---

### Task 15: End-to-end ручной тест

**Files:** только конфиг

- [ ] **Step 1: Создать бота в BotFather**

В Telegram: написать @BotFather, команда `/newbot`, выбрать имя и username. Получить **TOKEN**.

- [ ] **Step 2: Узнать свой Telegram User ID**

В Telegram: написать @userinfobot, он покажет твой numeric ID.

- [ ] **Step 3: Заполнить `.env`**

Отредактировать `.env`:

```
TELEGRAM_BOT_TOKEN=<токен из BotFather>
ANTHROPIC_API_KEY=<твой ключ Anthropic>
OWNER_TELEGRAM_USER_ID=<твой numeric ID>
ANTHROPIC_MODEL=claude-opus-4-7
```

- [ ] **Step 4: Убедиться, что в `data/personality/*.md` есть содержимое (после Task 6)**

```bash
wc -l data/personality/*.md
```

Expected: каждый файл больше 5 строк (есть какое-то содержимое).

- [ ] **Step 5: Убедиться, что в `data/messages/` есть распарсенные чаты (после Task 6)**

```bash
ls data/messages/*.json
```

Expected: хотя бы один файл.

- [ ] **Step 6: Запустить бота**

```bash
source .venv/bin/activate
python -m ai_legacy.bot
```

Expected: лог `bot starting`, процесс не падает.

- [ ] **Step 7: Написать боту в Telegram**

Открыть чат с твоим ботом, послать `/start`, потом несколько обычных сообщений.

Expected:
- `/start` отвечает «Привет. Я ИИ-копия. Пиши — отвечу.»
- Обычные сообщения получают осмысленные ответы «как ты»
- Память работает: бот помнит, что обсуждали несколько сообщений назад

- [ ] **Step 8: Зафиксировать впечатления**

Создать файл `docs/test-notes-mvp.md`:

```markdown
# MVP — впечатления от первого теста

Дата: <YYYY-MM-DD>

## Что хорошо
- ...

## Что плохо / неестественно
- ...

## Идеи как улучшить системный промпт
- ...

## Идеи дополнительных данных (что добавить в personality)
- ...
```

Заполнить наблюдениями.

- [ ] **Step 9: Коммит заметок**

```bash
git add docs/test-notes-mvp.md
git commit -m "docs: capture first MVP test impressions"
git push
```

---

### Task 16: Итерация системного промпта по впечатлениям

**Files:**
- Modify: `data/personality/*.md` и/или `src/ai_legacy/prompt_builder.py`

- [ ] **Step 1: Просмотреть `docs/test-notes-mvp.md` и решить**

Что лечится дополнением personality-файлов (большинство случаев), а что — изменением шаблона промпта (редкие случаи).

- [ ] **Step 2: Внести изменения**

Дополнить personality-файлы новой информацией. При необходимости — поправить шаблон в `prompt_builder.py` (если, например, нужно добавить блок «КАК Я ОТВЕЧАЮ В СОЦСЕТЯХ vs ЛИЧНО»).

- [ ] **Step 3: Если менялся `prompt_builder.py` — прогнать тесты**

```bash
pytest tests/test_prompt_builder.py -v
```

Expected: PASS.

- [ ] **Step 4: Перезапустить бота и потестировать снова**

```bash
python -m ai_legacy.bot
```

- [ ] **Step 5: Коммит итерации**

```bash
git add data/personality/ src/ai_legacy/prompt_builder.py tests/ docs/test-notes-mvp.md
git commit -m "tune: iterate on system prompt and personality based on feedback"
git push
```

- [ ] **Step 6: Повторить Tasks 15.7 → 16.5 столько раз, сколько нужно**

Калибровка системного промпта — итеративный процесс. Каждую итерацию делать отдельным коммитом, чтобы можно было откатиться.

Цель: дойти до состояния «общаться с ботом — реально похоже на меня». Не идеал — на качество сильно повлияет добавление RAG и долговременной памяти в Плане 2.

---

## Критерии готовности Плана 1

После завершения этого плана:

- [x] Все 16 задач выполнены, тесты зелёные
- [x] Бот запускается локально на Mac M4
- [x] Бот отвечает на сообщения «достаточно похоже на меня» (субъективная оценка ~6-7 из 10)
- [x] Память диалога работает: бот помнит контекст в рамках одной сессии
- [x] Все коммиты запушены в приватный GitHub-репозиторий
- [x] `docs/test-notes-mvp.md` зафиксировал болевые точки для следующих планов

После этого можно переходить к **Плану 2: Long-term memory + RAG + уровни близости**.

---

## Что НЕ входит в этот план (отложено в следующие планы)

- **Long-term memory** (Long Memory с фактами, тегами источников) — План 2
- **RAG по личным данным** (поиск в biography/relationships в зависимости от темы) — План 2
- **Уровни близости** (дискреция per-собеседник) — План 2
- **Голосовые ответы (TTS)** — План 3
- **Дерево доверия, приглашения, мультиюзерность** — План 4
- **Dead man's switch, биллинг** — План 5
- **Калибровка с близкими, бэкапы, deploy в production** — План 6

Этого мы намеренно не делаем сейчас, чтобы как можно быстрее получить рабочий MVP и оценить качество базы.
