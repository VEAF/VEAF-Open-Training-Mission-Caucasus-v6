"""Écrit le shape_name des statiques posées avant FIX-IN-GAME-TEST-FINDINGS 01 (#1023).

DCS refuse certaines statiques sans shape_name (mesuré sur GermanyCW-v6 : un .Command Center et trois
.Ammunition depot n'existaient pas). add_group l'écrit depuis #1023 ; les statiques posées avant ne
l'ont pas. Valeur prise dans les données de VMCT (veaf_libs.dcs_units_data.get_unit_shape_name), comme
l'action. Idempotent.
"""
from pathlib import Path

import paths  # noqa: F401  (met le code VMCT sur sys.path)
from veaf_libs.dcs_units_data import get_unit_shape_name  # noqa: E402
from veaf_mission_mcp.mission_folder import load_folder_mission, save_folder_mission  # noqa: E402

M = Path(__file__).resolve().parents[1]
mis = load_folder_mission(M)
fixed, unknown = 0, []
for side in mis.mission_content["coalition"].values():
    for c in side.get("country") or []:
        for g in (c.get("static") or {}).get("group") or []:
            for u in g["units"]:
                if u.get("shape_name"):
                    continue
                shape = get_unit_shape_name(u["type"])
                if shape:
                    u["shape_name"] = shape
                    fixed += 1
                else:
                    unknown.append(u["type"])
res = save_folder_mission(mis, M)
print(f"{fixed} shape_name écrits ; types sans shape_name connu : {sorted(set(unknown))} ; sauvegarde {res.get('backup')}")
