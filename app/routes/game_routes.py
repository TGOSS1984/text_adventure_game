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
    /status     — player stats overview screen
"""

from flask import render_template, request, redirect, url_for, session, flash
import random
from ..combat import BattleManager
from ..config import (
    NORMAL_BATTLE_BGS, BOSS_BATTLE_BGS, BOSS_BG_OVERRIDES, REST_BGS,
    GIFTS, DEFAULT_ESTUS,
)
from ..models import Character
from ..classes import CLASSES
from ..save_load import save_game, load_game, has_save, delete_save
from ..enemies import ENEMIES, BOSSES
from ..story.story_engine import Story

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
        # ── Active effect state (dual specials) ───────────────────────────────
        session["dot_damage"]          = 0
        session["dot_turns"]           = 0
        session["dot_label"]           = ""
        session["buff_stat"]           = None
        session["buff_amount"]         = 0
        session["buff_turns"]          = 0
        session["buff_label"]          = ""
        session["shield_pct"]          = 0.0
        session["shield_turns"]        = 0

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
            elif stat == "max_hp":                          # ← add this branch
                current = session["character"].get("max_hp", 0)
                session["character"]["max_hp"] = current + amount
                session["hp"] = session["character"]["max_hp"]  # live HP matches new max   
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
                boss_name = next_data.get("boss_name") if is_boss else None
                if is_boss and boss_name in BOSS_BG_OVERRIDES:
                    session["battle_bg"] = BOSS_BG_OVERRIDES[boss_name]
                else:
                    bg_pool = BOSS_BATTLE_BGS if is_boss else NORMAL_BATTLE_BGS
                    session["battle_bg"] = random.choice(bg_pool)
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
            session["rest_bg"] = random.choice(REST_BGS)
            session["hp"]    = session["character"]["max_hp"]
            session["estus"] = session.get("estus_max", DEFAULT_ESTUS)
            session["mp"]    = 0
            flash("🔥 You rest at the bonfire. HP, Estus Flasks and MP restored.", "info")
            session["rested_here"] = True
            return redirect(url_for("main.game"))

        session["rested_here"] = False
        hp = session.get("hp", session["character"]["max_hp"])

        # ── Secret map icon ───────────────────────────────────────────────────
        # Show on any story chapter that is not a battle, boss, or rest area.
        # Probability is set per-session so the icon appears consistently on the
        # same chapter across a single playthrough (not randomly per page load).
        chapter_id      = session.get("chapter", 0)
        is_eligible     = (
            not data.get("battle") and
            not data.get("boss") and
            not data.get("rest") and
            chapter_id not in [0, 100, 101, 102]  # exclude terminal chapters
        )
        # Use a session-stable set of "secret" chapters so the map appears
        # on the same chapters every playthrough (seeded when session starts).
        secret_chapters = session.get("secret_chapters", [])
        if not secret_chapters and is_eligible:
            # Pick 8 random eligible chapters to show the map on this run
            all_story = [n for n in range(1, 100)
                         if n not in [7,14,20,25,34,40,45,50,54,59,62,65,68,
                                      71,74,76,78,80,82,88,93]]
            secret_chapters = random.sample(all_story, min(8, len(all_story)))
            session["secret_chapters"] = secret_chapters

        show_secret_map = is_eligible and chapter_id in secret_chapters

        return render_template(
            "game.html",
            chapter=data,
            hp=hp,
            character=session["character"],
            is_rest=bool(data.get("rest", False)),
            gift=session.get("gift", "fading_soul"),
            souls=session.get("souls", 0),
            show_secret_map=show_secret_map,
        )

    @blueprint.route("/enter_shadow_realm", methods=["POST"])
    def enter_shadow_realm():
        """Store the return chapter and redirect to the Shadow Realm entry."""
        return_chapter = session.get("chapter", 0)
        session["secret_return_chapter"] = return_chapter
        session["chapter"] = 103
        return redirect(url_for("main.game"))

    @blueprint.route("/leave_shadow_realm", methods=["POST"])
    def leave_shadow_realm():
        """Return to the chapter the player was on when they found the map."""
        return_chapter = session.get("secret_return_chapter", 0)
        session["chapter"] = return_chapter
        return redirect(url_for("main.game"))

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

    @blueprint.route("/status")
    def status():
        """
        Player status screen — reads live session values so all
        shop upgrades, gift bonuses, and current HP/MP are reflected.
        Adding a new stat: pass it here and display it in status.html.
        """
        character = session.get("character", {})
        class_name = character.get("class_name", "")

        # Pull class lore and icon from CLASSES — single source of truth
        cls_def    = CLASSES.get(class_name, {})
        class_lore = cls_def.get("lore", "")
        class_icon = cls_def.get("icon", "fa-shield-halved")

        return render_template(
            "status.html",
            character=character,
            class_icon=class_icon,
            class_lore=class_lore,
            hp=session.get("hp", character.get("max_hp", 100)),
            mp=session.get("mp", 0),
            mp_max=character.get("mp_max", 100),
            estus=session.get("estus", 0),
            estus_max=session.get("estus_max", 5),
            souls=session.get("souls", 0),
            gift=session.get("gift", "fading_soul"),
            classes=CLASSES,
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