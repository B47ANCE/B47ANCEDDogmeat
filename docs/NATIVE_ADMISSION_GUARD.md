# Server admission guard development

Project Version: 0.2.0-dev.8

Historical selected-hook checkpoint: source/validation at `6518be2aa7afaa71d70e3ff4b28b68dc01e21a63`. Its 332-test/20-module/1,015-fallback results retain that scope. The same unreleased dev.7 has since been revised; current policy, counts and blockers are in [BLOCKER_RESOLUTION_REPORT.md](BLOCKER_RESOLUTION_REPORT.md) and [SERVER_ADMISSION_GUARD.md](SERVER_ADMISSION_GUARD.md). The earlier report below is preserved.

The approved `b47dogtest` / `grey` raccoon remains the carrier. This iteration implements a complete installation and refusal path for **nine selected Lua completion hooks**. It does **not** establish a complete native admission boundary or enable multiplayer ownership. The private dog UUID, ownership and history remain recoverable through the existing paired store; an observed physical carrier remains unverified.

## Implemented boundary

`NativeAdmissionGuard` installs only in the dedicated server or the explicit local SP authority adapter. Bootstrap loads the exact vanilla action classes first. Installation validates the entire set before replacing any completion function. It retains constructor identity and parameter metadata, establishes the same class index used by the vanilla constructor, rejects inherited/missing/aliased/already-owned classes, and refuses duplicate installation. A reservation keyed by the native server function also prevents a fresh API adapter from retrying a failed process installation.

| Completion hook | Server-side source checked before vanilla mutation |
| --- | --- |
| ISPickupAnimal | Supplied native animal |
| ISAddAnimalInTrailer | Supplied native animal, including the from-hand branch |
| ISRemoveAnimalFromTrailer | Supplied native animal before reconstruction |
| ISAttachAnimalToPlayer | Supplied native animal before attachment |
| ISAttachAnimalToTree | Supplied native animal before attachment |
| ISPutAnimalInHutch | Actual server player's equipped animal item |
| ISHutchGrabAnimal | Actual hutch map member selected by its integer key |
| ISDropWorldItemAction | Actual inventory item and embedded animal |
| ISDropVehicleItemAction | Actual inventory item and embedded animal |

Every registered carrier type is refused regardless of breed, marker, native integer, death or world-presence flags. A detached parser-created carrier therefore cannot bypass a check that only accepts world animals. These checks confer no authority on public ModData. Invalid or unreadable requests return false before delegating; they do not permanently disable the process merely because a remote request was malformed.

Unrelated valid animals, ordinary dropped items and native trailer corpses retain their vanilla completion behavior. The hutch lookup uses an integer-keyed map; the key is not incorrectly capped as a list position. No scan, recursive inventory traversal, tick watchdog, respawn or retry is introduced.

Every wrapper checks the entire class/constructor/completion/index/metatable set and native authority function identities before inspection, immediately before delegated mutation and afterward. Class or method replacement, changed lookup behavior, inspection failure during an integrity check, or loss of authority permanently closes the process guard. An exception from a delegated original closes the guard and is rethrown so its actual diagnostic is retained. Side effects cannot be rolled back or retried. Displacement during an original's execution returns false and closes the guard.

`NativeRuntime` checks the guard before recovery, status, observation, census and ownership preparation. Provisioning requires an installed guard for its exact namespace/type and rechecks it at each existing transaction boundary, after construction, before world insertion and before anchor publication. If construction becomes uncertain, existing receipts/private files and any native side effect remain as evidence. No new animal is allocated on retry.

The internal status is `coverage=LUA_ACTIONS_ONLY`, `ownershipReady=false`. Neither configuration, a caller-supplied trust flag nor a mutated returned status can change it. The dedicated `NativeSession.prepareOwnership` fence remains intact. The existing SP-only file-preparation fixture is not dedicated provenance or a production gameplay endpoint.

## Source audit refinements

[VERIFIED, packaged Build 42.21 inspection] `NetTimedAction.perform` resolves the action's `complete` at offsets 10–21. Its constructor path uses cached function resolution and Lua prototype parameter metadata, so this implementation preserves every `.new` function. Constructor wrappers with generic varargs are not substituted.

[VERIFIED, packaged inspection] Timed-action inventory arguments resolve an existing container/item ID; animal arguments resolve an online-manager `AnimalID`. Equipment, attached-item and trade server paths likewise resolve existing items. Their full item-body parsing on client paths does not itself prove a server inventory import. Native `dropHeavyItems` can reconstruct an animal directly, but **is not by itself proof that an ordinary client can introduce the required server-owned inventory item**. A complete upstream import cut could make downstream native reconstruction safe; that complete cut is not certified here.

[VERIFIED, packaged inspection] The previously uncertain `NetworkPlayerAI.parse(AnimalPacket)` world-add helper is invoked by the inspected `AnimalUpdatePacket` full/update branches only under `GameClient.client`. The server branch records requests/synchronization work. That helper is not recorded as a demonstrated server clone-admission route. A separate server-reachable removal path affects liveness; it does not establish clone creation. `AddObjectToMapPacket` constructs a tile from a sprite name, rather than restoring an arbitrary animal body. `AddItemInInventoryPacket`, `AddItemToMapPacket` and `ObjectChangePacket` have client handling type 2; the default `INetworkPacket.processServer` does nothing.

These distinctions narrow the remaining audit. They do not prove all parsers, native inventories, hutches, trailers, virtual animals, queued work or save/reload paths form a closed graph. Native methods can still execute without consulting these nine Lua wrappers. No native animal load/add veto was found in the inspected registration/exposure paths.

## Restart integrity remains blocked

A fresh successful hook installation says nothing about the previous process. For example, a displaced importer could mutate native state, the engine could save it, and the process could terminate before an integrity check observed the displacement. A rejection file written only after detection does not close that interval. A tick watchdog also does not establish a pre-mutation boundary.

A possible stronger design would persist an ARMED session before admitting anything, then require a source-proved final save/quiescence seal. Missing, corrupt, failed-readback or unsealed session data would refuse automatic recovery. **That journal is not implemented or silently approximated.** No source-proved final server seal boundary has been established. In the inspected JAR, `OnServerStartSaving` and `OnServerFinishSaving` are triggered by the client-side `StartPausePacket.processClient` / `StopPausePacket.processClient` at offsets 4–6. Their names do not make them server shutdown callbacks. `ServerMap.QueuedQuit` calls `QueuedSaveAll(true)` before native teardown, but no verified Lua final-admission seal was identified at that boundary.

The threat boundary continues to trust the server operator, private files and server-installed code; this is not protection against a malicious server mod. Even for compatibility failures, this iteration does not assert crash-persistent hook integrity. The process latch is intentionally described as process-local.

Consequently, no high native integer, private origin proof, automatic marker-only upgrade or multiplayer ownership permission is minted. Legacy records are preserved unchanged. A matching marker or native integer cannot choose the authoritative private record. The fresh-VM regression explicitly loses the old process latch, installs new guards, recovers the retained UUID and still refuses dedicated ownership without writing.

## Configuration and compatibility

The restrictions are technical safety conditions, not configurable gameplay balance. An option allowing these transitions would invalidate their admission assumptions and is not exposed. `B47ANCEDDogmeat.PersistenceTestMode` remains the sole default-off, server-authoritative test setting; existing localization and fallback policy are unchanged. Snapshot/marker/ownership schemas remain 1. Existing records are not migrated or reset. The model, original art checkpoint, user-supplied branding and unrelated vanilla source are unchanged.

The wrappers intentionally affect the mod's registered carrier types even when the diagnostic menu is disabled. Other server mods that replace these classes or constructors are incompatible until reviewed; detected displacement closes the guard. Restoring a function later does not reopen it. This is development source, not a claim of compatibility with every other mod.

## Validation and required continuation

[TESTED Windows offline, 2026-10-14, Lua 5.1 / Lupa 2.6] **332 tests PASS, zero failures**, including 56 admission cases and two new fresh-VM phases. All 20 current Lua sources compile offline. Version/contract/source checks pass; development assembly has exact source parity across 111 files. All 1,015 fallback entries across 29 languages and 30 frozen art files match. Native checks rehash 44 original M0R inputs and 251 checks across later manifests, including 89 in the admission manifest; overlapping inputs are not counted as unique evidence. Fixtures use fake native/UI/network APIs and real disposable files; fresh restart phases use separate Lua VMs. No native packet was sent, and no PZ process or real player save was opened.

Coverage includes each managed refusal and unrelated delegation, markerless/dead/detached carriers, ordinary item/corpse preservation, full integer hutch keys, constructor preservation, duplicate/aliased installation, missing/displaced hooks, malformed input, authority loss, inspection/delegation exceptions, displacement during execution, provisioning uncertainty, dedicated ownership refusal and fresh-VM loss of the process latch. All current Lua sources compile offline. Native provenance is reproducibly rehashed through `native-admission-evidence.json`; raw disassembly/classes remain ignored locally.

```powershell
$admissionPython = 'C:/Users/willi/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe'
& $admissionPython -B scripts/check_versions.py --root . --json
& $admissionPython -B scripts/validate_m0r.py --native --game-root 'E:/Program Files (x86)/Steam/steamapps/common/ProjectZomboid'
& $admissionPython -B scripts/validate_foundation.py --native --game-root 'E:/Program Files (x86)/Steam/steamapps/common/ProjectZomboid'
& $admissionPython -B scripts/test_domain.py
& $admissionPython -B scripts/build_loadable.py --check
& $admissionPython -B scripts/audit_public_push.py
git diff --cached --check
```

Required continuation is a source-proved complete upstream admission cut and prior-session integrity strategy, followed by disposable-save tests on a pristine supported client/dedicated build. Test native save/full restart, streaming, reconnect, copies before originals, altered markers saved before restart, duplicated native integers, representation changes, world/private rollback and interruption. The current modified loose-class/launcher installation remains an effective-runtime gate. Lua-only alternatives require explicit design review; no custom Java/JAR bridge is permitted.

A safe Lua-only fallback is to retain the private logical dog/ownership history and require explicit operator reconciliation before associating a physical carrier after restart. That would change the automatic same-native-dog contract and is a proposal only; no adoption, replacement or new operator workflow is implemented here.

**G6 NOT TESTED; G7 BLOCKED / NOT TESTED; stable-release G8 BLOCKED.** No game/server launch, deployment, release archive, Workshop upload, stable tag or main merge is part of this iteration.
