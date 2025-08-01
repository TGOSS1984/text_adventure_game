# generate_story_map.py

import json
import os
from pathlib import Path

# Adjust paths as needed
BASE_DIR = Path(__file__).resolve().parent  # → app/story/tools/
CHAPTERS_DIR = BASE_DIR.parent / "chapters"
OUTPUT_DIR = BASE_DIR  # → stay in tools

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

choices_mapping = {}
markdown_lines = ["# Storyboard Summary\n"]
graph_lines = ["graph TD;"]

# Control which stub choices should appear
ALLOWED_PLACEHOLDER_CHOICES = {"final_choice", "conclude_game"}  # Add as needed

# TEMP structure to collect mappings
temp_choice_map = {}
unresolved_choices = set()

# First pass — build summary and placeholder graph edges
for file in sorted(CHAPTERS_DIR.glob("*.json")):
    with open(file, "r", encoding="utf-8") as f:
        data = json.load(f)

    chapter_id = data["id"]
    text = data["text"].strip().split("\n")[0][:80] + "..."
    lore = data.get("lore", "").strip()[:100]
    battle = data.get("battle", False)
    rest = data.get("rest", False)
    boss = data.get("boss", False)

    markdown_lines.append(f"## Chapter {chapter_id}")
    markdown_lines.append(f"- **Text:** {text}")
    markdown_lines.append(f"- **Lore:** {lore or '—'}")
    markdown_lines.append(f"- **Battle:** {'Yes' if battle else 'No'}")
    markdown_lines.append(f"- **Rest:** {'Yes' if rest else 'No'}")
    markdown_lines.append(f"- **Boss:** {'Yes' if boss else 'No'}")

    choices = data.get("choices", [])
    if not choices:
        markdown_lines.append(f"- **Choices:** _None_")
    else:
        markdown_lines.append(f"- **Choices:**")
        for choice in choices:
            markdown_lines.append(f"  - `{choice}`")
            if choice in ALLOWED_PLACEHOLDER_CHOICES or not choice.startswith("choice_"):
                temp_choice_map.setdefault(choice, None)
                graph_lines.append(f'{chapter_id} -->|{choice}| ???')

    markdown_lines.append("")

# Manual fallback mapping for any unresolved choices
manual_fallbacks = {
    "explore_throne": 1,
    "descend_catacombs": 2,
    "fight_knight": 17,
    "flee": 3,
    "approach_watcher": 3,
    "hide": 3,
    "climb_tower": 16,
    "approach_final_gate": 4,
    "fight_final_boss": 99,
    "side_path_chapel": 6,
    "touch_relic": 8,
    "leave_relic": 4,
    "confront_guardian": 9,
    "enter_flame_path": 10,
    "descend_shadow_path": 11,
    "investigate_ruins": 12,
    "read_further": 13,
    "leave_quietly": 3,
    "walk_away": 14,
    "step_through": 15,
    "shatter_mirror": 3,
    "press_forward": 3,
    "return": 3,
    "descend_tomb": 7,
    "conclude_game": 5,
    "final_choice": 96
}

# Combine manual mapping with any found automatically
choices_mapping = {**manual_fallbacks, **temp_choice_map}

# Resolve any unknowns to fallback or 0
for choice in choices_mapping:
    if choices_mapping[choice] is None:
        resolved = manual_fallbacks.get(choice)
        if resolved is not None:
            choices_mapping[choice] = resolved
        else:
            choices_mapping[choice] = 0
            unresolved_choices.add(choice)

# Final pass: update graph edges with resolved targets
resolved_graph_lines = []
for line in graph_lines:
    if "-->" in line and "|" in line and "???" in line:
        parts = line.split("-->")
        from_id = parts[0].strip()
        label = parts[1].split("|")[1].strip()
        to_id = choices_mapping.get(label, 0)
        resolved_graph_lines.append(f"{from_id} -->|{label}| {to_id}")
    else:
        resolved_graph_lines.append(line)

# Write outputs
with open(OUTPUT_DIR / "choices_mapping.json", "w", encoding="utf-8") as f:
    json.dump(choices_mapping, f, indent=2)

with open(OUTPUT_DIR / "storyboard.md", "w", encoding="utf-8") as f:
    f.write("\n".join(markdown_lines))

with open(OUTPUT_DIR / "story_graph.mmd", "w", encoding="utf-8") as f:
    f.write("```mermaid\n")
    f.write("\n".join(resolved_graph_lines))
    f.write("\n```")

print("✅ Story mapping files generated:")
print("- choices_mapping.json")
print("- storyboard.md")
print("- story_graph.mmd")

if unresolved_choices:
    print("⚠️  Warning: Unresolved choices with no mapping found:")
    for c in sorted(unresolved_choices):
        print(f" - {c}")
