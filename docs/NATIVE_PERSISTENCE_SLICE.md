# Native observation and private save preparation

Project Version: 0.2.0-dev.4

Current implementation changes and the client-writable marker authority blocker are recorded in [loadable persistence diagnostic](NATIVE_BOOTSTRAP_TEST.md). Dedicated ownership preparation is disabled; the older preparation results below remain historical scope.

Historical implementation checkpoint: 0.2.0-dev.2, 2026-10-14. Current headers identify the document edition; the results below retain their tested version. The later [native pairing/lifecycle adapter](NATIVE_PAIRING_LIFECYCLE.md) adds explicit native event installation and same-handle detachment recovery. This preceding checkpoint connects a read-only native animal adapter to private identity matching, ownership proposals and file-backed snapshot preparation. It is an **unregistered prototype**, not a playable dog or an automatic persistent-save integration. Model work remains deferred; all 30 frozen art files are unchanged.

## Implemented path

`NativeSession.open` requires an explicit namespace, native type/breed allowlist, world UUID and trusted operator-paired checkpoint. It opens both private slots and copies their validated baseline. `observe` reads an actual `IsoAnimal` only on the server and compares its public marker against that private baseline. `prepareOwnership` uses the existing ownership rules with a trusted server context, reobserves the animal immediately before preparation, appends a private transition event, then writes and reads back the inactive slot. Its success is named `PREPARED_READBACK`; it never means a native or durable gameplay commit.

Authoritative files are enumerated in [source-inventory.json](../source-inventory.json): eight pure Lua domain modules, three native adapter/coordinator modules, prepared localization, and tests. There are no event registrations, network endpoints, native definitions, spawned animals, marker writes, gameplay projections sent to clients, or loadable mod metadata. The adapter takes explicit allowlists rather than inventing final species/breed IDs. `B47Dog` is an internal module path; the technical Mod ID and animal namespace remain provisional.

The future authenticated broker must derive account, character episode, session, current configuration, reach/visibility and transfer-target consent from verified server evidence. Those context values are not client arguments. The coordinator sets only the matched binding/recovered-store flags. It does not authenticate a native player, reconcile a native save, or provide a transaction commit. Existing HandlerPermissionMode and OwnerAfterCharacterDeath policies still apply; this slice adds no configurable gameplay behavior. File, recursion, identity and counter limits are internal safety bounds.

## Identity and privacy

The reader checks server role, `instanceof`, world membership and `isDead()==false`, then the allowed native type and breed. The small native animal ID is a diagnostic hint only. Its copied marker permits exactly schema, worldId, dogId, bindingGeneration and bindingToken. No ACL, personality, medical data, history or discoveries are placed in native ModData. Source inspection confirms animal update packets serialize native animal state including ModData; the marker must be treated as public and untrusted.

The registry requires a private LIVE ownership record and matching world, dog, generation, native type/breed and accepted binding token. It preserves older accepted binding tokens independently of the global file checkpoint. Missing/foreign records, observed duplicate handles, invalid or inconsistent marker changes, death or disappearance quarantine the affected association. Switching between already accepted tokens for the same binding remains valid. Quarantine is sticky. At 1,024 distinct handles or IDs, the next distinct value stops the entire session with CAPACITY while retaining existing evidence; one handle cannot grow quarantine indefinitely.

A match proves only the observations seen in this session. It cannot establish absence of unloaded duplicates or safe reload/replacement transitions. A new handle for an already observed ID quarantines conservatively. There is no adoption, allocation, tombstone creation, respawn or generation advance. Carry/release, growth, trailer/corpse conversion and reconnect/restart still need their specific source and runtime proof.

## Private format and preparation

`Codec` is original Lua for a strict canonical JSON subset: objects with string keys, booleans, signed integers from -2147483647 through 2147483647, and validated UTF-8 strings. It emits sorted keys and ASCII bytes with Unicode escapes. Arrays, null, floats, duplicate keys, alternate encodings, malformed Unicode, cycles and metatables are refused. Bounds are 1 MiB per encoded value/file, 16 KiB per string, 256 bytes per key, 8,192 values and depth 16. The native reader consumes at most MAX_BYTES+1 characters using `BufferedReader.read()` and closes even on failure. It does not allocate an unbounded line.

Snapshot schema 1 wraps a body with an Adler-32 corruption checksum. The body contains worldId, saveLocator, checkpoint, predecessor, sequence, allocation epoch/highwater, record count, canonical payload length/checksum and payload. At most 256 records are accepted. Ownership and private binding subrecords are validated; other bounded private domains are preserved verbatim through canonical encoding. Unknown envelope schemas/fields are refused; no migration is implemented. Checksums detect accidental corruption and are not authentication. Schema identifiers are independent of project SemVer.

The file adapter uses only `<cache>/Lua/<explicit namespace>/<world UUID>/slot-a.json` and `slot-b.json`. Native `getCurrentSaveName` is a locator, not world identity; it is compared before every operation and never inserted into a path. Readers use createIfNull=false. Writers use createIfNull=true and append=false only after store validation. Account names, client values and arbitrary paths cannot select files. Actual filesystem permissions remain an operator/runtime gate.

Both slots must be valid. Selection requires the exact checkpoint in a trusted `OperatorPaired` assertion; the largest sequence is never chosen automatically. Identical twin snapshots or a direct validated predecessor are accepted. An unpaired newer prepared slot yields PreparedPending and blocks writes. Missing, corrupt, foreign, future-schema or ambiguous files remain untouched. The implementation is deliberately stricter than the broader recovery design: it does not repair a damaged inactive slot from a valid predecessor.

Preparation permits only ownership changes. It retains all dog records, binding generations, phases and other private fields; requires matching ownership/ACL revision increments; preserves allocation highwater; and permits only append operations to ownershipEvents/checkpointLedger. Removal, rollback, arbitrary lifecycle changes and history replacement are refused. The store rereads both slots before writing, locks the session before I/O, writes only the inactive slot, closes and compares its reopened canonical bytes. It never retries an uncertain write, promotes the prepared state, or changes the selected baseline. The appended event records preparation, not a committed receipt or reward.

This is a single-coordinator prototype. Disk rechecks are not atomic compare-and-swap and cannot exclude another process writing between check and write. No filesystem lock, atomic rename, fsync or reliable PrintWriter error query is established. Immediate readback can find some write failures but cannot prove survival of process crash or power loss. There are no save-event hooks or automatic native/private checkpoint pairing. Supplying an operator assertion is not evidence that a native save completed. Live writes remain gated until exclusive ownership and a valid native pairing procedure are established.

No production initializer exists: missing files do not create a new world or empty store. The tests explicitly seed synthetic paired snapshots. A future first-spawn path must establish world identity, persist an allocation reservation, create exactly one native representation, and prove pairing before enabling gameplay. No real player save is used as a fixture.

## Native evidence

[The dated input manifest](native-persistence-evidence.json) records installed Build 42.21 hashes, exact signatures and inspection locations for native readers, file APIs, UUIDs, exposure and public animal serialization. [VERIFIED: source/class inspection] includes `IsoAnimal`, inherited `IsoGameCharacter.isDead`, `AnimalBreed.getName`, GlobalObject file/role/UUID functions and exposed `BufferedReader.read():int`. The installed JRE is Azul 25.0.1+8-LTS. The reader method is directly declared and its EOF is -1. Inspection uses local source and offline class tools, never custom runtime Java or injected classes.

The original 44 M0R input hashes were rechecked without changing the dated evidence. The pristine effective runtime remains unknown: loose classes differ from packaged classes and the observed client launch configuration includes an external agent. Nothing here changes the game installation or proves which implementation an actual client/server loads. Native API availability under Kahlua, Lua userdata/table behavior and file permissions require dedicated execution.

## Validation record

[TESTED Windows offline, 2026-10-14, 0.2.0-dev.2] **171 tests pass, zero failures**, using actual Lua 5.1 through Lupa 2.6: 94 ownership tests, 75 storage/native-adapter tests and two fresh-VM recovery phases. Coverage includes Unicode/canonical decoding, corrupt/future/foreign snapshots, predecessor/pairing refusal, unchanged selected slots, swallowed/partial/exceptional writes, close failures, size limits, path/role/save-locator checks, ownership/history rollback prevention, native death/duplicates/ID-capacity refusal, final reobservation and private history retention.

The native APIs are explicit fakes. File adapters write real disposable temporary files; recovery uses separate Lua VMs sharing only those files. An operator checkpoint transition is simulated deliberately. This tests Lua behavior and file persistence across those VMs, not Kahlua, a PZ save, a server restart, crash consistency, native pairing or multiplayer correctness. No game cache, player save, server or native source file was changed.

Exact commands from repository root:

```powershell
$featurePython = 'C:/Users/willi/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe'
& $featurePython -B scripts/check_versions.py --root . --json
& $featurePython -B scripts/validate_m0r.py
& $featurePython -B scripts/validate_m0r.py --native --game-root 'E:/Program Files (x86)/Steam/steamapps/common/ProjectZomboid'
& $featurePython -B scripts/validate_foundation.py
& $featurePython -B scripts/validate_foundation.py --native --game-root 'E:/Program Files (x86)/Steam/steamapps/common/ProjectZomboid'
& $featurePython -B scripts/test_domain.py
& $featurePython -B scripts/audit_public_push.py
git diff --cached --check
```

[TESTED Windows offline] Version consistency PASS; M0R and source validation STATIC PASS. The original 44 native inputs and the new 13-input manifest all match their recorded hashes. The source check covers 11 Lua modules, 609 English fallback entries across 29 languages, case-correct requires, restricted source boundaries and 30 frozen art hashes. Native rehashing is read-only source provenance. Public CI repeats portable offline checks and the Lua/file tests on Ubuntu; it has no installed game and proves no Linux PZ behavior. Git commit/push and exact-head CI results are reported separately after verification.

[RUNTIME GATE] G6 NOT TESTED; G7 BLOCKED / NOT TESTED; stable-release G8 BLOCKED. Remaining gates: pristine native loading/authority, original enabled-state assets/registration, actual native account/episode adapter, identity through lifecycle transitions, explicit first-world initialization/reservation, native/private save completion/pairing, exclusive commit/replay handling, restart/reconnect and two-client privacy/permission tests. No package, deployment, game/server launch, Workshop publication, main merge or stable tag occurred.
