"""
combat.py

Manages all battle-related logic.

Commit 7 additions:
- use_special(): resolves the class special move
- enemy_attack() respects the 'stunned' flag (skips counter if stunned)
- resolve_player_action() respects 'smoke_screen_active' flag (guaranteed dodge)

Special move design:
  Knight  — Shield Bash:   Normal attack damage + stun (enemy loses their counter this turn)
  Mage    — Arcane Burst:  2.0× attack, bypasses all defence (magic damage)
  Rogue   — Smoke Screen:  No damage; guarantees dodge on the NEXT enemy counter
  Archer  — Mark Target:   Guaranteed critical at 2.0× multiplier (vs normal 1.5×)

All specials:
  - Cost 35 MP
  - 3-turn cooldown after use
  - Regen 20 MP per turn (handled in routes.py)
"""

import numpy as np
from .models import Enemy, Character
from .enemies import ENEMIES, BOSSES

# ── Constants ──────────────────────────────────────────────────────────────────
MP_COST        = 50   # MP cost per special use — high enough to limit spam
MP_REGEN_ATTACK = 25   # MP earned only when player chooses Attack
                        # Passive actions (dodge/block/estus) earn nothing —
                        # you must fight aggressively to build your special
COOLDOWN_TURNS  = 4   # turns before special can be used again


class BattleManager:

    # ── Enemy generation ───────────────────────────────────────────────────────

    def generate_enemy(self, boss=False, boss_name=None):
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

    # ── Player actions ─────────────────────────────────────────────────────────

    def attack(self, player, enemy):
        """
        Standard attack. Returns (message, new_enemy_hp).
        """
        crit_chance      = float(player.get('crit_chance', 0.0))
        crit_multiplier  = float(player.get('crit_multiplier', 1.0))
        is_crit          = np.random.rand() < crit_chance

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
        Heal 70% of max HP. Returns (new_hp, new_estus_count, message).
        """
        if estus_count <= 0:
            return current_hp, 0, "No Estus Flasks left!"

        healed   = int(max_hp * 0.7)
        new_hp   = min(current_hp + healed, max_hp)
        new_estus = estus_count - 1
        msg      = f"You drink from the Estus Flask and recover {healed} HP."
        return new_hp, new_estus, msg

    def use_special(self, player, enemy, current_mp, cooldown):
        """
        Resolve the class-specific special move.

        Guards (MP and cooldown) are checked here so combat.py stays the
        single source of truth for special-move logic.

        Returns:
            message          (str)  — narrative result shown to player
            new_enemy_hp     (int)  — updated enemy HP (unchanged for non-damage specials)
            new_mp           (int)  — updated MP after cost
            new_cooldown     (int)  — cooldown turns set (COOLDOWN_TURNS)
            stun_enemy       (bool) — True if enemy loses their counter this turn
            smoke_screen     (bool) — True if next enemy counter is guaranteed-dodged
        """
        class_name = player.get('class_name', 'Knight')

        if current_mp < MP_COST:
            return (
                f"Not enough MP! ({current_mp}/{MP_COST} needed)",
                enemy.hp, current_mp, cooldown, False, False
            )
        if cooldown > 0:
            return (
                f"Special move recharging — {cooldown} turn{'s' if cooldown != 1 else ''} remaining.",
                enemy.hp, current_mp, cooldown, False, False
            )

        new_mp       = current_mp - MP_COST
        new_cooldown = COOLDOWN_TURNS
        stun_enemy   = False
        smoke_screen = False

        # ── Knight: Shield Bash ───────────────────────────────────────────────
        if class_name == 'Knight':
            dmg = player['attack'] - np.random.randint(0, 4)
            dmg = max(5, int(round(dmg)))
            enemy.hp -= dmg
            stun_enemy = True
            msg = (
                f"🛡️ Shield Bash! You crash your shield into the {enemy.name} "
                f"for {dmg} damage and stun them — they cannot counter this turn!"
            )

        # ── Mage: Arcane Burst ────────────────────────────────────────────────
        elif class_name == 'Mage':
            # Magic damage: 2.0× attack, bypasses all physical defence
            dmg = int(round(player['attack'] * 2.0))
            dmg = max(10, dmg)
            enemy.hp -= dmg
            msg = (
                f"✨ Arcane Burst! A torrent of magic tears through the "
                f"{enemy.name} for {dmg} damage — defence is useless against pure arcane force!"
            )

        # ── Rogue: Smoke Screen ───────────────────────────────────────────────
        elif class_name == 'Rogue':
            smoke_screen = True
            msg = (
                "💨 Smoke Screen! You vanish into shadow — the enemy's next "
                "attack will find nothing but smoke."
            )

        # ── Archer: Mark Target ───────────────────────────────────────────────
        elif class_name == 'Archer':
            # Guaranteed crit at 2.0× multiplier instead of normal 1.5×
            dmg = int(round(player['attack'] * 2.0))
            dmg = max(5, dmg)
            enemy.hp -= dmg
            msg = (
                f"🎯 Mark Target! A perfectly placed arrow finds the "
                f"{enemy.name}'s weak point for {dmg} damage!"
            )

        else:
            msg = "No special move available for this class."

        return msg, enemy.hp, new_mp, new_cooldown, stun_enemy, smoke_screen

    # ── Enemy actions ──────────────────────────────────────────────────────────

    def enemy_attack(self, player, enemy, action=None):
        """
        Resolve the enemy's attack move.
        Returns (action, warning_message, damage).
        """
        if action not in ('attack', 'big_hit', 'flurry'):
            action = np.random.choice(
                ['attack', 'big_hit', 'flurry'], p=[0.6, 0.25, 0.15]
            )

        if action == 'flurry':
            hits       = np.random.randint(3, 6)
            single_hit = max(2, enemy.attack // 3) + np.random.randint(6, 10)
            dmg        = hits * single_hit - int(player['defense'] * 1.0)
            dmg        = max(15, dmg)
            msg        = f"The enemy unleashes a flurry of {hits} strikes!"

        elif action == 'big_hit':
            dmg = enemy.attack + np.random.randint(10, 20) - int(player['defense'] * 0.8)
            dmg = max(8, dmg)
            msg = "A massive attack is incoming!"

        else:
            dmg = enemy.attack + np.random.randint(0, 10) - int(player['defense'] * 1.1)
            dmg = max(5, dmg)
            msg = "A swift strike!"

        return action, msg, dmg

    def resolve_player_action(self, move_type, player_action, dmg, current_hp, player,
                               smoke_screen_active=False):
        """
        Apply enemy damage modified by player's defensive choice.

        smoke_screen_active (Rogue special): overrides player_action to
        guaranteed dodge regardless of what action was chosen.

        Returns (new_hp, result_message).
        """
        class_name = player.get('class_name', 'Knight')

        # Smoke Screen overrides all — guaranteed dodge
        if smoke_screen_active:
            return current_hp, "💨 The smoke screen works — the attack passes harmlessly through shadow!"

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
            new_hp  = current_hp - blocked
            return new_hp, f"You blocked the hit and took {blocked} damage."

        else:
            new_hp = current_hp - dmg
            return new_hp, f"You took {dmg} damage."

    # ── Prediction ─────────────────────────────────────────────────────────────

    def predict_enemy_move(self, player):
        """
        Predict the enemy's next move for the UI hint.
        Returns (move, hint_message, None).
        """
        move = np.random.choice(['attack', 'big_hit', 'flurry'], p=[0.6, 0.25, 0.15])
        messages = {
            'flurry':  "The enemy is angered and preparing a flurry of strikes!",
            'big_hit': "The enemy is preparing a massive attack!",
            'attack':  "The enemy is preparing a standard attack.",
        }
        return move, messages[move], None