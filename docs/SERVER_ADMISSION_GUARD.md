# Central server admission policy

Project Version: 0.2.0-dev.7

`src/domain/B47Dog/AdmissionPolicy.lua` supplies one refusal/diagnostic policy, called by the selected native transition wrappers, NativeSession assessment, NativeRuntime assessment/census and dedicated ownership preparation. **ADMIT is reserved and unreachable.** There is no public Admit endpoint, new ownership feature, native interception hook or persistent admission certificate.

## Decision contract

| Decision | Meaning here | Examples |
| --- | --- | --- |
| ADMIT | Would require a complete trusted native genesis/lifecycle/previous-session proof; not implemented | A supplied flag, signed marker or diagnostic MATCHED result cannot select it |
| QUARANTINE | Evidence ambiguous/unavailable; private data retained, companion permissions refused | Exact public marker match, guard/anchor failure, unrecovered store |
| REJECT | Invalid, conflicting, unauthorized or explicitly unsupported request/representation | Foreign world, missing private record, copied conflict, known dead, managed inventory/trailer/growth route |
| DEFER | Required native state absent or assessment already active; no authority granted | Startup before loaded anchor, detached body, reentrant assessment |

`DEFER / Unmanaged` in a transition scope check means “outside managed type set,” not dog authorization. Wrappers independently validate the actual native object/type before allowing the original vanilla completion. Type/breed/marker data supplied by clients cannot relabel a managed object as vanilla. Malformed or unavailable source data is refused conservatively; no global constructor override is introduced.

## Boundary order

1. NativeRuntime verifies dedicated/SP authority, allowlisted route, current-process guard integrity, native-load/start phase and exact recovered checkpoint.
2. A process-local assessment latch refuses reentry before a second observation. NativeSession independently refuses simultaneous ownership preparation/assessment and freezes allowed types and the recovered private world identifier.
3. NativeAnimal reads current live/detached/dead/type/breed/marker state; Identity registry correlates against the private roster and retains conflict/death observations. Observation can update the bounded in-memory diagnostic registry, never private ownership or durable admission state.
4. Policy emits detached primitive fields: decision, technical reason, optional **existing private** dog ID, managed boolean, bindingVerified=false. A foreign marker never invents a returned ID.
5. Runtime rechecks guard and checkpoint after native getters return. Drift closes recovery and refuses further work. Dedicated preparation additionally retains NativeSession's unconditional untrusted-marker fence before any store write.

The route allowlist covers world_load, save_load, chunk_reentry, inventory_release, trailer_release, vehicle_load, hutch_release, growth, death, reconnect, admin_spawn, privileged_action and inspect. These are **assessment context labels**, not proof the native engine invokes this policy on those paths. [Coverage](NATIVE_ADMISSION_COVERAGE.md) identifies actual bypasses. No engine event/API is invented to dispatch them.

## Installation, vanilla behavior and diagnostics

The original nine server completion wrappers remain once-only and validate the entire class/new/complete/index/metatable/native API set before mutation. Missing/displaced hooks and delegated exceptions latch failure. Project checks cannot prevent an internal Java call to AddWorldInventoryItem, worker re-entry, deserializer or grow. Do not describe the latch as a native admission firewall or persisted previous-session proof.

The authorized existing Inspect response now includes loaded managed observation counts for ADMIT/QUARANTINE/REJECT/DEFER. They count **observations**, not unique private dogs or all unloaded representations. Unrelated vanilla animals are excluded. The UI appends a localized four-placeholder line; all 29 languages receive explicit English fallbacks. No owner, handler, hidden history or native object is exposed. Ordinary clients have no diagnostic/provision authority, and unsupported command names remain silent.

The existing default-off server sandbox option `B47ANCEDDogmeat.PersistenceTestMode` remains the only runtime option. Diagnostic mode is not an admission/ownership bypass. Provenance requirements, route enum, reentry latch and safety bounds are implementation constraints; exposing settings that invalidate identity guarantees is inappropriate. No new gameplay balance or configuration surface is added.

## Validation and limits

[TESTED — Windows offline Lua 5.1] Actual NativeRuntime/NativeSession/private-file/broker tests exercise copied markers in both arrival orders, stale/foreign/missing identity, paired rollback, interrupted bytes, prepared-pending state, repeats, reentry, anchor/guard changes from native getters, death, reconstructed handles and unauthorized requests. Separate VMs show a fresh intact guard cannot certify the preceding process. Refusals allocate nothing, write nothing and retain private owner/history.

Mocks do not prove native packet reachability, engine scheduling, native save pairing, other-mod compatibility, client privacy or dedicated durability. Current multiplayer ownership remains disabled. See [test plan](MULTIPLAYER_OWNERSHIP_TEST_PLAN.md) and [blocker report](BLOCKER_RESOLUTION_REPORT.md).
