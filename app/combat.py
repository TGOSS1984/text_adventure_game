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
            return Enemy(
                name="Cindergloom",
                hp=180,
                attack=25,
                image="cindergloom.png",
                lore="The final Flame Lord, bound in cinders and regret. Born of divine fire and destined to consume the end of all things.",
                is_boss=True
            )
        else:
            enemies = [
                {
                    "name": "Hollow Knight",
                    "hp": 80,
                    "attack": 18,
                    "image": "hollow_knight.png",
                    "lore": "Once noble, now a shell of oath and rust. Bound to duty, long after purpose has faded.",
                },
                {
                    "name": "Ash Beast",
                    "hp": 70,
                    "attack": 15,
                    "image": "ash_beast.png",
                    "lore": "Forged in the crucibles beneath the mountain. Its bones smolder with endless rage.",
                },
                {
                    "name": "Wraith",
                    "hp": 60,
                    "attack": 17,
                    "image": "wraith.png",
                    "lore": "A cursed soul slipping between realms. It strikes before shadows know it’s there.",
                },
                {
                    "name": "Ghoul",
                    "hp": 65,
                    "attack": 16,
                    "image": "ghoul.png",
                    "lore": "Twisted by hunger and time. Claws etched from broken vows and burial iron.",
                },
                {
                    "name": "Fallen Soldier",
                    "hp": 75,
                    "attack": 14,
                    "image": "fallen_soldier.png",
                    "lore": "He never left the battlefield. His sword still swings, though his war was lost centuries ago.",
                },
            ]
        e = np.random.choice(enemies)
        return Enemy(e["name"], e["hp"], e["attack"], e["image"], e["lore"])

    def attack(self, player, enemy):
        """
        Player's attack on the enemy.
        Damage is based on player's attack minus a small random amount.
        """
        dmg = player["attack"] - np.random.randint(0, 6)
        dmg = max(5, dmg)
        enemy.hp -= dmg
        return f"You strike the {enemy.name} for {dmg} damage!", enemy.hp

    def enemy_attack(self, player, enemy, action=None):
        if action not in ["attack", "big_hit", "flurry"]:
            action = np.random.choice(["attack", "big_hit", "flurry"], p=[0.6, 0.25, 0.15])

        if action == "flurry":
            hits = np.random.randint(4, 6)  # More hits: 4–5
            single_hit = max(2, enemy.attack // 3) + np.random.randint(6, 10)
            dmg = hits * single_hit - player["defense"] // 5
            dmg = max(15, dmg)  # Raise min to reflect danger
            msg = f"The enemy unleashes a flurry of {hits} strikes!"
        elif action == "big_hit":
            dmg = enemy.attack + np.random.randint(10, 20) - player["defense"] // 2
            dmg = max(8, dmg)
            msg = "A massive attack is incoming!"
        else:
            dmg = enemy.attack + np.random.randint(0, 10) - player["defense"] // 3
            dmg = max(5, dmg)
            msg = "A swift strike!"

        return action, msg, dmg


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
        move = np.random.choice(["attack", "big_hit", "flurry"], p=[0.6, 0.25, 0.15])

        if move == "flurry":
            return "flurry", "The enemy is angered and preparing a flurry of strikes!", None
        elif move == "big_hit":
            return "big_hit", "The enemy is preparing a massive attack!", None
        else:
            return "attack", "The enemy is preparing a standard attack.", None

