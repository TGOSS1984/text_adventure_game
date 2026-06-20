# ☠️ Elden Souls — A Dark Fantasy Text Adventure

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)]()
[![Flask](https://img.shields.io/badge/Backend-Flask-000000?style=for-the-badge&logo=flask&logoColor=white)]()
[![HTMX](https://img.shields.io/badge/Frontend-HTMX_1.9-3D72D7?style=for-the-badge)]()
[![Jinja2](https://img.shields.io/badge/Templates-Jinja2-B41717?style=for-the-badge)]()
[![CSS](https://img.shields.io/badge/CSS-Custom_Properties-1572B6?style=for-the-badge&logo=css3&logoColor=white)]()
[![Chapters](https://img.shields.io/badge/Story_Chapters-137-gold?style=for-the-badge)]()
[![Bosses](https://img.shields.io/badge/Bosses-18-crimson?style=for-the-badge)]()
[![Classes](https://img.shields.io/badge/Classes-10-purple?style=for-the-badge)]()

[![GitHub](https://img.shields.io/badge/GitHub-Repository-181717?style=for-the-badge&logo=github)](https://github.com/TGOSS1984/text_adventure_game)
[![Live Demo](https://img.shields.io/badge/Heroku-Live_Demo-430098?style=for-the-badge&logo=heroku)](https://elden-souls-text-adventure-app-6406dec306fc.herokuapp.com/)

---

## 📸 Screenshots
 
### 🏠 Title / Character Select Screen
 
![Game screen](app/static/images/screenshots/game_screen.PNG)
> *The atmospheric character select screen with class carousel and lore panels*
 
---
 
### 📖 Story Screen
 
![Story screen](app/static/images/screenshots/story_screen.PNG)
> *The main story interface — typewriter narrative, branching choices and the looping bonfire video background*
 
---
 
### 🔥 Rest Screen
 
![Rest screen](app/static/images/screenshots/rest_screen.PNG)
> *A bonfire respite — HP, Estus Flasks and MP fully restored, with the merchant just a step away*
 
---
 
### 🏪 Merchant Screen
 
![Merchant screen](app/static/images/screenshots/merchant_screen.PNG)
> *The merchant's wares — spend souls on consumables and upgrades between battles*
 
---
 
### ⚔️ Battle Screen
 
![Battle screen](app/static/images/screenshots/battle_screen.PNG)
> *The turn-based combat UI — HP/MP bars, active effects strip, dual special abilities and the battle timer*
 
---
 
### 📜 Status Screen
 
![Status screen](app/static/images/screenshots/status_screen.PNG)
> *The Bearer's status screen — full character stats and a running tally of the current journey's deeds*
 
---
 
### 📚 Bestiary Screen
 
![Bestiary screen](app/static/images/screenshots/bestiary_screen.PNG)
> *The bestiary & class compendium — enemy lore, locked-class previews and full stat breakdowns for every Bearer*
 
---
 
### 💀 Death Screen
 
![Death screen](app/static/images/screenshots/death_screen.PNG)
> *The death screen — atmospheric bonfire imagery and a prompt to begin again*
 
---
 
### 📐 Initial Wireframe
 
![Wireframe mockup](app/static/images/screenshots/wireframe_mockup.PNG)
> *Early concept wireframe for the story/game screen layout*

---

## 📚 Table of Contents

- [The Inspiration](#-the-inspiration)
- [Project Purpose](#-project-purpose)
- [Features at a Glance](#-features-at-a-glance)
- [Tech Stack](#-tech-stack)
- [File Structure](#-file-structure)
- [How to Run Locally](#-how-to-run-locally)
- [Game Mechanics](#-game-mechanics)
  - [Character Classes](#character-classes)
  - [Starting Gifts](#starting-gifts)
  - [Combat System](#combat-system)
  - [Dual Specials System](#dual-specials-system)
  - [Active Effects](#active-effects)
  - [Souls & Shop](#souls--shop)
  - [Estus Flask Healing](#estus-flask-healing)
  - [Bonfire & Rest System](#bonfire--rest-system)
  - [New Game Plus](#new-game-plus)
- [Enemies & Bosses](#-enemies--bosses)
- [Story & World](#-story--world)
  - [Story Architecture](#story-architecture)
  - [Branching Paths](#branching-paths)
  - [The Shadow Realm](#the-shadow-realm)
  - [Story Flowchart (Overview)](#story-flowchart-overview)
  - [Story Flowchart (Detailed)](#story-flowchart-detailed)
- [UI & Immersion](#-ui--immersion)
- [Audio System](#-audio-system)
- [Deployment](#-deployment)
- [Testing](#-testing)
- [Known Issues & Future Enhancements](#-known-issues--future-enhancements)
- [Credits](#-credits)

---

## 📖 The Inspiration

I have loved dark fantasy games — *Dark Souls*, *Elden Ring*, *Demon's Souls* — for a long time, but the root of this project goes further back. As a child, I was captivated by Ian Livingstone's *Fighting Fantasy* gamebooks: those *Choose Your Own Adventure* paperbacks where you played a lone hero navigating a monster-filled dungeon, making branching choices that led to wildly different outcomes, and rolling dice for turn-based combat that could end your run in an instant.

I wanted to build something in that spirit — a modern, web-based version of those gamebooks, where your choices genuinely matter, where the world feels dark and atmospheric, and where the combat has enough tactical depth to make each fight feel meaningful. *Elden Souls* is that project: a text adventure with 137 chapters of branching story, ten distinct character classes (six available from the start, four unlockable through play) each with unique stat builds and abilities, a full turn-based combat system with dodge, block, and dual special moves, boss fights with phase changes, a secret hidden realm, New Game+, and a gothic visual style inspired by FromSoftware's art direction.

The game started as a pure Python console project and grew into a full Flask web application — a journey that taught me an enormous amount about OOP, session handling, HTMX, modular CSS, and what it actually takes to build something that feels *finished*.

---

## 🎯 Project Purpose

*Elden Souls* was built to demonstrate Python programming fundamentals in a genuinely engaging context: object-oriented design, session-based state management, modular code architecture, branching data structures, and web deployment via Flask and Heroku. The game is designed to engage players in exploration, decision-making, and tactical combat — mirroring the grim fantasy tone of *Elden Ring* and *Dark Souls* while carving out its own lore and world.

---

## ✨ Features at a Glance

- 10 playable classes — 6 available from the start, 4 unlockable through play — each with distinct stats, lore, and **dual special abilities**
- 137 story chapters across the main path, two optional branches, and a hidden Shadow Realm
- 171+ choice-to-chapter mappings in a flat JSON dictionary, hot-reloaded on every choice
- Turn-based combat: attack, dodge, block, Estus Flask, primary special, secondary special
- 13 regular enemies with distinct damage types (physical, magic, mixed)
- 18 bosses — 10 on the main path, 2 in optional story branches, 6 exclusive to the Shadow Realm
- Two-phase boss fights with mid-battle lore reveals and increased damage
- Active combat effects: damage-over-time (bleed/poison), attack buffs, damage shields, stun, life leech, parry/counter, gambled heals
- New Game+ — two modes (fresh class or carry your build forward), capped soul carryover, scaling enemies
- Soul rewards from every encounter, spent in an in-world shop on permanent upgrades
- Starting gift system — a unique item chosen at the start of each run
- Bonfire rest system — restore HP and Estus, with a rotating selection of atmospheric background images
- Secret Shadow Realm — a hidden optional route accessed via a glowing map icon appearing randomly on story chapters
- Victory and Death overlays — animated banners in sync with their respective SFX before redirect
- In-place HTMX story navigation — smooth chapter-to-chapter transitions with no page reload, so the background video never restarts
- Cross-run lifetime stats — "N journeys have ended here before yours" banner on the title screen
- Looping background video on desktop (static fallback on mobile)
- Responsive design: 5-file CSS split using custom properties, HTMX battle fragment, animated class select carousel that scales up to 5 cards on large/ultrawide screens
- Audio system: background music, combat sound effects, Estus flask audio, per-area tracks
- 143-test automated suite (`pytest`) covering story integrity, save migration, and structural validation

---

## 🛠 Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3.11 / Flask (session-based, no database) |
| Templates | Jinja2 |
| Partial updates | HTMX 1.9.12 |
| CSS | 5 split files using CSS custom properties |
| JavaScript | Vanilla JS — 11 standalone modules |
| Story data | JSON chapters (0–147) + flat `choices_mapping.json` |
| Deployment | Heroku (gunicorn) |
| Fonts | Mantinia (custom woff), Google Fonts (Cinzel) |
| Icons | Font Awesome |

---

## 📁 File Structure

```
elden_souls/
├── run.py
├── Procfile
├── requirements.txt
├── .python-version
├── .gitignore
│
└── app/
    ├── __init__.py
    ├── classes.py              ← Single source of truth for all class definitions
    ├── enemies.py              ← ENEMIES list + BOSSES dict (with phase2 lore)
    ├── combat.py               ← BattleManager class — full dual special + active effects
    ├── config.py               ← MP costs, cooldowns, backgrounds, REST_BGS, SHOP_ITEMS
    ├── models.py               ← Character / Enemy model classes
    ├── save_load.py            ← Session and JSON save/load logic
    │
    ├── routes/
    │   ├── __init__.py
    │   ├── game_routes.py      ← Story/game flow, secret map logic, shadow realm routes
    │   ├── battle_routes.py    ← Combat loop, specials, active effects, victory redirect
    │   └── shop_routes.py      ← Soul spending, upgrades
    │
    ├── story/
    │   ├── __init__.py
    │   ├── story_engine.py     ← choose_path() — loads mapping fresh from disk each call
    │   ├── story_loader.py
    │   ├── choices_mapping.json  ← 171+ entries: choice key → chapter ID
    │   └── chapters/           ← 0.json through 147.json (with some gaps)
    │
    ├── static/
    │   ├── css/
    │   │   ├── base.css        ← :root tokens, resets, typography
    │   │   ├── animations.css  ← keyframes, transitions, pulse effects
    │   │   ├── components.css  ← reusable UI components (buttons, cards, HUD)
    │   │   ├── battle.css      ← battle-screen layout and effect pills
    │   │   └── pages.css       ← page-specific overrides (index, shop, status, etc.)
    │   │
    │   ├── js/
    │   │   ├── audio_manager.js    ← Central audio routing and volume control
    │   │   ├── battle_sounds.js    ← Combat SFX triggers
    │   │   ├── battle_timer.js     ← Turn timer countdown UI
    │   │   ├── carousel.js         ← Class select carousel (3/2/1 cards per breakpoint)
    │   │   ├── char_select_music.js← Music autoplay on class select screen
    │   │   ├── ember_particles.js  ← Particle effect on bonfire/rest screens
    │   │   ├── lightbox.js         ← Shadow Realm map lightbox overlay
    │   │   ├── settings.js         ← In-game settings panel (volume, SFX toggles)
    │   │   ├── sound.js            ← Core sound playback helper
    │   │   ├── title_intro.js      ← Animated title screen intro sequence
    │   │   └── typewriter.js       ← Typewriter effect for story text
    │   │
    │   ├── fonts/
    │   │   └── Mantinia.woff
    │   │
    │   ├── images/
    │   │   ├── areas/              ← Background images (battle, bonfire, landing)
    │   │   ├── bosses/             ← Boss portrait images
    │   │   ├── classes/            ← Class portrait images (knight, mage, rogue, archer, paladin, necromancer)
    │   │   ├── enemies/            ← Enemy portrait images
    │   │   └── screenshots/        ← README screenshots
    │   │
    │   └── sounds/                 ← SFX and background music tracks
    │
    └── templates/
        ├── index.html              ← Character select / title screen
        ├── game.html               ← Main story screen
        ├── battle.html             ← Full battle page
        ├── battle_fragment.html    ← HTMX partial — battle state update
        ├── _battle_hud.html        ← Shared HUD partial (HP/MP bars, effect pills)
        ├── shop.html               ← Soul shop
        ├── status.html             ← Character status screen
        ├── bestiary.html           ← Enemy and boss bestiary
        └── death.html              ← Death screen
```

---

## 🚀 How to Run Locally

**1. Clone the repository**

```bash
git clone https://github.com/TGOSS1984/text_adventure_game.git
cd text_adventure_game
git checkout refactor/css-js-cleanup
```

**2. Set up a virtual environment**

```bash
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
```

**3. Install dependencies**

```bash
pip install -r requirements.txt
```

**4. Run the application**

```bash
python run.py
```

Visit [http://127.0.0.1:5000](http://127.0.0.1:5000) in your browser.

> **Note:** The story engine loads `choices_mapping.json` fresh from disk on every choice, so you can add new chapter mappings without restarting the server.

---

## ⚔️ Game Mechanics

### Character Classes

Ten classes exist in total — six available from the start, and four unlockable through play. Every class is fully defined in `classes.py` as the single source of truth — stats, special moves, lore, assets, and combat modifiers all live in one place.

**Starting classes:**

| Class | HP | MP | Phys ATK | Magic ATK | Phys DEF | Magic DEF | Dodge | Block | Crit | Damage Type | Primary Special | Secondary Special |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Knight | 160 | 80 | 17 | — | 15 | 10 | 20% | 75% | 20% | Physical | Shield Bash | War Cry |
| Mage | 110 | 120 | — | 28 | 6 | 18 | 60% | 40% | 30% | Magic | Arcane Burst | Nullfield |
| Rogue | 130 | 100 | 22 | — | 8 | 6 | 70% | 50% | 40% | Physical | Smoke Screen | Backstab |
| Archer | 140 | 100 | 20 | — | 10 | 8 | 50% | 60% | 50% | Physical | Mark Target | Poison Arrow |
| Paladin | 150 | 90 | 18 | 18 | 12 | 14 | 40% | 70% | 20% | Mixed | Healing Light | Hammer of Justice |
| Necromancer | 100 | 130 | — | 24 | 10 | 22 | 55% | 50% | 25% | Magic | Raise the Dead | Soul Leech |

**Unlockable classes:**

| Class | HP | MP | Phys ATK | Phys DEF | Magic DEF | Dodge | Block | Crit | Damage Type | Primary Special | Secondary Special | Unlock Condition |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Wretch | 120 | 90 | 16 | 8 | 8 | 45% | 50% | 30% | Physical | Desperate Strike | Fortune's Favour | *Always available — no condition* |
| Barbarian | 170 | 70 | 24 | 10 | 6 | 25% | 55% | 25% | Physical | Berserker Rage | Feel No Pain | Complete the main story (any ending) |
| Samurai | 135 | 110 | 23 | 12 | 7 | 55% | 55% | 45% | Physical | Iaijutsu | Iron Stance | Defeat Mesmereth in the Shadow Realm |
| Hunter | 125 | 100 | 21 | 9 | 7 | 60% | 40% | 45% | Physical | Trick Weapon | Hunter's Mark | Complete a New Game+ run (any mode, any ending) |

Locked classes still appear on the Bestiary's Classes tab with full portrait, lore, stats, and both specials visible behind a lock badge — a teaser for what's waiting to be unlocked.

**Knight** — An ironclad brawler built to absorb punishment. High HP and defense, and the highest block reduction in the game (75% damage reduced). Slow to dodge at just 20% but unmatched in sustained durability. Lore: *Once a sentinel of the Sunken Citadel, their oath was not broken — only forgotten. Clad in rusted honour, they march through death unbent.*

**Mage** — A glass cannon who ignores physical armour entirely. Lowest HP in the game alongside the Necromancer, but the highest dodge chance (60%) and the highest raw magic attack (28). Devastating in offense, paper-thin in defense. Lore: *Bearer of forbidden glintfire, the Mage whispers truths carved in starlight. Each spell flung is a shard of a dream long devoured.*

**Rogue** — A skirmisher built on aggression and evasion. The highest dodge chance of any physical class (70%) and a strong crit chance (40%), with a bleed-applying Backstab secondary. Best used to evade incoming hits and chip enemies down before they can respond. Lore: *Born in the shadow of the Ashen Spires, the Rogue strikes like regret — unseen, swift, and final.*

**Archer** — A precision specialist and the deadliest critter in the game (50% crit chance — the highest on the roster). Mark Target guarantees a critical hit; Poison Arrow stacks damage-over-time for 5 turns. Effective at killing enemies before they close the distance. Lore: *From the ruins of Eldergrove they come, eyes hollow with distant wars. Each arrow loosed is a memory exiled into the dark.*

**Paladin** — A hybrid warrior who deals both physical and magic damage, the only class to do so. Well-rounded stats with solid defense on both types, a healing primary special, and a stun secondary. The most forgiving class for new players. Lore: *Oathbound to a god who no longer answers, the Paladin carries faith as a weapon and a wound.*

**Necromancer** — The highest-risk, highest-reward class. Tied for lowest HP in the game (100) but compensated by the highest magic defense (22), a 55% dodge chance, and the largest MP pool (130). Soul Leech heals for 150% of damage dealt and can completely turn a losing fight around. Lore: *They do not fear death. They have spoken to it, bargained with it, and worn its face as a mask.*

**Wretch** — The chaos pick, available from the very first run with no unlock required. Deliberately mediocre base stats; the risk/reward lives entirely in the specials — Desperate Strike is a flat random roll (5–60 damage) with zero stat scaling, win or lose entirely on luck. Fortune's Favour is a 50/50 coin flip: a big heal, or a smaller one plus a fury buff as a consolation prize. Lore: *They arrived at the Ashen Ruins with nothing — no name, no weapon, no plan. Somehow, they are still here. The world has not decided what to do with them yet. Neither have they.*

**Barbarian** — Unlocked by finishing the main story once, on any ending. Overwhelms rather than endures — Berserker Rage stacks an attack buff and a heal-over-time at once, and Feel No Pain grants full damage immunity for 2 turns, the only 100% damage shield in the game. Lore: *There are no tactics in the Barbarian's eyes — only the arithmetic of force. They have broken every chain that tried to hold them, including their own mercy.*

**Samurai** — Unlocked by defeating Mesmereth, the Shadow Realm's final boss. The highest crit chance of any physical class (45%) paired with a unique parry mechanic — Iron Stance halves incoming damage *and* auto-counters every hit landed against you for 3 turns. Iaijutsu lands two full-power strikes in one special. Lore: *They do not seek battle. Battle finds them, as it always has, and they meet it the same way every time — calmly, completely, and without regret. The blade has been drawn ten thousand times. It has never been drawn wrong.*

**Hunter** — Unlocked by completing a New Game+ run. A Bloodborne-inspired evasion build with the lowest block of any physical class (40%) — built to never get hit rather than shrug it off. Trick Weapon is the hardest-hitting physical special in the game (2.5× attack) with a stun; Hunter's Mark drains life back on every hit. Lore: *From the fog-choked streets of a city that no longer exists, the Hunter carries a weapon that remembers every kill it has ever made. The cleaver folds. The blunderbuss clicks. The hunt does not end — it only changes shape.*

---

### Starting Gifts

At the start of each run, players choose one starting gift — a unique bonus item that carries forward into the adventure.

| Gift | Effect |
|---|---|
| Estus +1 | Begin with 6 Estus Flasks instead of 5 |
| Hunter's Charm | +5% critical hit chance |
| Iron Talisman | +3 defense |
| Witch's Ember | +3 attack |
| Old Coin | Start with 200 bonus souls |
| Life Ring | +15 max HP |
| Fading Soul | No bonus — for those who seek no advantage |

---

### Combat System

Every battle is turn-based. On each turn the player selects one action, then the enemy responds.

**Player Actions:**

- **Attack** — Standard strike. Damage is calculated from the player's relevant attack stat (physical or magic), reduced by the enemy's relevant defense stat, with a physical penetration factor (55% of defense bypassed) to prevent defence from becoming a wall. Crits are rolled per-turn using the class's `crit_chance` — a successful crit applies `crit_multiplier` (1.5× for most classes). Attacking also regenerates 25 MP.

- **Dodge** — Attempt to avoid all incoming damage for the turn. Success is based on the class's `dodge_chance` (20% to 60%). A failed dodge means full incoming damage lands with no reduction. High-dodge classes like the Mage and Rogue should use this aggressively.

- **Block** — Reduce incoming damage by the class's `block_multiplier`. The Knight reduces incoming damage to just 25% of the hit (a 75% reduction — the best block in the game); the Mage lets 60% through (a 40% reduction), with other classes falling between. Blocking never fails — but it also provides no damage output.

- **Use Estus Flask** — Consume one flask to heal 70% of max HP. Estus is a finite resource (5 flasks per run, refilled at bonfires). The screen pulses green with rising bubble animations when a flask is used.

**Enemy Attack Types:**

Enemies use three attack patterns, weighted by probability:
- **Standard attack** (most common) — normal damage roll
- **Massive attack** (uncommon) — heavy single hit, telegraphed to the player
- **Flurry attack** (rare) — rapid multi-hit sequence; the screen pulses red during a flurry

The damage type of an attack (physical vs. magic) is determined by the enemy's `damage_type` field — enemies can be physical, magic, or mixed. Player defense stats apply accordingly, so a Mage's high magic defense is actually useful against magic enemies, even if their physical defense is paper-thin.

**Boss Phase 2:**

When a boss drops to 50% HP, Phase 2 triggers. A dramatic lore reveal message fires in the battle log, the boss's damage multiplier increases by 20%, and attack weights shift toward heavier hits. Phase 2 is a significant gear-check — players who have not managed their Estus or specials carefully will feel the pressure.

---

### Dual Specials System

Every class has two special abilities that share a single cooldown pool and a shared MP bar.

- **Primary Special** — costs 50 MP, cooldown 4–5 turns
- **Secondary Special** — costs 35 MP, uses the same shared cooldown

When either special fires, both buttons grey out simultaneously and display a countdown timer `(X)`. Players must choose between using the cheaper secondary to conserve MP, or saving for the primary's bigger effect.

| Class | Primary Special | Secondary Special |
|---|---|---|
| Knight | 🛡 Shield Bash — normal damage + stun | ⚔ War Cry — +25% attack and +20% defense for 3 turns |
| Mage | ✨ Arcane Burst — 2× magic, ignores armour | 🔮 Nullfield — 50% incoming damage blocked for 3 turns |
| Rogue | 💨 Smoke Screen — attack + dodge buff | 🗡 Backstab — 0.5× hit + bleed (3.5% max HP/turn × 4 turns) |
| Archer | 🎯 Mark Target — 2× guaranteed crit | 🏹 Poison Arrow — 3% enemy max HP poison/turn × 5 turns |
| Paladin | ✝ Healing Light — 40% HP restore + stun | 🔨 Hammer of Justice — 1.5× mixed damage + stun |
| Necromancer | 💀 Raise the Dead — 2.5× magic burst | 💉 Soul Leech — 1.5× magic + heal 150% of damage dealt (min 12% max HP) |
| Wretch | 🎲 Desperate Strike — random 5–60 damage, no stat scaling | 🪙 Fortune's Favour — 50% chance: heal 50% HP. 50% chance: small heal + 20% attack buff for 2 turns |
| Barbarian | 💢 Berserker Rage — +25% attack for 3 turns AND heal 5% max HP/turn for 3 turns | 🗿 Feel No Pain — 100% incoming damage blocked for 2 turns |
| Samurai | ⚔ Iaijutsu — two strikes, each at full attack power | 🛡 Iron Stance — 50% incoming damage blocked for 3 turns AND auto-counter 50% attack on every hit landed |
| Hunter | 🪓 Trick Weapon — 2.5× attack + stun | 🩸 Hunter's Mark — 1.5× attack, heal equal to damage dealt (min 10% max HP) |

MP regenerates by 25 per standard attack. Running low on MP means falling back on basic attacks while the cooldown ticks down — a deliberate resource tension.

The four unlockable classes introduce new special-effect types beyond the original roster: `combo_buff_hot` (a buff and a heal-over-time fired by the same special), `double_hit` (two full attacks in one special), `random_hit` (pure chance damage with no stat scaling at all), `parry` (a damage shield that also auto-counters), and `gamble_heal` (a 50/50 coin-flip heal).

---

### Active Effects

Secondary specials can apply persistent status effects that are tracked across turns and displayed as colour-coded pills in the battle HUD:

- **Damage Over Time** 🔴 — Bleed or Poison ticks at the start of each player turn for a set number of turns. Labels and messages are configurable in `config.py`.
- **Attack Buff** 🟡 — A flat or percentage bonus is added to the player's attack (and sometimes defense) for a set number of turns, then expires naturally with a message in the battle log.
- **Damage Shield** 🩵 — A percentage of incoming damage is absorbed. The Mage's Nullfield absorbs 50% of all incoming damage for 3 turns; the Barbarian's Feel No Pain absorbs 100% for 2 turns.
- **Parry / Counter** ⚔ — The Samurai's Iron Stance combines a damage shield with an automatic counter-attack on every hit landed against the player while it's active.
- **Stun** — Prevents the enemy from counterattacking on the turn it is applied.
- **Life Leech** — Soul Leech and Hunter's Mark heal the player based on damage dealt, enabling dramatic mid-fight recoveries.
- **Gambled Heal** — The Wretch's Fortune's Favour is a 50/50 coin flip between a large heal and a smaller one plus a consolation attack buff.

---

### Souls & Shop

Every defeated enemy drops a soul reward, calculated from a formula balancing HP and attack difficulty. Bosses drop substantially more. Souls accumulate across the run and are spent in the in-world shop, accessible at bonfire rest points.

**Shop Items:**

| Item | Effect | Cost |
|---|---|---|
| Estus Refill | Restore all Estus Flasks | 150 souls |
| Cracked Red Shard | +3 attack (permanent) | 225 souls |
| Cracked Blue Shard | +3 defense (permanent) | 200 souls |
| Vessel of Embers | +20 max HP (permanent) | 275 souls |
| Greater Vessel of Embers | +30 max HP (permanent) | 400 souls |
| Wraith-Step Pendant | +5% dodge chance (permanent) | 260 souls |
| Ironwall Talisman | Block damage reduced a further 5% (permanent) | 225 souls |
| Sharpened Crit Stone | +5% crit chance (permanent) | 260 souls |
| Executioner's Lens | +0.25× crit damage multiplier (permanent) | 325 souls |

The three percentage-based upgrades (Wraith-Step Pendant, Ironwall Talisman, Sharpened Crit Stone) are capped at a lifetime maximum of +15% above the class's base value, enforced in `shop_routes.py` — this matters most across New Game+ runs, where repeated purchases could otherwise stack indefinitely.

Mid-to-late-game boss HP values are scaled to expect 2–3 shop upgrades — particularly the Ember Tyrant (320 HP), Cindergloom (380 HP in the rebalanced version), and Mesmereth (420 HP).

---

### Estus Flask Healing

Players begin with 5 Estus Flasks (or 6 with the Estus +1 gift). Each flask restores 70% of the character's maximum HP. Flasks are consumed permanently until the player rests at a bonfire, where they are fully refilled. Managing Estus across a boss fight is the primary survival challenge — spending too early risks running dry in Phase 2.

---

### Bonfire & Rest System

When a story chapter has the `rest: true` flag, the player enters a bonfire rest screen. Resting:

- Fully restores HP
- Refills all Estus Flasks
- Gives access to the soul shop
- Sets a randomised atmospheric background image from the `REST_BGS` pool (Firelink Shrine, and four bonfire variants)

The active rest background is stored per-session as `session["rest_bg"]` and rendered via a CSS custom property `var(--rest-bg)` set inline on `<body>`. The bonfire screen includes ember particle animations for atmosphere.

---

### New Game Plus

Completing any ending unlocks two ways to begin again with carried-over progress:

- **New Journey** — pick a fresh class from scratch. Stats reset to that class's base values.
- **Bearer's Legacy** — keep your current class and every upgraded stat exactly as it stood at the end of the run, including shop upgrades.

Both modes:
- Cap souls carried into the new run at 600 (`NG_PLUS_SOUL_CAP`) — anything above that is discarded, with a flash message confirming how much carried over
- Scale every enemy: **+35% HP**, **+20% attack/magic attack**, and **+25% soul reward** per New Game+ level (so NG+2 enemies are scaled at double those percentages, and so on)
- Skip the starting-gift screen entirely — no gift is offered on NG+ runs
- Increment `session["ng_plus"]`, which drives a red "Journey N" banner on the title screen for the rest of that run

Completing a NG+ run (either mode, any ending) is the unlock condition for the Hunter class.

---

## 👾 Enemies & Bosses

### Regular Enemies (13)

Encountered randomly during story chapters with the `battle: true` flag. Each enemy has a distinct damage type that interacts with player defense stats.

Hollow Knight, Ash Beast, Wraith, Ghoul, Fallen Soldier, Mimic, Spectral Beast, The Hollow Weaver, Thornveil Knight, Echoing Knight, The Mourning Veil, Carrion Hound, Chitinous Widow.

### Main Path Bosses (10)

| Boss | HP | Type | Soul Reward |
|---|---|---|---|
| Ashen Knight | 240 | Physical | 352 |
| The Mireborn Serpent | 230 | Physical | ~300 |
| The Gravewarden | 230 | Physical | ~310 |
| The Ember Tyrant | 320 | Magic | 430 |
| The Lord of Chains | 220 | Physical | 301 |
| Pale Drake | 250 | Magic | 340 |
| The Blacksteel Sentinel | 250 | Mixed | 320 |
| The Thorn Matriarch | 240 | Magic | ~317 |
| The Abyss Watcher | 230 | Physical | ~309 |
| Cindergloom, Lord of Ashes | 380 | Magic | 350+ |

*(Cindergloom HP shown at rebalanced value. Soul reward boosted by 50% bonus on top of base.)*

There is also **Lothric and Lorian** — a twin-prince optional encounter in the mid-path.

### Optional Branch Bosses (2)

| Boss | HP | Type | Location |
|---|---|---|---|
| Vaelhis, the Unmourned King | 300 | Magic | Frozen Tundra (Ch75–84) |
| The Drowned Sovereign | 330 | Mixed | Sunken City Velundra (Ch85–98) |

### Shadow Realm Bosses (6)

| Boss | HP | Type | Soul Reward |
|---|---|---|---|
| The Starbound Colossus | 340 | Physical | — |
| The Gilded Predator | 310 | Mixed | — |
| The Saintess of Rot | 295 | Magic | — |
| The Moon-Sworn Blade | 320 | Mixed | — |
| Mesmereth, the Serpent Prince | 420 | Mixed | 476 |

All bosses have fully written phase 2 lore stored directly in `enemies.py` alongside their stats. `combat.py` reads `boss["phase2_lore"]` at runtime.

---

## 📖 Story & World

### Story Architecture

The story is built from individual JSON chapter files (`0.json` through `147.json`, with some gaps). Each chapter carries:

- `text` — the narrative prose for that chapter
- `choices` — an array of choice key strings
- `lore` — a separate flavour text sidebar (optional)
- `battle`, `boss`, `rest` — boolean flags that trigger the relevant game mechanic

A flat `choices_mapping.json` dictionary maps every choice key string to its destination chapter ID. This file has 171+ entries and is loaded fresh from disk on every player choice — meaning new story content can be added without restarting the server (a critical bug fix; the previous cached approach meant additions required a full restart to take effect).

### Branching Paths

The main story runs from Chapter 0 through to Cindergloom (the final boss) and three alternate endings. Two optional side branches exist as detours that rejoin the main path after completion:

**Branch 1 — Frozen Tundra (Chapters 75–84)**
Entry from Chapter 3 via the `follow_the_pale_gleam_north` choice. Two combat encounters, two rest points, culminating in a boss fight with Vaelhis, the Unmourned King. Rejoins the main path at Chapter 16.

**Branch 2 — Sunken City Velundra (Chapters 85–98)**
Entry from Chapter 10 via the `engage_the_brass_mechanism` choice. Three combat encounters, two rest points, culminating in a boss fight with The Drowned Sovereign. Rejoins the main path at Chapter 47.

Several previously orphaned chapters (22, 26, 33, 42, 68) have been mapped and connected as part of the refactor.

### The Shadow Realm

A hidden optional route accessible during a normal playthrough. A glowing gold map icon (`#secret-map-btn`) appears on a random selection of 4–8 eligible story chapters per run, fixed in the bottom-right corner with a pulsing animation. Clicking it opens a full-screen lightbox displaying cryptic notes — pressing Enter to the Shadow Realm is a choice the player must consciously make.

**Entry:** POST `/enter_shadow_realm` stores the current chapter as the return point and redirects to Chapter 103.

**Structure — three branching paths, all converging on Mesmereth:**

```
103 (entry) → 104 → 105 (battle) → 106 (REST — 3-way fork)

Path A — Colosseum:       107 → 108 (battle) → 109 (BOSS: Starbound Colossus) → 110 (rest) → 111 → 112
Path B — Dancing Hollows: 120 → 121 (battle) → 122 (BOSS: Gilded Predator)    → 123 (rest) → 112
Path C — Silk Road:       130 → 131 (battle) → 132 (BOSS: Saintess of Rot)    → 133 (rest) → 134 → 113

Convergence: 113 (half-tower) → fork:
  Direct:           114 (battle) → 115 (rest) → 116 → 117 → 118 → 119
  Moon Monastery:   140 → 141 (BOSS: Moon-Sworn Blade) → 142 → 143 → 116

→ 144 (BOSS: Mesmereth, the Serpent Prince) → 145 → 146 → 147 (REST) → Chapter 55 → Chapter 99
```

Completing the Shadow Realm deposits the player at Chapter 99 (the approach to Cindergloom), bypassing some of the main path. The return chapter stored at entry is preserved for players who do not complete the realm.

---

### Story Flowchart (Overview)

```mermaid
graph LR

    START["🔯 Start: Ashen Ruins"]
    START --> B1["💀 Ashen Knight"]
    B1 --> B2["💀 Mireborn Serpent"]
    B1 --> B3["💀 Gravewarden"]
    B1 --> B4["💀 Ember Tyrant"]

    B2 --> Hub1["⛩️ Chapel of Thorns"]
    B3 --> Hub1
    B4 --> Hub1

    Hub1 --> B5["💀 Lord of Chains"]
    Hub1 --> B6["💀 Pale Drake"]
    Hub1 --> B7["💀 Blacksteel Sentinel"]

    B5 --> Hub2["🌿 Cradle of Thorns"]
    B6 --> Hub2
    B7 --> Hub2

    Hub2 --> B8["💀 Thorn Matriarch"]
    B8 --> B9["💀 Abyss Watcher"]
    B9 --> FINAL["💀 Cindergloom, Lord of Ashes"]

    FINAL --> END1["🌅 Dawn of Flame"]
    FINAL --> END2["🌑 Age of Shadows"]
    FINAL --> END3["♻️ The Cycle Continues"]

    START -->|Optional| BRANCH1["❄️ Frozen Tundra\n💀 Vaelhis"]
    START -->|Optional| BRANCH2["🌊 Sunken City Velundra\n💀 Drowned Sovereign"]
    Hub1 -->|Hidden| SHADOW["🌑 Shadow Realm\n5 Bosses + Mesmereth"]
```

---

### Story Flowchart (Detailed)

```mermaid
graph TD

%% --- START ---
START["🔯 Awaken in Ashen Ruins"]
START -->|"Step into the smoldering remains"| R1C1["Ch1: Ashen Ruins I"]
START -->|"Dive into the drowned road"| R11C1["Ch: Drowned Village"]
R1C1 -->|"Search the scorched bones"| R1C2["Ch2: Ashen Ruins II"]
R1C2 -->|"Wander deeper"| R1C3["Ch3: Ashen Ruins III"]
R1C3 -->|"Follow the stench of rot"| R1A["→ Weeping Marsh"]
R1C3 -->|"Descend into the tomb-mouth"| R1B["→ Hollow Catacombs"]
R1C3 -->|"Climb the forgotten ledge"| R1C["→ Obsidian Peaks"]
R1C3 -->|"Follow the pale gleam north"| BRANCH1["❄️ Frozen Tundra Ch75–84"]
R1C3 -->|"Kneel before the flame"| BON1["🔥 Bonfire – R1"]
BON1 -->|"Confront the Ashen Knight"| B1["💀 Boss: Ashen Knight"]

%% --- FROZEN TUNDRA BRANCH ---
BRANCH1 --> TUN1["Ch75–84: Tundra path"]
TUN1 --> BOSS_VAE["💀 Boss: Vaelhis the Unmourned King"]
BOSS_VAE -->|"Rejoin"| R1C16["Ch16"]

%% --- REGION 2: Weeping Marsh ---
R1A -->| | R2C1["Ch: Weeping Marsh I"]
B1 --> R2C1
R2C1 -->|"Step beneath the hanging moss"| R2C2["Ch: Marsh II ⚔️"]
R2C2 -->|"Cross the sinking path"| R2C3["Ch: Marsh III"]
R2C3 -->|"Rest among drowned bones"| BON2["🔥 Bonfire – R2"]
BON2 -->|"Challenge the Mireborn Serpent"| B2["💀 Boss: Mireborn Serpent"]
B2 --> HubEntry["⛩ Path of Thorns"]

%% --- REGION 3: Hollow Catacombs ---
R1B --> R3C1["Ch: Hollow Catacombs I"]
B1 --> R3C1
R3C1 -->|"Descend the winding ossuary"| R3C2["Ch: Catacombs II"]
R3C2 -->|"Traverse the broken graves ⚔️"| R3C3["Ch: Catacombs III"]
R3C3 -->|"Pass beneath the chained dead"| R3C4["Ch: Catacombs IV"]
R3C4 -->|"Kindle the tombfire"| BON3["🔥 Bonfire – R3"]
BON3 --> B3["💀 Boss: Gravewarden"]
B3 --> HubEntry

%% --- REGION 4: Obsidian Peaks ---
R1C --> R4C1["Ch: Obsidian Peaks I"]
B1 --> R4C1
R4C1 -->|"Cross the blackened ridge"| R4C2["Ch: Peaks II"]
R4C2 -->|"Climb the scorched spire ⚔️"| R4C3["Ch: Peaks III"]
R4C3 -->|"Rest beside the magma fissure"| BON4["🔥 Bonfire – R4"]
BON4 --> B4["💀 Boss: Ember Tyrant"]
B4 --> Hub1

%% --- SUNKEN CITY BRANCH ---
R4C3 -->|"Engage the brass mechanism"| BRANCH2["🌊 Sunken City Ch85–98"]
BRANCH2 --> BOSS_DROWN["💀 Boss: Drowned Sovereign"]
BOSS_DROWN -->|"Rejoin"| Ch47["Ch47"]

%% --- HUB 1: Chapel of Thorns ---
HubEntry --> Hub1["⛩️ Central Hub: Chapel of Thorns"]
Hub1 -->|"Ascend the northern stair"| R5C1["Ch: Shattered Keep"]
Hub1 -->|"Venture down the eastern gorge"| R6C1["Ch: Forgotten Valley"]
Hub1 -->|"Slip south through bramble"| R7C1["Ch: Iron Bastion"]

%% --- SHADOW REALM ACCESS ---
Hub1 -.->|"🗺 Secret Map Icon (random chapters)"| SHADOW["🌑 Enter Shadow Realm"]
SHADOW --> SR103["Ch103: Shadow Realm Entry"]
SR103 --> SR106["Ch106: REST — 3-way fork"]
SR106 -->|"Path A"| SR_A["Ch107→108⚔️→109💀 Starbound Colossus→110→111→112"]
SR106 -->|"Path B"| SR_B["Ch120→121⚔️→122💀 Gilded Predator→123→112"]
SR106 -->|"Path C"| SR_C["Ch130→131⚔️→132💀 Saintess of Rot→133→134→113"]
SR_A --> SR113
SR_B --> SR113
SR_C --> SR113
SR113["Ch113: Half-Tower — fork"]
SR113 -->|"Direct"| SR114["Ch114⚔️→115→116→117→118→119"]
SR113 -->|"Moon Monastery"| SR140["Ch140→141💀 Moon-Sworn Blade→142→143→116"]
SR114 --> SR144
SR140 --> SR144
SR144["💀 Ch144: Mesmereth the Serpent Prince"]
SR144 --> SR147["Ch145→146→147 REST"]
SR147 -->|"Return"| Ch55["Ch55 → Ch99 → Cindergloom"]

%% --- REGION 5: Shattered Keep ---
R5C1 -->|"Enter the echoing hall ⚔️"| R5C2["Keep II ⚔️"]
R5C2 -->|"Cross the splintered drawbridge"| R5C3["Keep III"]
R5C3 -->|"Light the brazier of ruin"| BON5["🔥 Bonfire – R5"]
BON5 --> B5["💀 Boss: Lord of Chains"]
B5 --> Cross1["⚔ Path Convergence"]

%% --- REGION 6: Forgotten Valley ---
R6C1 -->|"Step through the whispering fog"| R6C2["Valley II"]
R6C2 -->|"Traverse the gnarled roots ⚔️"| R6C3["Valley III ⚔️"]
R6C3 -->|"Collapse near the old cairn"| BON6["🔥 Bonfire – R6"]
BON6 --> B6["💀 Boss: Pale Drake"]
B6 --> Cross1

%% --- REGION 7: Iron Bastion ---
R7C1 -->|"March through rusted gates ⚔️"| R7C2["Bastion II ⚔️"]
R7C2 -->|"Cross the molten forge"| R7C3["Bastion III"]
R7C3 -->|"Find solace in the furnace alcove"| BON7["🔥 Bonfire – R7"]
BON7 --> B7["💀 Boss: Blacksteel Sentinel"]
B7 --> Cross1

%% --- HUB 2: Cradle of Thorns ---
Cross1 -->|"Tear through the thornveil"| R8C1["Ch: Cradle of Thorns I"]
R8C1 -->|"Step into the vine maze ⚔️"| R8C2["Thorns II"]
R8C2 -->|"Collapse beneath a root pyre"| BON8["🔥 Bonfire – R8"]
BON8 --> B8["💀 Boss: Thorn Matriarch"]
B8 --> Hub2["🌿 Second Crossroads"]

%% --- REGION 9 & 10 ---
Hub2 -->|"Descend into the abyss"| R9C1["Ch: Abyssal Sanctum I"]
R9C1 -->|"Step beyond the veil ⚔️"| R9C2["Sanctum II ⚔️"]
R9C2 -->|"Kneel beneath the obsidian sky"| BON9["🔥 Bonfire – R9"]
BON9 --> B9["💀 Boss: Abyss Watcher"]
B9 --> Ch55

Hub2 -->|"Ascend the forgotten tower"| R10C1["Ch: Forgotten Citadel I"]
R10C1 -->|"Step through shattered court ⚔️"| R10C2["Citadel II ⚔️"]
R10C2 -->|"Cross the frostbound gallery"| R10C3["Citadel III"]
R10C3 -->|"Offer ashes to the flame"| BON10["🔥 Bonfire – R10"]
BON10 --> FINAL["💀 Final Boss: Cindergloom, Lord of Ashes"]

Ch55 --> FINAL

%% --- ENDINGS ---
FINAL -->|"Embrace the Flame"| END1["🌅 Dawn of Flame"]
FINAL -->|"Snuff the Light"| END2["🌑 Age of Shadows"]
FINAL -->|"Let the Cycle Turn"| END3["♻️ The Cycle Continues"]

%% --- OPTIONAL REGIONS ---
R11C1 -->|"Confront the sunken dead ⚔️"| R11C2["Drowned Village II ⚔️"]
R11C2 -->|"Light the waterlogged shrine"| BON11["🔥 Bonfire – R11"]
BON11 --> B1

Hub1 -->|"Fade into the spectral woods"| R12C1["Ch: Spectral Woods"]
R12C1 -->|"Follow whispers"| R12C2["Spectral Woods II"]
R12C2 -->|"Ignite the ghostfire"| BON12["🔥 Bonfire – R12"]
BON12 --> R6C3

Hub2 -->|"Scale the Tower of Whispers"| R13C1["Ch: Tower of Whispers I"]
R13C1 -->|"Echo through hollow heights ⚔️"| R13C2["Tower II ⚔️"]
R13C2 -->|"Rest beneath the singing spire"| BON13["🔥 Bonfire – R13"]
BON13 --> R10C2

R4C3 -->|"Plunge into molten depths"| R14C1["Ch: Molten Depths"]
R14C1 -->|"Cross the lava tomb"| R14C2["Depths II"]
R14C2 -->|"Collapse near ember altar"| BON14["🔥 Bonfire – R14"]
BON14 --> B4

R3C2 -->|"Wander the echoing hall"| R15C1["Ch: Halls of Echo"]
R15C1 -->|"Descend into screaming dark ⚔️"| R15C2["Halls II ⚔️"]
R15C2 -->|"Rest in the void chamber"| BON15["🔥 Bonfire – R15"]
BON15 --> R5C2
```

---

## 🎨 UI & Immersion

**Background Video**
A looping bonfire video (`dark-souls-bonfire.mp4`) plays as a fixed full-screen background element on the story and death screens, fading in smoothly on `canplaythrough`. On mobile (max-width 768px) the video is hidden and a static atmospheric image (`bonfire.jpg`) is shown instead via a CSS media rule — preventing layout and performance issues on smaller devices.

**CSS Architecture**
The original monolithic `style.css` has been split into five purpose-separated files, loaded in this order:

1. `base.css` — CSS custom properties (`:root` tokens), resets, typography, colour system
2. `animations.css` — all `@keyframes`, transitions, pulse effects, and particle animations
3. `components.css` — reusable UI components: buttons, cards, HUD, battle layout
4. `battle.css` — battle-specific layout, effect pills, special button states
5. `pages.css` — page-specific overrides (index, shop, status, bestiary, death)

Token values are defined in `base.css` `:root` and include:
- `--clr-special: #c9a227` — primary special gold
- `--clr-special2: #5dade2` — secondary special teal
- `--clr-hp: #c0392b` — HP bar red
- `--clr-mp: #2980b9` — MP bar blue

**HTMX Battle Fragment**
The battle screen uses HTMX 1.9.12 to update only the battle state partial (`battle_fragment.html`) on each turn — no full page reloads. The `_battle_hud.html` partial handles the HP/MP bars and active effects strip. HTMX's `htmx:beforeOnLoad` (not `htmx:beforeRedirect`, which does not work in v1.9.x) is used to intercept the `HX-Redirect` header and show the Victory Overlay before navigating.

**HTMX Smooth Story Navigation**
Story-chapter-to-story-chapter choices also swap in place via HTMX (`#story-content`, swapped against `game_fragment.html`) instead of triggering a full page reload — the persistent background video, menu, and audio controls live in a shell around the swap target and are never destroyed, so the video plays continuously across a sequence of chapter clicks rather than restarting from frame 0 every time. Transitions into or out of a rest chapter, or into a battle, still do a full reload by design, since the background is genuinely meant to change there. A `_render_chapter()` helper is the single source of truth used by both the full-page GET path and the in-place fragment path, so the two can never drift out of sync.

**Victory & Death Overlays**
When an enemy's HP reaches 0, the battle loop sets an `HX-Redirect` header. Before the browser follows it, `htmx:beforeOnLoad` fires, displaying an animated "Victory Achieved" overlay — gold text, a faded banner, dark background — in sync with the victory SFX, for 8.5 seconds before allowing the navigation to proceed. When the player's own HP reaches 0 instead, the same mechanism shows a mirrored crimson "You Died" banner in sync with a scream SFX before moving on to the death screen, where `death.mp3` plays separately on its own.

**Class Select Carousel**
The character select screen uses a carousel with responsive card counts: 1 card on the smallest phones, 2 on tablets, 3 on standard desktop screens, scaling up further to 4 cards at 1600px and 5 cards at 2000px+ so ultrawide monitors aren't left with a narrow column and huge unused margins. Cards display class portrait, lore, both special ability names, and core stats — including a lock badge with the unlock condition for the four unlockable classes. `carousel.js` reads the active card count directly from the `--cards-visible` CSS custom property at runtime rather than hardcoding it, so the JS and CSS can never drift out of sync as new breakpoints are added.

**Active Effects Pills**
During battle, active status effects are shown as colour-coded pills in the HUD strip:
- `.effect-pill--dot` — red, shows DoT name and remaining turns
- `.effect-pill--buff` — gold, shows buff name and remaining turns
- `.effect-pill--shield` — teal, shows shield percentage and remaining turns

**Typewriter Effect**
Story text is rendered character-by-character using `typewriter.js`, giving each new chapter the feel of words appearing on a page — matching the pacing of reading a gamebook.

**Ember Particles**
Bonfire and rest screens display an ember particle system (`ember_particles.js`) where glowing particles drift upward from the bottom of the screen, reinforcing the campfire atmosphere.

**Bestiary — Classes Tab**
Alongside the Enemy Codex, the Bestiary has a Classes tab mirroring the same visual pattern: portrait, full stats, lore, and both specials for every one of the ten classes — including the four unlockable ones, shown behind a lock badge with their unlock condition rather than hidden entirely.

**Cross-Run Lifetime Stats**
The title screen shows a small gold banner — "N journeys have ended here before yours" — tracking total completed runs across all sessions via `player_record.json`. It's hidden entirely at zero runs and uses correct singular/plural grammar at exactly one.

**Mobile Responsiveness Pass**
Beyond the carousel breakpoints, a dedicated mobile pass tightened up the battle, character-select, and story screens specifically for phones: the enemy lore disclosure defaults to collapsed on mobile (still open by default on desktop) to save vertical space, the class-stat list switches to a 2-column grid, the story screen's six nav buttons switch from an uneven wrapping row to a clean 2-column grid mirroring the battle screen's own action-button layout, and a global `overflow-x: hidden` safety net plus fluid `clamp()`-based heading sizes prevent the page from becoming horizontally pannable on narrow viewports.

---

## 🎵 Audio System

The audio system is split across multiple modules:

- `audio_manager.js` — central controller for routing background music and managing volume levels
- `battle_sounds.js` — triggers combat SFX (hit sounds, special ability effects, death stings) on the relevant HTMX events
- `sound.js` — core playback helper with fade-in/fade-out support
- `char_select_music.js` — handles music autoplay on the character select screen, respecting browser autoplay policies

An in-game settings panel (accessible during play) provides toggles for background music and SFX, plus volume controls. Settings are persisted per-session.

> **Note:** Secondary special abilities currently reuse the primary special SFX. Unique audio per secondary special is a planned enhancement.

---

## 🚀 Deployment

The application is deployed to Heroku via GitHub integration.

**Procfile**
```
web: gunicorn run:app
```

**Deploy to Heroku**

1. Create a `Procfile` and ensure `gunicorn` is in `requirements.txt`
2. Create a Heroku app and connect your GitHub repository
3. Enable automatic deploys from the target branch
4. Click Deploy Branch

Live demo: [https://elden-souls-text-adventure-app-6406dec306fc.herokuapp.com/](https://elden-souls-text-adventure-app-6406dec306fc.herokuapp.com/)

**Alternative: Render**

```
Build command: pip install -r requirements.txt
Start command: gunicorn run:app
```

---

## 🧪 Testing

### Manual Testing

Throughout development, features were tested iteratively using both in-browser play sessions and Flask terminal print statements.

**General**

| Test | Expected | Result |
|---|---|---|
| Class select — all 6 classes choosable | Each class loads its correct stats and specials into session | ✅ Pass |
| Starting gift applied correctly | Gift stat modifies character session on `/start` | ✅ Pass |
| Story chapter navigation | Choices map to correct chapter IDs via `choices_mapping.json` | ✅ Pass |
| New chapter mappings hot-reload | Adding an entry to `choices_mapping.json` works without server restart | ✅ Pass |
| Branching paths reach correct chapters | Branch 1 rejoins Ch16, Branch 2 rejoins Ch47 | ✅ Pass |
| Orphaned chapter fixes | Ch22, 26, 33, 42, 68 all reachable and correctly mapped | ✅ Pass |

**Combat**

| Test | Expected | Result |
|---|---|---|
| Standard attack damage calculation | Physical/magic damage respects PHYS_PEN and defense values | ✅ Pass |
| Dodge success/failure | Correct probability applied per class; failed dodge takes full damage | ✅ Pass |
| Block damage reduction | Knight blocks 75% of incoming; other classes per their multiplier | ✅ Pass |
| Estus Flask heal | Heals 70% max HP; screen pulses green with bubble animation | ✅ Pass |
| Estus Flask depleted | No heal when flasks reach 0; button disabled | ✅ Pass |
| Primary special fires correctly | 50 MP deducted; correct damage/effect applied; both buttons grey | ✅ Pass |
| Secondary special fires correctly | 35 MP deducted; correct effect applied; shared cooldown triggers | ✅ Pass |
| Cooldown countdown displays | Both special buttons show `(X)` countdown and re-enable at 0 | ✅ Pass |
| Damage-over-time ticks | Bleed/poison ticks at correct intervals with correct messages | ✅ Pass |
| Attack buff applies and expires | +5 attack for N turns, then expire message fires | ✅ Pass |
| Shield reduces incoming damage | Nullfield absorbs 50% for 2 turns | ✅ Pass |
| Soul Leech heals player | Damage dealt is added to player HP; minimum 15 HP applied | ✅ Pass |
| Boss Phase 2 trigger | Fires at 50% HP; lore message displayed; damage ×1.20 applied | ✅ Pass |
| Enemy attack types weighted correctly | Flurry attack rare; standard attack most common | ✅ Pass |
| Flurry attack screen pulse | Screen pulses red during flurry | ✅ Pass |
| Victory Overlay on boss kill | Overlay fires for 2.8s before navigation; death screen unaffected | ✅ Pass |
| Soul rewards accumulate | Each enemy death adds correct soul_reward to session | ✅ Pass |

**Shop & Bonfire**

| Test | Expected | Result |
|---|---|---|
| Rest screen restores HP and Estus | Full HP and full Estus on rest chapter entry | ✅ Pass |
| Rest background randomises | Different bonfire background image shown each rest | ✅ Pass |
| Ember particles display | Particles animate upward on bonfire screen | ✅ Pass |
| Shop deducts souls correctly | Purchase reduces session soul count by item cost | ✅ Pass |
| Permanent upgrades persist | Attack/defense/HP upgrades remain across all subsequent battles | ✅ Pass |
| Estus Refill restores flasks | Flask count resets to max after purchase | ✅ Pass |
| Cannot buy without sufficient souls | Purchase blocked with feedback when souls insufficient | ✅ Pass |

**Shadow Realm**

| Test | Expected | Result |
|---|---|---|
| Secret map icon appears on eligible chapters | Icon visible on 4–8 random story chapters per run | ✅ Pass |
| Icon does not appear on battle/boss/rest chapters | Eligible check correctly excludes non-story chapters | ✅ Pass |
| Lightbox opens on icon click | Full-screen lightbox with cryptic notes displayed | ✅ Pass |
| Enter Shadow Realm stores return chapter | `session["secret_return_chapter"]` set correctly | ✅ Pass |
| All three Shadow Realm paths completable | Path A, B, C each reach Ch112/113 | ✅ Pass |
| Moon Monastery detour reachable | Ch140 accessible and rejoins at Ch116 | ✅ Pass |
| Mesmereth fight triggers at Ch144 | Boss encounter loads correctly | ✅ Pass |
| Leave Shadow Realm returns to stored chapter | Player returned to correct story chapter | ✅ Pass |

**UI & Responsive**

| Test | Expected | Result |
|---|---|---|
| Background video fades in on desktop | `canplaythrough` event triggers smooth fade | ✅ Pass |
| Static bonfire fallback on mobile | Video hidden; `bonfire.jpg` shown at ≤768px | ✅ Pass |
| Class select carousel — desktop | 3 cards visible | ✅ Pass |
| Class select carousel — tablet | 2 cards visible | ✅ Pass |
| Class select carousel — mobile | 1 card visible; max-width 260px enforced | ✅ Pass |
| Active effect pills render correctly | DoT red, buff gold, shield teal — all visible in HUD | ✅ Pass |
| HTMX battle fragment partial update | No full page reload on battle actions | ✅ Pass |
| Typewriter effect on story text | Text appears character-by-character on new chapters | ✅ Pass |

**Code Quality**

| Check | Status |
|---|---|
| PEP8 compliance (`pycodestyle`) | ✅ Pass — all E501, E122, E302, W291, W293 resolved |
| `black` formatting applied | ✅ Pass |
| HTML validator | ✅ Pass (Flask/Jinja2 syntax excluded as expected) |
| CSS validator | ✅ Pass |
| JSHint | ✅ Pass |
| `pytest` suite (143 tests) | ✅ Pass |

---

### Bug Log & Resolutions

**`import random` inside function causing UnboundLocalError**
Python treats any variable assigned anywhere in a function as local throughout the entire function. Moving `import random` to the top of `game_routes.py` resolved a runtime error where `random` was considered local due to a later assignment, and was therefore `None` when called.

**Story mapping cached at startup, ignoring new chapters**
The original `story_engine.py` loaded `choices_mapping.json` once at server startup and cached it in memory. New chapter entries had no effect without a full server restart — and even then only if the cache was cleared. Fixed by having `choose_path()` load the mapping fresh from disk on every call.

**HTMX `htmx:beforeRedirect` not firing in v1.9.12**
Tried to intercept the `HX-Redirect` response header using `htmx:beforeRedirect` with `e.preventDefault()` for the Victory Overlay — this event does not fire in HTMX 1.9.x. Switched to `htmx:beforeOnLoad` which fires before HTMX processes the response, allowing the overlay to display before navigation proceeds.

**Carousel mobile overflow**
`pages.css` loads after `components.css` and can override carousel width rules. The mobile `.class-option { max-width: 260px }` in `pages.css` must match the `carousel-item` fixed width in `components.css`. Mismatch caused card overflow on mobile — resolved by aligning both values.

**Enemy lore not rendering in some sessions**
Enemy lore was stored in the session via object reference rather than as individual string fields. If the object was not correctly reconstructed from session on the next request, lore came back as `None`. Fixed by storing each field explicitly in session and reading `session.get("enemy_lore", "")` in the template.

**`session["rest_bg"]` not persisting across rest entry**
Rest background was being randomly selected but not committed to session before the redirect. Ensured `session.modified = True` is set after writing the new value.

**Shield damage reduction outliving its duration**
A class's shield percentage (e.g. Barbarian's Feel No Pain) was reset to 0 only via the turn-decrement path for `shield_turns`, but the function that actually applies the shield to incoming damage only checked `shield_pct > 0`, never `shield_turns`. Once a shield was cast, the percentage silently never cleared again unless that same special was recast — blocking nearly all damage for the rest of the fight, far past the intended duration. Fixed by explicitly zeroing `shield_pct` the instant `shield_turns` reaches 0, mirroring how the buff system already clears its own secondary amount at the same point.

**Dead or abandoned runs resumable via the Bestiary's "Continue Story" link**
Two related exploits, fixed the same way: `session["character"]`/`session["chapter"]` are left untouched both when a player dies and when they return to the title screen without saving — neither action actually clears the session. The Bestiary's `mid_run` check only looked for `session["character"]` existing, so "Continue Story" would silently resume a run that should have been over. Fixed with two explicit flags — `session["game_over"]` (set the instant HP hits 0) and `session["at_title"]` (set whenever the title screen renders, cleared the moment `/game` is genuinely reached again, e.g. via Save/Load) — both checked by the Bestiary route and, for the death case, defensively re-checked at the top of `/game` itself so the exploit can't be reached through any other path either (browser back button, a bookmarked URL).

**Carousel left arrow never reappearing after a touch swipe on some iOS Safari versions**
Arrow/dot visibility only updated via a debounced `scroll` listener when `'onscrollend' in window` was false. That feature check is a false positive on some Safari/iOS versions — the `scrollend` event property exists, but the event itself doesn't reliably fire for touch-driven momentum scrolling, only for programmatic or mouse-driven scrolls. Arrow-click scrolling is programmatic, so that path always worked, masking the bug — but real finger-swiping silently never re-evaluated arrow state, freezing it at whatever it was computed at page load. Fixed by always attaching the debounced `scroll` listener as the reliable baseline, treating `scrollend` as a purely additive speed-up where it happens to work rather than the sole update path.

**Whole page horizontally pannable on mobile**
`<h1>` had a fixed `5rem` font-size with no responsive scaling anywhere — "Elden Souls" at that size rendered far wider than any phone viewport, and with no `overflow-x: hidden` safety net on `html`/`body`, that excess width made the entire page horizontally draggable rather than just the intended carousel. Fixed with a fluid `clamp(2.2rem, 11vw, 5rem)` so the title scales down on narrow screens (reaching the original size again above ~728px), plus the `overflow-x: hidden` safety net as defense-in-depth against any future element doing the same thing.

---

### Automated Testing

A `pytest` suite of **143 tests** runs against the actual story data and save logic — not planned, fully implemented and passing.

```bash
pytest tests/ -q
```

> **Note:** `pytest.ini` sets `pythonpath = .` at the project root. Without it, running a bare `pytest` (rather than `python -m pytest`) fails with a `ModuleNotFoundError` on some setups, since the working directory isn't automatically added to `sys.path`.

**`test_story_integrity.py`** (138 tests):
- `test_chapter_structure` — parametrized once per chapter ID across all 137 chapter files, verifying every chapter has the required fields and correctly-typed `battle`/`boss`/`rest` flags
- `test_choice_mapping_connectivity` — every entry in `choices_mapping.json` resolves to a chapter ID that actually exists on disk

**`test_save_migration.py`** (5 tests):
- Builds a save dict shaped like an old session-version save (missing newer keys such as `ng_plus`, `shadow_realm_completed`, etc.) and verifies `load_game()` correctly backfills every missing key to its current default via `SESSION_DEFAULTS`, so older saves never crash on load after a version bump

**`test_story_structure.py`**:
- Currently holds a `walk()` path-reachability helper used for ad-hoc verification of branch connectivity; not yet wired into standalone `test_*` functions

---

## 🔮 Known Issues & Future Enhancements

**Mobile Carousel Touch Range (open issue)**
On some real mobile devices, the class-select and gift carousels can be swiped toward one end freely but won't reach all the way back to the first card/option — `scrollLeft` appears to never return fully to 0 via touch, even though clicking the left arrow button (which is JS-driven rather than a native gesture) works correctly. Confirmed not caused by the carousel's edge-fade mask (symmetric, doesn't explain a one-sided limit) or by `carousel.js` itself (it doesn't intercept native touch-scroll at all). Root cause not yet found — currently paused pending a rethink of how the mobile carousel should behave, rather than continuing to patch the existing touch-scroll approach.

**Audio**
- Secondary specials currently reuse primary special SFX — unique audio per secondary is planned
- The Barbarian's primary special plays the Necromancer's `raise_the_dead.mp3` rather than its own `war_cry.mp3`, which exists but is unused
- Samurai, Wretch, and Barbarian have no dedicated secondary-special sound yet (Hunter already has one)
- Additional rest and area-specific background music tracks

**Additional Rest Backgrounds**
- Currently only `firelink.jpg` and four bonfire variants in `REST_BGS` — more atmospheric variants planned

**Future Features**
- Levelling system with XP gain from combat
- Expanded bestiary with lore entries for all enemies
- Character screen with equipment/upgrade history
- New story branches and additional ending variants
- Additional enemy visual animations during combat
- `player_record.json` (unlocked classes, lifetime run count) is a single shared file with no per-user key — on a live multi-visitor deployment, unlocks and the lifetime-runs banner are shared across every visitor rather than tracked individually. A real fix needs an external database (Heroku's filesystem is ephemeral, so SQLite wouldn't survive any better than the current JSON file) — deliberately deferred for now

---

## 🙏 Credits

**Built by:** [Tom Goss](https://github.com/TGOSS1984)

**Inspiration**

- The atmosphere, lore style, enemy design, world-building tone, and gothic visual aesthetic of this project are deeply inspired by the work of **FromSoftware** — particularly *Dark Souls*, *Dark Souls III*, *Demon's Souls*, and *Elden Ring*. These games are the creative bedrock of *Elden Souls*.
- The structural inspiration — branching narrative with binary choices, a character with distinct stats and special items, and turn-based combat where each decision matters — comes from **Ian Livingstone** and **Steve Jackson's** *Fighting Fantasy* gamebook series, particularly titles like *Deathtrap Dungeon* and *Forest of Doom*. Those paperbacks shaped my love of interactive storytelling long before I knew what programming was.

**Libraries & Tools**

- **Flask** — lightweight Python web framework
- **HTMX 1.9.12** — partial page updates for the battle screen
- **Font Awesome** — UI icons
- **Google Fonts (Cinzel)** — gothic serif typeface for headings
- **Mantinia** (font.download) — display font for the game title
- **NumPy** — random selection and probability-based mechanics
- **gunicorn** — WSGI production server
- **pycodestyle / black** — PEP8 checking and auto-formatting

**Assets**

- Background images and enemy/boss portraits sourced from Google Images and Pixabay
- Sound effects: Pixabay
- Background video: community Dark Souls bonfire footage

**Development Notes**

This project pushed my understanding of Flask session management considerably — particularly around the quirks of session-scoped state in a request/response model, the importance of `session.modified`, and the gotchas around Python variable scoping in nested functions. The HTMX integration required digging into version-specific event documentation to resolve the `htmx:beforeRedirect` issue. Building a data-driven story engine where new content can be authored in JSON and hot-reloaded without server restarts was one of the more satisfying architectural decisions in the project.

Seeing the whole thing come together — the looping video, the typewriter text, the flurry attack screen pulse, a six-class combat system with active effects, and over 130 chapters of branching story — is genuinely rewarding, and has significantly sharpened my approach to modular, maintainable Python.

---

*"The Cycle stirs again. You have been chosen to tread its cursed rhythm once more."*