# enemies.py

# Regular enemies
ENEMIES = [
    {
        "name": "Hollow Knight",
        "hp": 80,
        "attack": 18,
        "image": "hollow_knight.png",
        "lore": "Once noble, now a shell of oath and rust. Bound to duty, long after purpose has faded.",
    },
    {
        "name": "Ash Beast",
        "hp": 70,
        "attack": 15,
        "image": "ash_beast.png",
        "lore": "Forged in the crucibles beneath the mountain. Its bones smolder with endless rage.",
    },
    {
        "name": "Wraith",
        "hp": 60,
        "attack": 17,
        "image": "wraith.png",
        "lore": "A cursed soul slipping between realms. It strikes before shadows know it’s there.",
    },
    {
        "name": "Ghoul",
        "hp": 65,
        "attack": 16,
        "image": "ghoul.png",
        "lore": "Twisted by hunger and time. Claws etched from broken vows and burial iron.",
    },
    {
        "name": "Fallen Soldier",
        "hp": 75,
        "attack": 14,
        "image": "fallen_soldier.png",
        "lore": "He never left the battlefield. His sword still swings, though his war was lost centuries ago.",
    },
    {
        "name": "Mimic",
        "hp": 95,
        "attack": 20,
        "image": "mimic.png",
        "lore": "Once guardians of forgotten vaults, Mimics were cursed by greed — not their own, but that of those who sought what lay within. Now they hunger not for gold, but for the breath of the living. To gaze upon one and see only a chest is to invite ruin. Their patience is ancient. Their hunger, endless.",
    },
]

# Boss enemies — key is the boss name
BOSSES = {
    "Cindergloom": {
        "hp": 250,
        "attack": 30,
        "image": "cindergloom.png",
        "lore": "The final Flame Lord, bound in cinders and regret. Born of divine fire and destined to consume the end of all things."
    },
    "Lothric and Lorian": {
        "hp": 200,
        "attack": 22,
        "image": "lothric_lorian.png",
        "lore": "Twin princes of fading flame. One silent and seething, the other bound to a cursed destiny of rekindling."
    },
    "Ashen Knight": {
        "hp": 290,
        "attack": 24,
        "image": "ashen_knight.png",
        "lore": ""
    },
    "Pale Drake": {
        "hp": 250,
        "attack": 28,
        "image": "pale_drake.png",
        "lore": ""
    },
    "The Lord of Chains": {
        "hp": 220,
        "attack": 25,
        "image": "the_lord_of_chains.png",
        "lore": ""
    },
    "The Ember Tyrant": {
        "hp": 400,
        "attack": 22,
        "image": "the_ember_tyrant.png",
        "lore": ""
    },
    "The Mireborn Serpent": {
        "hp": 230,
        "attack": 25,
        "image": "the_mireborn_serpent.png",
        "lore": ""
    },
    "The Gravewarden": {
        "hp": 250,
        "attack": 24,
        "image": "the_gravewarden.png",
        "lore": ""
    },
    "The Abyss Watcher": {
        "hp": 270,
        "attack": 26,
        "image": "the_abyss_watcher.png",
        "lore": ""
    },
    "The Thorn Matriarch": {
        "hp": 240,
        "attack": 25,
        "image": "the_thorn_matriarch.png",
        "lore": ""
    },
    "The Blacksteel Sentinel": {
        "hp": 300,
        "attack": 23,
        "image": "the_blacksteel_sentinel.png",
        "lore": ""
    }
}
