"""Lot 07 : balises radio du Mountain hike (v5) — sons embarqués, émission FM en boucle.

Les balises sont permanentes : leur nom ne commence pas par celui de la zone, qui ne les capture donc
pas (elles guident vers la zone avant qu'elle soit activée).
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from lib import BLUE, Batch  # noqa: E402

V5 = "D:/dev/_VEAF/VEAF-Open-Training-Mission-Caucasus/backup_v5/src/mission/l10n/DEFAULT"
b = Batch()
BEACONS = [  # nom, son, MHz FM, position (v5), sous-titre
    ("Balise MH01", "MH01.ogg", 31.0, (-191120, 605261), "MH01"),
    ("Balise MH02", "MH02.ogg", 32.0, (-185003, 622302), "MH02"),
    ("Balise MH03", "MH03.ogg", 33.0, (-178350, 630677), "MH03"),
    ("Balise SOS", "SOS.ogg", 34.0, (-167987, 629362), "SOS - équipage du Mi-8"),
]
for name, sound, mhz, pos, sub in BEACONS:
    b.act("add_sound", sound_path=f"{V5}/{sound}")
    b.act("add_group", **BLUE, category="vehicle", name=name, position={"x": pos[0], "y": pos[1]},
          units=[{"type": "Hummer", "name": name}], keep_position=True)
    b.act("edit_route", group_name=name, operation="add_task", index=1, task="set_frequency",
          task_params={"frequency_mhz": mhz, "modulation": "FM"})
    b.act("edit_route", group_name=name, operation="add_task", index=1, task="transmit_message",
          task_params={"sound": sound, "loop": True, "duration_s": 5, "subtitle": sub})
b.save("07-balises.json")
