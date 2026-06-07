"""
routes.py

Commit 7 additions:
- /start: initialise mp=0, special_cooldown=0 in session
- /battle POST: handle 'special' action via BattleManager.use_special()
- Each turn: regen MP (capped at mp_max), decrement cooldown
- Stun flag: if session['stunned'], skip enemy counter for that turn
- Smoke screen flag: if session['smoke_screen_active'], pass to resolve_player_action

Commit 10 additions:
- Enemy soul_reward stored in session["enemy"]["soul_reward"]
- On enemy kill: award soul_reward + boss 50% bonus
- /shop GET + /buy POST routes with 4 shop items

Commit 11 additions:
- session["boss_phase"]: 1 or 2, initialised in /start and when enemy is set
- session["phase_changed"]: single-use flag set when boss crosses 50% HP threshold
- boss_phase passed to enemy_attack() and predict_enemy_move()

Refactor:
- NORMAL_BATTLE_BGS, BOSS_BATTLE_BGS, SHOP_ITEMS imported from config.py
- GIFTS imported from config.py — /start gift logic is now a generic loop,
  no hardcoded if/elif per gift
- dodge_chance and block_multiplier added to session character dict so
  shop upgrades to these stats (e.g. Dodge Pendant) work correctly in combat
- BOSS_SOUL_BONUS, DEFAULT_ESTUS, ESTUS_HEAL_PCT imported from config.py
"""

from flask import Blueprint, render_template, request, redirect, url_for, session, flash, Response
from app.story.story_engine import Story
from .combat import BattleManager, MP_REGEN_ATTACK
from .config import (
    NORMAL_BATTLE_BGS, BOSS_BATTLE_BGS,
    SHOP_ITEMS, GIFTS,
    PHASE2_HP_TRIGGER,
    BOSS_SOUL_BONUS, DEFAULT_ESTUS,
)
from .models import Character, Enemy
from .classes import CLASSES
from .save_load import save_game, load_game, has_save, delete_save
from .enemies import ENEMIES, BOSSES
import random

main           = Blueprint("main", __name__)
story          = Story()
battle_manager = BattleManager()


def _is_htmx():
    return request.headers.get("HX-Request") == "true"


def _htmx_redirect(location):
    return Response(status=200, headers={"HX-Redirect": location})


@main.route("/")
def index():
    return render_template("index.html", classes=CLASSES, has_save=has_save())


@main.route("/start", methods=["POST"])
def start():
    posted     = (request.form.get("class") or "").strip()
    char_class = posted or session.get("character", {}).get("char_class")

    if not char_class:
        flash("Class not selected or missing. Please return to the main menu.", "error")
        return redirect(url_for("main.index"))

    character = Character.create(char_class)
    if not character:
        flash("Invalid character class.", "error")
        return redirect(url_for("main.index"))

    delete_save()

    session["character"] = {
        "name":            character.name,
        "attack":          character.attack,
        "defense":         character.defense,
        "max_hp":          character.max_hp,
        "class_name":      character.class_name,
        "image":           character.image,
        "crit_chance":     character.crit_chance,
        "crit_multiplier": character.crit_multiplier,
        "char_class":      char_class,
        "mp_max":          character.mp_max,
        "magic_attack":    character.magic_attack,
        "magic_defense":   character.magic_defense,
        "damage_type":     character.damage_type,
        # Stored so shop upgrades to these stats take effect in combat
        "dodge_chance":    character.dodge_chance,
        "block_multiplier": character.block_multiplier,
    }
    session["chapter"]             = 0
    session["hp"]                  = character.max_hp
    session["enemy"]               = {}
    session["estus"]               = DEFAULT_ESTUS
    session["mp"]                  = 0
    session["special_cooldown"]    = 0
    session["stunned"]             = False
    session["smoke_screen_active"] = False
    session["souls"]               = 0
    session["estus_max"]           = DEFAULT_ESTUS
    session["shop_bought"]         = []
    session["boss_phase"]          = 1
    session["phase_changed"]       = False

    gift = (request.form.get("gift") or "fading_soul").strip()
    session["gift"] = gift

    # ── Apply gift effect — driven entirely by GIFTS in config.py ─────────────
    gift_def = GIFTS.get(gift)
    if gift_def and gift_def.get("stat"):
        stat   = gift_def["stat"]
        amount = gift_def["amount"]
        mode   = gift_def.get("mode", "add")
        # Use magic_stat for magic damage_type classes if defined
        if session["character"].get("damage_type") == "magic":
            stat = gift_def.get("magic_stat", stat)

        if stat == "estus":
            # Sets both estus and estus_max
            session["estus"]     = amount
            session["estus_max"] = amount
        elif stat == "souls":
            session["souls"] = amount
        elif mode == "set":
            session["character"][stat] = amount
        else:
            # mode == "add"
            current = session["character"].get(stat, 0)
            session["character"][stat] = round(current + amount, 4)

    session.pop("_flashes", None)
    return redirect(url_for("main.game"))


@main.after_request
def no_cache(resp):
    resp.headers["Cache-Control"] = "no-store"
    return resp


@main.route("/game", methods=["GET", "POST"])
def game():
    if request.method == "POST":
        choice       = request.form["choice"]
        next_chapter = story.choose_path(choice)
        next_data    = story.get_chapter(next_chapter)

        session["choices"] = next_data.get("choices", [])

        if next_data.get("battle"):
            is_boss   = next_data.get("boss", False)
            bg_pool   = BOSS_BATTLE_BGS if is_boss else NORMAL_BATTLE_BGS
            session["battle_bg"] = random.choice(bg_pool)
            boss_name = next_data.get("boss_name") if is_boss else None
            enemy     = battle_manager.generate_enemy(boss=is_boss, boss_name=boss_name)

            session["enemy"] = {
                "name":          enemy.name,
                "hp":            enemy.hp,
                "max_hp":        enemy.hp,
                "attack":        enemy.attack,
                "image":         enemy.image,
                "lore":          enemy.lore,
                "soul_reward":   enemy.soul_reward,
                "magic_attack":  enemy.magic_attack,
                "magic_defense": enemy.magic_defense,
                "defense":       enemy.defense,
                "damage_type":   enemy.damage_type,
            }
            session["enemy_is_boss"]        = is_boss
            session["chapter_after_battle"] = next_chapter
            session["boss_phase"]           = 1
            session["phase_changed"]        = False
            return redirect(url_for("main.battle"))
        else:
            session["chapter"] = next_chapter
            return redirect(url_for("main.game"))

    chapter = session.get("chapter", 0)
    data    = story.get_chapter(chapter)

    if data.get("rest") and not session.get("rested_here"):
        session["hp"]    = session["character"]["max_hp"]
        session["estus"] = session.get("estus_max", DEFAULT_ESTUS)
        session["mp"]    = 0
        flash("🔥 You rest at the bonfire. HP, Estus Flasks and MP restored.", "info")
        session["rested_here"] = True
        return redirect(url_for("main.game"))

    session["rested_here"] = False
    hp = session.get("hp", session["character"]["max_hp"])

    return render_template(
        "game.html",
        chapter=data,
        hp=hp,
        character=session["character"],
        is_rest=bool(data.get("rest", False)),
        gift=session.get("gift", "fading_soul"),
        souls=session.get("souls", 0),
    )


@main.route("/battle", methods=["GET", "POST"])
def battle():
    preload_list = [url_for("static", filename=bg) for bg in NORMAL_BATTLE_BGS + BOSS_BATTLE_BGS]

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

    character   = session.get("character", {})
    player_hp   = session.get("hp", 100)
    estus_count = session.get("estus", 0)
    mp          = session.get("mp", 0)
    mp_max      = character.get("mp_max", 100)
    cooldown    = session.get("special_cooldown", 0)
    souls       = session.get("souls", 0)
    boss_phase    = session.get("boss_phase", 1)
    phase_changed = session.get("phase_changed", False)
    message = ""

    # ── GET ────────────────────────────────────────────────────────────────────
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

    # ── POST ───────────────────────────────────────────────────────────────────
    predicted_move      = session.get("predicted_move")
    action              = request.form.get("action")
    stunned             = session.get("stunned", False)
    smoke_screen_active = session.get("smoke_screen_active", False)

    session["phase_changed"] = False
    cooldown = max(0, cooldown - 1)

    # ── Player action ──────────────────────────────────────────────────────────
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

    # ── Check boss phase transition ────────────────────────────────────────────
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

    # ── Enemy counter-attack ───────────────────────────────────────────────────
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

    # ── Battle outcome ─────────────────────────────────────────────────────────
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

    # ── Write session state ────────────────────────────────────────────────────
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


# ── Shop routes ───────────────────────────────────────────────────────────────

@main.route("/shop")
def shop():
    souls     = session.get("souls", 0)
    bought    = session.get("shop_bought", [])
    character = session.get("character", {})
    estus     = session.get("estus", 0)
    estus_max = session.get("estus_max", DEFAULT_ESTUS)

    items = []
    for key, item in SHOP_ITEMS.items():
        can_buy        = souls >= item["cost"]
        already_bought = (not item["repeatable"]) and (key in bought)
        if key == "estus_refill" and estus >= estus_max:
            already_bought = True
        items.append({
            "key":            key,
            "name":           item["name"],
            "description":    item["description"],
            "cost":           item["cost"],
            "icon":           item["icon"],
            "can_buy":        can_buy and not already_bought,
            "already_bought": already_bought,
        })

    return render_template(
        "shop.html",
        items=items,
        souls=souls,
        character=character,
        gift=session.get("gift", "fading_soul"),
    )


@main.route("/buy", methods=["POST"])
def buy():
    item_key = request.form.get("item_key", "").strip()

    if item_key not in SHOP_ITEMS:
        flash("Unknown item.", "error")
        return redirect(url_for("main.shop"))

    item      = SHOP_ITEMS[item_key]
    souls     = session.get("souls", 0)
    bought    = session.get("shop_bought", [])
    estus     = session.get("estus", 0)
    estus_max = session.get("estus_max", DEFAULT_ESTUS)

    if not item["repeatable"] and item_key in bought:
        flash(f"You have already purchased {item['name']}.", "error")
        return redirect(url_for("main.shop"))

    if item_key == "estus_refill" and estus >= estus_max:
        flash("Your Estus Flasks are already full.", "error")
        return redirect(url_for("main.shop"))

    if souls < item["cost"]:
        flash(f"Not enough souls. You need {item['cost']}, you have {souls}.", "error")
        return redirect(url_for("main.shop"))

    session["souls"] = souls - item["cost"]

    if item_key == "estus_refill":
        session["estus"] = estus_max
        flash(f"🔥 Estus Flasks refilled. ({item['cost']} souls spent)", "info")

    elif item_key == "attack_shard":
        if session["character"].get("damage_type") == "magic":
            session["character"]["magic_attack"] += 3
            flash(f"✨ Magic Attack increased by 3. ({item['cost']} souls spent)", "info")
        else:
            session["character"]["attack"] += 3
            flash(f"⚔️ Attack increased by 3. ({item['cost']} souls spent)", "info")
        session["shop_bought"] = bought + [item_key]

    elif item_key == "defense_shard":
        if session["character"].get("damage_type") == "magic":
            session["character"]["magic_defense"] += 3
            flash(f"🔮 Magic Defense increased by 3. ({item['cost']} souls spent)", "info")
        else:
            session["character"]["defense"] += 3
            flash(f"🛡️ Defense increased by 3. ({item['cost']} souls spent)", "info")
        session["shop_bought"] = bought + [item_key]

    elif item_key == "hp_vessel":
        session["character"]["max_hp"] += 20
        session["hp"] = min(session.get("hp", 0) + 20, session["character"]["max_hp"])
        session["shop_bought"] = bought + [item_key]
        flash(f"❤️ Max HP increased by 20. ({item['cost']} souls spent)", "info")

    session.modified = True
    return redirect(url_for("main.shop"))


@main.route("/death")
def death():
    return render_template("death.html")


@main.route("/bestiary")
def bestiary():
    mid_run = bool(session.get("character"))
    return render_template(
        "bestiary.html",
        enemies=ENEMIES,
        bosses=BOSSES,
        mid_run=mid_run,
    )


@main.route("/restart", methods=["POST"])
def restart():
    delete_save()
    session.clear()
    session.pop("_flashes", None)
    return redirect(url_for("main.index"))


@main.route("/save")
def save():
    save_game(session)
    if request.args.get("next") == "index":
        return redirect(url_for("main.index"))
    return redirect(url_for("main.game"))


@main.route("/load")
def load():
    success = load_game(session)
    if not success:
        flash("Save file could not be loaded. Starting fresh.", "error")
        return redirect(url_for("main.index"))
    return redirect(url_for("main.game"))