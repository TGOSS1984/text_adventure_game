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

─── Commit 1 — Soul Economy Rebalance ───────────────────────────────────────────
SOUL_REWARD_MULTIPLIER:
    All boss soul_reward values in enemies.py have been reduced by 40% from their
    original values (rounded to nearest 5). This constant documents that scaling
    factor for future reference. If further tuning is needed, adjust enemies.py
    directly — this constant is informational, not applied at runtime.

    Reasoning: pre-rebalance, a main-path player finished with ~112% surplus over
    total shop cost. Target is ~25% surplus on main path — enough to buy everything
    comfortably without trivialising the economy. Full-completion runs (both branches
    + shadow realm) will have a larger surplus, which is intentional: optional content
    should feel rewarding. That surplus is controlled at NG+ entry via NG_PLUS_SOUL_CAP.

NG_PLUS_SOUL_CAP:
    Maximum souls carried into a New Game+ run. Any souls above this threshold are
    discarded on NG+ entry. Set to 600 = ~28% of total permanent shop value (2170).
    Gives a 2–3 item head start without allowing players to immediately buy everything.
    Adjust here only — applied in game_routes.py /ng_plus route.

SHOP_ITEM prices increased ~15% on permanent upgrade items (Estus Refill unchanged).
    Reasoning: shop was too cheap relative to soul income. With boss rewards reduced
    40%, prices needed a modest increase to keep each purchase feeling like a decision.
──────────────────────────────────────────────────────────────────────────────────
"""

# ── MP & special move ──────────────────────────────────────────────────────────
MP_COST           = 50    # MP cost to use a primary special move
MP_COST_SECONDARY = 35    # MP cost to use a secondary special move
MP_REGEN_ATTACK   = 25    # MP gained per standard attack
COOLDOWN_TURNS    = 4     # turns before special move can be used again (shared cooldown)

# ── Active effect flavour text ─────────────────────────────────────────────────
# Keys match the special2_dot_label field in classes.py.
# {dmg} is substituted at runtime.
DOT_TICK_MESSAGES = {
    "bleed":  "🩸 Bleeding for {dmg} damage!",
    "poison": "☠️ Poison deals {dmg} damage!",
}

# Shown in the battle log when a buff or shield expires naturally.
BUFF_EXPIRE_MESSAGES = {
    "war_cry":   "⚔️ War Cry fades — attack returns to normal.",
    "nullfield": "🔮 Nullfield dissipates — you are exposed once more.",
}

# ── Estus heal amount ──────────────────────────────────────────────────────────
ESTUS_HEAL_PCT = 0.70  # fraction of max_hp restored per flask

# ── Physical penetration ───────────────────────────────────────────────────────
# Physical attacks apply only PHYS_PEN x enemy/player physical defense.
# 0.55 = 55% of defense is applied; 45% is ignored.
PHYS_PEN = 0.55

# ── Boss soul reward bonus ─────────────────────────────────────────────────────
BOSS_SOUL_BONUS = 0.50  # boss soul reward multiplied by this and rounded to 5

# ── Boss phase 2 ───────────────────────────────────────────────────────────────
PHASE2_DMG_MULT   = 1.20   # all phase 2 damage ×1.20
PHASE2_HP_TRIGGER = 0.50   # phase 2 begins when boss HP <= 50%

# ── Enemy move probability weights ────────────────────────────────────────────
# Order: [attack, big_hit, flurry]
PHASE1_WEIGHTS = [0.60, 0.25, 0.15]   # attack high, big_hit mid, flurry rare
PHASE2_WEIGHTS = [0.40, 0.40, 0.20]   # more likely to trigger bigger hits

# ── Starting estus count ───────────────────────────────────────────────────────
DEFAULT_ESTUS = 5

# ── Soul economy ──────────────────────────────────────────────────────────────
# Commit 1: documented reduction factor applied to enemies.py boss rewards.
# Informational — not applied at runtime. See enemies.py for live values.
SOUL_REWARD_MULTIPLIER = 0.60   # boss rewards reduced to 60% of original values

# ── New Game+ soul carryover cap ───────────────────────────────────────────────
# Commit 1 (prep for Commit 2 — NG+).
# Souls above this threshold are discarded on entering a New Game+ run.
# 600 = ~28% of total permanent shop value. Gives a 2–3 item head start.
# To make NG+ harder/easier, adjust this single value.
NG_PLUS_SOUL_CAP = 600

# ── New Game+ enemy scaling ────────────────────────────────────────────────────
# All values are additive per level: NG+1 = base × (1 + SCALE), NG+2 = base × (1 + 2×SCALE).
# Adjust these constants only — scaling is applied in combat.py at enemy load time.
NG_PLUS_HP_SCALE   = 0.35   # +35% HP per NG+ level (all enemies)
NG_PLUS_ATK_SCALE  = 0.20   # +20% per NG+ level — applied to both attack AND magic_attack
NG_PLUS_DEF_SCALE  = 0.15   # +15% per NG+ level — applied to both defense AND magic_defense
NG_PLUS_SOUL_SCALE = 0.25   # +25% soul reward per NG+ level

# ── Battle backgrounds ─────────────────────────────────────────────────────────
NORMAL_BATTLE_BGS = [
    "images/areas/undead_settlement.jpg",
    "images/areas/high_walls.jpg",
    "images/areas/irithyl.jpg",
    "images/areas/bolateria.jpg",
    "images/areas/anor_londo.jpg",
    "images/areas/ariandel.jpg",
    "images/areas/battle_lotf.jpeg",
    "images/areas/battle_lotf_2.jpg",
    "images/areas/halls.jpg",
    "images/areas/irithyl_2.jpg",
    "images/areas/irithyl_3.jpg",
    "images/areas/limgrave.jpg",
    "images/areas/lothric_castle.jpg",
    "images/areas/lothric_corridors.jpg",
    "images/areas/marshes.jpeg",
    "images/areas/ringed_city_2.jpg",
    "images/areas/shadow_of_erdtree.png",
]
BOSS_BATTLE_BGS = [
    "images/areas/ringed_city.jpg",
    "images/areas/stormveil.jpg",
    "images/areas/erdtree.jpg",
    "images/areas/rotted_tree.jpg",
]

# ── Per-boss background overrides ─────────────────────────────────────────────
# If a boss name appears here, this background is used instead of a random
# selection from BOSS_BATTLE_BGS. Add any boss name from enemies.py.
BOSS_BG_OVERRIDES = {
    "Cindergloom": "images/areas/fiery_end.jpeg",
}

# ── Rest / bonfire backgrounds ─────────────────────────────────────────────────
# One is picked randomly each time a rest chapter is entered.
# Add any image from static/images/areas/ here.
REST_BGS = [
    "images/areas/firelink.jpg",
    "images/areas/bonfire2.jpg",
    "images/areas/bonfire3.jpg",
    "images/areas/bonfire4.jpg",
    "images/areas/bonfire5.jpg",
]

# ── Shop catalogue ────────────────────────────────────────────────────────────
# Adding a new item: add one entry here + one elif in routes.py /buy.
# The shop display, cost checks, and already-bought logic are all automatic.
#
# Commit 1 price changes (permanent upgrades increased ~15%):
#   Cracked Red Shard:       200 -> 225
#   Cracked Blue Shard:      175 -> 200
#   Vessel of Embers:        250 -> 275
#   Greater Vessel of Embers:350 -> 400
#   Wraith-Step Pendant:     225 -> 260
#   Ironwall Talisman:       200 -> 225
#   Sharpened Crit Stone:    225 -> 260
#   Executioner's Lens:      275 -> 325
#   Estus Refill: unchanged at 150 (consumable, not a permanent upgrade)
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
        "cost":        225,
        "icon":        "fas fa-fire-flame-curved",
        "repeatable":  False,
    },
    "defense_shard": {
        "name":        "Cracked Blue Shard",
        "description": "Harden your resolve. Defense +3 (permanent).",
        "cost":        200,
        "icon":        "fas fa-shield-halved",
        "repeatable":  False,
    },
    "hp_vessel": {
        "name":        "Vessel of Embers",
        "description": "Kindle your flame. Max HP +20 (permanent).",
        "cost":        275,
        "icon":        "fas fa-heart",
        "repeatable":  False,
    },
    "hp_vessel_greater": {
        "name":        "Greater Vessel of Embers",
        "description": "Kindle your flame brighter. Max HP +30 (permanent).",
        "cost":        400,
        "icon":        "fas fa-heart-pulse",
        "repeatable":  False,
    },
    "dodge_pendant": {
        "name":        "Wraith-Step Pendant",
        "description": "Move like shadow. Dodge chance +10% (permanent).",
        "cost":        260,
        "icon":        "fas fa-person-running",
        "repeatable":  False,
    },
    "block_talisman": {
        "name":        "Ironwall Talisman",
        "description": "Brace against the storm. Blocked damage reduced by a further 10% (permanent).",
        "cost":        225,
        "icon":        "fas fa-shield",
        "repeatable":  False,
    },
    "crit_stone": {
        "name":        "Sharpened Crit Stone",
        "description": "Find the gap between breath and bone. Crit chance +10% (permanent).",
        "cost":        260,
        "icon":        "fas fa-crosshairs",
        "repeatable":  False,
    },
    "crit_lens": {
        "name":        "Executioner's Lens",
        "description": "Strike where it hurts most. Crit damage multiplier +0.25× (permanent).",
        "cost":        325,
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
    "life_ring": {
        "name":   "Life Ring",
        "stat":   "max_hp",
        "amount": 15,
        "mode":   "add",
    },
    "fading_soul": {
        "name":   "Fading Soul",
        "stat":   None,   # no effect
        "amount": 0,
    },
}