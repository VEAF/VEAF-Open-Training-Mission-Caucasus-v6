"""Lot 11 : arène JcJ AirQuake (v5) et sanctuaire bleu (v5).

Arène : loin à l'ouest, sur la mer (positions de la v5) ; slots en départ en vol, par type de missile,
bleus au sud (cap au nord), rouges au nord (cap au sud) ; un AWACS par camp. Liste des slots et emports
repris de l'arène de GermanyCW-v6.
Sanctuaire : polygone de 22 unités en activation différée (positions de la v5) protégeant l'arrière bleu.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from lib import BLUE, GCW, RED, Batch, off, pylons  # noqa: E402

b = Batch()
arena = sorted((g for g in GCW.values() if g["name"].startswith("Arène - ")), key=lambda g: (g["coalition"], g["name"]))
iy = {"blue": 0, "red": 0}
for g in arena:
    side = g["coalition"]
    i = iy[side]
    iy[side] += 1
    x = -116500 if side == "blue" else -6000
    y = -225000 - 2500 * i
    b.act("add_air_group", **(BLUE if side == "blue" else RED), name=g["name"], unit_type=g["units"][0]["type"],
          count=4, start="air", position={"x": x, "y": y}, altitude_ft=25000, speed_kt=420,
          heading_deg=0 if side == "blue" else 180, skill="Client", task="CAP",
          frequency_mhz=280.0 if side == "blue" else 281.0, pylons=pylons(g["name"]))
for name, typ, side, a, fl, f in [("Darkstar 1", "E-3A", BLUE, (-218277, -303225), 300, 280.0),
                                  ("AWACS Arène Rouge", "A-50", RED, (83880, -181919), 300, 281.0)]:
    bb = off(a, 90, 30 * 1852)
    b.act("add_air_group", **side, name=name, unit_type=typ, count=1, start="air", position={"x": a[0], "y": a[1]},
          altitude_ft=fl * 100, speed_kt=360, frequency_mhz=f, task="AWACS", skill="High")
    b.act("edit_route", group_name=name, operation="add", position={"x": bb[0], "y": bb[1]}, altitude_ft=fl * 100, speed_kt=360)
    for task, params in [("set_unlimited_fuel", {"value": True}), ("awacs", {}), ("eplrs", {"value": True}),
                         ("orbit", {"pattern": "Race-Track", "altitude_ft": fl * 100, "speed_kt": 360})]:
        b.act("edit_route", group_name=name, operation="add_task", index=1, task=task, task_params=params)

SANCT = [(-159436, 455547, "ship"), (-185871, 431769, "ship"), (-272309, 397430, "ship"), (-377828, 370703, "ship"),
         (-425874, 406991, "ship"), (-417210, 559062, "vehicle"), (-396147, 784591, "vehicle"), (-366268, 923124, "vehicle"),
         (-339406, 948476, "vehicle"), (-299009, 932116, "vehicle"), (-264103, 888195, "vehicle"), (-238748, 844699, "vehicle"),
         (-259665, 806300, "vehicle"), (-267447, 757293, "vehicle"), (-272074, 710180, "vehicle"), (-267237, 692512, "vehicle"),
         (-242628, 659280, "vehicle"), (-232009, 623870, "vehicle"), (-206250, 570189, "vehicle"), (-183637, 517491, "vehicle"),
         (-160058, 474790, "vehicle"), (-158077, 459163, "vehicle")]
for i, (x, y, cat) in enumerate(SANCT, 1):
    n = f"Sanctuaire bleu-{i:02d}"
    b.act("add_group", **BLUE, category=cat, name=n, position={"x": x, "y": y},
          units=[{"type": "speedboat" if cat == "ship" else "Predator TrojanSpirit", "name": n}],
          late_activation=True, keep_position=True)
b.save("11-arene-sanctuaire.json")
