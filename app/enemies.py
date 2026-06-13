# enemies.py
#
# Commit 10 additions:
# - soul_reward added to every regular enemy (scaled by HP + attack difficulty)
# - soul_reward added to every boss (base reward × 3 boss multiplier)
# Formula guidance:
#   Regular: floor((hp * 0.5) + (attack * 3))  → range ~75–115
#   Boss:    floor((hp * 0.8) + (attack * 5))  → range ~250–500
#
# Commit 21 additions:
# - attack       — physical attack (0 for magic enemies)
# - magic_attack — magic attack (0 for physical enemies)
# - defense      — physical defence (resists player physical damage)
# - magic_defense — magic defence (resists player magic/Mage damage)
# - damage_type  — 'physical', 'magic', or 'mixed'
# All existing soul_reward values preserved unchanged.
# Boss HP values adjusted for balance (see simulation notes in commit 21 spec):
#   Ashen Knight 290->240, Blacksteel Sentinel 300->250,
#   Ember Tyrant 400->320, Abyss Watcher 270->230
#
# Refactor: phase2_lore moved here from combat.py — lives alongside the boss
# it describes. combat.py reads boss["phase2_lore"] instead of its own dict.
#
# Commit 1 — Soul Economy Rebalance:
# All boss soul_reward values reduced by 40% from their previous values,
# rounded to the nearest 5.
#
# Reasoning: pre-rebalance a main-path player finished with ~112% surplus over
# total shop cost (way too many leftover souls). Target is ~25% surplus on the
# main path — enough to buy everything comfortably without trivialising the economy.
#
# Full-completion runs (both branches + shadow realm) will still have a larger
# surplus (~117%). This is intentional — optional content should feel rewarding.
# That surplus is controlled at NG+ entry via NG_PLUS_SOUL_CAP in config.py (600).
#
# Original -> new values documented inline on each boss entry.
# Regular enemy rewards are unchanged (they are small, ~80–121, and
# reducing them further would make early-game feel punishing).

# ── Regular enemies ───────────────────────────────────────────────────────────

ENEMIES = [
    {
        "name":          "Hollow Knight",
        "hp":            80,
        "attack":        18,
        "magic_attack":  0,
        "defense":       8,
        "magic_defense": 3,
        "damage_type":   "physical",
        "image":         "hollow_knight.png",
        "lore":          "Once noble, now a shell of oath and rust. Bound to duty, long after purpose has faded.",
        "soul_reward":   94,
    },
    {
        "name":          "Ash Beast",
        "hp":            70,
        "attack":        15,
        "magic_attack":  0,
        "defense":       6,
        "magic_defense": 2,
        "damage_type":   "physical",
        "image":         "ash_beast.png",
        "lore":          "Forged in the crucibles beneath the mountain. Its bones smolder with endless rage.",
        "soul_reward":   80,
    },
    {
        "name":          "Wraith",
        "hp":            60,
        "attack":        0,
        "magic_attack":  17,
        "defense":       2,
        "magic_defense": 12,
        "damage_type":   "magic",
        "image":         "wraith.png",
        "lore":          "A cursed soul slipping between realms. It strikes before shadows know it's there.",
        "soul_reward":   81,
    },
    {
        "name":          "Ghoul",
        "hp":            65,
        "attack":        16,
        "magic_attack":  0,
        "defense":       4,
        "magic_defense": 2,
        "damage_type":   "physical",
        "image":         "ghoul.png",
        "lore":          "Twisted by hunger and time. Claws etched from broken vows and burial iron.",
        "soul_reward":   80,
    },
    {
        "name":          "Fallen Soldier",
        "hp":            75,
        "attack":        14,
        "magic_attack":  0,
        "defense":       7,
        "magic_defense": 3,
        "damage_type":   "physical",
        "image":         "fallen_soldier.png",
        "lore":          "He never left the battlefield. His sword still swings, though his war was lost centuries ago.",
        "soul_reward":   79,
    },
    {
        "name":          "Mimic",
        "hp":            95,
        "attack":        20,
        "magic_attack":  0,
        "defense":       6,
        "magic_defense": 4,
        "damage_type":   "physical",
        "image":         "mimic.png",
        "lore":          "Once guardians of forgotten vaults, Mimics were cursed by greed — not their own, but that of those who sought what lay within. Now they hunger not for gold, but for the breath of the living. To gaze upon one and see only a chest is to invite ruin. Their patience is ancient. Their hunger, endless.",
        "soul_reward":   107,
    },
    {
        "name":          "Spectral Beast",
        "hp":            110,
        "attack":        0,
        "magic_attack":  18,
        "defense":       2,
        "magic_defense": 10,
        "damage_type":   "magic",
        "image":         "spectral_beast.png",
        "lore":          "A ghostly, antlered deer borne from the cursed king of the drowned city of Thal'Rhuin, its ethereal form prowls the depths, dragging souls into the abyss with its eerie, otherworldly presence.",
        "soul_reward":   109,
    },
    {
        "name":          "The Hollow Weaver",
        "hp":            110,
        "attack":        0,
        "magic_attack":  18,
        "defense":       2,
        "magic_defense": 14,
        "damage_type":   "magic",
        "image":         "hollow_weaver.png",
        "lore":          "She once whispered to the stars, but now her voice is lost, drowned in the silent screams of forgotten realms, weaving forbidden spells from the threads of the void, forever searching for a way to reclaim her soul.",
        "soul_reward":   109,
    },
    {
        "name":          "Thornveil Knight",
        "hp":            140,
        "attack":        17,
        "magic_attack":  0,
        "defense":       10,
        "magic_defense": 4,
        "damage_type":   "physical",
        "image":         "thornveil_knight.png",
        "lore":          "Clad in armor wrought from living briar, the Thornveil Knight serves as both warden and herald of the Thorn Matriarch. Each plate is etched with the sigils of the chapel's lost saints, now half-buried beneath creeping thorns that bloom crimson in the presence of blood",
        "soul_reward":   121,
    },
    {
        "name":          "Echoing Knight",
        "hp":            135,
        "attack":        17,
        "magic_attack":  0,
        "defense":       10,
        "magic_defense": 4,
        "damage_type":   "physical",
        "image":         "echoing_knight.png",
        "lore":          "The Echoing Knight rides where no breath stirs, his helm absent and his neck a hollow column of shadow. In life, his voice was the clarion call that led armies to triumph; in death, it has become a curse, resounding still through the iron plates that encase him",
        "soul_reward":   118,
    },
    {
        "name":          "The Mourning Veil",
        "hp":            115,
        "attack":        0,
        "magic_attack":  20,
        "defense":       3,
        "magic_defense": 11,
        "damage_type":   "magic",
        "image":         "the_mourning_veil.png",
        "lore":          "They drift as one through the places where the veil between worlds thins, two shades bound by a death they did not choose. The elder bears the Reaping Sickle, her strokes wide and patient, harvesting the souls that dare linger. The younger moves swift as shadow, her dagger slipping between ribs before her form dissolves into mist.",
        "soul_reward":   117,
    },
    {
        "name":          "Carrion Hound",
        "hp":            65,
        "attack":        16,
        "magic_attack":  0,
        "defense":       4,
        "magic_defense": 2,
        "damage_type":   "physical",
        "image":         "carrion_hound.png",
        "lore":          "Once a loyal hound, now little more than sinew and spite, its hide hangs in tatters, crawling with blackened sores that weep foul ichor. The stench of rot precedes it, carried on ragged breaths that rasp like tearing cloth",
        "soul_reward":   80,
    },
    {
        "name":          "Chitinous Widow",
        "hp":            95,
        "attack":        0,
        "magic_attack":  18,
        "defense":       3,
        "magic_defense": 10,
        "damage_type":   "magic",
        "image":         "chitinous_widow.png",
        "lore":          "Beneath the hollow catacombs, where light dare not trespass, she weaves a lattice of bone and sinew. Once a priestess of the Pale Faith, she was entombed for crimes unspoken, her body reshaped by venom and shadow.",
        "soul_reward":   101,
    },
]

# ── Boss enemies ──────────────────────────────────────────────────────────────
# soul_reward formula: floor((hp * 0.8) + (attack * 5))
# Commit 21: HP adjustments noted inline where changed from original values.
# Refactor: phase2_lore field added to each boss — previously in combat.py.
# Commit 1: all soul_reward values reduced by 40%, rounded to nearest 5.
#           Original values shown in comments for reference.

BOSS_PHASE2_LORE_DEFAULT = (
    "⚠️ SECOND PHASE — The boss staggers — then steadies. "
    "Something ancient and terrible wakes behind its eyes."
)

BOSSES = {
    "Cindergloom": {
        "hp":            380,
        "attack":        0,
        "magic_attack":  30,
        "defense":       6,
        "magic_defense": 20,
        "damage_type":   "magic",
        "image":         "cindergloom.png",
        "lore":          "The final Flame Lord, bound in cinders and regret. Born of divine fire and destined to consume the end of all things. Within the lightless halls of the Forgotten Citadel, his throne rises from a lake of slow-burning ash, each ember a whisper of worlds already claimed. His flesh is a tapestry of charred fissures, glowing faintly with the molten pulse beneath. Horns wreathed in fire arc from his brow like the spires of a dying sun, and his talons drip molten gold that hisses against the blackened stones",
        "soul_reward":   270,   # was 454
        "phase2_lore": (
            "🔥 SECOND PHASE — The Flame Lord's wounds crack open, "
            "spilling rivers of molten gold. The air itself ignites. "
            "\"You dare fan the dying flame? Then burn with it!\""
        ),
    },
    "Lothric and Lorian": {
        "hp":            200,
        "attack":        22,
        "magic_attack":  18,
        "defense":       10,
        "magic_defense": 10,
        "damage_type":   "mixed",
        "image":         "lothric_lorian.png",
        "lore":          "Twin princes of fading flame. One silent and seething, the other bound to a cursed destiny of rekindling.",
        "soul_reward":   160,   # was 270
        "phase2_lore": (
            "⚡ SECOND PHASE — Lorian collapses — and Lothric descends upon his "
            "brother's back, pouring forbidden lightning into the broken body. "
            "They rise as one. The air crackles with desperate power."
        ),
    },
    "Ashen Knight": {
        "hp":            240,
        "attack":        24,
        "magic_attack":  0,
        "defense":       11,
        "magic_defense": 5,
        "damage_type":   "physical",
        "image":         "ashen_knight.png",
        "lore":          "The Ashen Knight looms, his form a grotesque amalgam of charred steel and twisted flesh, as though the armor has grown into him over centuries of penance",
        "soul_reward":   210,   # was 352
        "phase2_lore": (
            "💀 SECOND PHASE — The Ashen Knight tears the visor from his helm "
            "and screams. The ash fused to his flesh begins to glow. "
            "\"I have endured centuries of penance. You will not end it!\""
        ),
    },
    "Pale Drake": {
        "hp":            290,
        "attack":        0,
        "magic_attack":  27,
        "defense":       5,
        "magic_defense": 18,
        "damage_type":   "magic",
        "image":         "pale_drake.png",
        "lore":          "In the wind-scoured depths of the Forgotten Valley, where frost clings even to the bones of the mountains, the Pale Drake slumbers beneath a sky that remembers no sun. His scales, the color of moonlit marble, shimmer with the faint light of dying stars.",
        "soul_reward":   220,   # was 367
        "phase2_lore": (
            "❄️ SECOND PHASE — The Pale Drake rears back and shatters the ice "
            "shelf beneath you. His eyes, once clouded, blaze white. "
            "\"The stars do not forgive trespassers.\""
        ),
    },
    "The Lord of Chains": {
        "hp":            220,
        "attack":        25,
        "magic_attack":  0,
        "defense":       12,
        "magic_defense": 5,
        "damage_type":   "physical",
        "image":         "the_lord_of_chains.png",
        "lore":          "At the shattered heart of the Keep, upon a throne of rusted iron and broken manacles, sits the Lord of Chains. Once a conqueror whose name was a warcry, he traded crown and kin for the thrill of battle's red haze.",
        "soul_reward":   180,   # was 301
        "phase2_lore": (
            "⛓️ SECOND PHASE — The chains binding the Lord of Chains snap "
            "one by one. Each break draws blood — his own. He laughs. "
            "\"Pain is the only throne I need.\""
        ),
    },
    "The Ember Tyrant": {
        "hp":            360,
        "attack":        0,
        "magic_attack":  27,
        "defense":       6,
        "magic_defense": 16,
        "damage_type":   "magic",
        "image":         "the_ember_tyrant.png",
        "lore":          "The Ember Tyrant towers above the blackened earth, his skin a tapestry of cracked obsidian and veins of molten fire. Chains, long since fused to his flesh, drag behind him like the echoes of a broken throne.",
        "soul_reward":   255,   # was 423
        "phase2_lore": (
            "🌋 SECOND PHASE — The Ember Tyrant tears the fused chains "
            "free from his own flesh, roaring as obsidian skin splits. "
            "Magma pours from the wounds. The ground begins to melt."
        ),
    },
    "The Mireborn Serpent": {
        "hp":            230,
        "attack":        25,
        "magic_attack":  0,
        "defense":       10,
        "magic_defense": 6,
        "damage_type":   "physical",
        "image":         "the_mireborn_serpent.png",
        "lore":          "From the depths of the drowned fen rises the Mireborn Serpent, a colossal coil of rotting scales and slick, peat-soaked flesh. Once a lord of the marshlands, he offered his body to an ancient parasite in exchange for dominion eternal.",
        "soul_reward":   185,   # was 309
        "phase2_lore": (
            "🐍 SECOND PHASE — The Mireborn Serpent submerges entirely — "
            "then erupts through the floor behind you, twice the size. "
            "The parasite within pulses with sickly green light."
        ),
    },
    "The Gravewarden": {
        "hp":            250,
        "attack":        24,
        "magic_attack":  16,
        "defense":       10,
        "magic_defense": 10,
        "damage_type":   "mixed",
        "image":         "the_gravewarden.png",
        "lore":          "Beyond the final descent of the Hollow Catacombs, where the air hangs heavy with the dust of centuries, the Gravewarden stands vigil. Draped in funeral raiments stitched from the shrouds of kings, his form is gaunt yet towering, a silhouette crowned with jagged bone and tarnished gold",
        "soul_reward":   190,   # was 320
        "phase2_lore": (
            "☠️ SECOND PHASE — The Gravewarden removes his funeral crown "
            "and drives it into the earth. The buried dead begin to stir. "
            "\"Every soul here is mine to command.\""
        ),
    },
    "The Abyss Watcher": {
        "hp":            280,
        "attack":        28,
        "magic_attack":  20,
        "defense":       12,
        "magic_defense": 11,
        "damage_type":   "mixed",
        "image":         "the_abyss_watcher.png",
        "lore":          "At the brink of the world where the Abyss swallows all light, the Abyss Watcher stands sentinel. Cloaked in tattered black, his form is both man and beast — a knight's frame twisted by the long years in darkness.",
        "soul_reward":   220,   # was 364
        "phase2_lore": (
            "🌑 SECOND PHASE — The Abyss Watcher drives his own sword "
            "through his chest and pulls it free glowing red. "
            "\"The Abyss does not kill me. It feeds me.\""
        ),
    },
    "The Thorn Matriarch": {
        "hp":            240,
        "attack":        0,
        "magic_attack":  28,
        "defense":       6,
        "magic_defense": 16,
        "damage_type":   "magic",
        "image":         "the_thorn_matriarch.png",
        "lore":          "In the heart of the Chapel of Thorns, where rose and briar drink alike from bloodied soil, the Thorn Matriarch waits. Her armor blooms with living barbs, each petal forged from the steel of fallen pilgrims. Long strands of crimson hair drift like banners in the still, suffocating air. She moves with the elegance of a saint and the certainty of a blade, her every step sowing thorns that pierce flesh and spirit alike",
        "soul_reward":   190,   # was 317
        "phase2_lore": (
            "🌹 SECOND PHASE — Crimson thorns erupt from the Thorn Matriarch's "
            "wounds, spreading across the chapel floor. She raises her arms "
            "and the briars respond. \"Every cut is a garden.\""
        ),
    },
    "The Blacksteel Sentinel": {
        "hp":            280,
        "attack":        25,
        "magic_attack":  0,
        "defense":       13,
        "magic_defense": 4,
        "damage_type":   "physical",
        "image":         "the_blacksteel_sentinel.png",
        "lore":          "Within the furnace-lit shadow of the Iron Bastion, the Blacksteel Sentinel waits astride the wreckage of a thousand sieges. His armor is hammered from the very walls he has defended, blackened by the soot of endless forges and scarred by the weapons of would-be conquerors.",
        "soul_reward":   210,   # was 349
        "phase2_lore": (
            "⚒️ SECOND PHASE — The Blacksteel Sentinel drives both fists "
            "into the forge-floor. The entire bastion shudders. His armour "
            "glows white-hot. \"The walls do not fall. Neither do I.\""
        ),
    },
    "Vaelhis, the Unmourned King": {
        "hp":            300,
        "attack":        0,
        "magic_attack":  25,
        "defense":       8,
        "magic_defense": 20,
        "damage_type":   "magic",
        "image":         "vaelhis.png",
        "lore": (
            "He chose the cold willingly, believing it would preserve what the Flame would burn. "
            "He was not wrong. He preserved everything — his court, his memories, his grief. "
            "Vaelhis sits with all of it still, perfectly intact, perfectly alone, in a cold "
            "that has had centuries to deepen. His crown holds the faces of those he loved, "
            "frozen in the moment of their ending. He is not mourning them. He is mourning itself, "
            "given form and given patience."
        ),
        "soul_reward":   220,   # was 365
        "phase2_lore": (
            "❄️ SECOND PHASE — Vaelhis raises his crown and the faces within it open their frozen eyes. "
            "The temperature drops beyond bearing. "
            "\"You carry warmth into my silence. I have waited centuries for the chance to extinguish it.\""
        ),
    },
    "The Drowned Sovereign": {
        "hp":            330,
        "attack":        27,
        "magic_attack":  22,
        "defense":       14,
        "magic_defense": 16,
        "damage_type":   "mixed",
        "image":         "drowned_sovereign.png",
        "lore": (
            "It predates the city built above it. It predates the civilisation that built that city. "
            "The Drowned Sovereign was here when this was a seabed, and it remained when the sea left. "
            "It is not malevolent. It is simply immovable, and immovable things tend to cause damage "
            "simply by existing. Its amber light pulses with a rhythm that matches every living "
            "heartbeat nearby. It has been tracking yours since you stepped off the mechanism."
        ),
        "soul_reward":   240,   # was 399
        "phase2_lore": (
            "🌊 SECOND PHASE — The Drowned Sovereign's amber light turns deep red. "
            "The dried seabed cracks and ancient water begins to seep upward. "
            "\"Bearer. You are persistent. Good. I have not had a worthy ending in a very long time.\""
        ),
    },
    "The Starbound Colossus": {
        "hp":            340,
        "attack":        30,
        "magic_attack":  0,
        "defense":       15,
        "magic_defense": 10,
        "damage_type":   "physical",
        "image":         "starbound_colossus.png",
        "lore": (
            "He fought so many battles that the stars began to track his movements, "
            "drawn by the gravity of his consequence. When he fell, they followed him "
            "into the Shadow Realm and have been waiting there ever since — "
            "a constellation arranged around a defeat, still hoping for a rematch."
        ),
        "soul_reward":   255,   # was 422
        "phase2_lore": (
            "🌟 SECOND PHASE — The Starbound Colossus slams his chain-sword into the pit floor. "
            "The stars in orbit collapse inward, fusing to his armour. "
            "He rises larger, heavier, burning cold. The constellations rearrange into siege formations."
        ),
    },
    "The Gilded Predator": {
        "hp":            310,
        "attack":        25,
        "magic_attack":  25,
        "defense":       12,
        "magic_defense": 14,
        "damage_type":   "mixed",
        "image":         "gilded_predator.png",
        "lore": (
            "It has no fixed form. It wears shapes the way performers wear costumes, "
            "chosen for effect and discarded when the scene demands otherwise. "
            "Its true form is motion itself — and motion, when given teeth and will, "
            "is the most dangerous predator that exists."
        ),
        "soul_reward":   225,   # was 373
        "phase2_lore": (
            "✨ SECOND PHASE — The Gilded Predator abandons all pretence of form. "
            "It becomes light and motion and hunger, cycling through shapes faster than the eye can track. "
            "The bells of the temple toll in frantic counterpoint."
        ),
    },
    "The Saintess of Rot": {
        "hp":            295,
        "attack":        0,
        "magic_attack":  27,
        "defense":       8,
        "magic_defense": 18,
        "damage_type":   "magic",
        "image":         "saintess_of_rot.png",
        "lore": (
            "She was once a healer. She cured so many diseases that she began to wonder "
            "what they were for — what role they played in the design of things. "
            "Her faith is the conclusion she reached after long contemplation. "
            "She does not see rot as corruption. She sees it as completion."
        ),
        "soul_reward":   225,   # was 371
        "phase2_lore": (
            "🌸 SECOND PHASE — The Saintess of Rot opens her arms and the garden responds. "
            "Scarlet blooms erupt from the ground around her, filling the air with spores "
            "so thick they blot the amber light. She smiles. This is her sermon."
        ),
    },
    "The Moon-Sworn Blade": {
        "hp":            320,
        "attack":        28,
        "magic_attack":  20,
        "defense":       13,
        "magic_defense": 15,
        "damage_type":   "mixed",
        "image":         "moon_sworn_blade.png",
        "lore": (
            "She took her oath to the moon because the moon, unlike the sun, "
            "acknowledges that it only reflects rather than generates. "
            "She found this honest. Her blade has never been raised in a cause "
            "she did not believe to be true. She is uncertain what to believe about you. "
            "The uncertainty is, itself, a form of respect."
        ),
        "soul_reward":   240,   # was 396
        "phase2_lore": (
            "🌙 SECOND PHASE — The Moon-Sworn Blade sheathes her weapon. "
            "When she draws it again, it carries the moon's full weight — "
            "tidal, inevitable, pulling everything toward her orbit. "
            "\"You fight honestly. Now let me show you what honesty costs.\""
        ),
    },
    "Mesmereth, the Serpent Prince": {
        "hp":            420,
        "attack":        28,
        "magic_attack":  30,
        "defense":       18,
        "magic_defense": 22,
        "damage_type":   "mixed",
        "image":         "mesmereth.png",
        "lore": (
            "He served the principle of transformation itself — the force that insists "
            "all things must change and that the quality of change matters. "
            "He shed what he was and became what the realm needed, and has been "
            "what the realm needs for so long he has forgotten what he was before. "
            "This forgetting is the only thing that still grieves him. "
            "His cold flame does not burn. It illuminates. Each strike reveals a truth "
            "the struck has been avoiding. He is the last of his kind. He chose to be."
        ),
        "soul_reward":   285,   # was 476
        "phase2_lore": (
            "🐍 SECOND PHASE — Mesmereth, the Serpent Prince sheds his contained form entirely. "
            "The sanctum fills with cold flame — every surface, the air itself, burning "
            "with transformative light. His voice fills the space from everywhere at once: "
            "\"You have come far enough to see what I am. Now see what you are.\""
        ),
    },
}