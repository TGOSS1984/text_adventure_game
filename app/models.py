"""
models.py

Sets up the class stats
Shows the player & enemy stats
"""


class Character:
    def __init__(self, name, attack, defense, max_hp):
        """
        Sets up a character with name, attack power, defense, and max HP.
        """
        self.name = name
        self.attack = attack
        self.defense = defense
        self.max_hp = max_hp

    @staticmethod
    def create(class_name):
        """
        Creates a Character based on the selected class name.
        Each class has unique base stats.
        """
        if class_name == "Knight":
            return Character("Knight", 15, 10, 125)
        elif class_name == "Mage":
            return Character("Mage", 25, 5, 85)
        elif class_name == "Rogue":
            return Character("Rogue", 20, 7, 95)
        elif class_name == "Archer":
            return Character("Archer", 18, 8, 100)
        
    @staticmethod
    def get_class_stats():
        return {
            "Knight": Character("Knight", 15, 10, 125),
            "Mage": Character("Mage", 25, 5, 85),
            "Rogue": Character("Rogue", 20, 7, 95),
            "Archer": Character("Archer", 18, 8, 100),
        }


class Enemy:
    def __init__(self, name, hp, attack, image=None, lore=None, is_boss=False):
        """
        Enemy with a name, HP, attack power, optional image, and lore.
        """
        self.name = name
        self.hp = hp
        self.attack = attack
        self.image = image
        self.lore = lore
        self.is_boss = is_boss