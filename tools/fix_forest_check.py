"""Sort des forêts les groupes des champs de tir que `veaf-tools dcs forest-check` y trouve (16/11/2026).

forest-check lit les forêts dans les fichiers de la carte ; sur Syria il dit ce que dessine la carte (vérifié par
David dans l'éditeur, 16/11/2026).
Chaque groupe est décalé du plus petit vecteur qui met ses unités au dégagé : centre hors forêt, 8 points à 100 m
hors forêt et hors de l'eau, au plus 1 sur 8 à 200 m en forêt.
Une seule fois : il refuse de repasser.
"""

import sys

from paths import ROOT  # noqa: F401  (met aussi le code VMCT sur sys.path)
from veaf_mission_mcp.actions import register_default_actions  # noqa: E402
from veaf_mission_mcp.catalog import ActionCatalog  # noqa: E402
from veaf_mission_mcp.mission_folder import load_folder_mission  # noqa: E402

sys.stdout.reconfigure(encoding="utf-8")
M = ROOT.as_posix()
cat = ActionCatalog()
register_default_actions(cat)

#: groupe -> (décalage nord, décalage est), en mètres
MOVES = {
    "combatZone_Akhalkalaki_Medium-aaa-1": (-190, -163),
    "combatZone_Gori_Hard-ewr": (300, 0),
    "combatZone_Kobuleti_Medium-sr-2": (-150, 0),
}
GUARD = ("combatZone_Gori_Hard-ewr", (-283000, 830000))


def as_list(t):
    return [t[k] for k in sorted(t)] if isinstance(t, dict) else (t or [])


content = load_folder_mission(ROOT).mission_content
groups = {
    g["name"]: g
    for co in content["coalition"].values()
    for c in as_list(co.get("country"))
    for g in as_list((c.get("vehicle") or {}).get("group"))
}
unit = as_list(groups[GUARD[0]]["units"])[0]
if (round(unit["x"]), round(unit["y"])) != GUARD[1]:
    sys.exit("déjà fait, ou les groupes ne sont plus à la place que ce script attend")

for name, (dx, dz) in MOVES.items():
    g = groups[name]
    res = cat.run_action(
        "set_group_properties", {"mission_path": M, "group_name": name, "move_to": {"x": g["x"] + dx, "y": g["y"] + dz}}
    )
    warn = res.get("warnings") if isinstance(res, dict) else None
    print(f"{name}: +{dx} N, +{dz} E" + (f" — {warn}" if warn else ""))
