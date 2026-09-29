"""Transporte depuis la v5 les groupes aériens des missions scénarisées (routes, tâches, emports éprouvés).

Aucune action MCP ne copie un groupe d'une mission à une autre : ce script charge les deux tables Lua
(lecteur de VMCT, sans exécuter de Lua), copie les groupes, renumérote groupId / unitId au-dessus du
maximum de la mission, rend les noms d'unités uniques, et réécrit la mission du dossier via
save_folder_mission (qui sauvegarde avant d'écrire). Idempotent : un groupe déjà présent est sauté.
"""
import copy
import re
from pathlib import Path

import paths  # noqa: F401  (met le code VMCT sur sys.path)
from mission_tools.miz_tools import read_mission_folder  # noqa: E402
from veaf_mission_mcp.mission_folder import load_folder_mission, save_folder_mission  # noqa: E402

M = Path(__file__).resolve().parents[1]
V5 = Path("D:/dev/_VEAF/VEAF-Open-Training-Mission-Caucasus/backup_v5")
WANT = re.compile(r"^(Red Attack On Gudauta|Red Tu-160 Bomber|OnDemand-Intercept-Transport)")

src = read_mission_folder(V5).mission_content
dst_m = load_folder_mission(M)
dst = dst_m.mission_content


def all_groups(mis):
    for side in mis["coalition"].values():
        for c in side.get("country") or []:
            for cat in ("plane", "helicopter", "vehicle", "ship", "static"):
                for g in (c.get(cat) or {}).get("group") or []:
                    yield g


gmax = max(g["groupId"] for g in all_groups(dst))
umax = max(u["unitId"] for g in all_groups(dst) for u in g["units"])
unames = {u["name"] for g in all_groups(dst) for u in g["units"]}
gnames = {g["name"] for g in all_groups(dst)}
red_russia = next(c for c in dst["coalition"]["red"]["country"] if c["name"] == "Russia")
planes = red_russia.setdefault("plane", {}).setdefault("group", [])
copied = 0
for c in src["coalition"]["red"]["country"]:
    for g in (c.get("plane") or {}).get("group") or []:
        if not WANT.match(g["name"]) or g["name"] in gnames:
            continue
        g = copy.deepcopy(g)
        gmax += 1
        g["groupId"] = gmax
        for i, u in enumerate(g["units"], 1):
            umax += 1
            u["unitId"] = umax
            if u["name"] in unames:
                u["name"] = f"{g['name']}-{i}"
            unames.add(u["name"])
        planes.append(g)
        copied += 1
res = save_folder_mission(dst_m, M)
print(f"{copied} groupes copiés ; sauvegarde : {res.get('backup')}")
