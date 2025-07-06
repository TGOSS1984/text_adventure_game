"""
combat.py

Manages all battle-related logic 
Includes mechanics for:
- Enemy generation
- Attack resolution
- Estus Flask usage (Healing)
- Dodge/block/standard defense handling
- Predicting enemy moves

Uses NumPy for randomness and imports models for Enemy structure.
"""

import numpy as np
from .models import Enemy
from flask import session

class BattleManager:
    def __init__(self):
        pass  # No longer storing estus_flasks here

    def generate_enemy(self, boss=False):
        """
        Generates an enemy.
        If 'boss' is True, returns the final boss. Otherwise selects a random enemy from list.
        """
        if boss:
            return Enemy("Cindergloom", 180, 25)
        else:
            enemies = [
                {"name": "Hollow Knight", "hp": 80, "attack": 18},
                {"name": "Ash Beast", "hp": 70, "attack": 15},
                {"name": "Wraith", "hp": 60, "attack": 17},
                {"name": "Ghoul", "hp": 65, "attack": 16},
                {"name": "Fallen Soldier", "hp": 75, "attack": 14},
            ]
            e = np.random.choice(enemies)
            return Enemy(e["name"], e["hp"], e["attack"])

    def attack(self, player, enemy):
        """
        Player's attack on the enemy.
        Damage is based on player's attack minus a small random amount.
        """
        dmg = player["attack"] - np.random.randint(0, 6)
        dmg = max(5, dmg)
        enemy.hp -= dmg
        return f"You strike the {enemy.name} for {dmg} damage!", enemy.hp

    def enemy_attack(self, player, action="attack"):
        """
        Randomly selects enemy's move: standard attack or a 'big hit'.
        Damage is calculated differently depending on the move type. 
        Added so that it may help the player to choose to dodge or defend rather than just attack every time.
        """
        move = np.random.choice(["attack", "big_hit"])
        dmg = 0
        msg = ""

        if move == "big_hit":
            dmg = player["defense"] // 2 + np.random.randint(10, 25)
            msg = "A massive attack is incoming!"
        else:
            dmg = player["defense"] // 3 + np.random.randint(5, 15)
            msg = "A swift strike!"

        return move, msg, dmg

    def resolve_player_action(self, move_type, player_action, dmg, current_hp):
        """
        Resolves the player's defensive action (dodge, block, or none) against the enemy's move.
        Calculates new HP and returns result message.
        """
        result = ""
        if player_action == "dodge":
            success = np.random.rand() < 0.6
            if success:
                result = "You dodged the attack completely!"
                return current_hp, result
            else:
                current_hp -= dmg
                result = f"You failed to dodge and took {dmg} damage."
        elif player_action == "block":
            blocked = int(dmg / 2)
            current_hp -= blocked
            result = f"You blocked the hit and took {blocked} damage."
        else:  # no defense
            current_hp -= dmg
            result = f"You took {dmg} damage."
        return current_hp, result

    def use_estus(self, hp, max_hp):
        """
        Uses an Estus Flask to heal the player.
        Heals 60% of max HP and reduces flask count. Updates Flask session. Total flasks are currently 3.
        """
        estus = session.get("estus", 0)
        if estus > 0:
            healed = int(max_hp * 0.6)
            hp = min(hp + healed, max_hp)
            session["estus"] = estus - 1
            return hp, f"You drink from the Estus Flask and recover {healed} HP."
        return hp, "No Estus Flasks left!"

    def predict_enemy_move(self, player):
        """Predicts the enemy's next move for display purposes."""
        
        move = np.random.choice(["attack", "big_hit"])
        if move == "big_hit":
            return "big_hit", "The enemy is preparing a massive attack!", None
        else:
            return "attack", "The enemy is preparing a standard attack.", None