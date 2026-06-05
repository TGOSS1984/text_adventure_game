"""
routes.py

Commit 7 additions:
- /start: initialise mp=0, special_cooldown=0 in session
- /battle POST: handle 'special' action via BattleManager.use_special()
- Each turn: regen MP (capped at mp_max), decrement cooldown
- Stun flag: if session['stunned'], skip enemy counter for that turn
- Smoke screen flag: if session['smoke_screen_active'], pass to resolve_player_action
- Both flags are single-use and cleared after consumption

Commit 10 additions:
- Enemy soul_reward stored in session["enemy"]["soul_reward"]
- On enemy kill: award soul_reward to session["souls"]
  Boss bonus: award an additional 50% (rounded) on top of base reward
- /shop GET: render shop.html with available items and player's souls
- /buy  POST: validate item key, check funds, apply upgrade, deduct souls
  Items: estus_refill, attack_shard, defense_shard, hp_vessel
  Each item can only be bought once per run (session["shop_bought"] set)
"""

from flask import Blueprint, render_template, request, redirect, url_for, session, flash, Response
from app.story.story_engine import Story
from .combat import BattleManager, MP_REGEN_ATTACK
from .models import Character
from .save_load import save_game, load_game, has_save
from .models import Enemy
from .enemies import BOSSES
import random

NORMAL_BATTLE_BGS = [
    "images/areas/undead_settlement.jpg",
    "images/areas/high_walls.jpg",
    "images/areas/irithyl.jpg",
    "images/areas/bolateria.jpg",
]
BOSS_BATTLE_BGS = [
    "images/areas/ringed_city.jpg",
    "images/areas/stormveil.jpg",
    "images/areas/erdtree.jpg",
]

# ── Commit 10: Shop catalogue ─────────────────────────────────────────────────
# Each item: cost (souls), one-time purchase per run, effect applied in /buy
SHOP_ITEMS = {
    "estus_refill": {
        "name":        "Estus Refill",
        "description": "Restore all Estus Flasks to full.",
        "cost":        150,
        "icon":        "fas fa-flask",
        "repeatable":  True,   # can buy every time you visit a bonfire
    },
    "attack_shard": {
        "name":        "Cracked Red Shard",
        "description": "Sharpen your weapon. Attack +3 (permanent).",
        "cost":        200,
        "icon":        "fas fa-fire-flame-curved",
        "repeatable":  False,
    },
    "defense_shard": {
        "name":        "Cracked Blue Shard",
        "description": "Harden your resolve. Defense +3 (permanent).",
        "cost":        175,
        "icon":        "fas fa-shield-halved",
        "repeatable":  False,
    },
    "hp_vessel": {
        "name":        "Vessel of Embers",
        "description": "Kindle your flame. Max HP +20 (permanent).",
        "cost":        250,
        "icon":        "fas fa-heart",
        "repeatable":  False,
    },
}
# ─────────────────────────────────────────────────────────────────────────────

main        = Blueprint("main", __name__)
story       = Story()
battle_manager = BattleManager()


def _is_htmx():
    return request.headers.get("HX-Request") == "true"


def _htmx_redirect(location):
    return Response(status=200, headers={"HX-Redirect": location})


@main.route("/")
def index():
    class_stats = Character.get_class_stats()
    return render_template("index.html", class_stats=class_stats, has_save=has_save())


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

    session["character"] = {
        "name":             character.name,
        "attack":           character.attack,
        "defense":          character.defense,
        "max_hp":           character.max_hp,
        "class_name":       character.class_name,
        "image":            character.image,
        "crit_chance":      getattr(character, "crit_chance", 0.0),
        "crit_multiplier":  getattr(character, "crit_multiplier", 1.0),
        "char_class":       char_class,
        "mp_max":           character.mp_max,
    }
    session["chapter"]          = 0
    session["hp"]               = character.max_hp
    session["enemy"]            = {}
    session["estus"]            = 5
    # ── Commit 7: MP and special move state ──────────────────────────────────
    session["mp"]               = 0      # start at 0 — must be earned
    session["special_cooldown"] = 0      # ready immediately (no MP yet anyway)
    session["stunned"]          = False  # enemy stun flag
    session["smoke_screen_active"] = False  # Rogue smoke screen flag
    session["souls"]            = 0      # souls currency (Commit 10)
    session["estus_max"]        = 5      # default; raised to 6 by estus_plus gift
    # ── Commit 10: track one-time shop purchases ─────────────────────────────
    session["shop_bought"]      = []     # list of item keys bought this run
    # ─────────────────────────────────────────────────────────────────────────

    # ── Apply starting gift ───────────────────────────────────────────────────
    gift = (request.form.get("gift") or "fading_soul").strip()
    session["gift"] = gift

    if gift == "estus_plus":
        session["estus"]     = 6
        session["estus_max"] = 6
    elif gift == "hunters_charm":
        session["character"]["crit_chance"] = round(
            session["character"]["crit_chance"] + 0.05, 4
        )
    elif gift == "iron_talisman":
        session["character"]["defense"] += 3
    elif gift == "witchs_ember":
        session["character"]["attack"] += 3
    elif gift == "old_coin":
        session["souls"] = 200
    # fading_soul: no effect — intentional
    # ─────────────────────────────────────────────────────────────────────────

    session.pop("_flashes", None)

    return redirect(url_for("main.game"))


@main.after_request
def no_cache(resp):
    resp.headers["Cache-Control"] = "no-store"
    return resp


@main.route("/game", methods=["GET", "POST"])
def game():
    if request.method == "POST":
        choice     = request.form["choice"]
        next_chapter = story.choose_path(choice)
        next_data  = story.get_chapter(next_chapter)

        session["choices"] = next_data.get("choices", [])

        if next_data.get("battle"):
            is_boss    = next_data.get("boss", False)
            bg_pool    = BOSS_BATTLE_BGS if is_boss else NORMAL_BATTLE_BGS
            session["battle_bg"] = random.choice(bg_pool)
            boss_name  = next_data.get("boss_name") if is_boss else None
            enemy      = battle_manager.generate_enemy(boss=is_boss, boss_name=boss_name)

            session["enemy"] = {
                "name":        enemy.name,
                "hp":          enemy.hp,
                "max_hp":      enemy.hp,
                "attack":      enemy.attack,
                "image":       enemy.image,
                "lore":        enemy.lore,
                "soul_reward": enemy.soul_reward,   # Commit 10
            }
            session["enemy_is_boss"]       = is_boss
            session["chapter_after_battle"] = next_chapter
            return redirect(url_for("main.battle"))
        else:
            session["chapter"] = next_chapter
            return redirect(url_for("main.game"))

    chapter = session.get("chapter", 0)
    data    = story.get_chapter(chapter)

    if data.get("rest") and not session.get("rested_here"):
        session["hp"]    = session["character"]["max_hp"]
        session["estus"] = session.get("estus_max", 5)
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
        souls=session.get("souls", 0),   # Commit 10
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
        soul_reward=enemy_data.get("soul_reward", 0),   # Commit 10
    )
    enemy.max_hp = enemy_data.get("max_hp", enemy.hp)

    character    = session.get("character", {})
    player_hp    = session.get("hp", 100)
    estus_count  = session.get("estus", 0)
    mp           = session.get("mp", 0)
    mp_max       = character.get("mp_max", 100)
    cooldown     = session.get("special_cooldown", 0)
    souls        = session.get("souls", 0)   # Commit 10
    message      = ""

    # ── GET ────────────────────────────────────────────────────────────────────
    if request.method == "GET":
        predicted_move, predicted_msg, _ = battle_manager.predict_enemy_move(character)
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
            estus_max=session.get("estus_max", 5),
            souls=souls,   # Commit 10
        )

    # ── POST ───────────────────────────────────────────────────────────────────
    predicted_move      = session.get("predicted_move")
    action              = request.form.get("action")
    stunned             = session.get("stunned", False)
    smoke_screen_active = session.get("smoke_screen_active", False)

    # ── Cooldown tick (every turn) ───────────────────────────────────────────
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
        message      = msg
        stunned      = stun_enemy
        smoke_screen_active = smoke

    elif action in ["dodge", "block"]:
        message = ""

    elif action == "estus":
        player_hp, estus_count, message = battle_manager.use_estus(
            player_hp, character["max_hp"], estus_count
        )

    elif action == "timeout":
        _, warn_msg, dmg = battle_manager.enemy_attack(character, enemy, action=predicted_move)
        player_hp, result = battle_manager.resolve_player_action(
            predicted_move, "none", dmg, player_hp, character
        )
        message = "⏰ You hesitated! " + warn_msg + " " + result

    # ── Enemy counter-attack ───────────────────────────────────────────────────
    enemy_acted = False
    if enemy.hp > 0 and not stunned and action not in ("timeout", "estus"):
        _, warn_msg, dmg = battle_manager.enemy_attack(
            character, enemy, action=predicted_move
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
        enemy_acted = True

    if action == "estus" and enemy.hp > 0:
        _, warn_msg, dmg = battle_manager.enemy_attack(
            character, enemy, action=predicted_move
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
        # ── Commit 10: award souls on kill ────────────────────────────────────
        reward = enemy.soul_reward
        if session.get("enemy_is_boss", False):
            # Boss bonus: +50% souls rounded to nearest 5
            bonus  = round(reward * 0.5 / 5) * 5
            reward = reward + bonus
            flash(f"⚔️ Boss slain! You gain {reward} souls ({bonus} bonus).", "info")
        else:
            flash(f"💀 Enemy defeated. You gain {reward} souls.", "info")
        session["souls"] = session.get("souls", 0) + reward
        # ─────────────────────────────────────────────────────────────────────
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

    next_move, next_msg, _ = battle_manager.predict_enemy_move(character)
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
        estus_max=session.get("estus_max", 5),
        souls=session.get("souls", 0),   # Commit 10
    )

    if _is_htmx():
        return render_template("battle_fragment.html", **template_vars)
    return render_template("battle.html", **template_vars)


# ── Commit 10: Shop routes ────────────────────────────────────────────────────

@main.route("/shop")
def shop():
    """Bonfire shop — only reachable from rest chapters via game.html link."""
    souls      = session.get("souls", 0)
    bought     = session.get("shop_bought", [])
    character  = session.get("character", {})
    estus      = session.get("estus", 0)
    estus_max  = session.get("estus_max", 5)

    # Build display list: mark items as bought/unavailable
    items = []
    for key, item in SHOP_ITEMS.items():
        can_buy = souls >= item["cost"]
        already_bought = (not item["repeatable"]) and (key in bought)
        # estus_refill is pointless if already full
        if key == "estus_refill" and estus >= estus_max:
            already_bought = True  # show as "unavailable" label rather than "sold out"
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
    """Process a shop purchase. Validates funds, applies effect, deducts souls."""
    item_key = request.form.get("item_key", "").strip()

    if item_key not in SHOP_ITEMS:
        flash("Unknown item.", "error")
        return redirect(url_for("main.shop"))

    item       = SHOP_ITEMS[item_key]
    souls      = session.get("souls", 0)
    bought     = session.get("shop_bought", [])
    estus      = session.get("estus", 0)
    estus_max  = session.get("estus_max", 5)

    # Guard: one-time items
    if not item["repeatable"] and item_key in bought:
        flash(f"You have already purchased {item['name']}.", "error")
        return redirect(url_for("main.shop"))

    # Guard: estus_refill when already full
    if item_key == "estus_refill" and estus >= estus_max:
        flash("Your Estus Flasks are already full.", "error")
        return redirect(url_for("main.shop"))

    # Guard: afford?
    if souls < item["cost"]:
        flash(f"Not enough souls. You need {item['cost']}, you have {souls}.", "error")
        return redirect(url_for("main.shop"))

    # ── Apply effect ──────────────────────────────────────────────────────────
    session["souls"] = souls - item["cost"]

    if item_key == "estus_refill":
        session["estus"] = estus_max
        flash(f"🔥 Estus Flasks refilled. ({item['cost']} souls spent)", "info")

    elif item_key == "attack_shard":
        session["character"]["attack"] += 3
        session["shop_bought"] = bought + [item_key]
        flash(f"⚔️ Attack increased by 3. ({item['cost']} souls spent)", "info")

    elif item_key == "defense_shard":
        session["character"]["defense"] += 3
        session["shop_bought"] = bought + [item_key]
        flash(f"🛡️ Defense increased by 3. ({item['cost']} souls spent)", "info")

    elif item_key == "hp_vessel":
        session["character"]["max_hp"] += 20
        session["hp"] = min(session.get("hp", 0) + 20, session["character"]["max_hp"])
        session["shop_bought"] = bought + [item_key]
        flash(f"❤️ Max HP increased by 20. ({item['cost']} souls spent)", "info")
    # ─────────────────────────────────────────────────────────────────────────

    # Mark session as modified (mutable nested dict)
    session.modified = True

    return redirect(url_for("main.shop"))

# ─────────────────────────────────────────────────────────────────────────────


@main.route("/death")
def death():
    return render_template("death.html")


@main.route("/restart", methods=["POST"])
def restart():
    session.clear()
    session.pop("_flashes", None)
    return redirect(url_for("main.index"))


@main.route("/save")
def save():
    save_game(session)
    return redirect(url_for("main.game"))


@main.route("/load")
def load():
    load_game(session)
    return redirect(url_for("main.game"))