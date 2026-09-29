"""Lot 09 : QRA (rouges et bleues) et CAP à la demande.

QRA : réponse graduée, plusieurs variantes tirées au hasard par niveau, 60 s avant décollage, pas de
réaction aux hélicoptères (dit au briefing). Rayons choisis pour ne couvrir aucune base adverse avec
slots : MinVody 40 nm (Nalchik à 49), Krasnodar 55 nm (Sochi à 101, Taman à 94), Kutaisi 57 nm,
Gudauta 40 nm.
CAP rouges : l'échelle de menaces de la v5, sur la mer à l'ouest (secteur d'entraînement) ; CAP bleues :
opposition pour les joueurs rouges.
Emports : groupes de GermanyCW-v6 (tools/loadouts-germanycw.json).
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from lib import AIRFIELDS, BLUE, RED, Batch, bullseye, nm, off, pylons  # noqa: E402

b = Batch()
NM = 1852
LOAD = {"MiG-29S": "QRA Berlin - MiG-29S A", "Su-27": "QRA Berlin - Su-27", "Su-30": "QRA Berlin - Su-30",
        "MiG-31": "OnDemand-CAP MiG-31 - Neuruppin - FL400", "F-16C_50": "QRA Celle - F-16C A", "F-15C": "QRA Celle - F-15C"}


def qra(name, side, base, radius_nm, variants, levels):
    """variants: {suffixe: type} ; levels: [(nb d'intrus, [suffixes], combien en tirer)]."""
    pos = AIRFIELDS[base]
    groups = [{"name": f"{name} - {suf}", "units": [{"type": typ, "count": 2}], "position": {"x": pos[0], "y": pos[1]},
               "altitude_ft": 15000, "speed_kt": 350, "pylons": pylons(LOAD[typ])} for suf, typ in variants.items()]
    b.act("create_qra", name=name, **side, trigger_zone=name.replace(" ", "-"), position={"x": pos[0], "y": pos[1]},
          radius=radius_nm * NM, groups=groups, enemy_coalitions=["RED" if side is BLUE else "BLUE"],
          qra={"groups_by_enemy_count": [{"enemy_count": n, "groups": [f"{name} - {s}" for s in sufs], "random_pick": k}
                                         for n, sufs, k in levels],
               "airport_link": base, "delay_before_rearming": 600, "delay_before_activating": 60,
               "react_on_helicopters": False})


qra("QRA MinVody", RED, "Mineralnye Vody", 40,
    {"Su-30": "Su-30", "Su-27": "Su-27", "MiG-31": "MiG-31"},
    [(1, ["Su-27", "Su-30"], 1), (3, ["Su-27", "Su-30", "MiG-31"], 2)])
qra("QRA Krasnodar", RED, "Krasnodar-Pashkovsky", 55,
    {"MiG-29S": "MiG-29S", "Su-27": "Su-27", "MiG-31": "MiG-31"},
    [(1, ["MiG-29S", "Su-27"], 1), (3, ["MiG-29S", "Su-27", "MiG-31"], 2)])
qra("QRA Kutaisi", BLUE, "Kutaisi", 57, {"F-16C": "F-16C_50", "F-15C": "F-15C"},
    [(1, ["F-16C", "F-15C"], 1), (3, ["F-16C", "F-15C"], 2)])
qra("QRA Gudauta", BLUE, "Gudauta", 40, {"F-16C": "F-16C_50", "F-15C": "F-15C"},
    [(1, ["F-16C", "F-15C"], 1), (3, ["F-16C", "F-15C"], 2)])


def cap(title, side, typ, a, brg, fl, kt, what, count=2):
    bb = off(a, brg, 40 * NM)
    mid = ((a[0] + bb[0]) / 2, (a[1] + bb[1]) / 2)
    p = dict(mission_name=title, units=[{"type": typ, "count": count}], **side, position={"x": a[0], "y": a[1]},
             route=[{"x": bb[0], "y": bb[1], "altitude_ft": fl * 100}], altitude_ft=fl * 100, speed_kt=kt,
             cap={"menu_name": title, "briefing": f"{what} Hippodrome au FL{fl} centré sur {bullseye(mid)}.",
                  "default": False, "activated": True})
    if typ in LOAD:
        p["pylons"] = pylons(LOAD[typ])
    b.act("create_cap_mission", **p)


# rouges : secteur Ouest, sur la mer (positions de la v5)
cap("CAP Ouest - Tu-22M3 - FL300", RED, "Tu-22M3", (-302129, 177300), 90, 300, 420, "Deux Tu-22M3 : bombardier à intercepter.")
cap("CAP Ouest - Tu-95 - FL200", RED, "Tu-95MS", (-301381, 177752), 90, 200, 380, "Deux Tu-95 : bombardier lent à intercepter.")
cap("CAP Ouest - Su-27 - FL300", RED, "Su-27", (-300973, 177905), 90, 300, 420, "Paire de Su-27 armés Fox 1 (guidage radar semi-actif).")
cap("CAP Ouest - MiG-29S - FL300", RED, "MiG-29S", (-300415, 178155), 90, 300, 420, "Paire de MiG-29S armés Fox 3.")
cap("CAP Ouest - MiG-31 - FL300", RED, "MiG-31", (-299710, 178366), 90, 300, 480, "Paire de MiG-31 : intercepteur haut et rapide, Fox 3 longue portée.")
cap("Khashuri - L-39C - FL100", RED, "L-39C", (-390413, 713312), 0, 100, 250, "Paire de L-39C lents cap au nord, vers Khashuri : cible d'interception facile.")
# bleues : opposition pour les joueurs rouges
cap("CAP F-16C - Gudauta - FL250", BLUE, "F-16C_50", (-185000, 540000), 90, 250, 420, "Paire de F-16C armés Fox 3 : opposition pour les joueurs rouges.")
cap("CAP F-15C - Beslan - FL300", BLUE, "F-15C", (-175000, 790000), 90, 300, 420, "Paire de F-15C armés Fox 3 : opposition pour les joueurs rouges.")
b.save("09-qra-cap.json")
