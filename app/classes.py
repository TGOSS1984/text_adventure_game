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
    special2_dot_dmg    — flat damage per turn (dot only; 0 if using pct)
    special2_dot_pct     — % of enemy max HP per turn (dot only; 0 if using flat dmg)
    special2_dot_turns  — duration in turns (dot only)
    special2_dot_label  — key into DOT_TICK_MESSAGES in config.py ('bleed'/'poison')
    special2_buff_stat  — session character key to boost ('attack'/'magic_attack')
    special2_buff_amount— flat amount added to buff_stat
    special2_buff_turns — duration in turns
    special2_buff_label — key into BUFF_EXPIRE_MESSAGES in config.py
    special2_buff_stat2 — optional second stat to buff simultaneously (e.g. 'defense')
    special2_buff_pct2  — % of that stat to add as buff amount
    special2_shield_pct — fraction of incoming damage absorbed (0.0–1.0)
    special2_shield_turns — duration in turns
    special2_parry_counter_pct — fraction of player attack auto-countered each
                          turn while parry is active (parry effect only)

Unlock flags (Commit 8):
    unlocked_by_default — True = always available on the class select screen
                          False = hidden until the unlock condition is met
    unlock_condition    — human-readable string describing how to unlock
                          (used in the locked-class tooltip on the carousel)

New effect types added in Commit 7 (handled in combat.py Commit 8):
    combo_buff_hot  — Barbarian Berserker Rage: +6 atk buff 3t + 8 HP/turn HoT 3t
    double_hit      — Samurai Iaijutsu: two hits at 1.0x physical attack each
    random_hit      — Wretch Desperate Strike: random damage 5–60, no stat scaling
    parry           — Samurai Iron Stance: 50% damage shield for 3 turns AND
                      auto-counter at special2_parry_counter_pct × player attack
                      on each turn an enemy hit lands while parry is active.
                      Session keys: parry_turns, parry_counter_pct (Commit 8).
    gamble_heal     — Wretch Fortune's Favour: 50/50 large heal or small heal + atk buff

DOT/BUFF/EXPIRE config keys to add in Commit 8 (config.py):
    'berserker_rage' — BUFF_EXPIRE_MESSAGES: Barbarian atk buff expiry
    'iron_stance'    — BUFF_EXPIRE_MESSAGES: Samurai parry shield expiry
    'wretch_fury'    — BUFF_EXPIRE_MESSAGES: Wretch consolation atk buff expiry
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
        "special2_name":              "War Cry",
        "special2_label":             "⚔ War Cry",
        "special2_desc":              "Raise your weapon and bellow. Attack +25% and Defense +20% for 3 turns.",
        "special2_cost":              35,
        "special2_effect":            "buff_attack",
        "special2_multiplier":        0,
        "special2_dot_dmg":           0,
        "special2_dot_turns":         0,
        "special2_dot_label":         "",
        "special2_buff_stat":         "attack",
        "special2_buff_amount":       0,
        "special2_buff_pct":          0.25,
        "special2_buff_stat2":        "defense",
        "special2_buff_pct2":         0.20,
        "special2_buff_turns":        3,
        "special2_buff_label":        "war_cry",
        "special2_shield_pct":        0.0,
        "special2_shield_turns":      0,
        "special2_parry_counter_pct": 0.0,
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
        "special2_name":              "Nullfield",
        "special2_label":             "🔮 Nullfield",
        "special2_desc":              "Weave a barrier of arcane force. Incoming damage halved for 2 turns.",
        "special2_cost":              35,
        "special2_effect":            "shield",
        "special2_multiplier":        0,
        "special2_dot_dmg":           0,
        "special2_dot_turns":         0,
        "special2_dot_label":         "",
        "special2_buff_stat":         None,
        "special2_buff_amount":       0,
        "special2_buff_turns":        0,
        "special2_buff_label":        "nullfield",
        "special2_shield_pct":        0.50,
        "special2_shield_turns":      3,
        "special2_parry_counter_pct": 0.0,
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
        "special2_name":              "Backstab",
        "special2_label":             "🗡 Backstab",
        "special2_desc":              "Strike a critical spot — the enemy bleeds for 3.5% of their max HP per turn for 4 turns.",
        "special2_cost":              35,
        "special2_effect":            "dot",
        "special2_multiplier":        0.5,
        "special2_dot_dmg":           0,
        "special2_dot_pct":           0.035,
        "special2_dot_turns":         4,
        "special2_dot_label":         "bleed",
        "special2_buff_stat":         None,
        "special2_buff_amount":       0,
        "special2_buff_turns":        0,
        "special2_buff_label":        "",
        "special2_shield_pct":        0.0,
        "special2_shield_turns":      0,
        "special2_parry_counter_pct": 0.0,
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
        "special2_name":              "Poison Arrow",
        "special2_label":             "🏹 Poison Arrow",
        "special2_desc":              "Loose a barbed arrow laced with venom. 3% of the enemy's max HP in poison damage per turn for 5 turns.",
        "special2_cost":              35,
        "special2_effect":            "dot",
        "special2_multiplier":        0,
        "special2_dot_dmg":           0,
        "special2_dot_pct":           0.030,
        "special2_dot_turns":         5,
        "special2_dot_label":         "poison",
        "special2_buff_stat":         None,
        "special2_buff_amount":       0,
        "special2_buff_turns":        0,
        "special2_buff_label":        "",
        "special2_shield_pct":        0.0,
        "special2_shield_turns":      0,
        "special2_parry_counter_pct": 0.0,
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
        "special2_name":              "Hammer of Justice",
        "special2_label":             "🔨 Hammer of Justice",
        "special2_desc":              "1.5× mixed damage strike. Sacred force stuns — the enemy cannot counter.",
        "special2_cost":              35,
        "special2_effect":            "stun",
        "special2_multiplier":        1.5,
        "special2_dot_dmg":           0,
        "special2_dot_turns":         0,
        "special2_dot_label":         "",
        "special2_buff_stat":         None,
        "special2_buff_amount":       0,
        "special2_buff_turns":        0,
        "special2_buff_label":        "",
        "special2_shield_pct":        0.0,
        "special2_shield_turns":      0,
        "special2_parry_counter_pct": 0.0,
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
        "special2_name":              "Soul Leech",
        "special2_label":             "💉 Soul Leech",
        "special2_desc":              "Drain life — 1.5× magic damage, heal for 150% of damage dealt (min 12% of your max HP).",
        "special2_cost":              35,
        "special2_effect":            "leech",
        "special2_multiplier":        1.5,
        "special2_leech_min_heal":    0,
        "special2_leech_min_pct":     0.12,
        "special2_dot_dmg":           0,
        "special2_dot_turns":         0,
        "special2_dot_label":         "",
        "special2_buff_stat":         None,
        "special2_buff_amount":       0,
        "special2_buff_turns":        0,
        "special2_buff_label":        "",
        "special2_shield_pct":        0.0,
        "special2_shield_turns":      0,
        "special2_parry_counter_pct": 0.0,
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
        # Survives by killing quickly and healing off Berserker Rage HoT.
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
        "block_multiplier": 0.45,
        "damage_type":      "physical",
        # ── Assets ────────────────────────────────────────────────────────────
        "image":            "classes/barbarian.png",
        "icon":             "fa-hand-fist",
        # ── Unlock ────────────────────────────────────────────────────────────
        "unlocked_by_default": False,
        "unlock_condition":    "Complete the main story (any ending).",
        # ── Primary special — combo_buff_hot ──────────────────────────────────
        # Berserker Rage: +6 attack for 3 turns AND heal 8 HP per turn for 3 turns.
        # combat.py Commit 8: effect == 'combo_buff_hot' sets buff AND hot state.
        "special_name":       "Berserker Rage",
        "special_label":      "💢 Berserker Rage",
        "special_desc":       "Blood rises. Attack +25% for 3 turns, recover 5% max HP per turn for 3 turns.",
        "special_cost":       50,
        "special_cooldown":   5,
        "special_multiplier": 0,
        "special_effect":     "combo_buff_hot",
        "special_variance":   0,
        "special_min_dmg":    0,
        "special_buff_stat":    "attack",
        "special_buff_amount":  0,
        "special_buff_pct":     0.25,
        "special_buff_turns":   3,
        "special_buff_label":   "berserker_rage",
        "special_hot_dmg":      0,
        "special_hot_pct":      0.05,
        "special_hot_turns":    3,
        # ── Secondary special — Feel No Pain ──────────────────────────────────
        # 100% shield for 2 turns — full damage immunity.
        "special2_name":              "Feel No Pain",
        "special2_label":             "🗿 Feel No Pain",
        "special2_desc":              "The pain does not register. All incoming damage blocked for 2 turns.",
        "special2_cost":              35,
        "special2_effect":            "shield",
        "special2_multiplier":        0,
        "special2_dot_dmg":           0,
        "special2_dot_turns":         0,
        "special2_dot_label":         "",
        "special2_buff_stat":         None,
        "special2_buff_amount":       0,
        "special2_buff_turns":        0,
        "special2_buff_label":        "",
        "special2_shield_pct":        1.0,
        "special2_shield_turns":      2,
        "special2_parry_counter_pct": 0.0,
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
        # combat.py Commit 8: effect == 'double_hit' calls attack() twice.
        "special_name":       "Iaijutsu",
        "special_label":      "⚔ Iaijutsu",
        "special_desc":       "A lightning draw. Two strikes, each at full attack power.",
        "special_cost":       50,
        "special_cooldown":   4,
        "special_multiplier": 1.0,
        "special_effect":     "double_hit",
        "special_variance":   3,
        "special_min_dmg":    5,
        # ── Secondary special — Iron Stance (parry) ───────────────────────────
        # 50% incoming damage shield for 3 turns AND auto-counter at 50% player
        # attack on each turn an enemy hit lands while parry is active.
        # special2_effect = 'parry' — distinct from 'shield' so combat.py can
        # set both shield_pct/shield_turns AND parry_turns/parry_counter_pct.
        # Session keys added in Commit 8: parry_turns, parry_counter_pct.
        # Counter fires in battle_routes Step 4 after resolve_player_action()
        # if damage landed (not dodged, not smoked) and parry_turns > 0.
        "special2_name":              "Iron Stance",
        "special2_label":             "🛡 Iron Stance",
        "special2_desc":              "Blade raised, breath steady. Incoming damage halved for 3 turns — and you counter each blow for 50% attack.",
        "special2_cost":              35,
        "special2_effect":            "parry",
        "special2_multiplier":        0,
        "special2_dot_dmg":           0,
        "special2_dot_turns":         0,
        "special2_dot_label":         "",
        "special2_buff_stat":         None,
        "special2_buff_amount":       0,
        "special2_buff_turns":        0,
        "special2_buff_label":        "iron_stance",
        "special2_shield_pct":        0.50,   # damage reduction while parrying
        "special2_shield_turns":      3,       # also used as parry duration
        "special2_parry_counter_pct": 0.50,   # counter at 50% of player attack
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
        "block_multiplier": 0.50,
        "damage_type":      "physical",
        # ── Assets ────────────────────────────────────────────────────────────
        "image":            "classes/wretch.png",
        "icon":             "fa-person-drowning",
        # ── Unlock ────────────────────────────────────────────────────────────
        "unlocked_by_default": True,
        "unlock_condition":    "",
        # ── Primary special — random_hit ──────────────────────────────────────
        # Desperate Strike: pure chaos. Damage is a random roll 5–60 with no
        # stat scaling whatsoever.
        # combat.py Commit 8: effect == 'random_hit' uses randint(5, 60).
        "special_name":       "Desperate Strike",
        "special_label":      "🎲 Desperate Strike",
        "special_desc":       "Fortune favours no one. A wild blow — anywhere from 5 to 60 damage. No guarantees.",
        "special_cost":       50,
        "special_cooldown":   4,
        "special_multiplier": 0,
        "special_effect":     "random_hit",
        "special_variance":   0,
        "special_min_dmg":    15,
        # ── Secondary special — gamble_heal ───────────────────────────────────
        # Fortune's Favour: 50/50 roll.
        # Win (50%): heal 50% max HP.
        # Lose (50%): heal 8% max HP + +3 attack buff for 2 turns (consolation).
        # combat.py Commit 8: effect == 'gamble_heal' rolls and returns
        # appropriate heal_amount + optional buff in side_effects.
        "special2_name":              "Fortune's Favour",
        "special2_label":             "🪙 Fortune's Favour",
        "special2_desc":              "Flip the coin. 50% chance: restore 50% HP. 50% chance: restore a little and gain fury (+20% attack).",
        "special2_cost":              35,
        "special2_effect":            "gamble_heal",
        "special2_multiplier":        0,
        "special2_dot_dmg":           0,
        "special2_dot_turns":         0,
        "special2_dot_label":         "",
        "special2_buff_stat":         "attack",
        "special2_buff_amount":       0,
        "special2_buff_pct":          0.20,
        "special2_buff_turns":        2,
        "special2_buff_label":        "wretch_fury",
        "special2_shield_pct":        0.0,
        "special2_shield_turns":      0,
        "special2_parry_counter_pct": 0.0,
        # ── Flavour ───────────────────────────────────────────────────────────
        "lore": (
            "They arrived at the Ashen Ruins with nothing — no name, no weapon, no plan. "
            "Somehow, they are still here. The world has not decided what to do with them yet. "
            "Neither have they."
        ),
    },
    "Hunter": {
        # ── Core stats ────────────────────────────────────────────────────────
        # Rogue/Archer hybrid inspired by the Bloodborne Hunter.
        # Second highest dodge in the roster (65% → 60% after balance pass).
        # Sustains through Hunter's Mark leech rather than shields or healing.
        # Lowest block % of any physical class — built to avoid hits, not tank them.
        "attack":           21,
        "magic_attack":     0,
        "defense":          9,
        "magic_defense":    7,
        "max_hp":           125,
        "mp_max":           100,
        # ── Combat modifiers ──────────────────────────────────────────────────
        "crit_chance":      0.45,
        "crit_multiplier":  1.5,
        "dodge_chance":     0.60,
        "block_multiplier": 0.60,   # only 40% damage blocked — lowest physical class
        "damage_type":      "physical",
        # ── Assets ────────────────────────────────────────────────────────────
        "image":            "classes/hunter.png",
        "icon":             "fa-gun",
        # ── Unlock ────────────────────────────────────────────────────────────
        "unlocked_by_default": False,
        "unlock_condition":    "Complete a New Game+ run (any mode, any ending).",
        # ── Primary special — Trick Weapon ────────────────────────────────────
        # The cleaver transforms into a two-handed axe-cleaver.
        # Highest single-hit multiplier in the physical roster (2.5×) + stun.
        "special_name":       "Trick Weapon",
        "special_label":      "🪓 Trick Weapon",
        "special_desc":       "The cleaver cracks open into its true form. 2.5× attack — the enemy staggers and cannot counter.",
        "special_cost":       50,
        "special_cooldown":   5,
        "special_multiplier": 2.5,
        "special_effect":     "stun",
        "special_variance":   8,
        "special_min_dmg":    10,
        # ── Secondary special — Hunter's Mark ─────────────────────────────────
        # Bloodborne rally mechanic: strike back and drain life from the wound.
        # 1.5× physical attack, heal for 150% of damage dealt.
        # Min heal floor: 10% of player max HP (scales with NG+ HP gains).
        "special2_name":              "Hunter's Mark",
        "special2_label":             "🩸 Hunter's Mark",
        "special2_desc":              "Press the hunt. 1.5× attack — drain life from the wound and recover HP equal to damage dealt.",
        "special2_cost":              35,
        "special2_effect":            "leech",
        "special2_multiplier":        1.5,
        "special2_leech_min_heal":    0,
        "special2_leech_min_pct":     0.10,
        "special2_dot_dmg":           0,
        "special2_dot_pct":           0.0,
        "special2_dot_turns":         0,
        "special2_dot_label":         "",
        "special2_buff_stat":         None,
        "special2_buff_amount":       0,
        "special2_buff_pct":          0.0,
        "special2_buff_turns":        0,
        "special2_buff_label":        "",
        "special2_shield_pct":        0.0,
        "special2_shield_turns":      0,
        "special2_parry_counter_pct": 0.0,
        # ── Flavour ───────────────────────────────────────────────────────────
        "lore": (
            "From the fog-choked streets of a city that no longer exists, the Hunter "
            "carries a weapon that remembers every kill it has ever made. The cleaver "
            "folds. The blunderbuss clicks. The hunt does not end — it only changes shape."
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