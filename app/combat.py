"""
combat.py

Manages all battle-related logic.
Includes mechanics for:
- Enemy generation
- Attack resolution
- Estus Flask usage (healing)
- Dodge / block / standard defence handling
- Predicting enemy moves

Uses NumPy for randomness and imports models for Enemy/Character structure.

Design note: this module is deliberately free of Flask imports.
All state (HP, estus count) is passed in as arguments and returned as
values so that combat logic can be unit-tested without an app context.
"""

import numpy as np
from .models import Enemy, Character
from .enemies import ENEMIES, BOSSES


class BattleManager:
    def __init__(self):
        pass

    # ------------------------------------------------------------------
    # Enemy generation
    # ------------------------------------------------------------------

    def generate_enemy(self, boss=False, boss_name=None):
        """
        Generate an enemy for the current encounter.

        If boss=True and boss_name is given, returns the named boss.
        If boss=True with no name, defaults to Cindergloom.
        Otherwise returns a random standard enemy.
        """
        if boss:
            name = boss_name or 'Cindergloom'
            data = BOSSES.get(name)

            if not data:
                print(f"[WARN] Boss '{name}' not found. Defaulting to Cindergloom.")
                name = 'Cindergloom'
                data = BOSSES[name]

            return Enemy(
                name=name,
                hp=data['hp'],
                attack=data['attack'],
                image=data['image'],
                lore=data['lore'],
                is_boss=True,
            )
        else:
            e = np.random.choice(ENEMIES)
            return Enemy(
                name=e['name'],
                hp=e['hp'],
                attack=e['attack'],
                image=e['image'],
                lore=e['lore'],
            )

    # ------------------------------------------------------------------
    # Player actions
    # ------------------------------------------------------------------

    def attack(self, player, enemy):
        """
        Resolve the player's attack on the enemy.

        Damage is based on the player's attack stat minus a small random
        amount. A crit multiplier is applied before randomness so a crit
        is always stronger than any normal hit.

        Returns (message: str, new_enemy_hp: int).
        """
        crit_chance = float(player.get('crit_chance', 0.0))
        crit_multiplier = float(player.get('crit_multiplier', 1.0))
        is_crit = np.random.rand() < crit_chance

        base_attack = player['attack'] * crit_multiplier if is_crit else player['attack']
        dmg = base_attack - np.random.randint(0, 6)
        dmg = max(5, int(round(dmg)))

        enemy.hp -= dmg

        if is_crit:
            msg = f"💥 Critical hit! You strike the {enemy.name} for {dmg} damage!"
        else:
            msg = f"You strike the {enemy.name} for {dmg} damage!"

        return msg, enemy.hp

    def use_estus(self, current_hp, max_hp, estus_count):
        """
        Use an Estus Flask to heal the player.

        Heals 70 % of max HP, capped at max_hp.
        The caller is responsible for passing the current estus_count and
        storing the returned value — this method no longer reads or writes
        Flask session directly.

        Returns (new_hp: int, new_estus_count: int, message: str).
        """
        if estus_count <= 0:
            return current_hp, 0, "No Estus Flasks left!"

        healed = int(max_hp * 0.7)
        new_hp = min(current_hp + healed, max_hp)
        new_estus = estus_count - 1
        msg = f"You drink from the Estus Flask and recover {healed} HP."
        return new_hp, new_estus, msg

    # ------------------------------------------------------------------
    # Enemy actions
    # ------------------------------------------------------------------

    def enemy_attack(self, player, enemy, action=None):
        """
        Resolve the enemy's attack move.

        action can be 'attack', 'big_hit', or 'flurry'. If not provided
        (or invalid), a move is chosen randomly according to base weights.

        Returns (action: str, warning_message: str, damage: int).
        """
        if action not in ('attack', 'big_hit', 'flurry'):
            action = np.random.choice(
                ['attack', 'big_hit', 'flurry'], p=[0.6, 0.25, 0.15]
            )

        if action == 'flurry':
            hits = np.random.randint(3, 6)
            single_hit = max(2, enemy.attack // 3) + np.random.randint(6, 10)
            dmg = hits * single_hit - int(player['defense'] * 1.0)
            dmg = max(15, dmg)
            msg = f"The enemy unleashes a flurry of {hits} strikes!"

        elif action == 'big_hit':
            dmg = enemy.attack + np.random.randint(10, 20) - int(player['defense'] * 0.8)
            dmg = max(8, dmg)
            msg = "A massive attack is incoming!"

        else:  # standard attack
            dmg = enemy.attack + np.random.randint(0, 10) - int(player['defense'] * 1.1)
            dmg = max(5, dmg)
            msg = "A swift strike!"

        return action, msg, dmg

    def resolve_player_action(self, move_type, player_action, dmg, current_hp, player):
        """
        Apply the enemy's damage to the player, modified by their chosen
        defensive action (dodge / block / none).

        Returns (new_hp: int, result_message: str).
        """
        class_name = player.get('class_name', 'Knight')

        if player_action == 'dodge':
            success_chance = Character.get_dodge(class_name)
            if np.random.rand() < success_chance:
                return current_hp, "You dodged the attack completely!"
            else:
                new_hp = current_hp - dmg
                return new_hp, f"You failed to dodge and took {dmg} damage."

        elif player_action == 'block':
            reduction_ratio = Character.get_block_mult(class_name)
            blocked = int(dmg * reduction_ratio)
            new_hp = current_hp - blocked
            return new_hp, f"You blocked the hit and took {blocked} damage."

        else:  # no defence
            new_hp = current_hp - dmg
            return new_hp, f"You took {dmg} damage."

    # ------------------------------------------------------------------
    # Prediction (for move-hint UI)
    # ------------------------------------------------------------------

    def predict_enemy_move(self, player):
        """
        Predict the enemy's next move for display in the UI hint.

        Returns (move: str, hint_message: str, damage: None).
        """
        move = np.random.choice(['attack', 'big_hit', 'flurry'], p=[0.6, 0.25, 0.15])

        messages = {
            'flurry':   "The enemy is angered and preparing a flurry of strikes!",
            'big_hit':  "The enemy is preparing a massive attack!",
            'attack':   "The enemy is preparing a standard attack.",
        }
        return move, messages[move], None