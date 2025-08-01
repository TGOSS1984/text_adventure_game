import json
import os

BASE_DIR = os.path.dirname(__file__)
CHAPTERS_DIR = os.path.join(BASE_DIR, "chapters")
CHOICES_PATH = os.path.join(BASE_DIR, "choices_mapping.json")

def load_chapter(chapter_id):
    filepath = os.path.join(CHAPTERS_DIR, f"{chapter_id}.json")
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {"text": "Unknown", "choices": []}

def load_choice_mapping():
    try:
        with open(CHOICES_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}