"""
save_load.py

Handles saving and loading game progress using Flask's session object.

Save file is written to a 'saves/' directory alongside the app rather than
the process working directory, so it survives server restarts on most hosts.

NOTE: This is a flat-file save system suitable for single-player / development.
For multi-user or production deployments, replace with a database-backed
solution (e.g. SQLAlchemy SaveSlot model) in a future commit.

Version history:
    1 — original session structure
    2 — dual specials, active effects (dot_damage, buff_stat, shield_pct etc)
    3 — NG+ keys, shadow realm keys, damage type keys on enemy/character
    4 — run_stats dict, last_counted_chapter (Commit 3)
    5 — hot_dmg, hot_turns, parry_turns, parry_counter_pct (Commit 8)
"""

import json
import os

_SAVES_DIR = os.path.join(os.path.dirname(__file__), '..', 'saves')
_SAVE_PATH = os.path.join(_SAVES_DIR, 'savegame.json')

_SKIP_KEYS = {'_flashes', '_csrf_token'}

# ── Versioning ────────────────────────────────────────────────────────────────
# Bump whenever session structure changes. Old saves are backfilled from
# SESSION_DEFAULTS for any missing keys.
SAVE_VERSION = 5

# ── Session defaults ──────────────────────────────────────────────────────────
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

    # ── Active effects ─────────────────────────────────────────────────────
    "dot_damage":           0,
    "dot_turns":            0,
    "dot_label":            "",
    "buff_stat":            None,
    "buff_amount":          0,
    "buff_turns":           0,
    "buff_label":           "",
    "shield_pct":           0.0,
    "shield_turns":         0,

    # ── Commit 8: new active effects ───────────────────────────────────────
    # hot_dmg / hot_turns — Barbarian Berserker Rage heal-over-time
    # parry_turns / parry_counter_pct — Samurai Iron Stance auto-counter
    "hot_dmg":              0,
    "hot_turns":            0,
    "parry_turns":          0,
    "parry_counter_pct":    0.0,

    # ── New Game+ (Commit 2) ───────────────────────────────────────────────
    "ng_plus":               0,
    "ng_plus_mode":          "new_journey",
    "ng_plus_souls_carried": 0,

    # ── Shadow realm ──────────────────────────────────────────────────────
    "secret_chapters":       [],
    "secret_return_chapter": 0,

    # ── Run stats (Commit 3) ───────────────────────────────────────────────
    # Stored as a nested dict. Backfilled as an empty dict on old saves —
    # the display templates handle missing sub-keys with .get() defaults.
    "run_stats": {
        "enemies_defeated": 0,
        "bosses_defeated":  0,
        "bosses_list":      [],
        "damage_dealt":     0,
        "damage_taken":     0,
        "estus_used":       0,
        "specials_fired":   0,
        "souls_earned":     0,
        "chapters_visited": 0,
        "crits_landed":     0,
    },
    "last_counted_chapter":  -1,
}

# ── Type validation ────────────────────────────────────────────────────────────
_EXPECTED_TYPES = {
    "character":             dict,
    "chapter":               int,
    "hp":                    (int, float),
    "estus":                 int,
    "estus_max":             int,
    "mp":                    (int, float),
    "souls":                 (int, float),
    "shop_bought":           list,
    "choices":               list,
    "enemy":                 dict,
    "boss_phase":            int,
    "special_cooldown":      int,
    "chapter_after_battle":  int,
    "dot_damage":            (int, float),
    "dot_turns":             int,
    "buff_amount":           (int, float),
    "buff_turns":            int,
    "shield_pct":            float,
    "shield_turns":          int,
    # Commit 8: new active effect types
    "hot_dmg":               (int, float),
    "hot_turns":             int,
    "parry_turns":           int,
    "parry_counter_pct":     float,
    "ng_plus":               int,
    "ng_plus_souls_carried": (int, float),
    "secret_chapters":       list,
    "secret_return_chapter": int,
    "run_stats":             dict,
    "last_counted_chapter":  int,
}


def _ensure_saves_dir():
    os.makedirs(_SAVES_DIR, exist_ok=True)


def save_game(session):
    """Persist the current game state to disk."""
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
    Backfills missing keys, validates types, clamps HP.
    Returns True on success, False if no save or corrupt file.
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
              f"Backfilling missing keys.")

    # Backfill missing top-level keys
    for key, default in SESSION_DEFAULTS.items():
        if key not in data:
            data[key] = default
            if saved_version < SAVE_VERSION:
                print(f"[INFO]  backfilled '{key}'")

    # Backfill missing sub-keys inside run_stats
    # (handles saves from before Commit 3 that have an empty run_stats dict)
    default_stats = SESSION_DEFAULTS["run_stats"]
    loaded_stats  = data.get("run_stats", {})
    if isinstance(loaded_stats, dict):
        for sub_key, sub_default in default_stats.items():
            if sub_key not in loaded_stats:
                loaded_stats[sub_key] = sub_default
        data["run_stats"] = loaded_stats

    # Type validation
    for key, expected in _EXPECTED_TYPES.items():
        val = data.get(key)
        if val is not None and not isinstance(val, expected):
            default = SESSION_DEFAULTS.get(key)
            print(f"[WARN] load_game: '{key}' expected {expected}, "
                  f"got {type(val).__name__}. Resetting to default.")
            data[key] = default

    # HP clamp — Bearer's Legacy max_hp may differ from class base
    char     = data.get("character", {})
    saved_hp = data.get("hp", 0)
    saved_max = char.get("max_hp", saved_hp)
    if saved_hp > saved_max:
        print(f"[WARN] load_game: hp ({saved_hp}) > max_hp ({saved_max}). Clamping.")
        data["hp"] = saved_max

    session.update(data)
    return True


def has_save():
    return os.path.isfile(_SAVE_PATH)


def delete_save():
    try:
        os.remove(_SAVE_PATH)
    except FileNotFoundError:
        pass