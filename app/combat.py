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

New class support:
- use_special() handles 'heal_stun' effect (Paladin Healing Light):
  heals 50% max HP, stuns enemy, deals no damage
- Returns heal_amount as 7th value in tuple (0 for all other classes)
- Per-class special_cooldown override supported

Mixed damage type for players (Paladin):
- attack() handles damage_type == 'mixed':
  base_atk  = average of player attack and magic_attack
  eff_def   = average of enemy physical and magic defense (with PHYS_PEN on physical)
  type_label = "holy" — distinct from pure physical or magic
- Both attack and magic_attack stats are meaningful for Paladin:
  shop upgrades to either stat improve damage output
- Same pattern as enemy mixed damage but from the player side
"""

import numpy as np
from .models import Enemy, Character
from .enemies import ENEMIES, BOSSES, BOSS_PHASE2_LORE_DEFAULT
from .classes import CLASSES
from .config import (
    MP_COST, MP_COST_SECONDARY, MP_REGEN_ATTACK, COOLDOWN_TURNS,
    PHYS_PEN,
    PHASE2_DMG_MULT, PHASE2_HP_TRIGGER,
    PHASE1_WEIGHTS, PHASE2_WEIGHTS,
    DOT_TICK_MESSAGES, BUFF_EXPIRE_MESSAGES,
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
        Routes damage through the correct channel based on player damage_type.

        physical — player['attack'] vs enemy.defense x PHYS_PEN
        magic    — player['magic_attack'] vs enemy.magic_defense
        mixed    — average of both attack stats vs average of both defense stats
                   (Paladin). Both attack and magic_attack are meaningful —
                   shop upgrades to either stat improve Paladin damage output.
                   type_label is 'holy' to distinguish in the battle log.
        """
        crit_chance     = float(player.get('crit_chance', 0.0))
        crit_multiplier = float(player.get('crit_multiplier', 1.0))
        is_crit         = np.random.rand() < crit_chance

        damage_type = player.get('damage_type', 'physical')

        if damage_type == 'magic':
            base_atk   = player.get('magic_attack', 0)
            eff_def    = enemy.magic_defense
            type_label = "magic"

        elif damage_type == 'mixed':
            # Average of physical and magic attack stats
            phys_atk   = player.get('attack', 0)
            mag_atk    = player.get('magic_attack', 0)
            base_atk   = (phys_atk + mag_atk) / 2.0
            # Average of physical defense (with pen) and magic defense
            phys_def   = int(enemy.defense * PHYS_PEN)
            mag_def    = enemy.magic_defense
            eff_def    = (phys_def + mag_def) / 2.0
            type_label = "holy"

        else:
            # physical (default)
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
            special_multiplier  — applied to the relevant attack stat
            special_effect      — 'stun', 'smoke', 'heal_stun', or None
            special_variance    — max random int subtracted from raw damage
            special_min_dmg     — damage floor after all reductions
            special_cooldown    — per-class cooldown override (falls back to
                                  COOLDOWN_TURNS from config.py)
            damage_type         — determines which attack/defense stats to use

        Returns 7-tuple:
            msg, enemy.hp, new_mp, new_cooldown, stun_enemy, smoke_screen, heal_amount

        heal_amount is non-zero only for 'heal_stun' effect (Paladin).
        Routes must unpack all 7 values and apply heal_amount to player_hp.

        Mixed damage_type specials (Paladin) use the same averaged stat logic
        as attack() — multiplier applied to the average of both attack stats.
        """
        class_name = player.get('class_name', 'Knight')

        if current_mp < MP_COST:
            return (
                f"Not enough MP! ({current_mp}/{MP_COST} needed)",
                enemy.hp, current_mp, cooldown, False, False, 0
            )
        if cooldown > 0:
            return (
                f"Special move recharging — {cooldown} turn{'s' if cooldown != 1 else ''} remaining.",
                enemy.hp, current_mp, cooldown, False, False, 0
            )

        cls = CLASSES.get(class_name)
        if not cls:
            return (
                "No special move available for this class.",
                enemy.hp, current_mp, cooldown, False, False, 0
            )

        new_mp       = current_mp - MP_COST
        new_cooldown = cls.get('special_cooldown', COOLDOWN_TURNS)

        # ── Read special move definition from classes.py ───────────────────────
        multiplier    = cls.get('special_multiplier', 1.0)
        effect        = cls.get('special_effect', None)
        variance      = cls.get('special_variance', 0)
        min_dmg       = cls.get('special_min_dmg', 5)
        damage_type   = cls.get('damage_type', 'physical')
        special_label = cls.get('special_label', '⚡ Special')

        # ── Resolve effect flags ───────────────────────────────────────────────
        stun_enemy   = (effect in ('stun', 'heal_stun'))
        smoke_screen = (effect == 'smoke')
        heal_amount  = int(player.get('max_hp', 100) * 0.40) if effect == 'heal_stun' else 0

        # ── Resolve damage ─────────────────────────────────────────────────────
        if effect == 'heal_stun':
            # Healing Light — no damage, heal only
            dmg       = 0
            dmg_label = "sacred"

        elif damage_type == 'mixed':
            # Paladin special — averaged stats, same as attack()
            phys_atk  = player.get('attack', 0)
            mag_atk   = player.get('magic_attack', 0)
            base_atk  = (phys_atk + mag_atk) / 2.0
            phys_def  = int(enemy.defense * PHYS_PEN)
            mag_def   = enemy.magic_defense
            eff_def   = (phys_def + mag_def) / 2.0
            dmg_label = "holy"

            raw = int(round(base_atk * multiplier))
            if variance > 0:
                raw -= np.random.randint(0, variance)
            dmg = max(min_dmg, int(round(raw - eff_def)))
            enemy.hp -= dmg

        elif damage_type == 'magic':
            base_atk  = player.get('magic_attack', 0)
            eff_def   = enemy.magic_defense
            dmg_label = "magic"

            raw = int(round(base_atk * multiplier))
            if variance > 0:
                raw -= np.random.randint(0, variance)
            dmg = max(min_dmg, raw - eff_def)
            enemy.hp -= dmg

        else:
            # physical
            base_atk  = player.get('attack', 0)
            eff_def   = int(enemy.defense * PHYS_PEN)
            dmg_label = "physical"

            raw = int(round(base_atk * multiplier))
            if variance > 0:
                raw -= np.random.randint(0, variance)
            dmg = max(min_dmg, raw - eff_def)
            enemy.hp -= dmg

        # ── Build battle log message ───────────────────────────────────────────
        if effect == 'heal_stun':
            msg = (
                f"{special_label}! Sacred radiance floods your body, restoring "
                f"{heal_amount} HP. The blinding light staggers the {enemy.name} "
                f"— they cannot counter this turn!"
            )
        elif effect == 'stun':
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
        elif damage_type == 'mixed':
            msg = (
                f"{special_label}! Holy and physical force combine, "
                f"striking the {enemy.name} for {dmg} {dmg_label} damage!"
            )
        else:
            msg = (
                f"{special_label}! A devastating strike finds the "
                f"{enemy.name}'s weak point for {dmg} {dmg_label} damage!"
            )

        return msg, enemy.hp, new_mp, new_cooldown, stun_enemy, smoke_screen, heal_amount

    def use_special2(self, player, enemy, current_mp, cooldown):
        """
        Data-driven secondary special move — reads special2_* fields from classes.py.

        All secondary specials cost MP_COST_SECONDARY (35) and share the same
        cooldown as the primary special. Only one special (primary or secondary)
        can fire per cooldown cycle.

        Effect types:
            dot          — applies damage-over-time to the enemy; may also hit
            buff_attack  — raises player attack stat for N turns (via session)
            shield       — reduces incoming damage by a fraction for N turns
            stun         — deals damage and prevents enemy counter this turn
            leech        — deals damage and heals player for 50% of damage dealt

        Returns 9-tuple:
            msg, enemy.hp, new_mp, new_cooldown,
            stun_enemy,
            dot_dmg, dot_turns, dot_label,
            side_effects dict {
                buff_stat, buff_amount, buff_turns, buff_label,
                shield_pct, shield_turns, heal_amount
            }
        """
        class_name = player.get('class_name', 'Knight')

        _no_effect = {
            "buff_stat": None, "buff_amount": 0, "buff_turns": 0, "buff_label": "",
            "shield_pct": 0.0, "shield_turns": 0, "heal_amount": 0,
        }

        if current_mp < MP_COST_SECONDARY:
            return (
                f"Not enough MP! ({current_mp}/{MP_COST_SECONDARY} needed)",
                enemy.hp, current_mp, cooldown,
                False, 0, 0, "", _no_effect
            )
        if cooldown > 0:
            return (
                f"Special move recharging — {cooldown} turn{'s' if cooldown != 1 else ''} remaining.",
                enemy.hp, current_mp, cooldown,
                False, 0, 0, "", _no_effect
            )

        cls = CLASSES.get(class_name)
        if not cls:
            return (
                "No special move available for this class.",
                enemy.hp, current_mp, cooldown,
                False, 0, 0, "", _no_effect
            )

        new_mp       = current_mp - MP_COST_SECONDARY
        new_cooldown = cls.get('special_cooldown', COOLDOWN_TURNS)  # shared cooldown

        # ── Read secondary special definition ─────────────────────────────────
        effect        = cls.get('special2_effect', None)
        multiplier    = cls.get('special2_multiplier', 0)
        dot_dmg       = cls.get('special2_dot_dmg', 0)
        dot_turns     = cls.get('special2_dot_turns', 0)
        dot_label     = cls.get('special2_dot_label', '')
        buff_stat     = cls.get('special2_buff_stat', None)
        buff_amount   = cls.get('special2_buff_amount', 0)
        buff_turns    = cls.get('special2_buff_turns', 0)
        buff_label    = cls.get('special2_buff_label', '')
        shield_pct    = cls.get('special2_shield_pct', 0.0)
        shield_turns  = cls.get('special2_shield_turns', 0)
        special_label = cls.get('special2_label', '⚡ Special 2')
        damage_type   = cls.get('damage_type', 'physical')
        min_dmg       = cls.get('special_min_dmg', 5)  # reuse primary floor

        stun_enemy  = (effect == 'stun')
        heal_amount = 0

        # ── Resolve direct damage (if multiplier > 0) ─────────────────────────
        dmg = 0
        dmg_label = "physical"
        if multiplier > 0:
            if damage_type == 'magic':
                base_atk  = player.get('magic_attack', 0)
                eff_def   = enemy.magic_defense
                dmg_label = "magic"
            elif damage_type == 'mixed':
                phys_atk  = player.get('attack', 0)
                mag_atk   = player.get('magic_attack', 0)
                base_atk  = (phys_atk + mag_atk) / 2.0
                phys_def  = int(enemy.defense * PHYS_PEN)
                mag_def   = enemy.magic_defense
                eff_def   = (phys_def + mag_def) / 2.0
                dmg_label = "holy"
            else:
                base_atk  = player.get('attack', 0)
                eff_def   = int(enemy.defense * PHYS_PEN)
                dmg_label = "physical"

            raw = int(round(base_atk * multiplier))
            dmg = max(min_dmg, int(round(raw - eff_def)))
            enemy.hp -= dmg

        # ── Leech: heal 50% of damage dealt ───────────────────────────────────
        if effect == 'leech' and dmg > 0:
            heal_amount = max(1, int(dmg * 0.5))

        # ── Build battle log message ───────────────────────────────────────────
        if effect == 'dot':
            dot_name = dot_label.title()
            if dmg > 0:
                msg = (
                    f"{special_label}! You deal {dmg} {dmg_label} damage and the "
                    f"{enemy.name} begins to {dot_label}! "
                    f"({dot_dmg} damage/turn for {dot_turns} turns)"
                )
            else:
                msg = (
                    f"{special_label}! The {enemy.name} begins to {dot_label}! "
                    f"({dot_dmg} damage/turn for {dot_turns} turns)"
                )

        elif effect == 'buff_attack':
            msg = (
                f"{special_label}! Your battle cry echoes through the arena. "
                f"Attack raised by {buff_amount} for {buff_turns} turns!"
            )

        elif effect == 'shield':
            msg = (
                f"{special_label}! An arcane barrier surrounds you. "
                f"Incoming damage reduced by {int(shield_pct * 100)}% for {shield_turns} turns!"
            )

        elif effect == 'stun':
            msg = (
                f"{special_label}! You strike the {enemy.name} for {dmg} {dmg_label} damage "
                f"with sacred force — they are stunned and cannot counter!"
            )

        elif effect == 'leech':
            msg = (
                f"{special_label}! Life drains from the {enemy.name} — "
                f"{dmg} {dmg_label} damage dealt, {heal_amount} HP restored!"
            )

        else:
            msg = f"{special_label}! {dmg} damage dealt." if dmg > 0 else f"{special_label}!"

        side_effects = {
            "buff_stat":    buff_stat    if effect == 'buff_attack' else None,
            "buff_amount":  buff_amount  if effect == 'buff_attack' else 0,
            "buff_turns":   buff_turns   if effect == 'buff_attack' else 0,
            "buff_label":   buff_label   if effect == 'buff_attack' else "",
            "shield_pct":   shield_pct   if effect == 'shield' else 0.0,
            "shield_turns": shield_turns if effect == 'shield' else 0,
            "heal_amount":  heal_amount,
        }

        return (
            msg, enemy.hp, new_mp, new_cooldown,
            stun_enemy,
            dot_dmg if effect == 'dot' else 0,
            dot_turns if effect == 'dot' else 0,
            dot_label if effect == 'dot' else "",
            side_effects,
        )

    def apply_active_effects(self, enemy, player_hp, char_max_hp,
                              dot_dmg, dot_turns, dot_label,
                              buff_stat, buff_amount, buff_turns, buff_label,
                              shield_pct, shield_turns):
        """
        Called at the start of each POST turn before the player action.

        Ticks damage-over-time on the enemy, decrements buff and shield
        durations, and returns updated values plus a log prefix message.

        Returns:
            effects_msg  — str to prepend to the turn's battle log (may be "")
            enemy.hp     — updated after DoT tick
            dot_dmg      — unchanged (tick amount stays the same)
            dot_turns    — decremented; 0 when expired
            buff_stat    — unchanged
            buff_amount  — unchanged
            buff_turns   — decremented; 0 when expired
            buff_label   — unchanged
            shield_pct   — unchanged
            shield_turns — decremented; 0 when expired
        """
        parts = []

        # ── Tick DoT ──────────────────────────────────────────────────────────
        if dot_turns > 0 and dot_dmg > 0:
            enemy.hp -= dot_dmg
            tick_template = DOT_TICK_MESSAGES.get(dot_label, f"{dot_label} deals {{dmg}} damage!")
            parts.append(tick_template.format(dmg=dot_dmg))
            dot_turns -= 1

        # ── Decrement buff ────────────────────────────────────────────────────
        if buff_turns > 0:
            buff_turns -= 1
            if buff_turns == 0 and buff_label:
                expire_msg = BUFF_EXPIRE_MESSAGES.get(buff_label, "")
                if expire_msg:
                    parts.append(expire_msg)

        # ── Decrement shield ──────────────────────────────────────────────────
        if shield_turns > 0:
            shield_turns -= 1
            if shield_turns == 0 and buff_label == "nullfield":
                expire_msg = BUFF_EXPIRE_MESSAGES.get("nullfield", "")
                if expire_msg:
                    parts.append(expire_msg)

        effects_msg = " ".join(parts)

        return (
            effects_msg,
            enemy.hp,
            dot_dmg, dot_turns, dot_label,
            buff_stat, buff_amount, buff_turns, buff_label,
            shield_pct, shield_turns,
        )

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
                               smoke_screen_active=False, shield_pct=0.0):
        """
        Reads dodge_chance and block_multiplier from the live player session dict
        so any shop upgrades (e.g. Dodge Pendant) take effect immediately.
        Falls back to classes.py values if not present in session.

        shield_pct — if > 0 (Mage Nullfield active), reduces incoming damage
        by this fraction before dodge/block calculations. Applied multiplicatively.
        """
        class_name = player.get('class_name', 'Knight')

        # ── Apply active shield before any other reduction ────────────────────
        if shield_pct > 0.0:
            dmg = max(1, int(round(dmg * (1.0 - shield_pct))))

        if smoke_screen_active:
            return current_hp, "💨 The smoke screen works — the attack passes harmlessly through shadow!"

        if player_action == 'dodge':
            success_chance = player.get(
                'dodge_chance', Character.get_dodge(class_name)
            )
            if np.random.rand() < success_chance:
                return current_hp, "You dodged the attack completely!"
            else:
                new_hp = current_hp - dmg
                return new_hp, f"You failed to dodge and took {dmg} damage."

        elif player_action == 'block':
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