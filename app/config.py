"""
config.py

Single source of truth for all game configuration constants.

Replaces scattered definitions previously in:
- combat.py  — MP_COST, MP_REGEN_ATTACK, COOLDOWN_TURNS, PHYS_PEN,
               PHASE2_DMG_MULT, PHASE2_HP_TRIGGER,
               PHASE1_WEIGHTS, PHASE2_WEIGHTS
- routes.py  — NORMAL_BATTLE_BGS, BOSS_BATTLE_BGS, SHOP_ITEMS

Adding a new shop item : add one entry to SHOP_ITEMS.
Changing a battle background pool : edit the relevant list.
Tweaking any combat value : one place, zero hunting.
"""

# ── MP & special move ──────────────────────────────────────────────────────────
MP_COST         = 50    # MP cost to use a special move
MP_REGEN_ATTACK = 25    # MP gained per standard attack
COOLDOWN_TURNS  = 4     # turns before special move can be used again

# ── Physical penetration ───────────────────────────────────────────────────────
# Physical attacks apply only PHYS_PEN × enemy/player physical defense.
# 0.55 = 55% of defense is applied; 45% is ignored.
# Prevents armoured enemies from being unkillable walls.
PHYS_PEN = 0.55

# ── Boss phase 2 ───────────────────────────────────────────────────────────────
PHASE2_DMG_MULT   = 1.20   # all phase 2 damage ×1.20
PHASE2_HP_TRIGGER = 0.50   # phase 2 begins when boss HP ≤ 50%

# ── Enemy move probability weights ────────────────────────────────────────────
# Order: [attack, big_hit, flurry]
PHASE1_WEIGHTS = [0.60, 0.25, 0.15]   # attack ↑, big_hit mid, flurry rare
PHASE2_WEIGHTS = [0.30, 0.38, 0.32]   # attack ↓, big_hit ↑, flurry ↑↑

# ── Battle backgrounds ────────────────────────────────────────────────────────
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

# ── Shop catalogue ────────────────────────────────────────────────────────────
SHOP_ITEMS = {
    "estus_refill": {
        "name":        "Estus Refill",
        "description": "Restore all Estus Flasks to full.",
        "cost":        150,
        "icon":        "fas fa-flask",
        "repeatable":  True,
    },
    "attack_shard": {
        "name":        "Cracked Red Shard",
        "description": "Sharpen your weapon. Attack +3 (permanent).",
        "cost":        200,
        "icon":        "fas fa-fire-flame-curved",
        "repeatable":  False,
    },
    "defense_shard": {
        "name":        "Cracked Blue Shard",
        "description": "Harden your resolve. Defense +3 (permanent).",
        "cost":        175,
        "icon":        "fas fa-shield-halved",
        "repeatable":  False,
    },
    "hp_vessel": {
        "name":        "Vessel of Embers",
        "description": "Kindle your flame. Max HP +20 (permanent).",
        "cost":        250,
        "icon":        "fas fa-heart",
        "repeatable":  False,
    },
}