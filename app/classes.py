"""
classes.py

Single source of truth for all player class definitions.

Adding a new class: add one entry here. Everything else updates automatically.

Primary special fields (50 MP, shared cooldown):
    special_multiplier  — damage multiplier applied to relevant attack stat
    special_effect      — 'stun', 'smoke', 'heal_stun', or None
    special_variance    — max random int subtracted from damage (0 = no variance)
    special_min_dmg     — damage floor after all reductions

Secondary special fields (35 MP, same shared cooldown):
    special2_effect     — 'dot', 'buff_attack', 'shield', 'stun', 'leech'
    special2_multiplier — damage multiplier on the hit itself (0 = no direct hit)
    special2_dot_dmg    — damage per turn (dot only)
    special2_dot_turns  — duration in turns (dot only)
    special2_dot_label  — key into DOT_TICK_MESSAGES in config.py ('bleed'/'poison')
    special2_buff_stat  — session character key to boost ('attack'/'magic_attack')
    special2_buff_amount— flat amount added to buff_stat
    special2_buff_turns — duration in turns
    special2_buff_label — key into BUFF_EXPIRE_MESSAGES in config.py
    special2_shield_pct — fraction of incoming damage absorbed (0.0–1.0)
    special2_shield_turns — duration in turns
"""

CLASSES = {
    "Knight": {
        # ── Core stats ────────────────────────────────────────────────────────
        "attack":           17,
        "magic_attack":     0,
        "defense":          15,
        "magic_defense":    10,
        "max_hp":           160,
        "mp_max":           80,
        # ── Combat modifiers ──────────────────────────────────────────────────
        "crit_chance":      0.20,
        "crit_multiplier":  1.5,
        "dodge_chance":     0.20,
        "block_multiplier": 0.25,
        "damage_type":      "physical",
        # ── Assets ────────────────────────────────────────────────────────────
        "image":            "classes/knight.png",
        "icon":             "fa-chess-knight",
        # ── Primary special ───────────────────────────────────────────────────
        "special_name":       "Shield Bash",
        "special_label":      "🛡 Shield Bash",
        "special_desc":       "Normal damage + stun. Enemy cannot counter.",
        "special_cost":       50,
        "special_cooldown":   4,
        "special_multiplier": 1.0,
        "special_effect":     "stun",
        "special_variance":   4,
        "special_min_dmg":    5,
        # ── Secondary special ─────────────────────────────────────────────────
        "special2_name":         "War Cry",
        "special2_label":        "⚔ War Cry",
        "special2_desc":         "Raise your weapon and bellow. Attack +5 for 3 turns.",
        "special2_cost":         35,
        "special2_effect":       "buff_attack",
        "special2_multiplier":   0,
        "special2_dot_dmg":      0,
        "special2_dot_turns":    0,
        "special2_dot_label":    "",
        "special2_buff_stat":    "attack",
        "special2_buff_amount":  5,
        "special2_buff_turns":   3,
        "special2_buff_label":   "war_cry",
        "special2_shield_pct":   0.0,
        "special2_shield_turns": 0,
        # ── Flavour ───────────────────────────────────────────────────────────
        "lore": (
            "Once a sentinel of the Sunken Citadel, their oath was not broken "
            "— only forgotten. Clad in rusted honour, they march through death unbent."
        ),
    },

    "Mage": {
        # ── Core stats ────────────────────────────────────────────────────────
        "attack":           0,
        "magic_attack":     28,
        "defense":          6,
        "magic_defense":    18,
        "max_hp":           110,
        "mp_max":           120,
        # ── Combat modifiers ──────────────────────────────────────────────────
        "crit_chance":      0.30,
        "crit_multiplier":  1.5,
        "dodge_chance":     0.60,
        "block_multiplier": 0.50,
        "damage_type":      "magic",
        # ── Assets ────────────────────────────────────────────────────────────
        "image":            "classes/mage.png",
        "icon":             "fa-wand-magic-sparkles",
        # ── Primary special ───────────────────────────────────────────────────
        "special_name":       "Arcane Burst",
        "special_label":      "✨ Arcane Burst",
        "special_desc":       "2× magic attack. Bypasses all physical armour.",
        "special_cost":       50,
        "special_cooldown":   4,
        "special_multiplier": 2.0,
        "special_effect":     None,
        "special_variance":   0,
        "special_min_dmg":    10,
        # ── Secondary special ─────────────────────────────────────────────────
        "special2_name":         "Nullfield",
        "special2_label":        "🔮 Nullfield",
        "special2_desc":         "Weave a barrier of arcane force. Incoming damage halved for 2 turns.",
        "special2_cost":         35,
        "special2_effect":       "shield",
        "special2_multiplier":   0,
        "special2_dot_dmg":      0,
        "special2_dot_turns":    0,
        "special2_dot_label":    "",
        "special2_buff_stat":    None,
        "special2_buff_amount":  0,
        "special2_buff_turns":   0,
        "special2_buff_label":   "nullfield",
        "special2_shield_pct":   0.50,
        "special2_shield_turns": 2,
        # ── Flavour ───────────────────────────────────────────────────────────
        "lore": (
            "Bearer of forbidden glintfire, the Mage whispers truths carved in starlight. "
            "Each spell flung is a shard of a dream long devoured."
        ),
    },

    "Rogue": {
        # ── Core stats ────────────────────────────────────────────────────────
        "attack":           22,
        "magic_attack":     0,
        "defense":          8,
        "magic_defense":    6,
        "max_hp":           130,
        "mp_max":           100,
        # ── Combat modifiers ──────────────────────────────────────────────────
        "crit_chance":      0.40,
        "crit_multiplier":  1.5,
        "dodge_chance":     0.70,
        "block_multiplier": 0.50,
        "damage_type":      "physical",
        # ── Assets ────────────────────────────────────────────────────────────
        "image":            "classes/rogue.png",
        "icon":             "fa-skull-crossbones",
        # ── Primary special ───────────────────────────────────────────────────
        "special_name":       "Smoke Screen",
        "special_label":      "💨 Smoke Screen",
        "special_desc":       "1× attack damage + guaranteed dodge next enemy turn.",
        "special_cost":       50,
        "special_cooldown":   4,
        "special_multiplier": 1.0,
        "special_effect":     "smoke",
        "special_variance":   0,
        "special_min_dmg":    5,
        # ── Secondary special ─────────────────────────────────────────────────
        "special2_name":         "Backstab",
        "special2_label":        "🗡 Backstab",
        "special2_desc":         "Strike a critical spot — the enemy bleeds for 8 damage per turn for 4 turns.",
        "special2_cost":         35,
        "special2_effect":       "dot",
        "special2_multiplier":   0.5,
        "special2_dot_dmg":      8,
        "special2_dot_turns":    4,
        "special2_dot_label":    "bleed",
        "special2_buff_stat":    None,
        "special2_buff_amount":  0,
        "special2_buff_turns":   0,
        "special2_buff_label":   "",
        "special2_shield_pct":   0.0,
        "special2_shield_turns": 0,
        # ── Flavour ───────────────────────────────────────────────────────────
        "lore": (
            "Born in the shadow of the Ashen Spires, the Rogue strikes like regret "
            "— unseen, swift, and final. No name, no past, only the blade."
        ),
    },

    "Archer": {
        # ── Core stats ────────────────────────────────────────────────────────
        "attack":           20,
        "magic_attack":     0,
        "defense":          10,
        "magic_defense":    8,
        "max_hp":           140,
        "mp_max":           100,
        # ── Combat modifiers ──────────────────────────────────────────────────
        "crit_chance":      0.50,
        "crit_multiplier":  1.5,
        "dodge_chance":     0.50,
        "block_multiplier": 0.40,
        "damage_type":      "physical",
        # ── Assets ────────────────────────────────────────────────────────────
        "image":            "classes/archer.png",
        "icon":             "fa-feather",
        # ── Primary special ───────────────────────────────────────────────────
        "special_name":       "Mark Target",
        "special_label":      "🎯 Mark Target",
        "special_desc":       "2× attack. Finds the enemy's weak point.",
        "special_cost":       50,
        "special_cooldown":   4,
        "special_multiplier": 2.0,
        "special_effect":     None,
        "special_variance":   0,
        "special_min_dmg":    5,
        # ── Secondary special ─────────────────────────────────────────────────
        "special2_name":         "Poison Arrow",
        "special2_label":        "🏹 Poison Arrow",
        "special2_desc":         "Loose a barbed arrow laced with venom. 6 poison damage per turn for 5 turns.",
        "special2_cost":         35,
        "special2_effect":       "dot",
        "special2_multiplier":   0,
        "special2_dot_dmg":      6,
        "special2_dot_turns":    5,
        "special2_dot_label":    "poison",
        "special2_buff_stat":    None,
        "special2_buff_amount":  0,
        "special2_buff_turns":   0,
        "special2_buff_label":   "",
        "special2_shield_pct":   0.0,
        "special2_shield_turns": 0,
        # ── Flavour ───────────────────────────────────────────────────────────
        "lore": (
            "From the ruins of Eldergrove they come, eyes hollow with distant wars. "
            "Each arrow loosed is a memory exiled into the dark."
        ),
    },

    "Paladin": {
        # ── Core stats ────────────────────────────────────────────────────────
        "attack":           18,
        "magic_attack":     18,
        "defense":          12,
        "magic_defense":    14,
        "max_hp":           150,
        "mp_max":           90,
        # ── Combat modifiers ──────────────────────────────────────────────────
        "crit_chance":      0.20,
        "crit_multiplier":  1.5,
        "dodge_chance":     0.40,
        "block_multiplier": 0.30,
        "damage_type":      "mixed",
        # ── Assets ────────────────────────────────────────────────────────────
        "image":            "classes/paladin.png",
        "icon":             "fa-cross",
        # ── Primary special ───────────────────────────────────────────────────
        "special_name":       "Healing Light",
        "special_label":      "✝ Healing Light",
        "special_desc":       "Restore 40% max HP. Sacred light blinds the enemy — they cannot counter.",
        "special_cost":       50,
        "special_cooldown":   5,
        "special_multiplier": 0,
        "special_effect":     "heal_stun",
        "special_variance":   0,
        "special_min_dmg":    0,
        # ── Secondary special ─────────────────────────────────────────────────
        "special2_name":         "Hammer of Justice",
        "special2_label":        "🔨 Hammer of Justice",
        "special2_desc":         "1.5× mixed damage strike. Sacred force stuns — the enemy cannot counter.",
        "special2_cost":         35,
        "special2_effect":       "stun",
        "special2_multiplier":   1.5,
        "special2_dot_dmg":      0,
        "special2_dot_turns":    0,
        "special2_dot_label":    "",
        "special2_buff_stat":    None,
        "special2_buff_amount":  0,
        "special2_buff_turns":   0,
        "special2_buff_label":   "",
        "special2_shield_pct":   0.0,
        "special2_shield_turns": 0,
        # ── Flavour ───────────────────────────────────────────────────────────
        "lore": (
            "Oathbound to a god who no longer answers, the Paladin carries faith "
            "as a weapon and a wound. Where others see ruin, they see a reason to endure."
        ),
    },

    "Necromancer": {
        # ── Core stats ────────────────────────────────────────────────────────
        "attack":           0,
        "magic_attack":     22,
        "defense":          9,
        "magic_defense":    22,
        "max_hp":           100,
        "mp_max":           130,
        # ── Combat modifiers ──────────────────────────────────────────────────
        "crit_chance":      0.20,
        "crit_multiplier":  1.5,
        "dodge_chance":     0.55,
        "block_multiplier": 0.60,
        "damage_type":      "magic",
        # ── Assets ────────────────────────────────────────────────────────────
        "image":            "classes/necromancer.png",
        "icon":             "fa-skull",
        # ── Primary special ───────────────────────────────────────────────────
        "special_name":       "Raise the Dead",
        "special_label":      "💀 Raise the Dead",
        "special_desc":       "2.5× magic attack. Undead tear through armour — enemy cannot predict the assault.",
        "special_cost":       50,
        "special_cooldown":   5,
        "special_multiplier": 2.5,
        "special_effect":     None,
        "special_variance":   8,
        "special_min_dmg":    12,
        # ── Secondary special ─────────────────────────────────────────────────
        "special2_name":         "Soul Leech",
        "special2_label":        "💉 Soul Leech",
        "special2_desc":         "Drain life from the enemy — 1× magic damage, heal for 50% of damage dealt.",
        "special2_cost":         35,
        "special2_effect":       "leech",
        "special2_multiplier":   1.0,
        "special2_dot_dmg":      0,
        "special2_dot_turns":    0,
        "special2_dot_label":    "",
        "special2_buff_stat":    None,
        "special2_buff_amount":  0,
        "special2_buff_turns":   0,
        "special2_buff_label":   "",
        "special2_shield_pct":   0.0,
        "special2_shield_turns": 0,
        # ── Flavour ───────────────────────────────────────────────────────────
        "lore": (
            "They do not fear death. They have spoken to it, bargained with it, "
            "and worn its face as a mask. The dead answer when the Necromancer calls."
        ),
    },
}


def get_class(class_name: str) -> dict:
    """Return the class definition dict, or None if not found."""
    return CLASSES.get(class_name)


def get_special_label(class_name: str, fallback: str = "⚡ Special") -> str:
    """Return the primary special move button label for a given class."""
    cls = CLASSES.get(class_name)
    return cls["special_label"] if cls else fallback


def get_special2_label(class_name: str, fallback: str = "⚡ Special 2") -> str:
    """Return the secondary special move button label for a given class."""
    cls = CLASSES.get(class_name)
    return cls["special2_label"] if cls else fallback


def get_class_icon(class_name: str, fallback: str = "fa-shield-halved") -> str:
    """Return the Font Awesome icon class for a given class."""
    cls = CLASSES.get(class_name)
    return cls["icon"] if cls else fallback