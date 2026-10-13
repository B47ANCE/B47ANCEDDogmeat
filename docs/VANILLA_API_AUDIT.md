# Installed Build 42 API audit

Evidence date: 2026-10-12. Offline binary/Lua inspection only. No PZ client or server executed.

## Current environment, independent of historical baselines

[VERIFIED] Installed game root G: `E:/Program Files (x86)/Steam/steamapps/common/ProjectZomboid/`. Steam manifest build ID: `25485521`. Packaged `zombie.core.Core` initializes `GameVersion(42, 21, "")`: the inspected engine reports **42.21**, not the older workspace 42.20.3 baseline. An extra patch number was not established. Steam build ID is not the Project Version.

[VERIFIED] `ProjectZomboid64.json` places `.` before `projectzomboid.jar` and includes an additional ProjectRemnants NPCFW JAR. A loose `zombie/characters/animals/IsoAnimal.class` exists and differs from the packaged class. Runtime agent modifications and the additional JAR's behavior were not audited. This is an installed, modified environment, not a certified pristine vanilla installation.

| Native evidence | SHA-256 |
|---|---|
| Packaged `Core.class` | `8f5c69740c8bf2181123a831ab68d1dfb047453687cca6dc62c77816d76ab360` |
| Packaged `LuaManager.class` | `dcaad0082ca27a15550c7d0a6e14b3aeb71f634a14f32123dec620df180c646d` |
| Packaged `IsoAnimal.class` | `b3395fce0260301069cfe6e1e112d949533532dc7da1ec31861ac525100b9bbb` |
| Loose `IsoAnimal.class` | `f345480fb0a2e652ffe613d37df2a438b07e9c655213fe71f9b5e5c895fe1e73` |

`../research/NATIVE_CLASS_API.json` inventories 17 effective class files without executing them; `PACKAGED_ANIMAL_API.json` captures the packaged animal interface; `NATIVE_PRECEDENCE.json` distinguishes sources. `SOURCE_MANIFEST.json` hashes selected native Lua/script files and the JAR/launcher configuration. CFR 0.152 was used offline for targeted method inspection; decompiled line numbers are artifact-local, not original Java source line numbers. Public Java method presence alone is not proof of Lua exposure or dedicated correctness.

## Verified API surfaces and their limits

| Requirement | Concrete native evidence | Classification / limit |
|---|---|---|
| Native animal entity | Packaged `zombie.characters.animals.IsoAnimal`; GlobalObject `addAnimal` overloads | VERIFIED construction interface; preserve CD creation |
| Age/weight | `AnimalData:getAge,setAge,getWeight,setWeight`; vanilla Animal UI | VERIFIED reads/methods; custom mass, growth and carrying calculations EXPERIMENTAL |
| Lua exposure | `LuaManager$Exposer` registers IsoAnimal, AnimalData, ItemContainer, SafeHouse, PerkFactory, CharacterProfessionDefinition and IsoDeadBody | VERIFIED exposure; inherited methods require actual signature/usage checks |
| Native animal save/load | Packaged `IsoAnimal.save/load` serializes ModData; growth copies native ModData | VERIFIED persistence mechanism; CD recreation/snapshot remains separate |
| Animal attachment | shared `TimedActions/Animals/ISAttachAnimalToPlayer.lua:complete`; `AnimalData:setAttachedPlayer` | VERIFIED native attachment; dog lease/AI interaction and force modeling EXPERIMENTAL |
| Pickup/carry | shared `ISPickupAnimal.lua:complete`, native AnimalInventoryItem representation | VERIFIED vanilla route; identity continuity and MP antidupe EXPERIMENTAL |
| Trailer transport | shared `ISAddAnimalInTrailer.lua:complete`, remove action, `ISVehicleAnimalUI` and BaseVehicle overloads | VERIFIED native trailer support; arbitrary compartment trucks EXPERIMENTAL |
| Physical conditions | AnimalData, native animal health plus CD veterinary system | VERIFIED generic health; canine region-specific BodyDamage is not established |
| Human health UI | client `XpSystem/ISUI/ISHealthPanel.lua` derives ISPanelJoypad and uses human BodyPart/BodyDamage widgets | VERIFIED UI reference; human anatomical/dosing model must not be reused as canine authority |
| Radial/controller UI | client `ISUI/ISRadialMenu.lua:addSlice`, joypad focus/button-release methods | VERIFIED radial lifecycle; cross-input conflict/hold semantics need runtime |
| Context menus | client `ISUI/ISContextMenu.lua`; animal/context menus | VERIFIED menu API; parent-context and test-call contracts matter |
| Commands | server `ClientCommands.lua` and annotated GlobalObject sendClientCommand/sendServerCommand overloads | VERIFIED intent/result transport; sender validation must be implemented independently |
| World sounds | annotated GlobalObject `addSound(IsoObject,int,int,int,int,int)` | VERIFIED attraction interface; audible radius/balance and replication EXPERIMENTAL |
| Speech/vocalizations | vanilla emote shout route and CD notifications | VERIFIED existing presentation route; exact spoken cue/“Hey” audio reuse is EXPERIMENTAL |
| Survivor custom skill | `CustomPerks.init/initLua`; `media/perks.txt` loaded from mod version/common directory; PerkFactory | VERIFIED custom perk loader; custom-skill persistence and MP XP still require native test |
| Occupations | `media/scripts/generated/characters/character_professions.txt`; CharacterProfessionDefinitionScript registry lookup, cost/XP/recipes | VERIFIED modern definition path; new registry declaration/order and cost balance EXPERIMENTAL |
| Books | server `XpSystem/XPSystem_SkillBook.lua`; shared `ISReadABook.lua` server start/update, skill/page synchronization | VERIFIED existing study/multiplier path; custom perk registration and anti-replay need integration |
| VHS/recorded media | shared `RecordedMedia/ISRecordedMedia.lua`, RecMedia table, OnInitRecordedMedia register/addLine | VERIFIED media registration; custom dog-training XP codes not yet established |
| Safehouse permissions | exposed SafeHouse `isSafehouseAllowInteract`, `isSafehouseAllowLoot`, lookups | VERIFIED native permission candidates; server role/player resolution and SP fallback need tests |
| Real wildlife tracks | animal track definitions; `Foraging/ISAnimalTracksFinder.lua` consumes actual track/item records | VERIFIED real track system; independent dedicated dog tracking adapter EXPERIMENTAL |
| Foraging | shared `Foraging/ISForageAction.lua`; client discovery/tracks | VERIFIED existing domain; client icon visibility cannot authorize server rewards |
| Fishing | shared `Fishing/FishingUtils.lua`; client FishingManager | VERIFIED fishing subsystem; no dog knowledge of hidden fish or safe aquatic fetch API established |
| Inventory/container mutation | exposed ItemContainer; vanilla authoritative actions/server commands | VERIFIED inventory APIs; arbitrary dog reach, nested locks and transaction round trips EXPERIMENTAL |
| Corpse object | exposed IsoDeadBody/public methods; corpse support in trailer action | VERIFIED object presence; reanimate methods do not prove canine zombification, ragdoll or safe dragging |

## Hidden data and durable persistence

[VERIFIED] `GlobalModData.receiveRequest` reads a requested table name and sends that table to the requesting connection if present. The inspected method has no per-table private-record ACL. No independent packet-level private-table protection was established. A server-only writer does not make a global ModData table confidential.

[INFERRED] Hidden personality/history, prior command knowledge and undiscovered medical information must not be stored in synchronized animal/player ModData or a publicly requestable global table. Send a deliberately filtered, per-handler projection. Do not serialize the full record and rely on UI hiding or an obscure table name.

[VERIFIED] GlobalObject provides annotated `getFileWriter/getFileReader` for a Lua-cache directory, not the save directory. `getFileWriter` filters extensions/relative traversal and returns a writer or nil. `getCurrentSaveName` returns the current save directory string. These establish a private host-file candidate, not world-save atomicity. `getModFileWriter` writes inside the installed mod's common directory and is rejected for project persistence: it violates the no-installed-file-changes boundary and is not save-owned.

Proposed investigation: original server-only private store under the server Lua cache, scoped by a server-generated world/save identity, with bounded serialization, generation checks, write-ahead/dual-slot recovery and explicit world-backup inclusion. Because this lives outside normal world backups and atomic replacement/durable flush is not established, it is EXPERIMENTAL. If coherent private world-local persistence cannot be achieved through these APIs, document the exact gap before considering a narrow original Java save bridge. Do not persist hidden records in global ModData as a shortcut.

## Unsupported assumptions

- BLOCKED: vanilla human zombie reanimation is not a verified infected-canine entity path. A canine skin on a human zombie is not an acceptable substitution.
- BLOCKED: native human BodyPart regions do not establish canine wounds/fractures or validated canine medication.
- EXPERIMENTAL: physical leash pulling/stumbles, arbitrary body dragging, shared cooperative loads and animation collision synchronization. Presence of PZBullet or vehicle impulse internals is not an exposed canine physics contract.
- EXPERIMENTAL: zombie redirection needs actual sound attraction, safe route/escape and ownership proof; a targeted sound is not a guarantee of horde control.
- BLOCKED: a universally supported 8–10 compartment kennel truck was not found. Native trailers are the starting evidence, not an arbitrary vehicle kennel API.
- EXPERIMENTAL: drowning/water traversal/floating item pickup; no teleporting fetch reward or hidden-fish query may substitute for a real observed task.

## Independent runtime gates

G6 NOT TESTED; G7 BLOCKED / NOT TESTED. Required native spikes: custom skill/occupation boot on both platforms; authoritative timed-action completion/cancellation; attachment versus CD movement; carry/growth snapshot continuity; world-scoped private persistence including backup rollback; unsolicited/explicit client data requests; animal/item multiplayer synchronization; cargo transactions; source/launcher/override mismatches.

No JVM game classes were loaded by the inspection utility. Running the CFR analyzer JVM is an offline inspection command, not a PZ launch. No installed file was changed. Both unmodified-packaged and user-installed runtime conditions must be recorded separately in future operator tests.
