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
                    "Shadows stir beyond the old stones, as if the land itself remembers agony. The air reeks of soot and sorrow, each breath a memory not your own. A lone bonfire flickers nearby — "
                    "its flames dance with whispers of forgotten oaths and lost kings.\n\n"
                    "Fragments of who you were claw at your thoughts. You once stood defiant before the Ash Lords, wielding blade and flame. Their kingdoms now lie buried in cinders. "
                    "Yet something darker rises — older, patient, watching. You must press forward. Names echo through the void, and though you have forgotten yours, the world has not.\n\n"
                    "Limgrave stretches in broken majesty before you — a land cracked open by war and time. Towering battlements lie crumbled and half-sunken into marshes that weep ash. Statues of forgotten heroes lean in ruin, their stone eyes blind and hollow. In the distance, you glimpse a skyline jagged with the silhouettes of ancient fortresses, long overtaken by nature’s fury.\n\n"
                    "The bonfire beckons, not merely as warmth, but as a tether to the world’s last memory of light. Its embers spark and hiss, echoing voices long since consumed. This land was not always forsaken. It was sacred. And now, it calls for you."
                ),
                "choices": ["explore_throne", "descend_catacombs"],
                "lore": "Limgrave was once the seat of the First Flamebearers — venerated stewards of sacred fire. They kindled light in a world of dusk, but their covenant was broken when the Pyric Betrayal scorched the last altar. Now only their shadows remain, tethered to ruin."
            },
            1: {
                "text": (
                    "The Catacombs of Dust swallow all light. The air is thick with ancient grief. Faded runes line the cracked stone, whispering of a time when death was sacred — not feared. "
                    "You descend into the dark with cautious breath, each step stirring motes of forgotten decay.\n\n"
                    "Pillars carved in the likeness of saints and martyrs crumble beside you, their faces eroded by time and silence. Broken offerings — rusted weapons, shattered charms — litter the walkways. "
                    "You feel them watching: spirits who remember honor, now reduced to restless ash.\n\n"
                    "A Hollow Knight emerges from shadow — a remnant of oath and anguish. Bound in rust and regret, his armor sighs with every motion. His grip is firm upon a fractured blade, and though his eyes see nothing, he knows only the rhythm of battle. "
                    "There is no plea. No hesitation. Only the instinct to defend a tomb long lost to memory."
                ),
                "choices": ["fight_knight", "flee"],
                "lore": "Hollow Knights were once the Watchers of the Rite — sworn to guard the passage between flesh and spirit. Their souls, unable to pass on, now rot in servitude beneath stone, forgotten even by death. The Catacombs were once pilgrimage grounds, where the dying sought the blessing of Last Light. Now, only ruin and the echo of war remain.",
                "battle": True
            },
            2: {
                "text": (
                    "You flee into the Crimson Grove. The canopy above burns in eternal autumn, crimson leaves like falling blood. "
                    "The trees groan with age, their twisted limbs clawing at the heavens as if mourning the sun.\n\n"
                    "The ground pulses beneath your boots — warm, alive, almost breathing. Roots shift and writhe as though remembering what it meant to walk. "
                    "A rotten scent hangs in the still air: not death, but decay steeped in betrayal.\n\n"
                    "Suddenly, the silence breaks. From the heights of the treetops, a shape plummets — all bone and twisted root. The Crimson Watcher lands before you. Once noble, now monstrous, its eyes glow like dying coals. Its jaw unhinges, leaking soot and ash. "
                    "It emits no sound of speech. Only a wrath that predates language."
                ),
                "choices": ["approach_watcher", "hide"],
                "lore": "The Watcher once stood beside the Flame Mother, guardian of the Ember Tree that healed the land. When her sacred fire was stolen, the Watcher was bound in grief and rot. Twisted by sorrow and betrayed faith, it lost all memory of devotion — only rage endures. The Grove itself is now a wound upon the world, pulsing with corrupted life.",
                "battle": True
            },
            3: {
                "text": (
                    "You approach the Abyssal Watchtower. It looms like a jagged blade cleaving the sky, each stone slick with ancient rain and forgotten blood. "
                    "The tower hums — not with sound, but with time unraveling.\n\n"
                    "Mist coils at its base like dying breath. Cracked banners flutter on rusted iron poles, depicting faded sigils of gods long dethroned. Statues of cloaked sentinels line the approach, their eyes hollowed by centuries of sorrow. One clutches a scroll. Another, a rusted blade. All face inward — toward something no one dares name.\n\n"
                    "The great doors groan as they part, spilling cold air thick with incense and dust. You step into darkness lined with cracked stained glass and shattered iconography. Above, the tower spirals endlessly, its peak lost in shifting gloom.\n\n"
                    "You may ascend into the forgotten heavens... or drift toward the chapel path, where prayers once soothed and now accuse."
                ),
                "choices": ["climb_tower", "side_path_chapel"],
                "lore": "Raised by flamebound clerics to imprison a forgotten god, the tower's walls bear scars of war, ritual, and betrayal. Its foundations are etched with containment runes that now flicker faintly, suggesting their seal may soon break. Pilgrims once gathered here to seek visions — few ever returned sane."
            },

            4: {
                "text": (
                    "Atop the tower, the air thins to frost and fire. A shattered dome lets in a pale, storm-lit sky, where clouds churn like furious spirits. "
                    "The altar is cracked and scorched, once sacred, now desecrated. Blackened bones lie strewn in ceremonial patterns, as if a ritual was interrupted — or completed.\n\n"
                    "Lightning dances across shattered symbols etched into the stone. Runes meant to bind now flicker with instability. And in the silence, a tremor begins. From the gloom beyond the altar, he rises.\n\n"
                    "Cindergloom. Last of the Flame Lords. His body is wrought of molten iron and dying starfire, wrapped in a tattered cloak of living ash. His face is a mask of charred bone, his gaze searing with ancient hatred.\n\n"
                    "He speaks no words. He needs none. This is not a duel. It is a reckoning."
                ),
                "choices": ["fight_final_boss"],
                "lore": "Cindergloom was born of the First Pyre, shaped in the forges of the divine and cursed by their fall. His flame does not warm. It does not burn. It consumes — will, memory, and soul alike. He is the reason the heavens no longer blaze.",
                "battle": True,
                "boss": True
            },

            5: {
                "text": (
                    "Silence. Your enemy lies broken. The air itself shudders in the wake of his fall. The flames dim but do not die — instead, they curl inward, waiting. Watching.\n\n"
                    "Ash falls like slow, deliberate snow. Each flake sings faintly as it lands. The world is quieter now, as if holding its breath. You kneel at the broken altar, your reflection shimmering in blood and cinder.\n\n"
                    "The choice comes not as a voice, but as a weight. A fork in the soul.\n\n"
                    "Rekindle the Age of Flame and let light return — brilliant, but destined to burn away once more. Or embrace the coming dark, where truth may lie, cold and unyielding.\n\n"
                    "No one shall guide you now. You are legend — not for what you fought, but for what you chose. The world waits."
                ),
                "choices": [],
                "lore": "Every Age begins in brilliance and ends in ash. Some claim the flame is salvation. Others say it is a lie — a cycle that binds all souls to endless war. But what comes after ash? That has never been written. Until now."
            },

            6: {
                "text": (
                    "You enter the Chapel of Thorns, where silence grows like moss. Vines claw across broken pews, weaving through cracked mosaics that once depicted salvation.\n\n"
                    "At its heart lies a flame — small, steady, and golden. Not fierce like the pyres of war, but warm, like memory. Dust drifts through shafts of amber light from shattered stained glass. Each step echoes, reverent and uncertain.\n\n"
                    "You kneel. The air hums softly. The warmth seeps into your bones, quieting pain and silencing the ghosts that followed you. For a moment — just a moment — the world feels whole again."
                ),
                "choices": ["touch_relic", "leave_relic"],
                "lore": "The Thorn Chapel was a place of forbidden faith — where healers defied the pyromancer lords, nurturing flame without destruction. It was sealed in bramble and branded heresy. Some say it still remembers peace. Few are allowed to feel it.",
                "rest": True
            },
            7: {
                "text": (
                    "You descend into the Underglare Tomb, where shadow and light war without end. The walls shimmer with false reflections — echoes of faces not your own. "
                    "The deeper you tread, the more your thoughts turn against you.\n\n"
                    "At the tomb’s center lies a dais cracked by time, above which floats the Forgotten Guardian. His form is cloaked in brittle armor and unspoken law. "
                    "The stone beneath him has worn smooth from centuries of vigil.\n\n"
                    "He does not ask why you are here. He does not question fate. He simply raises his axe.\n\n"
                    "One word breaks the stillness: 'Judgment.'"
                ),
                "choices": ["confront_guardian"],
                "lore": "The Forgotten Guardian once served the Tribunal of Light, enforcers of balance. When their creed fell to ruin, he remained — the last to remember a justice now lost. Some say he is blind. Others claim he sees too much.",
                "battle": True
            },

            8: {
                "text": (
                    "The relic pulses with radiant breath, each beat echoing into the marrow of your bones. Symbols of flame and spirit swirl across its surface — not drawn, but alive.\n\n"
                    "The chamber hums with anticipation. Faint whispers — in languages older than the flame — reverberate through the stone. Runes once hidden blaze into view, outlining a sealed passage you had not noticed before.\n\n"
                    "As you step back, the air thickens. A hidden gate grinds open at the base of the tower, revealing a passage veiled in golden mist.\n\n"
                    "You do not feel fear. Only inevitability. Destiny has found its shape — and it wears your shadow."
                ),
                "choices": ["fight_final_boss"],
                "lore": "Only those marked by the relic — forged by flame, yet untouched by rage — may pass through the Gate of Cinders. The relic is not a tool. It is a key, awakened by resolve. It marks not heroes, but those who endure.",
                "battle": False
            },

            9: {
                "text": (
                    "Before you looms the Gate of Ash — a monolith scorched by centuries of flame and sorrow. Its surface crackles with veins of ember, pulsing like the last heartbeat of a dying god.\n\n"
                    "Three paths stretch from its base, each radiating a distinct dread.\n\n"
                    "To the left, a trail of molten rock winds into flame-choked valleys, where the air sings with heat and despair.\n\n"
                    "To the right, stairs spiral into a bottomless dark, untouched by sun or memory. And ahead lies a ruined causeway littered with idol fragments and the bones of kneeling pilgrims.\n\n"
                    "Each breath here feels heavier. Each step, a choice that echoes beyond time."
                ),
                "choices": ["enter_flame_path", "descend_shadow_path", "investigate_ruins"],
                "lore": "It is said the Ash Gate was forged from the remains of the First Flame, quenched and hammered by divine will. It judges all who approach. Few return. None return unchanged."
            },

            10: {
                "text": (
                    "You walk the flame-warped path. Ash swirls around you in choking spirals, and the ground cracks with every step, bleeding molten tears.\n\n"
                    "The corridor hums with pressure and pain, its stone scorched black by forgotten rites. Bones, melted into slag, line the edges like offerings to an angry god.\n\n"
                    "From the heart of the ruin comes a bellow — ancient, wounded, full of fury. A colossal figure lumbers forward, dripping magma, bones blackened and fused with iron.\n\n"
                    "This was once a smith. Now, it forges only death."
                ),
                "choices": ["press_forward"],
                "lore": "The Flame Corridor once led to the Crucible Forge, where the Flamebearers tempered blades that could kill gods. But when the last smith succumbed to madness, the fires turned against their makers.",
                "battle": True
            },
            11: {
                "text": (
                    "You descend into the Shadow Hollow, a place where light surrenders and time forgets.\n\n"
                    "The silence here is sentient. Whispers slither between the stones, and unseen eyes blink from the veil of dark.\n\n"
                    "The walls bleed a dim, sickly glow — not from torches, but from memories imprinted into the stone. "
                    "Names you’ve never heard stir in your mind like nightmares half-remembered.\n\n"
                    "Deeper still, the shadows converge. Something old moves beyond sight, stirring not with malice, but with hunger. "
                    "You have come too far to turn away."
                ),
                "choices": ["press_forward"],
                "lore": "The Shadow Hollow is where the First Sin was whispered into mortal ears. No light dares touch its core. What lies below is not evil — it is truth, unblinking and cruel.",
                "battle": True
            },

            12: {
                "text": (
                    "You investigate the ruins, their stones blackened and half-swallowed by the earth. At the heart lies a collapsed shrine, choked in thorn and silence.\n\n"
                    "Amidst the rubble, you find a journal — bound in scorched leather, its clasps rusted shut. Pages fall apart as you touch them, brittle with age. Yet some words endure.\n\n"
                    "'I saw the mirror. It saw me back. I was not ready.'\n\n"
                    "The air around you shifts. Dust thickens. Shadows lengthen. The ruin seems to hold its breath."
                ),
                "choices": ["read_further", "leave_quietly"],
                "lore": "The journal belonged to a penitent knight who sought absolution through reflection. What he found was not peace, but recognition — and a hunger staring back."
            },

            13: {
                "text": (
                    "You read the final entry: 'The mirror does not reflect — it remembers.'\n\n"
                    "The wind stops. The world narrows. At the ruin’s edge stands a cracked mirror, bound in roots and boundless dread.\n\n"
                    "As you approach, your reflection falters, twisting into shapes of moments you never lived — or buried long ago.\n\n"
                    "Behind the glass, something watches. It does not mimic. It judges."
                ),
                "choices": ["walk_away", "step_through"],
                "lore": "The Mirror of Binding is said to trap the echoes of those who could not bear their truth. It does not lie. It reveals. But not all can survive revelation."
            },
            14: {
                "text": (
                    "You turn away, but the mirror is not done with you. The air grows dense — not with threat, but with gravity.\n\n"
                    "Dust swirls as if in protest. The ground hums with withheld judgment.\n\n"
                    "Your name is whispered from the dark, not as a greeting — but as a sentence. Behind you, the mirror cracks. Not from impact. From longing."
                ),
                "choices": ["shatter_mirror", "return"],
                "lore": "Avoiding the mirror is not escape. To deny it is to fracture your story — and perhaps your soul. Some claim the mirror remembers you forever, even if you forget it.",
                "battle": False
            },

            15: {
                "text": (
                    "You step into the mirror’s echo. The world inverts — color drains, sound warps. You fall inward.\n\n"
                    "Before you stands your shadow, unbound by flesh or fear. It is not a reflection. It is what remains when all illusions are burned away.\n\n"
                    "It remembers every failure. Every cruelty. Every doubt. It moves before you do, with grace honed by your regret.\n\n"
                    "It does not hate you. It knows you. And it rises to end you."
                ),
                "choices": ["fight_knight"],
                "lore": "You cannot defeat what you refuse to face. The shadow has no mercy. It is not your enemy — it is your memory given form.",
                "battle": True
            },

            16: {
                "text": (
                    "At the summit of the Abyssal Watchtower, light pierces the gloom like blades. Crumbling gargoyles watch from above, their mouths agape in silent scream.\n\n"
                    "A bonfire burns at the altar — pale gold, unwavering, untouched by wind or time.\n\n"
                    "You kneel. The warmth washes over you, dissolving wounds and memory alike.\n\n"
                    "The path behind fades. The path ahead glows. The final gate waits, pulsing like a heartbeat. But you are no longer who you were.\n\n"
                    "You are ready."
                ),
                "choices": ["approach_final_gate"],
                "lore": "This flame was kindled by the first Flamebearer who chose mercy over might. Its light does not blind. It forgives. Few recall their name. But soon, they may recall yours.",
                "rest": True
            },

            99: {
                "text": (
                    "You step through the final gate, and the world shifts. Time unravels. Sound fades. The air thickens into fire, and yet your breath remains cold.\n\n"
                    "The sky is gone. Above you stretches a void of swirling cinders and molten light. A cathedral of ash surrounds you, carved not by mortal hands, but by despair given shape.\n\n"
                    "In the center, a figure stands — immense, unmoving. Cloaked in flame and ruin, his silhouette flickers between man and monster. Chains of scorched iron drag behind him, inscribed with the names of those who defied him — and burned.\n\n"
                    "Cindergloom. He turns, slow and sovereign. His gaze sears your soul, not in hatred, but recognition.\n\n"
                    "The ground shudders. His greatsword, forged of collapsed suns and bound prayers, ignites in silence. You cannot run. You would not.\n\n"
                    "The battle has already begun."
                ),
                "choices": [],
                "lore": "Cindergloom is not merely the final Flame Lord — he is flame given memory. When the gods fell, it was he who lit the pyres of their undoing. Bound neither by time nor fate, he waits only for one worthy enough to burn with him.",
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
