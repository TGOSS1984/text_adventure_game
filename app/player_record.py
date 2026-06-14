"""
player_record.py

Persistent cross-run player data that survives /restart.

Unlike savegame.json (which is deleted on /restart to start fresh),
player_record.json tracks permanent progress that should never be lost:
    - unlocked_classes: class names unlocked through gameplay
    - total_runs: number of completed runs (incremented on ending chapters)

Stored in the same saves/ directory as savegame.json.
On Heroku (ephemeral filesystem): data persists within a dyno session but
resets on dyno restart. This is the same limitation as the existing save system.

Usage:
    from .player_record import get_record, save_record, unlock_class, is_unlocked

Adding a new unlock condition:
    1. Add the class to CLASSES in classes.py with unlocked_by_default=False
    2. Call unlock_class('ClassName') at the appropriate trigger point
    3. Document the condition in the class's unlock_condition field
"""

import json
import os
from .classes import CLASSES

_SAVES_DIR     = os.path.join(os.path.dirname(__file__), '..', 'saves')
_RECORD_PATH   = os.path.join(_SAVES_DIR, 'player_record.json')


def _ensure_saves_dir():
    os.makedirs(_SAVES_DIR, exist_ok=True)


def _default_record():
    """
    Return a fresh player record with all default-unlocked classes pre-populated.
    Classes with unlocked_by_default=True are always in the unlocked list.
    """
    default_unlocked = [
        name for name, cls in CLASSES.items()
        if cls.get('unlocked_by_default', True)
    ]
    return {
        "unlocked_classes": default_unlocked,
        "total_runs":       0,
    }


def get_record():
    """
    Load the player record from disk. Returns default record if not found.
    Always backfills default-unlocked classes in case new ones were added.
    """
    _ensure_saves_dir()
    try:
        with open(_RECORD_PATH, 'r', encoding='utf-8') as f:
            record = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        record = _default_record()
        _write_record(record)
        return record

    # Backfill any newly added default-unlocked classes
    default_unlocked = [
        name for name, cls in CLASSES.items()
        if cls.get('unlocked_by_default', True)
    ]
    changed = False
    for name in default_unlocked:
        if name not in record.get('unlocked_classes', []):
            record.setdefault('unlocked_classes', []).append(name)
            changed = True

    if changed:
        _write_record(record)

    return record


def _write_record(record):
    """Write the record dict to disk."""
    _ensure_saves_dir()
    try:
        with open(_RECORD_PATH, 'w', encoding='utf-8') as f:
            json.dump(record, f, indent=2)
    except OSError as e:
        print(f"[WARN] player_record save failed: {e}")


def get_unlocked_names():
    """Return the set of currently unlocked class names."""
    return set(get_record().get('unlocked_classes', []))


def is_unlocked(class_name):
    """Return True if the given class name is unlocked."""
    return class_name in get_unlocked_names()


def unlock_class(class_name):
    """
    Unlock a class by name. No-op if already unlocked or not in CLASSES.
    Returns True if this was a new unlock, False if already unlocked.
    """
    if class_name not in CLASSES:
        print(f"[WARN] unlock_class: '{class_name}' not in CLASSES.")
        return False

    record = get_record()
    if class_name in record.get('unlocked_classes', []):
        return False  # already unlocked

    record.setdefault('unlocked_classes', []).append(class_name)
    _write_record(record)
    print(f"[INFO] Unlocked class: {class_name}")
    return True


def increment_total_runs():
    """Increment the total completed runs counter."""
    record = get_record()
    record['total_runs'] = record.get('total_runs', 0) + 1
    _write_record(record)
    return record['total_runs']