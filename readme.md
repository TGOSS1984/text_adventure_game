# Elden Souls — A Dark Fantasy Text Adventure Game

**Elden Souls** is a web-based text adventure game inspired by *Dark Souls* and *Elden Ring*. Built with Python and Flask, the game features branching narratives, tactical combat, and a rich, atmospheric world. Players choose from four distinct character classes and embark on a perilous journey through cursed lands.

---

## Table of Contents

- [Project Purpose](#project-purpose)
- [Features](#features)
- [File Structure](#file-structure)
- [How to Run Locally](#how-to-run-locally)
- [Story Flowchart](#story-flowchart)
- [Game Logic Overview](#game-logic-overview)
- [Testing & PEP8](#testing--pep8)
- [Deployment Options](#deployment-options)
  - [Deploy to Heroku](#deploy-to-heroku)
- [Libraries Used & Rationale](#libraries-used--rationale)
- [Known Issues & Future Enhancements](#known-issues--future-enhancements)
- [Credits](#credits)
- [License](#license)

---

## Project Purpose

The goal of *Elden Souls* is to provide a lore-rich, interactive text-based adventure that combines storytelling with strategic combat. It showcases Python programming fundamentals, including OOP, data handling, user interaction, and web deployment using Flask. The game is designed to engage users in decision-making, exploration, and tactical battles, simulating the grim fantasy tone of *Elden Ring* and *Dark Souls*.

---

## Features

- 4 unique classes: Knight, Mage, Rogue, Archer — each with lore, stats, and a special item
- Dynamic, branching storylines with hidden paths and multiple endings
- Turn-based battle mechanics with attack, dodge, block, and Estus Flask healing
- Boss fights and lore-driven enemy encounters
- Bonfire system to rest and restore health/Estus
- Save/Load functionality with session storage and JSON backup
- Responsive Flask web interface with gothic-themed styling

---

## File Structure

```
elden_souls/
├── app/
│   ├── __init__.py
│   ├── routes.py
│   ├── models.py
│   ├── combat.py
│   ├── story.py
│   ├── save_load.py
│   ├── templates/
│   │   ├── index.html
│   │   ├── game.html
│   │   ├── battle.html
│   │   └── death.html
│   ├── static/
│   │   ├── css/
│   │   │   └── style.css
│   │   ├── js/
│   │   └── images
├── requirements.txt
├── run.py
├── README.md
├── .gitignore
└── storyboard.md
```

---

## How to Run Locally

1. **Clone the repository**

```bash
git clone https://github.com/TGOSS1984/text_adventure_game.git
cd text_adventure_game
```

2. **Set up virtual environment**

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**

```bash
pip install -r requirements.txt
```

4. **Run the application**

```bash
python run.py
```

5. Visit [http://127.0.0.1:5000](http://127.0.0.1:5000) in your browser.

---

## Story Flowchart

```text
Select Class
   |
Chapter 0: Intro
   |
   +--> Choice A --> Chapter 1: Ashen Forest --> Battle --> Next Chapter
   |
   +--> Choice B --> Chapter 2: Weeping Vale --> Rest Point
   |
   +--> Hidden Path --> Chapter X --> Special Encounter
        |
        --> Boss Battle --> Ending
```

---
## Game Logic Overview

### Estus Flask System

- Players begin with a limited number of Estus Flasks (default: 3).
- Flasks restore a portion of HP during battle and are stored in the Flask session.
- The `use_estus()` function in `combat.py` checks how many flasks are available and heals the player, updating both HP and the session value.
- Estus count is reset at bonfires and certain story branches like the "rest point".

### Battle System Mechanics

- Enemy encounters are triggered by specific story chapters using a `battle` flag in `story.py`.
- Each enemy has distinct stats (HP, attack) and lore.
- Players use one of several actions: `attack`, `block`, or `dodge`.
- Using Block reduces damage by 50%, using didge has a chance to avoid 100% damage but is random, the prompt for enemy is preparing massive attack was added to encourage use of these mechanics as opposed to just hitting attack.
- Damage calculations are influenced by the player’s class stats (attack/defense) and randomized outcomes via `numpy.random`.
- Dodge and block success/failure use probability thresholds.
- Bosses have higher stats and use adjusted damage scaling.

### Routing & Story Mapping

- Routes are managed in `routes.py` using Flask's routing system.
- Choices made by the player (`POST` requests) determine the next chapter via `choose_path()`.
- Story progression is stored in session, and chapters are fetched dynamically.
- Each chapter includes narrative text, optional choices, flags for battle/rest/bonfire, and hidden conditions.
- HTML templates render logic dynamically from Flask using Jinja2 templating.

---

## Testing & PEP8

### Manual Testing

During development I struggled with Flask session handling — especially when writing unit tests that required active contexts. It took several iterations before I found a clean solution. Many google searches and reddit forums supported with troubleshooting. Some guidance was taken from online resources and AI-assisted tools for structuring markdown and troubleshooting Flask errors, but all content and logic were written and tested by myself.

- Verified form inputs for class selection — ensured radio buttons require a choice
- Validated session-based story progression and choice-based routing
- Tested story branches including edge cases like hidden path detection
- Battles tested for all mechanics (attack, dodge, block, Estus), HP tracking, and boss damage scaling
- Confirmed rest points and bonfire mechanics restore health and Estus Flasks
- Simulated saving/loading: ensured session persists and JSON restores game state
- Enemy image and lore rendering: confirmed fallback behavior works if image missing
- Troubleshot image rendering on mobile devices — updated `background-size: cover;` and height logic
- Resolved bug where lore did not appear despite enemy being generated (fixed session persistence and template binding)
- Investigated print/debug not appearing in console (clarified Flask prints show in terminal where server was started)
- Fixed test failure using `session.get()` outside Flask context by mocking session in unit tests

### PEP8 Compliance

Code was linted using `pycodestyle`:

```bash
pip install pycodestyle
pycodestyle app/ --max-line-length=100
```

All modules are PEP8-compliant with no significant issues.

---

## Deployment Options

### Replit

- Upload project files to Replit
- Add Flask to `packages`
- Set `run.py` as main file

### Render

- Push code to GitHub
- Connect GitHub repo to [Render.com](https://render.com)
- Set build command: `pip install -r requirements.txt`
- Set start command: `gunicorn run:app`

### Deploy to Heroku

1. **Create **`` in the root directory:

```
web: gunicorn run:app
```

2. **Add **``** to requirements.txt**:

```bash
pip install gunicorn
pip freeze > requirements.txt
```

3. **Commit and push to GitHub**

4. **On Heroku dashboard**:

   - Create a new app
   - Connect your GitHub repo under **Deploy > Deployment method**
   - Enable automatic deploys if desired
   - Click **Deploy Branch**

5. **Open App** once deployed (e.g., `https://elden-souls.herokuapp.com`)

---

## Libraries Used & Rationale

- **Flask**: Chosen for its simplicity and flexibility in building lightweight web apps
- **NumPy**: Used for random selection and probability-based mechanics in battles
- **FontAwesome**: Adds thematic icons for UI immersion
- **Google Fonts**: Cinzel font reflects the gothic atmosphere of the game
- **font.download**: Mantinia for game title

---

## Known Issues & Future Enhancements

- Add audio feedback during combat (JS-sound integration)
- Mobile UI improvements for full-screen image scaling
- Implement character leveling and item inventory system
- Visual battle animations or transition effects

**Further Notes**

This project has been an exciting challenge and learning opportunity. I approached it with a love for dark fantasy games like Elden Ring and aimed to mirror that tone through mechanics, design, and lore.

The Estus Flask healing system, battle logic using probabilistic chance (e.g., dodge/block), and branching narratives helped push my understanding of OOP, Flask session handling, and modular structure. Early in development, I faced bugs around enemy generation and session persistence, particularly where lore fields were None. I debugged this by confirming object structure and manually storing each field in session.

A particularly tough moment was writing unit tests for Flask routes and session-based features. I encountered the well-known RuntimeError: Working outside of request context, which I resolved by decoupling logic for isolated testing. These real-world bugs helped deepen my understanding of Flask internals.

Every chapter choice, battle flag, or session update was an opportunity to apply core Python logic. Seeing it all tie together in a working game — with visuals, story flow, and user interaction — was rewarding and has sharpened my skills significantly.

While some sections (like the README formatting and diagrams) were polished with structured tools and best practices, all narrative, logic, battle handling, and user flow was built manually, tested, and refined iteratively.

---

## Credits

- Built by: [Tom Goss](https://github.com/TGOSS1984)
- Icons: FontAwesome
- Fonts: Google Fonts (Cinzel)
- Fonts: Mantinia Font from font.download
- Lore, design, and mechanics inspired by *FromSoftware* games
- Images from Google images

---
