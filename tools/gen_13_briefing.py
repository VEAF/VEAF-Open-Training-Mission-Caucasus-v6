"""Lot 13 : date et heure, bullseye commun (mont Elbrouz), briefing.

Chiffres calculés depuis tools/lib.py (mêmes sources que les groupes).
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from lib import BULLSEYE, TANKERS, Batch  # noqa: E402

b = Batch()
b.act("set_mission_date", date="2022-06-29", start_time="08:00")
for side in ("blue", "red"):
    b.act("set_bullseye", coalition=side, position={"x": BULLSEYE[0], "y": BULLSEYE[1]})

tankers = "\n".join(f"- {n} : TACAN {tc}, {f:.1f} MHz, FL{fl}" for n, (_c, fl, tc, f) in TANKERS.items())
situation = f"""VEAF Open Training - Caucase (moderne, 2022)

La Géorgie, soutenue par l'OTAN, tient une ligne avancée en Russie (Sochi, Nalchik, Beslan) face aux forces russes. Le front court de la mer Noire (Sochi / Maykop) à l'Ossétie du Nord (Beslan / Mozdok).

BULLSEYE : mont Elbrouz, commun aux deux camps.

BASES BLEUES (slots) : Sochi, Gudauta, Batumi, Kobuleti, Kutaisi, Nalchik, Tbilissi, Vaziani (base mère), Beslan. FARP : Kaspi, Java, Ritsa, Lentehi, Aibgha, Beslan Nord, Krasnaya, Kodori, Dzhvari, Casimir.
BASES ROUGES (slots) : Maykop, Krasnodar-Pashkovsky, Mineralnye Vody, Mozdok.

RAVITAILLEURS
{tankers}
Porte-avions Stennis au large de Batumi : TACAN 10X, ICLS 10, Link 4 et tour 225.0 ; S-3B TACAN 75Y, 290.9.
Tarawa : TACAN 11X, ICLS 11, tour 226.0.

AWACS : Magic 1 (ouest) 265.0, Overlord 1 (est) 266.0.
Drones laser : Reaper 1 (Beslan, code 1688, 118.8 AM), Reaper 2 (Psebay, code 1687, 118.9 AM).

ZONES : menu F10 > VEAF > zones de combat. Entraînement hélicoptères (Kobuleti), attaque (Akhalkalaki), SEAD (Taman, secteur Ouest), recherche (Mountain hike), puis 16 vraies zones : front, SEAD, convois, frappe, OCA, antinavire.

QRA : rouges sur Mineralnye Vody (40 nm) et Krasnodar (55 nm) ; bleues sur Kutaisi (57 nm) et Gudauta (40 nm). Elles décollent une minute après l'entrée du premier intrus et ne réagissent pas aux hélicoptères. Le secteur Ouest (Taman, mer) est hors QRA.

COMBAT ENTRE JOUEURS : seulement dans l'arène AirQuake (slots en vol, loin à l'ouest) et entre les bases avec slots des deux camps. Le sud de la Géorgie est un sanctuaire bleu : un avion rouge qui y entre est détruit au bout de 60 secondes.

COMMANDES VEAF : un marqueur sur la carte F10 avec une commande, par exemple -sa6, -armor, -convoy, dest <point>, -jtac.

METAR : ${{METAR}}"""
b.act("set_briefing", sortie="VEAF Open Training - Caucase", situation=situation,
      blue_task="Choisissez une base, un avion, et une zone dans le menu F10 : entraînement, zones de combat, CAP à la demande ou missions scénarisées.",
      red_task="Défendez l'espace aérien russe depuis Maykop, Krasnodar, Mineralnye Vody ou Mozdok ; CAP bleues à la demande pour l'opposition. Le sud de la Géorgie est interdit (sanctuaire).")
b.save("13-briefing.json")
