# Task arbitration contract

Project Version: 0.2.0-dev.3

M0R design, 2026-10-12. FEASIBLE state machine; native task-control seam EXPERIMENTAL and gameplay gate BLOCKED until proved. Lua-only. [Ownership](NATIVE_STATE_OWNERSHIP_MATRIX.md), [time model](CANINE_BIOLOGY_TIME_MODEL.md), [transactions/recovery](PRIVATE_PERSISTENCE_RECOVERY_CONTRACT.md).

## Single decision owner

The server task arbiter chooses one logical task per dog. Native code remains the sole physical movement writer. The selected native behavior-control seam must safely stop conflicting flee/follow/need decisions, accept a path intent, report obstruction/completion, and restore vanilla operation at release. Merely calling setBlockMovement or setting a target does not establish this. If a Lua seam cannot satisfy the contract, preserve the requirement as BLOCKED and propose a separately reviewed native-autonomy/handler-led alternative; never add Java or direct position writes.

Genuine native emergency escape may preempt the managed task. Arbitration must observe and surrender to that safety interruption; suppressing danger-driven native flight is not an acceptable interpretation of preventing conflicting decisions.

## Priorities

| Priority | Class | Rule |
|---|---|---|
| Hard stop | Death, invalid binding, quarantine, unsupported schema | Reconcile irreversible receipts; cancel tasks/rewards; no simulation until resolved |
| 1 | Immediate danger / escape | Preempt lower tasks at safe native checkpoint; no path through an observed horde |
| 2 | Critical injury and emergency care | Safe care checkpoint; dangerous exposure can preempt; no invented clinical outcomes |
| 3 | Emergency physiological relief | Interrupt Stay/work before bodily limit; severe care/danger can delay route, never indefinite retention |
| 4 | Authorized controlled cue / manual care | Require cue/equipment/ACL; deny or explain deferral when higher need exists |
| 5 | Working / pack task | Validate each dog's ability and unique target claim |
| 6 | Routine food/water/relief/home needs | Consume actual resources, use safe reachable routes |
| 7 | Rest / social idle | No proximity or idle XP; preserve native baseline needs ownership |

Same-priority tasks keep the current lease unless an authorized explicit replacement/cancel is accepted. Pack commands submit independently validated per-dog intents; a pack coordinator never becomes a second movement writer. Transport suspends locomotion until native release/rebinding succeeds, while the appropriate biology clock continues.

## Task record and transitions

Proposed logical fields: taskId, dogId, bindingGeneration, recordRevision, authenticatedActorKey, kind, priority, goal reference, creation/expiry game time, configurationRevision, phase, interruption reason, resumable flag, reservation references and commit receipt. Route handles and native object pointers are transient and never saved as resumable authority.

States: REQUESTED → VALIDATED → RESERVED → RUNNING → COMMITTING → COMMITTED → COMPLETE. Alternative exits are REFUSED, CANCELLED, TIMED_OUT, INTERRUPTED, RECOVERING or QUARANTINED. Every transition is server-owned and idempotent. A client response means accepted/pending/refused, not successful movement or awarded XP.

| Checkpoint | Cancellation / interruption | Recovery / resume |
|---|---|---|
| Before reservation | Refuse/cancel without consuming resources | New intent only |
| Reserved, before physical commit | Release claims; no reward/refund because nothing consumed | Explicitly resumable goal may reacquire after all checks |
| Moving / preparing | Native safe stop, release transient route; record actual progress | Replan and revalidate dog generation, actor ACL, target, geometry, resources and timing |
| Physical/item/elimination commit in flight | Finish/reconcile exact receipt; never unconditional refund | Inspect native state before deciding result; ambiguity quarantines affected transaction |
| Committed, projection/reward pending | Publish committed result once; dedup award | Durable receipt governs retry; no replay reward |
| Death, transfer, transport or chunk detach | Invalidate stale actor/route and reconcile reservations | Rebind first; ownership transfer clears old rights; dead dogs cannot resume |

An exercise succeeds only after its real server-observed behavior and reinforcement conditions hold. Each behavior defines duration, displacement, distance, valid floor, distraction/obstruction conditions and timeout in its approved slice. True actor/dog movement distinguishes loose-leash practice from wall-walking. Stay can be eligible practice during a real verified activity, never an unlimited stationary-nearness reward. Discovery is separate from learning XP. Incomplete or interrupted work grants no success XP.

## Door and load reservations

One reservation per dog, physical item/load and conflicting flap crossing. Opposite-side dog approaches serialize or select a safe yielding tile; reservations expire without deleting dogs. Revalidate flap fit/mode/lock/power/ACL/barricade/collision immediately before entry and at any proved safe transition boundary. Power loss during transit must finish or retreat through native physical behavior; if no safe transition is exposed the feature stays BLOCKED. Cooperative hauling requires one shared load coordinator plus separate per-dog leases and a proved physical movement writer.

## Failure acceptance

T-TASK and T-TRANSACTION cover same-priority replacement, two handlers, disconnect, resource removal, native flee/need competition, loss of target, geometry obstruction, timeout, save/crash at every commit checkpoint, death, transport, transfer and replay. T-BIOLOGY covers emergency relief interrupting Stay and work. No task may teleport, fake completed inventory movement, resume a persisted pointer or suppress native errors to hide failure.
