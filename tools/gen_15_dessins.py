"""Lot 15 : dessins F10 (prompt §4.13), mêmes données que la carte du briefing (tools/gen_map.py).

Couche Common : ligne de front. Couche Blue : sanctuaire bleu, hippodromes bleus, étiquettes des zones
(numéros du briefing). Couche Red : hippodromes rouges.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import gen_map as G  # noqa: E402  (données seulement : le rendu n'est lancé qu'en __main__)
from lib import Batch  # noqa: E402

b = Batch()
RED_C, BLUE_C, TKB_C, TKR_C, GREEN_C = "0xa4221aff", "0x1f5fbfff", "0x0b86a8ff", "0xc96a10ff", "0x2e7f38ff"


def xy(p):
    return {"x": p[0], "y": p[1]}


b.act("add_map_drawing", layer="Common", shape="line", name="Ligne de front (approx.)",
      points=[xy(p) for p in G.FRONT_PTS], color=RED_C, thickness=8)
poly = [(G.GROUPS[f"Sanctuaire bleu-{i:02d}"][2]["x"], G.GROUPS[f"Sanctuaire bleu-{i:02d}"][2]["y"]) for i in range(1, 23)]
b.act("add_map_drawing", layer="Blue", shape="line", name="Sanctuaire bleu", points=[xy(p) for p in poly], closed=True,
      color=BLUE_C, thickness=6)
for n in G.SUPPORT:
    side, _cat, g = G.GROUPS[n]
    a, c = ((p["x"], p["y"]) for p in g["route"]["points"][:2])
    layer, col = ("Red", TKR_C) if side == "red" else ("Blue", TKB_C)
    b.act("add_map_drawing", layer=layer, shape="line", name=f"Hippodrome {n}", points=[xy(a), xy(c)], color=col, thickness=8)
    b.act("add_map_drawing", layer=layer, shape="textbox", name=f"Étiquette {n}", position=xy(c), text=n, color=col, font_size=12)
num = 0
for z in G.Y["modules"]["COMBATZONE"]["combat_zones"]:
    tz = G.ZONES[z["zone_name"]]
    if z.get("training"):
        if z["zone_name"].endswith(("_Easy", "MountainHike")):
            b.act("add_map_drawing", layer="Blue", shape="textbox", name=f"Entraînement {z['zone_name']}",
                  position=xy((tz["x"], tz["y"])), text=z["friendly_name"].split(" - ")[0] + " (entraînement)",
                  color=GREEN_C, font_size=12)
        continue
    num += 1
    b.act("add_map_drawing", layer="Blue", shape="textbox", name=f"Zone {num}", position=xy((tz["x"], tz["y"])),
          text=f"{num} - {z['friendly_name']}", color=RED_C, font_size=12)
b.save("15-dessins.json")
