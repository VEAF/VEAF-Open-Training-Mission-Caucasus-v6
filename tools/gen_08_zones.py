"""Lot 08 : les 16 vraies zones de combat (training: false).

Reprend les intentions et les éléments éprouvés de la v5 (routes « On Road » des convois, statiques de
l'usine de Psebay, de l'hôtel de Prokhladny et du barrage KM91, positions des défenses de Maykop) ;
ajoute un front côtier, un site SCUD, un dépôt, l'OCA de Mozdok et un convoi MinVody → Baksan.

Règle §4.7 : les SAM d'une zone active n'atteignent ni une base amie, ni une piste de ravitailleur, ni
une zone d'entraînement — vérifié par tools/check_portees.py.
Usage : python tools/gen_08_zones.py [fragment de nom de zone]
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from lib import BLUE, RED, ROOT, Batch, bullseye, cmd_unit, nearest_tanker, off  # noqa: E402

b = Batch()
only = sys.argv[1] if len(sys.argv) > 1 else None
V5 = json.loads((ROOT / "tools/v5-zones.json").read_text(encoding="utf-8"))
REPLACE = {"FARP Ammo Dump Coating": ".Ammunition depot"}  # un dépôt FARP rouge deviendrait un point logistique CTLD rouge


def xy(p):
    return {"x": p[0], "y": p[1]}


def where(c):
    return f"{bullseye(c)}. Ravitailleur le plus proche : {nearest_tanker(c)}."


def zone(name, center, radius, groups, friendly, family, briefing, category="vehicle", extra=None):
    """Zone + groupes du camp rouge ; `extra` = actions add_group supplémentaires (statiques, autre camp)."""
    if only and only not in name:
        return
    b.act("create_combat_zone", zone_name=name, position=xy(center), radius=radius, groups=groups, **RED,
          category=category, combat_zone={"friendly_name": friendly, "radio_group_name": family, "training": False,
                                          "briefing": briefing})
    for e in extra or []:
        b.act("add_group", for_combat_zone=name, keep_position=True, **e)


def static(name, typ, pos, side=RED):
    return dict(**side, category="static", name=name, position=xy(pos), units=[{"type": typ, "name": name}])


def v5_statics(prefix, zone_name):
    out = []
    for n, g in V5.items():
        if g["cat"] == "static" and prefix.lower() in n.lower():
            typ = REPLACE.get(g["units"][0][0], g["units"][0][0])
            out.append(static(f"{zone_name}-{len(out) + 1:02d}", typ, (g["x"], g["y"])))
    return out


def route(v5_name):
    return [{"x": p[0], "y": p[1]} for p in V5[v5_name]["route"]]


# ── Front ────────────────────────────────────────────────────────────────────────────────────────
BES = (-117500, 848000)
bes_red = [{"name": f"assaut-{i}", "units": [{"type": "BTR-80", "count": 4}],
            "position": xy(V5[f"combatZone_BattleOfBeslan-RU-mainforce #00{i}"]["route"][0][:2]),
            "route": route(f"combatZone_BattleOfBeslan-RU-mainforce #00{i}")} for i in (1, 2, 3)]
bes_red += [{"name": f"renforts-{i}", "units": [cmd_unit("-armor, size 7, armor 5, defense 0", "T-72B", f"Bes-r{i}", "#spawnradius=500")],
             "position": xy(off(BES, 20 + 40 * i, 3500))} for i in (1, 2)]
bes_red += [{"name": f"osa-{i}", "units": [cmd_unit("-sa8", "Osa 9A33 ln", f"Bes-o{i}", '#spawngroup="osa" #spawncount=1')],
             "position": xy(off(BES, 90 * i, 2500))} for i in (1, 2)]
bes_red += [{"name": "manpads", "units": [cmd_unit("-sa18s", "SA-18 Igla-S manpad", "Bes-m1")], "position": xy(off(BES, 0, 1500))},
            {"name": "aaa", "units": [cmd_unit("-shilka", "ZSU-23-4 Shilka", "Bes-a1")], "position": xy(off(BES, 180, 1500))}]
bes_blue = [dict(**BLUE, category="vehicle", name=f"combatZone_Beslan-allies-{i}",
                 position=xy(V5[f"combatZone_BattleOfBeslan-US-mainforce #00{i}"]["route"][0][:2]),
                 units=[{"type": "M-1 Abrams", "count": 3}], route=route(f"combatZone_BattleOfBeslan-US-mainforce #00{i}"))
            for i in (1, 2, 3)]
zone("combatZone_Beslan", BES, 8000, bes_red, "Bataille de Beslan", "Front",
     "Bataille blindée au nord de Beslan : trois compagnies de BTR-80 rouges montent à l'assaut des "
     "Abrams bleus, deux groupes blindés en renfort. Détruisez les blindés rouges ; ne tirez pas sur les "
     "Abrams. Défense : SA-8 (un des deux sites), MANPADS, Shilka. Drone Reaper 1 au-dessus (laser 1688). "
     + where(BES), extra=bes_blue)

TER = (-114217, 816657)
zone("combatZone_Terek", TER, 7620,
     [{"name": "logistique", "units": [cmd_unit("-transport, size 25, defense 1", "Ural-375", "Ter-1", "#spawnradius=2500")], "position": xy(TER)},
      {"name": "infanterie", "units": [cmd_unit("-infantry, size 25, armor 1, defense 2", "BTR-80", "Ter-2", "#spawnchance=50")], "position": xy(off(TER, 90, 1500))},
      {"name": "manpads", "units": [cmd_unit("-sa18s", "SA-18 Igla-S manpad", "Ter-3")], "position": xy(off(TER, 270, 1000))}],
     "Parc logistique de Terek", "Front",
     "Le parc logistique de Terek ravitaille l'offensive rouge sur Beslan. Détruisez les camions. "
     "Défense légère : DCA de convoi, une chance sur deux d'infanterie mécanisée, MANPADS. " + where(TER))

LAZ = off((-116680, 408929), 45, 3000)
zone("combatZone_Lazarevskoye", LAZ, 5000,
     [{"name": "blindes-1", "units": [cmd_unit("-armor, size 6, armor 3, defense 0", "T-72B", "Laz-1")], "position": xy(off(LAZ, 0, 1500))},
      {"name": "blindes-2", "units": [cmd_unit("-armor, size 6, armor 3, defense 0", "T-72B", "Laz-2")], "position": xy(off(LAZ, 120, 1500))},
      {"name": "artillerie", "units": [{"type": "Grad-URAL", "count": 3}], "position": xy(off(LAZ, 240, 2000))},
      {"name": "sa13", "units": [cmd_unit("-sa13_squad", "Strela-10M3", "Laz-3")], "position": xy(off(LAZ, 60, 800))},
      {"name": "aaa", "units": [cmd_unit("-shilka", "ZSU-23-4 Shilka", "Laz-4")], "position": xy(off(LAZ, 200, 800))}],
     "Front côtier de Lazarevskoye", "Front",
     "Le front de la côte, au nord-ouest de Sochi : deux groupes blindés et une batterie de lance-roquettes "
     "BM-21 en appui. Détruisez les blindés et les BM-21. Défense : SA-13, Shilka. " + where(LAZ))

# ── SEAD ─────────────────────────────────────────────────────────────────────────────────────────
PSS = (-76800, 520400)
zone("combatZone_Psebay_SAM", PSS, 3000,
     [{"name": "sa6", "units": [cmd_unit("-sa6", "Kub 2P25 ln", "PsS-1")], "position": {"x": -76809, "y": 520561}},
      {"name": "sa2", "units": [cmd_unit("-sa2", "S_75M_Volhov", "PsS-2")], "position": {"x": -77268, "y": 520408}},
      {"name": "sa15-n", "units": [cmd_unit("-sa15", "Tor 9A331", "PsS-3", '#spawngroup="sa15" #spawncount=1')], "position": {"x": -75894, "y": 520488}},
      {"name": "sa15-s", "units": [cmd_unit("-sa15", "Tor 9A331", "PsS-4", '#spawngroup="sa15" #spawncount=1')], "position": {"x": -76848, "y": 519736}},
      {"name": "aaa", "units": [cmd_unit("-shilka", "ZSU-23-4 Shilka", "PsS-5")], "position": xy(off(PSS, 300, 900))}],
     "Sites SAM de Psebay", "SEAD",
     "Les sites SAM qui couvrent l'usine de Psebay : un SA-2, un SA-6, et un SA-15 (un des deux sites), "
     "plus de la DCA. Neutralisez les radars avant la frappe de l'usine. " + where(PSS))

MOZS = off((-89140, 839198), 0, 12000)
zone("combatZone_Mozdok_SA11", MOZS, 3000,
     [{"name": "sa11", "units": [cmd_unit("-sa11", "SA-11 Buk LN 9A310M1", "MzS-1")], "position": xy(MOZS)},
      {"name": "sa15", "units": [cmd_unit("-sa15", "Tor 9A331", "MzS-2")], "position": xy(off(MOZS, 90, 1500))},
      {"name": "aaa", "units": [cmd_unit("-shilka", "ZSU-23-4 Shilka", "MzS-3")], "position": xy(off(MOZS, 270, 1000))}],
     "Site SA-11 au nord de Mozdok", "SEAD",
     "Une batterie SA-11 isolée au nord de Mozdok, protégée par un SA-15 et de la DCA. Détruisez le radar "
     "et les lanceurs du SA-11. " + where(MOZS))

# ── Convois ──────────────────────────────────────────────────────────────────────────────────────
KM = (-349034, 703649)
km_extra = v5_statics("combatZone_roadBlock", "combatZone_RoadBlock_KM91-poste")
zone("combatZone_RoadBlock_KM91", KM, 15240,
     [{"name": "convoi", "units": [{"type": "GAZ-3307", "count": 5}, {"type": "ZSU-23-4 Shilka"}],
       "position": xy(V5["combatZone_roadBlock-convoy #001"]["route"][0][:2]), "route": route("combatZone_roadBlock-convoy #001")},
      {"name": "infanterie", "units": [{"type": "Infantry AK", "count": 4}, {"type": "Paratrooper RPG-16", "count": 2}],
       "position": xy(V5["combatZone_roadBlock-mobileTransport #002"]["route"][0][:2])},
      {"name": "manpads", "units": [cmd_unit("-sa18s", "SA-18 Igla-S manpad", "KM-1")], "position": xy(off(KM, 0, 800))}],
     "Barrage routier KM91", "Convois",
     "Les Russes tiennent un barrage sur la route Batumi - Tbilissi, et un convoi arrive de l'est pour le "
     "renforcer. Détruisez les bunkers, les blindés du poste et le convoi. Défense : la Shilka du convoi, "
     "MANPADS. " + where(KM), extra=km_extra)

PRK_C = V5["combatZone_SaveTheHostages-Prohladniy-reliefConvoy"]["route"]
zone("combatZone_Convoi_Prokhladny", PRK_C[0][:2], 5000,
     [{"name": "convoi", "units": [{"type": "T-72B", "count": 2}, {"type": "BTR-80", "count": 2}, {"type": "Ural-375", "count": 4},
                                   {"type": "ZSU-23-4 Shilka"}, {"type": "Strela-10M3"}],
       "position": xy(PRK_C[0][:2]), "route": route("combatZone_SaveTheHostages-Prohladniy-reliefConvoy")}],
     "Convoi de secours vers Prokhladny", "Convois",
     "Un convoi blindé part de Mozdok pour secourir la garnison de Prokhladny, par la route. Arrêtez-le "
     "avant qu'il arrive. Défense dans la colonne : Shilka et SA-13. " + where(PRK_C[0][:2]))

MV = (-52627, 710268)
zone("combatZone_Convoi_MinVody", MV, 4000,
     [{"name": "convoi", "units": [{"type": "Ural-375", "count": 6}, {"type": "BMP-2", "count": 2}, {"type": "ZSU-23-4 Shilka"}],
       "position": xy(MV), "route": [xy(MV), {"x": -107316, "y": 749774}]}],
     "Convoi Mineralnye Vody - Baksan", "Convois",
     "Un convoi de ravitaillement quitte Mineralnye Vody par la route vers Baksan, derrière le front de "
     "Nalchik. Détruisez les camions. Défense : BMP-2 et Shilka dans la colonne. " + where(MV))

# ── Frappe dans la profondeur ────────────────────────────────────────────────────────────────────
PSF = (-75523, 525018)
zone("combatZone_Psebay_Usine", PSF, 1500,
     [{"name": "blindes", "units": [{"type": "T-90", "count": 2}, {"type": "BMP-3", "count": 2}], "position": xy(off(PSF, 90, 400))},
      {"name": "sa15", "units": [cmd_unit("-sa15", "Tor 9A331", "PsF-1", "#spawnchance=50")], "position": xy(off(PSF, 0, 600))},
      {"name": "aaa-1", "units": [cmd_unit("-shilka", "ZSU-23-4 Shilka", "PsF-2", '#spawngroup="aaa" #spawncount=2')], "position": xy(off(PSF, 120, 500))},
      {"name": "aaa-2", "units": [cmd_unit("-zu23", "Ural-375 ZU-23", "PsF-3", '#spawngroup="aaa" #spawncount=2')], "position": xy(off(PSF, 240, 500))},
      {"name": "aaa-3", "units": [cmd_unit("-shilka", "ZSU-23-4 Shilka", "PsF-4", '#spawngroup="aaa" #spawncount=2')], "position": xy(off(PSF, 300, 700))}],
     "Usine d'armes chimiques de Psebay", "Frappe",
     "Cette usine fabrique des armes chimiques pour un groupe terroriste. Détruisez les deux bâtiments de "
     "l'usine et le bunker des scientifiques ; le reste est secondaire. Défense : DCA, une chance sur deux "
     "d'un SA-15, et les sites SAM voisins (zone « Sites SAM de Psebay »). " + where(PSF),
     extra=v5_statics("combatZone_Psebay_Factory", "combatZone_Psebay_Usine-batiment"))

PRK = (-94373, 790912)
prk = [{"name": f"patrouille-{i}", "units": [{"type": "BTR-80", "count": 2}],
        "position": xy(V5[f"combatZone_SaveTheHostages-Prohladniy-armor #0{i}"]["route"][0][:2]),
        "route": route(f"combatZone_SaveTheHostages-Prohladniy-armor #0{i}"), "patrol": True} for i in ("14", "15", "21")]
prk += [{"name": f"aaa-{i}", "units": [cmd_unit("-shilka", "ZSU-23-4 Shilka", f"Prk-a{i}", '#spawngroup="aaa" #spawncount=2')],
         "position": xy(off(PRK, 120 * i, 900))} for i in (1, 2, 3)]
prk += [{"name": f"sa9-{i}", "units": [cmd_unit("-sa9_squad", "Strela-1 9P31", f"Prk-s{i}", '#spawngroup="sa9" #spawncount=1')],
         "position": xy(off(PRK, 60 + 180 * i, 1500))} for i in (1, 2)]
prk += [{"name": "sa8", "units": [cmd_unit("-sa8", "Osa 9A33 ln", "Prk-o1", "#spawnchance=50")], "position": xy(off(PRK, 200, 2500))},
        {"name": "manpads", "units": [cmd_unit("-sa18s", "SA-18 Igla-S manpad", "Prk-m1")], "position": xy(off(PRK, 30, 400))}]
zone("combatZone_Prokhladny_Otages", PRK, 13000, prk, "Otages à Prokhladny", "Frappe",
     "Des otages sont retenus dans un hôtel fortifié de Prokhladny. Détruisez la caserne et les patrouilles "
     "de BTR-80 ; l'hôtel doit rester debout pour l'équipe au sol. Défense : Shilka, SA-9, une chance sur "
     "deux d'un SA-8, MANPADS. " + where(PRK),
     extra=[static("combatZone_Prokhladny_Otages-hotel", "houseA_arm", (-94373, 790912)),
            static("combatZone_Prokhladny_Otages-caserne", "house1arm", (-94296, 790626))])

SC = off((-56173, 738276), 270, 6000)
zone("combatZone_Georgievsk_SCUD", SC, 3000,
     [{"name": "scud", "units": [{"type": "Scud_B", "count": 4}], "position": xy(SC)},
      {"name": "soutien", "units": [{"type": "Ural-375", "count": 3}, {"type": "ZIL-131 KUNG"}], "position": xy(off(SC, 90, 500))},
      {"name": "sa15", "units": [cmd_unit("-sa15", "Tor 9A331", "Scd-1")], "position": xy(off(SC, 0, 1200))},
      {"name": "aaa", "units": [cmd_unit("-shilka", "ZSU-23-4 Shilka", "Scd-2")], "position": xy(off(SC, 200, 800))},
      {"name": "manpads", "units": [cmd_unit("-sa18s", "SA-18 Igla-S manpad", "Scd-3")], "position": xy(off(SC, 300, 600))}],
     "Site SCUD de Georgievsk", "Frappe",
     "Quatre lanceurs SCUD en position de tir à l'ouest de Georgievsk. Détruisez les lanceurs. Défense : "
     "SA-15, Shilka, MANPADS. " + where(SC))

NV = off((-17773, 610312), 90, 3000)
nv_extra = [static(f"combatZone_Nevinnomyssk_Depot-{i + 1:02d}", t, off(NV, 40 * i, 250 + 30 * i))
            for i, t in enumerate(["Fuel tank", "Fuel tank", "Fuel tank", "Fuel tank", ".Ammunition depot", ".Ammunition depot",
                                   "Warehouse", "Warehouse", "Tech combine"])]
zone("combatZone_Nevinnomyssk_Depot", NV, 2000,
     [{"name": "sa19", "units": [cmd_unit("-sa19", "2S6 Tunguska", "Nev-1")], "position": xy(off(NV, 0, 900))},
      {"name": "aaa-1", "units": [cmd_unit("-zu23", "Ural-375 ZU-23", "Nev-2", '#spawngroup="aaa" #spawncount=1')], "position": xy(off(NV, 150, 700))},
      {"name": "aaa-2", "units": [cmd_unit("-zu23", "Ural-375 ZU-23", "Nev-3", '#spawngroup="aaa" #spawncount=1')], "position": xy(off(NV, 270, 700))}],
     "Dépôt logistique de Nevinnomyssk", "Frappe",
     "Le grand dépôt de carburant et de munitions qui alimente le front. Détruisez les réservoirs et les "
     "entrepôts. Défense locale : SA-19 et DCA ; attention, le dépôt est sous la couverture permanente du "
     "SA-10 de Stavropol. " + where(NV), extra=nv_extra)

# ── OCA ──────────────────────────────────────────────────────────────────────────────────────────
MK = (-23149, 456611)
mk = [{"name": "sa10", "units": [cmd_unit("-sa10", "S-300PS 5P85C ln", "Mk-1")], "position": {"x": -23147, "y": 456539}}]
mk += [{"name": f"sa15-{i}", "units": [cmd_unit("-sa15", "Tor 9A331", f"Mk-s{i}", '#spawngroup="sa15" #spawncount=2')],
        "position": xy((V5[f"CombatZone_MaykopDefenses - MaykopSA15 #-{i}"]["x"], V5[f"CombatZone_MaykopDefenses - MaykopSA15 #-{i}"]["y"]))} for i in (1, 2, 3, 4)]
mk += [{"name": f"aaa-{i}", "units": [cmd_unit("-shilka" if i % 2 else "-zu23", "ZSU-23-4 Shilka" if i % 2 else "Ural-375 ZU-23", f"Mk-a{i}", '#spawngroup="aaa" #spawncount=4')],
        "position": xy((V5[f"CombatZone_MaykopDefenses - MaykopAAA #-{i}"]["x"], V5[f"CombatZone_MaykopDefenses - MaykopAAA #-{i}"]["y"]))} for i in range(1, 9)]
mk += [{"name": "blindes", "units": [cmd_unit("-armor, armor 3, size 6, defense 0", "BMP-2", "Mk-b1", "#spawnradius=2500")], "position": {"x": -23148, "y": 457522}},
       {"name": "logistique", "units": [cmd_unit("-transport, defense 0, size 5", "GAZ-3307", "Mk-t1", "#spawnradius=2500")], "position": {"x": -22848, "y": 455755}}]
zone("combatZone_Maykop_Defenses", MK, 3048, mk, "Défenses de la base de Maykop", "OCA",
     "La base de Maykop est défendue par un bataillon SA-10, deux SA-15 tirés parmi quatre sites, quatre "
     "pièces de DCA tirées parmi huit, et des blindés. Neutralisez les défenses pour préparer l'assaut. "
     + where(MK))

MZ = (-83886, 835223)
stands = json.loads((ROOT / "tools/mozdok-stands.json").read_text())
jets = ["Tu-22M3", "Su-24M", "Su-24M", "Su-25", "Su-25", "IL-76MD", "Tu-22M3"]
mz_extra = [static(f"combatZone_Mozdok_OCA-avion-{i + 1}", t, (stands[2 * i]["x"], stands[2 * i]["y"])) for i, t in enumerate(jets[:6])]
zone("combatZone_Mozdok_OCA", MZ, 2500,
     [{"name": "sa15", "units": [cmd_unit("-sa15", "Tor 9A331", "Mz-1")], "position": xy(off(MZ, 45, 1200))},
      {"name": "aaa-1", "units": [cmd_unit("-shilka", "ZSU-23-4 Shilka", "Mz-2")], "position": xy(off(MZ, 135, 700))},
      {"name": "aaa-2", "units": [cmd_unit("-shilka", "ZSU-23-4 Shilka", "Mz-3")], "position": xy(off(MZ, 315, 700))}],
     "Avions au sol de Mozdok", "OCA",
     "Des bombardiers Tu-22M3, des Su-24M, des Su-25 et un Il-76 sont stationnés sur la base de Mozdok. "
     "Détruisez-les au sol. Défense de zone : SA-15, Shilka ; défense permanente de la base : SA-11 et "
     "SA-19. " + where(MZ), extra=mz_extra)

# ── Antinavire (zones de la v5, en mer au sud-ouest) ────────────────────────────────────────────
AN1 = (-295214, 193436)
zone("combatZone_Antinavire_Cargos", AN1, 15240,
     [{"name": "cargos", "units": [cmd_unit("_spawn group, name cargoships", "Dry-cargo ship-1", "An-1", "#spawnradius=20000")], "position": xy(AN1)}],
     "Cargos isolés", "Antinavire",
     "Des cargos sans escorte ravitaillent l'ennemi par la mer. Coulez-les. " + where(AN1), category="ship")
AN2 = (-283948, 192285)
zone("combatZone_Antinavire_Escorte", AN2, 15240,
     [{"name": "convoi", "units": [cmd_unit("_spawn group, name cargoships-escorted", "ALBATROS", "An-2")], "position": xy(AN2)}],
     "Convoi naval escorté", "Antinavire",
     "Des cargos escortés par des bâtiments de guerre ; une frégate Neustrashimy peut les accompagner. "
     "Coulez les cargos. " + where(AN2), category="ship")

b.save("08-zones.json" if not only else f"08-test-{only}.json")
