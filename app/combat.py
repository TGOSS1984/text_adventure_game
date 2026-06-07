"""
combat.py

Manages all battle-related logic.

Commit 7 additions:
- use_special(): resolves the class special move
- enemy_attack() respects the 'stunned' flag (skips counter if stunned)
- resolve_player_action() respects 'smoke_screen_active' flag (guaranteed dodge)

Commit 10 fix:
- generate_enemy() passes soul_reward= to Enemy() constructor

Commit 11 additions:
- enemy_attack() accepts boss_phase param; phase 2 uses heavier move weights
  and applies a 1.20x damage multiplier across all move types
- predict_enemy_move() also accepts boss_phase so the hint reflects real weights

Commit 21 additions:
- PHYS_PEN constant: physical attacks apply only 55% of enemy physical defense
- Player attack() routes through magic_attack vs enemy magic_defense for Mage
- use_special() uses the class damage type
- enemy_attack() uses enemy damage_type to select correct player defense stat

Refactor (constants):
- All constants moved to config.py, imported from there
- BOSS_PHASE2_LORE removed, phase2_lore lives in enemies.py boss dicts

Refactor (data-driven specials):
- use_special() no longer has per-class if/elif blocks
- All special move behaviour (multiplier, effect, variance, min_dmg) defined
  in classes.py and read here — adding a new class needs zero changes to combat.py
- resolve_player_action() reads dodge_chance and block_multiplier from the live
  player session dict so shop upgrades (e.g. Dodge Pendant) take effect in combat
"""

import numpy as np
from .models import Enemy, Character
from .enemies import ENEMIES, BOSSES, BOSS_PHASE2_LORE_DEFAULT
from .classes import CLASSES
from .config import (
    MP_COST, MP_REGEN_ATTACK, COOLDOWN_TURNS,
    PHYS_PEN,
    PHASE2_DMG_MULT, PHASE2_HP_TRIGGER,
    PHASE1_WEIGHTS, PHASE2_WEIGHTS,
)


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
                magic_attack=data.get('magic_attack', 0),
                defense=data.get('defense', 0),
                magic_defense=data.get('magic_defense', 0),
                damage_type=data.get('damage_type', 'physical'),
                image=data['image'],
                lore=data['lore'],
                is_boss=True,
                soul_reward=data.get('soul_reward', 0),
            )
        else:
            e = np.random.choice(ENEMIES)
            return Enemy(
                name=e['name'],
                hp=e['hp'],
                attack=e['attack'],
                magic_attack=e.get('magic_attack', 0),
                defense=e.get('defense', 0),
                magic_defense=e.get('magic_defense', 0),
                damage_type=e.get('damage_type', 'physical'),
                image=e['image'],
                lore=e['lore'],
                soul_reward=e.get('soul_reward', 0),
            )

    # ── Player actions ─────────────────────────────────────────────────────────

    def attack(self, player, enemy):
        """
        Routes damage through physical or magic channel depending on the
        player's damage_type.

        Physical classes use player['attack'] vs enemy.defense x PHYS_PEN.
        Mage uses player['magic_attack'] vs enemy.magic_defense (no pen).
        """
        crit_chance     = float(player.get('crit_chance', 0.0))
        crit_multiplier = float(player.get('crit_multiplier', 1.0))
        is_crit         = np.random.rand() < crit_chance

        damage_type = player.get('damage_type', 'physical')

        if damage_type == 'magic':
            base_atk   = player.get('magic_attack', 0)
            eff_def    = enemy.magic_defense
            type_label = "magic"
        else:
            base_atk   = player['attack']
            eff_def    = int(enemy.defense * PHYS_PEN)
            type_label = "physical"

        raw = base_atk * crit_multiplier if is_crit else base_atk
        dmg = raw - np.random.randint(0, 6) - eff_def
        dmg = max(5, int(round(dmg)))
        enemy.hp -= dmg

        if is_crit:
            msg = f"💥 Critical hit! You strike the {enemy.name} for {dmg} {type_label} damage!"
        else:
            msg = f"You strike the {enemy.name} for {dmg} {type_label} damage!"

        return msg, enemy.hp

    def use_estus(self, current_hp, max_hp, estus_count):
        if estus_count <= 0:
            return current_hp, 0, "No Estus Flasks left!"
        healed    = int(max_hp * 0.7)
        new_hp    = min(current_hp + healed, max_hp)
        new_estus = estus_count - 1
        msg       = f"You drink from the Estus Flask and recover {healed} HP."
        return new_hp, new_estus, msg

    def use_special(self, player, enemy, current_mp, cooldown):
        """
        Data-driven special moves — all behaviour defined in classes.py.

        Reads from CLASSES[class_name]:
            special_multiplier — applied to the relevant attack stat
            special_effect     — 'stun', 'smoke', or None
            special_variance   — max random int subtracted from raw damage
            special_min_dmg    — damage floor after all reductions
            damage_type        — determines which attack/defense stats to use

        Adding a new class with a special move: define these fields in
        classes.py. Zero changes needed here.
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

        cls = CLASSES.get(class_name)
        if not cls:
            return (
                "No special move available for this class.",
                enemy.hp, current_mp, cooldown, False, False
            )

        new_mp       = current_mp - MP_COST
        new_cooldown = COOLDOWN_TURNS

        # ── Read special move definition from classes.py ───────────────────────
        multiplier  = cls.get('special_multiplier', 1.0)
        effect      = cls.get('special_effect', None)      # 'stun', 'smoke', None
        variance    = cls.get('special_variance', 0)       # random damage reduction
        min_dmg     = cls.get('special_min_dmg', 5)
        damage_type = cls.get('damage_type', 'physical')
        special_name = cls.get('special_name', 'Special')

        # ── Resolve damage ─────────────────────────────────────────────────────
        if damage_type == 'magic':
            base_atk = player.get('magic_attack', 0)
            eff_def  = enemy.magic_defense
            dmg_label = "magic"
        else:
            base_atk = player.get('attack', 0)
            eff_def  = int(enemy.defense * PHYS_PEN)
            dmg_label = "physical"

        raw = int(round(base_atk * multiplier))
        if variance > 0:
            raw -= np.random.randint(0, variance)
        dmg = max(min_dmg, raw - eff_def)
        enemy.hp -= dmg

        # ── Resolve effect flags ───────────────────────────────────────────────
        stun_enemy   = (effect == 'stun')
        smoke_screen = (effect == 'smoke')

        # ── Build battle log message ───────────────────────────────────────────
        special_label = cls.get('special_label', '⚡ Special')

        if effect == 'stun':
            msg = (
                f"{special_label}! You crash your shield into the {enemy.name} "
                f"for {dmg} {dmg_label} damage and stun them "
                f"— they cannot counter this turn!"
            )
        elif effect == 'smoke':
            msg = (
                f"{special_label}! You hurl a blade from the shadows, "
                f"dealing {dmg} {dmg_label} damage, then vanish "
                f"— the enemy's next attack will find nothing but smoke."
            )
        elif damage_type == 'magic':
            msg = (
                f"{special_label}! A torrent of magic tears through the "
                f"{enemy.name} for {dmg} {dmg_label} damage "
                f"— armour is useless against pure arcane force!"
            )
        else:
            msg = (
                f"{special_label}! A devastating strike finds the "
                f"{enemy.name}'s weak point for {dmg} {dmg_label} damage!"
            )

        return msg, enemy.hp, new_mp, new_cooldown, stun_enemy, smoke_screen

    # ── Enemy actions ──────────────────────────────────────────────────────────

    def enemy_attack(self, player, enemy, action=None, boss_phase=1):
        """
        Selects the correct player defense stat based on the enemy's damage_type.

        physical -> player['defense'] x PHYS_PEN
        magic    -> player['magic_defense']
        mixed    -> attack/flurry use physical; big_hit uses magic
        """
        weights = PHASE2_WEIGHTS if boss_phase == 2 else PHASE1_WEIGHTS

        if action not in ('attack', 'big_hit', 'flurry'):
            action = np.random.choice(
                ['attack', 'big_hit', 'flurry'], p=weights
            )

        damage_type = getattr(enemy, 'damage_type', 'physical')

        if damage_type == 'magic':
            atk_stat  = getattr(enemy, 'magic_attack', enemy.attack)
            eff_def   = player.get('magic_defense', 0)
            dmg_label = "magic"
        elif damage_type == 'mixed':
            if action in ('attack', 'flurry'):
                atk_stat  = enemy.attack
                eff_def   = int(player.get('defense', 0) * PHYS_PEN)
                dmg_label = "physical"
            else:
                atk_stat  = getattr(enemy, 'magic_attack', enemy.attack)
                eff_def   = player.get('magic_defense', 0)
                dmg_label = "magic"
        else:
            atk_stat  = enemy.attack
            eff_def   = int(player.get('defense', 0) * PHYS_PEN)
            dmg_label = "physical"

        if action == 'flurry':
            hits       = np.random.randint(3, 6)
            single_hit = max(2, atk_stat // 3) + np.random.randint(6, 10)
            dmg        = hits * single_hit - int(eff_def * 1.0)
            dmg        = max(15, dmg)
            msg        = f"The enemy unleashes a flurry of {hits} {dmg_label} strikes!"

        elif action == 'big_hit':
            dmg = atk_stat + np.random.randint(10, 20) - int(eff_def * 0.8)
            dmg = max(8, dmg)
            msg = f"A massive {dmg_label} attack is incoming!"

        else:  # attack
            dmg = atk_stat + np.random.randint(0, 10) - int(eff_def * 1.1)
            dmg = max(5, dmg)
            msg = f"A swift {dmg_label} strike!"

        if boss_phase == 2:
            dmg = max(1, int(round(dmg * PHASE2_DMG_MULT)))

        return action, msg, dmg

    def resolve_player_action(self, move_type, player_action, dmg, current_hp, player,
                               smoke_screen_active=False):
        """
        Reads dodge_chance and block_multiplier from the live player session dict
        so any shop upgrades (e.g. Dodge Pendant) take effect immediately.
        Falls back to classes.py values if not present in session.
        """
        class_name = player.get('class_name', 'Knight')

        if smoke_screen_active:
            return current_hp, "💨 The smoke screen works — the attack passes harmlessly through shadow!"

        if player_action == 'dodge':
            # Read from session first — picks up any shop-purchased upgrades
            success_chance = player.get(
                'dodge_chance', Character.get_dodge(class_name)
            )
            if np.random.rand() < success_chance:
                return current_hp, "You dodged the attack completely!"
            else:
                new_hp = current_hp - dmg
                return new_hp, f"You failed to dodge and took {dmg} damage."

        elif player_action == 'block':
            # Read from session first — picks up any shop-purchased upgrades
            reduction_ratio = player.get(
                'block_multiplier', Character.get_block_mult(class_name)
            )
            blocked = int(dmg * reduction_ratio)
            new_hp  = current_hp - blocked
            return new_hp, f"You blocked the hit and took {blocked} damage."

        else:
            new_hp = current_hp - dmg
            return new_hp, f"You took {dmg} damage."

    # ── Prediction ─────────────────────────────────────────────────────────────

    def predict_enemy_move(self, player, boss_phase=1):
        """
        Predict the enemy's next move for the UI hint.
        Uses the correct weight set for the current phase.
        """
        weights = PHASE2_WEIGHTS if boss_phase == 2 else PHASE1_WEIGHTS
        move = np.random.choice(['attack', 'big_hit', 'flurry'], p=weights)
        messages = {
            'flurry':  "The enemy is angered and preparing a flurry of strikes!",
            'big_hit': "The enemy is preparing a massive attack!",
            'attack':  "The enemy is preparing a standard attack.",
        }
        return move, messages[move], None

    # ── Phase transition helper ────────────────────────────────────────────────

    def get_phase2_lore(self, boss_name):
        """Return the phase 2 transition lore message for this boss.
        Reads from the boss dict in enemies.py — no local dict needed.
        """
        boss = BOSSES.get(boss_name)
        if boss:
            return boss.get('phase2_lore', BOSS_PHASE2_LORE_DEFAULT)
        return BOSS_PHASE2_LORE_DEFAULT