"""Déclare src/mission/l10n/DEFAULT/carte.jpg comme image de briefing des trois camps (prompt §4.13).

Aucune action MCP ne le fait : charge la mission du dossier (lecteur de VMCT, sans exécuter de Lua),
ajoute la clé ResKey_ImageBriefing_carte à mapResource, la référence dans pictureFileNameB/R/N, et
réécrit via save_folder_mission (qui sauvegarde avant d'écrire). Idempotent. Même mécanisme que
GermanyCW-v6.
"""
import sys
from pathlib import Path

VMCT = Path("D:/dev/_VEAF/VMCT-develop")
sys.path.insert(0, str(VMCT / "src/python/veaf-tools"))
from veaf_mission_mcp.mission_folder import load_folder_mission, save_folder_mission  # noqa: E402

M = Path(__file__).resolve().parents[1]
KEY, FILE = "ResKey_ImageBriefing_carte", "carte.jpg"
assert (M / "src/mission/l10n/DEFAULT" / FILE).is_file(), "lancer tools/gen_map.py d'abord"
mis = load_folder_mission(M)
for side in ("B", "R", "N"):
    mis.mission_content[f"pictureFileName{side}"] = [KEY]
res = save_folder_mission(mis, M)
# save_folder_mission ne réécrit pas mapResource : on l'écrit comme add_sound (même sérialisation), en
# gardant l'ancien dans .veaf-backups/ et non à côté (voir tools/retours-vmct.md, n° 7)
import shutil  # noqa: E402
import time  # noqa: E402

import luadata  # noqa: E402

path = M / "src/mission/l10n/DEFAULT/mapResource"
resources = dict(mis.map_resource_content or {})
if resources.get(KEY) != FILE:
    bk = M / ".veaf-backups/l10n-DEFAULT"
    bk.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(path, bk / f"mapResource.{time.strftime('%Y%m%d-%H%M%S')}")
    resources[KEY] = FILE
    path.write_text("mapResource = \n" + luadata.serialize(resources, indent="  ", indent_level=0,
                                                            always_provide_keyname=True, sort=True),
                    encoding="utf-8", newline="\n")
print("image de briefing déclarée ;", res.get("backups"), "| mapResource :", sorted(resources))
