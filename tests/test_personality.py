from pathlib import Path
from ai_legacy.personality import load_personality


def test_loads_all_personality_files(tmp_path):
    (tmp_path / "principles.md").write_text("# Принципы\n- Честность")
    (tmp_path / "opinions.md").write_text("# Мнения\nЯ за свободу.")
    (tmp_path / "humor.md").write_text("# Юмор\nСаркастичный.")
    (tmp_path / "biography.md").write_text("# Био\nРодился в Москве.")
    (tmp_path / "relationships.md").write_text("# Отношения\n## Жена\nИрина")
    (tmp_path / "phrases.md").write_text("# Фразы\n- Чики-пуки")
    (tmp_path / "behavior.md").write_text("# Поведение\nКороткие реплики.")

    p = load_personality(tmp_path)

    assert "Честность" in p.principles
    assert "свободу" in p.opinions
    assert "Саркастичный" in p.humor
    assert "Москве" in p.biography
    assert "Ирина" in p.relationships
    assert "Чики-пуки" in p.phrases
    assert "Короткие реплики" in p.behavior


def test_missing_file_raises(tmp_path):
    import pytest
    (tmp_path / "principles.md").write_text("a")
    with pytest.raises(FileNotFoundError):
        load_personality(tmp_path)
