"""
models.py

Sets up the class stats
Shows the player & enemy stats
"""


class Character:
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
        }

    @staticmethod
    def create(class_name):
        """
        Creates a Character based on the selected class name.
        Each class has unique base stats.
        """
        if class_name == "Knight":
            return Character("Knight", 15, 12, 135, "classes/knight.png",
                             crit_chance=0.20, crit_multiplier=1.5)
        elif class_name == "Mage":
            return Character("Mage", 25, 6, 95, "classes/mage.png",
                             crit_chance=0.30, crit_multiplier=1.5)
        elif class_name == "Rogue":
            return Character("Rogue", 20, 8, 105, "classes/rogue.png",
                             crit_chance=0.40, crit_multiplier=1.5)
        elif class_name == "Archer":
            return Character("Archer", 18, 9, 110, "classes/archer.png",
                             crit_chance=0.50, crit_multiplier=1.5)

    @staticmethod
    def get_class_stats():
        return {
            "Knight": Character("Knight", 15, 11, 135, "knight.png",
                                crit_chance=0.20, crit_multiplier=1.5),
            "Mage": Character("Mage", 25, 6, 95, "mage.png",
                              crit_chance=0.30, crit_multiplier=1.5),
            "Rogue": Character("Rogue", 20, 8, 105, "rogue.png",
                               crit_chance=0.40, crit_multiplier=1.5),
            "Archer": Character("Archer", 18, 9, 110, "archer.png",
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
