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
- Random enemy encounters, can change per playthrough
- Boss fights and lore-driven enemy encounters
- Boss & Enemy battle backgrounds randomly generated
- Bonfire system to rest and restore health/Estus - includes background change upon finding a bonfire, and a flame/pulse effect
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

**Overview**

```mermaid
graph LR

    START["🔯 Start: Ashen Ruins"]
    START --> B1["💀 Ashen Knight"]
    B1 --> B2["💀 Mireborn Serpent"]
    B1 --> B3["💀 Grave Warden"]
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
    B8 --> FINAL["💀 Cindergloom, Lord of Ashes"]

    FINAL --> END1["🌅 Dawn of Flame"]
    FINAL --> END2["🌑 Age of Shadows"]
    FINAL --> END3["♻️ The Cycle Continues"]
```

**Detailed**

```mermaid
graph TD

%% --- START ---
START["🔯 Awaken in Ashen Ruins"]
START -->|"Step into the smoldering remains"| R1C1["R1: Ashen Ruins I"]
R1C1 -->|"Search the scorched bones (⚔️)"| R1C2["R1: Ashen Ruins II"]
R1C2 -->|"Wander deeper into the ash"| R1C3["R1: Ashen Ruins III"]
R1C3 -->|"Follow the stench of rot"| R1A["Go to Weeping Marsh"]
R1C3 -->|"Descend into the tomb-mouth"| R1B["Go to Hollow Catacombs"]
R1C3 -->|"Climb the forgotten ledge"| R1C["Go to Obsidian Peaks"]
R1C3 -->|"Kneel before the flame"| BON1["🔥 Bonfire - R1"]
BON1 -->|"Confront the Ashen Knight"| B1["💀 Boss 1: Ashen Knight"]
B1 -->|"Wade into the Weeping Marsh"| R2C1["R2: Weeping Marsh I"]
B1 -->|"Slip into the Hollow Catacombs"| R3C1["R3: Hollow Catacombs I"]
B1 -->|"Scale the Obsidian Peaks"| R4C1["R4: Obsidian Peaks I"]

%% --- REGION 2: Weeping Marsh ---
R1A -->|"Slog through the black mire"| R2C1
R2C1 -->|"Step beneath the hanging moss"| R2C2["R2: Weeping Marsh II (⚔️)"]
R2C2 -->|"Cross the sinking path"| R2C3["R2: Weeping Marsh III"]
R2C3 -->|"Rest among drowned bones"| BON2["🔥 Bonfire - R2"]
BON2 -->|"Challenge the Mireborn Serpent"| B2["💀 Boss 2: Mireborn Serpent"]
B2 -->|"Push on through the mist"| R3Entry["⛓ Path of Thorns"]
B2 -->|"Circle back to Hollow Catacombs"| R3C1

%% --- REGION 3: Hollow Catacombs ---
R1B -->|"Enter the yawning crypt"| R3C1
R3C1 -->|"Descend the winding ossuary"| R3C2["R3: Hollow Catacombs II"]
R3C2 -->|"Traverse the broken graves (⚔️)"| R3C3["R3: Hollow Catacombs III (⚔️)"]
R3C3 -->|"Pass beneath the chained dead"| R3C4["R3: Hollow Catacombs IV"]
R3C4 -->|"Kindle the old tombfire"| BON3["🔥 Bonfire - R3"]
BON3 -->|"Face the Grave Warden"| B3["💀 Boss 3: Grave Warden"]
B3 -->|"Climb toward flickering light"| R3Entry
B3 -->|"Return to Obsidian Peaks"| R4C1

%% --- REGION 4: Obsidian Peaks ---
R1C -->|"Tread the ashen slope"| R4C1
R4C1 -->|"Cross the blackened ridge"| R4C2["R4: Obsidian Peaks II"]
R4C2 -->|"Climb the scorched spire (⚔️)"| R4C3["R4: Obsidian Peaks III"]
R4C3 -->|"Rest beside the magma fissure"| BON4["🔥 Bonfire - R4"]
BON4 -->|"Duel the Ember Tyrant"| B4["💀 Boss 4: Ember Tyrant"]
B4 -->|"Drop into a lower passage"| R3Entry
B4 -->|"Pass through the arch of ash"| Hub1

%% --- HUB ENTRY ---
R3Entry -->|"Approach the Chapel of Thorns"| Hub1["⛩️ Central Hub: Chapel of Thorns"]
Hub1 -->|"Ascend the northern stair"| R5C1
Hub1 -->|"Venture down the eastern gorge"| R6C1
Hub1 -->|"Slip south through bramble"| R7C1
Hub1 -->|"Descend to Drowned Village"| R11C1

%% --- REGION 5: Shattered Keep ---
R5C1["R5: Shattered Keep I"]
R5C1 -->|"Enter the echoing hall (⚔️)"| R5C2["R5: Keep II (⚔️)"]
R5C2 -->|"Cross the splintered drawbridge"| R5C3["R5: Keep III"]
R5C3 -->|"Light the brazier of ruin"| BON5["🔥 Bonfire - R5"]
BON5 -->|"Unshackle the Lord of Chains"| B5["💀 Boss 5: Lord of Chains"]
B5 -->|"Walk the forgotten archway"| Cross1

%% --- REGION 6: Forgotten Valley ---
R6C1["R6: Forgotten Valley I"]
R6C1 -->|"Step through the whispering fog"| R6C2["R6: Valley II"]
R6C2 -->|"Traverse the gnarled roots (⚔️)"| R6C3["R6: Valley III (⚔️)"]
R6C3 -->|"Collapse near the old cairn"| BON6["🔥 Bonfire - R6"]
BON6 -->|"Rouse the Pale Drake"| B6["💀 Boss 6: Pale Drake"]
B6 -->|"Circle beneath the cliffs"| Cross1
B6 -->|"Sneak into Iron Bastion"| R7C1

%% --- REGION 7: Iron Bastion ---
R7C1["R7: Iron Bastion I"]
R7C1 -->|"March through rusted gates (⚔️)"| R7C2["R7: Bastion II (⚔️)"]
R7C2 -->|"Cross the molten forge"| R7C3["R7: Bastion III"]
R7C3 -->|"Find solace in the furnace alcove"| BON7["🔥 Bonfire - R7"]
BON7 -->|"Confront the Blacksteel Sentinel"| B7["💀 Boss 7: Blacksteel Sentinel"]
B7 -->|"Bridge the molten divide"| Cross1

%% --- REGION 8: Cradle of Thorns ---
Cross1 -->|"Tear through the thornveil"| R8C1["R8: Cradle of Thorns I"]
R8C1 -->|"Step into the vine maze (⚔️)"| R8C2["R8: Thorns II"]
R8C2 -->|"Collapse beneath a root pyre"| BON8["🔥 Bonfire - R8"]
BON8 -->|"Face the Thorn Matriarch"| B8["💀 Boss 8: Thorn Matriarch"]
B8 -->|"Climb toward the Second Crossroads"| Hub2

%% --- REGION 9: Abyssal Sanctum ---
Hub2 -->|"Descend into the abyss"| R9C1["R9: Abyssal Sanctum I"]
R9C1 -->|"Step beyond the veil (⚔️)"| R9C2["R9: Sanctum II (⚔️)"]
R9C2 -->|"Kneel beneath the obsidian sky"| BON9["🔥 Bonfire - R9"]
BON9 -->|"Challenge the Abyss Watcher"| B9["💀 Boss 9: Abyss Watcher"]
B9 -->|"Approach the silent citadel"| R10C1

%% --- REGION 10: Forgotten Citadel ---
Hub2 -->|"Ascend to the forgotten tower"| R10C1["R10: Forgotten Citadel I"]
R10C1 -->|"Step through shattered court (⚔️)"| R10C2["R10: Citadel II (⚔️)"]
R10C2 -->|"Cross the frostbound gallery"| R10C3["R10: Citadel III"]
R10C3 -->|"Offer ashes to the flame"| BON10["🔥 Bonfire - R10"]
BON10 -->|"Face Cindergloom, Lord of Ashes"| FINAL["💀 Final Boss: Cindergloom, Lord of Ashes"]

%% --- POST-GAME ---
FINAL -->|"Embrace the Flame"| END1["🌅 Ending: Dawn of Flame"]
FINAL -->|"Snuff the Light"| END2["🌑 Ending: Age of Shadows"]
FINAL -->|"Let the Cycle Turn"| END3["♻️ Ending: The Cycle Continues"]

%% --- OPTIONAL REGIONS ---
START -->|"Dive into the drowned road"| R11C1["R11: Drowned Village"]
R11C1 -->|"Confront the sunken dead (⚔️)"| R11C2["R11: Village II (⚔️)"]
R11C2 -->|"Light the waterlogged shrine"| BON11["🔥 Bonfire - R11"]
BON11 -->|"Rejoin the path of ash"| B1

Hub1 -->|"Fade into the spectral woods"| R12C1["R12: Spectral Woods"]
R12C1 -->|"Follow whispers in the trees"| R12C2["R12: Woods II"]
R12C2 -->|"Ignite the ghostfire"| BON12["🔥 Bonfire - R12"]
BON12 -->|"Slip beneath the moss veil"| R6C3

Hub2 -->|"Scale the Tower of Whispers"| R13C1["R13: Tower of Whispers"]
R13C1 -->|"Echo through hollow heights (⚔️)"| R13C2["R13: Tower II (⚔️)"]
R13C2 -->|"Rest beneath the singing spire"| BON13["🔥 Bonfire - R13"]
BON13 -->|"Enter citadel's fractured gate"| R10C2

R4C3 -->|"Plunge into molten depths"| R14C1["R14: Molten Depths"]
R14C1 -->|"Cross the lava tomb"| R14C2["R14: Depths II"]
R14C2 -->|"Collapse near ember altar"| BON14["🔥 Bonfire - R14"]
BON14 -->|"Return to the Ember Tyrant"| B4

R3C2 -->|"Wander the echoing hall"| R15C1["R15: Halls of Echo"]
R15C1 -->|"Descend into screaming dark (⚔️)"| R15C2["R15: Halls II (⚔️)"]
R15C2 -->|"Rest in the void chamber"| BON15["🔥 Bonfire - R15"]
BON15 -->|"Return to the shattered hall"| R5C2
```

---
## Game Logic Overview

### Estus Flask System

- Players begin with a limited number of Estus Flasks (default: 3).
- Flasks restore a portion of HP during battle and are stored in the Flask session.
- The `use_estus()` function in `combat.py` checks how many flasks are available and heals the player, updating both HP and the session value.
- Estus count is reset at bonfires and certain story branches like the "rest point".

### Player

- Each class has different perks
- Knight, high defence, high HP, high block absorb, low dodge chance, low attack, low critical hit chance
- Mage, low defence, low hp, medium block absorb, medium dodge chance, high attack, medium critical hit chance
- Rogue, low defence , low hp, medium block absorb, high dodge chance, high attack, medium critical hit chance
- Archer, medium defence, medium hp, high block absorb, medium dodge chance, medium attack, high critical chance

### Battle System Mechanics

- Enemy encounters are triggered by specific story chapters using a `battle` flag in `story.py`.
- Each enemy has distinct stats (HP, attack) and lore.
- Players use one of several actions: `attack`, `block`, `dodge`, or `use estus`.
- Using Block reduces damage by a % depending on class, using dodge has a chance to avoid 100% damage but is based on % chance of sucess for each class, the prompt for enemy upcoming attack was added to encourage use of these mechanics as opposed to just hitting attack.
- Enemy has 3 types of attack, standard attack, massive attack & flurry attack - this is probability based with the flurry attack being most rare & the standard attack being most common
- Animations are added for the flurry attack where the screen pulses Red and for using an Estus flask the sceen turns a green shade with bubbles rising to simulate health regeneration
- Damage calculations are influenced by the player’s class stats (attack/defense) and randomized outcomes via `numpy.random`.
- Dodge and block success/failure use probability thresholds.
- Bosses have higher stats and use adjusted damage scaling.

### Routing & Story Mapping

- Routes are managed in `routes.py` using Flask's routing system.
- Choices made by the player (`POST` requests) determine the next chapter via `choose_path()`.
- Story progression is stored in session, and chapters are fetched dynamically.
- Each chapter includes narrative text, optional choices, flags for battle/rest/bonfire, and hidden conditions.
- HTML templates render logic dynamically from Flask using Jinja2 templating.
- Story chapters are held in seperate.jsons with flags for battle/boss/bonsfire in each
- Story mapping is also kept in a .json file to connect each chapter
- Sotry is loaded using story_engine & Story_loader and they are called in routes.py

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

I found it helpful to use tools such as black to support with formatting of code but also running the code through the pep8 checker also supported my understanding of best practice with Python.

---

## Credits

- Built by: [Tom Goss](https://github.com/TGOSS1984)
- Icons: FontAwesome
- Fonts: Google Fonts (Cinzel)
- Fonts: Mantinia Font from font.download
- Lore, design, and mechanics inspired by *FromSoftware* games
- Images from Google images
- Pixabay for sound effects

---
