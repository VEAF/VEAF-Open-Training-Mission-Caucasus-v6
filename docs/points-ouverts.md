# Points ouverts — Open Training Caucasus v6

Ce qui reste à faire sur cette mission, avec ce qui a été mesuré pour chaque point. Les retours qui
concernent les **outils** et non la mission partent dans le backlog de VMCT et sont listés en bas.

## Relevés en vol sur private1, le 29/09/2026

Session live, six pilotes, sur la mission construite le jour même. Aucun n'est corrigé.

### 1. Étiquettes des dessins tactiques illisibles sur la carte F10 — corrigé le 01/10/2026

Les étiquettes sortaient sans `fill_color`, donc avec le fond par défaut de l'action —
`0x00000080`, noir à 50 % — sous un texte de la couleur du camp, toutes sombres. Fond blanc à 90 %
et taille 14 désormais (`tools/gen_15_dessins.py`).

### 2. Zones de combat et QRA sans contour — corrigé le 01/10/2026

Les 38 dessins étaient 10 lignes et 28 étiquettes, aucun polygone : les zones n'étaient que des
noms posés au centre. Chacune porte maintenant son cercle au rayon réel — 16 zones de combat,
4 zones d'entraînement, 4 QRA — sur la couche de son camp.

### 3. Fréquences des préréglages — passé chez VMCT

Le plan de la mission invente une série 270.x là où les tours DCS sont ailleurs (Batumi 260.0,
Krasnodar 251.0) : 10 bases sur 13 fausses. Mesuré sur 56 `presets.yaml` du poste, les missions
Foothold et l'Open Training v5 sont justes — c'est un défaut d'autorité de la méthode v6. Traité
dans le lot VMCT `FEAT-AIRFIELD-CHANNELS-FROM-DCS` : les collections de canaux seront générées
depuis le référentiel, et un outil choisira les bases d'une mission qui méritent un canal. **Cette
mission devra ensuite reprendre les vraies fréquences.**

Huit canaux tactiques VEAF tombent par ailleurs sur de vraies tours du Caucase (Arco 1 sur
Krasnodar, Magic 1 sur Nalchik) ; noté dans le PRD du lot, pas encore arbitré.

### 4. Zone d'entraînement SEAD trop à l'écart — corrigé le 01/10/2026

Taman était à 24 minutes de vol de la base bleue la plus proche, et son ravitailleur à 243 nm. Ce
n'était pas une négligence : le SA-10 du niveau difficile porte à 65 nm, et §4.7 interdit qu'un SAM
de zone atteigne une base amie, une piste de ravitailleur ou une autre zone d'entraînement — d'où
« loin de tout ce qui est bleu ». En Géorgie, aucun terrain plat ne satisfait les deux.

Décision de David : une zone d'entraînement **moins violente, sans SA-10**, la carte en gardant
trois ailleurs (défenses de Krasnodar et de Stavropol, zone de combat 13 sur Maykop). Le SA-11
devient la plus grosse menace (18,9 nm), ce qui permet la **plaine de Gori**, vallée du Kura :
40 nm de Tbilissi, **6 minutes de vol**, ravitailleur Shell 1 à 24 nm. `check_portees.py` repasse
à OK §4.7.

**Reste à vérifier en jeu** : le terrain des six groupes déplacés. L'action le dit elle-même —
*« the destination's surface was not checked: DCS terrain is not available design-time »* — et le
catalogue de terrain dégagé ne couvre que les abords des aérodromes. Le fond OSM montre une plaine
agricole sans relief ni eau, mais ce n'est pas une mesure.

## Côté serveurs

**Hook `VEAF-Server-hook.lua` installé le 01/10/2026** sur les six instances (`foothold1/2`,
`private1/2`, `public1/2`) : v2.7.1, 33 814 o, celui du commit VMCT `cf9958e9`. Elles tournaient
toutes celui du 10/08, sans `onGameEvent` ni l'envoi du niveau au changement de slot — c'est par là
que passe la moitié du correctif du lot `FIX-SECU-VERB-AND-LOG-NOISE` (ticket 01). Les anciens sont
gardés dans `Saved Games\_hook-backup-20261001-091118\`.

**Reste à faire : redémarrer chaque instance.** DCS lit ses hooks au démarrage ; jusque-là les
serveurs tournent encore sur l'ancien, et un pilote listé ne retrouve son niveau qu'à sa première
commande de chat, pas en prenant son slot.

Le hook n'est pas livré dans `published/` : il se prend dans le dépôt VMCT, `src/scripts/Hooks/`
(majuscule à `Hooks`).

## Vérifications en jeu encore dues

- Le panneau d'une zone de combat annonce-t-il enfin ses cibles **statiques** (Kobuleti et
  Akhalkalaki niveau facile) ? C'est le correctif VMCT du 29/09 que la mission embarque.
- Le briefing DCS enchaîne-t-il bien la carte du théâtre puis les huit zooms, une seule fois
  chacun ? Vérifié dans le `.miz` et dans le Lua de DCS, jamais à l'écran.
- Les balises MH01-03 et SOS, relevables au radiogoniomètre (il faut un hélicoptère sur la zone de
  sauvetage).
- Un pilote listé dans `veaf-pilots.txt`, resté connecté pendant un rechargement de mission, clique
  une commande `+` **sans taper aucun verbe** (lot VMCT `FIX-SECU-VERB-AND-LOG-NOISE`, ticket 01).
  Demande le hook redéployé.

## Parti chez VMCT

Lot `FIX-SECU-VERB-AND-LOG-NOISE` (VEAF-Mission-Creation-Tools, `5e1d0120`), cinq tickets de la
même session : le niveau d'un pilote listé n'atteint pas le menu radio et `/secu login` promet ce
qu'il ne donne plus, une faute de frappe dans le chat lève une erreur Lua, le watchdog des zones
journalise son inventaire en INFO, une déconnexion normale produit une ERROR, et le `+` d'une
commande sécurisée ne disparaît jamais.

Les retours plus anciens, sur ce que les outils n'ont pas su faire pendant la construction, sont
dans `tools/retours-vmct.md`.
