"""
models.py

Sets up the class stats and enemy model.

Refactor:
- All hardcoded class stat dicts (DODGE, BLOCK_MULT, MP_MAX, MAGIC_ATTACK,
  MAGIC_DEFENSE, DAMAGE_TYPE) removed — single source of truth is classes.py
- create() and get_class_stats() now build Character objects from CLASSES dict
- get_dodge(), get_block_mult() etc. read from CLASSES instead of local dicts
- Character constructor and as_dict() unchanged — same interface as before
- Enemy class unchanged
"""

from .classes import CLASSES


class Character:

    # ── Class methods — read from CLASSES, no local dicts ─────────────────────

    @classmethod
    def get_dodge(cls, class_name: str) -> float:
        c = CLASSES.get(class_name)
        return c["dodge_chance"] if c else 0.6

    @classmethod
    def get_block_mult(cls, class_name: str) -> float:
        c = CLASSES.get(class_name)
        return c["block_multiplier"] if c else 0.5

    @classmethod
    def get_mp_max(cls, class_name: str) -> int:
        c = CLASSES.get(class_name)
        return c["mp_max"] if c else 100

    @classmethod
    def get_magic_attack(cls, class_name: str) -> int:
        c = CLASSES.get(class_name)
        return c["magic_attack"] if c else 0

    @classmethod
    def get_magic_defense(cls, class_name: str) -> int:
        c = CLASSES.get(class_name)
        return c["magic_defense"] if c else 0

    @classmethod
    def get_damage_type(cls, class_name: str) -> str:
        c = CLASSES.get(class_name)
        return c["damage_type"] if c else "physical"

    # ── Constructor ────────────────────────────────────────────────────────────

    def __init__(self, name, attack, defense, max_hp, image,
                 crit_chance: float = 0.0, crit_multiplier: float = 1.0):
        self.name             = name
        self.attack           = attack
        self.defense          = defense
        self.max_hp           = max_hp
        self.image            = image
        self.class_name       = name
        self.crit_chance      = crit_chance
        self.crit_multiplier  = crit_multiplier
        self.dodge_chance     = self.get_dodge(self.class_name)
        self.block_multiplier = self.get_block_mult(self.class_name)
        self.mp_max           = self.get_mp_max(self.class_name)
        self.magic_attack     = self.get_magic_attack(self.class_name)
        self.magic_defense    = self.get_magic_defense(self.class_name)
        self.damage_type      = self.get_damage_type(self.class_name)

    def as_dict(self):
        """Convenient for storing in session cleanly."""
        return {
            "name":             self.name,
            "class_name":       self.class_name,
            "attack":           self.attack,
            "defense":          self.defense,
            "max_hp":           self.max_hp,
            "image":            self.image,
            "crit_chance":      self.crit_chance,
            "crit_multiplier":  self.crit_multiplier,
            "dodge_chance":     self.dodge_chance,
            "block_multiplier": self.block_multiplier,
            "mp_max":           self.mp_max,
            "magic_attack":     self.magic_attack,
            "magic_defense":    self.magic_defense,
            "damage_type":      self.damage_type,
        }

    # ── Factory methods ────────────────────────────────────────────────────────

    @staticmethod
    def create(class_name: str):
        """Creates a Character from the CLASSES definition. Returns None if
        class_name is not found."""
        c = CLASSES.get(class_name)
        if not c:
            return None
        return Character(
            name=class_name,
            attack=c["attack"],
            defense=c["defense"],
            max_hp=c["max_hp"],
            image=c["image"],
            crit_chance=c["crit_chance"],
            crit_multiplier=c["crit_multiplier"],
        )

    @staticmethod
    def get_class_stats() -> dict:
        """Returns a dict of {class_name: Character} for all classes.
        Used by index.html to render class selection cards."""
        return {
            name: Character(
                name=name,
                attack=c["attack"],
                defense=c["defense"],
                max_hp=c["max_hp"],
                image=c["image"],
                crit_chance=c["crit_chance"],
                crit_multiplier=c["crit_multiplier"],
            )
            for name, c in CLASSES.items()
        }


class Enemy:
    def __init__(self, name, hp, attack, image=None, lore=None,
                 is_boss=False, soul_reward: int = 0,
                 magic_attack: int = 0, magic_defense: int = 0,
                 defense: int = 0, damage_type: str = "physical"):
        """
        Enemy with full physical/magic stat split (Commit 21).

        attack        — physical attack power
        magic_attack  — magic attack power (0 for physical enemies)
        defense       — physical defence (reduces player physical damage)
        magic_defense — magic defence (reduces player magic damage)
        damage_type   — 'physical', 'magic', or 'mixed'
        """
        self.name          = name
        self.hp            = hp
        self.max_hp        = hp
        self.attack        = attack
        self.magic_attack  = magic_attack
        self.defense       = defense
        self.magic_defense = magic_defense
        self.damage_type   = damage_type
        self.image         = image
        self.lore          = lore
        self.is_boss       = is_boss
        self.soul_reward   = soul_reward