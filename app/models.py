"""
models.py

Sets up the class stats
Shows the player & enemy stats
"""


class Character:
        # --- NEW: centralised class modifiers ---
    DODGE = {
        "Knight": 0.2,
        "Mage": 0.6,
        "Rogue": 0.7,
        "Archer": 0.5,
    }
    # Damage taken multiplier while blocking (0.25 => take 25% of damage)
    BLOCK_MULT = {
        "Knight": 0.25,
        "Rogue": 0.5,
        "Archer": 0.4,
        "Mage": 0.5,
    }

    @classmethod
    def get_dodge(cls, class_name: str) -> float:
        return cls.DODGE.get(class_name, 0.6)

    @classmethod
    def get_block_mult(cls, class_name: str) -> float:
        return cls.BLOCK_MULT.get(class_name, 0.5)

    def __init__(self, name, attack, defense, max_hp, image,
                 crit_chance: float = 0.0, crit_multiplier: float = 1.0):
        """
        Sets up a character with name, attack power, defense, and max HP.
        """
        self.name = name
        self.attack = attack
        self.defense = defense
        self.max_hp = max_hp
        self.image = image
        self.class_name = name
        # NEW
        self.crit_chance = crit_chance        # e.g., 0.20 for 20%
        self.crit_multiplier = crit_multiplier  # e.g., 1.2
        # --- NEW: expose defensive profile on the instance ---
        self.dodge_chance = self.get_dodge(self.class_name)
        self.block_multiplier = self.get_block_mult(self.class_name)

    def as_dict(self):
        """Convenient for storing in session cleanly."""
        return {
            "name": self.name,
            "class_name": self.class_name,
            "attack": self.attack,
            "defense": self.defense,
            "max_hp": self.max_hp,
            "image": self.image,
            "crit_chance": self.crit_chance,
            "crit_multiplier": self.crit_multiplier,
            "dodge_chance": self.dodge_chance,           # NEW
            "block_multiplier": self.block_multiplier,   # NEW
        }

    @staticmethod
    def create(class_name):
        """
        Creates a Character based on the selected class name.
        Each class has unique base stats.
        """
        if class_name == "Knight":
            return Character("Knight", 15, 15, 135, "classes/knight.png",
                             crit_chance=0.20, crit_multiplier=1.5)
        elif class_name == "Mage":
            return Character("Mage", 25, 6, 95, "classes/mage.png",
                             crit_chance=0.30, crit_multiplier=1.5)
        elif class_name == "Rogue":
            return Character("Rogue", 20, 8, 105, "classes/rogue.png",
                             crit_chance=0.40, crit_multiplier=1.5)
        elif class_name == "Archer":
            return Character("Archer", 18, 10, 110, "classes/archer.png",
                             crit_chance=0.50, crit_multiplier=1.5)

    @staticmethod
    def get_class_stats():
        return {
            "Knight": Character("Knight", 15, 15, 135, "knight.png",
                                crit_chance=0.20, crit_multiplier=1.5),
            "Mage": Character("Mage", 25, 6, 95, "mage.png",
                              crit_chance=0.30, crit_multiplier=1.5),
            "Rogue": Character("Rogue", 20, 8, 105, "rogue.png",
                               crit_chance=0.40, crit_multiplier=1.5),
            "Archer": Character("Archer", 18, 10, 110, "archer.png",
                                crit_chance=0.50, crit_multiplier=1.5),
        }


class Enemy:
    def __init__(self, name, hp, attack, image=None, lore=None, is_boss=False):
        """
        Enemy with a name, HP, attack power, optional image, and lore.
        """
        self.name = name
        self.hp = hp
        self.max_hp = hp
        self.attack = attack
        self.image = image
        self.lore = lore
        self.is_boss = is_boss
