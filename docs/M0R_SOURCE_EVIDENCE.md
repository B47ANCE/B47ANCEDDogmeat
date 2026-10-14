# M0R native source evidence and exact limits

Project Version: 0.2.0-dev.2

Native observations below were recorded at 0.1.0-dev.1 on 2026-10-12. This current contract header is not a new native inspection or runtime result; the gsd-v002 art rebuild does not change those observations.

Evidence date: 2026-10-12. Environment: Windows offline vanilla Lua/file/class inspection. No game class executed and no custom Java mod/bridge built. Canonical current hash inventory: [native_evidence.json](contracts/native_evidence.json). G = installed ProjectZomboid root; P = this repository. Raw native binaries/decompiled research remain local under research and are excluded from public Git; the public index contains facts, signatures and hashes only.

## Environment and provenance

G currently is E:/Program Files (x86)/Steam/steamapps/common/ProjectZomboid. Matched packaged Core inspection reports GameVersion(42,21,""). The game JAR hashes to e1a69eb743ede60b213a0fe7f8b83d4fcab773036d256cc4543a336f3b058a33. Packaged IsoAnimal is b3395fce0260301069cfe6e1e112d949533532dc7da1ec31861ac525100b9bbb; loose IsoAnimal is f345480fb0a2e652ffe613d37df2a438b07e9c655213fe71f9b5e5c895fe1e73. Client JSON places '.' before the JAR and includes an external NPCFW JAR and javaagent. Server BAT lists './;projectzomboid.jar'. Actual running launcher/classes/agent transformation and a pristine dedicated installation are UNKNOWN. Modified-client evidence cannot certify vanilla Lua-only support.

Existing local decompiled artifacts were reused only after input-class hashes matched current binaries. Their line numbers are artifact-local. New javap/native bytecode offsets refer to the named packaged method, not original source lines. The JDK analyzer is an offline inspection tool, not a mod dependency; it did not run PZ classes. No external mod implementation was re-audited or copied in M0R. Optional item-identifier provenance remains historical until its adapter slice performs current clean-room validation.

## Evidence table

| ID | Exact source / symbol / call site | [VERIFIED] narrow finding | Larger feature limit |
|---|---|---|---|
| E-ENVIRONMENT | G/ProjectZomboid64.json; ProjectZomboidServer.bat; packaged Core/IsoAnimal | Current bytes and classpath candidates recorded | Actual effective/pristine client/server/Linux behavior UNKNOWN |
| E-REGISTRY | G/media/lua/shared/Definitions/animal/SheepDefinitions.lua:4,24,122,144; AnimalDefinitions.loadAnimalDefinitions bytecode27–88 and2655–2668 | stages/breeds/genome/animals Lua tables consumed; arbitrary type keys; body model resolved via ModelManager | Native lazy cache/load order and original canine registration EXPERIMENTAL |
| E-REGISTRY | P/research/native-inspection/zombie/Lua/LuaManager$GlobalObject.java:953–960; G/media/lua/server/ClientCommands.lua:753–760 | addAnimal(IsoCell,int,int,int,String,AnimalBreed[,boolean skeleton]):IsoAnimal; native server resolves breed then addToWorld | Debug capability-guarded call is not ordinary handler spawn authority or MP proof |
| E-ASSET | G/media/scripts/generated/models_animals.txt:316–321; animations_meshes.txt:107–113; media/AnimSets/ewe/pathfind/defaultPathfind.xml:3–30; walk/defaultWalk.xml:3–6; idle/idle1.xml:3–11 | Skinned model/mesh/shader/animationsMesh and meshFile/animationDirectory/prefix data; native moving/idle nodes and footfall events | Independent canine rig/clips/assets/export compatibility not created or tested |
| E-ASSET | P/research/native-packaged-inspection/zombie/characters/animals/IsoAnimal.java:499–503,962–975,1520 | Definition animset selected; native idle/eat/attack/walk/path/followwall/hit/fall/zone/alert/climbfence states | Every reachable original asset reference required; no native dog-flap/window state established |
| E-NATIVE | IsoAnimal source:562–575,2523–2534,3176–3177; exposed AnimalData/BaseAnimalBehavior/AnimalDefinitions at LuaManager$Exposer:1951–1957 | Nonclient behavior/data update; pathToLocation(int,int,int), pathToCharacter(IsoGameCharacter); native routes respect attachment checks | Server packet/trust/relevance and exclusive task arbitration still unproved |
| E-NATIVE | BaseAnimalBehavior.setBlockMovement(boolean) bytecode4–21; checkBehavior0–7; update0–21/135–185; wanderIdle0–39 | Blocking stops movement; doing flag can skip one check; earlier flee/follow/attack routines/timeouts still execute/reset | Flags do not establish a permanent exclusive B47ANCE task lease |
| E-NATIVE | AnimalInstanceManager.add/updateLocal; AnimalController.update0–9; AnimalSynchronizationManager.update97–145 | Native online ID/send-to-clients and server update candidates | Late join, malicious input and chunk relevance require dedicated proof |
| E-IDENTITY | IsoAnimal source:1319–1342,1433–1440,1522–1523,2006–2015 | Save/load serializes ModData; constructor animalId=Rand.Next(10000); copyFrom copies ModData/animalId | Small native ID not unique; copyFrom does not prove every replacement calls it |
| E-CARRY | G/media/lua/shared/TimedActions/Animals/ISPickupAnimal.lua:46–64; AnimalInventoryItem.setAnimal@13/save@13/load@17–30 | Base.Animal item embeds native animal; native embedded save/load includes animal serialization | Specific carried-drop release branch not mapped; lifecycle/antidupe runtime unproved |
| E-ATTACH | ISAttachAnimalToPlayer.lua complete; native AnimalData.setAttachedPlayer; trailer/feed actions use block flags | Native attachment and bounded timed interaction candidates | Physical canine pulling/stumble and exclusive follow behavior unproved |
| E-TRAILER | ISAddAnimalInTrailer.lua:65–78; BaseVehicle.removeAnimalFromTrailer(IsoAnimal):IsoObject @95–103 | Trailer operations; removal creates replacement and invokes copyFrom | Runtime generation/occupancy/sync and other vehicle compartments unproved |
| E-GROWTH | Packaged AnimalData.grow(String):void; 592-byte Code, new animal@92, native ID transfer@301–304, trailer replace@583 | Replacement construction and animalId transfer; no getModData/setModData/copyTable/copyFrom invocation shown in this route | Original marker transfer BLOCKED; historical broad growth-ModData assertion is narrowed here |
| E-DEATH | IsoDeadBody constructor(IsoGameCharacter,boolean,boolean) @1121–1128; getItem @29–32,213; OnDeadBodySpawn @1307 | Corpse receives ModData; corpse item copies marker/data candidate | Callback execution side, corpse/item round-trip and authoritative terminal handling unproved |
| E-FILES | GlobalObject.java:782–785,2086–2088,2840–2863,3471–3503; LuaManager.java:136,352–358 | Annotated getRandomUUID():String; getCurrentSaveName():String; getFileReader(String,boolean):BufferedReader; getFileWriter(String,boolean,boolean):LuaFileWriter; UTF8 cache/Lua, allowed json extension | Save locator not world ID; cache outside native backup; atomic write/flush/durable pairing unproved |
| E-FILES | LuaFileWriter public write(String),writeln(String),close(); close @4 | PrintWriter-backed close; no exposed checkError/fsync/atomic rename established | Readback detects some corruption, not power-loss durability |
| E-PRIVACY | GlobalModData.java:73–76,194–212,279–287 | Loads then OnInitGlobalModData; named table requests return existing table; world save storage | Public named table is not confidential; trusted client-tamper-resistant anchor / save completion needs proof |
| E-DOOR | IsoAnimal.canGoThere source1582–1595; IsoDoor.TestCollide(IsoMovingObject,IsoGridSquare,IsoGridSquare) @6–130; IsoThumpable.setCanPassThrough(boolean) @0–2 and TestCollide@99–121 | Blocked/window routes rejected; open native door allows crossing; closed door tests tile edge; thumpable pass flag global | No selective dog-size/ACL aperture seam; closed-door flap BLOCKED |
| E-ZOMBIE | ClimbThroughWindowState.isIgnoreCollide; G/media/AnimSets/zombie/getdown/toCrawl.xml:3–16 | Native window transition parameters and StartCrawling clip event exist | Does not prove dog-door squeeze or hostile canine entity; BLOCKED traversal/reanimation |
| E-CONTENT | Matched CustomPerks/CharacterProfessionDefinitionScript; historical native Lua inventory/reading/track interfaces | Native content/skill domain interfaces exist | Exact new canine content registration, wildlife-v-human trails/water/projectiles and optional IDs still separate gates |
| E-UI | ISAnimalUI.lua:622; ISVehicleAnimalUI.lua:232; original ISUI/radial surfaces in historical native inventory | Animal UI indexes AnimalAvatarDefinition by type; native UI primitives exist | Original panels/inputs/controller/accessibility not implemented |
| E-LOCALIZATION | G/media/lua/shared/Translate/EN/Sandbox.json/UI.json; installed29 folder names | JSON key/text convention and required languages observed | Shipped key coverage/new mod loading/rendering NOT TESTED |
| E-WORLD | No waste/flap carrier/world-object creation contract established in this audit | No verified waste API claim | Physical persistent/replicated urine/feces, offscreen anchors and cleanup stay EXPERIMENTAL/BLOCKED before implementation |

## Decisive blockers and next source questions

B-TASK: demonstrate a supported Lua scheduling seam and native interruptions without second writers. B-IDENTITY: map complete carried release and server lifecycle observation; solve growth marker loss without native-ID guessing. B-STORE: establish trustworthy native/private checkpoints, observable write failure and recoverable receipts; paired operator backup alternative is explicitly limited. B-DOOR/B-ZOMBIE: prove selective physical native traversal or retain blocked feature and separately review an actual-open-door alternative. B-WASTE: inspect persistent world-object creation/replication/anchor/cleanup before physical sanitation code. B-ASSET/B-ENV: original asset registration and pristine dedicated runtime remain required. No gap is resolved by custom Java or third-party dog implementations.

## Reproduction commands

Run the public validator from repository root with bundled Python:

```powershell
& 'C:/Users/willi/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe' -B scripts/validate_m0r.py --native --game-root 'E:/Program Files (x86)/Steam/steamapps/common/ProjectZomboid'
```

This rehashes the declared native files/JAR entries without executing them. Source inspection used targeted rg/Get-Content, in-memory ZIP/SHA256 and the existing inspect_class_api parser. New bytecode inspection used the existing JDK javap tool, not a gameplay Java component:

```powershell
& '../B47ANCEDEyewear/native/build/toolchain/jdk-25.0.4.1+1/bin/javap.exe' -classpath 'E:/Program Files (x86)/Steam/steamapps/common/ProjectZomboid/projectzomboid.jar' -c -p zombie.characters.animals.datas.AnimalData
```

Raw analyzer output is local research and is not redistributed. Hash equality proves applicability of inspected bytes only. No pristine/live/headless/Linux success was observed. G6 NOT TESTED; G7 BLOCKED / NOT TESTED; G8 BLOCKED.
