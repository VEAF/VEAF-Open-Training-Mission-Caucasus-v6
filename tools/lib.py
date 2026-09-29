"""Outils communs aux générateurs de lots (tools/gen_*.py).

Les générateurs écrivent un fichier de lot dans tools/batches/ ; tools/mcp.py l'exécute sur le
catalogue d'actions de veaf-mission-mcp (code VMCT de develop).
"""
import json
import math
from pathlib import Path

M = "D:/dev/_VEAF/VEAF-Open-Training-Mission-Caucasus-v6"
ROOT = Path(M)

BLUE = dict(coalition="blue", country_id=2, country_name="USA")
RED = dict(coalition="red", country_id=0, country_name="Russia")

# Bullseye commun : mont Elbrouz (geocode « Mount Elbrus »).
BULLSEYE = (-154706, 665527)

# Ravitailleurs : milieu de l'hippodrome, altitude (FL), TACAN, fréquence — voir gen_03_soutien.py.
TANKERS = {
    "Arco 1": ((-307500, 525000), 180, "51Y", 251.0),
    "Texaco 1": ((-245000, 585000), 220, "52Y", 252.0),
    "Shell 1": ((-290000, 787500), 200, "53Y", 253.0),
    "Shell 2": ((-325000, 867500), 240, "54Y", 254.0),
}

_af = json.loads((ROOT / "tools/airfields.json").read_text(encoding="utf-8").split(": ", 1)[1])["airfields"]
AIRFIELDS = {a["name"]: (a["x"], a["y"]) for a in _af}

_gcw = (ROOT / "tools/loadouts-germanycw.json").read_text(encoding="utf-8")
GCW = {g["name"]: g for g in json.loads(_gcw[_gcw.index("{"):])["groups"]}


def pylons(src_group):
    """Emport d'un groupe de GermanyCW-v6, au format {station: {"CLSID": ...}}."""
    return {k: {"CLSID": v} for k, v in GCW[src_group]["units"][0]["pylons"].items()}


def nm(a, b):
    return math.hypot(a[0] - b[0], a[1] - b[1]) / 1852


def off(p, brg, m):
    """Point à `m` mètres de `p`, au relèvement `brg` (degrés, x = nord, y = est)."""
    r = math.radians(brg)
    return (p[0] + m * math.cos(r), p[1] + m * math.sin(r))


def bullseye(p):
    """« BULLSEYE 123/45 » : cap = atan2(Δy, Δx), distance en nm."""
    brg = math.degrees(math.atan2(p[1] - BULLSEYE[1], p[0] - BULLSEYE[0])) % 360
    return f"BULLSEYE {brg:03.0f}/{nm(p, BULLSEYE):.0f}"


def nearest_tanker(p):
    n, (c, fl, tacan, f) = min(TANKERS.items(), key=lambda kv: nm(p, kv[1][0]))
    return f"{n} (TACAN {tacan}, {f:.1f} MHz, FL{fl}) à {nm(p, c):.0f} nm"


class Batch:
    def __init__(self):
        self.items = []

    def act(self, action, **params):
        self.items.append({"name": action, "params": {"mission_path": M, **params}})

    def save(self, name):
        path = ROOT / "tools/batches" / name
        path.write_text(json.dumps(self.items, indent=1, ensure_ascii=False), encoding="utf-8")
        print(len(self.items), "actions ->", path.name)


def cmd_unit(alias_cmd, carrier_type, tag, extra=""):
    """Faux porteur de zone : `#command="<alias ...>"` + suffixe unique (+ balises de tirage)."""
    name = f'#command="{alias_cmd}"'
    if extra:
        name += " " + extra
    return {"type": carrier_type, "name": f"{name} {tag}"}
