"""Contrôle (prompt §4.5 et §8) : aucune défense permanente ne couvre une base adverse avec slots,
et chaque porteur #veafInterpreter est du type du lanceur de son alias.

Portées : table de menace DCS embarquée dans AIEN.lua (champ `threat`, en mètres), non mesurées en jeu.
Usage : python tools/check_portees.py   (lit src/mission/, mission.yaml et src/warehouses.yaml)
"""
import json, math, re, sys
from pathlib import Path
from paths import VMCT  # noqa: F401  (met le code VMCT sur sys.path)
from mission_tools.miz_tools import read_mission_folder  # noqa: E402
import yaml  # noqa: E402
M = Path(__file__).resolve().parents[1]
threat = {m.group(1): int(t.group(1)) for m in re.finditer(r'\["([^"]+)"\] = \{([^}]*)\}', (VMCT / "src/scripts/community/AIEN.lua").read_text(encoding="utf-8"))
          for t in [re.search(r'\["threat"\] = (\d+)', m.group(2))] if t}
LAUNCHER = {"-patriot": "Patriot ln", "-hawk": "Hawk ln", "-nasams": "NASAMS_LN_C", "-avenger_squad": "M1097 Avenger",
            "-sa10": "S-300PS 5P85C ln", "-sa11": "SA-11 Buk LN 9A310M1", "-sa15": "Tor 9A331", "-sa19": "2S6 Tunguska",
            "-sa6": "Kub 2P25 ln", "-sa8": "Osa 9A33 ln", "-shilka": "ZSU-23-4 Shilka", "-sa2": "S_75M_Volhov"}
af = json.loads((M / "tools/airfields.json").read_text(encoding="utf-8").split(": ", 1)[1])["airfields"]
P = {a["name"]: (a["x"], a["y"]) for a in af}
wh = yaml.safe_load((M / "src/warehouses.yaml").read_text(encoding="utf-8"))
mis = read_mission_folder(M).mission_content
slots = {"blue": [], "red": []}
wa = read_mission_folder(M).warehouses_content["airports"]
names = {v: k for k, v in yaml.safe_load((VMCT / "src/python/veaf-tools/veaf_libs/data/airdromes.yaml").read_text(encoding="utf-8"))["theatres"]["Caucasus"].items()}
for aid, w in wa.items():
    side = (w.get("coalition") or "").lower()
    n = names.get(int(aid))
    if side in slots and n not in (wh.get(side, {}) or {}).get("exclude_airports", []):
        slots[side].append(n)
bad = 0
seen = 0
for side, co in mis["coalition"].items():
    for c in co.get("country") or []:
        for g in (c.get("vehicle") or {}).get("group") or []:
            for u in g["units"]:
                m = re.search(r'#veafInterpreter\["(-[\w]+)', u.get("name", ""))
                if not m:
                    continue
                alias = m.group(1); seen += 1
                want = LAUNCHER.get(alias)
                if want and u["type"] != want:
                    print(f"PORTEUR  {g['name']}: {u['type']} pour {alias} (attendu {want})"); bad += 1
                rng = threat.get(want or u["type"], 0) / 1852
                enemy = "red" if side == "blue" else "blue"
                for base in slots.get(enemy, []):
                    d = math.hypot(u["x"] - P[base][0], u["y"] - P[base][1]) / 1852
                    if d <= rng:
                        print(f"PORTÉE   {g['name']} ({alias}, {rng:.0f} nm) couvre {base} à {d:.0f} nm"); bad += 1
print("porteurs vus:", seen); print("slots bleus:", len(slots["blue"]), "rouges:", len(slots["red"]))
print("OK" if not bad else f"{bad} défaut(s)")

# ── §4.7 : SAM des zones de combat (#command) contre bases bleues, pistes de ravitailleurs, zones d'entraînement
sys.path.insert(0, str(M / "tools"))
from lib import TANKERS  # noqa: E402
cz = yaml.safe_load((M / "mission.yaml").read_text(encoding="utf-8"))["modules"]["COMBATZONE"]["combat_zones"]
tz = {z["zone_name"] for z in cz if z.get("training")}
zpos = {z["name"]: (z["x"], z["y"], z.get("radius", 0)) for z in mis["triggers"]["zones"]}
blue_bases = [n for n, w in ((names.get(int(a)), w) for a, w in wa.items()) if (w.get("coalition") or "").lower() == "blue"]
targets = [(f"base {n}", P[n], 0) for n in blue_bases] + [(f"piste {n}", c, 0) for n, (c, *_r) in TANKERS.items()]
targets += [(f"zone {n}", zpos[n][:2], zpos[n][2]) for n in tz]
bad2 = seen2 = 0
for c in mis["coalition"]["red"].get("country") or []:
    for g in (c.get("vehicle") or {}).get("group") or []:
        zn = next((z for z in zpos if g["name"].lower().startswith(z.lower())), None)
        if not zn:
            continue
        for u in g["units"]:
            m = re.search(r'#command="(-[\w]+)', u.get("name", ""))
            if not m:
                continue
            seen2 += 1
            rng = threat.get(LAUNCHER.get(m.group(1), u["type"]), 0) / 1852
            for label, p, r in targets:
                if label == f"zone {zn}" or (zn in tz and label.startswith("zone ") and label[5:].split("_")[1] == zn.split("_")[1]):
                    continue  # une zone d'entraînement et ses niveaux voisins partagent le même cercle
                d = max(0, math.hypot(u["x"] - p[0], u["y"] - p[1]) - r) / 1852
                if d <= rng:
                    print(f"§4.7     {g['name']} ({m.group(1)}, {rng:.1f} nm) atteint {label} à {d:.1f} nm"); bad2 += 1
print("porteurs de zone vus:", seen2, "|", "OK §4.7" if not bad2 else f"{bad2} défaut(s) §4.7")
