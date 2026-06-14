"""
routes/shop_routes.py

Shop routes:
    /shop  — GET: display purchasable items
    /buy   — POST: process a purchase and apply stat effect to session

NG+ dodge / block caps (added alongside DODGE_BONUS_CAP / BLOCK_BONUS_CAP in config.py):
    dodge_pendant and block_talisman reset with shop_bought each NG+ run, so
    they stack indefinitely across playthroughs. The cap is enforced here at
    purchase time by comparing the current session stat against the class's
    original base stat (looked up from classes.py via char_class).

    If the cap has already been reached — because the player bought the item in
    previous NG+ runs — the item shows as already_bought in the shop and the
    /buy route rejects the purchase with a clear message.
"""

from flask import render_template, request, redirect, url_for, session, flash
from ..config import SHOP_ITEMS, DEFAULT_ESTUS, DODGE_BONUS_CAP, BLOCK_BONUS_CAP
from ..classes import get_class


def _dodge_at_cap(character: dict) -> bool:
    """
    Return True if this character's dodge_chance has already reached the
    lifetime cap (class base + DODGE_BONUS_CAP). Looks up the original base
    stat from classes.py so accumulated NG+ bonuses don't skew the check.
    """
    base_cls = get_class(character.get("char_class", ""))
    if not base_cls:
        return False
    base_dodge = base_cls["dodge_chance"]
    current    = character.get("dodge_chance", base_dodge)
    return round(current - base_dodge, 6) >= DODGE_BONUS_CAP


def _block_at_cap(character: dict) -> bool:
    """
    Return True if this character's block_multiplier has already reached the
    lifetime floor (class base - BLOCK_BONUS_CAP). Lower block_multiplier
    means more damage blocked, so the cap is a minimum, not a maximum.
    """
    base_cls = get_class(character.get("char_class", ""))
    if not base_cls:
        return False
    base_block = base_cls["block_multiplier"]
    current    = character.get("block_multiplier", base_block)
    return round(base_block - current, 6) >= BLOCK_BONUS_CAP


def register(blueprint):
    """Attach shop routes to the given blueprint."""

    @blueprint.route("/shop")
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

            # Treat dodge/block as already_bought when the lifetime cap is
            # reached — even if shop_bought was reset for this NG+ run.
            if key == "dodge_pendant" and _dodge_at_cap(character):
                already_bought = True
            if key == "block_talisman" and _block_at_cap(character):
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

    @blueprint.route("/buy", methods=["POST"])
    def buy():
        item_key = request.form.get("item_key", "").strip()

        if item_key not in SHOP_ITEMS:
            flash("Unknown item.", "error")
            return redirect(url_for("main.shop"))

        item      = SHOP_ITEMS[item_key]
        souls     = session.get("souls", 0)
        bought    = session.get("shop_bought", [])
        character = session.get("character", {})
        estus     = session.get("estus", 0)
        estus_max = session.get("estus_max", DEFAULT_ESTUS)

        if not item["repeatable"] and item_key in bought:
            flash(f"You have already purchased {item['name']}.", "error")
            return redirect(url_for("main.shop"))

        if item_key == "estus_refill" and estus >= estus_max:
            flash("Your Estus Flasks are already full.", "error")
            return redirect(url_for("main.shop"))

        # ── NG+ lifetime cap guards ────────────────────────────────────────────
        # These fire when shop_bought has been reset for a new NG+ run but the
        # player has already hit their cap from previous playthroughs.
        if item_key == "dodge_pendant" and _dodge_at_cap(character):
            flash("Your footwork has reached its limit — dodge cannot improve further.", "error")
            return redirect(url_for("main.shop"))

        if item_key == "block_talisman" and _block_at_cap(character):
            flash("Your guard is already as strong as your body allows — block cannot improve further.", "error")
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

        elif item_key == "hp_vessel_greater":
            session["character"]["max_hp"] += 30
            session["hp"] = min(session.get("hp", 0) + 30, session["character"]["max_hp"])
            session["shop_bought"] = bought + [item_key]
            flash(f"❤️ Max HP increased by 30. ({item['cost']} souls spent)", "info")

        elif item_key == "dodge_pendant":
            base_cls   = get_class(character.get("char_class", ""))
            base_dodge = base_cls["dodge_chance"] if base_cls else 0
            current    = character.get("dodge_chance", base_dodge)
            # Clamp so floating-point drift can never sneak past the cap
            new_dodge  = round(min(current + 0.05, base_dodge + DODGE_BONUS_CAP), 4)
            session["character"]["dodge_chance"] = new_dodge
            session["shop_bought"] = bought + [item_key]
            flash(f"💨 Dodge chance increased by 5%. ({item['cost']} souls spent)", "info")

        elif item_key == "block_talisman":
            base_cls   = get_class(character.get("char_class", ""))
            base_block = base_cls["block_multiplier"] if base_cls else 0.5
            current    = character.get("block_multiplier", base_block)
            # Clamp so floating-point drift can never sneak below the floor
            new_block  = round(max(current - 0.05, base_block - BLOCK_BONUS_CAP), 4)
            session["character"]["block_multiplier"] = new_block
            session["shop_bought"] = bought + [item_key]
            flash(f"🛡️ Block damage reduction improved by 5%. ({item['cost']} souls spent)", "info")

        elif item_key == "crit_stone":
            current = session["character"].get("crit_chance", 0)
            session["character"]["crit_chance"] = round(min(current + 0.05, 0.95), 4)
            session["shop_bought"] = bought + [item_key]
            flash(f"🎯 Crit chance increased by 5%. ({item['cost']} souls spent)", "info")

        elif item_key == "crit_lens":
            current = session["character"].get("crit_multiplier", 1.5)
            session["character"]["crit_multiplier"] = round(min(current + 0.25, 3.0), 4)
            session["shop_bought"] = bought + [item_key]
            flash(f"💥 Crit damage multiplier increased by 0.25×. ({item['cost']} souls spent)", "info")

        session.modified = True
        return redirect(url_for("main.shop"))