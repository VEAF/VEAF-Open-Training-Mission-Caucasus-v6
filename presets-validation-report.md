# Rapport de validation des fréquences radio

Généré le : 2026-09-29  
Fichier presets : `D:\dev\_VEAF\VEAF-Open-Training-Mission-Caucasus-v6\src\presets.yaml`  
Mission : `D:\dev\_VEAF\VEAF-Open-Training-Mission-Caucasus-v6\VEAF_OpenTraining_Caucasus_ICAO_UGTB_20260929.miz`

## ℹ️ Hors plage — retirées de la radio injectée (DCS les stockerait mais les ignorerait)

*1 type d'appareil concerné.*

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
| 11 | Sochi | 270.1 |  | radio_2 |
| 12 | Gudauta | 270.2 |  | radio_2 |
| 13 | Batumi | 270.3 |  | radio_2 |
| 14 | Kobuleti | 270.4 |  | radio_2 |
| 15 | Kutaisi | 270.5 |  | radio_2 |
| 16 | Nalchik | 270.6 |  | radio_2 |
| 17 | Tbilisi | 270.7 |  | radio_2 |
| 18 | Vaziani | 270.8 |  | radio_2 |
| 19 | Beslan | 270.9 |  | radio_2 |
| 20 | Archer | 360.0 |  | radio_2 |
| 2 | AWACS Rouge (A-50) | 260.0 |  | radio_2 |
| 3 | Tanker Rouge (Il-78M) | 261.0 |  | radio_2 |
| 4 | AWACS Arene Rouge (A-50) | 281.0 |  | radio_2 |
| 5 | Maykop | 275.1 |  | radio_2 |
| 6 | Krasnodar | 275.2 |  | radio_2 |
| 7 | MinVody | 275.3 |  | radio_2 |
| 8 | Mozdok | 275.4 |  | radio_2 |
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
