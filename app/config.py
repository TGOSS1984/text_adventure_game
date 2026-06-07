"""
config.py

Single source of truth for all game configuration constants.

Replaces scattered definitions previously in:
- combat.py  — MP_COST, MP_REGEN_ATTACK, COOLDOWN_TURNS, PHYS_PEN,
               PHASE2_DMG_MULT, PHASE2_HP_TRIGGER,
               PHASE1_WEIGHTS, PHASE2_WEIGHTS
- routes.py  — NORMAL_BATTLE_BGS, BOSS_BATTLE_BGS, SHOP_ITEMS
- routes.py  — hardcoded gift if/elif block in /start

Adding a new shop item : add one entry to SHOP_ITEMS.
Adding a new gift     : add one entry to GIFTS.
Changing a background : edit NORMAL_BATTLE_BGS or BOSS_BATTLE_BGS.
Tweaking combat value : edit the relevant constant. One place, zero hunting.

Gift effect fields:
    stat        — which session character key to modify (or special values
                  'estus', 'souls')
    amount      — value to add / set
    magic_stat  — optional override stat for magic damage_type classes
                  (e.g. iron_talisman boosts magic_defense for Mage)
    mode        — 'add' (default) or 'set'
    description — shown in flash message on apply (optional)
"""

# ── MP & special move ──────────────────────────────────────────────────────────
MP_COST         = 50    # MP cost to use a special move
MP_REGEN_ATTACK = 25    # MP gained per standard attack
COOLDOWN_TURNS  = 4     # turns before special move can be used again

# ── Estus heal amount ─────────────────────────────────────────────────────────
ESTUS_HEAL_PCT  = 0.70  # fraction of max_hp restored per flask

# ── Physical penetration ───────────────────────────────────────────────────────
# Physical attacks apply only PHYS_PEN x enemy/player physical defense.
# 0.55 = 55% of defense is applied; 45% is ignored.
PHYS_PEN = 0.55

# ── Boss soul reward bonus ────────────────────────────────────────────────────
BOSS_SOUL_BONUS = 0.50  # boss soul reward multiplied by this and rounded to 5

# ── Boss phase 2 ───────────────────────────────────────────────────────────────
PHASE2_DMG_MULT   = 1.20   # all phase 2 damage x1.20
PHASE2_HP_TRIGGER = 0.50   # phase 2 begins when boss HP <= 50%

# ── Enemy move probability weights ────────────────────────────────────────────
# Order: [attack, big_hit, flurry]
PHASE1_WEIGHTS = [0.60, 0.25, 0.15]   # attack high, big_hit mid, flurry rare
PHASE2_WEIGHTS = [0.30, 0.38, 0.32]   # attack low, big_hit high, flurry high

# ── Starting estus count ──────────────────────────────────────────────────────
DEFAULT_ESTUS = 5

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
# Adding a new item: add one entry here + one elif in routes.py /buy.
# The shop display, cost checks, and already-bought logic are all automatic.
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
    "hp_vessel_greater": {
        "name":        "Greater Vessel of Embers",
        "description": "Kindle your flame brighter. Max HP +30 (permanent).",
        "cost":        350,
        "icon":        "fas fa-heart-pulse",
        "repeatable":  False,
    },
    "dodge_pendant": {
        "name":        "Wraith-Step Pendant",
        "description": "Move like shadow. Dodge chance +10% (permanent).",
        "cost":        225,
        "icon":        "fas fa-person-running",
        "repeatable":  False,
    },
    "block_talisman": {
        "name":        "Ironwall Talisman",
        "description": "Brace against the storm. Blocked damage reduced by a further 10% (permanent).",
        "cost":        200,
        "icon":        "fas fa-shield",
        "repeatable":  False,
    },
    "crit_stone": {
        "name":        "Sharpened Crit Stone",
        "description": "Find the gap between breath and bone. Crit chance +10% (permanent).",
        "cost":        225,
        "icon":        "fas fa-crosshairs",
        "repeatable":  False,
    },
    "crit_lens": {
        "name":        "Executioner's Lens",
        "description": "Strike where it hurts most. Crit damage multiplier +0.25× (permanent).",
        "cost":        275,
        "icon":        "fas fa-eye",
        "repeatable":  False,
    },
}

# ── Starting gifts ────────────────────────────────────────────────────────────
# Adding a new gift: add one entry here. No changes needed in routes.py.
#
# stat       — session["character"] key to modify.
#              Special values: 'estus' modifies session estus+estus_max,
#                              'souls' modifies session souls directly.
# amount     — value added to the stat.
# magic_stat — if set, magic damage_type classes modify this stat instead.
#              e.g. iron_talisman gives magic_defense to Mage, defense to others.
# mode       — 'add' (default): stat += amount
#              'set': stat  = amount (for estus which sets both estus and estus_max)
GIFTS = {
    "estus_plus": {
        "name":   "Estus +1",
        "stat":   "estus",
        "amount": 6,
        "mode":   "set",
    },
    "hunters_charm": {
        "name":   "Hunter's Charm",
        "stat":   "crit_chance",
        "amount": 0.05,
        "mode":   "add",
    },
    "iron_talisman": {
        "name":       "Iron Talisman",
        "stat":       "defense",
        "magic_stat": "magic_defense",
        "amount":     3,
        "mode":       "add",
    },
    "witchs_ember": {
        "name":       "Witch's Ember",
        "stat":       "attack",
        "magic_stat": "magic_attack",
        "amount":     3,
        "mode":       "add",
    },
    "old_coin": {
        "name":   "Old Coin",
        "stat":   "souls",
        "amount": 200,
        "mode":   "set",
    },
    "fading_soul": {
        "name":   "Fading Soul",
        "stat":   None,   # no effect
        "amount": 0,
    },
}