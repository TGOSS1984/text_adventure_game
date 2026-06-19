"""
routes/game_routes.py

General game flow routes:
    /                — class selection screen
    /start           — POST: create character, apply gift, init session
    /game            — story chapter display and choice handling
    /ng_plus         — POST: New Journey (new class, base stats, scaled enemies)
    /ng_plus_legacy  — POST: Bearer's Legacy (same class, inherited stats, scaled enemies)
    /death           — death screen
    /restart         — clear session and return to start
    /save            — persist session to disk
    /load            — restore session from disk
    /bestiary        — enemy/boss reference page
    /status          — player stats overview screen

Commit 2 — New Game+ additions:
    session['ng_plus'], session['ng_plus_mode'], session['ng_plus_souls_carried']
    Two routes: /ng_plus (New Journey) and /ng_plus_legacy (Bearer's Legacy).
    See route docstrings for full details.

Commit 3 — Run stats tracking:
    session['run_stats'] — dict tracking cumulative stats for the current run.
    Initialised in _reset_combat_state() so it resets on every new run
    (fresh start, New Journey NG+, Bearer's Legacy NG+).

    Keys:
        enemies_defeated  int  — regular enemy kills
        bosses_defeated   int  — boss kills
        bosses_list       list — names of bosses defeated (for completion %)
        damage_dealt      int  — total damage dealt to enemies
        damage_taken      int  — total damage taken (after reductions)
        estus_used        int  — Estus Flasks consumed
        specials_fired    int  — primary + secondary specials combined
        souls_earned      int  — cumulative souls earned this run
        chapters_visited  int  — story chapters passed through
        crits_landed      int  — critical hits landed

    chapters_visited is incremented in /game GET only when the chapter ID
    changes from the previously counted chapter, using session key
    'last_counted_chapter'. This prevents double-counting on redirects
    (rest chapters trigger a redirect-then-GET on the same chapter ID).

    All other stats are incremented in battle_routes.py via the
    _update_run_stat() and _append_run_stat_list() helpers defined there.

    run_stats is passed to death.html and game.html (ending chapters) so
    Commits 4 and 5 can display it without any further route changes.

Commit 8 — New class unlock system:
    player_record.py manages persistent cross-run unlock data in
    saves/player_record.json. Unlike savegame.json this file is NEVER
    deleted by /restart — unlocks survive across playthroughs.

    unlocked_names is loaded on every /index request and passed to the
    template so locked class cards can be rendered correctly.

    /start validates the chosen class is unlocked (guard against form tampering).

    Unlock triggers:
        Barbarian — fires in /game GET when an ending chapter (100/101/102)
                    is reached. unlock_class() is a no-op if already unlocked
                    so visiting the ending multiple times is safe.
        Samurai   — fires in battle_routes.py when Mesmereth is defeated.
        Wretch    — unlocked_by_default=True, always available.

    _reset_combat_state() gains four new keys:
        hot_dmg, hot_turns         — Barbarian Berserker Rage HoT
        parry_turns, parry_counter_pct — Samurai Iron Stance parry counter

    Note on Heroku: saves/player_record.json uses the filesystem, which is
    ephemeral on Heroku's free/eco tier. Unlocks persist within a dyno
    session but reset on dyno restart. Same limitation as savegame.json.
"""

from flask import render_template, request, redirect, url_for, session, flash, Response
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
from ..player_record import get_unlocked_names, unlock_class, increment_total_runs, get_total_runs

# ── Ending chapter IDs — show NG+ buttons on these ───────────────────────────
ENDING_CHAPTERS = {100, 101, 102}

# ── All boss names for completion % calculation ───────────────────────────────
# Used on the completion screen to show which bosses were missed.
# Update this list if new bosses are added to enemies.py.
ALL_BOSS_NAMES = list(BOSSES.keys())

story          = Story()
battle_manager = BattleManager()


def _blank_run_stats():
    """Return a fresh run_stats dict with all keys at zero/empty."""
    return {
        "enemies_defeated": 0,
        "bosses_defeated":  0,
        "bosses_list":      [],
        "damage_dealt":     0,
        "damage_taken":     0,
        "estus_used":       0,
        "specials_fired":   0,
        "souls_earned":     0,
        "chapters_visited": 0,
        "crits_landed":     0,
    }


def _cap_and_store_souls(current_ng):
    """
    Shared soul-capping logic for both NG+ routes.
    Reads session souls, applies NG_PLUS_SOUL_CAP, stores carried amount,
    flashes the appropriate message, and returns (new_ng_level, carried_souls).
    """
    new_ng_level  = current_ng + 1
    current_souls = session.get("souls", 0)
    carried_souls = min(current_souls, NG_PLUS_SOUL_CAP)
    discarded     = current_souls - carried_souls

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

    return new_ng_level, carried_souls


def _reset_combat_state(souls=0, ng_level=0):
    """
    Reset all combat and run-progression session keys WITHOUT touching
    session['character']. Used by /ng_plus_legacy (character dict survives)
    and internally by _reset_run_session (after it writes the character dict).

    Commit 3: run_stats and last_counted_chapter initialised here so they
    reset on every new run regardless of mode (fresh, New Journey, Legacy).

    Commit 8: hot_dmg, hot_turns, parry_turns, parry_counter_pct added for
    new class special effect session state.
    """
    session["chapter"]               = 0
    session["enemy"]                 = {}
    session["estus"]                 = DEFAULT_ESTUS
    session["mp"]                    = 0
    session["special_cooldown"]      = 0
    session["stunned"]               = False
    session["smoke_screen_active"]   = False
    session["souls"]                 = souls
    session["estus_max"]             = DEFAULT_ESTUS
    session["shop_bought"]           = []
    session["boss_phase"]            = 1
    session["phase_changed"]         = False
    session["ng_plus"]               = ng_level
    session["game_over"]             = False
    session["at_title"]              = False
    # ── Active effect state ───────────────────────────────────────────────────
    session["dot_damage"]            = 0
    session["dot_turns"]             = 0
    session["dot_label"]             = ""
    session["buff_stat"]             = None
    session["buff_amount"]           = 0
    session["buff_turns"]            = 0
    session["buff_label"]            = ""
    session["shield_pct"]            = 0.0
    session["shield_turns"]          = 0
    # Commit 8: new active effect state for Barbarian HoT and Samurai parry
    session["hot_dmg"]               = 0
    session["hot_turns"]             = 0
    session["parry_turns"]           = 0
    session["parry_counter_pct"]     = 0.0
    # ── Shadow realm state ────────────────────────────────────────────────────
    session["secret_chapters"]       = []
    session["shadow_realm_completed"]     = False
    # ── Run stats (Commit 3) ──────────────────────────────────────────────────
    session["run_stats"]             = _blank_run_stats()
    session["last_counted_chapter"]  = -1   # sentinel — no chapter counted yet


def _reset_run_session(char_class, souls=0, ng_level=0):
    """
    Build a fresh character dict and reset all session keys.
    Used by /start (fresh run and New Journey NG+).
    For Bearer's Legacy NG+, use _reset_combat_state() directly.
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

    _reset_combat_state(souls=souls, ng_level=ng_level)
    session["hp"] = session["character"]["max_hp"]

    return character


def _render_chapter(as_fragment=False):
    """
    Render whatever chapter session["chapter"] currently points to.

    This is the single source of truth for "what does the player see
    right now" — it's called both by a normal GET /game request, and by
    the POST branch of game() when an HTMX story-to-story transition
    qualifies for an in-place fragment swap instead of a full reload
    (see Commit 32). Keeping this logic in one place means the smooth
    HTMX path can never drift out of sync with what a plain GET would
    have shown for the same chapter — every flash message, secret-map
    eligibility check, and NG+/unlock side effect behaves identically
    either way.

    as_fragment=False (default) -> renders the full game.html page.
    as_fragment=True            -> renders only game_fragment.html,
                                    meant to be returned directly as the
                                    body of an HTMX response.

    Note: when as_fragment=True, this should only ever be called for a
    chapter confirmed (by the caller) to be neither rest nor battle —
    the one-time rest-restore branch below returns a redirect, which
    would be the wrong shape for an HTMX fragment response. The POST
    branch in game() guarantees this by checking next_data before
    deciding to call here with as_fragment=True, so the branch below is
    structurally unreachable in fragment mode rather than just
    defensively avoided.
    """
    chapter    = session.get("chapter", 0)
    data       = story.get_chapter(chapter)
    chapter_id = chapter

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

    # ── Commit 3: chapter visit tracking ──────────────────────────────────
    # Only count each chapter once — compare against last_counted_chapter
    # to avoid double-counting from the rest redirect.
    last_counted = session.get("last_counted_chapter", -1)
    if chapter_id != last_counted:
        stats = session.get("run_stats", _blank_run_stats())
        stats["chapters_visited"] = stats.get("chapters_visited", 0) + 1
        session["run_stats"]            = stats
        session["last_counted_chapter"] = chapter_id

    # ── Secret map icon ───────────────────────────────────────────────────
    is_eligible = (
        not data.get("battle") and
        not data.get("boss") and
        not data.get("rest") and
        chapter_id not in [0, 100, 101, 102] and
        not session.get("shadow_realm_completed", False)
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

    # ── NG+ buttons and run stats on ending chapters ───────────────────────
    ng_level     = session.get("ng_plus", 0)
    show_ng_plus = chapter_id in ENDING_CHAPTERS

    # ── Barbarian + Hunter unlock on game completion ──────────────────────
    # unlock_class() is a no-op if already unlocked, so repeated visits
    # to ending chapters are safe. increment_total_runs() always fires.
    # Barbarian: unlocked on any story completion (base game or NG+).
    # Hunter: unlocked on completing a NG+ run (ng_level > 0).
    if chapter_id in ENDING_CHAPTERS:
        newly_unlocked_barb = unlock_class("Barbarian")
        if newly_unlocked_barb:
            flash("💢 The Barbarian class has been unlocked!", "info")

        if ng_level > 0:
            newly_unlocked_hunter = unlock_class("Hunter")
            if newly_unlocked_hunter:
                flash("🩸 The Hunter class has been unlocked!", "info")

        increment_total_runs()

    # Build completion data for the ending/status screens
    run_stats      = session.get("run_stats", _blank_run_stats())
    bosses_missed  = [
        b for b in ALL_BOSS_NAMES
        if b not in run_stats.get("bosses_list", [])
    ]
    total_bosses   = len(ALL_BOSS_NAMES)
    bosses_hit     = len(run_stats.get("bosses_list", []))
    completion_pct = round((bosses_hit / total_bosses) * 100) if total_bosses else 0

    template_args = dict(
        chapter=data,
        hp=hp,
        character=session["character"],
        is_rest=bool(data.get("rest", False)),
        gift=session.get("gift", "fading_soul"),
        souls=session.get("souls", 0),
        show_secret_map=show_secret_map,
        show_ng_plus=show_ng_plus,
        ng_level=ng_level,
        run_stats=run_stats,
        bosses_missed=bosses_missed,
        completion_pct=completion_pct,
        total_bosses=total_bosses,
    )

    if as_fragment:
        return render_template("game_fragment.html", **template_args)

    # Preload the small rest-background pool so the random pick on the
    # next /rest chapter is already cached. Mirrors the same pattern
    # used in battle_routes.py for battle backgrounds.
    template_args["preload_list"] = [url_for("static", filename=bg) for bg in REST_BGS]
    return render_template("game.html", **template_args)


def register(blueprint):
    """Attach all game routes to the given blueprint."""

    @blueprint.route("/")
    def index():
        # Commit 8: load unlocked class names for carousel filtering
        unlocked_names = get_unlocked_names()

        # Marks that the player is sitting at the title/character-select
        # screen right now. Visiting here does NOT clear session["character"]
        # (a mid-run player might land here via "Return to Title" without
        # saving, or just be on a fresh browser tab with an old session
        # cookie) -- but it does mean Bestiary's "Continue Story" link
        # shouldn't be allowed to resume that run from here. The title
        # screen's own "Resume Journey" button (/load) is the intended way
        # back in, and /game clears this flag the moment it's reached, so
        # that path -- and any other genuine resume -- works exactly as
        # before. See bestiary()'s mid_run check below.
        session["at_title"] = True

        return render_template(
            "index.html",
            classes=CLASSES,
            unlocked_names=unlocked_names,
            has_save=has_save(),
            total_runs=get_total_runs(),
        )

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

        # Commit 8: guard against form tampering — verify class is unlocked
        unlocked_names = get_unlocked_names()
        if char_class not in unlocked_names:
            flash(
                f"{char_class} is not yet unlocked. "
                f"Complete the required conditions first.",
                "error"
            )
            return redirect(url_for("main.index"))

        # ── For NG+ re-entry: class is pre-filled, ng_level already set ───────
        # Read before _reset_run_session clears the session.
        ng_level      = session.get("ng_plus", 0)
        carried_souls = session.get("ng_plus_souls_carried", 0)
        ng_mode       = session.get("ng_plus_mode", "new_journey")

        delete_save()

        # Legacy mode bypasses /start entirely (redirects to /game directly),
        # but guard here in case someone navigates back to /start manually.
        if ng_level > 0 and ng_mode == "legacy":
            session["hp"] = session["character"].get("max_hp", 100)
            session.pop("ng_plus_souls_carried", None)
            session.pop("ng_plus_mode", None)
            session.pop("_flashes", None)
            return redirect(url_for("main.game"))

        character = _reset_run_session(
            char_class,
            souls=carried_souls,
            ng_level=ng_level,
        )

        if not character:
            flash("Invalid character class.", "error")
            return redirect(url_for("main.index"))

        # ── Apply starting gift (first run only) ───────────────────────────────
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
            session.pop("ng_plus_mode", None)

        session.pop("_flashes", None)
        return redirect(url_for("main.game"))

    # ── New Game+ — New Journey ────────────────────────────────────────────────

    @blueprint.route("/ng_plus", methods=["POST"])
    def ng_plus():
        """
        Begin a New Journey run.

        Player chooses a new class on the index screen. Character resets to
        base stats for that class. Enemies scale up. Souls capped and carried.
        No gift applied on NG+ runs.
        """
        current_ng = session.get("ng_plus", 0)

        char_class = session.get("character", {}).get("char_class", "")
        if not char_class:
            flash("Could not determine class. Please restart.", "error")
            return redirect(url_for("main.index"))

        _cap_and_store_souls(current_ng)
        session["ng_plus_mode"] = "new_journey"
        return redirect(url_for("main.index"))

    # ── New Game+ — Bearer's Legacy ────────────────────────────────────────────

    @blueprint.route("/ng_plus_legacy", methods=["POST"])
    def ng_plus_legacy():
        """
        Begin a Bearer's Legacy run.

        Same class. All upgraded stats preserved. shop_bought resets.
        Enemies scale up. Souls capped and carried.
        Redirects directly to /game — no class select needed.
        """
        current_ng = session.get("ng_plus", 0)

        char_class = session.get("character", {}).get("char_class", "")
        if not char_class:
            flash("Could not determine class. Please restart.", "error")
            return redirect(url_for("main.index"))

        new_ng_level, carried_souls = _cap_and_store_souls(current_ng)
        session["ng_plus_mode"]  = "legacy"
        inherited_max_hp         = session["character"].get("max_hp", 100)

        _reset_combat_state(souls=carried_souls, ng_level=new_ng_level)
        session["hp"]   = inherited_max_hp
        session["gift"] = session.get("gift", "fading_soul")

        session.pop("_flashes", None)
        return redirect(url_for("main.game"))

    # ── Main game loop ─────────────────────────────────────────────────────────

    @blueprint.route("/game", methods=["GET", "POST"])
    def game():
        if session.get("game_over"):
            # The run already ended (player HP hit 0 in battle — see
            # battle_routes.py). session["character"]/["chapter"] are
            # still sitting there from before death, so without this
            # check, navigating back to /game from anywhere (Bestiary's
            # "Continue Story" link, browser back button, a bookmarked
            # URL) would silently resume the dead run exactly where it
            # left off. Bounce back to the death screen instead,
            # regardless of how /game was reached.
            return redirect(url_for("main.death"))

        # The player is genuinely back in the run now -- whether they just
        # came from /load, a fresh /start, or anywhere else. Clears the
        # flag set by index() so Bestiary's "Continue Story" correctly
        # works again for the rest of this session, until they return to
        # the title screen again.
        session["at_title"] = False

        if request.method == "POST":
            # Determine the CURRENT chapter (the one being left) before
            # mutating session, so we know whether this is a plain
            # story-to-story transition eligible for a smooth in-place
            # HTMX swap, versus one that should still do a full page/
            # route transition exactly as before (entering/leaving a
            # rest chapter, or starting a battle).
            current_chapter_id = session.get("chapter", 0)
            current_data       = story.get_chapter(current_chapter_id)
            current_is_rest    = bool(current_data.get("rest", False))

            choice       = request.form["choice"]
            next_chapter = story.choose_path(choice)
            next_data    = story.get_chapter(next_chapter)

            session["choices"] = next_data.get("choices", [])

            is_htmx = request.headers.get("HX-Request") == "true"

            if next_data.get("battle"):
                is_boss   = next_data.get("boss", False)
                boss_name = next_data.get("boss_name") if is_boss else None
                if is_boss and boss_name in BOSS_BG_OVERRIDES:
                    session["battle_bg"] = BOSS_BG_OVERRIDES[boss_name]
                else:
                    bg_pool = BOSS_BATTLE_BGS if is_boss else NORMAL_BATTLE_BGS
                    session["battle_bg"] = random.choice(bg_pool)

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

                if is_htmx:
                    # A bare redirect() here would just hand HTMX a 3xx
                    # it auto-follows, swapping the *entire* destination
                    # page's HTML into #story-content. HX-Redirect tells
                    # HTMX to do a real top-level navigation instead —
                    # the browser ends up exactly where it would have
                    # with a normal redirect, full reload included.
                    resp = Response("")
                    resp.headers["HX-Redirect"] = url_for("main.battle")
                    return resp
                return redirect(url_for("main.battle"))

            next_is_rest = bool(next_data.get("rest", False))
            session["chapter"] = next_chapter

            if is_htmx and not current_is_rest and not next_is_rest:
                # Smooth path: plain story chapter -> plain story
                # chapter. Render just the inner fragment so HTMX swaps
                # #story-content in place, leaving the persistent
                # video/audio shell in game.html completely untouched —
                # this is the actual fix for the per-chapter stutter.
                return _render_chapter(as_fragment=True)

            if is_htmx:
                # Rest is involved on one end or the other — still a
                # deliberate full reload exactly like before (the
                # background is genuinely supposed to change), just
                # expressed as HX-Redirect so HTMX navigates instead of
                # trying to swap an auto-followed redirect's full HTML
                # into #story-content.
                resp = Response("")
                resp.headers["HX-Redirect"] = url_for("main.game")
                return resp

            # No-JS / non-HTMX fallback — completely unchanged behaviour.
            return redirect(url_for("main.game"))

        return _render_chapter(as_fragment=False)


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
        ng_level  = session.get("ng_plus", 0)
        run_stats = session.get("run_stats", _blank_run_stats())
        return render_template(
            "death.html",
            ng_level=ng_level,
            run_stats=run_stats,
        )

    @blueprint.route("/bestiary")
    def bestiary():
        # game_over guards the death-screen exploit (see Commit 35).
        # at_title guards this one: visiting / (title/character-select)
        # does NOT clear session["character"] -- a player might land there
        # via "Return to Title" without saving, or just on an old browser
        # tab -- so mid_run alone would still be True and "Continue Story"
        # would resume that run. The save/load mechanism (the title
        # screen's "Resume Journey" button) is the intended way back in;
        # this just closes the same-class shortcut through Bestiary.
        mid_run = (
            bool(session.get("character"))
            and not session.get("game_over", False)
            and not session.get("at_title", False)
        )
        return render_template(
            "bestiary.html",
            enemies=ENEMIES,
            bosses=BOSSES,
            classes=CLASSES,
            unlocked_names=get_unlocked_names(),
            mid_run=mid_run,
        )

    @blueprint.route("/status")
    def status():
        """
        Player status screen — reads live session values so all
        shop upgrades, gift bonuses, and current HP/MP are reflected.
        Adding a new stat: pass it here and display it in status.html.
        """
        character  = session.get("character", {})
        class_name = character.get("class_name", "")

        # Pull class lore and icon from CLASSES — single source of truth
        cls_def    = CLASSES.get(class_name, {})
        class_lore = cls_def.get("lore", "")
        class_icon = cls_def.get("icon", "fa-shield-halved")
        ng_level   = session.get("ng_plus", 0)
        ng_mode    = session.get("ng_plus_mode", "new_journey")
        run_stats  = session.get("run_stats", _blank_run_stats())

        # Completion tracking for status screen
        bosses_hit     = len(run_stats.get("bosses_list", []))
        total_bosses   = len(ALL_BOSS_NAMES)
        completion_pct = round((bosses_hit / total_bosses) * 100) if total_bosses else 0

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
            ng_mode=ng_mode,
            run_stats=run_stats,
            bosses_hit=bosses_hit,
            total_bosses=total_bosses,
            completion_pct=completion_pct,
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