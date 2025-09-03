# tests/test_story_integrity.py

import os
import json
import pytest

CHAPTERS_DIR = "app/story/chapters"
CHOICE_MAP_PATH = "app/story/choices_mapping.json"
BOSSES_PATH = "app/enemies.py"

def load_boss_names():
    """Load boss keys from enemies.py without executing the file."""
    with open(BOSSES_PATH, "r", encoding="utf-8") as f:
        content = f.read()
    lines = content.splitlines()
    boss_names = []
    for line in lines:
        if line.strip().startswith('"') and ":" in line and "hp" in line:
            boss_name = line.strip().split(":")[0].strip().strip('"')
            boss_names.append(boss_name)
    return boss_names

def load_choice_map():
    with open(CHOICE_MAP_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def load_chapter(chapter_id):
    path = os.path.join(CHAPTERS_DIR, f"{chapter_id}.json")
    if not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def get_all_chapter_ids():
    return sorted([int(fname.replace(".json", "")) for fname in os.listdir(CHAPTERS_DIR) if fname.endswith(".json")])

def pytest_generate_tests(metafunc):
    if "chapter_id" in metafunc.fixturenames:
        metafunc.parametrize("chapter_id", get_all_chapter_ids())

def test_chapter_structure(chapter_id):
    data = load_chapter(chapter_id)
    assert data is not None, f"Chapter {chapter_id} is missing"

    # Ensure required fields
    assert "text" in data, f"Chapter {chapter_id} missing 'text'"
    assert "choices" in data, f"Chapter {chapter_id} missing 'choices'"
    assert isinstance(data["choices"], list), f"Chapter {chapter_id} 'choices' must be a list"

    # Optional validations
    if data.get("battle") and data.get("boss"):
        boss_name = data.get("boss_name")
        if not boss_name:
            print(f"⚠️  Chapter {chapter_id} has boss battle but no 'boss_name'")
        else:
            bosses = load_boss_names()
            if boss_name not in bosses:
                print(f"⚠️  Chapter {chapter_id} boss '{boss_name}' not in BOSSES. Will default to Cindergloom.")

def test_choice_mapping_connectivity():
    choice_map = load_choice_map()
    chapter_ids = get_all_chapter_ids()
    all_targets = set(chapter_ids)

    missing_targets = []
    for choice, target in choice_map.items():
        if target not in all_targets:
            missing_targets.append((choice, target))

    assert not missing_targets, f"Choices point to missing chapters: {missing_targets}"

