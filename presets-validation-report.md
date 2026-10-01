# Rapport de validation des fréquences radio

Généré le : 2026-10-01  
Fichier presets : `D:\dev\_VEAF\VEAF-Open-Training-Mission-Caucasus-v6\src\presets.yaml`  
Mission : `D:\dev\_VEAF\VEAF-Open-Training-Mission-Caucasus-v6\VEAF_OpenTraining_Caucasus_ICAO_UGTB_20261001.miz`

## ℹ️ Hors plage — retirées de la radio injectée (DCS les stockerait mais les ignorerait)

*2 types d'appareil concernés.*

### M-2000C
Groupes : `Arène - M-2000C - FOX1 - bleu`, `M-2000C Template`, `Arène - M-2000C - FOX1 - rouge`, `M-2000C Template Red`  
Plages valides : 225.0–400.0 MHz (AM/FM), 118.0–140.0 MHz (AM/FM), 225.0–400.0 MHz (AM/FM)

| Canal | Titre | Fréquence (MHz) | Collection | Radio |
|---------|-------|-----------------|------------|-------|
| 10 | Beslan | 141.0 |  | radio_2 |

**Pour masquer :** ajouter dans `presets.yaml` :
```yaml
presets_assignments:
  blue:
    plane:
      M-2000C: none
```

### TF-51D
Groupes : `TF-51D Template`, `TF-51D Template Red`  
Plages valides : 38.0–156.0 MHz (AM/FM), 100.0–200.0 MHz (AM/FM)

| Canal | Titre | Fréquence (MHz) | Collection | Radio |
|---------|-------|-----------------|------------|-------|
| 1 | Guard | 243.0 |  | radio_2 |
| 2 | Magic 1 (AWACS) | 265.0 |  | radio_2 |
| 3 | Overlord 1 (AWACS) | 266.0 |  | radio_2 |
| 4 | Arco 1 / perche / 51Y | 251.0 |  | radio_2 |
| 5 | Texaco 1 / panier / 52Y | 252.0 |  | radio_2 |
| 6 | Shell 1 / panier / 53Y | 253.0 |  | radio_2 |
| 7 | Shell 2 / perche / 54Y | 254.0 |  | radio_2 |
| 8 | CVN-74 Stennis / 10X | 225.0 |  | radio_2 |
| 9 | LHA-1 Tarawa / 11X | 226.0 |  | radio_2 |
| 10 | Darkstar 1 (AWACS arene) | 280.0 |  | radio_2 |
| 11 | Sochi-Adler | 256.0 |  | radio_2 |
| 12 | Gudauta | 259.0 |  | radio_2 |
| 13 | Batumi / 16X | 260.0 |  | radio_2 |
| 14 | Kobuleti / 67X | 262.0 |  | radio_2 |
| 15 | Kutaisi / 44X | 263.0 |  | radio_2 |
| 16 | Nalchik | 265.0 |  | radio_2 |
| 17 | Tbilisi-Lochini / 25X | 267.0 |  | radio_2 |
| 18 | Vaziani / 22X | 269.0 |  | radio_2 |
| 19 | Beslan | 270.0 |  | radio_2 |
| 20 | Archer | 360.0 |  | radio_2 |
| 2 | AWACS Rouge (A-50) | 260.0 |  | radio_2 |
| 3 | Tanker Rouge (Il-78M) | 261.0 |  | radio_2 |
| 4 | AWACS Arene Rouge (A-50) | 281.0 |  | radio_2 |
| 5 | Maykop-Khanskaya | 254.0 |  | radio_2 |
| 6 | Krasnodar-Pashkovsky | 257.0 |  | radio_2 |
| 7 | Mineralnye Vody | 264.0 |  | radio_2 |
| 8 | Mozdok | 266.0 |  | radio_2 |
| 9 | Rouge-1 | 380.0 |  | radio_2 |
| 10 | Rouge-2 | 380.1 |  | radio_2 |
| 11 | Rouge-3 | 380.2 |  | radio_2 |
| 12 | Rouge-4 | 380.3 |  | radio_2 |

**Pour masquer :** ajouter dans `presets.yaml` :
```yaml
presets_assignments:
  blue:
    plane:
      TF-51D: none
```
