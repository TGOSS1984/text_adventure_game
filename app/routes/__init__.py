"""
routes/__init__.py

Creates the single 'main' Blueprint and registers all route modules onto it.

All url_for('main.xxx') calls across templates continue to work unchanged.

Adding a new route group:
    1. Create routes/your_routes.py with a register(blueprint) function
    2. Import and call register(main) below — one line
"""

from flask import Blueprint, request, Response

main = Blueprint("main", __name__)


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