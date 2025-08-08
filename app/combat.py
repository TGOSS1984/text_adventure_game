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
from .enemies import ENEMIES, BOSSES
from .models import Enemy, Character   # <-- add Character here


class BattleManager:
    def __init__(self):
        pass  # No longer storing estus_flasks here

    def generate_enemy(self, boss=False, boss_name=None):
        """
        Generates an enemy.

        If boss=True and boss_name is given, returns the named boss.
        If boss=True with no name, defaults to Cindergloom.
        Otherwise returns a random standard enemy.
        """
        if boss:
            name = boss_name or "Cindergloom"
            data = BOSSES.get(name)

            if not data:
                print(f"[WARN] Boss '{name}' not found. Defaulting to Cindergloom.")
                name = "Cindergloom"
                data = BOSSES[name]

            return Enemy(
                name=name,
                hp=data["hp"],
                attack=data["attack"],
                image=data["image"],
                lore=data["lore"],
                is_boss=True
            )
        else:
            e = np.random.choice(ENEMIES)
            return Enemy(
                name=e["name"],
                hp=e["hp"],
                attack=e["attack"],
                image=e["image"],
                lore=e["lore"]
            )


    def attack(self, player, enemy):
        """
        Player's attack on the enemy.
        Damage is based on player's attack minus a small random amount.
        Crit multiplier is applied BEFORE randomness so a crit is always stronger than any normal hit.
        """
        # Crit roll (safe defaults if fields are missing)
        crit_chance = float(player.get("crit_chance", 0.0))
        crit_multiplier = float(player.get("crit_multiplier", 1.0))
        is_crit = np.random.rand() < crit_chance

        # Apply multiplier to the ATTACK STAT before randomness
        base_attack = player["attack"] * crit_multiplier if is_crit else player["attack"]

        # Keep your original randomness + min clamp
        dmg = base_attack - np.random.randint(0, 6)
        dmg = max(5, int(round(dmg)))

        enemy.hp -= dmg

        if is_crit:
            msg = f"💥 Critical hit! You strike the {enemy.name} for {dmg} damage!"
        else:
            msg = f"You strike the {enemy.name} for {dmg} damage!"

        return msg, enemy.hp

    def enemy_attack(self, player, enemy, action=None):
        if action not in ["attack", "big_hit", "flurry"]:
            action = np.random.choice(["attack", "big_hit", "flurry"], p=[0.6, 0.25, 0.15])

        if action == "flurry":
            hits = np.random.randint(4, 6)  # More hits: 4–5
            single_hit = max(2, enemy.attack // 3) + np.random.randint(6, 10)
            dmg = hits * single_hit - int(player["defense"] * 1.0)
            dmg = max(15, dmg)  # Raise min to reflect danger
            msg = f"The enemy unleashes a flurry of {hits} strikes!"
        elif action == "big_hit":
            dmg = enemy.attack + np.random.randint(10, 20) - int(player["defense"] * 0.8)
            dmg = max(8, dmg)
            msg = "A massive attack is incoming!"
        else:
            dmg = enemy.attack + np.random.randint(0, 10) - int(player["defense"] * 1.1)
            dmg = max(5, dmg)
            msg = "A swift strike!"

        return action, msg, dmg


    def resolve_player_action(self, move_type, player_action, dmg, current_hp, player):
        """
        Resolves player's action: dodge, block, or none.
        Applies class-based modifiers for dodge and block.
        """
        class_name = player.get("class_name", "Knight")  # Default fallback
        result = ""


        if player_action == "dodge":
            # NEW: pull dodge chance from Character
            success_chance = Character.get_dodge(class_name)
            success = np.random.rand() < success_chance
            success = np.random.rand() < success_chance
            if success:
                result = "You dodged the attack completely!"
                return current_hp, result
            else:
                current_hp -= dmg
                result = f"You failed to dodge and took {dmg} damage."

        elif player_action == "block":
                # NEW: pull block multiplier from Character
                reduction_ratio = Character.get_block_mult(class_name)
                blocked = int(dmg * reduction_ratio)
                current_hp -= blocked
                result = f"You blocked the hit and took {blocked} damage."

        else:  # no defense
            current_hp -= dmg
            result = f"You took {dmg} damage."

        return current_hp, result


    def use_estus(self, hp, max_hp):
        """
        Uses an Estus Flask to heal the player.
        Heals 70% of max HP and reduces flask count. Updates Flask session. Total flasks are currently 3.
        """
        estus = session.get("estus", 0)
        if estus > 0:
            healed = int(max_hp * 0.7)
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

