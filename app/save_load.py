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

Version history:
    1 — original session structure
    2 — dual specials, active effects (dot_damage, buff_stat, shield_pct etc)
    3 — NG+ keys (ng_plus, ng_plus_mode, ng_plus_souls_carried)
          shadow realm keys (secret_chapters, secret_return_chapter)
          damage type keys (magic_attack, magic_defense on enemy/character)
          Commit 3 will bump to 4 when run_stats is added.
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
#
# IMPORTANT: whenever you add a new session key anywhere in the codebase,
# add it to SESSION_DEFAULTS below AND bump SAVE_VERSION.
SAVE_VERSION = 3

# ── Session defaults ──────────────────────────────────────────────────────────
# Canonical list of every session key used across the app and its safe default.
# load_game() uses this to backfill keys missing from older saves.
#
# Organised by logical group to make additions easy to locate.
SESSION_DEFAULTS = {

    # ── Character & run identity ───────────────────────────────────────────
    "character":            {},
    "gift":                 "fading_soul",
    "chapter":              0,
    "choices":              [],
    "rested_here":          False,

    # ── Vitals ────────────────────────────────────────────────────────────
    "hp":                   100,
    "estus":                5,
    "estus_max":            5,
    "mp":                   0,
    "souls":                0,

    # ── Combat state ──────────────────────────────────────────────────────
    "enemy":                {},
    "enemy_is_boss":        False,
    "chapter_after_battle": 0,
    "battle_bg":            "images/areas/undead_settlement.jpg",
    "boss_phase":           1,
    "phase_changed":        False,
    "predicted_move":       None,
    "predicted_msg":        None,
    "special_cooldown":     0,
    "stunned":              False,
    "smoke_screen_active":  False,
    "shop_bought":          [],

    # ── Active effects (dual specials — Commit 21 / refactor) ─────────────
    "dot_damage":           0,
    "dot_turns":            0,
    "dot_label":            "",
    "buff_stat":            None,
    "buff_amount":          0,
    "buff_turns":           0,
    "buff_label":           "",
    "shield_pct":           0.0,
    "shield_turns":         0,

    # ── New Game+ (Commit 2) ───────────────────────────────────────────────
    # ng_plus       — current NG+ depth (0 = first run, 1 = NG+, etc.)
    # ng_plus_mode  — 'new_journey' or 'legacy' (set during NG+ entry)
    # ng_plus_souls_carried — souls carried after cap (display only)
    "ng_plus":              0,
    "ng_plus_mode":         "new_journey",
    "ng_plus_souls_carried": 0,

    # ── Shadow realm (refactor) ────────────────────────────────────────────
    "secret_chapters":        [],
    "secret_return_chapter":  0,
}

# ── Basic type validation ─────────────────────────────────────────────────────
# Maps key → expected Python type. Checked on load; mismatches are corrected
# using SESSION_DEFAULTS rather than crashing.
_EXPECTED_TYPES = {
    # Core
    "character":             dict,
    "chapter":               int,
    "hp":                    (int, float),
    "estus":                 int,
    "estus_max":             int,
    "mp":                    (int, float),
    "souls":                 (int, float),
    "shop_bought":           list,
    "choices":               list,
    # Combat
    "enemy":                 dict,
    "boss_phase":            int,
    "special_cooldown":      int,
    "chapter_after_battle":  int,
    # Active effects
    "dot_damage":            (int, float),
    "dot_turns":             int,
    "buff_amount":           (int, float),
    "buff_turns":            int,
    "shield_pct":            float,
    "shield_turns":          int,
    # NG+
    "ng_plus":               int,
    "ng_plus_souls_carried": (int, float),
    # Shadow realm
    "secret_chapters":       list,
    "secret_return_chapter": int,
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
        print(f"[INFO] Save version {saved_version} → {SAVE_VERSION}. "
              f"Backfilling missing keys with defaults.")

    # ── Backfill missing keys ──────────────────────────────────────────────
    for key, default in SESSION_DEFAULTS.items():
        if key not in data:
            data[key] = default
            if saved_version < SAVE_VERSION:
                print(f"[INFO]  backfilled '{key}' = {default!r}")

    # ── Type validation ────────────────────────────────────────────────────
    for key, expected in _EXPECTED_TYPES.items():
        val = data.get(key)
        if val is not None and not isinstance(val, expected):
            default = SESSION_DEFAULTS.get(key)
            print(f"[WARN] load_game: '{key}' expected {expected}, "
                  f"got {type(val).__name__}. Resetting to default.")
            data[key] = default

    # ── Legacy run HP guard ────────────────────────────────────────────────
    # Bearer's Legacy runs may have max_hp higher than the class base.
    # Ensure loaded hp never exceeds the saved character's max_hp.
    char = data.get("character", {})
    saved_hp = data.get("hp", 0)
    saved_max = char.get("max_hp", saved_hp)
    if saved_hp > saved_max:
        print(f"[WARN] load_game: hp ({saved_hp}) > max_hp ({saved_max}). Clamping.")
        data["hp"] = saved_max

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