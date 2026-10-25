# Disposable database/native runtime validation plan

Project Version: 0.2.0-dev.10

**Plan only. No PZ/client/server launch, deployment, destructive interruption, installation repair or production save modification is authorized by this document.** Positive ownership/control steps below require a reviewed safe proof implementation first. The current mod cannot run those positive cases. Preserve [the existing diagnostic procedure](DISPOSABLE_RUNTIME_TEST_PROCEDURE.md) for available negative tests; do not invent new console commands or admission endpoints.

## Entry and isolation

1. Operator establishes separately verified clean Build 42.21 / Steam 25485521 client and dedicated baselines. Record effective launch/classpath and package/loose hashes without changing the current modified installation. Unknown precedence or remaining drift blocks interpretation.
2. Create separate disposable SP and dedicated save/cache roots with no actual player saves or credentials. Record canonical project version, exact candidate commit and source hashes. Use the raccoon carrier only. Keep PersistenceTestMode default-off except a deliberately enabled disposable diagnostic world.
3. Retain paired native/private backups outside the test target before every destructive scenario. Label each with world, private/native checkpoint, exact commit/build, schema and SHA-256. Never combine files from unrelated generations. Keep logs/Steam IDs/coordinates local; publish only redacted evidence summaries.
4. Dedicated test uses a headless server, two ordinary clients A/B and a separately controlled admin. Revoke admin privileges for authorization/exploit assertions. Server derives actors; argument IDs never choose identity. SP results never substitute for dedicated evidence.
5. Run existing offline/version/assembly checks before candidate deployment. Readiness to distribute/run is a separate authorization/gate decision. Production/source hash changes require renewed applicability review.

## Identity and lifecycle cases

| Case | Procedure when its safe instrumentation exists | Required evidence |
| --- | --- | --- |
| Two actors | A/B issue valid and forged owner/Steam/permission/bond arguments simultaneously | Callback actor tied to its connection, lossless decimal principal, correct slot/episode/session; forged fields ignored/refused, no data leakage |
| Reconnect / replacement | Disconnect/rejoin A; kill/replace character in disposable session; replay prior request/lease | Principal continuity per policy, new episode/session fences, stale connection rejected; B remains B |
| Missing actor | Send intent before player availability/after disconnect; duplicate request IDs | Refusal with no shared mutation or disclosure; old receipt cannot impersonate a new actor |
| Native save/restore | Provision once through approved diagnostic; clean save/exit/restart; stream chunks away/back | Same logical dog, no automatic replacement, authentic body receipt or quarantine, checkpoint evidence separated from marker correlation |
| Representation transitions | Separate carry/item, trailer/vehicle/hutch, maturation and death fixtures | Every supported origin/target path closes before admission. Unsupported paths refuse; native/no-body uncertainty retains logical identity without spawning |
| Copied/stale body | Controlled diagnostic constructs equal-marker/stale observations only under reviewed disposable instrumentation | No ownership/adoption on a copy; both ambiguous observations quarantined. No client exploit claim without actual ordinary-client path evidence |

## Control, interactions and offline policy

After D1/D2 and a sole-native-producer seam are proved: test Follow/Stay/Return/cancel around closed obstacles, hazard interruption, chunk unload and handler disconnect with both observers. Record task revision, lease fence/session and observed native positions; no teleport or repeated competing writers. Owner reconnect alone must preserve B's valid delegated lease; explicit owner preemption waits for a safe interruption/receipt boundary.

For feeding/petting/proximity/drinking/rest/equipment, observe real items/quantity and accepted native outcome. Test cancellation, no food, rejected petting, duplicate animation+complete callback, packet replay, stale target/body and restart at each reservation/effect/reconcile boundary. No reward/bond for a click, no-op, cancelled action or uncertain consumption. The current raccoon diagnostic's disabled interactions must not be bypassed to force a positive test.

Natural primary bonding and gameplay permissions remain unimplemented. Once separately authorized and safe: simultaneous primary 100 must yield one owner and retained secondary; secondary 100 never transfers; unauthorized care/training fails; owner disconnect and handler expiry fence authority without deleting history. SelfCare and StoreOffline stay unimplemented during this foundational proof. Test their behavior only after separate safe implementations; StoreOffline additionally requires all saved-body withdrawal/restore guarantees. No growth/model work.

## Store and recovery fault matrix

Use only disposable data. First run test-only Lua fixtures. Future real-process tests must instrument precise boundaries rather than infer them from elapsed time: before private prepare; during inactive write; after close/readback; before/after native effect; before/after anchor save; restart/restore. Expected outcome is either the exact prior pair or an explicitly reconciled complete candidate; ambiguous/incomplete data refuse writes and preserve evidence. Never auto-retry irreversible effects, heal files or respawn on absence.

Exercise missing/truncated/bit-corrupt/future-schema files, conflicting same-checkpoint slots, foreign-world data, private-only and native-only rollback, paired backup restore, repeated reloads and forward-migration copies. Paired rollback currently lacks a trusted independent freshness reference and may be indistinguishable; report that limitation instead of claiming detection. Real process termination is not a power-loss simulation; actual filesystem durability remains separately scoped.

Evidence for every case: exact version/commit/build; clean/effective environment; scenario/start pair; actor and side classification; redacted native/private before/after hashes; expected/observed outcome; reproduction count; errors; PASS/FAIL/NOT TESTED and unresolved conditions. Human operator supplies actual runtime evidence. D gates update only for demonstrated scope; dedicated G7 must pass independently before stable G8. Retain every failed/ambiguous backup for investigation, with no cleanup implicit in this plan.
