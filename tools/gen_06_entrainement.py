"""Lot 06 : zones d'entraînement — 3 familles × 3 niveaux (facile ⊂ moyen ⊂ difficile), + Mountain hike.

Chaque niveau ne contient que ses ajouts ; `includes:` fait inclure le niveau inférieur.
Facile = statiques inertes ; moyen / difficile = faux porteurs #command, avec balises de tirage.
Usage : python tools/gen_06_entrainement.py [fragment de nom de zone, pour ne générer qu'elle]
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from lib import BLUE, RED, ROOT, Batch, bullseye, cmd_unit, nearest_tanker, off  # noqa: E402

b = Batch()
only = sys.argv[1] if len(sys.argv) > 1 else None


def xy(p):
    return {"x": p[0], "y": p[1]}


def zone(name, center, radius, groups, category, friendly, family, briefing, includes=None, completable=True, side=RED):
    if only and only not in name:
        return
    cz = {"friendly_name": friendly, "radio_group_name": family, "training": True, "briefing": briefing,
          "completable": completable}
    if includes:
        cz["includes"] = [includes]
    b.act("create_combat_zone", zone_name=name, position=xy(center), radius=radius,
          groups=groups, **side, category=category, combat_zone=cz)


def where(c):
    return f"{bullseye(c)}. Ravitailleur le plus proche : {nearest_tanker(c)}."


MED_AAA = [("-zu23", "Ural-375 ZU-23"), ("-zu23", "Ural-375 ZU-23"), ("-shilka", "ZSU-23-4 Shilka"),
           ("-shilka", "ZSU-23-4 Shilka")]

# ── 1. Hélicoptères : range de Kobuleti (v5), FARP Casimir à côté ─────────────────────────────
K = (-328279, 631220)
stat = json.loads((ROOT / "tools/v5-kobuleti-statiques.json").read_text())
zone("combatZone_Kobuleti_Easy", K, 3000,
     [{"name": f"cible-{i + 1:02d}", "units": [{"type": s["t"], "name": f"combatZone_Kobuleti_Easy-cible-{i + 1:02d}"}],
       "position": {"x": s["x"], "y": s["y"]}, "keep_position": True} for i, s in enumerate(stat)],
     "static", "Kobuleti - hélicoptères - facile", "Entraînement hélicoptères",
     "Range de Kobuleti, 6 nm au sud-ouest de la base. Cibles inertes (statiques) : blindés, camions, "
     "missiles SCUD, bâtiments. Aucune défense. " + where(K))
zone("combatZone_Kobuleti_Medium", K, 3000,
     [{"name": f"aaa-{i + 1}", "units": [cmd_unit(a, t, f"KobM-{i + 1}", '#spawngroup="aaa" #spawncount=2')],
       "position": xy(off(K, 90 * i + 45, 1200))} for i, (a, t) in enumerate(MED_AAA)],
     "vehicle", "Kobuleti - hélicoptères - moyen", "Entraînement hélicoptères",
     "Range de Kobuleti, cibles du niveau facile plus DCA légère : deux pièces tirées parmi quatre "
     "(ZU-23, Shilka). " + where(K), includes="combatZone_Kobuleti_Easy")
HARD_K = [("-sa13_squad", "Strela-10M3"), ("-sa9_squad", "Strela-1 9P31"), ("-sa13_squad", "Strela-10M3"),
          ("-sa18s", "SA-18 Igla-S manpad"), ("-sa18s", "SA-18 Igla-S manpad")]
zone("combatZone_Kobuleti_Hard", K, 3000,
     [{"name": f"sr-{i + 1}", "units": [cmd_unit(a, t, f"KobH-{i + 1}", '#spawngroup="sr" #spawncount=3')],
       "position": xy(off(K, 72 * i, 1800))} for i, (a, t) in enumerate(HARD_K)],
     "vehicle", "Kobuleti - hélicoptères - difficile", "Entraînement hélicoptères",
     "Range de Kobuleti, niveau moyen plus une défense courte portée à guidage infrarouge : trois systèmes "
     "tirés parmi SA-13, SA-9 et MANPADS. " + where(K), includes="combatZone_Kobuleti_Medium")

# ── 2. Avions d'attaque : plateau d'Akhalkalaki (135 nm du front) ──────────────────────────────
A = off((-360693, 777466), 90, 5000)
EASY_A = ["T-72B", "T-72B", "T-72B", "BMP-2", "BMP-2", "BTR-80", "Ural-375", "Ural-375", "ZIL-131 KUNG", "Ural-375 PBU"]
zone("combatZone_Akhalkalaki_Easy", A, 3000,
     [{"name": f"cible-{i + 1:02d}", "units": [{"type": t, "name": f"combatZone_Akhalkalaki_Easy-cible-{i + 1:02d}"}],
       "position": xy(off(A, 36 * i, 300 + 60 * i))} for i, t in enumerate(EASY_A)],
     "static", "Akhalkalaki - attaque - facile", "Entraînement attaque",
     "Plateau d'Akhalkalaki, sud de la Géorgie. Colonne blindée à l'arrêt, cibles inertes (statiques). "
     "Aucune défense. " + where(A))
zone("combatZone_Akhalkalaki_Medium", A, 3000,
     [{"name": "blindes-1", "units": [cmd_unit("-armor, defense 0, size 6", "T-72B", "AkhM-1")], "position": xy(off(A, 200, 1500))},
      {"name": "blindes-2", "units": [cmd_unit("-armor, defense 0, size 6", "T-72B", "AkhM-2")], "position": xy(off(A, 20, 1500))}]
     + [{"name": f"aaa-{i + 1}", "units": [cmd_unit(a, t, f"AkhM-a{i + 1}", '#spawngroup="aaa" #spawncount=2')],
         "position": xy(off(A, 90 * i + 45, 1000))} for i, (a, t) in enumerate(MED_AAA)],
     "vehicle", "Akhalkalaki - attaque - moyen", "Entraînement attaque",
     "Plateau d'Akhalkalaki, cibles du niveau facile plus deux compagnies blindées vivantes et une DCA "
     "légère (deux pièces tirées parmi quatre). " + where(A), includes="combatZone_Akhalkalaki_Easy")
HARD_A = [("-sa8", "Osa 9A33 ln"), ("-sa15", "Tor 9A331"), ("-sa13_squad", "Strela-10M3"), ("-sa19", "2S6 Tunguska")]
zone("combatZone_Akhalkalaki_Hard", A, 3000,
     [{"name": "blindes-3", "units": [cmd_unit("-armor, defense 0, size 8, armor 4", "T-72B", "AkhH-1")], "position": xy(off(A, 110, 1800))}]
     + [{"name": f"sr-{i + 1}", "units": [cmd_unit(a, t, f"AkhH-s{i + 1}", '#spawngroup="sr" #spawncount=2')],
         "position": xy(off(A, 90 * i, 2000))} for i, (a, t) in enumerate(HARD_A)]
     + [{"name": "manpads", "units": [cmd_unit("-sa18s", "SA-18 Igla-S manpad", "AkhH-m1")], "position": xy(off(A, 300, 800))}],
     "vehicle", "Akhalkalaki - attaque - difficile", "Entraînement attaque",
     "Plateau d'Akhalkalaki, niveau moyen plus un bataillon blindé et une défense courte portée réaliste : "
     "deux systèmes tirés parmi SA-8, SA-15, SA-13 et SA-19, plus des MANPADS. " + where(A),
     includes="combatZone_Akhalkalaki_Medium")

# ── 3. SEAD / DEAD : secteur Ouest, péninsule de Taman (loin de tout ce qui est bleu) ──────────
T = (20000, 215000)
zone("combatZone_Taman_Easy", T, 6000,
     [{"name": "sa6", "units": [cmd_unit("-sa6", "Kub 2P25 ln", "TamE-1")], "position": xy(T)}],
     "vehicle", "Taman - SEAD - facile", "Entraînement SEAD",
     "Péninsule de Taman, secteur Ouest. Une batterie SA-6 seule, sans radar d'alerte. " + where(T))
zone("combatZone_Taman_Medium", T, 6000,
     [{"name": "sa15", "units": [cmd_unit("-sa15", "Tor 9A331", "TamM-1")], "position": xy(off(T, 45, 1500))},
      {"name": "sa8", "units": [cmd_unit("-sa8", "Osa 9A33 ln", "TamM-2")], "position": xy(off(T, 225, 1500))},
      {"name": "aaa", "units": [cmd_unit("-shilka", "ZSU-23-4 Shilka", "TamM-3")], "position": xy(off(T, 135, 800))}],
     "vehicle", "Taman - SEAD - moyen", "Entraînement SEAD",
     "Péninsule de Taman, le SA-6 du niveau facile protégé par une défense courte portée (SA-15, SA-8, "
     "Shilka). " + where(T), includes="combatZone_Taman_Easy")
zone("combatZone_Taman_Hard", T, 6000,
     [{"name": "sa10", "units": [cmd_unit("-sa10", "S-300PS 5P85C ln", "TamH-1")], "position": xy(off(T, 0, 4000))},
      {"name": "sa11", "units": [cmd_unit("-sa11", "SA-11 Buk LN 9A310M1", "TamH-2")], "position": xy(off(T, 270, 3500))},
      {"name": "ewr", "units": [{"type": "55G6 EWR", "name": "combatZone_Taman_Hard-ewr"}], "position": xy(off(T, 180, 3000))}],
     "vehicle", "Taman - SEAD - difficile", "Entraînement SEAD",
     "Péninsule de Taman, réseau intégré complet sous Skynet : SA-10 longue portée, SA-11, le SA-6 et la "
     "courte portée des niveaux inférieurs, et un radar d'alerte 55G6. " + where(T),
     includes="combatZone_Taman_Medium")

# ── Mountain hike (v5) : recherche d'un équipage d'hélicoptère abattu ──────────────────────────
CRASH = (-167998, 629239)
zone("combatZone_MountainHike", (-172591, 634578), 36576,
     [{"name": "epave", "units": [{"type": "Mi-8MT", "name": "combatZone_MountainHike-epave"}],
       "position": xy(CRASH), "keep_position": True}],
     "static", "Mountain hike - équipage abattu", "Entraînement recherche",
     "Un Mi-8 ami s'est écrasé en montagne, 45 nm au nord-est de Soukhoumi, près de la frontière russe. "
     "Décollez du FARP Kodori, suivez la vallée vers le nord-est et localisez l'épave. Balises FM sur "
     "l'itinéraire : MH01 31.0, MH02 32.0, MH03 33.0 ; l'équipage émet un SOS sur 34.0 FM. "
     + bullseye(CRASH) + ".", completable=False, side=BLUE)

b.save("06-entrainement.json" if not only else f"06-test-{only}.json")
