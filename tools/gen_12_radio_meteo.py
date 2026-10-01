"""Lot 12 : src/presets.yaml (plan radio), src/versions.yaml (variantes météo), src/waypoints.yaml.

Écrit les trois fichiers depuis les mêmes chiffres que les groupes (fréquences, TACAN, positions), pour
qu'une valeur ne diverge jamais entre groupe DCS, preset, ASSETS et briefing. Écrase les fichiers ; ceux
du gabarit sont gardés dans .veaf-backups/.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from lib import AIRFIELDS as AF, ROOT  # noqa: E402

# Noms DCS des aérodromes, pas des diminutifs : les canaux de base sont écrits par
# `veaf-tools content airfield-channels`, qui apparie sur le nom DCS. « Base-Krasnodar » était en
# plus ambigu (Krasnodar-Pashkovsky et Krasnodar-Center existent), et « Base-MinVody » n'appariait rien.
BLUE_BASES = ["Sochi-Adler", "Gudauta", "Batumi", "Kobuleti", "Kutaisi", "Nalchik", "Tbilisi-Lochini",
              "Vaziani", "Beslan"]
RED_BASES = ["Maykop-Khanskaya", "Krasnodar-Pashkovsky", "Mineralnye Vody", "Mozdok"]
FLIGHTS = ["Archer", "Arctic", "Ninja", "Pinder", "Bengal", "Blade"]
TACT = [("Magic-1", "Magic 1 (AWACS)", 265.0), ("Overlord-1", "Overlord 1 (AWACS)", 266.0),
        ("Arco-1", "Arco 1 / perche / 51Y", 251.0), ("Texaco-1", "Texaco 1 / panier / 52Y", 252.0),
        ("Shell-1", "Shell 1 / panier / 53Y", 253.0), ("Shell-2", "Shell 2 / perche / 54Y", 254.0),
        ("Stennis", "CVN-74 Stennis / 10X", 225.0), ("Tarawa", "LHA-1 Tarawa / 11X", 226.0),
        ("Darkstar-1", "Darkstar 1 (AWACS arene)", 280.0)]
RED_TACT = [("AWACS-Rouge", "AWACS Rouge (A-50)", 260.0), ("Tanker-Rouge", "Tanker Rouge (Il-78M)", 261.0),
            ("AWACS-Arene-Rouge", "AWACS Arene Rouge (A-50)", 281.0)]

# Titres sans accents : le build lit presets.yaml dans le mauvais encodage (voir tools/retours-vmct.md).
L = ["# Plan radio de la mission VEAF Open Training Caucasus (moderne).",
     "# L'ATC DCS est coupé (silence_atc_on_all_airbases) : les fréquences de base sont des fréquences de",
     "# trafic propres à la mission. Même fréquence partout : groupe DCS, preset, texte ASSETS, briefing.",
     "# Généré par tools/gen_12_radio_meteo.py.",
     "channel_lists:", "  blue:", "    primary_1: # première radio V/UHF (20 canaux au plus)",
     "      01: { title: Guard/UHF, channel: Guard }"]
blue_uhf = [c for c, _, _ in TACT] + [f"Base-{b}" for b in BLUE_BASES] + ["Archer"]
L += [f"      {i:02d}: {c}" for i, c in enumerate(blue_uhf, 2)]
assert len(blue_uhf) + 1 <= 20
L += ["    primary_2: # deuxième radio V/UHF (VHF) ; seule radio des warbirds", "      01: { title: Guard/VHF, channel: Guard }"]
blue_vhf = [f"Base-{b}" for b in BLUE_BASES] + ["Reaper-1", "Reaper-2"] + FLIGHTS
L += [f"      {i:02d}: {c}" for i, c in enumerate(blue_vhf, 2)]
FM = ["    fm_supplement: # FM en plus de deux radios V/UHF (A-10C, hélicoptères) ; 31-34 = balises du Mountain hike"]
FM += [f"      {i:02d}: {30 + i - 1}" for i in range(1, 31)]
L += FM
L += ["  red:", "    primary_1: # première radio V/UHF", "      01: { title: Guard/UHF, channel: Guard }"]
red_uhf = [c for c, _, _ in RED_TACT] + [f"Base-{b}" for b in RED_BASES] + ["Rouge-1", "Rouge-2", "Rouge-3", "Rouge-4"]
L += [f"      {i:02d}: {c}" for i, c in enumerate(red_uhf, 2)]
L += ["    primary_2: # deuxième radio V/UHF (VHF)", "      01: { title: Guard/VHF, channel: Guard }"]
L += [f"      {i:02d}: {c}" for i, c in enumerate([f"Base-{b}" for b in RED_BASES] + ["Rouge-1", "Rouge-2", "Rouge-3", "Rouge-4"], 2)]
L += FM
# surcharges et collections : reprises telles quelles de GermanyCW-v6 (Mi-8 sans injection, CH-47 FM/UHF)
gcw = (ROOT.parent / "VEAF-Open-Training-Mission-GermanyCW-v6/src/presets.yaml").read_text(encoding="utf-8")
block = gcw[gcw.index("presets_assignments:"):gcw.index("channels_collection:")]
block = block.replace("08: Shell-1\n        09: Base-Ramstein", "08: Shell-1\n        09: Base-Sochi")  # noqa
L += ["", *block.rstrip("\n").split("\n"), ""]
L += ["channels_collection: # toutes les fréquences de la mission", "  tactical:", "    Guard:", "      title: Guard",
      "      freqs: { uhf: 243, vhf: 121.5 }"]
for c, t, f in TACT + RED_TACT:
    L += [f"    {c}:", f"      title: {t}", f"      freqs: {{ uhf: {f} }}"]
L += ["    Reaper-1:", "      title: Reaper 1 (drone laser 1688)", "      freqs: { vhf: 118.8 }",
      "    Reaper-2:", "      title: Reaper 2 (drone laser 1687)", "      freqs: { vhf: 118.9 }"]
# La collection « bases » n'est PAS écrite ici. Une fréquence d'aérodrome appartient à DCS et se lit
# sur la vue F10 : la série inventée 270.x / 275.x, en place jusqu'au 01/10/2026, n'y correspondait
# pas, et un pilote qui choisissait le canal « Batumi » ne parlait pas à Batumi. Elles sont écrites
# par `veaf-tools content airfield-channels --apply "<nom DCS>" …`, depuis le référentiel capturé
# dans DCS. Ne tape aucune fréquence d'aérodrome à la main.
L += ["  flights:"]
for i, f in enumerate(FLIGHTS):
    L += [f"    {f}:", f"      title: {f}", f"      freqs: {{ vhf: {120.0 + i / 10:.1f}, uhf: {360.0 + i / 10:.1f} }}"]
for i in range(4):
    L += [f"    Rouge-{i + 1}:", f"      title: Rouge-{i + 1}", f"      freqs: {{ vhf: {124.0 + i / 10:.1f}, uhf: {380.0 + i / 10:.1f} }}"]
# la collection historique de GermanyCW nomme des canaux absents ici : on la réécrit pour le Caucase
text = "\n".join(L) + "\n"
text = text.replace("        09: Base-Sochi\n        10: Base-Spangdahlem\n        11: Base-Buchel\n        12: Base-Norvenich\n"
                    "        13: Base-Wiesbaden\n        14: Base-Nordholz\n        15: Base-Wunstorf\n        16: Base-Fassberg\n"
                    "        17: Base-Fulda\n", "".join(f"        {9 + i:02d}: Base-{b}\n" for i, b in enumerate(BLUE_BASES)))
text = text.replace("        02: Overlord-1\n        03: Magic-1\n        04: Texaco-1\n        05: Arco-1\n        06: Texaco-2\n"
                    "        07: Arco-2\n        08: Shell-1\n",
                    "        02: Magic-1\n        03: Overlord-1\n        04: Arco-1\n        05: Texaco-1\n        06: Shell-1\n"
                    "        07: Shell-2\n        08: Stennis\n")
(ROOT / "src/presets.yaml").write_text(text, encoding="utf-8")

# ── versions.yaml ────────────────────────────────────────────────────────────────────────────────
MOMENTS = [("nuit", '"02:00"', 18.0), ("aube", '"sunrise"', 17.0), ("matin", '"09:00"', 23.0),
           ("jour", '"14:00"', 31.0), ("soir", '"sunset-45*60"', 27.0)]
V = ["# Variantes météo et heure — VEAF Open Training Caucasus (moderne). Généré par tools/gen_12_radio_meteo.py.",
     "#", "# 5 heures (nuit, aube, matin, jour, soir) x 4 ciels (réel, dégagé, épars, pluie) = 20 .miz.",
     "# - réel   : METAR de Tbilisi (UGTB) récupéré au build ; sur le serveur, RealWeather le remplace au",
     "#            lancement grâce au _ICAO_UGTB du nom de la mission ;",
     "# - dégagé : météo manuelle, ciel clair (températures : estimation d'une fin juin à Tbilissi, non sourcée) ;",
     "# - épars / pluie : METAR fixe (le bloc weather: ne sait pas décrire la pluie).", "",
     "position:", "  latitude: 41.637736     # Vaziani, base mère", "  longitude: 45.019091",
     '  timezone: "Asia/Tbilisi"', "", 'base_date: "2022-06-29"', "", "versions:"]
for name, time, temp in MOMENTS:
    V += [f"  - name: {name}-reel", f"    time: {time}", "    airport_icao: UGTB", "",
          f"  - name: {name}-degage", f"    time: {time}", "    weather:", f"      temperature: {temp}",
          "      wind_speed: 3.0", "      wind_direction: 90.0", "      visibility: 40000", '      cloud_type: "clear"',
          "      fog_enabled: false", "",
          f"  - name: {name}-epars", f"    time: {time}",
          f'    metar: "METAR UGTB 291200Z 09008KT 9999 SCT040 SCT090 {int(temp):02d}/12 Q1013"', "",
          f"  - name: {name}-pluie", f"    time: {time}",
          f'    metar: "METAR UGTB 291200Z 27014G24KT 5000 RA BKN012 OVC030 {int(temp) - 6:02d}/{int(temp) - 7:02d} Q1006"', ""]
(ROOT / "src/versions.yaml").write_text("\n".join(V), encoding="utf-8")

# ── waypoints.yaml ───────────────────────────────────────────────────────────────────────────────
PTS = [("ARCO_1", (-300000, 500000), 5486, 200), ("TEXACO_1", (-235000, 560000), 6706, 200),
       ("SHELL_1", (-285000, 760000), 6096, 200), ("SHELL_2", (-320000, 840000), 7315, 200),
       ("TANKER_ROUGE", (20000, 470000), 6096, 200),
       ("FARP_KASPI", (-291157, 847594), 300, 50), ("FARP_JAVA", (-247483, 799954), 300, 50),
       ("FARP_RITSA", (-151582, 518375), 300, 50), ("FARP_LENTEHI", (-214299, 695511), 300, 50),
       ("FARP_AIBGHA", (-146610, 486256), 300, 50), ("FARP_BESLAN_NORD", (-131141, 847396), 300, 50),
       ("FARP_KRASNAYA", (-139098, 478312), 300, 50), ("FARP_KODORI", (-199368, 586501), 300, 50),
       ("FARP_DZHVARI", (-230777, 641049), 300, 50), ("FARP_CASIMIR", (-326935, 661463), 300, 50)]
RED_PTS = [(n.upper(), AF[full], 300, 50) for n, full in (("MAYKOP", "Maykop-Khanskaya"), ("KRASNODAR", "Krasnodar-Pashkovsky"),
                                                           ("MINVODY", "Mineralnye Vody"), ("MOZDOK", "Mozdok"))]
PTS += RED_PTS
PLANS = {  # un plan par catégorie et par camp jouable (le BULLSEYE est ajouté par le build)
    "bleu_avions": ("plane", "blue", ["ARCO_1", "TEXACO_1", "SHELL_1", "SHELL_2"]),
    "bleu_helicopteres": ("helicopter", "blue", [p[0] for p in PTS if p[0].startswith("FARP_")]),
    "rouge_avions": ("plane", "red", ["TANKER_ROUGE"] + [p[0] for p in RED_PTS]),
    "rouge_helicopteres": ("helicopter", "red", [p[0] for p in RED_PTS]),
}
W = ["# Points de navigation injectés dans les appareils joueurs (slots dynamiques) — Caucasus.",
     "# Le BULLSEYE vient de la mission (set_bullseye, mont Elbrouz) et est ajouté par le build.",
     "# x vers le nord, y vers l'est, en mètres ; alt en mètres ; speed en m/s. Généré par tools/gen_12_radio_meteo.py.",
     "", "waypoints:"]
for n, (x, y), alt, spd in PTS:
    W += [f"  {n}:", '    type: "Turning Point"', '    action: "Turning Point"', f"    alt: {alt}", '    alt_type: "BARO"',
          f"    speed: {spd}", '    speed_type: "TAS"', f"    x: {round(x)}", f"    y: {round(y)}", f'    name: "{n}"']
W += ["", "settings:"]
for plan, (cat, side, pts) in PLANS.items():
    W += [f"  {plan}:", f'    category: "{cat}"', f'    coalition: "{side}"', "    waypoints:"] + [f'      {p}: "{p}"' for p in pts]
(ROOT / "src/waypoints.yaml").write_text("\n".join(W) + "\n", encoding="utf-8")
print("presets.yaml, versions.yaml, waypoints.yaml écrits")
