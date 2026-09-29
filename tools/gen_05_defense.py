"""Lot 05 : défense aérienne permanente des bases et des arrières (#veafInterpreter + EWR).

Règle : aucune batterie permanente ne couvre une base adverse avec slots. Portées de la table de
menace DCS embarquée dans AIEN.lua (non mesurées en jeu) : Patriot 54 nm, Hawk 24, SA-10 65,
SA-11 19, NASAMS 8, Tor 6,5, Tunguska 4,3, Avenger < 5.
"""
import json, math
M = "D:/dev/_VEAF/VEAF-Open-Training-Mission-Caucasus-v6"
t = open(M + "/tools/airfields.json", encoding="utf-8").read()
P = {a["name"]: (a["x"], a["y"]) for a in json.loads(t[t.index("{"):])["airfields"]}
BLUE = dict(coalition="blue", country_id=2, country_name="USA")
RED = dict(coalition="red", country_id=0, country_name="Russia")
ALIAS = {  # alias -> lanceur (porteur), vérifié dans veaf-units.yaml
    "-patriot": "Patriot ln", "-hawk": "Hawk ln", "-nasams": "NASAMS_LN_C", "-avenger_squad": "M1097 Avenger",
    "-sa10": "S-300PS 5P85C ln", "-sa11": "SA-11 Buk LN 9A310M1", "-sa15": "Tor 9A331", "-sa19": "2S6 Tunguska",
}
def off(p, brg, km):
    r = math.radians(brg)
    return (p[0] + km * 1000 * math.cos(r), p[1] + km * 1000 * math.sin(r))
b = []
def act(action, **p):
    b.append({"name": action, "params": {"mission_path": M, **p}})
def site(side, tag, anchor, alias, country, brg, km):
    x, y = off(anchor, brg, km)
    act("add_group", **side, category="vehicle", name=f"AD-{tag}", position={"x": x, "y": y},
        units=[{"type": ALIAS[alias], "name": f'#veafInterpreter["{alias}, country {country}"] #{tag}'}])
# bleu : (base, relèvement vers l'intérieur des terres, MR, LR ?)
for base, brg, mr, lr in [
    ("Sochi-Adler", 45, "-nasams", True), ("Gudauta", 40, "-nasams", False), ("Batumi", 90, "-nasams", False),
    ("Kobuleti", 90, "-nasams", False), ("Kutaisi", 0, "-nasams", True), ("Tbilisi-Lochini", 0, "-nasams", False),
    ("Vaziani", 0, "-nasams", True), ("Nalchik", 180, "-hawk", False), ("Beslan", 180, "-hawk", False)]:
    tag = base.split("-")[0]
    site(BLUE, f"{tag}-SR", P[base], "-avenger_squad", "usa", brg, 1.5)
    site(BLUE, f"{tag}-MR", P[base], mr, "usa", brg + 60, 3.0)
    if lr:
        site(BLUE, f"{tag}-LR", P[base], "-patriot", "usa", brg - 60, 5.0)
# rouge : SR + MR sur les 4 bases avec slots ; SA-10 à Krasnodar et Stavropol
for base, brg in [("Maykop-Khanskaya", 0), ("Krasnodar-Pashkovsky", 0), ("Mineralnye Vody", 0), ("Mozdok", 0)]:
    tag = base.split("-")[0].split(" ")[0]
    site(RED, f"{tag}-SR", P[base], "-sa19", "russia", brg, 1.5)
    site(RED, f"{tag}-MR", P[base], "-sa11", "russia", brg + 120, 3.5)
site(RED, "Krasnodar-LR", P["Krasnodar-Pashkovsky"], "-sa10", "russia", 60, 6.0)
STAVROPOL = (27998, 607332)  # geocode « Stavropol, Stavropol Krai », 117 nm de Nalchik, 131 de Sochi
site(RED, "Stavropol-LR", STAVROPOL, "-sa10", "russia", 0, 0)
site(RED, "Stavropol-SR", STAVROPOL, "-sa15", "russia", 90, 1.5)
# EWR (positions de la v5)
for tag, pos in [("EWR-SE", (-289609, 911190)), ("EWR-SW", (-348761, 633431)), ("EWR-NE", (-136829, 854741)), ("EWR-NW", (-153549, 478873))]:
    act("add_group", **BLUE, category="vehicle", name=f"AD-{tag}", position={"x": pos[0], "y": pos[1]}, units=[{"type": "1L13 EWR", "name": f"AD-{tag}"}])
for tag, pos in [("EWR-Rouge-NW", (15298, 393732)), ("EWR-Rouge-S", (-92108, 550781)), ("EWR-Rouge-NE", (-48675, 706658)), ("EWR-Rouge-E", (-116098, 873169))]:
    act("add_group", **RED, category="vehicle", name=f"AD-{tag}", position={"x": pos[0], "y": pos[1]}, units=[{"type": "55G6 EWR", "name": f"AD-{tag}"}])
json.dump(b, open(M + "/tools/batches/05-defense.json", "w", encoding="utf-8"), indent=1, ensure_ascii=False)
print(len(b), "actions")
