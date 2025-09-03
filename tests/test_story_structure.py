import os
import json

# Load all chapter files
CHAPTERS_DIR = "app/story/chapters"
ALL_CHAPTERS = {}

for filename in os.listdir(CHAPTERS_DIR):
    if filename.endswith(".json"):
        path = os.path.join(CHAPTERS_DIR, filename)
        with open(path, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
                chapter_id = int(filename.replace(".json", ""))
                ALL_CHAPTERS[chapter_id] = data
            except Exception as e:
                print(f"❌ Error loading {filename}: {e}")

# Load mapping (choice → chapter)
with open("app/story/choices_mapping.json", "r", encoding="utf-8") as f:
    CHOICE_MAP = json.load(f)

# 1. Check for valid chapter links
invalid_links = []
for choice, target in CHOICE_MAP.items():
    if target not in ALL_CHAPTERS:
        invalid_links.append((choice, target))

if invalid_links:
    print("\n❌ Invalid chapter links found:")
    for choice, target in invalid_links:
        print(f"  Choice '{choice}' maps to missing chapter {target}")
else:
    print("✅ All choice mappings resolve to existing chapters.")

# 2. Traverse all paths recursively and track visited
visited = set()
endings = set()
paths = []

def walk(ch_id, path=[]):
    if ch_id in path:
        print(f"🔁 Loop detected at chapter {ch_id}: {path + [ch_id]}")
        return
    if ch_id not in ALL_CHAPTERS:
        print(f"❌ Missing chapter: {ch_id}")
        return
    visited.add(ch_id)
    current = ALL_CHAPTERS[ch_id]
    path = path + [ch_id]

    if not current.get("choices"):
        endings.add(ch_id)
        return

    for choice in current["choices"]:
        next_ch = CHOICE_MAP.get(choice)
        if next_ch is None:
            print(f"❌ Choice '{choice}' in chapter {ch_id} has no mapping")
        else:
            walk(next_ch, path)

walk(0)  # Start from Chapter 0

print(f"\n✅ Traversal complete: {len(visited)} chapters visited.")
print(f"🏁 {len(endings)} unique endings reached.")
print(f"📁 {len(ALL_CHAPTERS)} total chapter files.\n")

# 3. Check for unused chapters
unused = set(ALL_CHAPTERS.keys()) - visited
if unused:
    print("⚠️ Unused chapter files (not reachable from Chapter 0):")
    print(sorted(unused))
else:
    print("✅ All chapter files are reachable from Chapter 0.")

# 4. Check all boss_name entries are valid
from app.enemies import BOSSES
invalid_bosses = []
for ch_id, ch in ALL_CHAPTERS.items():
    if ch.get("battle") and ch.get("boss"):
        boss_name = ch.get("boss_name")
        if boss_name and boss_name not in BOSSES:
            invalid_bosses.append((ch_id, boss_name))

if invalid_bosses:
    print("\n❌ Invalid boss names found in chapters:")
    for ch_id, name in invalid_bosses:
        print(f"  Chapter {ch_id}: unknown boss '{name}'")
else:
    print("✅ All boss names used in chapters exist in BOSSES.")

