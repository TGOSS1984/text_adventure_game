"""
models.py

Sets up the class stats.
Shows the player & enemy stats.

Commit 7 additions:
- mp_max added per class (Knight 80, Mage 120, Rogue 100, Archer 100)
- as_dict() includes mp_max so session stores it

Commit 10 additions:
- Enemy gains soul_reward field (int, default 0)
- soul_reward passed through to routes.py for awarding on kill

Commit 21 additions:
- magic_attack stat per class (Mage only; physical classes = 0)
- magic_defense stat per class
- damage_type per class ('physical' or 'magic')
- MAGIC_ATTACK, MAGIC_DEFENSE, DAMAGE_TYPE class dicts added
- as_dict() updated to include all three new fields
- Enemy gains magic_attack, magic_defense, defense, damage_type fields
- Rogue HP adjusted 105 -> 118 (balance pass commit 21)
- Knight attack adjusted 15 -> 17 (balance pass commit 21)
"""


class Character:

    # ── Defensive modifiers ────────────────────────────────────────────────────

    DODGE = {
        "Knight": 0.2,
        "Mage":   0.6,
        "Rogue":  0.7,
        "Archer": 0.5,
    }

    # Damage taken multiplier while blocking (0.25 => take 25% of damage)
    BLOCK_MULT = {
        "Knight": 0.25,
        "Rogue":  0.50,
        "Archer": 0.40,
        "Mage":   0.50,
    }

    # ── MP pool per class ──────────────────────────────────────────────────────
    MP_MAX = {
        "Knight": 80,
        "Mage":   120,
        "Rogue":  100,
        "Archer": 100,
    }

    # ── Commit 21: magic attack per class ─────────────────────────────────────
    # Mage deals magic damage; all other classes deal physical damage.
    # Physical classes have magic_attack = 0 — the field is stored for
    # completeness and future extensibility (new classes, enchanted weapons).
    MAGIC_ATTACK = {
        "Knight": 0,
        "Mage":   28,   # Mage's primary damage stat
        "Rogue":  0,
        "Archer": 0,
    }

    # ── Commit 21: magic defense per class ────────────────────────────────────
    # How much magic damage the class can absorb.
    # Knight: mid — armour provides some magic warding
    # Mage:   highest — innate magical attunement
    # Rogue:  lowest — no protection, relies on dodge
    # Archer: mid-low — light armour, some natural resistance
    MAGIC_DEFENSE = {
        "Knight": 10,
        "Mage":   18,
        "Rogue":  6,
        "Archer": 8,
    }

    # ── Commit 21: damage type per class ─────────────────────────────────────
    # Determines which enemy stat (defense or magic_defense) resists the
    # player's attacks, and which icon/label is shown in the UI.
    DAMAGE_TYPE = {
        "Knight": "physical",
        "Mage":   "magic",
        "Rogue":  "physical",
        "Archer": "physical",
    }

    # ── Class methods ──────────────────────────────────────────────────────────

    @classmethod
    def get_dodge(cls, class_name: str) -> float:
        return cls.DODGE.get(class_name, 0.6)

    @classmethod
    def get_block_mult(cls, class_name: str) -> float:
        return cls.BLOCK_MULT.get(class_name, 0.5)

    @classmethod
    def get_mp_max(cls, class_name: str) -> int:
        return cls.MP_MAX.get(class_name, 100)

    @classmethod
    def get_magic_attack(cls, class_name: str) -> int:
        return cls.MAGIC_ATTACK.get(class_name, 0)

    @classmethod
    def get_magic_defense(cls, class_name: str) -> int:
        return cls.MAGIC_DEFENSE.get(class_name, 0)

    @classmethod
    def get_damage_type(cls, class_name: str) -> str:
        return cls.DAMAGE_TYPE.get(class_name, "physical")

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
        # Commit 21
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
            # Commit 21
            "magic_attack":     self.magic_attack,
            "magic_defense":    self.magic_defense,
            "damage_type":      self.damage_type,
        }

    # ── Factory methods ────────────────────────────────────────────────────────

    @staticmethod
    def create(class_name):
        """Creates a Character based on the selected class name."""
        classes = {
            # Commit 21: Knight attack 15->17, Rogue hp 105->118
            "Knight": Character("Knight", 17, 15, 135, "classes/knight.png",
                                crit_chance=0.20, crit_multiplier=1.5),
            "Mage":   Character("Mage",    0,  6,  95, "classes/mage.png",
                                crit_chance=0.30, crit_multiplier=1.5),
            "Rogue":  Character("Rogue",  20,  8, 118, "classes/rogue.png",
                                crit_chance=0.40, crit_multiplier=1.5),
            "Archer": Character("Archer", 18, 10, 110, "classes/archer.png",
                                crit_chance=0.50, crit_multiplier=1.5),
        }
        return classes.get(class_name)

    @staticmethod
    def get_class_stats():
        return {
            "Knight": Character("Knight", 17, 15, 135, "knight.png",
                                crit_chance=0.20, crit_multiplier=1.5),
            "Mage":   Character("Mage",    0,  6,  95, "mage.png",
                                crit_chance=0.30, crit_multiplier=1.5),
            "Rogue":  Character("Rogue",  20,  8, 118, "rogue.png",
                                crit_chance=0.40, crit_multiplier=1.5),
            "Archer": Character("Archer", 18, 10, 110, "archer.png",
                                crit_chance=0.50, crit_multiplier=1.5),
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