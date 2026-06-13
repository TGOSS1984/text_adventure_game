"""
routes/game_routes.py

General game flow routes:
    /           — class selection screen
    /start      — POST: create character, apply gift, init session
    /game       — story chapter display and choice handling
    /ng_plus    — POST: begin New Game+, preserve class/ng_level, cap souls
    /death      — death screen
    /restart    — clear session and return to start
    /save       — persist session to disk
    /load       — restore session from disk
    /bestiary   — enemy/boss reference page
    /status     — player stats overview screen

Commit 2 — New Game+ additions:
    session['ng_plus']
        Integer tracking the current NG+ depth. 0 = first run, 1 = NG+, 2 = NG++.
        Persists across the /ng_plus route and is never reset by /restart
        (restart always returns to NG+0 since it clears the full session).
        Passed to generate_enemy() so combat.py can apply stat scaling.

    session['ng_plus_souls_carried']
        Souls carried into this NG+ run after the cap was applied. Stored for
        display purposes (status screen, death screen). Not used in combat logic.

    /ng_plus route:
        - Reads current ng_plus level and increments by 1.
        - Caps carried souls at NG_PLUS_SOUL_CAP (config.py). Any excess is
          discarded — this prevents players from immediately buying everything
          on NG+ entry with banked souls from optional content.
        - Preserves: char_class, ng_plus level, capped souls.
        - Resets: everything else (HP, MP, Estus, shop_bought, active effects,
          chapter, enemy state). This is intentional — NG+ is a fresh run of
          the story with harder enemies, not a continuation.
        - Does NOT re-apply the starting gift — that was a first-run choice.
          On NG+ the player starts without a gift bonus, which is consistent
          with starting from a position of strength (upgrades carried over).
        - Redirects to /start with the class pre-filled so the player sees
          the class select screen and can confirm before the run begins.
          This also gives a natural moment to see the NG+ indicator.

    show_ng_plus flag in /game GET:
        When the player reaches an ending chapter (100, 101, 102) and their
        session is still live (not yet restarted), show_ng_plus=True is passed
        to game.html so the template can render a "Begin Journey 2" button
        alongside the existing ending text. The button POSTs to /ng_plus.
        No changes to the chapter JSON files are needed.

    ng_plus passed to generate_enemy():
        game_routes.py reads session['ng_plus'] and passes it through to
        battle_manager.generate_enemy() whenever a battle chapter is entered.
        combat.py applies the scaling — game_routes.py never touches enemy stats
        directly (clean separation of concerns).
"""

from flask import render_template, request, redirect, url_for, session, flash
import random
from ..combat import BattleManager
from ..config import (
    NORMAL_BATTLE_BGS, BOSS_BATTLE_BGS, BOSS_BG_OVERRIDES, REST_BGS,
    GIFTS, DEFAULT_ESTUS, NG_PLUS_SOUL_CAP,
)
from ..models import Character
from ..classes import CLASSES
from ..save_load import save_game, load_game, has_save, delete_save
from ..enemies import ENEMIES, BOSSES
from ..story.story_engine import Story

# ── Ending chapter IDs — show 'Begin Journey 2' on these ─────────────────────
ENDING_CHAPTERS = {100, 101, 102}

story          = Story()
battle_manager = BattleManager()


def _reset_run_session(char_class, souls=0, ng_level=0):
    """
    Shared helper: initialise all run-specific session keys.

    Used by both /start (fresh run) and /ng_plus (NG+ run).
    Separating this into a helper prevents the two routes from drifting
    out of sync as new session keys are added in future commits.

    char_class — class name string (e.g. 'Knight')
    souls      — starting souls (0 for fresh runs, capped value for NG+)
    ng_level   — NG+ depth to write into session (0 for first run)
    """
    character = Character.create(char_class)
    if not character:
        return None

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
    session["souls"]               = souls
    session["estus_max"]           = DEFAULT_ESTUS
    session["shop_bought"]         = []
    session["boss_phase"]          = 1
    session["phase_changed"]       = False
    session["ng_plus"]             = ng_level
    # ── Active effect state ────────────────────────────────────────────────────
    session["dot_damage"]          = 0
    session["dot_turns"]           = 0
    session["dot_label"]           = ""
    session["buff_stat"]           = None
    session["buff_amount"]         = 0
    session["buff_turns"]          = 0
    session["buff_label"]          = ""
    session["shield_pct"]          = 0.0
    session["shield_turns"]        = 0
    # ── Shadow realm state ────────────────────────────────────────────────────
    session["secret_chapters"]     = []

    return character


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
            flash(
                "Class not selected or missing. Please return to the main menu.",
                "error"
            )
            return redirect(url_for("main.index"))

        # ── For NG+ re-entry: class is pre-filled, ng_level already set ───────
        # Read before _reset_run_session clears the session.
        ng_level      = session.get("ng_plus", 0)
        carried_souls = session.get("ng_plus_souls_carried", 0)

        delete_save()
        character = _reset_run_session(
            char_class,
            souls=carried_souls,
            ng_level=ng_level,
        )

        if not character:
            flash("Invalid character class.", "error")
            return redirect(url_for("main.index"))

        # ── Apply starting gift (first run only) ───────────────────────────────
        # On NG+ the player keeps their class but gets no gift bonus — they
        # already start with carried upgrades and carried souls.
        gift = (request.form.get("gift") or "fading_soul").strip()
        if ng_level == 0:
            session["gift"] = gift
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
                elif stat == "max_hp":
                    current = session["character"].get("max_hp", 0)
                    session["character"]["max_hp"] = current + amount
                    session["hp"] = session["character"]["max_hp"]
                elif mode == "set":
                    session["character"][stat] = amount
                else:
                    current = session["character"].get(stat, 0)
                    session["character"][stat] = round(current + amount, 4)
        else:
            # NG+ run — clear the carried_souls flag now that it's been applied
            session["gift"] = "fading_soul"
            session.pop("ng_plus_souls_carried", None)

        session.pop("_flashes", None)
        return redirect(url_for("main.game"))

    @blueprint.route("/ng_plus", methods=["POST"])
    def ng_plus():
        """
        Begin a New Game+ run.

        Reads the current ng_plus level, increments it, caps carried souls,
        and preserves the char_class. All other run state is cleared by
        _reset_run_session() when the player hits /start.

        We redirect to /start (not directly to /game) so the player sees the
        class select screen and can confirm their class before the run begins.
        The class is pre-filled via a hidden field in index.html when ng_level > 0.
        """
        current_ng   = session.get("ng_plus", 0)
        new_ng_level = current_ng + 1

        # Cap souls at NG_PLUS_SOUL_CAP — excess is discarded
        current_souls  = session.get("souls", 0)
        carried_souls  = min(current_souls, NG_PLUS_SOUL_CAP)
        discarded      = current_souls - carried_souls

        char_class = session.get("character", {}).get("char_class", "")
        if not char_class:
            flash("Could not determine class for New Game+. Please restart.", "error")
            return redirect(url_for("main.index"))

        # Store NG+ state before clearing session
        # These survive into /start where _reset_run_session reads them
        session["ng_plus"]               = new_ng_level
        session["ng_plus_souls_carried"] = carried_souls

        if discarded > 0:
            flash(
                f"🔥 Journey {new_ng_level + 1} begins. "
                f"{carried_souls} souls carried. "
                f"{discarded} souls faded beyond the threshold.",
                "info"
            )
        else:
            flash(
                f"🔥 Journey {new_ng_level + 1} begins. "
                f"{carried_souls} souls carried into the dark.",
                "info"
            )

        # Redirect to /start with class pre-filled
        # index.html should render a hidden form when ng_plus > 0 that
        # auto-submits to /start with the char_class — or the player
        # can re-select. Either way /start reads session['ng_plus'].
        return redirect(url_for("main.index"))

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

                # ── Pass ng_level to generate_enemy for NG+ scaling ───────────
                ng_level = session.get("ng_plus", 0)
                enemy    = battle_manager.generate_enemy(
                    boss=is_boss,
                    boss_name=boss_name,
                    ng_level=ng_level,
                )

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
        chapter_id  = session.get("chapter", 0)
        is_eligible = (
            not data.get("battle") and
            not data.get("boss") and
            not data.get("rest") and
            chapter_id not in [0, 100, 101, 102]
        )
        secret_chapters = session.get("secret_chapters", [])
        if not secret_chapters and is_eligible:
            all_story = [n for n in range(1, 100)
                         if n not in [7, 14, 20, 25, 34, 40, 45, 50, 54,
                                      59, 62, 65, 68, 71, 74, 76, 78, 80,
                                      82, 88, 93]]
            secret_chapters = random.sample(all_story, min(8, len(all_story)))
            session["secret_chapters"] = secret_chapters

        show_secret_map = is_eligible and chapter_id in secret_chapters

        # ── New Game+ — show 'Begin Journey N' on ending chapters ─────────────
        ng_level     = session.get("ng_plus", 0)
        show_ng_plus = chapter_id in ENDING_CHAPTERS

        return render_template(
            "game.html",
            chapter=data,
            hp=hp,
            character=session["character"],
            is_rest=bool(data.get("rest", False)),
            gift=session.get("gift", "fading_soul"),
            souls=session.get("souls", 0),
            show_secret_map=show_secret_map,
            show_ng_plus=show_ng_plus,
            ng_level=ng_level,
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
        ng_level = session.get("ng_plus", 0)
        return render_template("death.html", ng_level=ng_level)

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
        """
        character  = session.get("character", {})
        class_name = character.get("class_name", "")
        cls_def    = CLASSES.get(class_name, {})
        class_lore = cls_def.get("lore", "")
        class_icon = cls_def.get("icon", "fa-shield-halved")
        ng_level   = session.get("ng_plus", 0)

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
            ng_level=ng_level,
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