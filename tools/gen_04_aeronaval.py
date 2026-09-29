"""Lot 04 : groupe aéronaval (Stennis + Tarawa), slots de pont, drones Reaper."""
import json
M = "D:/dev/_VEAF/VEAF-Open-Training-Mission-Caucasus-v6"
t = open(M + "/tools/loadouts-germanycw.json", encoding="utf-8").read()
G = {g["name"]: g for g in json.loads(t[t.index("{"):])["groups"]}
def pylons(src):
    return {k: {"CLSID": v} for k, v in G[src]["units"][0]["pylons"].items()}
BLUE = dict(coalition="blue", country_id=2, country_name="USA")
b = []
def act(action, **p):
    b.append({"name": action, "params": {"mission_path": M, **p}})
# Porte-avions : positions et fréquences de la v5 (TACAN 10X STS, ICLS 10, U225 ; Tarawa 11X TAA, ICLS 11, U226)
act("add_carrier_group", **BLUE, name="CSG-74 Stennis", carrier_name="CVN-74 Stennis", carrier_type="Stennis",
    position={"x": -347934, "y": 511479}, heading_deg=270, speed_kt=15, escorts=["TICONDEROG", "TICONDEROG", "PERRY"],
    tower_mhz=225.0, tacan_channel=10, tacan_callsign="STS", icls_channel=10, link4_mhz=225.0,
    recovery_tanker=True, tanker_tacan_channel=75, tanker_tacan_callsign="T74", tanker_frequency_mhz=290.9,
    rescue_helicopter=True)
act("add_carrier_group", **BLUE, name="CSG-01 Tarawa", carrier_name="LHA-1 Tarawa", carrier_type="LHA_Tarawa",
    position={"x": -340061, "y": 468500}, heading_deg=270, speed_kt=12, escorts=["PERRY", "PERRY"],
    tower_mhz=226.0, tacan_channel=11, tacan_callsign="TAA", icls_channel=11, link4_mhz=None,
    recovery_tanker=False, rescue_helicopter=True)
# Slots de pont (joueurs)
for name, typ, n, start, src in [
    ("F/A-18C Stennis 1", "FA-18C_hornet", 4, "deck-cold", None),
    ("F/A-18C Stennis HOT 1", "FA-18C_hornet", 4, "deck-hot", None),
    ("F-14B Stennis 1", "F-14B", 1, "deck-cold", "F-14B Stennis 1"),
    ("F-14B Stennis 2", "F-14B", 1, "deck-cold", "F-14B Stennis 2"),
    ("F-14B Stennis HOT 1", "F-14B", 1, "deck-hot", "F-14B Stennis HOT 1"),
]:
    p = dict(**BLUE, name=name, unit_type=typ, count=n, start=start, carrier="CVN-74 Stennis", skill="Client",
             frequency_mhz=225.0, task="CAP")
    if src:
        p["pylons"] = pylons(src)
    act("add_air_group", **p)
for name, start in [("AV-8B Tarawa 1", "deck-cold"), ("AV-8B Tarawa HOT 1", "deck-hot")]:
    act("add_air_group", **BLUE, name=name, unit_type="AV8BNA", count=2, start=start, carrier="LHA-1 Tarawa",
        skill="Client", frequency_mhz=226.0, task="CAS")
# Drones de guidage laser (v5 : Agate / Bizmuth, laser 1687 / 1688, V118.90 / 118.80)
for name, pos, f in [("Reaper 1", (-131000, 830000), 118.8), ("Reaper 2", (-75500, 525000), 118.9)]:
    act("add_air_group", **BLUE, name=name, unit_type="MQ-9 Reaper", count=1, start="air",
        position={"x": pos[0], "y": pos[1]}, altitude_ft=15000, speed_kt=160, frequency_mhz=f, task="AFAC", skill="High")
    act("edit_route", group_name=name, operation="add_task", index=1, task="set_unlimited_fuel", task_params={"value": True})
    act("edit_route", group_name=name, operation="add_task", index=1, task="orbit",
        task_params={"pattern": "Circle", "altitude_ft": 15000, "speed_kt": 160})
json.dump(b, open(M + "/tools/batches/04-aeronaval-drones.json", "w", encoding="utf-8"), indent=1, ensure_ascii=False)
print(len(b), "actions")
