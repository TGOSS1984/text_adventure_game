"""
story.py

Handles all branching story logic, narrative & story triggers like battles etc. Maps choices to story paths
"""

class Story:
    def __init__(self):
        self.chapter = 0
        self.story_data = {
            0: {
                "text": (
                    "As a newly risen soul in the forsaken lands, you awaken amidst the ruin of Limgrave. "
                    "Shadows stir beyond the old stones. The air reeks of soot and sorrow. A lone bonfire flickers nearby — "
                    "your only warmth in this forsaken world.\n\n"
                    "Memories of a broken world surge through you. You once stood against the Ash Lords, their kingdoms now ash. "
                    "But something darker rises. You must press forward. The world has not forgotten your name, though you have."
                ),
                "choices": ["explore_throne", "descend_catacombs"],
                "lore": "Limgrave was the seat of the First Flamebearers — now only dust remains. Once blessed with holy fire, now cursed with endless dusk."
            },
            1: {
                "text": (
                    "The Catacombs of Dust swallow all light. Faded runes line the cracked stone, whispering of a time when death was sacred. "
                    "You tread carefully as distant echoes betray something moving. A Hollow Knight, bound in rust and regret, steps from the gloom. "
                    "It raises a broken blade. It remembers nothing... but the fight."
                ),
                "choices": ["fight_knight", "flee"],
                "lore": "Hollow Knights guard the dead who sleep forever beneath these cursed tombs. Their oaths remain long after memory fades.",
                "battle": True
            },
            2: {
                "text": (
                    "You flee into the Crimson Grove. The canopy above burns red as if forever trapped in autumn. "
                    "The ground pulses beneath your feet — alive, but wrong. Suddenly, the Crimson Watcher drops from the treetops, all bone and twisted root. "
                    "Its jaw unhinges. No words. Only wrath."
                ),
                "choices": ["approach_watcher", "hide"],
                "lore": "The Watcher once protected the Tree of Flame — now twisted and blind with rage. The flame it worshipped was extinguished... by betrayal.",
                "battle": True
            },
            3: {
                "text": (
                    "You approach the Abyssal Watchtower. It looms above like a broken blade stabbed into the sky. "
                    "Mist curls at its base, and somewhere within, you sense time itself unraveling. "
                    "The doors open with a groan like a dying god. You may ascend, or explore the chapel path branching off into forgotten devotion."
                ),
                "choices": ["climb_tower", "side_path_chapel"],
                "lore": "This tower was raised to contain a god who outgrew his form. Even its walls whisper secrets no man should hear."
            },
            4: {
                "text": (
                    "Atop the tower, the flame bursts into storm. Lightning crackles along the broken altar. "
                    "Cindergloom, last of the Flame Lords, stirs from eternal rest. His body is fire and shadow. "
                    "He does not speak. He does not feel. He only burns."
                ),
                "choices": ["fight_final_boss"],
                "lore": "Cindergloom was born from starfire. He does not burn — he consumes.",
                "battle": True,
                "boss": True
            },
            5: {
                "text": (
                    "Silence. Your enemy lies still. The flame does not roar — it whispers. "
                    "Ash falls like snow around you. The world is quiet. You kneel.\n\n"
                    "Now, a choice lies before you: rekindle the age of flame or embrace the coming dark. "
                    "No one shall guide you now. You are legend, forged by your own will. The world waits for your decision...\n\n"
                    "And so, another tale is written in ash and blood."
                ),
                "choices": [],
                "lore": "Every Age begins with fire and ends with ash. But what comes after ash?"
            },
            6: {
                "text": (
                    "You enter the Chapel of Thorns. Vines curl like veins around shattered pews. A gentle flame glows at the center — not a threat, but a refuge.\n\n"
                    "You kneel before it. The warmth seeps into your bones. Your wounds begin to fade, and the whispers recede. "
                    "For a moment, you remember who you were."
                ),
                "choices": ["touch_relic", "leave_relic"],
                "lore": "The Thorn Chapel was built to honor a flame that healed instead of burned. It was cursed for its defiance.",
                "rest": True
            },
            7: {
                "text": (
                    "You descend into the Underglare Tomb. Here, the light is an enemy. Shadows twist and writhe. "
                    "At the center of the ruin, the Forgotten Guardian rises from the stone. His axe is cracked, but his will is not. "
                    "He speaks one word: 'Judgment.'"
                ),
                "choices": ["confront_guardian"],
                "lore": "The Guardian never left his post. He waited for a final command. Perhaps you are it.",
                "battle": True
            },
            8: {
                "text": (
                    "The relic pulses with light and sound and your wounds are healed. Runes glow, and a hidden gate grinds open at the base of the tower. "
                    "You feel the end approach — not in fear, but in inevitability. "
                    "This is where fate sharpens its blade."
                ),
                "choices": ["fight_final_boss"],
                "lore": "Only those marked by the relic can face the Last Flame. You are marked now.",
                "battle": False
            },
                        9: {
                "text": (
                    "Before you lies the Gate of Ash — towering, cracked, and smoldering. Three branching paths lead away from it:\n\n"
                    "A seared trail soaked in smoke and fire. A staircase descending into lightless depth. And a crumbling road lined with shattered idols.\n\n"
                    "Each breath here feels heavier. Each choice feels final. Choose wisely, for some paths do not return."
                ),
                "choices": ["enter_flame_path", "descend_shadow_path", "investigate_ruins"],
                "lore": "It’s said the Ash Gate judges all who enter. Few return. None unchanged."
            },
            10: {
                "text": (
                    "You walk the path of fire. Ash storms blind you and molten stone cracks beneath your boots. "
                    "The air is alive with heat — and something more. From within the ruin, a beast of magma and bone shambles forth, roaring.\n\n"
                    "It was once a smith, perhaps. Now, it forges only death."
                ),
                "choices": ["press_forward"],
                "lore": "The Flame Corridor once led to the heart of the Flamebearers’ forge. Now it is a furnace for broken souls.",
                "battle": True
            },
            11: {
                "text": (
                    "You descend into the Shadow Hollow. No light dares follow. Whispers scratch at your mind like claws. "
                    "Eyes blink where no faces dwell. In the deepest corner, something stirs, older than flame.\n\n"
                    "It reaches not with hands, but memory. Prepare yourself."
                ),
                "choices": ["press_forward"],
                "lore": "The Shadow Hollow is said to be where the First Sin was whispered. It echoes still.",
                "battle": True
            },
            12: {
                "text": (
                    "You investigate the ruins and find a crumbling journal bound in scorched leather. Pages fall apart as you touch them, but some words remain:\n\n"
                    "'I saw the mirror. It saw me back. I was not ready.'\n\n"
                    "The air grows cold. The shadows deepen."
                ),
                "choices": ["read_further", "leave_quietly"],
                "lore": "The journal belonged to a soul who lost their way — or found a darker one. The ink is not dry."
            },
            13: {
                "text": (
                    "You read the final entry: 'The mirror does not reflect — it remembers.'\n\n"
                    "A cracked mirror stands at the far end of the ruin. As you approach, your reflection fades. Something else watches back. "
                    "Your blood runs cold."
                ),
                "choices": ["walk_away", "step_through"],
                "lore": "It is said the Mirror of Binding traps the echoes of the damned. But what happens when one walks willingly?"
            },
            14: {
                "text": (
                    "You turn away, but the air pulls at you. Dust swirls in defiance. Your name is whispered from the dark. "
                    "You are marked.\n\n"
                    "The mirror behind you cracks. Its song grows louder."
                ),
                "choices": ["shatter_mirror", "return"],
                "lore": "Avoiding fate has its own consequences. To turn from the mirror is to deny yourself.",
                "battle": False
            },
            15: {
                "text": (
                    "You step into the mirror’s echo. The world blurs and folds inward. Your shadow detaches — it moves with purpose.\n\n"
                    "It remembers every failure, every fear. It has learned from you. Now, it rises.\n\n"
                    "You must face yourself."
                ),
                "choices": ["fight_knight"],
                "lore": "You cannot defeat what you refuse to face. The shadow has no mercy.",
                "battle": True
            },
            16: {
                "text": (
                    "At the summit of the Abyssal Watchtower, beyond winding stone and shattered statues, "
                    "you find a crumbling altar where a bonfire burns with pale gold light.\n\n"
                    "You kneel beside it. The fire is warm — not hungry. You feel whole again. The long road behind you fades from pain to memory.\n\n"
                    "Ahead, the final gate pulses with heat. The end of your journey calls. But you are ready now."
                ),
                "choices": ["approach_final_gate"],
                "lore": "This flame was kindled by the first Flamebearer who chose mercy over power. Few remember their name. You will.",
                "rest": True
            },
            99: {
                "text": "You step through the final gate. Cindergloom's presence burns across your soul. The battle begins now.",
                "choices": [],
                "lore": "You face the Last Flame.",
                "battle": True,
                "boss": True
            }

        }

    def get_chapter(self, chapter_id):
        return self.story_data.get(chapter_id, {"text": "Unknown", "choices": []})

    def choose_path(self, choice):
        mapping = {
            "explore_throne": 1,
            "descend_catacombs": 2,
            "fight_knight": 1,
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
            "return": 3
        }
        return mapping.get(choice, 0)
