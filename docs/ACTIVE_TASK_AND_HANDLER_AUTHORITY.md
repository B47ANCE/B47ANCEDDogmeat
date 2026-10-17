# Active task and handler authority

Project Version: 0.2.0-dev.7

The latest task-arbitration handoff governs this design. **One permanent logical dog, one authoritative active task, at most one active handler lease.** No live task controller is enabled while native binding, exclusive physical control, reconstruction/durability and multiplayer gates remain unresolved. The original [TASK_ARBITRATION_CONTRACT.md](TASK_ARBITRATION_CONTRACT.md) remains the earlier baseline; its physical transaction/receipt safeguards still apply, while the public states/priorities below supersede the older proposal.

For a valid active representation, idle/self-care is an explicit arbiter choice when no human task runs. Assigned/Running tasks share one exclusive active slot; saved Suspended intents do not execute concurrently. Hard stops/unavailable representations allow no active physical execution, rather than inventing an idle movement writer.

## Default priorities and hard stops

| Priority | Category | Examples / limits |
| --- | --- | --- |
| 1 | Immediate survival | Escape lethal danger/zombies, respond to critical injury; native emergency behavior is respected |
| 2 | Urgent biological needs | Severe thirst/hunger, bathroom urgency, exhaustion; may interrupt Stay/Place |
| 3 | Primary-owner commands | Authorized Recall/Heel/Stay/Place/Follow; not unconditional success |
| 4 | Trusted-handler commands | Permitted Walk/Recall/Train/Return Home; owner policy still required |
| 5 | Autonomous care | Routine eat/drink/rest/groom/relief/home needs using real resources |
| 6 | Nonurgent assigned work | Retrieval/search/haul/guard; cannot indefinitely block biological needs |
| 7 | Social/idle | Explore/play/socialize; no free XP |

Death, invalid binding, unsupported schema, quarantine or uncertain physical transaction is a **hard authority stop**, outside the priority queue. Preserve/reconcile evidence rather than moving a dog or automatically completing work. Anxiety, knowledge, fitness/equipment and dog willingness can refuse/fail any command. Priorities choose eligible intent; they do not override danger or authorize an untrained dog.

## Handler lease

Fields: canonical key, authenticated principal, relationship, allowed capability snapshot, createdAt, expiresAt, currentTaskId, serverSessionId, leaseFence. Acquire only if private dog exists, alive/available, native binding verified, actor authenticated/current, bond/sub-bond and specific permission sufficient, equipment/skills/reachability valid, no incompatible lease and no uninterruptible critical action. A client lease/task ID never proves authority.

One server coordinator compares expected dog/task/ACL/config revisions and the current fence, then grants at most one lease. Same-priority work retains the valid lease unless an authorized replacement is accepted. A valid primary-owner request can request preemption of lower-priority handling; first reach a safe interruptible checkpoint, resolve claims/physical commit, revoke/fence the prior lease, then assign the new task. No overlapping movement instructions and no owner teleport. Critical or uncertain in-flight work can defer the owner's request.

Release/expire on handler disconnect/explicit release, task completion, dog unavailability, critical emergency, deadline or safely committed stored state. Server presence is connection/episode-based; a forged disconnect cannot release another handler. Loss of binding immediately fences commands; it is not a respawn signal. Lease expiry uses a verified server elapsed-time source and finite technical safety bounds before implementation; no client clocks. Saved wall time or a lease from another session never restores active authority. Renewal revalidates the same permission/binding/fence.

Owner disconnect in SelfCare releases **that owner's** command lease. An authorized secondary handler may continue compatible work if offline policy permits; otherwise resolve/suspend safely before autonomous care. Owner reconnect alone preserves another valid handler's lease and committed care/training. An explicit eligible owner command follows the preemption process. Lease release/timeout never transfers permanent ownership.

## Public task state machine

`Requested → Validated → Assigned → Running → Completed`; alternatives are Suspended, Cancelled and Failed. A refusal may end Requested as Failed with a reason; it is not execution. `Suspended → Validated` requires all checks again, a fresh binding/lease/resource claim as needed, and definition-declared resumption. Completed/Cancelled/Failed are terminal and cannot silently restart. Assigning a task is not proof of successful movement or XP.

| State | Entry/exit contract |
| --- | --- |
| Requested | Server receives bounded intent; no lease/resources/reward yet |
| Validated | Current actor, private record, permission/cooperation, native binding/target and configuration pass |
| Assigned | Coordinator reserves task, handler lease and required unique resources; revision/fence recorded |
| Running | Sole native writer accepts supported intent; progress comes from trusted server observations |
| Suspended | Persist remaining logical work/reason; release/reconcile transient routes/claims as defined; never restore pointers |
| Completed | Actual success conditions plus reconciled physical/private commit and one completion receipt; reward once |
| Cancelled | Work abandoned only after claims/leases/temporary resources are safely resolved; no unearned rewards |
| Failed | Definite observed failure/reason, cleanup reconciled; unavailable/ambiguous body cannot be asserted safe |

Physical transaction phases such as RESERVED, EFFECT_PENDING, RECONCILING and COMMITTED are **internal receipt states**, not additional public task states or permission to force cancellation midway through an irreversible action. If an effect is uncertain, keep the logical task suspended/pending reconciliation and quarantine the binding/transaction. Do not fake a terminal failure, refund or completion to hide ambiguity.

Every task definition declares priority, skills, equipment, handler permissions, valid start, interrupt/resume rules, completion evidence, failure conditions and persistence policy. Training interrupted by exhaustion/danger awards no cancelled repetition XP. Retrieval must release or preserve its item claim according to commit state. Guarding yields to urgent relief/critical needs. Unsafe bathroom routes seek permitted alternatives/accidents; no door teleport. Doghouse growth cannot begin with an incompatible task and remains separately blocked.

## Pack work, resource claims and restart

Expand a pack command into independently validated per-dog tasks. Each dog retains capability/training/physical limits and its own task/lease. A world-scoped resource coordinator grants each item/corpse/load quantity once; duplicate requests cannot independently reserve or transfer it. Shared hauling needs a separate physical coordination contract. Pack coordination is not a second movement producer.

Persist durable task intent/definition revision/handler/target/destination/checkpoint/outstanding claims, not native pointers/routes or active lease authority. On restart, clear all active session leases/fences, suspend nonterminal work and reconstruct only evidence-backed claims. Revalidate dog/target/destination/private checkpoint/native binding before any resume. Unauthenticated targets or unresolved physical effects stay suspended/quarantined, never completed or rewarded automatically. Exactly-once logical receipt processing does not prove exactly-once native item transfer.

UI must show relevant current activity/task/progress/needs/handler and useful refusal. Proposed keys cover BusyHandler, InsufficientTrust, SafetyReturn and OwnerRecall; names are shown only when permitted. Take for Walk/Release Dog/Resume Training/Return Home appear only in their valid states. [All 18 requested multiplayer cases](DATABASE_REDESIGN_VALIDATION.md) remain BLOCKED / NOT TESTED, regardless of offline design consistency.
