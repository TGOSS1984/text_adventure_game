"""
classes.py

Single source of truth for all player class definitions.

Adding a new class: add one entry here. Everything else updates automatically.

Primary special fields (50 MP, shared cooldown):
    special_multiplier  — damage multiplier applied to relevant attack stat
    special_effect      — 'stun', 'smoke', 'heal_stun', 'double_hit',
                          'random_hit', 'combo_buff_hot', or None
    special_variance    — max random int subtracted from damage (0 = no variance)
    special_min_dmg     — damage floor after all reductions

Secondary special fields (35 MP, same shared cooldown):
    special2_effect     — 'dot', 'buff_attack', 'shield', 'stun', 'leech',
                          'parry', 'gamble_heal'
    special2_multiplier — damage multiplier on the hit itself (0 = no direct hit)
    special2_dot_dmg    — damage per turn (dot only)
    special2_dot_turns  — duration in turns (dot only)
    special2_dot_label  — key into DOT_TICK_MESSAGES in config.py ('bleed'/'poison')
    special2_buff_stat  — session character key to boost ('attack'/'magic_attack')
    special2_buff_amount— flat amount added to buff_stat
    special2_buff_turns — duration in turns
    special2_buff_label — key into BUFF_EXPIRE_MESSAGES in config.py
    special2_shield_pct — fraction of incoming damage absorbed (0.0–1.0)
    special2_shield_turns — duration in turns

Unlock flags (Commit 8):
    unlocked_by_default — True = always available on the class select screen
                          False = hidden until the unlock condition is met
    unlock_condition    — human-readable string describing how to unlock
                          (used in the locked-class tooltip on the carousel)

New effect types added in Commit 7 (handled in combat.py Commit 8):
    combo_buff_hot  — Barbarian Berserker Rage: +6 atk buff 3t + 8 HP/turn HoT 3t
    double_hit      — Samurai Iaijutsu: two hits at 1.0x physical attack each
    random_hit      — Wretch Desperate Strike: random damage 5–60, no stat scaling
    parry           — Samurai Iron Stance: 50% shield 3t (reuses shield mechanism)
    gamble_heal     — Wretch Fortune's Favour: 50/50 large heal or small heal + atk buff

DOT/BUFF config keys added in Commit 8 (config.py):
    'berserker_rage' — BUFF_EXPIRE_MESSAGES key for Barbarian atk buff
    'iron_stance'    — BUFF_EXPIRE_MESSAGES key for Samurai parry shield
"""

CLASSES = {
    "Knight": {
        # ── Core stats ────────────────────────────────────────────────────────
        "attack":           17,
        "magic_attack":     0,
        "defense":          15,
        "magic_defense":    10,
        "max_hp":           160,
        "mp_max":           80,
        # ── Combat modifiers ──────────────────────────────────────────────────
        "crit_chance":      0.20,
        "crit_multiplier":  1.5,
        "dodge_chance":     0.20,
        "block_multiplier": 0.25,
        "damage_type":      "physical",
        # ── Assets ────────────────────────────────────────────────────────────
        "image":            "classes/knight.png",
        "icon":             "fa-chess-knight",
        # ── Unlock ────────────────────────────────────────────────────────────
        "unlocked_by_default": True,
        "unlock_condition":    "",
        # ── Primary special ───────────────────────────────────────────────────
        "special_name":       "Shield Bash",
        "special_label":      "🛡 Shield Bash",
        "special_desc":       "Normal damage + stun. Enemy cannot counter.",
        "special_cost":       50,
        "special_cooldown":   4,
        "special_multiplier": 1.0,
        "special_effect":     "stun",
        "special_variance":   4,
        "special_min_dmg":    5,
        # ── Secondary special ─────────────────────────────────────────────────
        "special2_name":         "War Cry",
        "special2_label":        "⚔ War Cry",
        "special2_desc":         "Raise your weapon and bellow. Attack +5 for 3 turns.",
        "special2_cost":         35,
        "special2_effect":       "buff_attack",
        "special2_multiplier":   0,
        "special2_dot_dmg":      0,
        "special2_dot_turns":    0,
        "special2_dot_label":    "",
        "special2_buff_stat":    "attack",
        "special2_buff_amount":  5,
        "special2_buff_turns":   3,
        "special2_buff_label":   "war_cry",
        "special2_shield_pct":   0.0,
        "special2_shield_turns": 0,
        # ── Flavour ───────────────────────────────────────────────────────────
        "lore": (
            "Once a sentinel of the Sunken Citadel, their oath was not broken "
            "— only forgotten. Clad in rusted honour, they march through death unbent."
        ),
    },

    "Mage": {
        # ── Core stats ────────────────────────────────────────────────────────
        "attack":           0,
        "magic_attack":     28,
        "defense":          6,
        "magic_defense":    18,
        "max_hp":           110,
        "mp_max":           120,
        # ── Combat modifiers ──────────────────────────────────────────────────
        "crit_chance":      0.30,
        "crit_multiplier":  1.5,
        "dodge_chance":     0.60,
        "block_multiplier": 0.60,
        "damage_type":      "magic",
        # ── Assets ────────────────────────────────────────────────────────────
        "image":            "classes/mage.png",
        "icon":             "fa-wand-magic-sparkles",
        # ── Unlock ────────────────────────────────────────────────────────────
        "unlocked_by_default": True,
        "unlock_condition":    "",
        # ── Primary special ───────────────────────────────────────────────────
        "special_name":       "Arcane Burst",
        "special_label":      "✨ Arcane Burst",
        "special_desc":       "2× magic attack. Bypasses all physical armour.",
        "special_cost":       50,
        "special_cooldown":   4,
        "special_multiplier": 2.0,
        "special_effect":     None,
        "special_variance":   0,
        "special_min_dmg":    10,
        # ── Secondary special ─────────────────────────────────────────────────
        "special2_name":         "Nullfield",
        "special2_label":        "🔮 Nullfield",
        "special2_desc":         "Weave a barrier of arcane force. Incoming damage halved for 2 turns.",
        "special2_cost":         35,
        "special2_effect":       "shield",
        "special2_multiplier":   0,
        "special2_dot_dmg":      0,
        "special2_dot_turns":    0,
        "special2_dot_label":    "",
        "special2_buff_stat":    None,
        "special2_buff_amount":  0,
        "special2_buff_turns":   0,
        "special2_buff_label":   "nullfield",
        "special2_shield_pct":   0.50,
        "special2_shield_turns": 3,
        # ── Flavour ───────────────────────────────────────────────────────────
        "lore": (
            "Bearer of forbidden glintfire, the Mage whispers truths carved in starlight. "
            "Each spell flung is a shard of a dream long devoured."
        ),
    },

    "Rogue": {
        # ── Core stats ────────────────────────────────────────────────────────
        "attack":           22,
        "magic_attack":     0,
        "defense":          8,
        "magic_defense":    6,
        "max_hp":           130,
        "mp_max":           100,
        # ── Combat modifiers ──────────────────────────────────────────────────
        "crit_chance":      0.40,
        "crit_multiplier":  1.5,
        "dodge_chance":     0.70,
        "block_multiplier": 0.50,
        "damage_type":      "physical",
        # ── Assets ────────────────────────────────────────────────────────────
        "image":            "classes/rogue.png",
        "icon":             "fa-skull-crossbones",
        # ── Unlock ────────────────────────────────────────────────────────────
        "unlocked_by_default": True,
        "unlock_condition":    "",
        # ── Primary special ───────────────────────────────────────────────────
        "special_name":       "Smoke Screen",
        "special_label":      "💨 Smoke Screen",
        "special_desc":       "1× attack damage + guaranteed dodge next enemy turn.",
        "special_cost":       50,
        "special_cooldown":   4,
        "special_multiplier": 1.0,
        "special_effect":     "smoke",
        "special_variance":   0,
        "special_min_dmg":    5,
        # ── Secondary special ─────────────────────────────────────────────────
        "special2_name":         "Backstab",
        "special2_label":        "🗡 Backstab",
        "special2_desc":         "Strike a critical spot — the enemy bleeds for 8 damage per turn for 4 turns.",
        "special2_cost":         35,
        "special2_effect":       "dot",
        "special2_multiplier":   0.5,
        "special2_dot_dmg":      8,
        "special2_dot_turns":    4,
        "special2_dot_label":    "bleed",
        "special2_buff_stat":    None,
        "special2_buff_amount":  0,
        "special2_buff_turns":   0,
        "special2_buff_label":   "",
        "special2_shield_pct":   0.0,
        "special2_shield_turns": 0,
        # ── Flavour ───────────────────────────────────────────────────────────
        "lore": (
            "Born in the shadow of the Ashen Spires, the Rogue strikes like regret "
            "— unseen, swift, and final. No name, no past, only the blade."
        ),
    },

    "Archer": {
        # ── Core stats ────────────────────────────────────────────────────────
        "attack":           20,
        "magic_attack":     0,
        "defense":          10,
        "magic_defense":    8,
        "max_hp":           140,
        "mp_max":           100,
        # ── Combat modifiers ──────────────────────────────────────────────────
        "crit_chance":      0.50,
        "crit_multiplier":  1.5,
        "dodge_chance":     0.50,
        "block_multiplier": 0.40,
        "damage_type":      "physical",
        # ── Assets ────────────────────────────────────────────────────────────
        "image":            "classes/archer.png",
        "icon":             "fa-feather",
        # ── Unlock ────────────────────────────────────────────────────────────
        "unlocked_by_default": True,
        "unlock_condition":    "",
        # ── Primary special ───────────────────────────────────────────────────
        "special_name":       "Mark Target",
        "special_label":      "🎯 Mark Target",
        "special_desc":       "2× attack. Finds the enemy's weak point.",
        "special_cost":       50,
        "special_cooldown":   4,
        "special_multiplier": 2.0,
        "special_effect":     None,
        "special_variance":   0,
        "special_min_dmg":    5,
        # ── Secondary special ─────────────────────────────────────────────────
        "special2_name":         "Poison Arrow",
        "special2_label":        "🏹 Poison Arrow",
        "special2_desc":         "Loose a barbed arrow laced with venom. 7 poison damage per turn for 5 turns.",
        "special2_cost":         35,
        "special2_effect":       "dot",
        "special2_multiplier":   0,
        "special2_dot_dmg":      7,
        "special2_dot_turns":    5,
        "special2_dot_label":    "poison",
        "special2_buff_stat":    None,
        "special2_buff_amount":  0,
        "special2_buff_turns":   0,
        "special2_buff_label":   "",
        "special2_shield_pct":   0.0,
        "special2_shield_turns": 0,
        # ── Flavour ───────────────────────────────────────────────────────────
        "lore": (
            "From the ruins of Eldergrove they come, eyes hollow with distant wars. "
            "Each arrow loosed is a memory exiled into the dark."
        ),
    },

    "Paladin": {
        # ── Core stats ────────────────────────────────────────────────────────
        "attack":           18,
        "magic_attack":     18,
        "defense":          12,
        "magic_defense":    14,
        "max_hp":           150,
        "mp_max":           90,
        # ── Combat modifiers ──────────────────────────────────────────────────
        "crit_chance":      0.20,
        "crit_multiplier":  1.5,
        "dodge_chance":     0.40,
        "block_multiplier": 0.30,
        "damage_type":      "mixed",
        # ── Assets ────────────────────────────────────────────────────────────
        "image":            "classes/paladin.png",
        "icon":             "fa-cross",
        # ── Unlock ────────────────────────────────────────────────────────────
        "unlocked_by_default": True,
        "unlock_condition":    "",
        # ── Primary special ───────────────────────────────────────────────────
        "special_name":       "Healing Light",
        "special_label":      "✝ Healing Light",
        "special_desc":       "Restore 40% max HP. Sacred light blinds the enemy — they cannot counter.",
        "special_cost":       50,
        "special_cooldown":   5,
        "special_multiplier": 0,
        "special_effect":     "heal_stun",
        "special_variance":   0,
        "special_min_dmg":    0,
        # ── Secondary special ─────────────────────────────────────────────────
        "special2_name":         "Hammer of Justice",
        "special2_label":        "🔨 Hammer of Justice",
        "special2_desc":         "1.5× mixed damage strike. Sacred force stuns — the enemy cannot counter.",
        "special2_cost":         35,
        "special2_effect":       "stun",
        "special2_multiplier":   1.5,
        "special2_dot_dmg":      0,
        "special2_dot_turns":    0,
        "special2_dot_label":    "",
        "special2_buff_stat":    None,
        "special2_buff_amount":  0,
        "special2_buff_turns":   0,
        "special2_buff_label":   "",
        "special2_shield_pct":   0.0,
        "special2_shield_turns": 0,
        # ── Flavour ───────────────────────────────────────────────────────────
        "lore": (
            "Oathbound to a god who no longer answers, the Paladin carries faith "
            "as a weapon and a wound. Where others see ruin, they see a reason to endure."
        ),
    },

    "Necromancer": {
        # ── Core stats ────────────────────────────────────────────────────────
        "attack":           0,
        "magic_attack":     24,
        "defense":          10,
        "magic_defense":    22,
        "max_hp":           100,
        "mp_max":           130,
        # ── Combat modifiers ──────────────────────────────────────────────────
        "crit_chance":      0.25,
        "crit_multiplier":  1.5,
        "dodge_chance":     0.55,
        "block_multiplier": 0.50,
        "damage_type":      "magic",
        # ── Assets ────────────────────────────────────────────────────────────
        "image":            "classes/necromancer.png",
        "icon":             "fa-skull",
        # ── Unlock ────────────────────────────────────────────────────────────
        "unlocked_by_default": True,
        "unlock_condition":    "",
        # ── Primary special ───────────────────────────────────────────────────
        "special_name":       "Raise the Dead",
        "special_label":      "💀 Raise the Dead",
        "special_desc":       "2.5× magic attack. Undead tear through armour — enemy cannot predict the assault.",
        "special_cost":       50,
        "special_cooldown":   5,
        "special_multiplier": 2.5,
        "special_effect":     None,
        "special_variance":   8,
        "special_min_dmg":    12,
        # ── Secondary special ─────────────────────────────────────────────────
        "special2_name":         "Soul Leech",
        "special2_label":        "💉 Soul Leech",
        "special2_desc":         "Drain life — 1.5× magic damage, heal for 150% of damage dealt (min 15 HP).",
        "special2_cost":         35,
        "special2_effect":       "leech",
        "special2_multiplier":   1.5,
        "special2_leech_min_heal": 15,
        "special2_dot_dmg":      0,
        "special2_dot_turns":    0,
        "special2_dot_label":    "",
        "special2_buff_stat":    None,
        "special2_buff_amount":  0,
        "special2_buff_turns":   0,
        "special2_buff_label":   "",
        "special2_shield_pct":   0.0,
        "special2_shield_turns": 0,
        # ── Flavour ───────────────────────────────────────────────────────────
        "lore": (
            "They do not fear death. They have spoken to it, bargained with it, "
            "and worn its face as a mask. The dead answer when the Necromancer calls."
        ),
    },

    # ══════════════════════════════════════════════════════════════════════════
    # NEW CLASSES — Commit 7
    # Locked by default until unlock conditions are met (Commit 8).
    # New special effect types defined here; combat.py handling added Commit 8.
    # ══════════════════════════════════════════════════════════════════════════

    "Barbarian": {
        # ── Core stats ────────────────────────────────────────────────────────
        # High HP and attack, low defenses and magic resistance.
        # Survives by killing quickly and healing off Berserker Rage.
        # Differentiated from Knight: Knight endures, Barbarian overwhelms.
        "attack":           24,
        "magic_attack":     0,
        "defense":          10,
        "magic_defense":    6,
        "max_hp":           170,
        "mp_max":           70,
        # ── Combat modifiers ──────────────────────────────────────────────────
        "crit_chance":      0.25,
        "crit_multiplier":  1.5,
        "dodge_chance":     0.25,
        "block_multiplier": 0.45,   # 55% damage reduced — decent but not Knight-tier
        "damage_type":      "physical",
        # ── Assets ────────────────────────────────────────────────────────────
        "image":            "classes/barbarian.png",
        "icon":             "fa-hand-fist",
        # ── Unlock ────────────────────────────────────────────────────────────
        "unlocked_by_default": False,
        "unlock_condition":    "Complete the main story (any ending).",
        # ── Primary special — combo_buff_hot ──────────────────────────────────
        # Berserker Rage: +6 attack for 3 turns AND heal 8 HP per turn for 3 turns.
        # The HoT (heal-over-time) is a new session mechanism added in Commit 8.
        # combat.py Commit 8: effect == 'combo_buff_hot' sets both buff and HoT state.
        "special_name":       "Berserker Rage",
        "special_label":      "💢 Berserker Rage",
        "special_desc":       "Blood rises. Attack +6 for 3 turns, recover 8 HP per turn for 3 turns.",
        "special_cost":       50,
        "special_cooldown":   5,
        "special_multiplier": 0,        # no direct damage — pure buff + HoT
        "special_effect":     "combo_buff_hot",
        "special_variance":   0,
        "special_min_dmg":    0,
        # Combo-specific fields (read by combat.py Commit 8):
        "special_buff_stat":    "attack",
        "special_buff_amount":  6,
        "special_buff_turns":   3,
        "special_buff_label":   "berserker_rage",
        "special_hot_dmg":      8,      # HP healed per turn (HoT)
        "special_hot_turns":    3,
        # ── Secondary special — Feel No Pain ──────────────────────────────────
        # Full damage immunity for 2 turns. Uses existing shield mechanism at 100%.
        # Low magic defense means the Barbarian still struggles against magic enemies —
        # Feel No Pain blocks everything but the enemy can wait it out.
        "special2_name":         "Feel No Pain",
        "special2_label":        "🩸 Feel No Pain",
        "special2_desc":         "The pain does not register. All incoming damage blocked for 2 turns.",
        "special2_cost":         35,
        "special2_effect":       "shield",
        "special2_multiplier":   0,
        "special2_dot_dmg":      0,
        "special2_dot_turns":    0,
        "special2_dot_label":    "",
        "special2_buff_stat":    None,
        "special2_buff_amount":  0,
        "special2_buff_turns":   0,
        "special2_buff_label":   "",
        "special2_shield_pct":   1.0,   # 100% block — full immunity
        "special2_shield_turns": 2,
        # ── Flavour ───────────────────────────────────────────────────────────
        "lore": (
            "There are no tactics in the Barbarian's eyes — only the arithmetic of force. "
            "They have broken every chain that tried to hold them, including their own mercy."
        ),
    },

    "Samurai": {
        # ── Core stats ────────────────────────────────────────────────────────
        # High dodge and crit, decent attack, low defenses.
        # Differentiated from Rogue: Rogue evades and bleeds; Samurai
        # parries and bursts with precision double strikes.
        # Higher defense than Rogue but lower dodge — trades evasion for technique.
        "attack":           23,
        "magic_attack":     0,
        "defense":          12,
        "magic_defense":    7,
        "max_hp":           135,
        "mp_max":           110,
        # ── Combat modifiers ──────────────────────────────────────────────────
        "crit_chance":      0.45,
        "crit_multiplier":  1.5,
        "dodge_chance":     0.55,
        "block_multiplier": 0.45,
        "damage_type":      "physical",
        # ── Assets ────────────────────────────────────────────────────────────
        "image":            "classes/samurai.png",
        "icon":             "fa-person-falling-burst",
        # ── Unlock ────────────────────────────────────────────────────────────
        "unlocked_by_default": False,
        "unlock_condition":    "Defeat Mesmereth in the Shadow Realm.",
        # ── Primary special — double_hit ──────────────────────────────────────
        # Iaijutsu: two rapid strikes, each at 1.0× attack.
        # Total damage slightly lower than a 2× crit but more consistent.
        # combat.py Commit 8: effect == 'double_hit' calls attack() twice.
        "special_name":       "Iaijutsu",
        "special_label":      "⚔ Iaijutsu",
        "special_desc":       "A lightning draw. Two strikes, each at full attack power.",
        "special_cost":       50,
        "special_cooldown":   4,
        "special_multiplier": 1.0,      # applied to each hit individually
        "special_effect":     "double_hit",
        "special_variance":   3,
        "special_min_dmg":    5,
        # ── Secondary special — Iron Stance (parry) ───────────────────────────
        # 50% damage shield for 3 turns.
        # Uses existing shield mechanism — no new session state needed.
        # The parry flavour comes from the lore/label; mechanical effect is shield.
        # Full auto-counter (Commit 8+ optional enhancement) can be added later.
        "special2_name":         "Iron Stance",
        "special2_label":        "🛡 Iron Stance",
        "special2_desc":         "Blade raised, breath steady. Parry incoming attacks — damage halved for 3 turns.",
        "special2_cost":         35,
        "special2_effect":       "shield",
        "special2_multiplier":   0,
        "special2_dot_dmg":      0,
        "special2_dot_turns":    0,
        "special2_dot_label":    "",
        "special2_buff_stat":    None,
        "special2_buff_amount":  0,
        "special2_buff_turns":   0,
        "special2_buff_label":   "iron_stance",
        "special2_shield_pct":   0.50,
        "special2_shield_turns": 3,
        # ── Flavour ───────────────────────────────────────────────────────────
        "lore": (
            "They do not seek battle. Battle finds them, as it always has, "
            "and they meet it the same way every time — calmly, completely, and without regret. "
            "The blade has been drawn ten thousand times. It has never been drawn wrong."
        ),
    },

    "Wretch": {
        # ── Core stats ────────────────────────────────────────────────────────
        # Deliberately mediocre base stats — the chaos class.
        # Fixed stats mean basic attacks still work; the high-variance specials
        # are where the risk/reward lives. Not unwinnable — just unpredictable.
        # Always available (no unlock required) as the challenge pick.
        "attack":           16,
        "magic_attack":     0,
        "defense":          8,
        "magic_defense":    8,
        "max_hp":           120,
        "mp_max":           90,
        # ── Combat modifiers ──────────────────────────────────────────────────
        "crit_chance":      0.30,
        "crit_multiplier":  1.5,
        "dodge_chance":     0.45,
        "block_multiplier": 0.50,   # 50% damage reduced — average
        "damage_type":      "physical",
        # ── Assets ────────────────────────────────────────────────────────────
        "image":            "classes/wretch.png",
        "icon":             "fa-person-drowning",
        # ── Unlock ────────────────────────────────────────────────────────────
        "unlocked_by_default": True,   # always available — the masochist pick
        "unlock_condition":    "",
        # ── Primary special — random_hit ──────────────────────────────────────
        # Desperate Strike: pure chaos. Damage is a random roll 5–60 with no
        # stat scaling whatsoever. Could scratch, could devastate.
        # combat.py Commit 8: effect == 'random_hit' uses randint(5, 60).
        "special_name":       "Desperate Strike",
        "special_label":      "🎲 Desperate Strike",
        "special_desc":       "Fortune favours no one. A wild blow — anywhere from 5 to 60 damage. No guarantees.",
        "special_cost":       50,
        "special_cooldown":   4,
        "special_multiplier": 0,        # ignored — damage is pure random
        "special_effect":     "random_hit",
        "special_variance":   0,
        "special_min_dmg":    5,
        # ── Secondary special — gamble_heal ───────────────────────────────────
        # Fortune's Favour: 50/50 roll.
        # Win (50%): heal 50% max HP — a dramatic recovery.
        # Lose (50%): heal only 8% max HP + +3 attack buff for 2 turns (consolation).
        # combat.py Commit 8: effect == 'gamble_heal' rolls the dice and returns
        # the appropriate heal_amount + optional buff in side_effects.
        "special2_name":         "Fortune's Favour",
        "special2_label":        "🪙 Fortune's Favour",
        "special2_desc":         "Flip the coin. 50% chance: restore 50% HP. 50% chance: restore a little and gain fury.",
        "special2_cost":         35,
        "special2_effect":       "gamble_heal",
        "special2_multiplier":   0,
        "special2_dot_dmg":      0,
        "special2_dot_turns":    0,
        "special2_dot_label":    "",
        "special2_buff_stat":    "attack",    # used on the consolation branch
        "special2_buff_amount":  3,
        "special2_buff_turns":   2,
        "special2_buff_label":   "wretch_fury",
        "special2_shield_pct":   0.0,
        "special2_shield_turns": 0,
        # ── Flavour ───────────────────────────────────────────────────────────
        "lore": (
            "They arrived at the Ashen Ruins with nothing — no name, no weapon, no plan. "
            "Somehow, they are still here. The world has not decided what to do with them yet. "
            "Neither have they."
        ),
    },
}


def get_class(class_name: str) -> dict:
    """Return the class definition dict, or None if not found."""
    return CLASSES.get(class_name)


def get_special_label(class_name: str, fallback: str = "⚡ Special") -> str:
    """Return the primary special move button label for a given class."""
    cls = CLASSES.get(class_name)
    return cls["special_label"] if cls else fallback


def get_special2_label(class_name: str, fallback: str = "⚡ Special 2") -> str:
    """Return the secondary special move button label for a given class."""
    cls = CLASSES.get(class_name)
    return cls["special2_label"] if cls else fallback


def get_class_icon(class_name: str, fallback: str = "fa-shield-halved") -> str:
    """Return the Font Awesome icon class for a given class."""
    cls = CLASSES.get(class_name)
    return cls["icon"] if cls else fallback