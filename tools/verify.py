"""Contrôles de la section 8 du prompt sur les .miz construits (lus avec le lecteur de VMCT, jamais par
recherche de texte). Adapté de l'outil de GermanyCW-v6.

Usage : python tools/verify.py <base serveur .miz> <base LOCAL_TEST .miz> [variantes .miz ...]
"""
import collections
import json
import sys
import zipfile
from pathlib import Path

VMCT = Path("D:/dev/_VEAF/VMCT-develop")
sys.path.insert(0, str(VMCT / "src/python/veaf-tools"))
from mission_tools.miz_tools import read_miz  # noqa: E402
import yaml  # noqa: E402

M = Path(__file__).resolve().parents[1]
SUPPORT = ["Arco 1", "Texaco 1", "Shell 1", "Shell 2", "Magic 1", "Overlord 1", "Tanker Rouge", "AWACS Rouge",
           "Darkstar 1", "AWACS Arène Rouge", "Reaper 1", "Reaper 2", "CVN-74 Stennis S3B-Tanker"]
names = {v: k for k, v in yaml.safe_load((VMCT / "src/python/veaf-tools/veaf_libs/data/airdromes.yaml").read_text(encoding="utf-8"))["theatres"]["Caucasus"].items()}


def seq(v):
    return list(v.values()) if isinstance(v, dict) else list(v or [])


def groups(m):
    for side, co in m["coalition"].items():
        for c in seq(co.get("country")):
            for cat in ("plane", "helicopter", "vehicle", "ship", "static"):
                for g in seq((c.get(cat) or {}).get("group")):
                    yield side, c.get("name"), cat, g


def task_ids(point):
    out = []
    for t in seq(((point.get("task") or {}).get("params") or {}).get("tasks")):
        out.append(t["id"] if t["id"] != "WrappedAction" else t["params"]["action"]["id"])
    return out


def check(path, label):
    print(f"\n===== {label} : {Path(path).name}")
    miz = read_miz(Path(path))
    m = miz.mission_content
    gnames, unames, gid, uid = (collections.Counter() for _ in range(4))
    counts = collections.Counter()
    problems = []
    for side, _country, cat, g in groups(m):
        gnames[g["name"]] += 1
        gid[g["groupId"]] += 1
        counts[(side, cat)] += 1
        for u in seq(g["units"]):
            unames[u["name"]] += 1
            uid[u["unitId"]] += 1
            if cat in ("plane", "helicopter") and not g.get("dynSpawnTemplate") and not g["name"].startswith("veafSpawn-"):
                pt0 = seq(g["route"]["points"])[0]
                on_deck_or_ground = "TakeOff" in (pt0.get("type") or "")
                if (u.get("alt") or 0) <= 0 and not on_deck_or_ground:
                    problems.append(f"alt<=0 {g['name']}")
                if not (u.get("payload") or {}).get("fuel"):
                    problems.append(f"sans carburant {g['name']}")
            if cat == "static" and not u.get("category"):
                problems.append(f"statique sans category {g['name']} {u['type']}")
        if g["name"] in SUPPORT:
            print(f"  soutien {g['name']:28s} {task_ids(seq(g['route']['points'])[0])}")
        if "convoi" in g["name"].lower():
            print(f"  convoi  {g['name']:40s} {[p.get('action') for p in seq(g['route']['points'])]} {len(seq(g['units']))} unités")
    dup = lambda c: [k for k, v in c.items() if v > 1]  # noqa: E731
    print(f"  groupes {sum(gnames.values())} | unités {sum(unames.values())} | noms de groupes en double {dup(gnames)[:5]} "
          f"| noms d'unités en double {dup(unames)[:5]} | groupId en double {len(dup(gid))} | unitId en double {len(dup(uid))}")
    print("  par camp / catégorie :", dict(sorted(counts.items())))
    print("  défauts de structure :", len(problems), problems[:8])
    dyn = sorted((names.get(int(k), k), a.get("coalition")) for k, a in (miz.warehouses_content.get("airports") or {}).items()
                 if isinstance(a, dict) and a.get("dynamicSpawn"))
    print("  slots dynamiques sur :", len(dyn), dyn)
    ships = [(k, a.get("coalition"), a.get("dynamicSpawn"), len(a.get("aircrafts") or {})) for k, a in (miz.warehouses_content.get("warehouses") or {}).items()
             if isinstance(a, dict) and a.get("dynamicSpawn")]
    print("  navires / FARP avec slots :", len(ships))
    print("  requiredModules :", m.get("requiredModules"))
    w = m["weather"]
    st = m.get("start_time", 0)
    print(f"  météo : clouds.preset {w.get('clouds', {}).get('preset')} | season.temperature {w.get('season', {}).get('temperature')} "
          f"| wind.atGround {w.get('wind', {}).get('atGround')} | départ {st // 3600:02d}:{st % 3600 // 60:02d} | date {m.get('date')}")
    for s in ("blue", "red"):
        print(f"  bullseye {s} :", m["coalition"][s].get("bullseye"))
    with zipfile.ZipFile(path) as z:
        cfg = [n for n in z.namelist() if n.endswith("veaf-config.lua")]
        txt = z.read(cfg[0]).decode("utf-8") if cfg else ""
        stray = [n for n in z.namelist() if "dictionary." in n or "mapResource." in n]
    grab = lambda k: [ln.strip() for ln in txt.splitlines() if k in ln][:1]  # noqa: E731
    print(f"  veaf-config.lua : SecurityDisabled {grab('SecurityDisabled')} | ForcedLogLevel {grab('ForcedLogLevel')} "
          f"| Diagnostics {grab('Diagnostics')} | AddZone {txt.count('veafCombatZone.AddZone')} | VeafQRA:new {txt.count('VeafQRA:new')} "
          f"| addCapMission {txt.count('addCapMission(')} | sanctuaires {txt.count('VeafSanctuaryZone:new')} | fichiers parasites {stray}")
    assets = yaml.safe_load((M / "mission.yaml").read_text(encoding="utf-8"))["modules"]["ASSETS"]["assets"]
    missing = [a["name"] for a in assets if a["name"] not in gnames] + [a["linked"] for a in assets if a.get("linked") and a["linked"] not in gnames]
    print("  assets sans groupe :", missing)
    return m


if __name__ == "__main__":
    check(sys.argv[1], "BASE serveur")
    check(sys.argv[2], "BASE LOCAL_TEST")
    for p in sys.argv[3:]:
        check(p, "variante")
