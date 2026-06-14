"""
routes/battle_routes.py

Battle route:
    /battle  — GET: initial battle render
               POST: process player action, enemy counter, phase transition

Commit 8 additions:
    New session keys read/written: hot_dmg, hot_turns, parry_turns, parry_counter_pct.
    parry_counter_pct_active stored in active_character dict so combat.py can read it
    in fire_parry_counter() without touching the session directly.

    use_special() now returns 8-tuple — 8th value is primary_side_fx dict.
    action == 'special' unpacks primary_side_fx and applies buff + HoT session keys.

    apply_active_effects() signature extended — passes hot/parry state, receives
    extended 15-tuple return.

    Step 4 (enemy counter): after resolve_player_action(), if damage landed and
    parry_turns > 0, fire_parry_counter() is called and counter damage dealt to enemy.

    Step 5 (victory): hot_dmg, hot_turns, parry_turns, parry_counter_pct cleared.
    Step 6 (session write): new keys persisted.

    Unlock triggers:
    - Mesmereth defeated: unlock_class('Samurai') called
    - Any ending chapter reached via game_routes /game — handled there, not here
      (battle_routes doesn't know chapter IDs)
    - Barbarian unlock: triggered in game_routes when ending chapter is reached
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
from ..player_record import unlock_class

battle_manager = BattleManager()

# Boss name that triggers Samurai unlock
_SAMURAI_UNLOCK_BOSS = "Mesmereth, the Serpent Prince"


def _is_htmx():
    return request.headers.get("HX-Request") == "true"


def _htmx_redirect(location):
    return Response(status=200, headers={"HX-Redirect": location})


def _update_run_stat(key, delta):
    stats = session.get("run_stats", {})
    stats[key] = stats.get(key, 0) + delta
    session["run_stats"] = stats


def _append_run_stat_list(key, value):
    stats = session.get("run_stats", {})
    lst   = stats.get(key, [])
    if value not in lst:
        lst.append(value)
    stats[key] = lst
    session["run_stats"] = stats


def register(blueprint):

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
        dot_dmg           = session.get("dot_damage", 0)
        dot_turns         = session.get("dot_turns", 0)
        dot_label         = session.get("dot_label", "")
        buff_stat         = session.get("buff_stat", None)
        buff_amount       = session.get("buff_amount", 0)
        buff_turns        = session.get("buff_turns", 0)
        buff_label        = session.get("buff_label", "")
        shield_pct        = session.get("shield_pct", 0.0)
        shield_turns      = session.get("shield_turns", 0)
        # Commit 8: new active effect state
        hot_dmg           = session.get("hot_dmg", 0)
        hot_turns         = session.get("hot_turns", 0)
        parry_turns       = session.get("parry_turns", 0)
        parry_counter_pct = session.get("parry_counter_pct", 0.0)

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
                hot_dmg=hot_dmg,
                hot_turns=hot_turns,
                parry_turns=parry_turns,
            )

        # ── POST ───────────────────────────────────────────────────────────────
        predicted_move      = session.get("predicted_move")
        action              = request.form.get("action")
        stunned             = session.get("stunned", False)
        smoke_screen_active = session.get("smoke_screen_active", False)

        session["phase_changed"] = False
        cooldown = max(0, cooldown - 1)

        # ── Step 1: Tick active effects ────────────────────────────────────────
        (
            effects_msg,
            enemy.hp, player_hp,
            dot_dmg, dot_turns, dot_label,
            buff_stat, buff_amount, buff_turns, buff_label,
            shield_pct, shield_turns,
            hot_dmg, hot_turns,
            parry_turns,
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
            hot_dmg=hot_dmg,
            hot_turns=hot_turns,
            parry_turns=parry_turns,
            parry_counter_pct=parry_counter_pct,
        )

        # Build active_character — includes buff and parry_counter_pct for combat.py
        active_character = dict(character)
        if buff_stat and buff_turns > 0 and buff_amount > 0:
            current_val = active_character.get(buff_stat, 0)
            active_character[buff_stat] = current_val + buff_amount
        # Pass parry_counter_pct so fire_parry_counter() can read it
        active_character['parry_counter_pct_active'] = parry_counter_pct

        # ── Step 2: Player action ──────────────────────────────────────────────
        enemy_hp_before_action = enemy.hp
        mp_before_action       = mp

        if action == "attack":
            result, enemy.hp = battle_manager.attack(active_character, enemy)
            message = result
            mp      = min(mp + MP_REGEN_ATTACK, mp_max)
            dealt   = max(0, enemy_hp_before_action - enemy.hp)
            if dealt > 0:
                _update_run_stat("damage_dealt", dealt)
            if "💥 Critical" in result:
                _update_run_stat("crits_landed", 1)

        elif action == "special":
            # 8-tuple return — unpack primary_side_fx
            msg, enemy.hp, mp, cooldown, stun_enemy, smoke, heal_amt, primary_sfx = (
                battle_manager.use_special(active_character, enemy, mp, cooldown)
            )
            message             = msg
            stunned             = stun_enemy
            smoke_screen_active = smoke

            if heal_amt > 0:
                player_hp = min(player_hp + heal_amt, character["max_hp"])

            # Apply combo_buff_hot side effects (Barbarian)
            if primary_sfx.get("buff_stat") and primary_sfx.get("buff_turns", 0) > 0:
                buff_stat   = primary_sfx["buff_stat"]
                buff_amount = primary_sfx["buff_amount"]
                buff_turns  = primary_sfx["buff_turns"]
                buff_label  = primary_sfx["buff_label"]
            if primary_sfx.get("hot_turns", 0) > 0:
                hot_dmg   = primary_sfx["hot_dmg"]
                hot_turns = primary_sfx["hot_turns"]

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

            # Commit 8: parry effect sets both shield and parry state
            if side_fx.get("parry_turns", 0) > 0:
                parry_turns       = side_fx["parry_turns"]
                parry_counter_pct = side_fx["parry_counter_pct"]

            if side_fx["heal_amount"] > 0:
                player_hp = min(player_hp + side_fx["heal_amount"], character["max_hp"])

            if mp < mp_before_action:
                _update_run_stat("specials_fired", 1)
            dealt = max(0, enemy_hp_before_action - enemy.hp)
            if dealt > 0:
                _update_run_stat("damage_dealt", dealt)

        elif action in ["dodge", "block"]:
            message = ""

        elif action == "estus":
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
            taken   = max(0, hp_before_timeout - player_hp)
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
        damage_landed = False   # track whether a hit actually connected

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
            taken   = max(0, hp_before_counter - player_hp)
            if taken > 0:
                _update_run_stat("damage_taken", taken)
                damage_landed = True

            # ── Commit 8: Samurai parry auto-counter ───────────────────────────
            # Fires only if damage landed (not dodged/smoked) and parry is active
            if damage_landed and parry_turns > 0:
                counter_msg, enemy.hp, counter_dmg = battle_manager.fire_parry_counter(
                    active_character, enemy
                )
                message = (message + " " + counter_msg).strip()
                if counter_dmg > 0:
                    _update_run_stat("damage_dealt", counter_dmg)

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
            taken   = max(0, hp_before_estus_counter - player_hp)
            if taken > 0:
                _update_run_stat("damage_taken", taken)

        # Track DoT damage dealt (ticked in Step 1)
        original_dot_turns = session.get("dot_turns", 0)
        if original_dot_turns > 0 and session.get("dot_damage", 0) > 0:
            _update_run_stat("damage_dealt", session.get("dot_damage", 0))

        if effects_msg:
            message = (effects_msg + " " + message).strip()

        session["stunned"]             = False
        session["smoke_screen_active"] = False

        # ── Step 5: Battle outcome ─────────────────────────────────────────────
        if enemy.hp <= 0:
            # Clear all active effects
            session["dot_damage"]       = 0
            session["dot_turns"]        = 0
            session["dot_label"]        = ""
            session["buff_stat"]        = None
            session["buff_amount"]      = 0
            session["buff_turns"]       = 0
            session["buff_label"]       = ""
            session["shield_pct"]       = 0.0
            session["shield_turns"]     = 0
            session["hot_dmg"]          = 0
            session["hot_turns"]        = 0
            session["parry_turns"]      = 0
            session["parry_counter_pct"] = 0.0

            reward = enemy.soul_reward
            if session.get("enemy_is_boss", False):
                bonus  = round(reward * BOSS_SOUL_BONUS / 5) * 5
                reward = reward + bonus
                flash(f"⚔️ Boss slain! You gain {reward} souls ({bonus} bonus).", "info")
                _update_run_stat("bosses_defeated", 1)
                _append_run_stat_list("bosses_list", enemy.name)

                # ── Commit 8: unlock triggers ──────────────────────────────────
                if enemy.name == _SAMURAI_UNLOCK_BOSS:
                    newly_unlocked = unlock_class("Samurai")
                    if newly_unlocked:
                        flash("⚔ The Samurai class has been unlocked!", "info")
                    session["shadow_realm_completed"] = True
            else:
                flash(f"💀 Enemy defeated. You gain {reward} souls.", "info")
                _update_run_stat("enemies_defeated", 1)

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
        session["enemy"]["hp"]       = enemy.hp
        session["hp"]                = player_hp
        session["estus"]             = estus_count
        session["mp"]                = mp
        session["special_cooldown"]  = cooldown
        session["phase_changed"]     = phase_changed
        session["dot_damage"]        = dot_dmg
        session["dot_turns"]         = dot_turns
        session["dot_label"]         = dot_label
        session["buff_stat"]         = buff_stat
        session["buff_amount"]       = buff_amount
        session["buff_turns"]        = buff_turns
        session["buff_label"]        = buff_label
        session["shield_pct"]        = shield_pct
        session["shield_turns"]      = shield_turns
        session["hot_dmg"]           = hot_dmg
        session["hot_turns"]         = hot_turns
        session["parry_turns"]       = parry_turns
        session["parry_counter_pct"] = parry_counter_pct

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
            hot_dmg=hot_dmg,
            hot_turns=hot_turns,
            parry_turns=parry_turns,
        )

        if _is_htmx():
            return render_template("battle_fragment.html", **template_vars)
        return render_template("battle.html", **template_vars)