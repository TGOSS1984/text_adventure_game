# Elden Souls — A Dark Fantasy Text Adventure Game

**Elden Souls** is a web-based text adventure game inspired by *Dark Souls* and *Elden Ring*. Built with Python and Flask, the game features branching narratives, tactical combat, and a rich, atmospheric world. Players choose from four distinct character classes and embark on a perilous journey through cursed lands.

[Github (repo) link to project](https://github.com/TGOSS1984/text_adventure_game)

[Heroku Link to project](https://elden-souls-text-adventure-app-6406dec306fc.herokuapp.com/)

**Image from my flask web app**

![Image from flask](app/static/images/screenshots/game_screen.PNG)

---

## Table of Contents

- [Project Purpose](#project-purpose)
- [Features](#features)
- [File Structure](#file-structure)
- [How to Run Locally](#how-to-run-locally)
- [Story Flowchart](#story-flowchart)
- [Game Logic Overview](#game-logic-overview)
- [Testing & PEP8](#testing--pep8)
- [Deployment](#deployment)
  - [Deploy to Heroku](#deploy-to-heroku)
- [Libraries Used & Rationale](#libraries-used--rationale)
- [Known Issues & Future Enhancements](#known-issues--future-enhancements)
- [Credits](#credits)

---

## Project Purpose

The goal of *Elden Souls* is to provide a lore-rich, interactive text-based adventure that combines storytelling with strategic combat. It showcases Python programming fundamentals, including OOP, data handling, user interaction, and web deployment using Flask. The game is designed to engage users in decision-making, exploration, and tactical battles, simulating the grim fantasy tone of *Elden Ring* and *Dark Souls*. I began brainstorming this idea with the intent of making a fully backend python text adventure which would be run entirely on the console but decided I wanted to integrate some visual flair as well which led me down the route of creating the flask based web application, this was very challenging but ultimately rewarding to learn some of the new concepts.

---

## Features

- 4 unique classes: Knight, Mage, Rogue, Archer — each with lore, stats, and a special item
- Dynamic, branching storylines with hidden paths and multiple endings
- Turn-based battle mechanics with attack, dodge, block, and Estus Flask healing
- Boss fights and lore-driven enemy encounters
- Bonfire system to rest and restore health/Estus
- Save/Load functionality with session storage and JSON backup
- Responsive Flask web interface with gothic-themed styling using html & CSS
- This project was primarily for use of python but as I decided to add some visual style to it using flask I wanted to also add more immersion by adding some themed music whihc be manually controlled by the user 

**Initial Wireframe Design/Concept for story screen**

![Image from flask](app/static/images/screenshots/wireframe_mockup.PNG)

## Screenshot Examples of game

**Story Screen**

![Image from flask](app/static/images/screenshots/story_screen.PNG)

**Battle Screen**

![Image from flask](app/static/images/screenshots/battle_screen.PNG)

**Death Screen**

![Image from flask](app/static/images/screenshots/death_screen.PNG)

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
├── Procfile
├── .python-version
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

**Notes**

During development I struggled with Flask session handling — especially when writing unit tests that required active contexts. It took several iterations before I found a clean solution. Many google searches and reddit forums supported with troubleshooting. Some guidance was taken from online resources and AI-assisted tools for structuring markdown and troubleshooting Flask errors, but all content and logic were written and tested by myself.

Learning about flask syntax within hmtl was interesting as I learnt about how to bridge python together with html.

It was interesting to use Heroku for the first time & to troubleshoot new issues which lead me to  learn more about the importance of the project files/requirements.

Initially, I had issues setting the project up in Heroku , when I first linked my project to github I received errors, after troubleshooting the errors were caused by not adding a python version file in my project files. After this fix I found another error – again after troubleshooting I discovered I required a Procfile to be created in my project along with some other requirements in the requirements.txt. After adding these things I  managed to successfully link & run my project in Heroku.

**General Tests**

- Throughout the project regular use of print statements were used to test functions
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

**Validators**

- HTML tested in html validator (passed, learnt that flask syntax will be flagged as error so ran without)
- CSS validator passed
- JS tested in JSHint without issue

### PEP8 Compliance

## Code Quality & Linting

Code throughout the project has been checked and cleaned to ensure it meets **PEP8 standards**.

### Tools Used

- **`pycodestyle`** was used to identify PEP8 violations:  
  Run `pip install pycodestyle` and  
  `pycodestyle app/ --max-line-length=100`

- **[pep8ci.herokuapp.com](https://pep8ci.herokuapp.com/#)** was used for manual checks.

- **`black`** was installed and used to auto-format the project:  
  Run `pip install black` and `black .`

`black` helped normalize indentation, line length, and overall structure according to modern Python formatting conventions.

### Issues Identified and Resolved

- `E501`: **Line too long**
- `E122`: **Continuation line missing indentation**
- `E302`: **Expected 2 blank lines before top-level function/class**
- `W291`: **Trailing whitespace**
- `W293`: **Blank line contains whitespace**

All modules were successfully cleaned and verified to be **PEP8-compliant**.

---

## Deployment

### Options

**Replit**

- Upload project files to Replit
- Add Flask to `packages`
- Set `run.py` as main file

**Render**

- Push code to GitHub
- Connect GitHub repo to [Render.com](https://render.com)
- Set build command: `pip install -r requirements.txt`
- Set start command: `gunicorn run:app`

### This Project

**VSCode**

- Code was written using VSCode
- Folder structure was a bit more complex than what I have been used to, run.py , Readme, requirements, gitignore all exist in the main folder. All other python files exist within the app folder alogn with templates folder whihc contains the html, the static which contains the CSS/JS & image & sound assests.

**GitHub**

- A GitHub account was created
- A new reposiory was created on GitHub by clicking the 'New' button. It was named and set as public.
- A folder was created in VSCode and initialised as a Git repository
- In VSCode the terminal was used to run commands to link the local project to the GitHub repository
- Throughout the process of builing the website, commits & pushes were staged regularly using terminal commands such as 'git add .' , 'git-commit -m' & 'git push'
- Host the project: Went to my GitHub repository, clicked settings > pages and selected the branch to publish, hit save and then GitHub generated a live link (link at top of readme)

**Deploy to Heroku**

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

5. **Open App** once deployed (`https://elden-souls-text-adventure-app-6406dec306fc.herokuapp.com/`)

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
- Add background audio for each differetn area to add to the mood and aid atmosphere
- Mobile UI improvements for full-screen image scaling
- Implement character leveling and item inventory system
- Add unique starting item for different classes
- Evolve the battle system with deeper logic and more variety
- Visual battle animations or transition effects
- Add new imagery for different areas to improve immersion

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
