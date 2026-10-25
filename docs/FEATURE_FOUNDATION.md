# Ownership and inspection feature foundation

Project Version: 0.2.0-dev.11

Current guard integration: [server admission guard](NATIVE_ADMISSION_GUARD.md) adds nine completion guards and guarded recovery/provisioning. This report retains its earlier implementation/test scope; complete native provenance and dedicated ownership remain blocked.

Current integration: [loadable persistence diagnostic](NATIVE_BOOTSTRAP_TEST.md) adds only an admin save/load test using the approved raccoon carrier. Ownership gameplay is not deployed; dedicated native ownership preparation is blocked because marker provenance is untrusted. The following domain report remains its original 0.2.0-dev.1 scope.

The user authorized feature work on 2026-10-14 and deferred model refinement. This document describes the ownership foundation introduced and tested at 0.2.0-dev.1. It implements **engine-independent Lua logic**, with actual offline Lua tests. Current native observation and private file preparation are documented separately in [NATIVE_PERSISTENCE_SLICE.md](NATIVE_PERSISTENCE_SLICE.md). It is not yet a playable mod. The later [native pairing/lifecycle adapter](NATIVE_PAIRING_LIFECYCLE.md) supplies explicit event installation; no automatic bootstrap, authenticated-player broker, gameplay commit, command endpoint or UI is installed.

## Implemented behavior

- Claim an unowned dog using the authenticated actor supplied by the future server adapter. A reserved owner account can reclaim on a new character under RequireNewClaim; a different account cannot take over.
- Name a dog with bounded, validated UTF-8 literal text. Only the current owner can rename it. Names are trimmed, limited to 48 Unicode code points/192 bytes, and reject malformed UTF-8, control/bidirectional formatting characters and angle-bracket markup. Percent signs and ordinary international names remain literal text.
- Grant and revoke account-based handler access. OwnerOnly suspends grant use without deleting grants or relationship history. Handlers cannot rename, grant, revoke or transfer.
- Transfer ownership to a server-resolved, consenting, reachable living target. The dog ID and binding generation remain unchanged; all old grants are removed. Historical relationships and discoveries belong to separate private records and must be retained by the adapter.
- Resolve owner/handler/observer roles from current private state and server configuration. Account case is significant. Character-specific discoveries are never inherited merely because an account retains ownership.
- Build fresh inspection projections from a positive allowlist. They include current version references, coarse visible state, eligible action codes and only this world/dog/account/character episode's discovered relationship/cues. The module does not generate discoveries, train cues, infer hidden traits or award XP.
- Refuse malformed/extra intent fields, unknown protocols/schemas, stale session/configuration/revision/generation, unverified bindings, unresolved recovery and inactive dog states. No input table is changed. Unknown ownership fields are refused and preserved, never silently reset.

F108 is partial. F04 has an offline ownership-transfer invariant only; transport, death, growth and native save identity are not implemented. [The complete roadmap](FEATURE_TRACEABILITY_MATRIX.md) remains in scope.

## Source and data boundary

[source-inventory.json](../source-inventory.json) declares authoritative source, prepared localization and validation commands. The original ownership modules are Guard, Access, Ownership and Projection in `src/domain/B47Dog`; the current inventory also includes the later identity/snapshot/store modules and unregistered native adapters. `B47Dog` is an internal module path, not a finalized Mod ID or native animal namespace. There is no `media`, `Contents`, `mod.info`, staging or distribution tree.

The ownership schema 1 is a dedicated subrecord: schema, worldId, dogId, generation, revision, aclRevision, phase, optional name, optional ownerAccount/ownerEpisode and a bounded explicit handlers map. Never pass or replace the entire private dog record with this subrecord. Other personality, health, history, reward and training domains remain outside it. Unknown schema/fields produce Recovery with no mutation. The ownership foundation did not supply a private-store format. The later native/private slice supplies a bounded prototype snapshot format and preparation path; no migration is implemented.

`Ownership.propose(state, context, request)` returns either `{ok=false, reason=...}` or a **server-only proposed subrecord**, expected revisions and an optional private transition event. It performs no commit. Successful no-ops do not advance revision or produce events. Counter exhaustion refuses further changes; the 64-handler limit is an internal bounded record/packet safety limit, not a progression setting.

`Projection.build(state, context, discoveries)` returns an allowlisted view or refusal. The optional discovery envelope requires worldId, dogId and byAccount; mismatched envelopes are refused. Current actor account/episode select within that envelope. Returned nested tables are fresh copies. Existing discovery input is not modified on grant, revoke or transfer. Observation values are coarse enumerations; raw native/hidden values are never forwarded.

`Access.role`, `Access.canClaim` and `Access.actions` are internal helpers requiring prior Guard.ready validation. Public callers use Ownership.propose, Projection.build or Access.validate.

## Trusted server context and future commit adapter

Context fields are **not network arguments**. A verified server adapter must derive the exact authenticated account, server-created character episode, world/session, alive/connected status, current native binding, visible/reachable observations, recovered store status, target reference resolution and effective configuration. Ownership capability defaults unavailable unless explicitly enabled by that adapter. No administrator role can be requested through this protocol.

The intent contains only protocol 1, worldId, sessionId, dogId, generation, revision, configRevision, action and the action's name or opaque targetRef. Unknown keys, including actor/owner/role/proximity claims, are refused. Target identity/consent must be resolved and validated server-side. Revocation can resolve an offline account from a trusted retained grant; granting identity never comes directly from client args.

The later NativeSession prepares a private file from a matched native observation and trusted context. An authenticated native broker and gameplay commit adapter still must:

1. Authenticate and bound/rate-limit input before resolving world/dog/target records. Verify native character lifecycle and account uniqueness under T-AUTH.
2. Serialize each dog's mutations. Immediately before committing, reread current actor/binding/configuration/ACL/target and rerun the proposal inside a compare-and-swap boundary. Two proposals computed from the same state are alternatives, never two committed successes.
3. Persist the ownership subrecord together with required receipts/history while preserving every other private domain. Reconcile native/private checkpoints first. A proposal's event is not a durable receipt, and this module does not provide atomicity or restart-safe exactly-once execution.
4. Re-resolve permissions and build a new projection immediately before sending. Invalidate queued responses on ACL/configuration/episode/session changes. Do not cache or send an old projection. Never send the proposal, expected actor fields, private transition event or full private record.

The core is not attached to OnClientCommand. The later explicit load/start/death observer does not satisfy the authenticated broker or commit obligations. [Native ownership](NATIVE_STATE_OWNERSHIP_MATRIX.md), [identity](CANINE_IDENTITY_CONTRACT.md) and [private recovery](PRIVATE_PERSISTENCE_RECOVERY_CONTRACT.md) remain the authoritative integration contracts. The ownership modules have no native API calls or game-source copies. The later native adapter has its own dated source-evidence manifest.

## Configuration and localization

The core consumes the two existing server policies: HandlerPermissionMode (`OwnerOnly`/`OwnerAndGranted`) and OwnerAfterCharacterDeath (`RetainAccountAccess`/`RequireNewClaim`). It requires explicit validated semantic values and configuration revision; missing/invalid values refuse access rather than broadening it. Registry defaults remain OwnerAndGranted/RetainAccountAccess. A future native adapter must map the installed sandbox representation to these tokens and propagate configuration revision changes; numeric enum positions are not guessed here. No native sandbox registration is implemented.

Prepared `src/localization/<language>/UI.json` and Sandbox.json contain 13 action/refusal keys and eight existing configuration keys in every one of the 29 required languages. All are explicit English fallback pending reviewed translations; Name Dog is the only added design key, making 304 total. The exact key/value sets are checked. These files are authoritative source for future native placement; they are not evidence of UI loading. Role/status/cue enumeration rendering and any additional UI copy must receive their own reviewed keys when that UI is implemented. No runtime UI or manual claims these features are playable.

## Validation and remaining gates

[TESTED Windows offline, 2026-10-14, 0.2.0-dev.1] 94 test cases passed under Lua 5.1 through Lupa 2.6, including claim/name/grants/transfer, actor spoofing, stale/config/session/replay refusal, consent, privacy, new-character access, malformed inputs, unsupported schema/fields, overflow and unchanged input tables. Disposable tables are used; no player saves or native files are read or written. Lua 5.1 syntax/behavior is not Kahlua or PZ runtime proof.

Exact commands from repository root (Python3 with Lupa 2.6 for the Lua test):

```powershell
$featurePython = 'C:/Users/willi/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe'
& $featurePython -B scripts/check_versions.py --root . --json
& $featurePython -B scripts/validate_m0r.py
& $featurePython -B scripts/validate_foundation.py
& $featurePython -B scripts/test_domain.py
& $featurePython -B scripts/audit_public_push.py
git diff --cached --check
```

The foundation validator checks the bounded source inventory, case-correct requires, all 609 prepared fallback entries and30 unchanged art files. GitHub CI repeats the offline checks on Ubuntu with pinned Lupa 2.6; green CI does not establish Linux PZ compatibility. That original foundation introduced no native adapter; the later native/private slice separately rechecks native inputs and extends the test suite to 171 cases at 0.2.0-dev.2.

The art remains gsd-v002 tested at 0.1.0-dev.2/commit 643ead1. [Frozen checkpoint hashes](art-checkpoint.json) use canonical Git bytes, with only declared text-newline normalization for Windows checkouts. Binary bytes remain exact. Existing art results retain their original scope; the visual benchmark is still NOT MET and model work is deferred.

[RUNTIME GATE] B-ENV/B-ASSET, B-IDENTITY and B-STORE still block live companion integration. T-AUTH, T-PROTOCOL, T-PRIVACY, T-RECOVERY, native character changes, reconnect/restart and two-client permission changes require actual dedicated evidence. No durable receipt/CAS, packet flood control, complete native lifecycle binding, initialization, migration, handler roster UI or gameplay command is implemented. The later read-only native match and prepared private file do not satisfy those gates. G6 NOT TESTED; G7 BLOCKED / NOT TESTED; stable-release G8 BLOCKED. No game/server launch, deployment, package, Workshop upload or main merge is authorized by these tests.
