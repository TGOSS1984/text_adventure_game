"""
models.py

Sets up the class stats
Shows the player & enemy stats
"""


class Character:
    def __init__(self, name, attack, defense, max_hp, image):
        """
        Sets up a character with name, attack power, defense, and max HP.
        """
        self.name = name
        self.attack = attack
        self.defense = defense
        self.max_hp = max_hp
        self.image = image
        self.class_name = name

    @staticmethod
    def create(class_name):
        """
        Creates a Character based on the selected class name.
        Each class has unique base stats.
        """
        if class_name == "Knight":
            return Character("Knight", 15, 11, 125, "classes/knight.png")
        elif class_name == "Mage":
            return Character("Mage", 25, 6, 85, "classes/mage.png")
        elif class_name == "Rogue":
            return Character("Rogue", 20, 8, 95, "classes/rogue.png")
        elif class_name == "Archer":
            return Character("Archer", 18, 9, 100, "classes/archer.png")
        
    @staticmethod
    def get_class_stats():
        return {
            "Knight": Character("Knight", 15, 11, 125, "knight.png"),
            "Mage": Character("Mage", 25, 6, 85, "mage.png"),
            "Rogue": Character("Rogue", 20, 8, 95, "rogue.png"),
            "Archer": Character("Archer", 18, 9, 100, "archer.png"),
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