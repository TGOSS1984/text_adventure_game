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
- BOSS_PHASE2_LORE: dict of per-boss phase transition lore messages
- enemy_attack() accepts boss_phase param; phase 2 uses heavier move weights
  and applies a 1.20× damage multiplier across all move types
- predict_enemy_move() also accepts boss_phase so the hint reflects real weights
"""

import numpy as np
from .models import Enemy, Character
from .enemies import ENEMIES, BOSSES

# ── Constants ──────────────────────────────────────────────────────────────────
MP_COST         = 50
MP_REGEN_ATTACK = 25
COOLDOWN_TURNS  = 4

# Phase 2 modifiers
PHASE2_DMG_MULT   = 1.20   # all phase 2 damage ×1.20
PHASE2_HP_TRIGGER = 0.50   # phase 2 begins when boss HP ≤ 50%

# Phase 1 vs Phase 2 move probability weights
PHASE1_WEIGHTS = [0.60, 0.25, 0.15]   # attack / big_hit / flurry
PHASE2_WEIGHTS = [0.30, 0.38, 0.32]   # attack ↓, big_hit ↑, flurry ↑↑

# ── Per-boss phase 2 lore messages ────────────────────────────────────────────
# Shown once when the boss crosses the 50% HP threshold.
# Keep them short — they appear in the battle log box.
BOSS_PHASE2_LORE = {
    "Cindergloom": (
        "🔥 SECOND PHASE — The Flame Lord's wounds crack open, "
        "spilling rivers of molten gold. The air itself ignites. "
        "\"You dare fan the dying flame? Then burn with it!\""
    ),
    "Lothric and Lorian": (
        "⚡ SECOND PHASE — Lorian collapses — and Lothric descends upon his "
        "brother's back, pouring forbidden lightning into the broken body. "
        "They rise as one. The air crackles with desperate power."
    ),
    "Ashen Knight": (
        "💀 SECOND PHASE — The Ashen Knight tears the visor from his helm "
        "and screams. The ash fused to his flesh begins to glow. "
        "\"I have endured centuries of penance. You will not end it!\""
    ),
    "Pale Drake": (
        "❄️ SECOND PHASE — The Pale Drake rears back and shatters the ice "
        "shelf beneath you. His eyes, once clouded, blaze white. "
        "\"The stars do not forgive trespassers.\""
    ),
    "The Lord of Chains": (
        "⛓️ SECOND PHASE — The chains binding the Lord of Chains snap "
        "one by one. Each break draws blood — his own. He laughs. "
        "\"Pain is the only throne I need.\""
    ),
    "The Ember Tyrant": (
        "🌋 SECOND PHASE — The Ember Tyrant tears the fused chains "
        "free from his own flesh, roaring as obsidian skin splits. "
        "Magma pours from the wounds. The ground begins to melt."
    ),
    "The Mireborn Serpent": (
        "🐍 SECOND PHASE — The Mireborn Serpent submerges entirely — "
        "then erupts through the floor behind you, twice the size. "
        "The parasite within pulses with sickly green light."
    ),
    "The Gravewarden": (
        "☠️ SECOND PHASE — The Gravewarden removes his funeral crown "
        "and drives it into the earth. The buried dead begin to stir. "
        "\"Every soul here is mine to command.\""
    ),
    "The Abyss Watcher": (
        "🌑 SECOND PHASE — The Abyss Watcher drives his own sword "
        "through his chest and pulls it free glowing red. "
        "\"The Abyss does not kill me. It feeds me.\""
    ),
    "The Thorn Matriarch": (
        "🌹 SECOND PHASE — Crimson thorns erupt from the Thorn Matriarch's "
        "wounds, spreading across the chapel floor. She raises her arms "
        "and the briars respond. \"Every cut is a garden.\""
    ),
    "The Blacksteel Sentinel": (
        "⚒️ SECOND PHASE — The Blacksteel Sentinel drives both fists "
        "into the forge-floor. The entire bastion shudders. His armour "
        "glows white-hot. \"The walls do not fall. Neither do I.\""
    ),
}

# Fallback for any boss not in the dict
PHASE2_LORE_DEFAULT = (
    "⚠️ SECOND PHASE — The boss staggers — then steadies. "
    "Something ancient and terrible wakes behind its eyes."
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
                image=e['image'],
                lore=e['lore'],
                soul_reward=e.get('soul_reward', 0),
            )

    # ── Player actions ─────────────────────────────────────────────────────────

    def attack(self, player, enemy):
        crit_chance     = float(player.get('crit_chance', 0.0))
        crit_multiplier = float(player.get('crit_multiplier', 1.0))
        is_crit         = np.random.rand() < crit_chance

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
        if estus_count <= 0:
            return current_hp, 0, "No Estus Flasks left!"
        healed    = int(max_hp * 0.7)
        new_hp    = min(current_hp + healed, max_hp)
        new_estus = estus_count - 1
        msg       = f"You drink from the Estus Flask and recover {healed} HP."
        return new_hp, new_estus, msg

    def use_special(self, player, enemy, current_mp, cooldown):
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

        if class_name == 'Knight':
            dmg = player['attack'] - np.random.randint(0, 4)
            dmg = max(5, int(round(dmg)))
            enemy.hp -= dmg
            stun_enemy = True
            msg = (
                f"🛡️ Shield Bash! You crash your shield into the {enemy.name} "
                f"for {dmg} damage and stun them — they cannot counter this turn!"
            )

        elif class_name == 'Mage':
            dmg = int(round(player['attack'] * 2.0))
            dmg = max(10, dmg)
            enemy.hp -= dmg
            msg = (
                f"✨ Arcane Burst! A torrent of magic tears through the "
                f"{enemy.name} for {dmg} damage — defence is useless against pure arcane force!"
            )

        elif class_name == 'Rogue':
            dmg = max(3, int(round(player['attack'] * 0.5)))
            enemy.hp -= dmg
            smoke_screen = True
            msg = (
                f"💨 Smoke Screen! You hurl a blade from the shadows, dealing {dmg} damage, "
                "then vanish — the enemy's next attack will find nothing but smoke."
            )

        elif class_name == 'Archer':
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

    def enemy_attack(self, player, enemy, action=None, boss_phase=1):
        """
        Resolve the enemy's attack move.

        boss_phase (int): 1 = normal, 2 = enraged.
          Phase 2 uses heavier move weights and applies PHASE2_DMG_MULT.

        Returns (action, warning_message, damage).
        """
        weights = PHASE2_WEIGHTS if boss_phase == 2 else PHASE1_WEIGHTS

        if action not in ('attack', 'big_hit', 'flurry'):
            action = np.random.choice(
                ['attack', 'big_hit', 'flurry'], p=weights
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

        # Phase 2: all damage multiplied
        if boss_phase == 2:
            dmg = max(1, int(round(dmg * PHASE2_DMG_MULT)))

        return action, msg, dmg

    def resolve_player_action(self, move_type, player_action, dmg, current_hp, player,
                               smoke_screen_active=False):
        class_name = player.get('class_name', 'Knight')

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

    def predict_enemy_move(self, player, boss_phase=1):
        """
        Predict the enemy's next move for the UI hint.
        Uses the correct weight set for the current phase.
        Returns (move, hint_message, None).
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
        """Return the phase 2 transition lore message for this boss."""
        return BOSS_PHASE2_LORE.get(boss_name, PHASE2_LORE_DEFAULT)