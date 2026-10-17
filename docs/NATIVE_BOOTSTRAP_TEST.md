# Loadable native persistence diagnostic

Project Version: 0.2.0-dev.7

Current guard integration: [server admission guard](NATIVE_ADMISSION_GUARD.md) adds nine completion guards and guarded recovery/provisioning. This report retains its earlier implementation/test scope; complete native provenance and dedicated ownership remain blocked.

This report retains the 0.2.0-dev.4 bootstrap implementation/evidence scope (259 tests). The current [identity investigation](NATIVE_IDENTITY_AUTHORITY.md) adds independent private-ID reporting and adversarial tests; this document header identifies the current contract edition, not a renewed native test.

User decisions, 2026-10-14: technical Mod ID **B47ANCEDDogmeat**; use a **raccoon** as the temporary save/load test carrier; leave the original Shepherd model unchanged. This checkpoint supplies loadable source, native registration and explicit first-store provisioning. **PZ has not been launched and in-game save/load is NOT TESTED.** This is a disposable-world diagnostic, not a playable dog-training release.

## Concrete source and load path

Authoritative Lua remains in src/domain and src/native, with three new entries under src/bootstrap. Metadata is src/metadata/mod.info and sandbox-options.txt. scripts/build_loadable.py maps those sources into a new B42 development tree: common/, 42/mod.info, server authority modules, shared registration, client menu and shared translations. It refuses an existing output directory, verifies exact source parity and never installs, overwrites/removes existing output, creates an archive or uploads. Its check mode cleans only its own disposable test tree. Generated trees are not source. No vanilla assets or code are distributed.

Shared registration adds b47dogtest/grey through an independent deep runtime copy of vanilla raccoonboar, its avatar and carcass-parts definitions. The single adult stage has no successor; sex is male, no mate/baby type. The ordinary pickup, pet and attachment menus are disabled. Native trailer/feed paths can ignore definition flags: native raccoon interactions, needs, movement, sounds and carcass yields remain. Carry/trailer/corpse continuity and trained canine behavior are unsupported. The user-approved raccoon is diagnostic presentation, not acceptance of the original canine asset contract. All 30 original art files are unchanged.

Server bootstrap installs the adapter before native initialization. Dedicated uses OnServerStarted; explicit SP local authority uses OnGameStart. Both wait for OnInitGlobalModData and ignore its unreliable new-game hint. Remote clients install no authority bootstrap. SP responses use a local callback because native sendServerCommand does nothing in SP. No OnTick scan, forced save, save-completion inference, receive-to-anchor copy or automatic population spawn exists.

## Explicit initialization and recovery

The only runtime-defined setting is **B47ANCEDDogmeat.PersistenceTestMode**, boolean, default false, server authoritative, localized in all 29 supported languages with explicit English fallback. Its native definition and existing-save policy are inventoried in src/metadata/runtime-options.json. Turning it off blocks new diagnostic requests; existing native/private recovery remains read-only and records/carriers are retained. The older 79-setting catalog remains future design data under its original proposed identifiers; none of those settings is registered by this diagnostic.

An alive native player with Capability.AnimalCheats on dedicated, or the local SP authority, can open the context menu. The server checks the current setting, actual event player, startup state and existing anchor/receipt before issuing a one-use confirmation challenge. The challenge is bound privately to that player and exact native save-directory locator, expires after 120 seconds, and is consumed before initialization. Network intent contains only protocol, challenge and a fixed fresh-disposable-world acknowledgement. Coordinates, animal type, breed and identity never come from the client. Inspect requests have a one-second per-player limit; at most 128 player contexts are retained.

**Fresh-world recognition is an explicit operator assertion, not an automatic filesystem proof.** The confirmation says to use a new disposable test world. Absence alone never authorizes initialization. Never confirm against an established gameplay save, copied save or a world with lost storage. The adapter refuses occupied/malformed anchors, existing provisioning directories, duplicate UUIDs and occupied world directories. A checksum collision in the locator's receipt path refuses; it never selects another directory to bypass residue.

The bounded transaction is:

1. Close the process latch. Generate distinct world, dog, binding, checkpoint and allocation UUIDs.
2. Write and reopen a private attempt receipt at B47ANCEDDogmeat/provision-<locator-checksum>/slot-a.json. It retains the exact locator and attempt IDs. It is never a gameplay/native-save success receipt.
3. Write and verify both identical sequence-1 ROOT snapshots in B47ANCEDDogmeat/<world-UUID>/slot-a.json and slot-b.json. They contain one expected LIVE identity, a fixed test name and private test provenance. LIVE here is the expected record binding; an absent carrier never authorizes a spawn.
4. Recheck authority, locator, anchor absence, player/tile, receipt and roots. The broker checked the actual player's role before this synchronous transaction. Construct one fixed registered carrier on the player's server-observed ground-floor tile using integer coordinates. Native construction may register an instance before addToWorld.
5. Validate type/breed/liveness, stamp only the nonsecret five-field marker, and call addToWorld. Recheck marker, native state and all private bytes.
6. Create the anchor last with ModData.create, which refuses occupied names. Publish only schema/worldId/checkpoint and verify table identity. Report WAITING_INITIAL_NATIVE_RELOAD.

No uncertain write or constructor is retried. Errors preserve receipt, partial roots and any created animal. A later restart with residue, missing/corrupt roots or lost anchor refuses initialization; it never repairs, deletes, generates new identity or respawns. Reusing a save name also retains its prior receipt and requires separate recovery review. The adapter has no exclusive-create/fsync primitive: this protocol assumes a single authority process and no concurrent external writer to its cache namespace. Readback is not power-loss durability or atomic coordination with native saves.

Only a fresh native load can select the exact checkpoint; discovery then compares loaded carrier markers to private records. The menu reports loaded marker matches/quarantined observations and the diagnostic dog ID. Unloaded or missing carriers remain unavailable. The loaded census is explicit/on-startup only and is not a whole-world uniqueness proof. Successful native save ordering, complete native animal recovery and privacy still need in-game evidence.

## Newly established multiplayer authority blocker

[VERIFIED packaged Build 42.21 inspection] ObjectModDataPacket accepts logged-in client packets that load/wipe an animal's ModData. MovingObject resolves animal references through the online-ID manager; its consistency check only establishes a non-null object. Therefore an exact loaded marker match **cannot prove identity provenance**. A client can forge/copy a public marker without changing the private file.

NativeSession.prepareOwnership now refuses **UntrustedNativeMarker on dedicated**, including when every marker field matches. No deployed ownership/reward/training/gameplay mutation endpoint exists. The diagnostic initialization endpoint requires native admin capability and creates only its explicit test carrier. MATCHED means observed bytes match a retained record; it unlocks no multiplayer gameplay action. The offline SP prototype can still exercise local private ownership preparation, but the UI exposes only Inspect/Provision and the old one-pending-checkpoint limit remains.

No authenticated durable native identifier was established by this bootstrap audit: default animalId is small/random, online ID is transient, and virtualId is mutable native state. The later identity investigation verifies that Lua can assign a larger animalId; that corrects the allocation limitation but does not by itself prove secure provenance. This blocks production identity/ownership until an independently validated Lua-only authority design exists. A source/CI pass cannot clear this blocker. Native trailer/pickup flags and other animal packet handlers are not a security boundary either.

## Evidence and validation

[native-bootstrap-evidence.json](native-bootstrap-evidence.json) records 44 new-scope inputs with exact hashes/byte sizes, overlapping older manifests where appropriate. Key sites: GlobalModData.create exists check bytecode 2 / nil return 17 / insertion 30; GlobalObject.cacheFileExists source 2563–2569 (relative to cache/Lua); ClientCommands.lua 753–760 (native capability and construction); ObjectModDataPacket.parse load 75 / wipe 139; MovingObject animal lookup 19–38; ButcheringUtil.lua 18/27 (required parts entry). GameServer shared/server Lua load precedes world initialization; OnGameStart is IngameState.enter bytecode 199–202. These are packaged/source observations, not effective loading proof.

[TESTED Windows offline, 2026-10-14, 0.2.0-dev.4] **259 tests PASS**, Lua 5.1/Lupa 2.6: 94 ownership, 75 storage, 33 pairing/lifecycle, 46 provisioning/broker, one registration fixture, four bootstrap/menu flows and six fresh-VM recovery phases. All 19 Lua sources compile in Lua 5.1. Fake native/UI/network APIs and simulated native serialization are explicit; file tests use real disposable directories. Fresh VMs recover the exact ID/name/private test provenance without a new spawn. Missing/invalid state, drift, unauthorized callers, expired/replayed challenges, fast confirmation and partial failures are covered. Registration fixtures verify no vanilla table mutation and complete independent avatar/parts copies. No Kahlua, rendering, real network or PZ save was exercised.

Exact commands from repository root:

```powershell
$bootstrapPython = 'C:/Users/willi/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe'
& $bootstrapPython -B scripts/check_versions.py --root . --json
& $bootstrapPython -B scripts/validate_m0r.py --native --game-root 'E:/Program Files (x86)/Steam/steamapps/common/ProjectZomboid'
& $bootstrapPython -B scripts/validate_foundation.py --native --game-root 'E:/Program Files (x86)/Steam/steamapps/common/ProjectZomboid'
& $bootstrapPython -B scripts/test_domain.py
& $bootstrapPython -B scripts/build_loadable.py --check
& $bootstrapPython -B scripts/audit_public_push.py
git diff --cached --check
```

Current checks: version consistency PASS; contract/source/layout checks STATIC PASS; 44 original M0R hashes and 91 later-manifest input checks match; 1,015 fallback entries across 29 languages and 30 frozen art hashes match. The loadable tree contains 108 files plus common/. Exact push and CI results are reported only after verification. Historical 0.2.0-dev.3/0.2.0-dev.2 and art evidence retain their actual scope and observed versions.

## Operator runtime procedure — not executed

After separately authorized deployment to a pristine supported Build 42.21 environment:

1. Enable B47ANCEDDogmeat and Persistence Test Mode in a **new disposable world with a unique save name**. On dedicated, use an account with native AnimalCheats capability and a second unauthorized observer.
2. On a loaded ground-floor tile, right-click and choose Dog save/load test. Read the fresh-world confirmation and accept once. Expect one raccoon test carrier and a pending-reload message; a second request must not create another.
3. Let the ordinary native save complete, quit normally and fully restart the process with the same mod/config/save/cache. No tool-provided success message substitutes for this step.
4. Open the menu again after the area loads. Confirm the same dog ID, a marker match and no second spawn. Independently verify retained private name/history locally without publishing private cache data. Missing carrier means investigate, never initialize again.
5. In disposable copies, test interrupted writes, removed/corrupt slots, missing anchor, copied/forged markers, absent/unloaded carriers, death, rejoin and full dedicated restart. The unauthorized client must receive no challenge/private details and must never provision. Forged marker diagnostic matches must never unlock ownership.
6. Record actual logs/build/commit/environment and distinguish SP from dedicated. Trailer/carry and production ownership remain unsupported, even if the happy-path save test passes.

The inspected installation has differing loose classes and an agent-enabled launcher; no files were repaired or executed. Effective/pristine loading remains an operator gate. **G6 NOT TESTED; G7 BLOCKED / NOT TESTED; stable-release G8 BLOCKED.** No deployment, game/server launch, Workshop upload, main merge or stable tag is part of this checkpoint.
