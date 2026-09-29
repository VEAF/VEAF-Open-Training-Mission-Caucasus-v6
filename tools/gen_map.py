"""Cartes du briefing (prompt §4.13) : la carte du théâtre et un zoom par secteur, sur fond OpenStreetMap.

Sorties : docs/carte.jpg (en tête du README), docs/cartes/*.jpg (les zooms), les mêmes images dans
src/mission/l10n/DEFAULT/ pour le briefing DCS, déclarées dans mapResource et listées dans les tables
pictureFileName* de la mission (ce script les réécrit : la mission liste toujours ce qui a été dessiné).

Tout vient des données de la mission (src/mission/, mission.yaml, tools/lib.py) : bases avec slots,
FARP, hippodromes de soutien, CAP, cercles de QRA, zones numérotées comme dans le README, zones
d'entraînement, sanctuaire, front approximatif, porte-avions, bullseye. Tuiles OSM en cache dans
.veaf-backups/tiles/ ; User-Agent sans aucune donnée personnelle (politique d'usage OSM).
Adapté de gen_map.py de GermanyCW-v6.
Usage : python tools/gen_map.py
"""
import math
import re
import sys
from pathlib import Path

import requests
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, str(Path(__file__).parent))
from paths import VMCT  # noqa: E402  (met aussi le code VMCT sur sys.path)
import yaml  # noqa: E402
from mission_tools.miz_tools import read_mission_folder  # noqa: E402
from veaf_libs.coordinates import xy_to_latlon  # noqa: E402

from lib import AIRFIELDS, BULLSEYE, ROOT  # noqa: E402

TILE = 256
TILE_URL = "https://tile.openstreetmap.org/{z}/{x}/{y}.png"
UA = {"User-Agent": "veaf-briefing-map/1.0 (+https://github.com/VEAF/VEAF-Mission-Creation-Tools)"}
L10N = ROOT / "src/mission/l10n/DEFAULT"
NM = 1852
FONT, FONTB, FONTI = (r"C:\Windows\Fonts\segoeui.ttf", r"C:\Windows\Fonts\segoeuib.ttf", r"C:\Windows\Fonts\segoeuii.ttf")
BLUE, RED, TKB, TKR, GREEN, INK, FRONT, HALO = "#1f5fbf", "#c2362b", "#0b86a8", "#c96a10", "#2e7f38", "#1b2629", "#a4221a", "#ffffff"


def ll(x, y):
    r = xy_to_latlon("Caucasus", x, y)
    return (r[0], r[1]) if isinstance(r, (tuple, list)) else (r["lat"], r["lon"])


def merc01(lat, lon):
    """Coordonnées Web Mercator du monde entier dans [0, 1] (indépendantes du niveau de zoom)."""
    return ((lon + 180) / 360,
            (1 - math.log(math.tan(math.radians(lat)) + 1 / math.cos(math.radians(lat))) / math.pi) / 2)


class View:
    """Une fenêtre du fond de carte (bornes Mercator [0, 1]), le niveau de tuiles et la largeur de sortie."""

    def __init__(self, u0, v0, u1, v1, zoom, out_w):
        self.u0, self.v0, self.u1, self.v1, self.zoom, self.out_w = u0, v0, u1, v1, zoom, out_w
        self.scale = out_w / ((u1 - u0) * 2 ** zoom * TILE)   # px de sortie par px de tuile
        self.out_h = round((v1 - v0) * 2 ** zoom * TILE * self.scale)

    def px(self, x, y):
        u, v = merc01(*ll(x, y))
        k = 2 ** self.zoom * TILE * self.scale
        return ((u - self.u0) * k, (v - self.v0) * k)

    def px_per_m(self, x, y):
        return self.px_per_m_at(ll(x, y)[0])

    def px_per_m_at(self, lat):
        return self.scale / (156543.03 * math.cos(math.radians(lat)) / (2 ** self.zoom))

    def centre_lat(self):
        v = (self.v0 + self.v1) / 2
        return math.degrees(math.atan(math.sinh(math.pi * (1 - 2 * v))))


V = None  # la vue en cours de dessin : tous les utilitaires la lisent


def px(x, y):
    return V.px(x, y)


def px_per_m(x, y):
    return V.px_per_m(x, y)


def basemap():
    cache = ROOT / ".veaf-backups/tiles"
    cache.mkdir(parents=True, exist_ok=True)
    n = 2 ** V.zoom
    X0, Y0, X1, Y1 = V.u0 * n, V.v0 * n, V.u1 * n, V.v1 * n
    tx0, ty0, tx1, ty1 = int(X0), int(Y0), int(X1), int(Y1)
    sheet = Image.new("RGB", ((tx1 - tx0 + 1) * TILE, (ty1 - ty0 + 1) * TILE), "#f4f6f2")
    sess = requests.Session()
    for i, tx in enumerate(range(tx0, tx1 + 1)):
        for j, ty in enumerate(range(ty0, ty1 + 1)):
            f = cache / f"{V.zoom}_{tx}_{ty}.png"
            if not f.exists():
                r = sess.get(TILE_URL.format(z=V.zoom, x=tx, y=ty), headers=UA, timeout=30)
                r.raise_for_status()
                f.write_bytes(r.content)
            sheet.paste(Image.open(f).convert("RGB"), (i * TILE, j * TILE))
    box = (round((X0 - tx0) * TILE), round((Y0 - ty0) * TILE), round((X1 - tx0) * TILE), round((Y1 - ty0) * TILE))
    return sheet.crop(box).resize((V.out_w, V.out_h), Image.LANCZOS)


def faded_basemap():
    img = basemap().convert("RGBA")
    return Image.alpha_composite(img, Image.new("RGBA", img.size, (255, 255, 255, 95)))


def font(size, bold=False, italic=False):
    return ImageFont.truetype(FONTB if bold else FONTI if italic else FONT, size)


def dashed_poly(d, pts, fill, width, dash):
    """Tirets le long d'une polyligne, le motif se poursuivant d'un segment à l'autre (sinon un petit
    cercle, fait de segments plus courts qu'un tiret, se dessine en trait plein)."""
    left, on = dash[0], True   # ce qui reste du tiret (ou du blanc) en cours
    for (ax, ay), (bx, by) in zip(pts, pts[1:]):
        length = math.hypot(bx - ax, by - ay)
        if not length:
            continue
        ux, uy, t = (bx - ax) / length, (by - ay) / length, 0.0
        while t < length:
            t2 = min(t + left, length)
            if on:
                d.line([(ax + ux * t, ay + uy * t), (ax + ux * t2, ay + uy * t2)], fill=fill, width=width)
            left -= t2 - t
            t = t2
            if left <= 1e-9:
                on = not on
                left = dash[0] if on else dash[1]


def dashed(d, a, b, fill, width, dash=(14, 8)):
    dashed_poly(d, [a, b], fill, width, dash)


def dashed_circle(d, c, r, fill, width, dash):
    n = max(48, int(r / 6))
    ring = [(c[0] + r * math.cos(2 * math.pi * k / n), c[1] + r * math.sin(2 * math.pi * k / n)) for k in range(n + 1)]
    dashed_poly(d, ring, fill, width, dash)


def label(d, xy, text, fill, size=17, bold=True, anchor="la", italic=False, halo=3):
    d.text(xy, text, font=font(size, bold, italic), fill=fill, anchor=anchor, stroke_width=halo, stroke_fill=HALO)


def disc(d, c, r, fill, outline, w=3):
    d.ellipse([c[0] - r, c[1] - r, c[0] + r, c[1] + r], fill=fill, outline=outline, width=w)


PLACED = []  # centres des repères déjà posés, pour écarter ceux qui se chevauchent


def place(c, r=16, text_w=0):
    """Position libre la plus proche de c, pour un repère de rayon r suivi d'une étiquette de text_w
    pixels : le nom d'une zone ne doit pas recouvrir celui d'une base. Renvoie (position, côté de
    l'étiquette : +1 à droite, -1 à gauche)."""
    def spots(p, side):
        step = 14
        return [p] + [(p[0] + side * (20 + k), p[1]) for k in range(0, int(text_w) + step, step)]

    def inside(ss):
        return all(8 < a[0] < V.out_w - 8 and 8 < a[1] < V.out_h - 8 for a in ss)

    def free(ss):
        return inside(ss) and all(math.hypot(a[0] - q[0], a[1] - q[1]) >= 2 * r + 2 for a in ss for q in PLACED)

    best = None   # à défaut de place libre, la position la moins encombrée plutôt que le point exact
    for k in range(0, 160):
        ang, dist = k * 0.9, 0 if k == 0 else 2 * r + 6 * (k // 7)
        p = (c[0] + dist * math.cos(ang), c[1] + dist * math.sin(ang))
        for side in (1, -1):
            ss = spots(p, side)
            if free(ss):
                PLACED.extend(ss)
                return p, side
            if inside(ss):
                room = min(math.hypot(a[0] - q[0], a[1] - q[1]) for a in ss for q in PLACED)
                if best is None or room > best[0]:
                    best = (room, p, side, ss)
    if best:
        PLACED.extend(best[3])
        return best[1], best[2]
    PLACED.extend(spots(c, 1))
    return c, 1


def obstacles():
    """Pixels occupés par un objet de la mission ou son nom : l'étiquette d'une ligne s'en écarte."""
    pts = []
    for _side, _n, (x, y) in BASES:
        c = px(x, y)
        pts += [(c[0] + k * 40, c[1]) for k in range(6)]
    for z in Y["modules"]["COMBATZONE"]["combat_zones"]:
        tz = ZONES[z["zone_name"]]
        pts.append(px(tz["x"], tz["y"]))
    for n in SUPPORT:
        a, b = (px(p["x"], p["y"]) for p in GROUPS[n][2]["route"]["points"][:2])
        pts += [(a[0] + (b[0] - a[0]) * k / 8, a[1] + (b[1] - a[1]) * k / 8) for k in range(9)]
    return pts


def clear_point(line, inset=150, step=30):
    """Le point d'une ligne, bien dans la vue, le plus loin de tout autre objet (un zoom n'en montre qu'un bout)."""
    obs, best = obstacles(), None
    for a, b in zip(line, line[1:]):
        n = max(1, int(math.hypot(b[0] - a[0], b[1] - a[1]) / step))
        for k in range(n + 1):
            p = (a[0] + (b[0] - a[0]) * k / n, a[1] + (b[1] - a[1]) * k / n)
            if not (inset < p[0] < V.out_w - inset and inset < p[1] < V.out_h - inset):
                continue
            score = min(math.hypot(p[0] - o[0], p[1] - o[1]) for o in obs)
            if best is None or score > best[0]:
                best = (score, p)
    return best[1] if best else None


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
FARPS = [(n, g) for n, (_s, cat, g) in GROUPS.items() if cat == "static" and n.startswith("FARP ") and "munitions" not in n]
CARRIERS = [("CSG-74 Stennis", "Stennis"), ("CSG-01 Tarawa", "Tarawa")]
FRONT_PTS = [((AIRFIELDS[a][0] + AIRFIELDS[b][0]) / 2, (AIRFIELDS[a][1] + AIRFIELDS[b][1]) / 2)
             for a, b in (("Sochi-Adler", "Maykop-Khanskaya"), ("Gudauta", "Maykop-Khanskaya"), ("Nalchik", "Mineralnye Vody"), ("Beslan", "Mozdok"))]
FRONT_PTS = [(-116680, 408929)] + FRONT_PTS[:1] + FRONT_PTS[2:] + [(-140000, 900000)]  # de la côte à l'est de Beslan
LETTERS = {"Kobuleti": "H", "Akhalkalaki": "A", "Taman": "S", "MountainHike": "R"}
SANCTUARY = [GROUPS[f"Sanctuaire bleu-{i:02d}"][2] for i in range(1, 23)]
# l'arène n'a pas de zone de déclenchement : ses slots en vol et les deux AWACS qui la couvrent la bornent
ARENA = [GROUPS[n][2] for n in ("Arène - F-14B - FOX1 - bleu", "Arène - F-14B - FOX1 - rouge", "Darkstar 1", "AWACS Arène Rouge")]


def arena_centre():
    return (sum(g["x"] for g in ARENA) / len(ARENA), sum(g["y"] for g in ARENA) / len(ARENA))


def arena_radius():
    c = arena_centre()
    return max(math.hypot(g["x"] - c[0], g["y"] - c[1]) for g in ARENA) + 10 * NM


# ── dessin ───────────────────────────────────────────────────────────────────────────────────────
def draw_layers(img, detail, title_box=None):
    """Tous les objets de la mission, dans la vue V. detail : carte zoomée (noms des zones, cercle de l'arène)."""
    PLACED.clear()
    reserve(ImageDraw.Draw(img), detail, title_box)   # les étiquettes placées s'écartent de ce qui est fixe
    qras = Y["modules"]["QRA"]["definitions"]
    area = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ad = ImageDraw.Draw(area)
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
        if c[1] - r < TITLE_H:   # le haut du cercle touche le bandeau du titre : étiquette sous le cercle
            label(d, (c[0], c[1] + r + 6), q["name"], col, 18, anchor="mt")
        else:
            label(d, (c[0], c[1] - r - 6), q["name"], col, 18, anchor="ms")

    # sanctuaire bleu : polygone de ses unités, dans l'ordre
    poly = [px(g["x"], g["y"]) for g in SANCTUARY]
    dashed_poly(d, poly + poly[:1], BLUE, 6, (18, 10))
    if not detail:
        label(d, px(-392000, 520000), "SANCTUAIRE BLEU", BLUE, 20, anchor="mm")
    elif (p := clear_point(poly + poly[:1])) is not None:   # un zoom n'en montre qu'un bord : le nommer côté intérieur
        cx, cy = px(sum(g["x"] for g in SANCTUARY) / len(SANCTUARY), sum(g["y"] for g in SANCTUARY) / len(SANCTUARY))
        k = 34 / (math.hypot(cx - p[0], cy - p[1]) or 1)
        label(d, (p[0] + (cx - p[0]) * k, p[1] + (cy - p[1]) * k), "sanctuaire bleu", BLUE, 17, italic=True, bold=False, anchor="mm")

    front = [px(*p) for p in FRONT_PTS]
    dashed_poly(d, front, FRONT, 6, (22, 12))
    fm = clear_point(front) if detail else ((front[1][0] + front[2][0]) / 2, (front[1][1] + front[2][1]) / 2 - 14)
    if fm:
        label(d, fm, "ligne de front (approx.)", FRONT, 18, bold=False, italic=True, anchor="ms")

    for cp in Y.get("cap_missions") or []:
        side, _cat, g = GROUPS[f"OnDemand-{cp['group_name']}"]
        pts = g["route"]["points"]
        a, b = px(pts[0]["x"], pts[0]["y"]), px(pts[1]["x"], pts[1]["y"])
        col = RED if side == "red" else BLUE
        dashed(d, a, b, col, 4, (10, 8))
        if detail:
            mid = ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2)
            w = d.textlength(cp["menu_name"], font=font(15, italic=True))
            pos, sd = place(mid, r=14, text_w=w)   # cinq CAP partent du même hippodrome à l'ouest
            label(d, (pos[0] + sd * 10, pos[1]), cp["menu_name"], col, 15, bold=False, italic=True,
                  anchor="lm" if sd > 0 else "rm")
    for n in SUPPORT:
        side, _cat, g = GROUPS[n]
        a, b = (px(p["x"], p["y"]) for p in g["route"]["points"][:2])
        if detail and not any(-40 < q[0] < V.out_w + 40 and -40 < q[1] < V.out_h + 40 for q in (a, b)):
            continue   # hippodrome entièrement hors du cadre : ni trait ni étiquette flottante
        col = TKR if side == "red" else TKB
        d.line([a, b], fill=col, width=9)
        w = d.textlength(n, font=font(17, True))
        anchor_pt = b if b[0] + 10 + w < V.out_w - 8 else a   # sinon l'étiquette sortirait du cadre
        if anchor_pt[0] + 10 + w < V.out_w - 8:
            label(d, (anchor_pt[0] + 10, anchor_pt[1]), n, col, 17, anchor="lm")
        else:   # ancrée à droite, et ramenée dans le cadre
            label(d, (min(anchor_pt[0] - 10, V.out_w - 8), anchor_pt[1]), n, col, 17, anchor="rm")

    ABOVE = {"Tbilisi"}  # étiquette au-dessus du carré : à droite elle chevauche Vaziani, à gauche Shell 2
    for side, n, (x, y) in BASES:
        c = px(x, y)
        col = RED if side == "red" else BLUE
        d.rectangle([c[0] - 8, c[1] - 8, c[0] + 8, c[1] + 8], fill=col, outline=HALO, width=2)
        if n in ABOVE and not detail:
            label(d, (c[0], c[1] - 12), n, col, 18, anchor="ms")
        else:
            label(d, (c[0] + 13, c[1] - 2), n, col, 18, anchor="lm")

    # zones : entraînement (lettre, niveau facile seulement) et combat (numéro du README)
    num = 0
    for z in Y["modules"]["COMBATZONE"]["combat_zones"]:
        tz = ZONES[z["zone_name"]]
        key = z["zone_name"].split("_")[1]
        if z.get("training"):
            if z["zone_name"].endswith(("_Easy", "MountainHike")):
                true_c = px(tz["x"], tz["y"])
                if detail:   # l'étendue de la zone compte pour qui s'y entraîne
                    dashed_circle(d, true_c, tz["radius"] * px_per_m(tz["x"], tz["y"]), GREEN, 4, (12, 8))
                short = z["friendly_name"].split(" - ")[0]
                c, side = place(true_c, text_w=d.textlength(short, font=font(17, True)) if detail else 0)
                disc(d, c, 15, HALO, GREEN, 4)
                label(d, c, LETTERS[key], GREEN, 17, anchor="mm", halo=0)
                if detail:
                    label(d, (c[0] + side * 20, c[1]), short, GREEN, 17, anchor="lm" if side > 0 else "rm")
            continue
        num += 1
        true_c = px(tz["x"], tz["y"])
        if detail and not (0 < true_c[0] < V.out_w and 0 < true_c[1] < V.out_h):
            continue   # repère hors du cadre : son étiquette seule, collée au bord, ne dirait rien
        c, side = place(true_c, text_w=d.textlength(z["friendly_name"], font=font(17, True)) if detail else 0)
        if math.hypot(c[0] - true_c[0], c[1] - true_c[1]) > 3:
            d.line([true_c, c], fill=RED, width=2)
            disc(d, true_c, 3, RED, RED, 1)
        disc(d, c, 15, RED, HALO, 3)
        label(d, c, str(num), HALO, 15, anchor="mm", halo=0)
        if detail:
            label(d, (c[0] + side * 20, c[1]), z["friendly_name"], RED, 17, anchor="lm" if side > 0 else "rm")

    for n, g in FARPS:
        c = px(g["x"], g["y"])
        d.polygon([(c[0], c[1] - 10), (c[0] + 10, c[1] + 7), (c[0] - 10, c[1] + 7)], fill=GREEN, outline=HALO)
        if detail:
            label(d, (c[0] + 14, c[1] + 8), n, GREEN, 16, anchor="lm")
    for name, short in CARRIERS:
        g = GROUPS[name][2]
        c = px(g["x"], g["y"])
        d.polygon([(c[0] - 16, c[1] - 5), (c[0] + 16, c[1] - 5), (c[0] + 10, c[1] + 7), (c[0] - 10, c[1] + 7)], fill=BLUE, outline=HALO)
        label(d, (c[0], c[1] + 12), name if detail else short, BLUE, 16, anchor="mt")

    # arène AirQuake : son cercle dans le zoom, une flèche au bord de la carte du théâtre
    ax, ay = px(*arena_centre())
    if detail:
        r = arena_radius() * px_per_m(*arena_centre())
        dashed_circle(d, (ax, ay), r, INK, 5, (16, 10))
        label(d, (ax, ay - r - 8), "Arène AirQuake — slots en vol, un AWACS par camp", INK, 20, anchor="ms")
        for n, txt, col in (("Arène - F-14B - FOX1 - bleu", "slots bleus (Fox 1 et Fox 3)", BLUE),
                            ("Arène - F-14B - FOX1 - rouge", "slots rouges (Fox 1 et Fox 3)", RED),
                            ("Darkstar 1", "Darkstar 1 (AWACS bleu)", TKB),
                            ("AWACS Arène Rouge", "AWACS Arène Rouge", TKR)):
            g = GROUPS[n][2]
            c = px(g["x"], g["y"])
            disc(d, c, 9, col, HALO, 3)
            pos, sd = place(c, r=14, text_w=d.textlength(txt, font=font(17, True)))
            if pos != c:
                d.line([c, pos], fill=col, width=2)
            label(d, (pos[0] + sd * 14, pos[1]), txt, col, 17, anchor="lm" if sd > 0 else "rm")
    else:
        ay = min(max(ay, TITLE_H + 40), V.out_h - 40)
        d.polygon([(8, ay), (34, ay - 14), (34, ay + 14)], fill=INK)
        label(d, (42, ay), "Arène AirQuake (ouest, sur la mer)", INK, 17, anchor="lm")

    bu = px(*BULLSEYE)
    disc(d, bu, 11, None, INK, 3)
    disc(d, bu, 3.5, INK, INK, 1)
    txt = "BULLSEYE (Elbrouz)"
    if bu[0] + 15 + d.textlength(txt, font=font(17, True)) < V.out_w - 8:
        label(d, (bu[0] + 15, bu[1] - 12), txt, INK, 17, anchor="ls")
    else:
        label(d, (bu[0] - 15, bu[1] - 12), txt, INK, 17, anchor="rs")
    return img, d


def reserve(d, detail, title_box=None):
    """Inscrit dans PLACED tout ce qui se dessine à une position imposée — repères et noms des bases,
    FARP, porte-avions, traits de soutien et de CAP. Les étiquettes que place() positionne ensuite
    (zones, CAP) ne peuvent plus recouvrir ce qui était là avant elles."""
    def text_row(c, text, size, dx=13):
        w = d.textlength(text, font=font(size, True))
        PLACED.extend([c] + [(c[0] + dx + k, c[1]) for k in range(0, int(w) + 14, 14)])

    if title_box:   # le bandeau du titre recouvre ce qui passe dessous
        x0, y0, x1, y1 = title_box
        PLACED.extend([(x, y) for x in range(int(x0), int(x1) + 14, 14) for y in range(int(y0), int(y1) + 14, 14)])
    for _side, n, (x, y) in BASES:
        text_row(px(x, y), n, 18)
    for n, g in FARPS:
        text_row(px(g["x"], g["y"]), n if detail else "", 16)
    for name, short in CARRIERS:
        g = GROUPS[name][2]
        text_row(px(g["x"], g["y"]), name if detail else short, 16)
    for n in SUPPORT + [f"OnDemand-{c['group_name']}" for c in Y.get("cap_missions") or []]:
        a, b = (px(pt["x"], pt["y"]) for pt in GROUPS[n][2]["route"]["points"][:2])
        PLACED.extend([(a[0] + (b[0] - a[0]) * k / 12, a[1] + (b[1] - a[1]) * k / 12) for k in range(13)])


def attribution(d):
    label(d, (V.out_w - 24, V.out_h - 24), "Fond de carte © OpenStreetMap contributors", "#5a6668", 15,
          bold=False, anchor="rs", halo=2)


# ── carte du théâtre ─────────────────────────────────────────────────────────────────────────────
LAT_N, LAT_S, LON_W, LON_E = 46.1, 40.9, 35.8, 46.2  # tout objet dessiné tombe dans ce cadre, sauf l'arène
MAIN_ZOOM, MAIN_W = 9, 2000


def render_main():
    global V
    (u0, v0), (u1, v1) = merc01(LAT_N, LON_W), merc01(LAT_S, LON_E)
    V = View(u0, v0, u1, v1, MAIN_ZOOM, MAIN_W)
    img, d = draw_layers(faded_basemap(), detail=False)
    label(d, (24, 22), "VEAF Open Training — Caucase (moderne)", INK, 30, anchor="la")
    label(d, (24, 62), Y["mission"]["name"], INK, 17, bold=False, anchor="la")
    legend(d, (V.out_w - 24 - 440, 20))
    scalebar(d, (V.out_w - 24, V.out_h - 70), 50, px_per_m(*BULLSEYE), "échelle au bullseye")
    attribution(d)
    return img.convert("RGB")


# ── cartes zoomées ───────────────────────────────────────────────────────────────────────────────
# Chaque zoom est nommé par ce qu'il doit montrer ; son cadre est la boîte autour de ces objets
# (rayons compris) plus une marge. Le briefing DCS les affiche après la carte du théâtre, dans cet ordre.
ZOOMS = [
    ("georgie_ouest", "Géorgie de l'ouest : Batumi, Kobuleti, Kutaisi, entraînement hélicoptères et attaque",
     ["base:Batumi", "base:Kobuleti", "base:Kutaisi", "qra:QRA Kutaisi", "zone:combatZone_Kobuleti_Easy",
      "zone:combatZone_Akhalkalaki_Easy", "zone:combatZone_RoadBlock_KM91", "cap:Khashuri - L-39C - FL100"]),
    ("abkhazie", "Abkhazie et côte : Gudauta, Sochi, FARP Kodori, recherche et sauvetage",
     ["base:Gudauta", "base:Sochi", "qra:QRA Gudauta", "zone:combatZone_MountainHike",
      "zone:combatZone_Lazarevskoye", "farp:FARP Kodori", "farp:FARP Ritsa", "cap:CAP F-16C - Gudauta - FL250"]),
    ("front_est", "Front est — Ossétie : Beslan, Nalchik, Mozdok, Prokhladny",
     ["base:Beslan", "base:Nalchik", "base:Mozdok", "zone:combatZone_Beslan", "zone:combatZone_Terek",
      "zone:combatZone_Mozdok_SA11", "zone:combatZone_Mozdok_OCA", "zone:combatZone_Convoi_Prokhladny",
      "zone:combatZone_Prokhladny_Otages", "cap:CAP F-15C - Beslan - FL300"]),
    ("nord_stavropol", "Nord — Mineralnye Vody, Georgievsk, Nevinnomyssk",
     ["base:Mineralnye Vody", "qra:QRA MinVody", "zone:combatZone_Convoi_MinVody",
      "zone:combatZone_Georgievsk_SCUD", "zone:combatZone_Nevinnomyssk_Depot"]),
    ("kouban", "Kouban — Krasnodar, Maykop, Psebay",
     ["base:Krasnodar", "base:Maykop", "qra:QRA Krasnodar", "zone:combatZone_Psebay_SAM",
      "zone:combatZone_Psebay_Usine", "zone:combatZone_Maykop_Defenses"]),
    ("taman", "Secteur Ouest — péninsule de Taman : entraînement SEAD, hors QRA",
     ["zone:combatZone_Taman_Hard@22"]),
    ("mer_noire", "Mer Noire : porte-avions et zones antinavire",
     ["carrier:CSG-74 Stennis", "carrier:CSG-01 Tarawa", "zone:combatZone_Antinavire_Cargos",
      "zone:combatZone_Antinavire_Escorte"]),
    ("arene", "Arène AirQuake (ouest, sur la mer)", ["arena"]),
]
ZOOM_W = 1600    # px : le panneau de briefing DCS ajuste une image à la fois à sa taille
MARGIN = 0.10    # de la boîte, de chaque côté
TITLE_H = 110    # px du bandeau de titre, laissés libres au-dessus des objets à cadrer
ASPECT = (1.0, 1.5)   # largeur / hauteur maintenue dans cet intervalle


def extents(ref):
    """Points (x, y, rayon en m) qu'un zoom doit contenir, pour une référence.

    Un suffixe `@<nm>` impose un rayon minimal autour de l'objet, pour garder du contexte autour
    d'une zone étroite (la péninsule autour du SA-6 de Taman).
    """
    ref, _, wide = ref.partition("@")
    around = float(wide) * NM if wide else 0
    kind, _, name = ref.partition(":")
    if around:
        return [(x, y, max(r, around)) for x, y, r in _extents(kind, name)]
    return _extents(kind, name)


def _extents(kind, name):
    if kind == "base":
        found = [p for _s, n, p in BASES if n == name]
        if not found:
            raise KeyError(f"zoom : base {name!r} inconnue")
        return [(found[0][0], found[0][1], 8 * NM)]
    if kind == "farp":
        g = GROUPS[name][2]
        return [(g["x"], g["y"], 8 * NM)]
    if kind == "zone":
        z = ZONES[name]
        return [(z["x"], z["y"], max(z["radius"], 6 * NM))]
    if kind == "qra":
        q = next(q for q in Y["modules"]["QRA"]["definitions"] if q["name"] == name)
        z = ZONES[q["trigger_zone"]]
        return [(z["x"], z["y"], z["radius"])]
    if kind in ("support", "cap"):
        g = GROUPS[name if kind == "support" else f"OnDemand-{name}"][2]
        return [(p["x"], p["y"], 6 * NM) for p in g["route"]["points"][:2]]
    if kind == "carrier":
        g = GROUPS[name][2]
        return [(g["x"], g["y"], 10 * NM)]
    if kind == "arena":
        c = arena_centre()
        return [(c[0], c[1], arena_radius() + 4 * NM)]
    raise KeyError(f"zoom : référence inconnue {kind}:{name}")


def zoom_view(refs):
    us, vs = [], []
    for ref in refs:
        for x, y, r in extents(ref):
            for dx, dy in ((r, 0), (-r, 0), (0, r), (0, -r)):
                u, v = merc01(*ll(x + dx, y + dy))
                us.append(u)
                vs.append(v)
    u0, u1, v0, v1 = min(us), max(us), min(vs), max(vs)
    w, h = u1 - u0, v1 - v0
    u0, u1, v0, v1 = u0 - w * MARGIN, u1 + w * MARGIN, v0 - h * MARGIN, v1 + h * MARGIN
    w, h = u1 - u0, v1 - v0
    if w / h < ASPECT[0]:      # agrandir le côté court autour du centre
        g = (h * ASPECT[0] - w) / 2
        u0, u1 = u0 - g, u1 + g
    elif w / h > ASPECT[1]:
        g = (w / ASPECT[1] - h) / 2
        v0, v1 = v0 - g, v1 + g
    v0 -= TITLE_H * (u1 - u0) / ZOOM_W   # place pour le bandeau de titre au-dessus de la boîte
    zoom = round(math.log2(ZOOM_W / ((u1 - u0) * TILE)))   # niveau de tuiles le plus proche de la résolution de sortie
    return View(u0, v0, u1, v1, zoom, ZOOM_W)


def nice_scale_nm(ppm):
    """Une échelle ronde, environ un cinquième de la largeur."""
    target = V.out_w / 5 / ppm / NM
    return max(n for n in (2, 5, 10, 20, 25, 50, 100) if n <= max(target, 2))


def render_zoom(index, title, refs):
    global V
    V = zoom_view(refs)
    sub = f"VEAF Open Training Caucase — zoom {index} sur {len(ZOOMS)} · bullseye : mont Elbrouz"
    probe = ImageDraw.Draw(Image.new("RGB", (1, 1)))
    tw = max(probe.textlength(title, font=font(30, True)), probe.textlength(sub, font=font(16))) + 40
    img, d = draw_layers(faded_basemap(), detail=True, title_box=(12, 12, 12 + tw, 100))
    d.rounded_rectangle([12, 12, 12 + tw, 100], radius=8, fill=(255, 255, 255, 235), outline="#b7c1c3")
    d.text((32, 24), title, font=font(30, True), fill=INK, anchor="la")
    d.text((32, 68), sub, font=font(16), fill="#3c4a4d", anchor="la")
    ppm = V.px_per_m_at(V.centre_lat())
    scalebar(d, (V.out_w - 24, V.out_h - 70), nice_scale_nm(ppm), ppm, "échelle au centre")
    attribution(d)
    return img.convert("RGB")


# ── sorties ──────────────────────────────────────────────────────────────────────────────────────
def render():
    """Dessine toutes les cartes, écrit docs/ et les images du briefing, et les liste dans la mission."""
    # tout dessiner d'abord : une tuile qui ne se télécharge pas doit laisser la mission et ses images intactes
    main = render_main()
    zooms = [(f"carte_{i:02d}_{slug}.jpg", render_zoom(i, title, refs)) for i, (slug, title, refs) in enumerate(ZOOMS, 1)]

    (ROOT / "docs/cartes").mkdir(parents=True, exist_ok=True)
    main.save(ROOT / "docs/carte.jpg", quality=88, optimize=True)
    small = main.resize((ZOOM_W, round(main.height * ZOOM_W / main.width)), Image.LANCZOS)
    small.save(L10N / "carte.jpg", quality=80, optimize=True)
    for old in list((ROOT / "docs/cartes").glob("carte_*.jpg")) + list(L10N.glob("carte_*.jpg")):
        old.unlink()   # un zoom renommé ou retiré ne doit pas traîner dans le .miz
    for name, im in zooms:
        im.save(ROOT / "docs/cartes" / name, quality=85, optimize=True)
        im.save(L10N / name, quality=80, optimize=True)
    declare_pictures(["carte.jpg"] + [name for name, _ in zooms])
    return main


def reskey(name):
    return "ResKey_ImageBriefing_" + Path(name).stem


def declare_pictures(pictures):
    """Entrées de mapResource et tables pictureFileName* de la mission.

    Le bleu et le neutre listent toutes les images, le rouge aucune. DCS affiche la liste rouge puis
    la bleue à un joueur dont il ignore le camp (slot Client, slot dynamique, spectateur : lu dans
    me_autobriefing.lua ; la règle du briefing en vol appartient au moteur et reste à confirmer), donc
    une même image présente dans les deux listes s'affiche deux fois. Ici aucune unité n'est de niveau
    Player et les seuls slots rouges classiques sont ceux de l'arène : personne ne perd de carte.
    """
    path = L10N / "mapResource"
    text, nl = path.read_text(encoding="utf-8"), eol(path)
    # tout ce qui n'est pas une image de briefing est gardé tel quel (les sons des balises, MCP_Sound_*)
    kept = [ln for ln in text.splitlines() if "=" in ln and "mapResource" not in ln and "ResKey_ImageBriefing_" not in ln]
    lines = [f'  {reskey(p)} = "{p}",' for p in pictures] + kept
    path.write_text("mapResource = \n{\n" + "\n".join(sorted(lines)) + "\n}", encoding="utf-8", newline=nl)

    mpath = ROOT / "src/mission/mission"
    mission, nl = mpath.read_text(encoding="utf-8"), eol(mpath)
    listed = "{\n" + "".join(f'    [{i}] = "{reskey(p)}",\n' for i, p in enumerate(pictures, 1)) + "  },"
    for side, value in (("B", listed), ("N", listed), ("R", "{},")):
        mission, n = re.subn(r"(?m)^  pictureFileName%s = (?:\{\},|\{\n(?:    .*\n)*?  \},)" % side,
                             f"  pictureFileName{side} = {value}", mission)
        if n != 1:
            raise RuntimeError(f"pictureFileName{side} : {n} correspondance(s) dans {mpath}")
    mpath.write_text(mission, encoding="utf-8", newline=nl)


def eol(path):
    """La fin de ligne du fichier (git peut l'extraire dans les deux sens) : une réécriture la garde."""
    return "\r\n" if b"\r\n" in Path(path).read_bytes()[:4096] else "\n"


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


def scalebar(d, origin, nm, ppm, where):
    x1, y = origin
    length = nm * NM * ppm
    x0 = x1 - length
    d.rectangle([x0 - 6, y - 26, x1 + 6, y + 8], fill=(255, 255, 255, 220))
    d.line([(x0, y), (x1, y)], fill=INK, width=4)
    for x in (x0, x0 + length / 2, x1):
        d.line([(x, y - 8), (x, y + 4)], fill=INK, width=3)
    d.text(((x0 + x1) / 2, y - 12), f"{nm} nm ({where})", font=font(14), fill=INK, anchor="ms")


if __name__ == "__main__":
    img = render()
    print("docs/carte.jpg", img.size, "+", len(ZOOMS), "zooms")
