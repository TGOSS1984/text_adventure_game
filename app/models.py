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
"""


class Character:

    # ── Defensive modifiers

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

    # ── MP pool per class
    # Reflects each class's relationship with special abilities:
    #   Knight: lowest — brute force, special is a utility stun
    #   Mage:   highest — glass cannon, special is their main damage spike
    #   Rogue:  mid — evasion specialist, special is a defensive escape
    #   Archer: mid — balanced, special amplifies their already-high crit

    MP_MAX = {
        "Knight": 80,
        "Mage":   120,
        "Rogue":  100,
        "Archer": 100,
    }

    @classmethod
    def get_dodge(cls, class_name: str) -> float:
        return cls.DODGE.get(class_name, 0.6)

    @classmethod
    def get_block_mult(cls, class_name: str) -> float:
        return cls.BLOCK_MULT.get(class_name, 0.5)

    @classmethod
    def get_mp_max(cls, class_name: str) -> int:
        return cls.MP_MAX.get(class_name, 100)

    # ── Constructor

    def __init__(self, name, attack, defense, max_hp, image,
                 crit_chance: float = 0.0, crit_multiplier: float = 1.0):
        self.name            = name
        self.attack          = attack
        self.defense         = defense
        self.max_hp          = max_hp
        self.image           = image
        self.class_name      = name
        self.crit_chance     = crit_chance
        self.crit_multiplier = crit_multiplier
        self.dodge_chance    = self.get_dodge(self.class_name)
        self.block_multiplier = self.get_block_mult(self.class_name)
        self.mp_max          = self.get_mp_max(self.class_name)

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
        }

    # ── Factory methods

    @staticmethod
    def create(class_name):
        """Creates a Character based on the selected class name."""
        classes = {
            "Knight": Character("Knight", 15, 15, 135, "classes/knight.png",
                                crit_chance=0.20, crit_multiplier=1.5),
            "Mage":   Character("Mage",   28,  6,  95, "classes/mage.png",
                                crit_chance=0.30, crit_multiplier=1.5),
            "Rogue":  Character("Rogue",  20,  8, 105, "classes/rogue.png",
                                crit_chance=0.40, crit_multiplier=1.5),
            "Archer": Character("Archer", 18, 10, 110, "classes/archer.png",
                                crit_chance=0.50, crit_multiplier=1.5),
        }
        return classes.get(class_name)

    @staticmethod
    def get_class_stats():
        return {
            "Knight": Character("Knight", 15, 15, 135, "knight.png",
                                crit_chance=0.20, crit_multiplier=1.5),
            "Mage":   Character("Mage",   28,  6,  95, "mage.png",
                                crit_chance=0.30, crit_multiplier=1.5),
            "Rogue":  Character("Rogue",  20,  8, 105, "rogue.png",
                                crit_chance=0.40, crit_multiplier=1.5),
            "Archer": Character("Archer", 18, 10, 110, "archer.png",
                                crit_chance=0.50, crit_multiplier=1.5),
        }


class Enemy:
    def __init__(self, name, hp, attack, image=None, lore=None,
                 is_boss=False, soul_reward: int = 0):
        """Enemy with name, HP, attack power, optional image, lore, and soul reward."""
        self.name        = name
        self.hp          = hp
        self.max_hp      = hp
        self.attack      = attack
        self.image       = image
        self.lore        = lore
        self.is_boss     = is_boss
        self.soul_reward = soul_reward  # Commit 10: souls awarded on kill