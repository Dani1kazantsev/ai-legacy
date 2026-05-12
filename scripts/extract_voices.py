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
