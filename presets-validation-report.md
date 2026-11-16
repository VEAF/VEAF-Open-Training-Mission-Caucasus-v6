# Rapport de validation des fréquences radio

Fichier presets : `src/presets.yaml`  
Mission : `VEAF_OpenTraining_Caucasus_ICAO_UGTB`

## ℹ️ Hors plage — retirées de la radio injectée (DCS les stockerait mais les ignorerait)

*2 types d'appareil concernés.*

### M-2000C
Groupes : `Arène - M-2000C - FOX1 - bleu`, `M-2000C Template`, `Arène - M-2000C - FOX1 - rouge`, `M-2000C Template Red`  
Plages valides : 225.0–400.0 MHz (AM/FM), 118.0–140.0 MHz (AM/FM), 225.0–400.0 MHz (AM/FM)

| Canal | Titre | Fréquence (MHz) | Collection | Radio |
|---------|-------|-----------------|------------|-------|
| 9 | Beslan | 141.0 |  | radio_2 |

**Rien à faire :** les canaux à portée restent sur les radios de cet avion ; DCS aurait ignoré ceux-ci. Ne passez pas le type à `none` — cela retire tous ses presets.

### TF-51D
Groupes : `TF-51D Template`, `TF-51D Template Red`  
Plages valides : 38.0–156.0 MHz (AM/FM), 100.0–200.0 MHz (AM/FM)

| Canal | Titre | Fréquence (MHz) | Collection | Radio |
|---------|-------|-----------------|------------|-------|
| 1 | Magic 1 (AWACS) | 285.0 |  | radio_2 |
| 1 | AWACS Rouge (A-50) | 296.0 |  | radio_2 |

**Rien à faire :** les canaux à portée restent sur les radios de cet avion ; DCS aurait ignoré ceux-ci. Ne passez pas le type à `none` — cela retire tous ses presets.

## ⚠️ AWACS et ravitailleurs qu'aucun preset n'atteint — ajoutez leur canal dans src/presets.yaml

| Groupe | Tâche | Fréquence (MHz) | Coalition |
|--------|------|-----------------|-----------|
| `CVN-74 Stennis S3B-Tanker` | Refueling | 290.9 | blue |
| `Darkstar 1` | AWACS | 280.0 | blue |
| `AWACS Arène Rouge` | AWACS | 281.0 | red |
