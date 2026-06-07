"""
routes/battle_routes.py

Battle route:
    /battle  — GET: initial battle render
               POST: process player action, enemy counter, phase transition
"""

from flask import render_template, request, redirect, url_for, session, flash, Response
from ..combat import BattleManager, MP_REGEN_ATTACK
from ..config import (
    NORMAL_BATTLE_BGS, BOSS_BATTLE_BGS,
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


def register(blueprint):
    """Attach battle routes to the given blueprint."""

    @blueprint.route("/battle", methods=["GET", "POST"])
    def battle():
        preload_list = [
            url_for("static", filename=bg)
            for bg in NORMAL_BATTLE_BGS + BOSS_BATTLE_BGS
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
        message       = ""

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
            )

        # ── POST ───────────────────────────────────────────────────────────────
        predicted_move      = session.get("predicted_move")
        action              = request.form.get("action")
        stunned             = session.get("stunned", False)
        smoke_screen_active = session.get("smoke_screen_active", False)

        session["phase_changed"] = False
        cooldown = max(0, cooldown - 1)

        # ── Player action ──────────────────────────────────────────────────────
        if action == "attack":
            result, enemy.hp = battle_manager.attack(character, enemy)
            message = result
            mp = min(mp + MP_REGEN_ATTACK, mp_max)

        elif action == "special":
            msg, enemy.hp, mp, cooldown, stun_enemy, smoke = battle_manager.use_special(
                character, enemy, mp, cooldown
            )
            message             = msg
            stunned             = stun_enemy
            smoke_screen_active = smoke

        elif action in ["dodge", "block"]:
            message = ""

        elif action == "estus":
            player_hp, estus_count, message = battle_manager.use_estus(
                player_hp, character["max_hp"], estus_count
            )

        elif action == "timeout":
            _, warn_msg, dmg = battle_manager.enemy_attack(
                character, enemy, action=predicted_move, boss_phase=boss_phase
            )
            player_hp, result = battle_manager.resolve_player_action(
                predicted_move, "none", dmg, player_hp, character
            )
            message = "⏰ You hesitated! " + warn_msg + " " + result

        # ── Boss phase transition ──────────────────────────────────────────────
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

        # ── Enemy counter-attack ───────────────────────────────────────────────
        if enemy.hp > 0 and not stunned and action not in ("timeout", "estus"):
            _, warn_msg, dmg = battle_manager.enemy_attack(
                character, enemy, action=predicted_move, boss_phase=boss_phase
            )
            player_hp, counter_result = battle_manager.resolve_player_action(
                predicted_move,
                action if action in ("dodge", "block") else "none",
                dmg,
                player_hp,
                character,
                smoke_screen_active=smoke_screen_active,
            )
            message = (message + " " + warn_msg + " " + counter_result).strip()

        if action == "estus" and enemy.hp > 0:
            _, warn_msg, dmg = battle_manager.enemy_attack(
                character, enemy, action=predicted_move, boss_phase=boss_phase
            )
            player_hp, counter_result = battle_manager.resolve_player_action(
                predicted_move, "none", dmg, player_hp, character,
                smoke_screen_active=False,
            )
            message = (message + " " + warn_msg + " " + counter_result).strip()

        session["stunned"]             = False
        session["smoke_screen_active"] = False

        # ── Battle outcome ─────────────────────────────────────────────────────
        if enemy.hp <= 0:
            reward = enemy.soul_reward
            if session.get("enemy_is_boss", False):
                bonus  = round(reward * BOSS_SOUL_BONUS / 5) * 5
                reward = reward + bonus
                flash(f"⚔️ Boss slain! You gain {reward} souls ({bonus} bonus).", "info")
            else:
                flash(f"💀 Enemy defeated. You gain {reward} souls.", "info")
            session["souls"] = session.get("souls", 0) + reward
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

        # ── Write session state ────────────────────────────────────────────────
        session["enemy"]["hp"]      = enemy.hp
        session["hp"]               = player_hp
        session["estus"]            = estus_count
        session["mp"]               = mp
        session["special_cooldown"] = cooldown
        session["phase_changed"]    = phase_changed

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
        )

        if _is_htmx():
            return render_template("battle_fragment.html", **template_vars)
        return render_template("battle.html", **template_vars)