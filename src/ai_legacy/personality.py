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
