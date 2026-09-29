"""Lot 03 : ravitailleurs, AWACS et leurs escortes (bleu et rouge)."""
import json
M = "D:/dev/_VEAF/VEAF-Open-Training-Mission-Caucasus-v6"
t = open(M + "/tools/loadouts-germanycw.json", encoding="utf-8").read()
G = {g["name"]: g for g in json.loads(t[t.index("{"):])["groups"]}
def pylons(src):
    return {k: {"CLSID": v} for k, v in G[src]["units"][0]["pylons"].items()}
BLUE = dict(coalition="blue", country_id=2, country_name="USA")
RED = dict(coalition="red", country_id=0, country_name="Russia")
# name, type, side, a, b, FL, kt, MHz, task, beacon (channel, callsign) or None, escort type/source
SUPPORT = [
    ("Arco 1", "KC-135", BLUE, (-300000, 500000), (-315000, 550000), 180, 420, 251.0, "Refueling", (51, "AR1"), "Shell 1 escort"),
    ("Texaco 1", "KC135MPRS", BLUE, (-235000, 560000), (-255000, 610000), 220, 420, 252.0, "Refueling", (52, "TX1"), "Shell 1 escort"),
    ("Shell 1", "KC135MPRS", BLUE, (-285000, 760000), (-295000, 815000), 200, 420, 253.0, "Refueling", (53, "SH1"), "Shell 1 escort"),
    ("Shell 2", "KC-135", BLUE, (-320000, 840000), (-330000, 895000), 240, 420, 254.0, "Refueling", (54, "SH2"), "Shell 1 escort"),
    ("Magic 1", "E-3A", BLUE, (-275000, 450000), (-290000, 510000), 300, 360, 265.0, "AWACS", None, "Magic 1 escort"),
    ("Overlord 1", "E-3A", BLUE, (-305000, 700000), (-315000, 760000), 310, 360, 266.0, "AWACS", None, "Overlord 1 escort"),
    ("Tanker Rouge", "IL-78M", RED, (20000, 470000), (30000, 530000), 200, 420, 261.0, "Refueling", None, "Tanker Rouge escort"),
    ("AWACS Rouge", "A-50", RED, (30000, 620000), (40000, 690000), 300, 360, 260.0, "AWACS", None, "AWACS Rouge escort"),
]
b = []
def act(action, **p):
    b.append({"name": action, "params": {"mission_path": M, **p}})
for n, typ, side, a, bb, fl, kt, f, task, beacon, esc in SUPPORT:
    act("add_air_group", **side, name=n, unit_type=typ, count=1, start="air", position={"x": a[0], "y": a[1]},
        altitude_ft=fl * 100, speed_kt=kt, frequency_mhz=f, task=task, skill="High")
    act("edit_route", group_name=n, operation="add", position={"x": bb[0], "y": bb[1]}, altitude_ft=fl * 100, speed_kt=kt)
    act("edit_route", group_name=n, operation="add_task", index=1, task="set_unlimited_fuel", task_params={"value": True})
    if beacon:
        act("edit_route", group_name=n, operation="add_task", index=1, task="activate_beacon",
            task_params={"channel": beacon[0], "mode": "Y", "callsign": beacon[1], "bearing": True, "aa": True})
    if task == "Refueling":
        act("edit_route", group_name=n, operation="add_task", index=1, task="tanker", task_params={})
    else:
        act("edit_route", group_name=n, operation="add_task", index=1, task="awacs", task_params={})
        act("edit_route", group_name=n, operation="add_task", index=1, task="eplrs", task_params={"value": True})
    act("edit_route", group_name=n, operation="add_task", index=1, task="orbit",
        task_params={"pattern": "Race-Track", "altitude_ft": fl * 100, "speed_kt": kt})
    # escorte : une paire, 2 km derrière, même altitude
    src = G[esc]
    en = n + " escort"
    act("add_air_group", **side, name=en, unit_type=src["units"][0]["type"], count=2, start="air",
        position={"x": a[0] - 2000, "y": a[1] - 2000}, altitude_ft=fl * 100, speed_kt=kt, frequency_mhz=f,
        task="Escort", skill="High", pylons=pylons(esc))
    act("edit_route", group_name=en, operation="add_task", index=1, task="set_unlimited_fuel", task_params={"value": True})
    act("edit_route", group_name=en, operation="add_task", index=1, task="escort",
        task_params={"group_name": n, "engagement_distance_nm": 30})
json.dump(b, open(M + "/tools/batches/03-soutien.json", "w", encoding="utf-8"), indent=1, ensure_ascii=False)
print(len(b), "actions")
