"""
classes.py

Single source of truth for all player class definitions.

Replaces the scattered class data previously spread across:
- models.py  — create() dict, get_class_stats() dict, DODGE, BLOCK_MULT,
               MP_MAX, MAGIC_ATTACK, MAGIC_DEFENSE, DAMAGE_TYPE dicts
- battle.html / battle_fragment.html — hardcoded special_label dicts
- combat.py  — hardcoded if class_name == 'Knight' special move logic
- index.html — 4 hardcoded class cards with stats, lore, icons inline

Adding a new class: add one entry here. Everything else updates automatically.

Special move fields:
    special_multiplier — damage multiplier applied to the relevant attack stat
    special_effect     — 'stun', 'smoke', or None
    special_variance   — max random int subtracted from damage (0 = no variance)
    special_min_dmg    — damage floor after all reductions
"""

CLASSES = {
    "Knight": {
        # ── Core stats ────────────────────────────────────────────────────────
        "attack":           17,
        "magic_attack":     0,
        "defense":          15,
        "magic_defense":    10,
        "max_hp":           135,
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
        # ── Special move ──────────────────────────────────────────────────────
        "special_name":     "Shield Bash",
        "special_label":    "🛡 Shield Bash",
        "special_desc":     "Normal damage + stun. Enemy cannot counter.",
        "special_cost":     50,
        "special_cooldown": 4,
        "special_multiplier": 1.0,
        "special_effect":     "stun",
        "special_variance":   4,      # randint(0, 4) subtracted from damage
        "special_min_dmg":    5,
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
        "max_hp":           95,
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
        # ── Special move ──────────────────────────────────────────────────────
        "special_name":     "Arcane Burst",
        "special_label":    "✨ Arcane Burst",
        "special_desc":     "2× magic attack. Bypasses all physical armour.",
        "special_cost":     50,
        "special_cooldown": 4,
        "special_multiplier": 2.0,
        "special_effect":     None,
        "special_variance":   0,
        "special_min_dmg":    10,
        # ── Flavour ───────────────────────────────────────────────────────────
        "lore": (
            "Bearer of forbidden glintfire, the Mage whispers truths carved in starlight. "
            "Each spell flung is a shard of a dream long devoured."
        ),
    },
    "Rogue": {
        # ── Core stats ────────────────────────────────────────────────────────
        "attack":           100,
        "magic_attack":     0,
        "defense":          8,
        "magic_defense":    6,
        "max_hp":           118,
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
        # ── Special move ──────────────────────────────────────────────────────
        "special_name":     "Smoke Screen",
        "special_label":    "💨 Smoke Screen",
        "special_desc":     "1× attack damage + guaranteed dodge next enemy turn.",
        "special_cost":     50,
        "special_cooldown": 4,
        "special_multiplier": 1.0,
        "special_effect":     "smoke",
        "special_variance":   0,
        "special_min_dmg":    5,
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
        "max_hp":           110,
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
        # ── Special move ──────────────────────────────────────────────────────
        "special_name":     "Mark Target",
        "special_label":    "🎯 Mark Target",
        "special_desc":     "2× attack. Finds the enemy's weak point.",
        "special_cost":     50,
        "special_cooldown": 4,
        "special_multiplier": 2.0,
        "special_effect":     None,
        "special_variance":   0,
        "special_min_dmg":    5,
        # ── Flavour ───────────────────────────────────────────────────────────
        "lore": (
            "From the ruins of Eldergrove they come, eyes hollow with distant wars. "
            "Each arrow loosed is a memory exiled into the dark."
        ),
    },
}


def get_class(class_name: str) -> dict:
    """Return the class definition dict, or None if not found."""
    return CLASSES.get(class_name)


def get_special_label(class_name: str, fallback: str = "⚡ Special") -> str:
    """Return the special move button label for a given class."""
    cls = CLASSES.get(class_name)
    return cls["special_label"] if cls else fallback


def get_class_icon(class_name: str, fallback: str = "fa-shield-halved") -> str:
    """Return the Font Awesome icon class for a given class."""
    cls = CLASSES.get(class_name)
    return cls["icon"] if cls else fallback