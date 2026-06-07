"""
save_load.py

Handles saving and loading game progress using Flask's session object.

Save file is written to a 'saves/' directory alongside the app rather than
the process working directory, so it survives server restarts on most hosts.

NOTE: This is a flat-file save system suitable for single-player / development.
For multi-user or production deployments, replace with a database-backed
solution (e.g. SQLAlchemy SaveSlot model) in a future commit.

Refactor additions:
- SAVE_VERSION: integer bumped whenever session structure changes.
  Loaded saves with an older version get missing keys backfilled with
  SESSION_DEFAULTS so old saves never cause KeyErrors on new fields.
- SESSION_DEFAULTS: canonical list of every session key and its default value.
  When adding a new session key anywhere in the codebase, add it here too.
  load_game() uses this to backfill missing keys from old saves.
- Basic type/structure validation on load — rejects saves where core fields
  are the wrong type to prevent corrupted data reaching route logic.
"""

import json
import os

# ── Save file location ────────────────────────────────────────────────────────
_SAVES_DIR = os.path.join(os.path.dirname(__file__), '..', 'saves')
_SAVE_PATH = os.path.join(_SAVES_DIR, 'savegame.json')

# Keys that should never be persisted (Flask internals / security tokens)
_SKIP_KEYS = {'_flashes', '_csrf_token'}

# ── Versioning ────────────────────────────────────────────────────────────────
# Bump this integer whenever the session structure changes (new keys, renamed
# keys, changed types). Old saves will be backfilled with SESSION_DEFAULTS
# for any missing keys rather than crashing.
SAVE_VERSION = 2

# ── Session defaults ──────────────────────────────────────────────────────────
# Canonical list of every session key used across the app and its safe default.
# When you add a new session key anywhere: add it here too.
# load_game() uses this to backfill keys missing from older saves.
SESSION_DEFAULTS = {
    "character":           {},
    "chapter":             0,
    "hp":                  100,
    "enemy":               {},
    "enemy_is_boss":       False,
    "estus":               5,
    "estus_max":           5,
    "mp":                  0,
    "special_cooldown":    0,
    "stunned":             False,
    "smoke_screen_active": False,
    "souls":               0,
    "shop_bought":         [],
    "boss_phase":          1,
    "phase_changed":       False,
    "predicted_move":      None,
    "predicted_msg":       None,
    "battle_bg":           "images/areas/undead_settlement.jpg",
    "chapter_after_battle": 0,
    "gift":                "fading_soul",
    "rested_here":         False,
    "choices":             [],
}

# ── Basic type validation ─────────────────────────────────────────────────────
# Maps key → expected Python type. Checked on load; mismatches are corrected
# using SESSION_DEFAULTS rather than crashing.
_EXPECTED_TYPES = {
    "character":        dict,
    "chapter":          int,
    "hp":               (int, float),
    "enemy":            dict,
    "estus":            int,
    "estus_max":        int,
    "mp":               (int, float),
    "special_cooldown": int,
    "souls":            (int, float),
    "shop_bought":      list,
    "boss_phase":       int,
}


def _ensure_saves_dir():
    """Create the saves directory if it doesn't exist."""
    os.makedirs(_SAVES_DIR, exist_ok=True)


def save_game(session):
    """
    Persist the current game state to disk.

    Filters out Flask-internal session keys before writing.
    Writes SAVE_VERSION so load_game() can detect and migrate old saves.
    """
    _ensure_saves_dir()
    data = {k: v for k, v in dict(session).items() if k not in _SKIP_KEYS}
    data["_save_version"] = SAVE_VERSION
    try:
        with open(_SAVE_PATH, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
    except OSError as e:
        print(f"[WARN] save_game failed: {e}")


def load_game(session):
    """
    Load a previously saved game state into the current session.

    - Backfills any keys missing from old saves using SESSION_DEFAULTS.
    - Corrects any keys whose values are the wrong type.
    - Returns True if a save was found and loaded, False otherwise.
    """
    try:
        with open(_SAVE_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        return False
    except (json.JSONDecodeError, OSError) as e:
        print(f"[WARN] load_game failed: {e}")
        return False

    saved_version = data.pop("_save_version", 0)
    if saved_version < SAVE_VERSION:
        print(f"[INFO] Save version {saved_version} < current {SAVE_VERSION}. "
              f"Backfilling missing keys with defaults.")

    # ── Backfill missing keys from SESSION_DEFAULTS ────────────────────────
    for key, default in SESSION_DEFAULTS.items():
        if key not in data:
            data[key] = default
            if saved_version < SAVE_VERSION:
                print(f"[INFO]  backfilled '{key}' = {default!r}")

    # ── Type validation — correct wrong types rather than crashing ─────────
    for key, expected in _EXPECTED_TYPES.items():
        val = data.get(key)
        if val is not None and not isinstance(val, expected):
            default = SESSION_DEFAULTS.get(key)
            print(f"[WARN] load_game: '{key}' expected {expected}, "
                  f"got {type(val).__name__}. Resetting to default.")
            data[key] = default

    session.update(data)
    return True


def has_save():
    """Return True if a save file exists on disk."""
    return os.path.isfile(_SAVE_PATH)


def delete_save():
    """Remove the save file (used on New Game to avoid stale data)."""
    try:
        os.remove(_SAVE_PATH)
    except FileNotFoundError:
        pass