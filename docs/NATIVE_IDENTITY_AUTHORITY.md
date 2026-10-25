# Multiplayer identity authority investigation

Project Version: 0.2.0-dev.11

The approved `B47ANCEDDogmeat` / `b47dogtest` / `grey` raccoon remains the diagnostic carrier. The model is unchanged. This report retains the 0.2.0-dev.5 identity audit scope, with later source refinements identified below. The current [server admission guard](NATIVE_ADMISSION_GUARD.md) refuses selected Lua representation transitions but does not certify native provenance. **Automatic multiplayer carrier admission remains blocked; no game or server was launched.**

## Implemented safe boundary

The world UUID, dog UUID, ownership and retained history remain in the existing server-private two-slot store. Recovery still requires the exact native anchor, save locator and compatible checkpoint chain. No format migration, reallocation, automatic adoption, automatic replacement or new gameplay endpoint is introduced.

`NativeSession.identitySummary()` returns a detached summary of the recovered private snapshot: record count, the dog UUID only when exactly one record exists, and `bindingVerified=false`. No owner/account, ACL or private history is projected. Native observations and census results also explicitly carry `bindingVerified=false`, including `MATCHED` observations. The dedicated preparation fence still refuses before any ownership proposal or private write; supplied trust flags cannot override it. The existing local SP preparation fixture is separate and does not prove network authority.

The authorized diagnostic broker now takes its displayed dog ID from that private summary, not from the set of observed markers. Missing/unloaded carriers and erased/foreign/copied markers therefore cannot hide or choose the retained dog UUID. Census counts still describe only currently loaded observations. With multiple records the menu reports their count and no arbitrary single dog ID. The updated diagnostic wording has explicit English fallbacks in all 29 languages.

This preserves and exposes logical identity recovery without pretending to solve physical identity. A private record's expected `LIVE` state does not establish an existing, unique or authenticated world carrier. After restart, the mod does not infer that a public marker is genuine because it came from a save: client changes may already have been saved. Transient quarantine loss cannot promote a byte match into multiplayer permission.

## Native candidate and threat model

[VERIFIED packaged Build 42.21] `IsoAnimal.getAnimalID()` and `setAnimalID(int)` are Lua-exposed public methods. The setter is not restricted to vanilla's random initialization range. `init` chooses `Rand.Next(10000)` at offsets 44–50; `save(ByteBuffer,boolean,boolean)` writes the integer at 206 and `load` restores it at 270. `VirtualAnimal.save/load` delegate animal serialization at 179/197. `copyFrom` copies the integer at 99, and growth preserves it through `AnimalData`'s setter call at 304. This corrects an overly broad reading of the earlier “small/random hint” description: **server allocation above the vanilla range is technically possible**.

The public [IsoAnimal API reference](https://projectzomboid.com/modding/zombie/characters/animals/IsoAnimal.html) corroborates the methods; the exact installed packaged bytes are the authority for this investigation. Lua exposure was checked through `LuaManager$Exposer` (737/740) and `LuaJavaClassExposer.exposeMethods` (34–65), including the absence of `HiddenFromLua` on the accessors.

A private allocator plus assigned native integer could resolve marker transplant only if ordinary clients cannot overwrite, clone or admit a physical carrier with that integer. Default-range separation proves none of those properties. Native full snapshots disclose the integer and other candidate fields. Type, breed, position, name, genome or another public signature cannot independently prove origin. A valid signed marker can be replayed intact; signatures do not tie it to a unique physical body.

The trust boundary assumes a trusted server/operator, private cache access and server-installed mods. An administrator with native animal cheats is not an ordinary hostile client. Server files or other server mods are not protected by this Lua module. Ordinary client packets, saved client-writable state and duplicate or missing representations must remain untrusted.

## Packet inspection and limitations

[VERIFIED packaged inspection] `ObjectModDataPacket` can replace/wipe animal markers for logged-in clients. That established blocker remains. `AnimalCommandPacket` requires `AnimalCheats` before parsing; its server processing is not evidence that an ordinary client can execute the client-side pickup/trailer branches. Similarly, client-receive-only inventory packets do not establish server injection.

Some ordinary-client parsers deserialize arbitrary inventory items before checking their subtype. `AnimalInventoryItem.load` constructs an animal and restores its serialized integer, but that fact alone is **not** a physical clone proof. Its zero-coordinate constructor bypasses `cell.addMovingObject`; load/init register only an online-manager object. `IsoCell.getAnimals` enumerates `objectList`, and `isExistInTheWorld` requires the exact instance in its square's moving-object list. The present adapter requires both. Native animal saving scans the cell list too. A further world-admission route must be demonstrated before calling such a detached object a copied world dog.

The later trailer review found a source-supported admission concern, beyond mere detached-object registration: the server completion path does not establish the expected source-inventory condition before `BaseVehicle.addAnimalFromHandsInTrailer` mutates the trailer. That method adds the supplied animal and vehicle association before looking up the matching inventory item; an absent source only logs an error and does not roll back the insertion. Native trailer reconstruction preserves `animalId`. This rejects the assumption that an assigned integer is intrinsically protected. It is static defensive analysis, not a tested exploit or a claim that all affected behavior is reachable on the effective installation.

Wrapping only animal transport actions is insufficient. `IsoGridSquare.AddWorldInventoryItem(InventoryItem,float,float,float,boolean,boolean)` dispatches on `AnimalInventoryItem` before either boolean matters, constructs an animal, copies its state and adds it to the world. Generic item-drop and vehicle-drop actions reach it. Native `IsoGameCharacter.dropHeavyItems()` also reaches that method directly on the non-client path, before its notification events; wrapping Lua actions or a Lua convenience function cannot intercept this internal native call. Hutch restoration/release is another native representation boundary. Admission integrity must cover the underlying imported/equipped/container state, not just visible animal menus.

The counterexamples were checked carefully: pickup's completion explicitly repeats a world-presence check; player reconnect loads server-owned character data in inspected paths; `AddItemToMapPacket` is client-receive-only. Those sites are not reported as confirmed ordinary-client server injection. The later 0.2.0-dev.7 review resolves the previously unknown synchronization helper's inspected invocation branches as client-only. It also verifies existing-item resolution in equipment/trade/attached-item server paths: the native heavy-drop call alone does not establish an ordinary-client import. Complete upstream coverage remains uncertified; see the current guard report for exact distinctions.

**Disposition:** no safe automatic physical rebind has been established in the current Lua-only design. At the original 0.2.0-dev.5 audit checkpoint no wrappers were installed. The current 0.2.0-dev.7 adds nine explicit server completion guards with an honest LUA_ACTIONS_ONLY status; it still does not allocate high native integers or enable multiplayer ownership from them. This is not a claim that every future Lua-only design is impossible. A candidate must first demonstrate a complete, pre-mutation admission boundary and prior-session integrity, then pass native restart/streaming tests. Selected wrappers must never be presented as closing that entire authority gap.

## Safe continuation and acceptance criteria

The established Lua-only continuation keeps permanent logical identity, owner/handler data and history in the private store and refuses native admission on ambiguity. That safe subset is implemented and tested offline. It preserves data while the raccoon remains diagnostic. It does **not** fulfill automatic ownership of the same native dog after restart.

Two larger approaches remain proposals, not implemented scope changes:

- A restricted live-carrier design with private allocation plus a verified native key: prove every import/reconstruction route is guarded before mutation, scope guards to this mod's type, verify installation before recovery, and permanently stop admission if a guard is missing/displaced. No existing marker-only carrier may be upgraded automatically. Both direct native and Lua paths must be accounted for.
- A persistent logical dog with separately reconciled presentation carriers: preserve private identity through restart and require explicit, evidence-backed operator reconciliation before a new physical association. Automatically replacing the animal would change native death/transport/lifecycle semantics and is not silently substituted for the requested same-dog contract.

Server-private storage cannot prevent a client from altering public carrier data, and a new sandbox toggle cannot turn an unsafe identity scheme into a safe one. No new gameplay setting is needed for this diagnostic/security boundary. Existing PersistenceTestMode remains the sole default-off runtime option.

## Reproducible source evidence

[native-identity-evidence.json](native-identity-evidence.json) records 71 inspected packaged-class/installed-Lua inputs with exact hashes and sizes. Original raw classes/disassembly remain ignored locally and are not distributed. Key defensive review anchors are the native-ID serialization/exposure sites above, `BaseVehicle.addAnimalFromHandsInTrailer` mutation-before-source-check ordering, `NetTimedAction.perform`'s Lua completion invocation, `IsoGridSquare.AddWorldInventoryItem`'s item-class dispatch, and `IsoGameCharacter.dropHeavyItems`'s direct native calls. Each is source evidence, not a runtime acceptance result.

## Validation and required runtime checks

**Historical 0.2.0-dev.5: 274 tests PASS, zero failures**, including 13 new authority-boundary cases and two new fresh-VM phases. All 19 Lua sources compiled under the offline Lua 5.1 interpreter; no source or asset registration was added then. Version/contracts/source checks passed; source assembly verified 108 files, 1,015 localized fallback entries matched, and all 30 frozen art files remained unchanged. Native verification rehashed 44 original M0R inputs and 162 checks across the later manifests, including 71 inputs for that investigation. Current source/tests/assembly are recorded separately in [the guard report](NATIVE_ADMISSION_GUARD.md).

[TESTED Windows offline, 2026-10-14] Tests use Lua 5.1 through Lupa 2.6 and real disposable files. Adversarial fixtures exercise a clone observed first, maximum positive native integer, erased/foreign/duplicate markers, dead/detached carriers, empty and subsequently unloaded censuses, forged trust flags, private-summary mutation and multiple retained records. Separate Lua VMs retain the private UUID while losing transient quarantine, and still refuse ownership. These are boundary fixtures, not a native packet exploit or real PZ save.

Exact commands from repository root:

```powershell
$identityPython = 'C:/Users/willi/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe'
& $identityPython -B scripts/check_versions.py --root . --json
& $identityPython -B scripts/validate_m0r.py --native --game-root 'E:/Program Files (x86)/Steam/steamapps/common/ProjectZomboid'
& $identityPython -B scripts/validate_foundation.py --native --game-root 'E:/Program Files (x86)/Steam/steamapps/common/ProjectZomboid'
& $identityPython -B scripts/test_domain.py
& $identityPython -B scripts/build_loadable.py --check
& $identityPython -B scripts/audit_public_push.py
git diff --cached --check
```

Before approving any physical identity scheme, use a pristine supported build and disposable saves to test controlled allocation, native save/full restart, stream-out/in, ordinary observer rejoin, a clone presented before its original, altered markers saved before restart, duplicated native integers, world-only/private-only rollback, and interrupted transitions. Required acceptance is the same retained logical dog, exactly one authenticated physical representation and no ownership grant to a copy. The current diagnostic must keep reporting the retained private ID without granting gameplay authority.

**G6 NOT TESTED; G7 BLOCKED / NOT TESTED; stable-release G8 BLOCKED.** Existing modified loose classes and an agent-enabled launcher remain an effective-runtime gate. No deployment, game/server execution, Workshop publication, release archive, tag or main merge occurred.
