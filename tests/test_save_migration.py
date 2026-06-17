# tests/test_save_migration.py
"""
Verifies that an old-format save (pre-Commit 8, "v4") loads cleanly
through save_load.load_game() and ends up fully backfilled to the
current SAVE_VERSION, instead of crashing or silently missing keys.

This was previously an unverified assumption ("the migration should
work, the backfill logic looks generic enough") — this test exercises
the actual backfill / type-validation code path against a real
v4-shaped save dict, so future changes to SESSION_DEFAULTS or
_EXPECTED_TYPES that break old saves get caught here instead of in
a player's browser.
"""

import json
import os
import shutil

import pytest

from app.save_load import SAVE_VERSION, _SAVE_PATH, _SAVES_DIR, load_game

# A representative v4 save — only the keys that existed at that version.
# Missing: hot_dmg/hot_turns/parry_turns/parry_counter_pct (added in v5),
# shadow_realm_completed (added in v6), ng_plus_mode, and several others.
OLD_V4_SAVE = {
    "character": {"class_name": "Knight", "char_class": "Knight", "max_hp": 100},
    "gift": "fading_soul",
    "chapter": 12,
    "choices": ["some_choice"],
    "hp": 80,
    "estus": 3,
    "estus_max": 5,
    "mp": 20,
    "souls": 150,
    "enemy": {},
    "ng_plus": 0,
    "ng_plus_souls_carried": 0,
    "secret_chapters": [],
    "secret_return_chapter": 0,
    "run_stats": {"enemies_defeated": 2},
    "_save_version": 4,
}


@pytest.fixture
def isolated_save_file():
    """
    Back up any real save file, write OLD_V4_SAVE in its place for the
    duration of the test, then restore the original (or remove the test
    file if there wasn't one). Prevents this test from clobbering a
    developer's actual saves/savegame.json.
    """
    os.makedirs(_SAVES_DIR, exist_ok=True)
    backup_path = _SAVE_PATH + ".bak_test"
    had_existing = os.path.exists(_SAVE_PATH)
    if had_existing:
        shutil.move(_SAVE_PATH, backup_path)

    with open(_SAVE_PATH, "w", encoding="utf-8") as f:
        json.dump(OLD_V4_SAVE, f)

    yield

    if os.path.exists(_SAVE_PATH):
        os.remove(_SAVE_PATH)
    if had_existing:
        shutil.move(backup_path, _SAVE_PATH)


def test_v4_save_loads_successfully(isolated_save_file):
    session = {}
    assert load_game(session) is True


def test_v4_save_backfills_keys_added_in_v5_and_v6(isolated_save_file):
    session = {}
    load_game(session)

    # v5 additions (hot_dmg/hot_turns — Barbarian HoT; parry_turns/
    # parry_counter_pct — Samurai auto-counter)
    assert session["hot_dmg"] == 0
    assert session["hot_turns"] == 0
    assert session["parry_turns"] == 0
    assert session["parry_counter_pct"] == 0.0

    # v6 addition
    assert session["shadow_realm_completed"] is False


def test_v4_save_backfills_run_stats_subkeys(isolated_save_file):
    session = {}
    load_game(session)

    stats = session["run_stats"]
    # Original v4 value preserved...
    assert stats["enemies_defeated"] == 2
    # ...and every newer sub-key backfilled to its default so templates
    # using .get() defaults never see a missing key.
    for key in (
        "bosses_defeated", "bosses_list", "damage_dealt", "damage_taken",
        "estus_used", "specials_fired", "souls_earned",
        "chapters_visited", "crits_landed",
    ):
        assert key in stats


def test_v4_save_preserves_original_progress_data(isolated_save_file):
    session = {}
    load_game(session)

    assert session["chapter"] == 12
    assert session["souls"] == 150
    assert session["hp"] == 80
    assert session["choices"] == ["some_choice"]


def test_current_save_version_is_6():
    """
    Documents the expectation set in the Chunk 2 review: the project's
    current SAVE_VERSION is 6. If this fails, the migration tests above
    and their OLD_V4_SAVE fixture comments need a matching update.
    """
    assert SAVE_VERSION == 6