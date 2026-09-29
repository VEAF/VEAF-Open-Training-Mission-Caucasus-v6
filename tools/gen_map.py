"""Carte du briefing (prompt §4.13) : docs/carte.jpg + image de briefing DCS, sur fond OpenStreetMap.

Tout vient des données de la mission (src/mission/, mission.yaml, tools/lib.py) : bases avec slots,
FARP, hippodromes de soutien, CAP, cercles de QRA, zones numérotées comme dans le README, zones
d'entraînement, sanctuaire, front approximatif, porte-avions, bullseye. Tuiles OSM en cache dans
.veaf-backups/tiles/ ; User-Agent sans aucune donnée personnelle (politique d'usage OSM).
Adapté de gen_map.py de GermanyCW-v6.
Usage : python tools/gen_map.py   (écrit docs/carte.jpg et src/mission/l10n/DEFAULT/carte.jpg)
"""
import math
import sys
from pathlib import Path

import requests
from PIL import Image, ImageDraw, ImageFont

VMCT = Path("D:/dev/_VEAF/VMCT-develop")
sys.path.insert(0, str(VMCT / "src/python/veaf-tools"))
sys.path.insert(0, str(Path(__file__).parent))
import yaml  # noqa: E402
from mission_tools.miz_tools import read_mission_folder  # noqa: E402
from veaf_libs.coordinates import xy_to_latlon  # noqa: E402

from lib import AIRFIELDS, BULLSEYE, ROOT  # noqa: E402

ZOOM, TILE = 9, 256
TILE_URL = "https://tile.openstreetmap.org/{z}/{x}/{y}.png"
UA = {"User-Agent": "veaf-briefing-map/1.0 (+https://github.com/VEAF/VEAF-Mission-Creation-Tools)"}
LAT_N, LAT_S, LON_W, LON_E = 46.1, 40.9, 35.8, 46.2  # tout objet dessiné tombe dans ce cadre, sauf l'arène
OUT_W = 2000
FONT, FONTB, FONTI = (r"C:\Windows\Fonts\segoeui.ttf", r"C:\Windows\Fonts\segoeuib.ttf", r"C:\Windows\Fonts\segoeuii.ttf")
BLUE, RED, TKB, TKR, GREEN, INK, FRONT, HALO = "#1f5fbf", "#c2362b", "#0b86a8", "#c96a10", "#2e7f38", "#1b2629", "#a4221a", "#ffffff"


def ll(x, y):
    r = xy_to_latlon("Caucasus", x, y)
    return (r[0], r[1]) if isinstance(r, (tuple, list)) else (r["lat"], r["lon"])


def merc(lat, lon):
    n = 2 ** ZOOM
    return (lon + 180) / 360 * n, (1 - math.log(math.tan(math.radians(lat)) + 1 / math.cos(math.radians(lat))) / math.pi) / 2 * n


X0, Y0 = merc(LAT_N, LON_W)
X1, Y1 = merc(LAT_S, LON_E)
SCALE = OUT_W / ((X1 - X0) * TILE)
OUT_H = round((Y1 - Y0) * TILE * SCALE)


def px(x, y):
    xt, yt = merc(*ll(x, y))
    return ((xt - X0) * TILE * SCALE, (yt - Y0) * TILE * SCALE)


def px_per_m(x, y):
    lat, _ = ll(x, y)
    return SCALE / (156543.03 * math.cos(math.radians(lat)) / (2 ** ZOOM))


def basemap():
    cache = ROOT / ".veaf-backups/tiles"
    cache.mkdir(parents=True, exist_ok=True)
    tx0, ty0, tx1, ty1 = int(X0), int(Y0), int(X1), int(Y1)
    sheet = Image.new("RGB", ((tx1 - tx0 + 1) * TILE, (ty1 - ty0 + 1) * TILE), "#f4f6f2")
    sess = requests.Session()
    for i, tx in enumerate(range(tx0, tx1 + 1)):
        for j, ty in enumerate(range(ty0, ty1 + 1)):
            f = cache / f"{ZOOM}_{tx}_{ty}.png"
            if not f.exists():
                r = sess.get(TILE_URL.format(z=ZOOM, x=tx, y=ty), headers=UA, timeout=30)
                r.raise_for_status()
                f.write_bytes(r.content)
            sheet.paste(Image.open(f).convert("RGB"), (i * TILE, j * TILE))
    box = (round((X0 - tx0) * TILE), round((Y0 - ty0) * TILE), round((X1 - tx0) * TILE), round((Y1 - ty0) * TILE))
    return sheet.crop(box).resize((OUT_W, OUT_H), Image.LANCZOS)


def font(size, bold=False, italic=False):
    return ImageFont.truetype(FONTB if bold else FONTI if italic else FONT, size)


def dashed(d, a, b, fill, width, dash=(14, 8)):
    (ax, ay), (bx, by) = a, b
    length = math.hypot(bx - ax, by - ay)
    if not length:
        return
    ux, uy, t, on = (bx - ax) / length, (by - ay) / length, 0.0, True
    while t < length:
        t2 = min(t + (dash[0] if on else dash[1]), length)
        if on:
            d.line([(ax + ux * t, ay + uy * t), (ax + ux * t2, ay + uy * t2)], fill=fill, width=width)
        t, on = t2, not on


def label(d, xy, text, fill, size=17, bold=True, anchor="la", italic=False, halo=3):
    d.text(xy, text, font=font(size, bold, italic), fill=fill, anchor=anchor, stroke_width=halo, stroke_fill=HALO)


def disc(d, c, r, fill, outline, w=3):
    d.ellipse([c[0] - r, c[1] - r, c[0] + r, c[1] + r], fill=fill, outline=outline, width=w)


PLACED = []  # centres des repères déjà posés, pour écarter ceux qui se chevauchent


def place(c, r=16):
    """Position libre la plus proche de c (spirale), pour un repère de rayon r."""
    for k in range(0, 60):
        ang, dist = k * 0.9, 0 if k == 0 else 2 * r + 4 * (k // 7)
        p = (c[0] + dist * math.cos(ang), c[1] + dist * math.sin(ang))
        if all(math.hypot(p[0] - q[0], p[1] - q[1]) >= 2 * r + 2 for q in PLACED):
            PLACED.append(p)
            return p
    PLACED.append(c)
    return c


# ── données ──────────────────────────────────────────────────────────────────────────────────────
Y = yaml.safe_load((ROOT / "mission.yaml").read_text(encoding="utf-8"))
MIS = read_mission_folder(ROOT)
m = MIS.mission_content
ZONES = {z["name"]: z for z in m["triggers"]["zones"]}
GROUPS = {}
for side, co in m["coalition"].items():
    for c in co.get("country") or []:
        for cat in ("plane", "helicopter", "vehicle", "ship", "static"):
            for g in (c.get(cat) or {}).get("group") or []:
                GROUPS[g["name"]] = (side, cat, g)
excl = {s: set((yaml.safe_load((ROOT / "src/warehouses.yaml").read_text(encoding="utf-8")).get(s) or {}).get("exclude_airports") or [])
        for s in ("blue", "red")}
ids = {v: k for k, v in yaml.safe_load((VMCT / "src/python/veaf-tools/veaf_libs/data/airdromes.yaml").read_text(encoding="utf-8"))["theatres"]["Caucasus"].items()}
BASES = []
for aid, w in MIS.warehouses_content["airports"].items():
    side, n = (w.get("coalition") or "").lower(), ids.get(int(aid))
    if side in ("blue", "red") and n not in excl[side]:
        BASES.append((side, n.replace("-Adler", "").replace("-Pashkovsky", "").replace("-Lochini", "").replace("-Khanskaya", ""), AIRFIELDS[n]))
SUPPORT = ["Arco 1", "Texaco 1", "Shell 1", "Shell 2", "Magic 1", "Overlord 1", "Tanker Rouge", "AWACS Rouge"]
FRONT_PTS = [((AIRFIELDS[a][0] + AIRFIELDS[b][0]) / 2, (AIRFIELDS[a][1] + AIRFIELDS[b][1]) / 2)
             for a, b in (("Sochi-Adler", "Maykop-Khanskaya"), ("Gudauta", "Maykop-Khanskaya"), ("Nalchik", "Mineralnye Vody"), ("Beslan", "Mozdok"))]
FRONT_PTS = [(-116680, 408929)] + FRONT_PTS[:1] + FRONT_PTS[2:] + [(-140000, 900000)]  # de la côte à l'est de Beslan
LETTERS = {"Kobuleti": "H", "Akhalkalaki": "A", "Taman": "S", "MountainHike": "R"}


def render():
    img = basemap().convert("RGBA")
    img = Image.alpha_composite(img, Image.new("RGBA", img.size, (255, 255, 255, 95)))
    area = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ad = ImageDraw.Draw(area)
    qras = Y["modules"]["QRA"]["definitions"]
    for q in qras:
        z = ZONES[q["trigger_zone"]]
        col = (194, 54, 43) if q["coalition"] == "RED" else (31, 95, 191)
        c, r = px(z["x"], z["y"]), z["radius"] * px_per_m(z["x"], z["y"])
        ad.ellipse([c[0] - r, c[1] - r, c[0] + r, c[1] + r], fill=col + (34,), outline=col + (230,), width=3)
    img = Image.alpha_composite(img, area)
    d = ImageDraw.Draw(img)
    for q in qras:
        z = ZONES[q["trigger_zone"]]
        c, r = px(z["x"], z["y"]), z["radius"] * px_per_m(z["x"], z["y"])
        col = RED if q["coalition"] == "RED" else BLUE
        if c[1] - r < 90:  # le haut du cercle touche le bandeau du titre : étiquette sous le cercle
            label(d, (c[0], c[1] + r + 6), q["name"], col, 18, anchor="mt")
        else:
            label(d, (c[0], c[1] - r - 6), q["name"], col, 18, anchor="ms")

    # sanctuaire bleu (polygone de ses unités, dans l'ordre)
    poly = [px(GROUPS[f"Sanctuaire bleu-{i:02d}"][2]["x"], GROUPS[f"Sanctuaire bleu-{i:02d}"][2]["y"]) for i in range(1, 23)]
    for a, b in zip(poly, poly[1:] + poly[:1]):
        dashed(d, a, b, BLUE, 6, (18, 10))
    label(d, px(-392000, 520000), "SANCTUAIRE BLEU", BLUE, 20, anchor="mm")

    front = [px(*p) for p in FRONT_PTS]
    for a, b in zip(front, front[1:]):
        dashed(d, a, b, FRONT, 6, (22, 12))
    mid = ((front[1][0] + front[2][0]) / 2, (front[1][1] + front[2][1]) / 2)
    label(d, (mid[0], mid[1] - 14), "ligne de front (approx.)", FRONT, 18, bold=False, italic=True, anchor="ms")

    for cp in Y.get("cap_missions") or []:
        side, _cat, g = GROUPS[f"OnDemand-{cp['group_name']}"]
        pts = g["route"]["points"]
        dashed(d, px(pts[0]["x"], pts[0]["y"]), px(pts[1]["x"], pts[1]["y"]), RED if side == "red" else BLUE, 4, (10, 8))
    for n in SUPPORT:
        side, _cat, g = GROUPS[n]
        a, b = (px(p["x"], p["y"]) for p in g["route"]["points"][:2])
        col = TKR if side == "red" else TKB
        d.line([a, b], fill=col, width=9)
        label(d, (b[0] + 10, b[1]), n, col, 17, anchor="lm")

    ABOVE = {"Tbilisi"}  # étiquette au-dessus du carré : à droite, elle chevauche Vaziani ; à gauche, Shell 2
    for side, n, (x, y) in BASES:
        c = px(x, y)
        col = RED if side == "red" else BLUE
        d.rectangle([c[0] - 8, c[1] - 8, c[0] + 8, c[1] + 8], fill=col, outline=HALO, width=2)
        w = d.textlength(n, font=font(18, True))
        if n in ABOVE:
            label(d, (c[0], c[1] - 12), n, col, 18, anchor="ms")
            xs = [c[0] - w / 2 + k for k in range(0, int(w), 14)]
        else:
            label(d, (c[0] + 13, c[1] - 2), n, col, 18, anchor="lm")
            xs = [c[0] + 13 + k for k in range(0, int(w), 14)]
        PLACED.extend([c] + [(xx, c[1]) for xx in xs])  # obstacles pour les numéros de zone

    # zones : entraînement (lettre, niveau facile seulement) et combat (numéro du README)
    num = 0
    for z in Y["modules"]["COMBATZONE"]["combat_zones"]:
        tz = ZONES[z["zone_name"]]
        key = z["zone_name"].split("_")[1]
        if z.get("training"):
            if z["zone_name"].endswith(("_Easy", "MountainHike")):
                c = place(px(tz["x"], tz["y"]))
                disc(d, c, 15, HALO, GREEN, 4)
                label(d, c, LETTERS[key], GREEN, 17, anchor="mm", halo=0)
            continue
        num += 1
        true_c = px(tz["x"], tz["y"])
        c = place(true_c)
        if math.hypot(c[0] - true_c[0], c[1] - true_c[1]) > 3:
            d.line([true_c, c], fill=RED, width=2)
            disc(d, true_c, 3, RED, RED, 1)
        disc(d, c, 15, RED, HALO, 3)
        label(d, c, str(num), HALO, 15, anchor="mm", halo=0)

    for name, (side, cat, g) in GROUPS.items():
        if cat == "static" and name.startswith("FARP ") and "munitions" not in name:
            c = px(g["x"], g["y"])
            d.polygon([(c[0], c[1] - 10), (c[0] + 10, c[1] + 7), (c[0] - 10, c[1] + 7)], fill=GREEN, outline=HALO)
    for name, lbl in (("CSG-74 Stennis", "Stennis"), ("CSG-01 Tarawa", "Tarawa")):
        g = GROUPS[name][2]
        c = px(g["x"], g["y"])
        d.polygon([(c[0] - 16, c[1] - 5), (c[0] + 16, c[1] - 5), (c[0] + 10, c[1] + 7), (c[0] - 10, c[1] + 7)], fill=BLUE, outline=HALO)
        label(d, (c[0], c[1] + 12), lbl, BLUE, 16, anchor="mt")

    # arène AirQuake, à l'ouest hors du cadre : flèche sur le bord gauche, à sa latitude
    ax, ay = px(-116500, -230000)
    ay = min(max(ay, 40), OUT_H - 40)
    d.polygon([(8, ay), (34, ay - 14), (34, ay + 14)], fill=INK)
    label(d, (42, ay), "Arène AirQuake (ouest, sur la mer)", INK, 17, anchor="lm")

    bu = px(*BULLSEYE)
    disc(d, bu, 11, None, INK, 3)
    disc(d, bu, 3.5, INK, INK, 1)
    label(d, (bu[0] + 15, bu[1] - 12), "BULLSEYE (Elbrouz)", INK, 17, anchor="ls")

    label(d, (24, 22), "VEAF Open Training — Caucase (moderne)", INK, 30, anchor="la")
    label(d, (24, 62), Y["mission"]["name"], INK, 17, bold=False, anchor="la")
    legend(d, (OUT_W - 24 - 440, 20))
    scalebar(d, (OUT_W - 24, OUT_H - 70))
    label(d, (OUT_W - 24, OUT_H - 24), "Fond de carte © OpenStreetMap contributors", "#5a6668", 15, bold=False, anchor="rs", halo=2)

    out = img.convert("RGB")
    (ROOT / "docs").mkdir(exist_ok=True)
    out.save(ROOT / "docs/carte.jpg", quality=88, optimize=True)
    small = out.resize((1600, round(OUT_H * 1600 / OUT_W)), Image.LANCZOS)
    small.save(ROOT / "src/mission/l10n/DEFAULT/carte.jpg", quality=80, optimize=True)
    return out


def legend(d, origin):
    x, top = origin
    rows = [("rect", BLUE, "Base bleue avec slots"), ("rect", RED, "Base rouge avec slots"), ("tri", GREEN, "FARP"),
            ("line", TKB, "Ravitailleur / AWACS bleu (hippodrome)"), ("line", TKR, "Ravitailleur / AWACS rouge"),
            ("dash", RED, "CAP à la demande (rouge / bleue)"), ("qra", RED, "QRA : rayon d'intervention"),
            ("num", RED, "Zone de combat (numéro du briefing)"), ("let", GREEN, "Entraînement : H hélicos, A attaque, S SEAD, R recherche"),
            ("front", FRONT, "Ligne de front (approx.)"), ("sanct", BLUE, "Sanctuaire bleu"), ("ship", BLUE, "Porte-avions")]
    lh, w = 24, 440
    d.rounded_rectangle([x, top, x + w, top + len(rows) * lh + 20], radius=8, fill=(255, 255, 255, 235), outline="#b7c1c3")
    for i, (kind, col, text) in enumerate(rows):
        cy, cx = top + 14 + i * lh + lh / 2, x + 22
        if kind == "rect":
            d.rectangle([cx - 8, cy - 8, cx + 8, cy + 8], fill=col, outline=HALO, width=2)
        elif kind == "tri":
            d.polygon([(cx, cy - 10), (cx + 10, cy + 7), (cx - 10, cy + 7)], fill=col)
        elif kind == "line":
            d.line([(cx - 14, cy), (cx + 14, cy)], fill=col, width=8)
        elif kind in ("dash", "front", "sanct"):
            dashed(d, (cx - 14, cy), (cx + 14, cy), col, {"dash": 4, "front": 5, "sanct": 6}[kind], (7, 5))
        elif kind == "qra":
            disc(d, (cx, cy), 11, None, col, 2)
        elif kind == "num":
            disc(d, (cx, cy), 11, col, HALO, 2)
            label(d, (cx, cy), "1", HALO, 12, anchor="mm", halo=0)
        elif kind == "let":
            disc(d, (cx, cy), 11, HALO, col, 3)
            label(d, (cx, cy), "H", col, 12, anchor="mm", halo=0)
        elif kind == "ship":
            d.polygon([(cx - 13, cy - 4), (cx + 13, cy - 4), (cx + 8, cy + 6), (cx - 8, cy + 6)], fill=col)
        d.text((x + 46, cy), text, font=font(15), fill=INK, anchor="lm")


def scalebar(d, origin):
    x1, y = origin
    length = 50 * 1852 * px_per_m(*BULLSEYE)
    x0 = x1 - length
    d.rectangle([x0 - 6, y - 26, x1 + 6, y + 8], fill=(255, 255, 255, 220))
    d.line([(x0, y), (x1, y)], fill=INK, width=4)
    for x in (x0, x0 + length / 2, x1):
        d.line([(x, y - 8), (x, y + 4)], fill=INK, width=3)
    d.text(((x0 + x1) / 2, y - 12), "50 nm (échelle au bullseye)", font=font(14), fill=INK, anchor="ms")


if __name__ == "__main__":
    print(render().size)
