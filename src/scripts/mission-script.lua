-- mission-script.lua
-- Mission-specific Lua code that cannot be generated from mission.yaml.
--
-- This file is loaded AFTER veaf-config.lua (which is generated automatically
-- from mission.yaml by the veaf-tools build command).
--
-- Put here:
--   - Custom shortcuts / aliases  (VeafAlias:new():...)
--   - Custom Lua helper functions
--   - Third-party script setup (CTLD, CSAR, …) that requires Lua code
--
-- Do NOT put here:
--   - Module initialization calls  → use mission.yaml (modules:)
--   - Mission identity             → use mission.yaml (mission:)
--   - QRA definitions              → use mission.yaml (modules.QRA)
--   - Combat/CAP missions          → use mission.yaml (combat_missions: / cap_missions:)
--   - Assets lists                 → use mission.yaml (modules.ASSETS.assets)

-- ── Missions scénarisées (prompt Open Training §4.12) ──────────────────────────────────────────
-- Écrites ici et non dans `combat_missions:` de mission.yaml, qui ne porte ni objectifs ni niveau
-- des pilotes. Reprises de la v5 (groupes transportés par tools/port_v5_scenarios.py).
if veafCombatMission then
  -- Attaque rouge sur Gudauta : SEAD (Su-25T) puis bombardiers (Su-24M) ; ratée si la tour, le
  -- dépôt de carburant ou le mess de la base sont détruits. Identifiants de décor repris de la v5.
  veafCombatMission.AddMission(
    VeafCombatMission:new()
      :setSecured(true)
      :setRadioMenuEnabled(true)
      :setName("Attaque-Gudauta")
      :setFriendlyName("Attaque rouge sur Gudauta")
      :setBriefing([[
Alerte, ce n'est pas un exercice !
Des avions d'attaque et des bombardiers ont été détectés à la frontière russe, au nord de Gudauta.
Leur cap les mène sur la base de Gudauta, qui est très probablement leur objectif.
Abattez tous les bombardiers avant qu'ils frappent la base !]])
      :addElement(
        VeafCombatMissionElement:new()
          :setName("SEAD")
          :setGroups({
            "Red Attack On Gudauta - Wave 1-1",
            "Red Attack On Gudauta - Wave 1-2",
            "Red Attack On Gudauta - Wave 1-3",
            "Red Attack On Gudauta - Wave 1-4",
          })
          :setSkill("Random")
      )
      :addElement(
        VeafCombatMissionElement:new()
          :setName("Bombardiers")
          :setGroups({
            "Red Attack On Gudauta - Wave 2-1",
            "Red Attack On Gudauta - Wave 2-2",
            "Red Attack On Gudauta - Wave 2-3",
          })
          :setSkill("Random")
      )
      :addObjective(
        VeafCombatMissionObjective:new()
          :setName("Bâtiments de Gudauta")
          :setDescription("la mission est ratée si un des bâtiments protégés de Gudauta est détruit")
          :setMessage("Bâtiment(s) de Gudauta détruit(s) : %s !")
          :configureAsPreventDestructionOfSceneryObjectsInZone(
            { "Gudauta-Tour", "Gudauta-Carburant", "Gudauta-Mess" },
            {
              [156696667] = "la tour de contrôle",
              [156735615] = "le dépôt de carburant",
              [156729386] = "le mess",
            }
          )
      )
      :addObjective(
        VeafCombatMissionObjective:new()
          :setName("Abattre les bombardiers")
          :setDescription("vous devez abattre tous les bombardiers")
          :setMessage("%d bombardiers abattus !")
          :configureAsKillEnemiesObjective()
      )
      :initialize()
  )

  -- Vague de 11 Tu-160, au FL200 et à Mach 0,8, à détruire en moins de 15 minutes (secteur Ouest).
  veafCombatMission.AddMission(
    VeafCombatMission:new()
      :setSecured(false)
      :setRadioMenuEnabled(true)
      :setName("Vague-Tu-160")
      :setFriendlyName("Entraînement - vague de Tu-160")
      :setBriefing([[
Onze Tu-160 arrivent face à vous, au FL200 et à Mach 0,8, au-dessus de la mer à l'ouest.
Détruisez-les ou faites-les faire demi-tour en moins de 15 minutes !]])
      :addElement(
        VeafCombatMissionElement:new()
          :setName("Bombardiers")
          :setGroups({
            "Red Tu-160 Bomber Wave1-1", "Red Tu-160 Bomber Wave1-2", "Red Tu-160 Bomber Wave1-3",
            "Red Tu-160 Bomber Wave1-4", "Red Tu-160 Bomber Wave1-5", "Red Tu-160 Bomber Wave1-6",
            "Red Tu-160 Bomber Wave1-7", "Red Tu-160 Bomber Wave1-8", "Red Tu-160 Bomber Wave1-9",
            "Red Tu-160 Bomber Wave1-10", "Red Tu-160 Bomber Wave1-11",
          })
          :setSkill("Good")
      )
      :addObjective(
        VeafCombatMissionObjective:new()
          :setName("Moins de 15 minutes")
          :setDescription("la mission se termine au bout de 15 minutes")
          :setMessage("Les 15 minutes sont écoulées !")
          :configureAsTimedObjective(900)
      )
      :addObjective(
        VeafCombatMissionObjective:new()
          :setName("Abattre les bombardiers")
          :setDescription("abattez ou faites faire demi-tour à tous les bombardiers")
          :setMessage("%d bombardiers abattus ou repoussés !")
          :configureAsKillEnemiesObjective(-1, 50)
      )
      :initialize()
  )

  -- Interception d'un transport VIP escorté, de Krasnodar à Mineralnye Vody.
  veafCombatMission.AddMissionsWithSkillAndScale(
    VeafCombatMission:new()
      :setSecured(true)
      :setRadioMenuEnabled(true)
      :setName("Interception-VIP")
      :setFriendlyName("Intercepter un transport VIP (Krasnodar - Mineralnye Vody)")
      :setBriefing([[
Un avion de transport russe décolle de Krasnodar pour emmener une personnalité à Mineralnye Vody.
Il est escorté par une patrouille de chasse. Abattez le transport.]])
      :addElement(
        VeafCombatMissionElement:new()
          :setName("Transport")
          :setGroups({ "OnDemand-Intercept-Transport-Krasnodar-Mineral-Transport" })
          :setScalable(false)
      )
      :addElement(
        VeafCombatMissionElement:new()
          :setName("Escorte")
          :setGroups({ "OnDemand-Intercept-Transport-Krasnodar-Mineral-Escort" })
          :setSkill("Random")
      )
      :addObjective(
        VeafCombatMissionObjective:new()
          :setName("Abattre le transport")
          :setDescription("abattez le transport et la personnalité à bord")
          :setMessage("%d avions de transport abattus !")
          :configureAsKillEnemiesObjective()
      )
      :initialize()
  )
end

