"""
routes/game_routes.py

General game flow routes:
    /           — class selection screen
    /start      — POST: create character, apply gift, init session
    /game       — story chapter display and choice handling
    /death      — death screen
    /restart    — clear session and return to start
    /save       — persist session to disk
    /load       — restore session from disk
    /bestiary   — enemy/boss reference page
"""

from flask import render_template, request, redirect, url_for, session, flash
from ..combat import BattleManager
from ..config import (
    NORMAL_BATTLE_BGS, BOSS_BATTLE_BGS,
    GIFTS, DEFAULT_ESTUS,
)
from ..models import Character
from ..classes import CLASSES
from ..save_load import save_game, load_game, has_save, delete_save
from ..enemies import ENEMIES, BOSSES
from ..story.story_engine import Story
import random

story          = Story()
battle_manager = BattleManager()


def register(blueprint):
    """Attach all game routes to the given blueprint."""

    @blueprint.route("/")
    def index():
        return render_template("index.html", classes=CLASSES, has_save=has_save())

    @blueprint.route("/start", methods=["POST"])
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
            "name":             character.name,
            "attack":           character.attack,
            "defense":          character.defense,
            "max_hp":           character.max_hp,
            "class_name":       character.class_name,
            "image":            character.image,
            "crit_chance":      character.crit_chance,
            "crit_multiplier":  character.crit_multiplier,
            "char_class":       char_class,
            "mp_max":           character.mp_max,
            "magic_attack":     character.magic_attack,
            "magic_defense":    character.magic_defense,
            "damage_type":      character.damage_type,
            "dodge_chance":     character.dodge_chance,
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

        # ── Apply gift — driven by GIFTS in config.py ──────────────────────
        gift_def = GIFTS.get(gift)
        if gift_def and gift_def.get("stat"):
            stat   = gift_def["stat"]
            amount = gift_def["amount"]
            mode   = gift_def.get("mode", "add")
            if session["character"].get("damage_type") == "magic":
                stat = gift_def.get("magic_stat", stat)

            if stat == "estus":
                session["estus"]     = amount
                session["estus_max"] = amount
            elif stat == "souls":
                session["souls"] = amount
            elif mode == "set":
                session["character"][stat] = amount
            else:
                current = session["character"].get(stat, 0)
                session["character"][stat] = round(current + amount, 4)

        session.pop("_flashes", None)
        return redirect(url_for("main.game"))

    @blueprint.route("/game", methods=["GET", "POST"])
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

    @blueprint.route("/death")
    def death():
        return render_template("death.html")

    @blueprint.route("/bestiary")
    def bestiary():
        mid_run = bool(session.get("character"))
        return render_template(
            "bestiary.html",
            enemies=ENEMIES,
            bosses=BOSSES,
            mid_run=mid_run,
        )

    @blueprint.route("/restart", methods=["POST"])
    def restart():
        delete_save()
        session.clear()
        session.pop("_flashes", None)
        return redirect(url_for("main.index"))

    @blueprint.route("/save")
    def save():
        save_game(session)
        if request.args.get("next") == "index":
            return redirect(url_for("main.index"))
        return redirect(url_for("main.game"))

    @blueprint.route("/load")
    def load():
        success = load_game(session)
        if not success:
            flash("Save file could not be loaded. Starting fresh.", "error")
            return redirect(url_for("main.index"))
        return redirect(url_for("main.game"))