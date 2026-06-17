"""
routes/__init__.py

Creates the single 'main' Blueprint and registers all route modules onto it.

All url_for('main.xxx') calls across templates continue to work unchanged.

Adding a new route group:
    1. Create routes/your_routes.py with a register(blueprint) function
    2. Import and call register(main) below — one line
"""

from flask import Blueprint, request, Response, session, redirect, url_for, flash

main = Blueprint("main", __name__)


# ── Session expiry guard ───────────────────────────────────────────────────
# Several routes/templates read session["character"][...] directly rather
# than via .get() (mutating stats, reading max_hp, etc). If the session
# cookie is gone — browser closed (default Flask session is non-permanent
# and dies with the browser), cookie cleared, or a stale link opened in a
# fresh browser — session["character"] doesn't exist and those routes throw
# a raw KeyError -> 500 instead of failing gracefully.
#
# This runs before every request and bounces anyone hitting a run-only route
# without an active character back to the title screen with an explanation,
# instead of a crash or blank page.
#
# Routes intentionally NOT in this set: "main.index", "main.start" (these
# are how a run begins, so naturally don't require one yet), "main.restart",
# "main.save", "main.load", "main.bestiary" (all already session.get()-safe
# and meant to be reachable without an active run).
_REQUIRES_ACTIVE_RUN = {
    "main.game",
    "main.battle",
    "main.shop",
    "main.buy",
    "main.ng_plus",
    "main.ng_plus_legacy",
    "main.enter_shadow_realm",
    "main.leave_shadow_realm",
    "main.death",
    "main.status",
}


@main.before_request
def _guard_active_run():
    if request.endpoint not in _REQUIRES_ACTIVE_RUN:
        return None
    if not session.get("character"):
        flash(
            "Your journey was interrupted — the session expired or was lost. "
            "Please begin again.",
            "error",
        )
        return redirect(url_for("main.index"))
    return None


# ── Cache control — applied to every response ─────────────────────────────────
@main.after_request
def no_cache(resp):
    resp.headers["Cache-Control"] = "no-store"
    return resp


# ── Register route modules ────────────────────────────────────────────────────
from . import game_routes, battle_routes, shop_routes  # noqa: E402

game_routes.register(main)
battle_routes.register(main)
shop_routes.register(main)