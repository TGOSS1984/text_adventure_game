import json
import os
from functools import lru_cache

BASE_DIR = os.path.dirname(__file__)
CHAPTERS_DIR = os.path.join(BASE_DIR, "chapters")
CHOICES_PATH = os.path.join(BASE_DIR, "choices_mapping.json")

# ── Caching ───────────────────────────────────────────────────────────────
# Previously these two functions hit the filesystem on EVERY call — not
# just at cold start, but on every single chapter navigation for the
# entire life of the process (150+ chapter files, each re-read from disk
# every time any player walks through the story). lru_cache turns that
# into one disk read per chapter/file for the whole process lifetime.
#
# Safe because both callers (story_engine.py) only ever read from the
# returned dict (.get(...)) and never mutate it in place — confirmed by
# checking every load_chapter()/load_choice_mapping() call site.
#
# Chapter content and choices_mapping.json are static game data that
# doesn't change while the server is running. If you're editing chapter
# JSON files live during development, restart the dev server (or call
# load_chapter.cache_clear() / load_choice_mapping.cache_clear()) to see
# changes — they will NOT hot-reload otherwise.


@lru_cache(maxsize=None)
def load_chapter(chapter_id):
    filepath = os.path.join(CHAPTERS_DIR, f"{chapter_id}.json")
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {"text": "Unknown", "choices": []}


@lru_cache(maxsize=None)
def load_choice_mapping():
    try:
        with open(CHOICES_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}