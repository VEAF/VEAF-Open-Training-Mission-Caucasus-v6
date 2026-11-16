"""Lot 06e : un vrai niveau difficile pour le range hélicoptères de Kobuleti (FIX-OPEN-TRAINING-PILOT-FEEDBACK, ticket 01).

Retour de David après vol (15/11/2026) : le « difficile » n'était qu'un moyen, sans aucun système à guidage radar.
Décision D1 : le moyen prend le contenu de l'ancien difficile (DCA légère + SA-13, SA-9 et MANPADS à guidage
infrarouge), le difficile y ajoute deux systèmes courte portée à guidage radar tirés au sort parmi SA-15 Tor,
SA-19 Tunguska et SA-8 Osa.

  - les groupes `combatZone_Kobuleti_Hard-sr-*` passent au niveau moyen (`…_Medium-sr-*`), sans bouger ;
  - trois faux porteurs `rad-*` (`#spawngroup="rad" #spawncount=2`) au niveau difficile, au sud des cibles : la base
    de Kobuleti est à 12 km au 027°, hors de portée du Tor (12 km) posé au 180°, Batumi à 31 km au 205°.
    add_group les recale sur le terrain dégagé du catalogue Caucasus ; check_portees.py contrôle le résultat.

Ne s'importe pas gen_06_entrainement.py : il écrit son lot à l'import.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from lib import RED, Batch, cmd_unit, off  # noqa: E402

K = (-328279, 631220)   # centre du range, gen_06_entrainement.py
RADAR = [("-sa15", "Tor 9A331", 180, 2000), ("-sa19", "2S6 Tunguska", 215, 1800), ("-sa8", "Osa 9A33 ln", 145, 2000)]

b = Batch()
for i in range(1, 6):
    b.act("set_group_properties", group_name=f"combatZone_Kobuleti_Hard-sr-{i}",
          new_name=f"combatZone_Kobuleti_Medium-sr-{i}", acknowledge_conventions=True)   # voulu : le moyen capte
for i, (alias, carrier, brg, dist) in enumerate(RADAR, 1):
    p = off(K, brg, dist)
    b.act("add_group", **RED, category="vehicle", name=f"rad-{i}", position={"x": p[0], "y": p[1]},
          for_combat_zone="combatZone_Kobuleti_Hard",
          units=[cmd_unit(alias, carrier, f"KobH-rad-{i}", '#spawngroup="rad" #spawncount=2')])
b.save("06e-kobuleti-radar.json")
