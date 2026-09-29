# Retours pour VMCT — construction de l'OT Caucasus v6 (28/09/2026)

Tenu au fil de la construction. Chaque entrée : quoi, où, comment je l'ai vu, ce que j'ai fait.

1. **Le serveur MCP d'une session ouverte avant un merge garde l'ancien code.** Le serveur
   `veaf-mission-mcp` (lancé par `poetry -C <VMCT> run`) a démarré avant le merge de #1022 :
   `describe_action add_carrier_group` échoue. Contourné en appelant le catalogue en Python
   in-process sur `develop` (`tools/mcp.py`, qui refuse de tourner si le checkout VMCT n'est pas
   sur `develop`).
2. **`scaffold_mission` installe la release publiée (6.25.0), pas `develop`.** Les outils du dossier
   n'ont donc ni `veaf.Diagnostics` (#1021) ni le lot #1022. Le build se fera avec des outils
   reconstruits depuis `develop`.
3. **`add_air_group` attribue les familles d'indicatif dans l'ordre de création, pas d'après le
   nom du groupe.** Le groupe « Arco 1 » a reçu Texaco11, « Texaco 1 » Arco11, « Magic 1 »
   Overlord11. Le prompt exige un nom partout (groupe = indicatif). Corrigé par
   `set_unit_properties` (lot `03b-indicatifs.json`).
4. **`set_unit_properties callsign.name` est écrit tel quel.** Passer `name: "Arco"` écrit
   « Arco », alors que DCS stocke « Arco11 » (famille + vol + numéro). Il a fallu passer la forme
   complète. L'action pourrait la composer, ou refuser une forme incomplète.
5. **`combat_missions:` ne porte ni objectifs ni niveau des pilotes** (`lua_config_generator.py`,
   `_emit_combat_mission`). Les missions scénarisées avec objectifs passent par
   `src/scripts/mission-script.lua`.
6. **`edit_route` n'a pas de tâche FAC.** Un drone de guidage laser est monté comme sur
   GermanyCW-v6 : tâche de groupe `AFAC`, orbite en cercle, et clés `jtac` / `freq` / `mod` dans
   `modules.ASSETS`.
7. **`add_sound` sauvegarde `dictionary` et `mapResource` à côté du fichier, dans
   `src/mission/l10n/DEFAULT/`** (`dictionary.20260928-211647`…), alors que les autres actions
   sauvegardent dans `.veaf-backups/`. Ces copies partiraient dans le `.miz` au build. Déplacées à la
   main dans `.veaf-backups/l10n-DEFAULT/`.
8. **Le catalogue de terrain dégagé du Caucase ne couvre presque que les abords des aérodromes.**
   `add_group` / `create_combat_zone` ont averti « no clear-ground catalogue covers this place » pour
   la grande majorité des groupes posés hors des bases.
9. **Aucun contrôle de la nature du sol à la construction** (terre ou eau). Pour la péninsule de Taman,
   criblée de lagunes, je l'ai vérifié par le géocodage inverse d'OSM (aucune étendue d'eau aux quatre
   points), ce qui ne vaut pas une sonde DCS.
10. **`create_qra` remplit `simple_groups` avec tous les groupes, même quand `groups_by_enemy_count`
    est donné.** Sans effet en jeu (le niveau 1 de la réponse graduée réécrit ce que `addGroup` y a mis,
    `veafQraCore.lua:276-313`), mais trompeur à la relecture. Mis à `[]` à la main, comme GermanyCW-v6.
11. **Le build lit `src/presets.yaml` dans le mauvais encodage : les accents des titres de canaux
    sortent en « arÃ¨ne » dans le rapport de validation ET dans les planches de kneeboard des presets**
    (vu sur `KNEEBOARD/FA-18C_hornet/IMAGES/presets-blue.png`). GermanyCW-v6 doit l'avoir aussi
    (« Büchel », « Nörvenich »). Contourné ici par des titres sans accents.
12. **`${METAR}` reste tel quel dans le briefing des variantes à météo manuelle** (« dégagé ») : le build
    l'annonce (« n'a pas pu être renseignée »). Le pilote lit « METAR : ${METAR} ». Il faudrait
    l'effacer, ou écrire la météo manuelle à sa place.
13. **Le `.gitignore` du gabarit ne contient pas `.veaf-backups/`**, où toutes les actions MCP
    sauvegardent : un premier `git add .` y enverrait des dizaines de copies de la mission. Ajouté à la main.
14. **Aucune action MCP pour l'image de briefing** (`pictureFileNameB/R/N` + clé `mapResource`). Faite par
    script (`tools/set_briefing_picture.py`), comme sur GermanyCW-v6. `add_sound` embarque un fichier et le
    déclare dans `mapResource`, mais n'accepte que `.ogg` / `.wav`.
15. **`save_folder_mission` ne réécrit pas `mapResource`** : une clé ajoutée à `map_resource_content` est
    perdue en silence. Écrit à la main, avec la même sérialisation que `add_sound`.
16. **Pas de générateur de carte du briefing dans les outils** : chaque mission refait le sien
    (`tools/gen_map.py` ici, adapté de GermanyCW-v6). Voir le lot VMCT proposé.
17. **Le correctif `shape_name` de #1023 ne vaut que pour les poses à venir** : les 42 statiques posées
    avant lui n'en avaient pas, et seule la validation le signale. Complétées par `tools/fix_shape_names.py`
    (même source que l'action, `get_unit_shape_name`). Une action ou une option de `validate_mission` qui
    répare éviterait à chaque mission existante d'écrire ce script.
