"""
save_load.py

Handles saving and loading game progress using Flask's session object.

Save file is written to a 'saves/' directory alongside the app rather than
the process working directory, so it survives server restarts on most hosts.

NOTE: This is a flat-file save system suitable for single-player / development.
For multi-user or production deployments, replace with a database-backed
solution (e.g. SQLAlchemy SaveSlot model) in a future commit.
"""

import json
import os

# Resolve saves directory relative to this file so it works regardless of
# where the process is launched from.
_SAVES_DIR = os.path.join(os.path.dirname(__file__), '..', 'saves')
_SAVE_PATH = os.path.join(_SAVES_DIR, 'savegame.json')

# Keys that should never be persisted (Flask internals / security tokens)
_SKIP_KEYS = {'_flashes', '_csrf_token'}


def _ensure_saves_dir():
    """Create the saves directory if it doesn't exist."""
    os.makedirs(_SAVES_DIR, exist_ok=True)


def save_game(session):
    """
    Persist the current game state to disk.

    Filters out Flask-internal session keys before writing so that
    security tokens and flash messages are never saved.
    """
    _ensure_saves_dir()
    data = {k: v for k, v in dict(session).items() if k not in _SKIP_KEYS}
    try:
        with open(_SAVE_PATH, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
    except OSError as e:
        # Log but don't crash — the player can retry
        print(f"[WARN] save_game failed: {e}")


def load_game(session):
    """
    Load a previously saved game state into the current session.

    Returns True if a save was found and loaded, False otherwise.
    """
    try:
        with open(_SAVE_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)
        session.update(data)
        return True
    except FileNotFoundError:
        return False
    except (json.JSONDecodeError, OSError) as e:
        print(f"[WARN] load_game failed: {e}")
        return False


def has_save():
    """Return True if a save file exists on disk."""
    return os.path.isfile(_SAVE_PATH)


def delete_save():
    """Remove the save file (used on New Game to avoid stale data)."""
    try:
        os.remove(_SAVE_PATH)
    except FileNotFoundError:
        pass