# Milestone 0 validation record

Project Version: 0.1.0-dev.1

Date: 2026-10-12. Environment: Windows; bundled Python; offline class/Lua inspection. No PZ or server launched.

## Commands

Run from the project root using the installed bundled interpreter:

```powershell
$auditPython = 'C:/Users/willi/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe'
& $auditPython './scripts/check_versions.py' --root . --json
& $auditPython './scripts/collect_evidence.py' --workshop-root 'E:/Program Files (x86)/Steam/steamapps/workshop/content/108600' --game-root 'E:/Program Files (x86)/Steam/steamapps/common/ProjectZomboid' --output-dir './research'
& $auditPython './scripts/validate_audit.py'
```

Native API inventory command:

```powershell
& $auditPython './scripts/inspect_class_api.py' --game-root 'E:/Program Files (x86)/Steam/steamapps/common/ProjectZomboid' --output './research/NATIVE_CLASS_API.json' zombie.core.Core zombie.core.GameVersion zombie.characters.animals.IsoAnimal zombie.characters.animals.datas.AnimalData zombie.Lua.LuaManager 'zombie.Lua.LuaManager$GlobalObject' 'zombie.Lua.LuaManager$Exposer' zombie.characters.skills.CustomPerks zombie.characters.skills.CustomPerk zombie.characters.skills.PerkFactory zombie.characters.professions.CharacterProfessionDefinition zombie.scripting.objects.CharacterProfessionDefinitionScript zombie.vehicles.BaseVehicle zombie.iso.areas.SafeHouse zombie.iso.objects.IsoDeadBody zombie.inventory.ItemContainer zombie.world.moddata.GlobalModData
& $auditPython './scripts/inspect_class_api.py' --game-root 'E:/Program Files (x86)/Steam/steamapps/common/ProjectZomboid' --output './research/PACKAGED_ANIMAL_API.json' --prefer-jar zombie.characters.animals.IsoAnimal
```

Targeted method bodies were inspected offline by extracting selected native class files from the installed JAR/loose classpath and running the existing analyzer:

```powershell
& 'E:/Program Files (x86)/Steam/steamapps/common/ProjectZomboid/jre64/bin/java.exe' -jar '../.tmp-nightfall-decompile/cfr-0.152.jar' '<extracted-class-path>' --outputdir '<local-inspection-directory>' --silent true
```

Hashes and public API descriptors are the stable evidence records. Temporary native binary extracts and decompiled inspection outputs remain under `research/native-*` as local research artifacts; they are not project gameplay implementation and must never be packaged or redistributed. Automatic approval review rejected their recursive cleanup as “blocked by policy”; no deletion occurred. The CFR invocation does not execute game classes. Core/GameVersion, CustomPerks, LuaManager Exposer/GlobalObject, GlobalModData, CharacterProfessionDefinitionScript and packaged/effective IsoAnimal were the targeted inspection subjects. No third-party dependency Lua/asset implementation was copied into project runtime source.

## Results

- [TESTED — offline audit tooling] Source collector: PASS, 368 source/hash records, 17 current dependency metadata entries, 38 public item identifiers; no listed native path missing.
- [TESTED — offline audit tooling] API parser: PASS on 17 effective class files plus packaged animal class; this is not a Lua invocation or native behavior test.
- [TESTED — offline documentation] Required deliverables, feature coverage, public identifier inventory, source-hash stability and documentation links: recorded by `research/DOCUMENTATION_CHECK.json` after final validation.
- [TESTED — offline versions] Canonical/mirrors/changelog checks: recorded by `research/VERSION_CHECK_FINAL.json`; no distribution artifacts, development check explicitly defers them.
- Gameplay unit tests: NOT TESTED / not implemented. No claim is made from tooling PASS to mod behavior.

## Gates

| Gate | Status | Evidence / blocker |
|---|---|---|
| G0 requirements | PASS for Milestone 0 scope | Historical user handoff, canine scope, authority/config assessment |
| G1 source investigation | PASS for bounded audit deliverables | Exact installed metadata, hashes, native/public API and gap records |
| G2 production design | BLOCKED for affected gameplay | Private persistence, identity, strict movement and non-bypassable policy seams unresolved |
| G3 gameplay implementation | NOT STARTED | User authorized Milestone 0 only |
| G4 static documentation/tooling | PASS if final recorded checker succeeds | No runtime-source or release claim |
| G5 gameplay offline tests | NOT TESTED | No gameplay code |
| G6 actual PZ client | NOT TESTED | No game launch / operator evidence |
| G7 dedicated MP | BLOCKED / NOT TESTED | No dedicated/two-client runtime evidence |
| G8 package/release | BLOCKED | G7 missing, no packages, no release authorization |

Source audit PASS is only the completion of documented investigation, not closure of an EXPERIMENTAL/BLOCKED capability. No live mods, Workshop staging, external dependency files or installed game files changed.
