"""
routes/shop_routes.py

Shop routes:
    /shop  — GET: display purchasable items
    /buy   — POST: process a purchase and apply stat effect to session
"""

from flask import render_template, request, redirect, url_for, session, flash
from ..config import SHOP_ITEMS, DEFAULT_ESTUS


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
        estus     = session.get("estus", 0)
        estus_max = session.get("estus_max", DEFAULT_ESTUS)

        if not item["repeatable"] and item_key in bought:
            flash(f"You have already purchased {item['name']}.", "error")
            return redirect(url_for("main.shop"))

        if item_key == "estus_refill" and estus >= estus_max:
            flash("Your Estus Flasks are already full.", "error")
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
            current = session["character"].get("dodge_chance", 0)
            session["character"]["dodge_chance"] = round(min(current + 0.10, 0.95), 4)
            session["shop_bought"] = bought + [item_key]
            flash(f"💨 Dodge chance increased by 10%. ({item['cost']} souls spent)", "info")

        elif item_key == "block_talisman":
            current = session["character"].get("block_multiplier", 0.5)
            session["character"]["block_multiplier"] = round(max(current - 0.10, 0.05), 4)
            session["shop_bought"] = bought + [item_key]
            flash(f"🛡️ Block damage reduction improved by 10%. ({item['cost']} souls spent)", "info")

        elif item_key == "crit_stone":
            current = session["character"].get("crit_chance", 0)
            session["character"]["crit_chance"] = round(min(current + 0.10, 0.95), 4)
            session["shop_bought"] = bought + [item_key]
            flash(f"🎯 Crit chance increased by 10%. ({item['cost']} souls spent)", "info")

        elif item_key == "crit_lens":
            current = session["character"].get("crit_multiplier", 1.5)
            session["character"]["crit_multiplier"] = round(min(current + 0.25, 3.0), 4)
            session["shop_bought"] = bought + [item_key]
            flash(f"💥 Crit damage multiplier increased by 0.25×. ({item['cost']} souls spent)", "info")

        session.modified = True
        return redirect(url_for("main.shop"))