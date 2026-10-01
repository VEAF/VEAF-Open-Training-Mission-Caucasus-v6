# Points ouverts — Open Training Caucasus v6

Ce qui reste à faire sur cette mission, avec ce qui a été mesuré pour chaque point. Les retours qui
concernent les **outils** et non la mission partent dans le backlog de VMCT et sont listés en bas.

## Relevés en vol sur private1, le 29/09/2026

Session live, six pilotes, sur la mission construite le jour même. Aucun n'est corrigé.

### 1. Les étiquettes des dessins tactiques sont illisibles sur la carte F10

Les couleurs viennent de `tools/gen_15_dessins.py`. 28 des 38 dessins sont des `textbox`, donc
c'est le gros du sujet. Reste à instruire : couleur du texte, couleur de fond, taille.

### 2. Les zones de combat ne sont pas dessinées

Mesuré : nos 38 dessins F10 sont 10 `line` + 28 `textbox`, **aucun polygone**. Les zones de combat
*et* les cercles de QRA ne sont que des étiquettes posées au centre, sans contour — alors que la
carte du briefing, elle, les dessine. GermanyCW-v6 a **12 `primitiveType = "Polygon"`** dans ses
dessins ; reste à voir quels objets y sont cerclés.

Les points 1 et 2 touchent le même fichier et se corrigent ensemble.

### 3. Les fréquences des préréglages ne correspondent pas toujours à celle que DCS affiche (vue F10)

Non instruit. Sources à regarder : `src/presets.yaml`, l'injecteur de préréglages de VMCT, et la
fréquence que DCS montre pour l'appareil. À ne pas confondre avec `presets-validation-report.md`,
qui signale autre chose (le TF-51D n'a pas de radio UHF, ses canaux UHF sont donc retirés).

### 4. La zone d'entraînement SEAD est trop à l'écart

Taman est à `BULLSEYE 291/261` et à **243 nm** du ravitailleur le plus proche (Arco 1). À comparer
aux deux autres familles : Kobuleti est à 51 nm d'un ravitailleur, Akhalkalaki à 38 nm — Taman est
cinq fois plus loin.

Le placement « SEAD en secteur Ouest (Taman) » avait été retenu le 28/09 pour le mettre hors QRA ;
l'écart au ravitailleur n'avait pas été mesuré à ce moment-là. **Deux issues, et elles ne donnent
pas la même mission** : rapprocher la zone (elle perd le « hors QRA » qui justifiait Taman), ou
poser un ravitailleur dans le secteur Ouest. À trancher avant de coder.

## Côté serveurs, avant la prochaine session

**Le hook `VEAF-Server-hook.lua` doit être redéployé.** Mesuré le 01/10/2026 sur les six instances
(`foothold1/2`, `private1/2`, `public1/2`) : toutes tournent avec le hook du **10/08/2026**, sans
`onGameEvent` ni l'envoi du niveau au changement de slot. Or c'est par là que passe la moitié du
correctif du lot VMCT `FIX-SECU-VERB-AND-LOG-NOISE` (ticket 01) : sans lui, un pilote listé ne
retrouve son niveau qu'à sa première commande de chat, pas en prenant son slot. Le hook n'est pas
livré dans `published/` — il se prend dans le dépôt VMCT, `src/scripts/hooks/`.

C'est aussi la condition de la vérification en jeu ci-dessous.

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
