"""
routes/battle_routes.py

Battle route:
    /battle  — GET: initial battle render
               POST: process player action, enemy counter, phase transition

Dual specials (secondary):
    action == "special2" fires use_special2() instead of use_special().
    Both share the same special_cooldown so only one can be used per cycle.

Active effects (DoT, buff, shield):
    apply_active_effects() ticks at the start of every POST turn.
    Session keys: dot_damage, dot_turns, dot_label,
                  buff_stat, buff_amount, buff_turns, buff_label,
                  shield_pct, shield_turns

Commit 3 — Run stats tracking:
    session['run_stats'] is updated at the following points each POST turn:

    damage_dealt   — incremented by the HP delta on the enemy object before
                     and after each damaging player action. Using the HP delta
                     (enemy_hp_before - enemy.hp) rather than a raw damage
                     variable avoids changing any combat.py return signatures.

    damage_taken   — incremented by the HP delta on the player before and
                     after resolve_player_action(). Captures real received
                     damage after dodge/block/shield reductions are applied.
                     Tracked for both the main counter-attack and the estus
                     counter (two separate enemy attack calls per turn).

    estus_used     — incremented only when estus_count > 0 before the call
                     (use_estus() already guards against empty flasks, but
                     we guard here too so the counter stays honest).

    specials_fired — incremented for both primary (special) and secondary
                     (special2) actions, but only when the special actually
                     fires (MP and cooldown checks pass). Detected by
                     comparing mp before and after — if mp decreased, a
                     special fired successfully.

    enemies_defeated / bosses_defeated / bosses_list / souls_earned —
                     all updated in Step 5 (battle outcome) when enemy.hp
                     drops to 0. souls_earned tracks the final reward
                     including the boss bonus.

    crits_landed   — detected by checking for the '💥 Critical' prefix in
                     the battle log message returned from attack(). Avoids
                     touching combat.py.

    All increments use a helper _update_run_stat() that reads the current
    session dict, modifies it, and writes it back. Flask sessions require
    explicit reassignment of mutable values to trigger the modified flag.
"""

from flask import render_template, request, redirect, url_for, session, flash, Response
from ..combat import BattleManager
from ..config import (
    MP_REGEN_ATTACK,
    NORMAL_BATTLE_BGS, BOSS_BATTLE_BGS, BOSS_BG_OVERRIDES,
    PHASE2_HP_TRIGGER,
    BOSS_SOUL_BONUS, DEFAULT_ESTUS,
)
from ..models import Enemy
from ..classes import CLASSES

battle_manager = BattleManager()


def _is_htmx():
    return request.headers.get("HX-Request") == "true"


def _htmx_redirect(location):
    return Response(status=200, headers={"HX-Redirect": location})


def _update_run_stat(key, delta):
    """
    Increment a single integer key inside session['run_stats'] by delta.

    Flask sessions require the dict to be reassigned (not just mutated)
    to mark the session as modified. This helper handles that correctly.

    key   — string key inside run_stats (e.g. 'damage_dealt')
    delta — integer to add (always positive)
    """
    stats = session.get("run_stats", {})
    stats[key] = stats.get(key, 0) + delta
    session["run_stats"] = stats


def _append_run_stat_list(key, value):
    """
    Append a value to a list key inside session['run_stats'].
    Used for bosses_list.
    """
    stats = session.get("run_stats", {})
    lst   = stats.get(key, [])
    if value not in lst:   # no duplicates — same boss can't be killed twice
        lst.append(value)
    stats[key] = lst
    session["run_stats"] = stats


def register(blueprint):
    """Attach battle routes to the given blueprint."""

    @blueprint.route("/battle", methods=["GET", "POST"])
    def battle():
        preload_list = [
            url_for("static", filename=bg)
            for bg in NORMAL_BATTLE_BGS + BOSS_BATTLE_BGS + list(BOSS_BG_OVERRIDES.values())
        ]

        enemy_data  = session.get("enemy", {})
        enemy_image = enemy_data.get("image") or "default.png"
        enemy_lore  = enemy_data.get("lore")  or "An unknown entity lurks in the darkness."

        enemy = Enemy(
            name=enemy_data.get("name"),
            hp=enemy_data.get("hp"),
            attack=enemy_data.get("attack"),
            image=enemy_image,
            lore=enemy_lore,
            is_boss=session.get("enemy_is_boss", False),
            soul_reward=enemy_data.get("soul_reward", 0),
            magic_attack=enemy_data.get("magic_attack", 0),
            magic_defense=enemy_data.get("magic_defense", 0),
            defense=enemy_data.get("defense", 0),
            damage_type=enemy_data.get("damage_type", "physical"),
        )
        enemy.max_hp = enemy_data.get("max_hp", enemy.hp)

        character     = session.get("character", {})
        player_hp     = session.get("hp", 100)
        estus_count   = session.get("estus", 0)
        mp            = session.get("mp", 0)
        mp_max        = character.get("mp_max", 100)
        cooldown      = session.get("special_cooldown", 0)
        souls         = session.get("souls", 0)
        boss_phase    = session.get("boss_phase", 1)
        phase_changed = session.get("phase_changed", False)

        # ── Active effect state ────────────────────────────────────────────────
        dot_dmg      = session.get("dot_damage", 0)
        dot_turns    = session.get("dot_turns", 0)
        dot_label    = session.get("dot_label", "")
        buff_stat    = session.get("buff_stat", None)
        buff_amount  = session.get("buff_amount", 0)
        buff_turns   = session.get("buff_turns", 0)
        buff_label   = session.get("buff_label", "")
        shield_pct   = session.get("shield_pct", 0.0)
        shield_turns = session.get("shield_turns", 0)

        message = ""

        # ── GET ────────────────────────────────────────────────────────────────
        if request.method == "GET":
            predicted_move, predicted_msg, _ = battle_manager.predict_enemy_move(
                character, boss_phase=boss_phase
            )
            session["predicted_move"] = predicted_move
            session["predicted_msg"]  = predicted_msg
            battle_bg = session.get("battle_bg", "images/areas/undead_settlement.jpg")
            return render_template(
                "battle.html",
                enemy=enemy,
                player_hp=player_hp,
                character=character,
                message=message,
                move_hint=predicted_msg,
                battle_bg=battle_bg,
                preload_list=preload_list,
                mp=mp,
                mp_max=mp_max,
                cooldown=cooldown,
                gift=session.get("gift", "fading_soul"),
                estus_max=session.get("estus_max", DEFAULT_ESTUS),
                souls=souls,
                boss_phase=boss_phase,
                phase_changed=False,
                classes=CLASSES,
                dot_dmg=dot_dmg,
                dot_turns=dot_turns,
                dot_label=dot_label,
                buff_stat=buff_stat,
                buff_amount=buff_amount,
                buff_turns=buff_turns,
                shield_pct=shield_pct,
                shield_turns=shield_turns,
            )

        # ── POST ───────────────────────────────────────────────────────────────
        predicted_move      = session.get("predicted_move")
        action              = request.form.get("action")
        stunned             = session.get("stunned", False)
        smoke_screen_active = session.get("smoke_screen_active", False)

        session["phase_changed"] = False
        cooldown = max(0, cooldown - 1)

        # ── Step 1: Tick active effects at turn start ──────────────────────────
        (
            effects_msg,
            enemy.hp,
            dot_dmg, dot_turns, dot_label,
            buff_stat, buff_amount, buff_turns, buff_label,
            shield_pct, shield_turns,
        ) = battle_manager.apply_active_effects(
            enemy=enemy,
            player_hp=player_hp,
            char_max_hp=character.get("max_hp", 100),
            dot_dmg=dot_dmg,
            dot_turns=dot_turns,
            dot_label=dot_label,
            buff_stat=buff_stat,
            buff_amount=buff_amount,
            buff_turns=buff_turns,
            buff_label=buff_label,
            shield_pct=shield_pct,
            shield_turns=shield_turns,
        )

        # Apply any attack buff to the character dict for this turn's damage calc
        active_character = dict(character)
        if buff_stat and buff_turns > 0 and buff_amount > 0:
            current_val = active_character.get(buff_stat, 0)
            active_character[buff_stat] = current_val + buff_amount

        # ── Step 2: Player action ──────────────────────────────────────────────
        # Track enemy HP before each damaging action so we can derive
        # actual damage dealt from the delta (avoids changing combat.py).
        enemy_hp_before_action = enemy.hp
        mp_before_action       = mp

        if action == "attack":
            result, enemy.hp = battle_manager.attack(active_character, enemy)
            message = result
            mp      = min(mp + MP_REGEN_ATTACK, mp_max)
            # Track damage dealt and crits
            dealt = max(0, enemy_hp_before_action - enemy.hp)
            if dealt > 0:
                _update_run_stat("damage_dealt", dealt)
            if "💥 Critical" in result:
                _update_run_stat("crits_landed", 1)

        elif action == "special":
            msg, enemy.hp, mp, cooldown, stun_enemy, smoke, heal_amt = (
                battle_manager.use_special(active_character, enemy, mp, cooldown)
            )
            message             = msg
            stunned             = stun_enemy
            smoke_screen_active = smoke
            if heal_amt > 0:
                player_hp = min(player_hp + heal_amt, character["max_hp"])
            # Track special fired (mp decreased = special succeeded)
            if mp < mp_before_action:
                _update_run_stat("specials_fired", 1)
            dealt = max(0, enemy_hp_before_action - enemy.hp)
            if dealt > 0:
                _update_run_stat("damage_dealt", dealt)

        elif action == "special2":
            (
                msg, enemy.hp, mp, cooldown,
                stun_enemy,
                new_dot_dmg, new_dot_turns, new_dot_label,
                side_fx,
            ) = battle_manager.use_special2(active_character, enemy, mp, cooldown)
            message = msg
            stunned = stun_enemy

            if new_dot_turns > 0:
                dot_dmg   = new_dot_dmg
                dot_turns = new_dot_turns
                dot_label = new_dot_label

            if side_fx["buff_stat"] and side_fx["buff_turns"] > 0:
                buff_stat   = side_fx["buff_stat"]
                buff_amount = side_fx["buff_amount"]
                buff_turns  = side_fx["buff_turns"]
                buff_label  = side_fx["buff_label"]

            if side_fx["shield_turns"] > 0:
                shield_pct   = side_fx["shield_pct"]
                shield_turns = side_fx["shield_turns"]

            if side_fx["heal_amount"] > 0:
                player_hp = min(
                    player_hp + side_fx["heal_amount"], character["max_hp"]
                )

            # Track special fired and damage dealt
            if mp < mp_before_action:
                _update_run_stat("specials_fired", 1)
            dealt = max(0, enemy_hp_before_action - enemy.hp)
            if dealt > 0:
                _update_run_stat("damage_dealt", dealt)

        elif action in ["dodge", "block"]:
            message = ""

        elif action == "estus":
            # Only count as used if flasks were available
            if estus_count > 0:
                _update_run_stat("estus_used", 1)
            player_hp, estus_count, message = battle_manager.use_estus(
                player_hp, character["max_hp"], estus_count
            )

        elif action == "timeout":
            _, warn_msg, dmg = battle_manager.enemy_attack(
                character, enemy, action=predicted_move, boss_phase=boss_phase
            )
            hp_before_timeout = player_hp
            player_hp, result = battle_manager.resolve_player_action(
                predicted_move, "none", dmg, player_hp, character,
                shield_pct=shield_pct,
            )
            message = "⏰ You hesitated! " + warn_msg + " " + result
            taken = max(0, hp_before_timeout - player_hp)
            if taken > 0:
                _update_run_stat("damage_taken", taken)

        # ── Step 3: Boss phase transition ──────────────────────────────────────
        phase_changed = False
        if (
            session.get("enemy_is_boss", False)
            and boss_phase == 1
            and enemy.hp > 0
            and enemy.hp <= enemy.max_hp * PHASE2_HP_TRIGGER
        ):
            boss_phase            = 2
            session["boss_phase"] = 2
            phase_changed         = True
            phase_lore            = battle_manager.get_phase2_lore(enemy.name)
            message = phase_lore + (" — " + message if message else "")

        # ── Step 4: Enemy counter-attack ───────────────────────────────────────
        if enemy.hp > 0 and not stunned and action not in ("timeout", "estus"):
            _, warn_msg, dmg = battle_manager.enemy_attack(
                character, enemy, action=predicted_move, boss_phase=boss_phase
            )
            hp_before_counter = player_hp
            player_hp, counter_result = battle_manager.resolve_player_action(
                predicted_move,
                action if action in ("dodge", "block") else "none",
                dmg,
                player_hp,
                character,
                smoke_screen_active=smoke_screen_active,
                shield_pct=shield_pct,
            )
            message = (message + " " + warn_msg + " " + counter_result).strip()
            # Track real damage taken after dodge/block/shield reductions
            taken = max(0, hp_before_counter - player_hp)
            if taken > 0:
                _update_run_stat("damage_taken", taken)

        if action == "estus" and enemy.hp > 0:
            _, warn_msg, dmg = battle_manager.enemy_attack(
                character, enemy, action=predicted_move, boss_phase=boss_phase
            )
            hp_before_estus_counter = player_hp
            player_hp, counter_result = battle_manager.resolve_player_action(
                predicted_move, "none", dmg, player_hp, character,
                shield_pct=shield_pct,
            )
            message = (message + " " + warn_msg + " " + counter_result).strip()
            taken = max(0, hp_before_estus_counter - player_hp)
            if taken > 0:
                _update_run_stat("damage_taken", taken)

        # Also track DoT damage dealt (ticked in Step 1 before player action)
        # DoT hits enemy — calculate from effects_msg presence and dot_dmg value
        # Simpler: track at tick time — dot_dmg was applied if dot_turns was > 0
        # before apply_active_effects ran. We already have the original values
        # from the session read at the top of POST — check if dot ticked.
        # dot_turns read from session at top = original; after apply it decrements.
        # If original dot_turns > 0, a tick happened.
        original_dot_turns = session.get("dot_turns", 0)
        if original_dot_turns > 0 and session.get("dot_damage", 0) > 0:
            _update_run_stat("damage_dealt", session.get("dot_damage", 0))

        if effects_msg:
            message = (effects_msg + " " + message).strip()

        session["stunned"]             = False
        session["smoke_screen_active"] = False

        # ── Step 5: Battle outcome ─────────────────────────────────────────────
        if enemy.hp <= 0:
            # Clear active effects on victory
            session["dot_damage"]   = 0
            session["dot_turns"]    = 0
            session["dot_label"]    = ""
            session["buff_stat"]    = None
            session["buff_amount"]  = 0
            session["buff_turns"]   = 0
            session["buff_label"]   = ""
            session["shield_pct"]   = 0.0
            session["shield_turns"] = 0

            reward = enemy.soul_reward
            if session.get("enemy_is_boss", False):
                bonus  = round(reward * BOSS_SOUL_BONUS / 5) * 5
                reward = reward + bonus
                flash(
                    f"⚔️ Boss slain! You gain {reward} souls ({bonus} bonus).",
                    "info"
                )
                # ── Track boss defeat ──────────────────────────────────────────
                _update_run_stat("bosses_defeated", 1)
                _append_run_stat_list("bosses_list", enemy.name)
            else:
                flash(f"💀 Enemy defeated. You gain {reward} souls.", "info")
                # ── Track regular enemy defeat ─────────────────────────────────
                _update_run_stat("enemies_defeated", 1)

            # ── Track souls earned (post-bonus) ───────────────────────────────
            _update_run_stat("souls_earned", reward)

            session["souls"]   = session.get("souls", 0) + reward
            session["chapter"] = session.get("chapter_after_battle", 0)
            victory_url = url_for("main.game")
            if _is_htmx():
                return _htmx_redirect(victory_url)
            return redirect(victory_url)

        if player_hp <= 0:
            death_url = url_for("main.death")
            if _is_htmx():
                return _htmx_redirect(death_url)
            return redirect(death_url)

        # ── Step 6: Write session state ────────────────────────────────────────
        session["enemy"]["hp"]      = enemy.hp
        session["hp"]               = player_hp
        session["estus"]            = estus_count
        session["mp"]               = mp
        session["special_cooldown"] = cooldown
        session["phase_changed"]    = phase_changed
        # Active effects
        session["dot_damage"]       = dot_dmg
        session["dot_turns"]        = dot_turns
        session["dot_label"]        = dot_label
        session["buff_stat"]        = buff_stat
        session["buff_amount"]      = buff_amount
        session["buff_turns"]       = buff_turns
        session["buff_label"]       = buff_label
        session["shield_pct"]       = shield_pct
        session["shield_turns"]     = shield_turns

        next_move, next_msg, _ = battle_manager.predict_enemy_move(
            character, boss_phase=boss_phase
        )
        session["predicted_move"] = next_move
        session["predicted_msg"]  = next_msg

        battle_bg = session.get("battle_bg", "images/areas/undead_settlement.jpg")

        template_vars = dict(
            enemy=enemy,
            player_hp=player_hp,
            character=character,
            message=message,
            move_hint=next_msg,
            battle_bg=battle_bg,
            preload_list=preload_list,
            mp=mp,
            mp_max=mp_max,
            cooldown=cooldown,
            gift=session.get("gift", "fading_soul"),
            estus_max=session.get("estus_max", DEFAULT_ESTUS),
            souls=souls,
            boss_phase=boss_phase,
            phase_changed=phase_changed,
            classes=CLASSES,
            dot_dmg=dot_dmg,
            dot_turns=dot_turns,
            dot_label=dot_label,
            buff_stat=buff_stat,
            buff_amount=buff_amount,
            buff_turns=buff_turns,
            shield_pct=shield_pct,
            shield_turns=shield_turns,
        )

        if _is_htmx():
            return render_template("battle_fragment.html", **template_vars)
        return render_template("battle.html", **template_vars)