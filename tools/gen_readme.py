"""Génère README.md (briefing pilotes, point d'entrée de la mission) depuis les sources de la mission.

Aucune valeur tapée à la main : bases, soutien, zones, QRA, CAP, radio et météo sont relus dans
src/mission/, mission.yaml, src/presets.yaml et src/versions.yaml ; caps et distances calculés.
Usage : python tools/gen_readme.py
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from paths import VMCT  # noqa: E402  (met aussi le code VMCT sur sys.path)
import yaml  # noqa: E402
from mission_tools.miz_tools import read_mission_folder  # noqa: E402
from veaf_libs.coordinates import xy_to_latlon  # noqa: E402

from gen_map import ZOOMS  # noqa: E402  (la liste des zooms, telle que gen_map.py les dessine)
from lib import AIRFIELDS, BULLSEYE, ROOT, TANKERS, bullseye, nearest_tanker  # noqa: E402

ZOOM = {slug: (f"docs/cartes/carte_{i:02d}_{slug}.jpg", title) for i, (slug, title, _refs) in enumerate(ZOOMS, 1)}


def zooms(*slugs):
    """Les cartes zoomées d'une section, deux par ligne, chacune s'ouvrant en grand au clic."""
    if len(slugs) == 1:
        f, t = ZOOM[slugs[0]]
        return [f"[![{t}]({f})]({f})", ""]
    cells = [f'<td width="50%"><a href="{ZOOM[s][0]}"><img src="{ZOOM[s][0]}" alt="{ZOOM[s][1]}"></a><br>'
             f'<sub>{ZOOM[s][1]}</sub></td>' for s in slugs]
    rows = ["<tr>" + "".join(cells[k:k + 2]) + "</tr>" for k in range(0, len(cells), 2)]
    return ["<table>" + "".join(rows) + "</table>", ""]

Y = yaml.safe_load((ROOT / "mission.yaml").read_text(encoding="utf-8"))
MOD = Y["modules"]
PR = yaml.safe_load((ROOT / "src/presets.yaml").read_text(encoding="utf-8"))["channels_collection"]
VER = yaml.safe_load((ROOT / "src/versions.yaml").read_text(encoding="utf-8"))
import json  # noqa: E402
TOOLS_VERSION = json.loads((ROOT / "published/veaf-version.json").read_text(encoding="utf-8"))["version"]
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

o = [f"# VEAF Open Training — Caucase (moderne)", "",
     "Mission d'entraînement ouverte des serveurs VEAF, sur la carte **Caucasus** de DCS, dans un scénario moderne "
     "fictif. Ce document est le briefing complet. Positions en degrés et minutes décimales, et en cap / distance depuis "
     "le bullseye (cap vrai, nautiques).", "",
     "| Mission | Date | Bullseye (bleu et rouge) | Météo réelle | ATC |", "|---|---|---|---|---|",
     f"| `{Y['mission']['name']}` | {m['date']['Day']:02d}/{m['date']['Month']:02d}/{m['date']['Year']} | mont Elbrouz · {ll(BULLSEYE)} "
     "| UGTB (Tbilissi) | coupé sur tous les aérodromes |", "",
     "Tout se pilote par le menu radio F10 : zones de combat, missions et CAP, soutien (*ASSETS*), porte-avions (*CARRIER OPS*).", "",
     "**Sommaire** : [Carte](#carte) · [Situation](#situation) · [Bases](#bases) · [Défense aérienne permanente](#défense-aérienne-permanente) · "
     "[Soutien](#soutien) · [Entraînement](#entraînement) · [Zones de combat](#zones-de-combat) · [Missions scénarisées](#missions-scénarisées) · "
     "[QRA](#qra) · [CAP à la demande](#cap-à-la-demande) · [Combat entre joueurs](#combat-entre-joueurs) · [Plan radio](#plan-radio) · "
     "[Météo et heures](#météo-et-heures) · [Commandes utiles](#commandes-utiles) · "
     "[Pour les créateurs de mission](#pour-les-créateurs-de-mission)", "",
     "## Carte", "", "![Carte de la mission](docs/carte.jpg)", "",
     "Carrés : bases avec slots. Traits pleins : hippodromes des ravitailleurs et AWACS ; tirets fins : CAP à la "
     "demande. Cercles : QRA. Pastilles vertes : entraînement (H hélicoptères, A attaque, S SEAD, R recherche). "
     "Pastilles rouges : zones de combat, numérotées comme la liste plus bas. Grands tirets bleus : sanctuaire. "
     "L'arène est hors du cadre, à l'ouest (flèche). La même image est dans le briefing DCS, et la carte F10 porte "
     "les mêmes dessins, chaque camp ne voyant que les siens. Générée par `tools/gen_map.py`.", "",
     "Le panneau de briefing de DCS ajuste chaque image à sa taille : la carte du théâtre y sert de vue d'ensemble, "
     "et ce sont les zooms qui se lisent (flèches sous l'image). Ils sont repris ci-dessous dans les sections "
     "qu'ils illustrent : " + " · ".join(f"[{t.split(' : ')[0].split(' — ')[0]}]({f})" for f, t in ZOOM.values()) + ".", "",
     "## Situation", "",
     "La Géorgie, soutenue par l'OTAN, tient une ligne avancée en Russie — Sochi, Nalchik, Beslan — face aux forces russes. "
     "Le front court de la mer Noire (Sochi / Maykop) à l'Ossétie du Nord (Beslan / Mozdok), sur environ 207 nm. Le secteur "
     "Ouest, au large de la péninsule de Taman, accueille l'arène ; il reste hors QRA.", "",
     "## Bases", ""] + zooms("georgie_ouest", "abkhazie") + [
     "| Base | Camp | Slots | Position | Bullseye | UHF | VHF | FM | Défense permanente |",
     "|---|---|---|---|---|---|---|---|---|"]
for side in ("blue", "red"):
    for n, slots in sorted(bases[side], key=lambda t: (not t[1], t[0])):
        f = freq(f"Base-{n}") if slots else {}
        ad_tag = n.split("-")[0].split(" ")[0]  # même découpe que tools/gen_05_defense.py
        ad = ", ".join(AD.get(ad_tag, [])) if slots else ""
        o.append(f"| {n} | {'bleu' if side == 'blue' else 'rouge'} | {'oui' if slots else 'non'} | {ll(AIRFIELDS[n])} | {bullseye(AIRFIELDS[n])} "
                 f"| {f.get('uhf', '—')} | {f.get('vhf', '—')} | {f.get('fm', '—')} | {ad or '—'} |")
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
      "Jouez un seul niveau à la fois.", ""] + zooms("gori")
cz = MOD["COMBATZONE"]["combat_zones"]
for training, title in ((True, None), (False, "## Zones de combat")):
    if title:
        o += ["", title, "", "Menus F10 par type. Les défenses citées sont celles de la zone ; certaines sont tirées au hasard à "
              "chaque activation.", ""] + zooms("front_est", "kouban", "nord_stavropol", "mer_noire")
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
o += ["", "## Combat entre joueurs", ""] + zooms("arene") + [
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
      f"Construite de zéro le 28/09/2026 avec VEAF Mission Creation Tools (`veaf-tools`, {TOOLS_VERSION}) et le serveur MCP "
      "`veaf-mission-mcp`, à partir du prompt `new-open-training-mission.fr.md` de VMCT, en s'inspirant de la v5 "
      "(`VEAF-Open-Training-Mission-Caucasus`, dossier `backup_v5/`) sans la recopier. Trois ensembles en sont repris : "
      "l'arène « Air Quake », le groupe aéronaval du Stennis et la zone hélicoptère "
      "« Mountain Hike ».", "",
      "### Construire", "",
      "```powershell",
      "# récupérer les outils et les scripts VEAF (exécutables et published/, hors dépôt)",
      ".\\veaf-tools-updater.exe", "",
      "# contrôle avant build",
      ".\\veaf-tools.exe mission validate", "",
      f"# configuration serveur : sécurité active, logs info, {len(VER['versions'])} variantes météo dans missions/",
      ".\\veaf-tools.exe mission build", "",
      "# essais sur un poste : sécurité coupée, logs debug, noms de groupes lisibles, pas de variantes",
      ".\\veaf-tools.exe mission build --profile LOCAL_TEST",
      "```", "",
      "### Fichiers", "",
      "| Fichier | Rôle |", "|---|---|",
      "| `mission.yaml` | Identité, sécurité, profil `LOCAL_TEST`, modules, zones de combat (niveaux imbriqués par `includes:`), QRA, CAP, assets |",
      "| `ctld-config.yaml` | Points logistiques, troupes et cargos CTLD |",
      "| `src/mission/` | La mission DCS éclatée (groupes, zones de déclenchement, aérodromes, dessins de la carte F10) |",
      "| `src/presets.yaml` | Plan radio bleu et rouge |",
      "| `src/versions.yaml` | Variantes météo et heure |",
      "| `src/waypoints.yaml` | Points de navigation injectés dans les appareils joueurs |",
      "| `src/warehouses.yaml` | Bases qui offrent des slots, carburant et munitions illimités, appareils proposés sur le pont du porte-avions (`ships:`) |",
      "| `src/spawnables.yaml`, `src/spawn-groups.yaml` | Groupes tirables par les zones de combat et les QRA |",
      "| `src/dynamic-slot-templates.yaml` | Appareils proposés en slots dynamiques |",
      "| `src/scripts/*.lua` | Configuration des scripts VEAF embarqués (`veaf-config.lua`, CTLD, script de mission) |",
      "| `src/mission/l10n/DEFAULT/*.ogg` | Sons des balises de la zone de sauvetage (MH01 à MH03, SOS), déclarés dans `mapResource` |",
      "| `docs/carte.jpg`, `docs/cartes/` | La carte du théâtre et les huit zooms ; les mêmes images sont dans "
      "`src/mission/l10n/DEFAULT/` pour le briefing DCS, où `tools/gen_map.py` écrit lui-même `mapResource` et les "
      "listes `pictureFileName*` (côté bleu et neutre seulement : DCS affiche la liste rouge puis la bleue à un joueur "
      "dont il ignore le camp, et une image présente dans les deux s’afficherait deux fois) |",
      "| `tools/paths.py` | Où trouver le code Python de VMCT ; se règle par la variable d’environnement `VMCT_PY` |",
      "| `tools/` | Les générateurs qui ont construit la mission (`gen_*.py`), les lots rejouables (`tools/batches/`), les contrôles (`check_portees.py`, `verify.py`) et `retours-vmct.md` (ce que les outils n'ont pas su faire) |", "",
      "Hors dépôt (voir `.gitignore`) : les exécutables téléchargés (`veaf-tools`, `dcs-serve`, `dcs-client`), "
      "les scripts VEAF de `published/`, les `.miz` construits et `missions/`, les sauvegardes `.veaf-backups/`.", "",
      "### Régénérer ce document", "",
      "Ce README est **généré depuis la mission** : aucune valeur n'y est tapée à la main. Après tout "
      "changement dans `src/` ou `mission.yaml` :", "",
      "```powershell",
      "python tools\\gen_map.py     # la carte du théâtre, les zooms, et les images du briefing DCS",
      "python tools\\gen_readme.py  # ce fichier",
      "```", "",
      "### Limites connues", "",
      "Plusieurs éléments n'ont pas d'action MCP dédiée et ont été écrits par script directement dans la "
      "table de la mission : leurres et indicatifs des slots de l'arène, tâches ATC et slots de pont du porte-avions, "
      "entrepôt du navire, balises radio de la zone de sauvetage, balises de tirage (`#spawngroup`, `#spawncount`) des "
      "zones de combat. Ils se relisent dans `src/mission/mission` comme le reste. Le détail est dans "
      "`tools/retours-vmct.md`.", ""]
(ROOT / "README.md").write_text("\n".join(o), encoding="utf-8")
print("README.md :", len(o), "lignes")
