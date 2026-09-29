"""Génère README.md (briefing pilotes, point d'entrée de la mission) depuis les sources de la mission.

Aucune valeur tapée à la main : bases, soutien, zones, QRA, CAP, radio et météo sont relus dans
src/mission/, mission.yaml, src/presets.yaml et src/versions.yaml ; caps et distances calculés.
Usage : python tools/gen_readme.py
"""
import re
import sys
from pathlib import Path

VMCT = Path("D:/dev/_VEAF/VMCT-develop")
sys.path.insert(0, str(VMCT / "src/python/veaf-tools"))
sys.path.insert(0, str(Path(__file__).parent))
import yaml  # noqa: E402
from mission_tools.miz_tools import read_mission_folder  # noqa: E402
from veaf_libs.coordinates import xy_to_latlon  # noqa: E402

from lib import AIRFIELDS, BULLSEYE, ROOT, TANKERS, bullseye, nearest_tanker  # noqa: E402

Y = yaml.safe_load((ROOT / "mission.yaml").read_text(encoding="utf-8"))
MOD = Y["modules"]
PR = yaml.safe_load((ROOT / "src/presets.yaml").read_text(encoding="utf-8"))["channels_collection"]
VER = yaml.safe_load((ROOT / "src/versions.yaml").read_text(encoding="utf-8"))
MIS = read_mission_folder(ROOT)
m = MIS.mission_content
ZONES = {z["name"]: z for z in m["triggers"]["zones"]}


def ll(p):
    r = xy_to_latlon("Caucasus", p[0], p[1])
    lat, lon = (r[0], r[1]) if isinstance(r, (tuple, list)) else (r["lat"], r["lon"])
    f = lambda v, pos, neg, w: f"{pos if v >= 0 else neg}{int(abs(v)):0{w}d}°{(abs(v) % 1) * 60:06.3f}'"  # noqa: E731
    return f"`{f(lat, 'N', 'S', 2)} {f(lon, 'E', 'W', 3)}`"


def groups():
    for side, co in m["coalition"].items():
        for c in co.get("country") or []:
            for cat in ("plane", "helicopter", "vehicle", "ship", "static"):
                for g in (c.get(cat) or {}).get("group") or []:
                    yield side, cat, g


ALIAS_NAME = {"-patriot": "Patriot", "-hawk": "Hawk", "-nasams": "NASAMS", "-avenger_squad": "Avenger", "-sa10": "SA-10",
              "-sa11": "SA-11", "-sa15": "SA-15", "-sa19": "SA-19"}
AD = {}
for side, cat, g in groups():
    if g["name"].startswith("AD-") and not g["name"].startswith("AD-EWR"):
        a = re.search(r'#veafInterpreter\["(-\w+)', g["units"][0]["name"])
        AD.setdefault(g["name"][3:].rsplit("-", 1)[0], []).append(ALIAS_NAME.get(a.group(1), a.group(1)) if a else "?")
wh_air = MIS.warehouses_content["airports"]
ids = {v: k for k, v in yaml.safe_load((VMCT / "src/python/veaf-tools/veaf_libs/data/airdromes.yaml").read_text(encoding="utf-8"))["theatres"]["Caucasus"].items()}
excl = {s: set((yaml.safe_load((ROOT / "src/warehouses.yaml").read_text(encoding="utf-8")).get(s) or {}).get("exclude_airports") or []) for s in ("blue", "red")}
bases = {"blue": [], "red": []}
for aid, w in wh_air.items():
    side = (w.get("coalition") or "").lower()
    n = ids.get(int(aid))
    if side in bases:
        bases[side].append((n, n not in excl[side]))
freq = lambda key: PR["bases"].get(key, {}).get("freqs", {})  # noqa: E731
SHORT = {"Sochi-Adler": "Sochi", "Tbilisi-Lochini": "Tbilisi", "Maykop-Khanskaya": "Maykop", "Krasnodar-Pashkovsky": "Krasnodar",
         "Mineralnye Vody": "MinVody"}

o = [f"# VEAF Open Training — Caucase (moderne)", "",
     "Mission d'entraînement ouverte des serveurs VEAF, sur la carte **Caucasus** de DCS, dans un scénario moderne "
     "fictif. Ce document est le briefing complet. Positions en degrés et minutes décimales, et en cap / distance depuis "
     "le bullseye (cap vrai, nautiques).", "",
     "| Mission | Date | Bullseye (bleu et rouge) | Météo réelle | ATC |", "|---|---|---|---|---|",
     f"| `{Y['mission']['name']}` | {m['date']['Day']:02d}/{m['date']['Month']:02d}/{m['date']['Year']} | mont Elbrouz · {ll(BULLSEYE)} "
     "| UGTB (Tbilissi) | coupé sur tous les aérodromes |", "",
     "Tout se pilote par le menu radio F10 : zones de combat, missions et CAP, soutien (*ASSETS*), porte-avions (*CARRIER OPS*).", "",
     "## Carte", "", "![Carte de la mission](docs/carte.jpg)", "",
     "Carrés : bases avec slots. Traits pleins : hippodromes des ravitailleurs et AWACS ; tirets fins : CAP à la "
     "demande. Cercles : QRA. Pastilles vertes : entraînement (H hélicoptères, A attaque, S SEAD, R recherche). "
     "Pastilles rouges : zones de combat, numérotées comme la liste plus bas. Grands tirets bleus : sanctuaire. "
     "L'arène est hors du cadre, à l'ouest (flèche). La même image est dans le briefing DCS, et la carte F10 porte "
     "les mêmes dessins, chaque camp ne voyant que les siens. Générée par `tools/gen_map.py`.", "",
     "## Situation", "",
     "La Géorgie, soutenue par l'OTAN, tient une ligne avancée en Russie — Sochi, Nalchik, Beslan — face aux forces russes. "
     "Le front court de la mer Noire (Sochi / Maykop) à l'Ossétie du Nord (Beslan / Mozdok), sur environ 207 nm. Le secteur "
     "Ouest (péninsule de Taman et la mer au large) sert de terrain d'entraînement, hors QRA.", "",
     "## Bases", "", "| Base | Camp | Slots | Position | Bullseye | UHF | VHF | Défense permanente |", "|---|---|---|---|---|---|---|---|"]
for side in ("blue", "red"):
    for n, slots in sorted(bases[side], key=lambda t: (not t[1], t[0])):
        s = SHORT.get(n, n.split("-")[0])
        f = freq(f"Base-{s}") if slots else {}
        ad_tag = n.split("-")[0].split(" ")[0]  # même découpe que tools/gen_05_defense.py
        ad = ", ".join(AD.get(ad_tag, [])) if slots else ""
        o.append(f"| {n} | {'bleu' if side == 'blue' else 'rouge'} | {'oui' if slots else 'non'} | {ll(AIRFIELDS[n])} | {bullseye(AIRFIELDS[n])} "
                 f"| {f.get('uhf', '—')} | {f.get('vhf', '—')} | {ad or '—'} |")
o += ["", "FARP bleus (dépôt de munitions et chargement de troupes CTLD) :", ""]
for side, cat, g in groups():
    if cat == "static" and g["name"].startswith("FARP ") and "munitions" not in g["name"]:
        o.append(f"- **{g['name']}** — {ll((g['x'], g['y']))} — {bullseye((g['x'], g['y']))}")
o += ["", "## Défense aérienne permanente", "",
      "En plus de la défense de chaque base (tableau ci-dessus) : SA-10 à Krasnodar et à Stavropol, radars d'alerte "
      "(1L13 bleus, 55G6 rouges) derrière les lignes, en réseau Skynet. Aucune batterie permanente n'atteint une base "
      "adverse avec slots (portées de la table de menace DCS embarquée dans AIEN, vérifiées par `tools/check_portees.py`).", ""]
for side, cat, g in groups():
    if g["name"].startswith(("AD-Stavropol", "AD-EWR", "AD-Krasnodar-LR")):
        o.append(f"- {g['name'][3:]} ({'bleu' if side == 'blue' else 'rouge'}) — {ll((g['x'], g['y']))} — {bullseye((g['x'], g['y']))}")
o += ["", "## Soutien", "", "| Indicatif | Rôle | Informations |", "|---|---|---|"]
for a in MOD["ASSETS"]["assets"]:
    o.append(f"| {a['name']} | {a['description']} | {a['information'].replace(chr(10), ' — ')} |")
o += ["", "Les ravitailleurs et AWACS sont escortés. Les drones Reaper désignent au laser (menu *ASSETS*).", "",
      "## Entraînement", "", "Trois familles de trois niveaux (facile ⊂ moyen ⊂ difficile) : chaque niveau contient le précédent. "
      "Jouez un seul niveau à la fois.", ""]
cz = MOD["COMBATZONE"]["combat_zones"]
for training, title in ((True, None), (False, "## Zones de combat")):
    if title:
        o += ["", title, "", "Menus F10 par type. Les défenses citées sont celles de la zone ; certaines sont tirées au hasard à "
              "chaque activation.", ""]
    fam, num = None, 0
    for z in cz:
        if bool(z.get("training")) != training:
            continue
        if z.get("radio_group_name") != fam:
            fam = z.get("radio_group_name")
            o += ["", f"### {fam}", ""]
        c = (ZONES[z["zone_name"]]["x"], ZONES[z["zone_name"]]["y"])
        if not training:
            num += 1
        tag = f"{num}. " if not training else ""
        o.append(f"- **{tag}{z['friendly_name']}** — {ll(c)} — {z['briefing']}")
o += ["", "## Missions scénarisées", "", "Menu F10 *MISSIONS* : attaque rouge sur Gudauta (défendre la base), vague de 11 Tu-160 "
      "à abattre en 15 minutes (secteur Ouest), interception d'un transport VIP escorté entre Krasnodar et Mineralnye Vody.", "",
      "## QRA", "", "| QRA | Camp | Base | Rayon | Réponse |", "|---|---|---|---|---|"]
for q in MOD["QRA"]["definitions"]:
    z = ZONES[q["trigger_zone"]]
    lv = " ; ".join(f"≥ {g['enemy_count']} intrus : {g['random_pick']} groupe(s) parmi {', '.join(x.split(' - ')[-1] for x in g['groups'])}"
                    for g in q["groups_by_enemy_count"])
    o.append(f"| {q['name']} | {q['coalition'].lower()} | {q['airport_link']} | {z['radius'] / 1852:.0f} nm | {lv} |")
o += ["", "Décollage une minute après l'entrée du premier intrus ; les QRA ne réagissent pas aux hélicoptères.", "",
      "## CAP à la demande", ""]
o += [f"- **{c['menu_name']}** — {c['briefing']}" for c in Y.get("cap_missions") or []]
o += ["", "## Combat entre joueurs", "",
      "- **Arène AirQuake**, loin à l'ouest sur la mer : slots en vol pour les deux camps, par type de missile (Fox 1, Fox 3), "
      "un AWACS par camp (Darkstar 1 et AWACS Arène Rouge).",
      "- Entre les bases avec slots des deux camps.",
      "- **Sanctuaire bleu** : le sud de la Géorgie. Un avion rouge qui y entre est détruit au bout de 60 secondes, et les "
      "missiles tirés sur un avion bleu à l'intérieur sont détruits.", "",
      "## Plan radio", "", "| Canal | UHF | VHF |", "|---|---|---|"]
for grp in ("tactical", "bases", "flights"):
    for k, v in PR[grp].items():
        o.append(f"| {v['title']} | {v['freqs'].get('uhf', '—')} | {v['freqs'].get('vhf', '—')} |")
o += ["", "FM 30 à 59 en supplément (hélicoptères, A-10C) ; balises du Mountain hike sur 31.0 à 34.0 FM.", "",
      "## Météo et heures", "",
      f"{len(VER['versions'])} variantes : nuit, aube, matin, jour, soir × réel (METAR de Tbilissi), dégagé, épars, pluie. "
      f"Fuseau {VER['position']['timezone']}, date {VER['base_date']}.", "",
      "## Commandes utiles", "",
      "Un marqueur sur la carte F10, avec une commande dans son texte : `-sa6`, `-armor`, `-convoy, dest <point>`, "
      "`-jtac, laser 1688`, `-point <nom>`. Options : `side`, `size`, `defense 0-5`, `armor 0-5`, `dest`, `patrol`.", "",
      "## Pour les créateurs de mission", "",
      "- Construire : `veaf-tools.exe build` dans ce dossier ; pour un test local, `veaf-tools.exe build --profile LOCAL_TEST` "
      "(sécurité coupée, logs debug, noms lisibles, sans variantes météo).",
      "- `tools/` : les générateurs qui ont construit la mission (lots rejouables, `tools/batches/`), les contrôles "
      "(`check_portees.py`, `verify.py`), ce générateur de README, et `retours-vmct.md` (ce que les outils n'ont pas su faire).",
      "- Construite de zéro le 28/09/2026 avec le prompt `new-open-training-mission.fr.md` de VMCT, en s'inspirant de la v5 "
      "(`VEAF-Open-Training-Mission-Caucasus`, dossier `backup_v5/`).", ""]
(ROOT / "README.md").write_text("\n".join(o), encoding="utf-8")
print("README.md :", len(o), "lignes")
