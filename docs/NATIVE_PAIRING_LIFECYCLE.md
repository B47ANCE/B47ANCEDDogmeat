# Native checkpoint pairing and lifecycle observation

Project Version: 0.2.0-dev.5

Historical implementation/validation scope: **0.2.0-dev.3**, including the 206-case result below. The current [loadable persistence diagnostic](NATIVE_BOOTSTRAP_TEST.md) adds bootstrap/initialization and explicitly blocks dedicated ownership after discovering client-writable animal markers. Earlier statements about absent bootstrap refer to that historical checkpoint; they are not the current source inventory.

User-authorized continuation, 2026-10-14. This adds an explicit native event adapter to the existing private snapshot prototype. The model is unchanged. **Dogs are not yet saving/loading in a running game:** there is no installed/loadable mod, safe first-world initializer or registered original canine. The implementation below is ready for source review and offline tests; it must not be described as in-game or dedicated verification.

## Implemented native path

`NativeRuntime.install(config, api)` installs exactly three server event handlers: OnInitGlobalModData, OnServerStarted and OnCharacterDeath. It has no automatic bootstrap. A future server entry point must call it before native initialization with the approved namespace and verified native type/breed allowlist. Configuration is copied and bounded; client role, duplicate installation and unavailable events refuse. Partial registration cannot be retried in the same process. Hot reload and changing worlds inside one Lua session are unsupported; use a fresh process.

OnInitGlobalModData is observed after the native GlobalModData loader. The handler reads an **existing** table through ModData.get and accepts only schema, worldId and checkpoint. It does not create, replace or import tables. It ignores the event's isNewGame value because inspected dedicated startup does not establish that value reliably. Missing/foreign/future/malformed anchors and missing/invalid private slots remain untouched and block recovery.

The strict loaded anchor supplies a trusted NativeLoaded context to PrivateStore. It selects the exact matching private checkpoint; it does not choose the newest file. Both slots must validate, including the existing predecessor rules. A newer unpaired private preparation still blocks recovery. The old OperatorPaired path remains available for explicit external recovery; neither context is a network argument or a way to skip file validation.

After OnServerStarted, a one-shot census calls getCell():getAnimals(). The native method scans the entire object list; the adapter never calls it from a tick/update event. It refuses a list above 1,024 entries before iterating. An explicit server recovery call may repeat the census. Output says OBSERVED_LOADED_ONLY: it covers the returned loaded objects, not the whole world, carried inventory, trailers, virtual animals or unloaded chunks. Duplicate results are reported using the final quarantined registry state, never the first provisional match.

The controller accepts an ownership preparation only after recovery/startup and while the loaded anchor object, fields, save locator and server role remain unchanged. NativeSession still requires the future authenticated broker's trusted actor/episode/configuration/interaction facts. After private inactive-slot readback succeeds, NativeCheckpoint changes only the existing public anchor's checkpoint field and enters WAITING_NATIVE_RELOAD. The old paired slot and prepared slot remain intact; another preparation is refused.

This pending result means **an in-memory anchor has changed**. Normal native saving may later persist it. No save is forced. The controller does not listen to OnSave, OnPostSave or OnReceiveGlobalModData and does not promote from another read of the live table. Duplicate load/start events cannot promote it either. Only a genuinely later native load in a fresh process can select the prepared checkpoint. Native anchor persistence is not proof that every animal/chunk saved successfully; every observed carrier must still match its private record and ambiguous/missing carriers are never respawned.

## Lifecycle continuity

The native reader requires exact boolean results. A true isDead result on a known handle yields sticky KNOWN_DEAD even if it is already detached; nil/nonboolean results are unavailable, not fabricated death. OnCharacterDeath is only a notification: the reader checks actual native death again, and an unknown living animal cannot be bound through that event.

An exact false isExistInTheWorld result on a known handle yields DETACHED_PENDING and blocks actions. This does not delete a record or infer death. If the **same** handle returns with the full expected world/dog/generation/type/breed/token marker, it can return to MATCHED. A different handle carrying the ID remains quarantined in that session, even when the old handle is detached. Accepted native replacement requires a separately proved transition/recovery boundary; a new handle alone cannot distinguish legitimate reload/drop from duplication.

A new process and exact loaded checkpoint create a fresh registry, allowing newly loaded native handles to match their retained private identities. Unobserved dogs remain retained and unavailable. No dog is allocated, adopted, stamped, respawned, given a new generation or revived by discovery. Observational death is not a persisted tombstone; corpse/cargo transitions still require their own verified transaction path. All private record/history preservation rules remain in force.

## Source findings that determine the limits

[VERIFIED: offline Build 42.21 source/class inspection] The [new evidence manifest](native-pairing-evidence.json) records exact inputs and offsets; the previous [native file evidence](native-persistence-evidence.json) remains dated to its original scope.

| Finding | Consequence |
|---|---|
| GlobalModData.init loads before OnInitGlobalModData; GameServer initializes the world before OnServerStarted | The adapter can distinguish a captured native-load anchor from a later live table read. |
| Incoming GlobalModDataPacket parses a separate table and emits OnReceiveGlobalModData; it does not replace the authoritative map | Never copy receive payloads into the anchor. Named table requests disclose contents, so the anchor contains only nonsecret identifiers. |
| Dedicated ServerMap.QueuedSaveAll saves animals then global ModData, catches global-data errors and still prints its finishing message | Neither console text nor a general save request proves complete native pairing. |
| Dedicated save code emits no OnSave/OnPostSave; GameWindow uses those events before saving or after caught failures | Those callbacks cannot acknowledge dedicated completion. Lua save/saveGame wrappers also swallow failures and use the client/SP save route. |
| WorldDictionary's new-game flag defaults true; its setter was found in client/SP loading, not dedicated startup | Never initialize absent dog storage from OnInitGlobalModData(true). |
| VirtualAnimal saves/loads IsoAnimal including ModData; some virtualization paths reuse handles and serialized loads construct new ones | A marker has a persistence path, but handle replacement requires reconciliation. |
| AnimalInventoryItem embeds/serializes the animal; the specific IsoGridSquare carried-drop branch constructs a replacement and invokes copyFrom | The previously unknown drop route is now source-mapped. Marker copying does not establish transaction atomicity or safe generation handoff. |
| IsoAnimal.OnDeath emits OnCharacterDeath; inspected IsoDeadBody suppresses OnDeadBodySpawn on a dedicated server | Use revalidated known-handle death observation; do not rely on the corpse event for dedicated lifecycle tracking. |
| SGlobalObjectSystem can restrict private data synchronization, but registration/load can leave missing/partial data and automatic saves truncate its original file while swallowing failures | It is not adopted as a replacement private store; preserving unknown/corrupt originals takes precedence. |

Four newly inspected loose classes differ from the packaged classes: GameWindow, IsoWorld, LuaEventManager and GameLoadingState. The existing launcher/agent concern remains. The source audit verifies packaged behavior and records the differing inputs; it does not establish actual effective class loading or repair the game installation.

## Validation and remaining in-game work

[TESTED Windows offline, 2026-10-14, 0.2.0-dev.3] 206 cases pass under Lua 5.1/Lupa 2.6: 94 ownership, 75 storage, 33 pairing/lifecycle and four fresh-VM recovery phases. Tests use explicit fake events/native APIs and real disposable files. The new restart test serializes a **simulated** native anchor, creates another Lua VM with new animal handles, and checks private name/history recovery. It does not invoke native serialization, launch PZ, exercise Kahlua or prove a dedicated restart.

Coverage includes loaded-anchor schema/identity refusal, ignored client payloads/new-game hints/save callbacks, one pending checkpoint, drift during preparation, failure paths retaining old/private data, duplicate/partial event registration, startup ordering, bounded census, same-handle detachment return, sticky death, invalid native booleans and replacement/duplicate quarantine. Prior 0.2.0-dev.2 results remain historical evidence; the current suite reruns those modules with the changed lifecycle behavior.

Exact commands from repository root:

```powershell
$pairingPython = 'C:/Users/willi/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe'
& $pairingPython -B scripts/check_versions.py --root . --json
& $pairingPython -B scripts/validate_m0r.py
& $pairingPython -B scripts/validate_m0r.py --native --game-root 'E:/Program Files (x86)/Steam/steamapps/common/ProjectZomboid'
& $pairingPython -B scripts/validate_foundation.py
& $pairingPython -B scripts/validate_foundation.py --native --game-root 'E:/Program Files (x86)/Steam/steamapps/common/ProjectZomboid'
& $pairingPython -B scripts/test_domain.py
& $pairingPython -B scripts/audit_public_push.py
git diff --cached --check
```

[TESTED Windows offline] Version consistency PASS; contract/source checks STATIC PASS. All 44 original M0R input hashes and 47 input checks across the two later manifests match (some inputs overlap). Exact commit/push/CI results are reported after verification. The source inventory now includes 13 Lua modules. The validator checks only the approved event registrations/anchor access, 609 prepared English fallback entries and all 30 unchanged art files. Internal checkpoint/lifecycle status codes are server diagnostics, not untranslated player UI. No gameplay setting was added: identity/census limits and event ordering are implementation safety constraints, while the existing ownership sandbox policies still apply.

To reach an actual in-game dog save/load test, the remaining concrete prerequisites are a pristine supported client/dedicated environment, original canine native registration/assets (the existing GLB is not a native game registration), and explicit first-world allocation/anchor/marker provisioning that preserves existing saves. A disposable test world must then exercise normal native save, full process restart, same ID/name/private history, absent and duplicate carriers, unload/reload and two-client privacy. No existing save may be used as an initializer fixture. Continuous commits between native checkpoints and automatic replacement/growth/carry reconciliation remain blocked until their own evidence is established.

[RUNTIME GATE] G6 NOT TESTED; G7 BLOCKED / NOT TESTED; stable-release G8 BLOCKED. No live deployment, game/server launch, package, Workshop upload, main merge or stable tag occurred. The global AGENTS.md requires separate authorization for those runtime/deployment actions; this task implements and validates source only.
