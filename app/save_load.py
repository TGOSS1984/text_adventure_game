"""
save_load.py

Handles saving and loading game progress using Flask's session object.
"""

import json


def save_game(session):
    with open("savegame.json", "w") as f:
        json.dump(dict(session), f)


def load_game(session):
    try:
        with open("savegame.json", "r") as f:
            data = json.load(f)
            session.update(data)
    except FileNotFoundError:
        pass
