"""
combat.py

Manages all battle-related logic.

Commit 8 — New class special effect handlers:

use_special() — new primary effects:
    combo_buff_hot (Barbarian Berserker Rage):
        No direct damage. Sets attack buff AND heal-over-time in the same action.
        Returns an 8th value: primary_side_fx dict containing buff and HoT fields.
        battle_routes.py reads primary_side_fx and writes the new session keys.
        use_special() now always returns an 8-tuple — existing callers that
        unpacked 7 values must be updated to unpack 8 (see battle_routes.py).

    double_hit (Samurai Iaijutsu):
        Calls attack() twice. Each hit uses the same stat/defense routing.
        Returns combined damage message. No new session state.

    random_hit (Wretch Desperate Strike):
        Damage is random.randint(5, 60), completely ignoring player stats.
        The unpredictability is the mechanic. No new session state.

use_special2() — new secondary effects:
    parry (Samurai Iron Stance):
        Sets shield_pct/shield_turns (existing mechanism for damage reduction)
        AND returns parry_counter_pct/parry_turns in side_effects.
        battle_routes.py Step 4 fires the auto-counter when damage lands
        while parry_turns > 0.

    gamble_heal (Wretch Fortune's Favour):
        50/50 roll. Win: heal 50% max HP. Lose: heal 8% max HP + attack buff.
        heal_amount returned in side_effects; conditional buff in buff_* fields.

apply_active_effects() — new parameters:
    hot_dmg, hot_turns  — heal-over-time (player heals each turn)
    parry_turns         — parry duration counter (decrements, expire message)
    parry_counter_pct   — stored for battle_routes Step 4 (not ticked here)
    player_hp, char_max_hp — needed for HoT heal cap
    Returns extended tuple with all new values.

Return signature changes:
    use_special()        : 7-tuple → 8-tuple (adds primary_side_fx dict)
    apply_active_effects(): extended params and return tuple
    use_special2()       : side_effects dict gains parry_counter_pct, parry_turns
"""

import random as _random
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
    HOT_TICK_MESSAGE, PARRY_COUNTER_MSG,
    NG_PLUS_HP_SCALE, NG_PLUS_ATK_SCALE,
    NG_PLUS_DEF_SCALE, NG_PLUS_SOUL_SCALE,
)


def _apply_ng_scaling(base_value, scale, ng_level):
    if ng_level <= 0 or base_value <= 0:
        return base_value
    return int(round(base_value * (1 + scale * ng_level)))


def _scale_soul_reward(base_value, ng_level):
    if ng_level <= 0 or base_value <= 0:
        return base_value
    scaled = base_value * (1 + NG_PLUS_SOUL_SCALE * ng_level)
    return round(scaled / 5) * 5


# ── Empty primary side-effects dict (returned when no primary side-fx apply) ──
_EMPTY_PRIMARY_SFX = {
    "buff_stat":   None, "buff_amount": 0, "buff_turns": 0, "buff_label": "",
    "hot_dmg":     0,    "hot_turns":   0,
}


class BattleManager:

    # ── Enemy generation ───────────────────────────────────────────────────────

    def generate_enemy(self, boss=False, boss_name=None, ng_level=0):
        if boss:
            name = boss_name or 'Cindergloom'
            data = BOSSES.get(name)
            if not data:
                print(f"[WARN] Boss '{name}' not found. Defaulting to Cindergloom.")
                name = 'Cindergloom'
                data = BOSSES[name]
            return Enemy(
                name=name,
                hp=_apply_ng_scaling(data['hp'], NG_PLUS_HP_SCALE, ng_level),
                attack=_apply_ng_scaling(data['attack'], NG_PLUS_ATK_SCALE, ng_level),
                magic_attack=_apply_ng_scaling(data.get('magic_attack', 0), NG_PLUS_ATK_SCALE, ng_level),
                defense=_apply_ng_scaling(data.get('defense', 0), NG_PLUS_DEF_SCALE, ng_level),
                magic_defense=_apply_ng_scaling(data.get('magic_defense', 0), NG_PLUS_DEF_SCALE, ng_level),
                damage_type=data.get('damage_type', 'physical'),
                image=data['image'],
                lore=data['lore'],
                is_boss=True,
                soul_reward=_scale_soul_reward(data.get('soul_reward', 0), ng_level),
            )
        else:
            e = np.random.choice(ENEMIES)
            return Enemy(
                name=e['name'],
                hp=_apply_ng_scaling(e['hp'], NG_PLUS_HP_SCALE, ng_level),
                attack=_apply_ng_scaling(e['attack'], NG_PLUS_ATK_SCALE, ng_level),
                magic_attack=_apply_ng_scaling(e.get('magic_attack', 0), NG_PLUS_ATK_SCALE, ng_level),
                defense=_apply_ng_scaling(e.get('defense', 0), NG_PLUS_DEF_SCALE, ng_level),
                magic_defense=_apply_ng_scaling(e.get('magic_defense', 0), NG_PLUS_DEF_SCALE, ng_level),
                damage_type=e.get('damage_type', 'physical'),
                image=e['image'],
                lore=e['lore'],
                soul_reward=_scale_soul_reward(e.get('soul_reward', 0), ng_level),
            )

    # ── Player actions ─────────────────────────────────────────────────────────

    def attack(self, player, enemy):
        """Standard attack — routes through physical/magic/mixed."""
        crit_chance     = float(player.get('crit_chance', 0.0))
        crit_multiplier = float(player.get('crit_multiplier', 1.0))
        is_crit         = np.random.rand() < crit_chance
        damage_type     = player.get('damage_type', 'physical')

        if damage_type == 'magic':
            base_atk   = player.get('magic_attack', 0)
            eff_def    = enemy.magic_defense
            type_label = "magic"
        elif damage_type == 'mixed':
            base_atk   = (player.get('attack', 0) + player.get('magic_attack', 0)) / 2.0
            eff_def    = (int(enemy.defense * PHYS_PEN) + enemy.magic_defense) / 2.0
            type_label = "holy"
        else:
            base_atk   = player['attack']
            eff_def    = int(enemy.defense * PHYS_PEN)
            type_label = "physical"

        raw = base_atk * crit_multiplier if is_crit else base_atk
        dmg = max(5, int(round(raw - np.random.randint(0, 6) - eff_def)))
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
        return new_hp, new_estus, f"You drink from the Estus Flask and recover {healed} HP."

    def use_special(self, player, enemy, current_mp, cooldown):
        """
        Primary special move handler.

        Returns 8-tuple:
            msg, enemy.hp, new_mp, new_cooldown,
            stun_enemy, smoke_screen,
            heal_amount,
            primary_side_fx   ← NEW in Commit 8

        primary_side_fx is a dict used by combo_buff_hot (Barbarian):
            { buff_stat, buff_amount, buff_turns, buff_label, hot_dmg, hot_turns }
        All other effects return _EMPTY_PRIMARY_SFX.
        battle_routes.py must unpack all 8 values.
        """
        class_name = player.get('class_name', 'Knight')
        _fail = lambda msg: (msg, enemy.hp, current_mp, cooldown, False, False, 0, _EMPTY_PRIMARY_SFX)

        if current_mp < MP_COST:
            return _fail(f"Not enough MP! ({current_mp}/{MP_COST} needed)")
        if cooldown > 0:
            return _fail(f"Special move recharging — {cooldown} turn{'s' if cooldown != 1 else ''} remaining.")

        cls = CLASSES.get(class_name)
        if not cls:
            return _fail("No special move available for this class.")

        new_mp       = current_mp - MP_COST
        new_cooldown = cls.get('special_cooldown', COOLDOWN_TURNS)
        multiplier   = cls.get('special_multiplier', 1.0)
        effect       = cls.get('special_effect', None)
        variance     = cls.get('special_variance', 0)
        min_dmg      = cls.get('special_min_dmg', 5)
        damage_type  = cls.get('damage_type', 'physical')
        label        = cls.get('special_label', '⚡ Special')

        stun_enemy   = effect in ('stun', 'heal_stun')
        smoke_screen = (effect == 'smoke')
        heal_amount  = int(player.get('max_hp', 100) * 0.40) if effect == 'heal_stun' else 0
        primary_sfx  = dict(_EMPTY_PRIMARY_SFX)  # mutable copy

        dmg       = 0
        dmg_label = "physical"

        # ── New Commit 8 effects ───────────────────────────────────────────────

        if effect == 'combo_buff_hot':
            # Barbarian Berserker Rage — no damage, buff + HoT
            primary_sfx = {
                "buff_stat":   cls.get('special_buff_stat', 'attack'),
                "buff_amount": cls.get('special_buff_amount', 0),
                "buff_turns":  cls.get('special_buff_turns', 0),
                "buff_label":  cls.get('special_buff_label', ''),
                "hot_dmg":     cls.get('special_hot_dmg', 0),
                "hot_turns":   cls.get('special_hot_turns', 0),
            }
            msg = (
                f"{label}! Rage floods through your veins. "
                f"Attack +{primary_sfx['buff_amount']} for {primary_sfx['buff_turns']} turns, "
                f"regenerating {primary_sfx['hot_dmg']} HP per turn!"
            )
            return msg, enemy.hp, new_mp, new_cooldown, False, False, 0, primary_sfx

        elif effect == 'double_hit':
            # Samurai Iaijutsu — two separate physical hits
            dmg_label = "physical"
            eff_def   = int(enemy.defense * PHYS_PEN)
            base_atk  = player.get('attack', 0)

            raw1 = int(round(base_atk * multiplier))
            if variance > 0:
                raw1 -= np.random.randint(0, variance)
            dmg1 = max(min_dmg, raw1 - eff_def)
            enemy.hp -= dmg1

            raw2 = int(round(base_atk * multiplier))
            if variance > 0:
                raw2 -= np.random.randint(0, variance)
            dmg2 = max(min_dmg, raw2 - eff_def)
            enemy.hp -= dmg2

            total = dmg1 + dmg2
            msg = (
                f"{label}! Two lightning strikes — {dmg1} and {dmg2} {dmg_label} damage "
                f"({total} total)!"
            )
            return msg, enemy.hp, new_mp, new_cooldown, False, False, 0, primary_sfx

        elif effect == 'random_hit':
            # Wretch Desperate Strike — pure chaos, no stat scaling
            dmg = _random.randint(5, 60)
            enemy.hp -= dmg
            if dmg >= 45:
                msg = f"{label}! A wild, desperate swing connects for {dmg} damage — somehow devastating!"
            elif dmg <= 12:
                msg = f"{label}! A flailing blow grazes the {enemy.name} for {dmg} damage. Barely a scratch."
            else:
                msg = f"{label}! A chaotic strike hits the {enemy.name} for {dmg} damage!"
            return msg, enemy.hp, new_mp, new_cooldown, False, False, 0, primary_sfx

        # ── Existing effects ───────────────────────────────────────────────────

        elif effect == 'heal_stun':
            msg = (
                f"{label}! Sacred radiance floods your body, restoring {heal_amount} HP. "
                f"The blinding light staggers the {enemy.name} — they cannot counter this turn!"
            )

        else:
            # Standard damage specials (stun, smoke, magic, mixed, physical)
            if damage_type == 'mixed':
                base_atk  = (player.get('attack', 0) + player.get('magic_attack', 0)) / 2.0
                eff_def   = (int(enemy.defense * PHYS_PEN) + enemy.magic_defense) / 2.0
                dmg_label = "holy"
            elif damage_type == 'magic':
                base_atk  = player.get('magic_attack', 0)
                eff_def   = enemy.magic_defense
                dmg_label = "magic"
            else:
                base_atk  = player.get('attack', 0)
                eff_def   = int(enemy.defense * PHYS_PEN)
                dmg_label = "physical"

            raw = int(round(base_atk * multiplier))
            if variance > 0:
                raw -= np.random.randint(0, variance)
            dmg = max(min_dmg, int(round(raw - eff_def)))
            enemy.hp -= dmg

            if effect == 'stun':
                msg = (
                    f"{label}! You crash into the {enemy.name} for {dmg} {dmg_label} damage "
                    f"and stun them — they cannot counter this turn!"
                )
            elif effect == 'smoke':
                msg = (
                    f"{label}! You strike for {dmg} {dmg_label} damage then vanish "
                    f"— the enemy's next attack will find nothing but smoke."
                )
            elif damage_type == 'magic':
                msg = (
                    f"{label}! A torrent of magic tears through the {enemy.name} "
                    f"for {dmg} {dmg_label} damage — armour is useless!"
                )
            elif damage_type == 'mixed':
                msg = (
                    f"{label}! Holy and physical force combine, "
                    f"striking the {enemy.name} for {dmg} {dmg_label} damage!"
                )
            else:
                msg = (
                    f"{label}! A devastating strike finds the {enemy.name}'s "
                    f"weak point for {dmg} {dmg_label} damage!"
                )

        return msg, enemy.hp, new_mp, new_cooldown, stun_enemy, smoke_screen, heal_amount, primary_sfx

    def use_special2(self, player, enemy, current_mp, cooldown):
        """
        Secondary special move handler.

        side_effects dict gains two new keys in Commit 8:
            parry_counter_pct — auto-counter damage fraction (parry effect only)
            parry_turns       — parry duration (parry effect only; mirrors shield_turns)

        gamble_heal outcome is determined here and returned via heal_amount
        and conditional buff fields in side_effects.
        """
        class_name = player.get('class_name', 'Knight')

        _no_effect = {
            "buff_stat": None, "buff_amount": 0, "buff_turns": 0, "buff_label": "",
            "shield_pct": 0.0, "shield_turns": 0, "heal_amount": 0,
            "parry_counter_pct": 0.0, "parry_turns": 0,
        }

        _fail = lambda msg: (msg, enemy.hp, current_mp, cooldown, False, 0, 0, "", _no_effect)

        if current_mp < MP_COST_SECONDARY:
            return _fail(f"Not enough MP! ({current_mp}/{MP_COST_SECONDARY} needed)")
        if cooldown > 0:
            return _fail(f"Special move recharging — {cooldown} turn{'s' if cooldown != 1 else ''} remaining.")

        cls = CLASSES.get(class_name)
        if not cls:
            return _fail("No special move available for this class.")

        new_mp       = current_mp - MP_COST_SECONDARY
        new_cooldown = cls.get('special_cooldown', COOLDOWN_TURNS)
        effect       = cls.get('special2_effect', None)
        multiplier   = cls.get('special2_multiplier', 0)
        dot_dmg      = cls.get('special2_dot_dmg', 0)
        dot_turns    = cls.get('special2_dot_turns', 0)
        dot_label    = cls.get('special2_dot_label', '')
        buff_stat    = cls.get('special2_buff_stat', None)
        buff_amount  = cls.get('special2_buff_amount', 0)
        buff_turns   = cls.get('special2_buff_turns', 0)
        buff_label   = cls.get('special2_buff_label', '')
        shield_pct   = cls.get('special2_shield_pct', 0.0)
        shield_turns = cls.get('special2_shield_turns', 0)
        label        = cls.get('special2_label', '⚡ Special 2')
        damage_type  = cls.get('damage_type', 'physical')
        min_dmg      = cls.get('special_min_dmg', 5)

        stun_enemy  = (effect == 'stun')
        heal_amount = 0
        dmg = 0
        dmg_label = "physical"

        # Direct damage if multiplier > 0
        if multiplier > 0:
            if damage_type == 'magic':
                base_atk  = player.get('magic_attack', 0)
                eff_def   = enemy.magic_defense
                dmg_label = "magic"
            elif damage_type == 'mixed':
                base_atk  = (player.get('attack', 0) + player.get('magic_attack', 0)) / 2.0
                eff_def   = (int(enemy.defense * PHYS_PEN) + enemy.magic_defense) / 2.0
                dmg_label = "holy"
            else:
                base_atk  = player.get('attack', 0)
                eff_def   = int(enemy.defense * PHYS_PEN)
                dmg_label = "physical"

            raw = int(round(base_atk * multiplier))
            dmg = max(min_dmg, int(round(raw - eff_def)))
            enemy.hp -= dmg

        if effect == 'leech' and dmg > 0:
            min_heal    = cls.get('special2_leech_min_heal', 0)
            heal_amount = max(min_heal, int(dmg * 1.5))

        # ── New Commit 8 effects ───────────────────────────────────────────────

        if effect == 'parry':
            # Samurai Iron Stance — shield + auto-counter tracking
            parry_counter_pct = cls.get('special2_parry_counter_pct', 0.0)
            msg = (
                f"{label}! You settle into Iron Stance. "
                f"Incoming damage halved for {shield_turns} turns — "
                f"and you will counter each blow for "
                f"{int(parry_counter_pct * 100)}% attack!"
            )
            side_effects = {
                "buff_stat":         None,
                "buff_amount":       0,
                "buff_turns":        0,
                "buff_label":        buff_label,   # 'iron_stance' for expire msg
                "shield_pct":        shield_pct,
                "shield_turns":      shield_turns,
                "heal_amount":       0,
                "parry_counter_pct": parry_counter_pct,
                "parry_turns":       shield_turns,  # same duration as shield
            }
            return (
                msg, enemy.hp, new_mp, new_cooldown,
                False, 0, 0, "",
                side_effects,
            )

        elif effect == 'gamble_heal':
            # Wretch Fortune's Favour — 50/50 heal
            max_hp = player.get('max_hp', 100)
            win    = _random.random() < 0.5

            if win:
                heal_amount  = int(max_hp * 0.50)
                gamble_buff_stat   = None
                gamble_buff_amount = 0
                gamble_buff_turns  = 0
                gamble_buff_label  = ""
                msg = (
                    f"{label}! The coin lands in your favour! "
                    f"Fortune surges through your wounds — {heal_amount} HP restored!"
                )
            else:
                heal_amount  = int(max_hp * 0.08)
                gamble_buff_stat   = cls.get('special2_buff_stat', 'attack')
                gamble_buff_amount = cls.get('special2_buff_amount', 3)
                gamble_buff_turns  = cls.get('special2_buff_turns', 2)
                gamble_buff_label  = cls.get('special2_buff_label', 'wretch_fury')
                msg = (
                    f"{label}! The coin betrays you — only {heal_amount} HP restored. "
                    f"But fury takes the pain's place. Attack +{gamble_buff_amount} "
                    f"for {gamble_buff_turns} turns!"
                )

            side_effects = {
                "buff_stat":         gamble_buff_stat,
                "buff_amount":       gamble_buff_amount,
                "buff_turns":        gamble_buff_turns,
                "buff_label":        gamble_buff_label,
                "shield_pct":        0.0,
                "shield_turns":      0,
                "heal_amount":       heal_amount,
                "parry_counter_pct": 0.0,
                "parry_turns":       0,
            }
            return (
                msg, enemy.hp, new_mp, new_cooldown,
                False, 0, 0, "",
                side_effects,
            )

        # ── Existing effects ───────────────────────────────────────────────────

        if effect == 'dot':
            msg = (
                f"{label}! You deal {dmg} {dmg_label} damage and "
                f"the {enemy.name} begins to {dot_label}! "
                f"({dot_dmg} damage/turn for {dot_turns} turns)"
            ) if dmg > 0 else (
                f"{label}! The {enemy.name} begins to {dot_label}! "
                f"({dot_dmg} damage/turn for {dot_turns} turns)"
            )
        elif effect == 'buff_attack':
            msg = (
                f"{label}! Your battle cry echoes through the arena. "
                f"Attack raised by {buff_amount} for {buff_turns} turns!"
            )
        elif effect == 'shield':
            msg = (
                f"{label}! An arcane barrier surrounds you. "
                f"Incoming damage reduced by {int(shield_pct * 100)}% "
                f"for {shield_turns} turns!"
            )
        elif effect == 'stun':
            msg = (
                f"{label}! You strike the {enemy.name} for {dmg} {dmg_label} damage "
                f"with sacred force — they are stunned and cannot counter!"
            )
        elif effect == 'leech':
            msg = (
                f"{label}! Life drains from the {enemy.name} — "
                f"{dmg} {dmg_label} damage dealt, {heal_amount} HP restored!"
            )
        else:
            msg = f"{label}! {dmg} damage dealt." if dmg > 0 else f"{label}!"

        side_effects = {
            "buff_stat":         buff_stat    if effect == 'buff_attack' else None,
            "buff_amount":       buff_amount  if effect == 'buff_attack' else 0,
            "buff_turns":        buff_turns   if effect == 'buff_attack' else 0,
            "buff_label":        buff_label   if effect == 'buff_attack' else "",
            "shield_pct":        shield_pct   if effect == 'shield' else 0.0,
            "shield_turns":      shield_turns if effect == 'shield' else 0,
            "heal_amount":       heal_amount,
            "parry_counter_pct": 0.0,
            "parry_turns":       0,
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
                              shield_pct, shield_turns,
                              hot_dmg=0, hot_turns=0,
                              parry_turns=0, parry_counter_pct=0.0):
        """
        Called at the start of each POST turn before the player action.

        Commit 8 additions:
            hot_dmg, hot_turns      — Barbarian HoT heals player each turn
            parry_turns             — Samurai parry duration counter
            parry_counter_pct       — passed through unchanged (used in battle_routes)

        Returns extended 15-tuple:
            effects_msg,
            enemy.hp, player_hp,
            dot_dmg, dot_turns, dot_label,
            buff_stat, buff_amount, buff_turns, buff_label,
            shield_pct, shield_turns,
            hot_dmg, hot_turns,
            parry_turns
        """
        parts = []

        # ── Tick DoT ──────────────────────────────────────────────────────────
        if dot_turns > 0 and dot_dmg > 0:
            enemy.hp -= dot_dmg
            tick_template = DOT_TICK_MESSAGES.get(dot_label, f"{dot_label} deals {{dmg}} damage!")
            parts.append(tick_template.format(dmg=dot_dmg))
            dot_turns -= 1

        # ── Tick HoT (heal-over-time) ──────────────────────────────────────────
        if hot_turns > 0 and hot_dmg > 0:
            player_hp = min(player_hp + hot_dmg, char_max_hp)
            parts.append(HOT_TICK_MESSAGE.format(hp=hot_dmg))
            hot_turns -= 1

        # ── Decrement attack buff ──────────────────────────────────────────────
        if buff_turns > 0:
            buff_turns -= 1
            if buff_turns == 0 and buff_label:
                expire_msg = BUFF_EXPIRE_MESSAGES.get(buff_label, "")
                if expire_msg:
                    parts.append(expire_msg)

        # ── Decrement shield ───────────────────────────────────────────────────
        if shield_turns > 0:
            shield_turns -= 1
            if shield_turns == 0:
                expire_key = buff_label if buff_label else "nullfield"
                expire_msg = BUFF_EXPIRE_MESSAGES.get(expire_key, "")
                if expire_msg:
                    parts.append(expire_msg)

        # ── Decrement parry turns ──────────────────────────────────────────────
        if parry_turns > 0:
            parry_turns -= 1
            # Expire message fires when shield_turns hits 0 (above), so no
            # duplicate message needed here — parry_turns mirrors shield_turns.

        effects_msg = " ".join(parts)

        return (
            effects_msg,
            enemy.hp, player_hp,
            dot_dmg, dot_turns, dot_label,
            buff_stat, buff_amount, buff_turns, buff_label,
            shield_pct, shield_turns,
            hot_dmg, hot_turns,
            parry_turns,
        )

    # ── Enemy actions ──────────────────────────────────────────────────────────

    def enemy_attack(self, player, enemy, action=None, boss_phase=1):
        weights = PHASE2_WEIGHTS if boss_phase == 2 else PHASE1_WEIGHTS
        if action not in ('attack', 'big_hit', 'flurry'):
            action = np.random.choice(['attack', 'big_hit', 'flurry'], p=weights)

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
            dmg        = max(15, hits * single_hit - int(eff_def * 1.0))
            msg        = f"The enemy unleashes a flurry of {hits} {dmg_label} strikes!"
        elif action == 'big_hit':
            dmg = max(8, atk_stat + np.random.randint(10, 20) - int(eff_def * 0.8))
            msg = f"A massive {dmg_label} attack is incoming!"
        else:
            dmg = max(5, atk_stat + np.random.randint(0, 10) - int(eff_def * 1.1))
            msg = f"A swift {dmg_label} strike!"

        if boss_phase == 2:
            dmg = max(1, int(round(dmg * PHASE2_DMG_MULT)))

        return action, msg, dmg

    def resolve_player_action(self, move_type, player_action, dmg, current_hp, player,
                               smoke_screen_active=False, shield_pct=0.0):
        class_name = player.get('class_name', 'Knight')

        if shield_pct > 0.0:
            dmg = max(1, int(round(dmg * (1.0 - shield_pct))))

        if smoke_screen_active:
            return current_hp, "💨 The smoke screen works — the attack passes harmlessly through shadow!"

        if player_action == 'dodge':
            success_chance = player.get('dodge_chance', Character.get_dodge(class_name))
            if np.random.rand() < success_chance:
                return current_hp, "You dodged the attack completely!"
            else:
                return current_hp - dmg, f"You failed to dodge and took {dmg} damage."
        elif player_action == 'block':
            reduction_ratio = player.get('block_multiplier', Character.get_block_mult(class_name))
            blocked = int(dmg * reduction_ratio)
            return current_hp - blocked, f"You blocked the hit and took {blocked} damage."
        else:
            return current_hp - dmg, f"You took {dmg} damage."

    def predict_enemy_move(self, player, boss_phase=1):
        weights = PHASE2_WEIGHTS if boss_phase == 2 else PHASE1_WEIGHTS
        move    = np.random.choice(['attack', 'big_hit', 'flurry'], p=weights)
        messages = {
            'flurry':  "The enemy is angered and preparing a flurry of strikes!",
            'big_hit': "The enemy is preparing a massive attack!",
            'attack':  "The enemy is preparing a standard attack.",
        }
        return move, messages[move], None

    def get_phase2_lore(self, boss_name):
        boss = BOSSES.get(boss_name)
        if boss:
            return boss.get('phase2_lore', BOSS_PHASE2_LORE_DEFAULT)
        return BOSS_PHASE2_LORE_DEFAULT

    def fire_parry_counter(self, player, enemy):
        """
        Fire the Samurai Iron Stance auto-counter.
        Called by battle_routes Step 4 when damage lands while parry is active.
        Returns (counter_msg, enemy.hp, dmg).
        """
        parry_counter_pct = player.get('parry_counter_pct_active', 0.0)
        base_atk  = player.get('attack', 0)
        eff_def   = int(enemy.defense * PHYS_PEN)
        dmg       = max(1, int(round(base_atk * parry_counter_pct)) - eff_def)
        enemy.hp -= dmg
        msg = PARRY_COUNTER_MSG.format(dmg=dmg)
        return msg, enemy.hp, dmg