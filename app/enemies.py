# enemies.py
#
# Commit 10 additions:
# - soul_reward added to every regular enemy (scaled by HP + attack difficulty)
# - soul_reward added to every boss (base reward × 3 boss multiplier)
# Formula guidance:
#   Regular: floor((hp * 0.5) + (attack * 3))  → range ~75–115
#   Boss:    floor((hp * 0.8) + (attack * 5))  → range ~250–500

# Regular enemies
ENEMIES = [
    {
        "name": "Hollow Knight",
        "hp": 80,
        "attack": 18,
        "image": "hollow_knight.png",
        "lore": "Once noble, now a shell of oath and rust. Bound to duty, long after purpose has faded.",
        "soul_reward": 94,   # (80*0.5) + (18*3) = 40+54
    },
    {
        "name": "Ash Beast",
        "hp": 70,
        "attack": 15,
        "image": "ash_beast.png",
        "lore": "Forged in the crucibles beneath the mountain. Its bones smolder with endless rage.",
        "soul_reward": 80,   # (70*0.5) + (15*3) = 35+45
    },
    {
        "name": "Wraith",
        "hp": 60,
        "attack": 17,
        "image": "wraith.png",
        "lore": "A cursed soul slipping between realms. It strikes before shadows know it's there.",
        "soul_reward": 81,   # (60*0.5) + (17*3) = 30+51
    },
    {
        "name": "Ghoul",
        "hp": 65,
        "attack": 16,
        "image": "ghoul.png",
        "lore": "Twisted by hunger and time. Claws etched from broken vows and burial iron.",
        "soul_reward": 80,   # (65*0.5) + (16*3) = 32.5+48
    },
    {
        "name": "Fallen Soldier",
        "hp": 75,
        "attack": 14,
        "image": "fallen_soldier.png",
        "lore": "He never left the battlefield. His sword still swings, though his war was lost centuries ago.",
        "soul_reward": 79,   # (75*0.5) + (14*3) = 37.5+42
    },
    {
        "name": "Mimic",
        "hp": 95,
        "attack": 20,
        "image": "mimic.png",
        "lore": "Once guardians of forgotten vaults, Mimics were cursed by greed — not their own, but that of those who sought what lay within. Now they hunger not for gold, but for the breath of the living. To gaze upon one and see only a chest is to invite ruin. Their patience is ancient. Their hunger, endless.",
        "soul_reward": 107,  # (95*0.5) + (20*3) = 47.5+60
    },
    {
        "name": "Spectral Beast",
        "hp": 110,
        "attack": 18,
        "image": "spectral_beast.png",
        "lore": "A ghostly, antlered deer borne from the cursed king of the drowned city of Thal'Rhuin, its ethereal form prowls the depths, dragging souls into the abyss with its eerie, otherworldly presence.",
        "soul_reward": 109,  # (110*0.5) + (18*3) = 55+54
    },
    {
        "name": "The Hollow Weaver",
        "hp": 110,
        "attack": 18,
        "image": "hollow_weaver.png",
        "lore": "She once whispered to the stars, but now her voice is lost, drowned in the silent screams of forgotten realms, weaving forbidden spells from the threads of the void, forever searching for a way to reclaim her soul.",
        "soul_reward": 109,  # same stats as Spectral Beast
    },
    {
        "name": "Thornveil Knight",
        "hp": 140,
        "attack": 17,
        "image": "thornveil_knight.png",
        "lore": "Clad in armor wrought from living briar, the Thornveil Knight serves as both warden and herald of the Thorn Matriarch. Each plate is etched with the sigils of the chapel's lost saints, now half-buried beneath creeping thorns that bloom crimson in the presence of blood",
        "soul_reward": 121,  # (140*0.5) + (17*3) = 70+51
    },
    {
        "name": "Echoing Knight",
        "hp": 135,
        "attack": 17,
        "image": "echoing_knight.png",
        "lore": "The Echoing Knight rides where no breath stirs, his helm absent and his neck a hollow column of shadow. In life, his voice was the clarion call that led armies to triumph; in death, it has become a curse, resounding still through the iron plates that encase him",
        "soul_reward": 118,  # (135*0.5) + (17*3) = 67.5+51
    },
    {
        "name": "The Mourning Veil",
        "hp": 115,
        "attack": 20,
        "image": "the_mourning_veil.png",
        "lore": "They drift as one through the places where the veil between worlds thins, two shades bound by a death they did not choose. The elder bears the Reaping Sickle, her strokes wide and patient, harvesting the souls that dare linger. The younger moves swift as shadow, her dagger slipping between ribs before her form dissolves into mist.",
        "soul_reward": 117,  # (115*0.5) + (20*3) = 57.5+60
    },
    {
        "name": "Carrion Hound",
        "hp": 65,
        "attack": 16,
        "image": "carrion_hound.png",
        "lore": "Once a loyal hound, now little more than sinew and spite, its hide hangs in tatters, crawling with blackened sores that weep foul ichor. The stench of rot precedes it, carried on ragged breaths that rasp like tearing cloth",
        "soul_reward": 80,   # (65*0.5) + (16*3) = 32.5+48
    },
    {
        "name": "Chitinous Widow",
        "hp": 95,
        "attack": 18,
        "image": "chitinous_widow.png",
        "lore": "Beneath the hollow catacombs, where light dare not trespass, she weaves a lattice of bone and sinew. Once a priestess of the Pale Faith, she was entombed for crimes unspoken, her body reshaped by venom and shadow.",
        "soul_reward": 101,  # (95*0.5) + (18*3) = 47.5+54
    },
]

# Boss enemies — key is the boss name
# soul_reward formula: floor((hp * 0.8) + (attack * 5))
BOSSES = {
    "Cindergloom": {
        "hp": 250,
        "attack": 30,
        "image": "cindergloom.png",
        "lore": "The final Flame Lord, bound in cinders and regret. Born of divine fire and destined to consume the end of all things. Within the lightless halls of the Forgotten Citadel, his throne rises from a lake of slow-burning ash, each ember a whisper of worlds already claimed. His flesh is a tapestry of charred fissures, glowing faintly with the molten pulse beneath. Horns wreathed in fire arc from his brow like the spires of a dying sun, and his talons drip molten gold that hisses against the blackened stones",
        "soul_reward": 350,  # (250*0.8) + (30*5) = 200+150
    },
    "Lothric and Lorian": {
        "hp": 200,
        "attack": 22,
        "image": "lothric_lorian.png",
        "lore": "Twin princes of fading flame. One silent and seething, the other bound to a cursed destiny of rekindling.",
        "soul_reward": 270,  # (200*0.8) + (22*5) = 160+110
    },
    "Ashen Knight": {
        "hp": 290,
        "attack": 24,
        "image": "ashen_knight.png",
        "lore": "The Ashen Knight looms, his form a grotesque amalgam of charred steel and twisted flesh, as though the armor has grown into him over centuries of penance",
        "soul_reward": 352,  # (290*0.8) + (24*5) = 232+120
    },
    "Pale Drake": {
        "hp": 250,
        "attack": 28,
        "image": "pale_drake.png",
        "lore": "In the wind-scoured depths of the Forgotten Valley, where frost clings even to the bones of the mountains, the Pale Drake slumbers beneath a sky that remembers no sun. His scales, the color of moonlit marble, shimmer with the faint light of dying stars.",
        "soul_reward": 340,  # (250*0.8) + (28*5) = 200+140
    },
    "The Lord of Chains": {
        "hp": 220,
        "attack": 25,
        "image": "the_lord_of_chains.png",
        "lore": "At the shattered heart of the Keep, upon a throne of rusted iron and broken manacles, sits the Lord of Chains. Once a conqueror whose name was a warcry, he traded crown and kin for the thrill of battle's red haze.",
        "soul_reward": 301,  # (220*0.8) + (25*5) = 176+125
    },
    "The Ember Tyrant": {
        "hp": 400,
        "attack": 22,
        "image": "the_ember_tyrant.png",
        "lore": "The Ember Tyrant towers above the blackened earth, his skin a tapestry of cracked obsidian and veins of molten fire. Chains, long since fused to his flesh, drag behind him like the echoes of a broken throne.",
        "soul_reward": 430,  # (400*0.8) + (22*5) = 320+110
    },
    "The Mireborn Serpent": {
        "hp": 230,
        "attack": 25,
        "image": "the_mireborn_serpent.png",
        "lore": "From the depths of the drowned fen rises the Mireborn Serpent, a colossal coil of rotting scales and slick, peat-soaked flesh. Once a lord of the marshlands, he offered his body to an ancient parasite in exchange for dominion eternal.",
        "soul_reward": 309,  # (230*0.8) + (25*5) = 184+125
    },
    "The Gravewarden": {
        "hp": 250,
        "attack": 24,
        "image": "the_gravewarden.png",
        "lore": "Beyond the final descent of the Hollow Catacombs, where the air hangs heavy with the dust of centuries, the Gravewarden stands vigil. Draped in funeral raiments stitched from the shrouds of kings, his form is gaunt yet towering, a silhouette crowned with jagged bone and tarnished gold",
        "soul_reward": 320,  # (250*0.8) + (24*5) = 200+120
    },
    "The Abyss Watcher": {
        "hp": 270,
        "attack": 26,
        "image": "the_abyss_watcher.png",
        "lore": "At the brink of the world where the Abyss swallows all light, the Abyss Watcher stands sentinel. Cloaked in tattered black, his form is both man and beast — a knight's frame twisted by the long years in darkness.",
        "soul_reward": 346,  # (270*0.8) + (26*5) = 216+130
    },
    "The Thorn Matriarch": {
        "hp": 240,
        "attack": 25,
        "image": "the_thorn_matriarch.png",
        "lore": "In the heart of the Chapel of Thorns, where rose and briar drink alike from bloodied soil, the Thorn Matriarch waits. Her armor blooms with living barbs, each petal forged from the steel of fallen pilgrims. Long strands of crimson hair drift like banners in the still, suffocating air. She moves with the elegance of a saint and the certainty of a blade, her every step sowing thorns that pierce flesh and spirit alike",
        "soul_reward": 317,  # (240*0.8) + (25*5) = 192+125
    },
    "The Blacksteel Sentinel": {
        "hp": 300,
        "attack": 23,
        "image": "the_blacksteel_sentinel.png",
        "lore": "Within the furnace-lit shadow of the Iron Bastion, the Blacksteel Sentinel waits astride the wreckage of a thousand sieges. His armor is hammered from the very walls he has defended, blackened by the soot of endless forges and scarred by the weapons of would-be conquerors.",
        "soul_reward": 355,  # (300*0.8) + (23*5) = 240+115
    },
}