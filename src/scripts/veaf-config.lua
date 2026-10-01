---------------------------------------------------------------------------------------------------------------------------------------------
-- Généré par veaf-tools build depuis mission.yaml
-- Ne pas éditer manuellement.
-- Relancez 'veaf-tools build' ou 'veaf-tools generate-config' pour régénérer.
---------------------------------------------------------------------------------------------------------------------------------------------

-- ── Mission identity ─────────────────────────────────────────────────────────
veaf.config.MISSION_NAME = "VEAF_OpenTraining_Caucasus_ICAO_UGTB"
veaf.config.era = veaf.ERA.MODERN
veaf.silenceAtcOnAllAirbases()
veaf.HideNamesFromSpawnedGroups = true

veaf.config.language = "fr"

-- ── Security ─────────────────────────────────────────────────────────────────
veaf.SecurityDisabled = false

-- ── Global log level ─────────────────────────────────────────────────────────
veaf.ForcedLogLevel = "info"

-- ── Module settings ──────────────────────────────────────────────────────────
veaf.Diagnostics = false

-- ── CTLD 2 ───────────────────────────────────────────────────────────────────
-- Configuration lives in ctld-config.yaml (edit it with ctld-tools); this only starts it.
if ctld then
    veaf.ctld_initialize()
end

-- ── Module configuration + initialization ────────────────────────────────────

-- ── Core ──

if veafSecurity then
    veafSecurity.initialize()
end

if veafRadio then
    veafRadio.initialize(true)
end

if veafShortcuts then
    veafShortcuts.initialize()
end

if veafNamedPoints then
    veafNamedPoints.initialize({})
end

if veafSpawn then
    veafSpawn.initialize()
end

-- ── Combat ──

if veafCarrierOperations then
    veafCarrierOperations.initialize(true)
end

if veafCasMission then
    veafCasMission.initialize()
end

if veafTransportMission then
    veafTransportMission.initialize()
end

if veafCombatMission then
    veafCombatMission.initialize()
    veafCombatMission.addCapMission("CAP Ouest - Tu-22M3 - FL300", "CAP Ouest - Tu-22M3 - FL300", "Deux Tu-22M3 : bombardier à intercepter. Hippodrome au FL300 centré sur BULLSEYE 252/256.", false, true)
    veafCombatMission.addCapMission("CAP Ouest - Tu-95 - FL200", "CAP Ouest - Tu-95 - FL200", "Deux Tu-95 : bombardier lent à intercepter. Hippodrome au FL200 centré sur BULLSEYE 252/256.", false, true)
    veafCombatMission.addCapMission("CAP Ouest - Su-27 - FL300", "CAP Ouest - Su-27 - FL300", "Paire de Su-27 armés Fox 1 (guidage radar semi-actif). Hippodrome au FL300 centré sur BULLSEYE 252/256.", false, true)
    veafCombatMission.addCapMission("CAP Ouest - MiG-29S - FL300", "CAP Ouest - MiG-29S - FL300", "Paire de MiG-29S armés Fox 3. Hippodrome au FL300 centré sur BULLSEYE 252/256.", false, true)
    veafCombatMission.addCapMission("CAP Ouest - MiG-31 - FL300", "CAP Ouest - MiG-31 - FL300", "Paire de MiG-31 : intercepteur haut et rapide, Fox 3 longue portée. Hippodrome au FL300 centré sur BULLSEYE 252/255.", false, true)
    veafCombatMission.addCapMission("Khashuri - L-39C - FL100", "Khashuri - L-39C - FL100", "Paire de L-39C lents cap au nord, vers Khashuri : cible d'interception facile. Hippodrome au FL100 centré sur BULLSEYE 166/110.", false, true)
    veafCombatMission.addCapMission("CAP F-16C - Gudauta - FL250", "CAP F-16C - Gudauta - FL250", "Paire de F-16C armés Fox 3 : opposition pour les joueurs rouges. Hippodrome au FL250 centré sur BULLSEYE 251/51.", false, true)
    veafCombatMission.addCapMission("CAP F-15C - Beslan - FL300", "CAP F-15C - Beslan - FL300", "Paire de F-15C armés Fox 3 : opposition pour les joueurs rouges. Hippodrome au FL300 centré sur BULLSEYE 097/88.", false, true)
end

if veafCombatZone then
    veafCombatZone.AddZone(
        VeafCombatZone:new()
        :setMissionEditorZoneName("combatZone_Kobuleti_Easy")
        :setFriendlyName("Kobuleti - hélicoptères - facile")
        :setRadioGroupName("Entraînement hélicoptères")
        :setBriefing([[Range de Kobuleti, 6 nm au sud-ouest de la base. Cibles inertes (statiques) : blindés, camions, missiles SCUD, bâtiments. Aucune défense. BULLSEYE 191/96. Ravitailleur le plus proche : Texaco 1 (TACAN 52Y, 252.0 MHz, FL220) à 51 nm.]])
        :setTraining(true)
        :initialize()
    )
    veafCombatZone.AddZone(
        VeafCombatZone:new()
        :setMissionEditorZoneName("combatZone_Kobuleti_Medium")
        :setFriendlyName("Kobuleti - hélicoptères - moyen")
        :setRadioGroupName("Entraînement hélicoptères")
        :setBriefing([[Range de Kobuleti, cibles du niveau facile plus DCA légère : deux pièces tirées parmi quatre (ZU-23, Shilka). BULLSEYE 191/96. Ravitailleur le plus proche : Texaco 1 (TACAN 52Y, 252.0 MHz, FL220) à 51 nm.]])
        :setTraining(true)
        :initialize()
    )
    veafCombatZone.AddZone(
        VeafCombatZone:new()
        :setMissionEditorZoneName("combatZone_Kobuleti_Hard")
        :setFriendlyName("Kobuleti - hélicoptères - difficile")
        :setRadioGroupName("Entraînement hélicoptères")
        :setBriefing([[Range de Kobuleti, niveau moyen plus une défense courte portée à guidage infrarouge : trois systèmes tirés parmi SA-13, SA-9 et MANPADS. BULLSEYE 191/96. Ravitailleur le plus proche : Texaco 1 (TACAN 52Y, 252.0 MHz, FL220) à 51 nm.]])
        :setTraining(true)
        :initialize()
    )
    veafCombatZone.AddZone(
        VeafCombatZone:new()
        :setMissionEditorZoneName("combatZone_Akhalkalaki_Easy")
        :setFriendlyName("Akhalkalaki - attaque - facile")
        :setRadioGroupName("Entraînement attaque")
        :setBriefing([[Plateau d'Akhalkalaki, sud de la Géorgie. Colonne blindée à l'arrêt, cibles inertes (statiques). Aucune défense. BULLSEYE 150/128. Ravitailleur le plus proche : Shell 1 (TACAN 53Y, 253.0 MHz, FL200) à 38 nm.]])
        :setTraining(true)
        :initialize()
    )
    veafCombatZone.AddZone(
        VeafCombatZone:new()
        :setMissionEditorZoneName("combatZone_Akhalkalaki_Medium")
        :setFriendlyName("Akhalkalaki - attaque - moyen")
        :setRadioGroupName("Entraînement attaque")
        :setBriefing([[Plateau d'Akhalkalaki, cibles du niveau facile plus deux compagnies blindées vivantes et une DCA légère (deux pièces tirées parmi quatre). BULLSEYE 150/128. Ravitailleur le plus proche : Shell 1 (TACAN 53Y, 253.0 MHz, FL200) à 38 nm.]])
        :setTraining(true)
        :initialize()
    )
    veafCombatZone.AddZone(
        VeafCombatZone:new()
        :setMissionEditorZoneName("combatZone_Akhalkalaki_Hard")
        :setFriendlyName("Akhalkalaki - attaque - difficile")
        :setRadioGroupName("Entraînement attaque")
        :setBriefing([[Plateau d'Akhalkalaki, niveau moyen plus un bataillon blindé et une défense courte portée réaliste : deux systèmes tirés parmi SA-8, SA-15, SA-13 et SA-19, plus des MANPADS. BULLSEYE 150/128. Ravitailleur le plus proche : Shell 1 (TACAN 53Y, 253.0 MHz, FL200) à 38 nm.]])
        :setTraining(true)
        :initialize()
    )
    veafCombatZone.AddZone(
        VeafCombatZone:new()
        :setMissionEditorZoneName("combatZone_Taman_Easy")
        :setFriendlyName("Taman - SEAD - facile")
        :setRadioGroupName("Entraînement SEAD")
        :setBriefing([[Péninsule de Taman, secteur Ouest. Une batterie SA-6 seule, sans radar d'alerte. BULLSEYE 291/261. Ravitailleur le plus proche : Arco 1 (TACAN 51Y, 251.0 MHz, FL180) à 243 nm.]])
        :setTraining(true)
        :initialize()
    )
    veafCombatZone.AddZone(
        VeafCombatZone:new()
        :setMissionEditorZoneName("combatZone_Taman_Medium")
        :setFriendlyName("Taman - SEAD - moyen")
        :setRadioGroupName("Entraînement SEAD")
        :setBriefing([[Péninsule de Taman, le SA-6 du niveau facile protégé par une défense courte portée (SA-15, SA-8, Shilka). BULLSEYE 291/261. Ravitailleur le plus proche : Arco 1 (TACAN 51Y, 251.0 MHz, FL180) à 243 nm.]])
        :setTraining(true)
        :initialize()
    )
    veafCombatZone.AddZone(
        VeafCombatZone:new()
        :setMissionEditorZoneName("combatZone_Taman_Hard")
        :setFriendlyName("Taman - SEAD - difficile")
        :setRadioGroupName("Entraînement SEAD")
        :setBriefing([[Péninsule de Taman, réseau intégré complet sous Skynet : SA-10 longue portée, SA-11, le SA-6 et la courte portée des niveaux inférieurs, et un radar d'alerte 55G6. BULLSEYE 291/261. Ravitailleur le plus proche : Arco 1 (TACAN 51Y, 251.0 MHz, FL180) à 243 nm.]])
        :setTraining(true)
        :initialize()
    )
    veafCombatZone.AddZone(
        VeafCombatZone:new()
        :setMissionEditorZoneName("combatZone_MountainHike")
        :setFriendlyName("Mountain hike - équipage abattu")
        :setRadioGroupName("Entraînement recherche")
        :setBriefing([[Un Mi-8 ami s'est écrasé en montagne, 45 nm au nord-est de Soukhoumi, près de la frontière russe. Décollez du FARP Kodori, suivez la vallée vers le nord-est et localisez l'épave. Balises FM sur l'itinéraire : MH01 31.0, MH02 32.0, MH03 33.0 ; l'équipage émet un SOS sur 34.0 FM. BULLSEYE 250/21.]])
        :setCompletable(false)
        :setTraining(true)
        :initialize()
    )
    veafCombatZone.AddZone(
        VeafCombatZone:new()
        :setMissionEditorZoneName("combatZone_Beslan")
        :setFriendlyName("Bataille de Beslan")
        :setRadioGroupName("Front")
        :setBriefing([[Bataille blindée au nord de Beslan : trois compagnies de BTR-80 rouges montent à l'assaut des Abrams bleus, deux groupes blindés en renfort. Détruisez les blindés rouges ; ne tirez pas sur les Abrams. Défense : SA-8 (un des deux sites), MANPADS, Shilka. Drone Reaper 1 au-dessus (laser 1688). BULLSEYE 078/101. Ravitailleur le plus proche : Shell 1 (TACAN 53Y, 253.0 MHz, FL200) à 99 nm.]])
        :setTraining(false)
        :initialize()
    )
    veafCombatZone.AddZone(
        VeafCombatZone:new()
        :setMissionEditorZoneName("combatZone_Terek")
        :setFriendlyName("Parc logistique de Terek")
        :setRadioGroupName("Front")
        :setBriefing([[Le parc logistique de Terek ravitaille l'offensive rouge sur Beslan. Détruisez les camions. Défense légère : DCA de convoi, une chance sur deux d'infanterie mécanisée, MANPADS. BULLSEYE 075/84. Ravitailleur le plus proche : Shell 1 (TACAN 53Y, 253.0 MHz, FL200) à 96 nm.]])
        :setTraining(false)
        :initialize()
    )
    veafCombatZone.AddZone(
        VeafCombatZone:new()
        :setMissionEditorZoneName("combatZone_Lazarevskoye")
        :setFriendlyName("Front côtier de Lazarevskoye")
        :setRadioGroupName("Front")
        :setBriefing([[Le front de la côte, au nord-ouest de Sochi : deux groupes blindés et une batterie de lance-roquettes BM-21 en appui. Détruisez les blindés et les BM-21. Défense : SA-13, Shilka. BULLSEYE 279/139. Ravitailleur le plus proche : Texaco 1 (TACAN 52Y, 252.0 MHz, FL220) à 117 nm.]])
        :setTraining(false)
        :initialize()
    )
    veafCombatZone.AddZone(
        VeafCombatZone:new()
        :setMissionEditorZoneName("combatZone_Psebay_SAM")
        :setFriendlyName("Sites SAM de Psebay")
        :setRadioGroupName("SEAD")
        :setBriefing([[Les sites SAM qui couvrent l'usine de Psebay : un SA-2, un SA-6, et un SA-15 (un des deux sites), plus de la DCA. Neutralisez les radars avant la frappe de l'usine. BULLSEYE 298/89. Ravitailleur le plus proche : Texaco 1 (TACAN 52Y, 252.0 MHz, FL220) à 97 nm.]])
        :setTraining(false)
        :initialize()
    )
    veafCombatZone.AddZone(
        VeafCombatZone:new()
        :setMissionEditorZoneName("combatZone_Mozdok_SA11")
        :setFriendlyName("Site SA-11 au nord de Mozdok")
        :setRadioGroupName("SEAD")
        :setBriefing([[Une batterie SA-11 isolée au nord de Mozdok, protégée par un SA-15 et de la DCA. Détruisez le radar et les lanceurs du SA-11. BULLSEYE 066/103. Ravitailleur le plus proche : Shell 1 (TACAN 53Y, 253.0 MHz, FL200) à 118 nm.]])
        :setTraining(false)
        :initialize()
    )
    veafCombatZone.AddZone(
        VeafCombatZone:new()
        :setMissionEditorZoneName("combatZone_RoadBlock_KM91")
        :setFriendlyName("Barrage routier KM91")
        :setRadioGroupName("Convois")
        :setBriefing([[Les Russes tiennent un barrage sur la route Batumi - Tbilissi, et un convoi arrive de l'est pour le renforcer. Détruisez les bunkers, les blindés du poste et le convoi. Défense : la Shilka du convoi, MANPADS. BULLSEYE 169/107. Ravitailleur le plus proche : Shell 1 (TACAN 53Y, 253.0 MHz, FL200) à 55 nm.]])
        :setTraining(false)
        :initialize()
    )
    veafCombatZone.AddZone(
        VeafCombatZone:new()
        :setMissionEditorZoneName("combatZone_Convoi_Prokhladny")
        :setFriendlyName("Convoi de secours vers Prokhladny")
        :setRadioGroupName("Convois")
        :setBriefing([[Un convoi blindé part de Mozdok pour secourir la garnison de Prokhladny, par la route. Arrêtez-le avant qu'il arrive. Défense dans la colonne : Shilka et SA-13. BULLSEYE 068/98. Ravitailleur le plus proche : Shell 1 (TACAN 53Y, 253.0 MHz, FL200) à 112 nm.]])
        :setTraining(false)
        :initialize()
    )
    veafCombatZone.AddZone(
        VeafCombatZone:new()
        :setMissionEditorZoneName("combatZone_Convoi_MinVody")
        :setFriendlyName("Convoi Mineralnye Vody - Baksan")
        :setRadioGroupName("Convois")
        :setBriefing([[Un convoi de ravitaillement quitte Mineralnye Vody par la route vers Baksan, derrière le front de Nalchik. Détruisez les camions. Défense : BMP-2 et Shilka dans la colonne. BULLSEYE 024/60. Ravitailleur le plus proche : Texaco 1 (TACAN 52Y, 252.0 MHz, FL220) à 124 nm.]])
        :setTraining(false)
        :initialize()
    )
    veafCombatZone.AddZone(
        VeafCombatZone:new()
        :setMissionEditorZoneName("combatZone_Psebay_Usine")
        :setFriendlyName("Usine d'armes chimiques de Psebay")
        :setRadioGroupName("Frappe")
        :setBriefing([[Cette usine fabrique des armes chimiques pour un groupe terroriste. Détruisez les deux bâtiments de l'usine et le bunker des scientifiques ; le reste est secondaire. Défense : DCA, une chance sur deux d'un SA-15, et les sites SAM voisins (zone « Sites SAM de Psebay »). BULLSEYE 299/87. Ravitailleur le plus proche : Texaco 1 (TACAN 52Y, 252.0 MHz, FL220) à 97 nm.]])
        :setTraining(false)
        :initialize()
    )
    veafCombatZone.AddZone(
        VeafCombatZone:new()
        :setMissionEditorZoneName("combatZone_Prokhladny_Otages")
        :setFriendlyName("Otages à Prokhladny")
        :setRadioGroupName("Frappe")
        :setBriefing([[Des otages sont retenus dans un hôtel fortifié de Prokhladny. Détruisez la caserne et les patrouilles de BTR-80 ; l'hôtel doit rester debout pour l'équipe au sol. Défense : Shilka, SA-9, une chance sur deux d'un SA-8, MANPADS. BULLSEYE 064/75. Ravitailleur le plus proche : Shell 1 (TACAN 53Y, 253.0 MHz, FL200) à 106 nm.]])
        :setTraining(false)
        :initialize()
    )
    veafCombatZone.AddZone(
        VeafCombatZone:new()
        :setMissionEditorZoneName("combatZone_Georgievsk_SCUD")
        :setFriendlyName("Site SCUD de Georgievsk")
        :setRadioGroupName("Frappe")
        :setBriefing([[Quatre lanceurs SCUD en position de tir à l'ouest de Georgievsk. Détruisez les lanceurs. Défense : SA-15, Shilka, MANPADS. BULLSEYE 034/64. Ravitailleur le plus proche : Texaco 1 (TACAN 52Y, 252.0 MHz, FL220) à 129 nm.]])
        :setTraining(false)
        :initialize()
    )
    veafCombatZone.AddZone(
        VeafCombatZone:new()
        :setMissionEditorZoneName("combatZone_Nevinnomyssk_Depot")
        :setFriendlyName("Dépôt logistique de Nevinnomyssk")
        :setRadioGroupName("Frappe")
        :setBriefing([[Le grand dépôt de carburant et de munitions qui alimente le front. Détruisez les réservoirs et les entrepôts. Défense locale : SA-19 et DCA ; attention, le dépôt est sous la couverture permanente du SA-10 de Stavropol. BULLSEYE 339/79. Ravitailleur le plus proche : Texaco 1 (TACAN 52Y, 252.0 MHz, FL220) à 124 nm.]])
        :setTraining(false)
        :initialize()
    )
    veafCombatZone.AddZone(
        VeafCombatZone:new()
        :setMissionEditorZoneName("combatZone_Maykop_Defenses")
        :setFriendlyName("Défenses de la base de Maykop")
        :setRadioGroupName("OCA")
        :setBriefing([[La base de Maykop est défendue par un bataillon SA-10, deux SA-15 tirés parmi quatre sites, quatre pièces de DCA tirées parmi huit, et des blindés. Neutralisez les défenses pour préparer l'assaut. BULLSEYE 302/133. Ravitailleur le plus proche : Texaco 1 (TACAN 52Y, 252.0 MHz, FL220) à 138 nm.]])
        :setTraining(false)
        :initialize()
    )
    veafCombatZone.AddZone(
        VeafCombatZone:new()
        :setMissionEditorZoneName("combatZone_Mozdok_OCA")
        :setFriendlyName("Avions au sol de Mozdok")
        :setRadioGroupName("OCA")
        :setBriefing([[Des bombardiers Tu-22M3, des Su-24M, des Su-25 et un Il-76 sont stationnés sur la base de Mozdok. Détruisez-les au sol. Défense de zone : SA-15, Shilka ; défense permanente de la base : SA-11 et SA-19. BULLSEYE 067/99. Ravitailleur le plus proche : Shell 1 (TACAN 53Y, 253.0 MHz, FL200) à 114 nm.]])
        :setTraining(false)
        :initialize()
    )
    veafCombatZone.AddZone(
        VeafCombatZone:new()
        :setMissionEditorZoneName("combatZone_Antinavire_Cargos")
        :setFriendlyName("Cargos isolés")
        :setRadioGroupName("Antinavire")
        :setBriefing([[Des cargos sans escorte ravitaillent l'ennemi par la mer. Coulez-les. BULLSEYE 253/266. Ravitailleur le plus proche : Arco 1 (TACAN 51Y, 251.0 MHz, FL180) à 179 nm.]])
        :setTraining(false)
        :initialize()
    )
    veafCombatZone.AddZone(
        VeafCombatZone:new()
        :setMissionEditorZoneName("combatZone_Antinavire_Escorte")
        :setFriendlyName("Convoi naval escorté")
        :setRadioGroupName("Antinavire")
        :setBriefing([[Des cargos escortés par des bâtiments de guerre ; une frégate Neustrashimy peut les accompagner. Coulez les cargos. BULLSEYE 255/265. Ravitailleur le plus proche : Arco 1 (TACAN 51Y, 251.0 MHz, FL180) à 180 nm.]])
        :setTraining(false)
        :initialize()
    )
    veafCombatZone.GetZone("combatZone_Kobuleti_Medium"):addZoneElementsFromZoneNamed("combatZone_Kobuleti_Easy")
    veafCombatZone.GetZone("combatZone_Kobuleti_Hard"):addZoneElementsFromZoneNamed("combatZone_Kobuleti_Medium")
    veafCombatZone.GetZone("combatZone_Kobuleti_Hard"):addZoneElementsFromZoneNamed("combatZone_Kobuleti_Easy")
    veafCombatZone.GetZone("combatZone_Akhalkalaki_Medium"):addZoneElementsFromZoneNamed("combatZone_Akhalkalaki_Easy")
    veafCombatZone.GetZone("combatZone_Akhalkalaki_Hard"):addZoneElementsFromZoneNamed("combatZone_Akhalkalaki_Medium")
    veafCombatZone.GetZone("combatZone_Akhalkalaki_Hard"):addZoneElementsFromZoneNamed("combatZone_Akhalkalaki_Easy")
    veafCombatZone.GetZone("combatZone_Taman_Medium"):addZoneElementsFromZoneNamed("combatZone_Taman_Easy")
    veafCombatZone.GetZone("combatZone_Taman_Hard"):addZoneElementsFromZoneNamed("combatZone_Taman_Medium")
    veafCombatZone.GetZone("combatZone_Taman_Hard"):addZoneElementsFromZoneNamed("combatZone_Taman_Easy")
    veafCombatZone.initialize()
end

if veafQraManager then
    veafQraManager.initialize()
    local QRA_MinVody = VeafQRA:new()
        :setName("QRA MinVody")
        :setCoalition(coalition.side.RED)
        :addEnnemyCoalition(coalition.side.BLUE)
        :setTriggerZone("QRA-MinVody")
        :setRandomGroupsToDeployByEnemyQuantity(1, {"QRA MinVody - Su-27", "QRA MinVody - Su-30"}, 1)
        :setRandomGroupsToDeployByEnemyQuantity(3, {"QRA MinVody - Su-27", "QRA MinVody - Su-30", "QRA MinVody - MiG-31"}, 2)
        :setDelayBeforeRearming(600)
        :setDelayBeforeActivating(60)
        :setAirportLink("Mineralnye Vody")
        :start()
    local QRA_Krasnodar = VeafQRA:new()
        :setName("QRA Krasnodar")
        :setCoalition(coalition.side.RED)
        :addEnnemyCoalition(coalition.side.BLUE)
        :setTriggerZone("QRA-Krasnodar")
        :setRandomGroupsToDeployByEnemyQuantity(1, {"QRA Krasnodar - MiG-29S", "QRA Krasnodar - Su-27"}, 1)
        :setRandomGroupsToDeployByEnemyQuantity(3, {"QRA Krasnodar - MiG-29S", "QRA Krasnodar - Su-27", "QRA Krasnodar - MiG-31"}, 2)
        :setDelayBeforeRearming(600)
        :setDelayBeforeActivating(60)
        :setAirportLink("Krasnodar-Pashkovsky")
        :start()
    local QRA_Kutaisi = VeafQRA:new()
        :setName("QRA Kutaisi")
        :setCoalition(coalition.side.BLUE)
        :addEnnemyCoalition(coalition.side.RED)
        :setTriggerZone("QRA-Kutaisi")
        :setRandomGroupsToDeployByEnemyQuantity(1, {"QRA Kutaisi - F-16C", "QRA Kutaisi - F-15C"}, 1)
        :setRandomGroupsToDeployByEnemyQuantity(3, {"QRA Kutaisi - F-16C", "QRA Kutaisi - F-15C"}, 2)
        :setDelayBeforeRearming(600)
        :setDelayBeforeActivating(60)
        :setAirportLink("Kutaisi")
        :start()
    local QRA_Gudauta = VeafQRA:new()
        :setName("QRA Gudauta")
        :setCoalition(coalition.side.BLUE)
        :addEnnemyCoalition(coalition.side.RED)
        :setTriggerZone("QRA-Gudauta")
        :setRandomGroupsToDeployByEnemyQuantity(1, {"QRA Gudauta - F-16C", "QRA Gudauta - F-15C"}, 1)
        :setRandomGroupsToDeployByEnemyQuantity(3, {"QRA Gudauta - F-16C", "QRA Gudauta - F-15C"}, 2)
        :setDelayBeforeRearming(600)
        :setDelayBeforeActivating(60)
        :setAirportLink("Gudauta")
        :start()
end

-- ── Features ──

if veafGrass then
    veafGrass.initialize()
end

if veafAssets then
    veafAssets.Assets = {
        {sort = 1, name = "Arco 1", description = "Arco 1 (KC-135, perche) - ouest", information = "TACAN 51Y AR1 U251.0 - FL180", linked = "Arco 1 escort"},
        {sort = 2, name = "Texaco 1", description = "Texaco 1 (KC-135MPRS, panier) - ouest", information = "TACAN 52Y TX1 U252.0 - FL220", linked = "Texaco 1 escort"},
        {sort = 3, name = "Shell 1", description = "Shell 1 (KC-135MPRS, panier) - est", information = "TACAN 53Y SH1 U253.0 - FL200", linked = "Shell 1 escort"},
        {sort = 4, name = "Shell 2", description = "Shell 2 (KC-135, perche) - est", information = "TACAN 54Y SH2 U254.0 - FL240", linked = "Shell 2 escort"},
        {sort = 5, name = "Magic 1", description = "Magic 1 (E-3A) - ouest", information = "U265.0 - FL300", linked = "Magic 1 escort"},
        {sort = 6, name = "Overlord 1", description = "Overlord 1 (E-3A) - est", information = "U266.0 - FL310", linked = "Overlord 1 escort"},
        {sort = 7, name = "CSG-74 Stennis", description = "CVN-74 Stennis (porte-avions) - large de Batumi", information = "TACAN 10X STS - ICLS 10 - Link 4 225.0 Tour 225.0 - S-3B et Pedro par le menu CARRIER OPS"},
        {sort = 8, name = "CVN-74 Stennis S3B-Tanker", description = "S-3B du Stennis (ravitailleur embarqué)", information = "TACAN 75Y T74 U290.9"},
        {sort = 9, name = "CSG-01 Tarawa", description = "LHA-1 Tarawa (porte-hélicoptères) - large de Batumi", information = "TACAN 11X TAA - ICLS 11 Tour 226.0"},
        {sort = 10, name = "Tanker Rouge", description = "Tanker Rouge (Il-78M)", information = "U261.0 - FL200", linked = "Tanker Rouge escort"},
        {sort = 11, name = "AWACS Rouge", description = "AWACS Rouge (A-50)", information = "U260.0 - FL300", linked = "AWACS Rouge escort"},
        {sort = 12, name = "Darkstar 1", description = "Darkstar 1 (E-3A) - arène, bleu", information = "U280.0 - FL300"},
        {sort = 13, name = "AWACS Arène Rouge", description = "AWACS Arène Rouge (A-50) - arène, rouge", information = "U281.0 - FL300"},
        {sort = 14, name = "Reaper 1", description = "Reaper 1 (drone laser) - Beslan", information = "Laser 1688 - V118.8 AM FL150 au-dessus de la zone", jtac = 1688, freq = "118.8", mod = "AM"},
        {sort = 15, name = "Reaper 2", description = "Reaper 2 (drone laser) - Psebay", information = "Laser 1687 - V118.9 AM FL150 au-dessus de la zone", jtac = 1687, freq = "118.9", mod = "AM"},
    }
    veafAssets.initialize()
end

if veafMove then
    veafMove.initialize()
end

if veafSanctuary then
    veafSanctuary.initialize()
    veafSanctuary.addZone(
        VeafSanctuaryZone:new()
        :setName("Sanctuaire bleu")
        :setPolygonFromUnits({"Sanctuaire bleu-01", "Sanctuaire bleu-02", "Sanctuaire bleu-03", "Sanctuaire bleu-04", "Sanctuaire bleu-05", "Sanctuaire bleu-06", "Sanctuaire bleu-07", "Sanctuaire bleu-08", "Sanctuaire bleu-09", "Sanctuaire bleu-10", "Sanctuaire bleu-11", "Sanctuaire bleu-12", "Sanctuaire bleu-13", "Sanctuaire bleu-14", "Sanctuaire bleu-15", "Sanctuaire bleu-16", "Sanctuaire bleu-17", "Sanctuaire bleu-18", "Sanctuaire bleu-19", "Sanctuaire bleu-20", "Sanctuaire bleu-21", "Sanctuaire bleu-22"})
        :setCoalition(coalition.side.BLUE)
        :setDelayWarning(0)
        :setDelaySpawn(-1)
        :setDelayInstant(60)
        :setProtectFromMissiles(true)
    )
end

if veafWeather then
    veafWeather.initialize()
end

if veafRemote then
    veafRemote.initialize()
end

if veafAirbases then
    veafAirbases.initialize()
end

-- ── Infrastructure ──

if veafMarkers then
    veafMarkers.initialize()
end

if veafTime then
    veafTime.initialize()
end

if veafUnits then
    veafUnits.initialize()
end

if veafCacheManager then
    veafCacheManager.initialize()
end

if veafEventHandler then
    veafEventHandler.initialize()
end

-- ── Core ──

if veafGroundAI then
    veafGroundAI.initialize()
end

-- ── Infrastructure ──

if veafCommands then
    veafCommands.initialize()
end

-- ── Features ──

if veafInterpreter then
    veafInterpreter.initialize()
end

-- ── Community scripts disabled (VEAF leaves their globals alone) ──────────────
veaf.setConfig("tum", "enable", false)

-- ── Skynet-IADS ──────────────────────────────────────────────────────────────
if veafSkynet then
    veafSkynet.SpotterNetwork = true
    veafSkynet.SpotterView = "off"
    veafSkynet.initialize(false, false, false, false)
end

-- ── CSAR configuration ───────────────────────────────────────────────────────
-- Note: CSAR.lua must be loaded by mission-script.lua before this block.
if csar then
    csar.initialize()
end
