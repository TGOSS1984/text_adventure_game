"""
routes.py

File for the main flask routes that controls game flow.
Displays home page & class selection
Starts the game & initializes session data
Navigates through the story chapters
Manages battle initiation & combat mechanics
Healing logic, rest point, death logic
Save/Load state using session data

The routes combine with the story, combat, models files to move the gameplay along.
"""

from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from .story import Story
from .combat import BattleManager
from .models import Character
from .save_load import save_game, load_game
from .models import Enemy
import random

main = Blueprint("main", __name__)
story = Story()
battle_manager = BattleManager()


@main.route("/")
def index():
    return render_template("index.html")


@main.route("/start", methods=["POST"])
def start():
    char_class = request.form.get("class") or session.get("character", {}).get(
        "char_class"
    )
    if not char_class:
        flash("Class not selected or missing. Please return to the main menu.", "error")
        return redirect(url_for("main.index"))

    character = Character.create(char_class)
    if not character:
        flash("Invalid character class.", "error")
        return redirect(url_for("main.index"))

    session["character"] = character.__dict__
    session["chapter"] = 0
    session["hp"] = character.max_hp
    session["enemy"] = {}
    session["estus"] = 3
    return redirect(url_for("main.game"))


@main.route("/game", methods=["GET", "POST"])
def game():
    chapter = session.get("chapter", 0)
    hp = session.get("hp", 100)
    data = story.get_chapter(chapter)

    # Rest point logic (bonfire)
    if data.get("rest"):
        session["hp"] = session["character"]["max_hp"]
        session["estus"] = 3
        flash("You rest at the bonfire. HP and Estus Flasks restored.", "info")

    if request.method == "POST":
        choice = request.form["choice"]
        next_chapter = story.choose_path(choice)
        next_data = story.get_chapter(next_chapter)

        # Battle detection for next chapter
        if next_data.get("battle"):
            is_boss = next_data.get("boss", False)
            enemy = battle_manager.generate_enemy(boss=is_boss)

            # Store all relevant enemy attributes manually
            session["enemy"] = {
                "name": enemy.name,
                "hp": enemy.hp,
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

    return render_template(
        "game.html", chapter=data, hp=hp, character=session["character"]
    )


@main.route("/battle", methods=["GET", "POST"])
def battle():
    enemy_data = session.get("enemy", {})
    enemy_image = enemy_data.get("image") or "default.png"
    enemy_lore = enemy_data.get("lore") or "An unknown entity lurks in the darkness."

    enemy = Enemy(
        name=enemy_data.get("name"),
        hp=enemy_data.get("hp"),
        attack=enemy_data.get("attack"),
        image=enemy_image,
        lore=enemy_lore,
        is_boss=session.get("enemy_is_boss", False)
    )
    character = session.get("character", {})
    player_hp = session.get("hp", 100)
    estus_count = session.get("estus", 0)
    message = ""

    # GET: Predict next move and store in session
    if request.method == "GET":
        predicted_move, predicted_msg, _ = battle_manager.predict_enemy_move(character)
        session["predicted_move"] = predicted_move
        session["predicted_msg"] = predicted_msg
        return render_template(
            "battle.html",
            enemy=enemy,
            player_hp=player_hp,
            character=character,
            message=message,
            move_hint=predicted_msg,
        )

    # POST: Use the stored prediction
    predicted_move = session.get("predicted_move")
    move_hint = session.get("predicted_msg")
    action = request.form["action"]

    if action == "attack":
        result, enemy.hp = battle_manager.attack(character, enemy)
        message = result
        if enemy.hp > 0:
            _, warn_msg, dmg = battle_manager.enemy_attack(character, action=predicted_move)
            player_hp, result = battle_manager.resolve_player_action(
                predicted_move, "none", dmg, player_hp
            )
            message += " " + warn_msg + " " + result

    elif action in ["dodge", "block"]:
        _, warn_msg, dmg = battle_manager.enemy_attack(character, action=predicted_move)
        player_hp, result = battle_manager.resolve_player_action(
            predicted_move, action, dmg, player_hp
        )
        message = warn_msg + " " + result

    elif action == "estus":
        if estus_count > 0:
            player_hp, message = battle_manager.use_estus(player_hp, character["max_hp"])
            estus_count -= 1
        else:
            message = "You are out of Estus Flasks!"

    # Check battle outcome
    if enemy.hp <= 0:
        session["chapter"] = 5 if session.get("enemy_is_boss") else session.get("chapter_after_battle", 0)
        return redirect(url_for("main.game"))

    if player_hp <= 0:
        return redirect(url_for("main.death"))

    # Update session state
    session["enemy"]["hp"] = enemy.hp
    session["hp"] = player_hp
    session["estus"] = estus_count

    # Predict next move for next turn
    next_move, next_msg, _ = battle_manager.predict_enemy_move(character)
    session["predicted_move"] = next_move
    session["predicted_msg"] = next_msg

    return render_template(
        "battle.html",
        enemy=enemy,
        player_hp=player_hp,
        character=character,
        message=message,
        move_hint=next_msg,
    )


@main.route("/death")
def death():
    return render_template("death.html")


@main.route("/save")
def save():
    save_game(session)
    return redirect(url_for("main.game"))


@main.route("/load")
def load():
    load_game(session)
    return redirect(url_for("main.game"))
