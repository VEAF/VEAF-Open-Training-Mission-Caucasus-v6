"""Lot 15 : dessins F10 (prompt §4.13), mêmes données que la carte du briefing (tools/gen_map.py).

Couche Common : ligne de front. Couche Blue : sanctuaire bleu, hippodromes bleus, cercles et
étiquettes des zones de combat et d'entraînement. Couche Red : hippodromes rouges. Les cercles de
QRA vont sur la couche du camp qui tient la QRA.

Lisibilité (retour de David en vol, 29/09/2026) : une étiquette sans `fill_color` prenait le fond
par défaut de l'action — `0x00000080`, noir à 50 % — sous un texte de couleur sombre, donc illisible
sur la carte F10. Le fond est maintenant blanc presque opaque, et le texte garde la couleur du camp.

Les zones n'avaient aucun contour (10 lignes et 28 étiquettes, pas un seul polygone) : chaque zone
de combat, zone d'entraînement et QRA porte désormais son cercle, au rayon réel de la zone.

Ce lot REMPLACE les dessins précédents : il les retire d'abord par leur nom, un dessin ne pouvant
pas être créé deux fois sous le même nom.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import gen_map as G  # noqa: E402  (données seulement : le rendu n'est lancé qu'en __main__)
from lib import Batch  # noqa: E402

b = Batch()
RED_C, BLUE_C, TKB_C, TKR_C, GREEN_C = "0xa4221aff", "0x1f5fbfff", "0x0b86a8ff", "0xc96a10ff", "0x2e7f38ff"
# fond des étiquettes : blanc à 90 %, pour que le texte sombre du camp se lise sur la carte F10
LABEL_BG = "0xffffffe6"
# remplissage des cercles : la couleur du camp, très transparente — le contour porte l'information
RED_FILL, BLUE_FILL, GREEN_FILL = "0xa4221a26", "0x1f5fbf26", "0x2e7f3826"
FONT = 14


def xy(p):
    return {"x": p[0], "y": p[1]}


def label(layer, name, position, text, color):
    b.act("add_map_drawing", layer=layer, shape="textbox", name=name, position=xy(position),
          text=text, color=color, fill_color=LABEL_BG, font_size=FONT)


def circle(layer, name, centre, radius_m, color, fill):
    b.act("add_map_drawing", layer=layer, shape="circle", name=name, position=xy(centre),
          radius=radius_m, color=color, fill_color=fill, thickness=4)


# ── retirer les dessins déjà présents ────────────────────────────────────────────────────────────
# Lus dans la mission, jamais déduits de la configuration : un dessin posé avant un renommage de
# zone porte l'ancien nom, et une suppression déduite échoue sur un nom qui n'existe pas — ce qui a
# interrompu ce lot à mi-chemin le 01/10/2026, laissant la carte à moitié effacée.
for _layer in (G.MIS.mission_content.get("drawings") or {}).get("layers") or []:
    for _d in _layer.get("objects") or []:
        b.act("edit_map_drawing", layer=_layer["name"], name=_d["name"], remove=True)

# ── front et sanctuaire ──────────────────────────────────────────────────────────────────────────
b.act("add_map_drawing", layer="Common", shape="line", name="Ligne de front (approx.)",
      points=[xy(p) for p in G.FRONT_PTS], color=RED_C, thickness=8)
poly = [(g["x"], g["y"]) for g in G.SANCTUARY]
b.act("add_map_drawing", layer="Blue", shape="line", name="Sanctuaire bleu", points=[xy(p) for p in poly],
      closed=True, color=BLUE_C, thickness=6)

# ── soutien : hippodrome et son étiquette ────────────────────────────────────────────────────────
for n in G.SUPPORT:
    side, _cat, g = G.GROUPS[n]
    a, c = ((p["x"], p["y"]) for p in g["route"]["points"][:2])
    layer, col = ("Red", TKR_C) if side == "red" else ("Blue", TKB_C)
    b.act("add_map_drawing", layer=layer, shape="line", name=f"Hippodrome {n}", points=[xy(a), xy(c)],
          color=col, thickness=8)
    label(layer, f"Étiquette {n}", c, n, col)

# ── QRA : le cercle au rayon réel, sur la couche du camp qui la tient ────────────────────────────
for q in G.Y["modules"]["QRA"]["definitions"]:
    z = G.ZONES[q["trigger_zone"]]
    red = q["coalition"] == "RED"
    layer, col, fill = ("Red", RED_C, RED_FILL) if red else ("Blue", BLUE_C, BLUE_FILL)
    circle(layer, f"QRA {q['name']}", (z["x"], z["y"]), z["radius"], col, fill)
    # au NORD du cercle : dans le repère DCS x est le nord et y l'est, et une étiquette posée à
    # l'est partait de 40 à 57 nm de côté, jusque sur une autre zone (relu le 01/10/2026)
    label(layer, f"Étiquette {q['name']}", (z["x"] + z["radius"], z["y"]), q["name"], col)

# ── zones : cercle + étiquette, entraînement en vert, combat en rouge numéroté ───────────────────
num = 0
for z in G.Y["modules"]["COMBATZONE"]["combat_zones"]:
    tz = G.ZONES[z["zone_name"]]
    c = (tz["x"], tz["y"])
    if z.get("training"):
        if z["zone_name"].endswith(("_Easy", "MountainHike")):
            circle("Blue", f"Entraînement {z['zone_name']}", c, tz["radius"], GREEN_C, GREEN_FILL)
            label("Blue", f"Étiquette entraînement {z['zone_name']}", c,
                  z["friendly_name"].split(" - ")[0] + " (entraînement)", GREEN_C)
        continue
    num += 1
    circle("Blue", f"Zone {num}", c, tz["radius"], RED_C, RED_FILL)
    label("Blue", f"Étiquette zone {num}", c, f"{num} - {z['friendly_name']}", RED_C)

b.save("15-dessins.json")
