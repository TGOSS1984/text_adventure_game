"""
routes.py

File for the main flask routes that controls game flow.

HTMX integration (Commit 5):
- /battle POST now checks for the HX-Request header.
- If present (HTMX call from battle_sounds.js):
    - Normal turn  → render battle_fragment.html (partial, no full page)
    - Victory/Death → return empty 200 with HX-Redirect header so HTMX
                      follows the redirect cleanly without a full reload
- If absent (direct browser POST / fallback):
    - Behaves exactly as before — full page render or redirect
This means the game works correctly with JS disabled or on browsers
without HTMX support.
"""

from flask import Blueprint, render_template, request, redirect, url_for, session, flash, Response
from app.story.story_engine import Story
from .combat import BattleManager
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

main = Blueprint("main", __name__)
story = Story()
battle_manager = BattleManager()


def _is_htmx():
    """Return True if the request was made by HTMX (partial swap expected)."""
    return request.headers.get("HX-Request") == "true"


def _htmx_redirect(location):
    """
    Return an empty 200 response with HX-Redirect header.
    HTMX intercepts this and navigates the browser to `location` —
    the equivalent of a server-side redirect but handled client-side
    so the full page is replaced cleanly.
    """
    return Response(
        status=200,
        headers={"HX-Redirect": location},
    )


@main.route("/")
def index():
    class_stats = Character.get_class_stats()
    return render_template("index.html", class_stats=class_stats, has_save=has_save())


@main.route("/start", methods=["POST"])
def start():
    posted = (request.form.get("class") or "").strip()
    char_class = posted or session.get("character", {}).get("char_class")

    if not char_class:
        flash("Class not selected or missing. Please return to the main menu.", "error")
        return redirect(url_for("main.index"))

    character = Character.create(char_class)
    if not character:
        flash("Invalid character class.", "error")
        return redirect(url_for("main.index"))

    session["character"] = {
        "name": character.name,
        "attack": character.attack,
        "defense": character.defense,
        "max_hp": character.max_hp,
        "class_name": character.class_name,
        "image": character.image,
        "crit_chance": getattr(character, "crit_chance", 0.0),
        "crit_multiplier": getattr(character, "crit_multiplier", 1.0),
        "char_class": char_class,
    }
    session["chapter"] = 0
    session["hp"] = character.max_hp
    session["enemy"] = {}
    session["estus"] = 5
    session.pop("_flashes", None)

    return redirect(url_for("main.game"))


@main.after_request
def no_cache(resp):
    resp.headers["Cache-Control"] = "no-store"
    return resp


@main.route("/game", methods=["GET", "POST"])
def game():
    if request.method == "POST":
        choice = request.form["choice"]
        next_chapter = story.choose_path(choice)
        next_data = story.get_chapter(next_chapter)

        session["choices"] = next_data.get("choices", [])

        if next_data.get("battle"):
            is_boss = next_data.get("boss", False)
            bg_pool = BOSS_BATTLE_BGS if is_boss else NORMAL_BATTLE_BGS
            session["battle_bg"] = random.choice(bg_pool)
            boss_name = next_data.get("boss_name") if is_boss else None
            enemy = battle_manager.generate_enemy(boss=is_boss, boss_name=boss_name)

            session["enemy"] = {
                "name": enemy.name,
                "hp": enemy.hp,
                "max_hp": enemy.hp,
                "attack": enemy.attack,
                "image": enemy.image,
                "lore": enemy.lore,
            }

            session["enemy_is_boss"] = is_boss
            session["chapter_after_battle"] = next_chapter
            return redirect(url_for("main.battle"))
        else:
            session["chapter"] = next_chapter
            return redirect(url_for("main.game"))

    # GET
    chapter = session.get("chapter", 0)
    data = story.get_chapter(chapter)

    if data.get("rest") and not session.get("rested_here"):
        session["hp"] = session["character"]["max_hp"]
        session["estus"] = 5
        flash("🔥 You rest at the bonfire. HP and Estus Flasks restored.", "info")
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
    )


@main.route("/battle", methods=["GET", "POST"])
def battle():
    preload_list = [url_for("static", filename=bg) for bg in NORMAL_BATTLE_BGS + BOSS_BATTLE_BGS]

    enemy_data = session.get("enemy", {})
    enemy_image = enemy_data.get("image") or "default.png"
    enemy_lore = enemy_data.get("lore") or "An unknown entity lurks in the darkness."

    enemy = Enemy(
        name=enemy_data.get("name"),
        hp=enemy_data.get("hp"),
        attack=enemy_data.get("attack"),
        image=enemy_image,
        lore=enemy_lore,
        is_boss=session.get("enemy_is_boss", False),
    )
    enemy.max_hp = enemy_data.get("max_hp", enemy.hp)

    character = session.get("character", {})
    player_hp = session.get("hp", 100)
    estus_count = session.get("estus", 0)
    message = ""

    # ── GET: first load of battle page ────────────────────────────────────────
    if request.method == "GET":
        predicted_move, predicted_msg, _ = battle_manager.predict_enemy_move(character)
        session["predicted_move"] = predicted_move
        session["predicted_msg"] = predicted_msg
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
        )

    # ── POST: battle action ───────────────────────────────────────────────────
    predicted_move = session.get("predicted_move")
    action = request.form.get("action")

    if action == "attack":
        result, enemy.hp = battle_manager.attack(character, enemy)
        message = result
        if enemy.hp > 0:
            _, warn_msg, dmg = battle_manager.enemy_attack(character, enemy, action=predicted_move)
            player_hp, result = battle_manager.resolve_player_action(
                predicted_move, "none", dmg, player_hp, character
            )
            message += " " + warn_msg + " " + result

    elif action in ["dodge", "block"]:
        _, warn_msg, dmg = battle_manager.enemy_attack(character, enemy, action=predicted_move)
        player_hp, result = battle_manager.resolve_player_action(
            predicted_move, action, dmg, player_hp, character
        )
        message = warn_msg + " " + result

    elif action == "estus":
        player_hp, estus_count, message = battle_manager.use_estus(
            player_hp, character["max_hp"], estus_count
        )

    # ── Battle outcome ────────────────────────────────────────────────────────

    if enemy.hp <= 0:
        session["chapter"] = session.get("chapter_after_battle", 0)
        victory_url = url_for("main.game")
        # HTMX: send HX-Redirect so the client navigates to the game screen
        if _is_htmx():
            return _htmx_redirect(victory_url)
        return redirect(victory_url)

    if player_hp <= 0:
        death_url = url_for("main.death")
        if _is_htmx():
            return _htmx_redirect(death_url)
        return redirect(death_url)

    # ── Normal turn: update session, return next state ────────────────────────

    session["enemy"]["hp"] = enemy.hp
    session["hp"] = player_hp
    session["estus"] = estus_count

    next_move, next_msg, _ = battle_manager.predict_enemy_move(character)
    session["predicted_move"] = next_move
    session["predicted_msg"] = next_msg

    battle_bg = session.get("battle_bg", "images/areas/undead_settlement.jpg")

    template_vars = dict(
        enemy=enemy,
        player_hp=player_hp,
        character=character,
        message=message,
        move_hint=next_msg,
        battle_bg=battle_bg,
        preload_list=preload_list,
    )

    # HTMX request → return only the fragment (no <html>, no <head>)
    if _is_htmx():
        return render_template("battle_fragment.html", **template_vars)

    # Non-HTMX fallback → full page (graceful degradation)
    return render_template("battle.html", **template_vars)


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
