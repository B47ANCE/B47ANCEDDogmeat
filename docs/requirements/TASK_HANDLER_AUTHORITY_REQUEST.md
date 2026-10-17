# 10. TASK ARBITRATION & ACTIVE HANDLER AUTHORITY

**Project:** B47ANCE'd Dogmeat  
**Architecture:** Standalone, Lua-only, database-authoritative, dedicated-server-first  
**Status:** Design specification — implementation pending native lifecycle and multiplayer authority validation

## 10.1 Objective

Implement a centralized, server-authoritative task arbitration system that determines what each dog is currently doing, which player may direct it, when autonomous behavior takes priority, and how tasks are interrupted, resumed, or cancelled.

Every dog must have **one authoritative active task at a time**.

The system must support:

- Primary owners.
- Trusted secondary handlers.
- Trainers.
- Caretakers.
- Autonomous self-care.
- Safehouse routines.
- Training exercises.
- Working-dog assignments.
- Pack commands.
- Emergency behavior.
- Owner disconnections and reconnects.

The database must preserve the dog's persistent task and relationship information without allowing competing clients to control the same physical animal.

---

## 10.2 Task Priority Hierarchy

Use the following default priority order.

| Priority | Task category | Examples |
|---|---|---|
| 1 — Critical | Immediate survival | Escape zombies, avoid lethal hazards, respond to critical injury |
| 2 — Urgent | Essential biological needs | Severe thirst, hunger, bathroom urgency, exhaustion |
| 3 — Primary Owner | Authorized owner commands | Recall, Heel, Stay, Place, Follow |
| 4 — Trusted Handler | Authorized secondary commands | Walk, Recall, Train, Return Home |
| 5 — Autonomous Care | Routine self-maintenance | Eat, drink, rest, groom, use doggy door |
| 6 — Assigned Work | Nonurgent tasks | Retrieval, searching, hauling, guarding |
| 7 — Social / Idle | Optional behavior | Exploring, playing, socializing |

These priorities are defaults, not unconditional overrides.

A dog may refuse or fail a command because of anxiety, training, physical limitations, or immediate danger.

Severe biological needs may interrupt even an established Stay or Place command.

A trusted handler must never bypass owner permissions simply because the dog likes them.

## 10.3 Active Handler Lease

Only one player may actively direct a dog at a time.

The server maintains a temporary handler lease containing:

- Canonical dog ID.
- Authenticated player identity.
- Handler relationship.
- Authorized capabilities.
- Lease creation time.
- Lease expiration.
- Current task reference.
- Server session identifier.

The primary owner has priority over secondary handlers but must not automatically teleport or forcibly reposition the dog.

### Lease acquisition

Before granting a lease, validate:

1. Dog exists in the authoritative database.
2. Dog is alive and available.
3. Native representation is safely bound.
4. Player identity is authenticated.
5. Player has the required bond or sub-bond.
6. Requested action is permitted.
7. Dog is physically reachable where necessary.
8. No incompatible active lease exists.
9. Dog is not performing an uninterruptible critical action.

### Lease release

Release or expire the lease when:

- The handler disconnects.
- The handler explicitly releases the dog.
- The task completes.
- The dog becomes unavailable.
- A critical emergency interrupts control.
- The lease expires.
- The dog enters a safely committed stored state.

A disconnected handler must never retain an indefinite movement or command lease.

## 10.4 Primary Owner and Secondary Handler Conflicts

The primary owner controls permanent ownership and delegation policies.

Secondary handlers may earn trust naturally, but trust alone does not grant unrestricted administrative authority.

When two players issue conflicting commands:

1. Server validates both requests.
2. Server checks active lease ownership.
3. Server checks permissions and priority.
4. Server determines whether the current task may be interrupted.
5. Only one command is accepted for execution.
6. The rejected player receives an understandable explanation.

Examples:

- "Rex is currently being handled by another survivor."
- "You have not earned enough trust to lead Rex."
- "Rex is returning to safety."
- "The owner has recalled Rex."

The server must never execute conflicting movement instructions simultaneously.

## 10.5 Autonomous Self-Care

When no authorized player is actively handling the dog, it may enter autonomous behavior.

If the primary owner is offline and the sandbox setting uses the default **Remain in World — Self-Care**, the dog remains present and manages its needs.

Supported routines include:

- Finding accessible food.
- Drinking accessible water.
- Seeking shelter.
- Resting.
- Sleeping.
- Using a designated potty area.
- Using compatible doggy doors.
- Returning to its assigned safehouse.
- Avoiding zombies.
- Seeking its assigned doghouse.
- Performing eligible growth transitions when technically supported.

Self-care must use real resources.

Do not generate free food, water, medical recovery, or training XP.

If the dog is inside its assigned safehouse, it should remain there except for essential trips or safety-related movement.

When outdoors, it should prefer its assigned home territory and return when practical.

## 10.6 Offline Owner Modes

Provide a server sandbox setting:

`B47ANCEDDogmeat.OfflineCompanionMode`

Proposed values:

- `SelfCare` — default.
- `StoreOffline` — optional.

### SelfCare

The dog remains physically present.

Trusted secondary handlers may continue interacting with it according to their permissions.

The dog performs autonomous care when not being handled.

### StoreOffline

When the primary owner disconnects:

1. Stop accepting new noncritical tasks.
2. Resolve or cancel active handling leases.
3. Safely suspend active work.
4. Persist the dog's authoritative state.
5. Confirm the private checkpoint is durable.
6. Withdraw the native representation only through a verified lifecycle mechanism.
7. Mark the dog as stored.

When the owner reconnects, restoration must be validated before a physical representation is created.

Do not enable StoreOffline until safe withdrawal and restoration are demonstrated.

The existing native identity NO-GO remains applicable.

## 10.7 Trusted Caretaker and Trainer Activity

A secondary player may earn a sub-bond through:

- Calm proximity.
- Feeding.
- Petting.
- Grooming.
- Walking.
- Positive training.
- Successful shared experiences.

The database tracks these relationships independently of primary ownership.

A trusted caretaker may perform authorized care tasks.

A trusted trainer may teach and reinforce commands if their relationship, skills, and owner permissions allow it.

A trusted handler may temporarily lead the dog.

**Sub-bond progression never automatically transfers primary ownership.**

If the owner is offline, authorized secondary players can care for and train the dog without changing its permanent ownership record.

## 10.8 Task State Machine

Every task must use an explicit lifecycle.

Proposed states:

- `Requested`
- `Validated`
- `Assigned`
- `Running`
- `Suspended`
- `Completed`
- `Cancelled`
- `Failed`

### Task transitions

A task may begin only after server validation.

A task completes only after the server observes its actual success conditions.

Suspension preserves the task's remaining work when appropriate.

Cancellation releases claims, leases, and temporary resources.

Failure records a reason and returns the dog to a safe available state.

Tasks must not remain permanently active after disconnects, entity loss, or server restart.

## 10.9 Interruption and Resumption

Each task definition must declare:

- Priority.
- Required skills.
- Required equipment.
- Required handler permissions.
- Valid starting conditions.
- Interruption rules.
- Resumption rules.
- Completion evidence.
- Failure conditions.
- Persistence policy.

Examples:

**Training session:** May be interrupted by danger or exhaustion. Cancelled repetitions must not award unearned XP.

**Retrieval:** May be suspended when the dog encounters danger. The claimed item must be released or safely retained according to transaction state.

**Bathroom trip:** May interrupt idle behavior or noncritical work. If the route is unsafe, the dog should seek alternatives.

**Guarding:** May continue during routine self-care interruptions but must not prevent essential biological needs indefinitely.

**Doghouse growth:** Requires a separately validated identity-preserving transition and must not begin while another incompatible task owns the dog.

## 10.10 Pack Task Arbitration

Pack-wide commands must expand into individually validated dog tasks.

Each dog retains:

- Its own canonical identity.
- Its own active task.
- Its own handler permissions.
- Its own training requirements.
- Its own movement authority.
- Its own physical limitations.

A pack command does not grant untrained dogs advanced abilities.

For coordinated tasks, the server must allocate work without duplication.

Examples:

- One corpse cannot be independently claimed by two dogs.
- One inventory item cannot be transferred twice.
- One dog cannot simultaneously guard and retrieve.
- One physical representation cannot be controlled by two task writers.

Shared-load hauling requires a separate verified coordination contract.

## 10.11 Database Task Persistence

The authoritative database should store durable task information where necessary.

Persistent fields may include:

- Canonical dog ID.
- Task ID.
- Task type.
- Assigned handler.
- Current task state.
- Target identity.
- Destination.
- Server revision.
- Checkpoint information.
- Outstanding resource claims.

Transient movement handles, client pointers, and native object references must not be treated as durable identities.

After restart, the server must reconcile saved task state against the actual world.

Do not automatically resume a task if its native dog representation, target item, or destination cannot be authenticated.

Ambiguous tasks must be suspended or quarantined rather than completed automatically.

## 10.12 Concurrency and Duplicate Protection

The server must prevent:

- Two active handler leases.
- Two simultaneous movement writers.
- Duplicate task completion.
- Replayed reward packets.
- Duplicate item transfers.
- Duplicate corpse claims.
- Conflicting care interactions.
- Stale client task updates.
- Repeated task restoration after restart.

Use server-generated task identities and idempotent completion handling.

Client-supplied task identifiers are not proof of authorization.

## 10.13 User Interface

The dog management panel should show:

- Current activity.
- Active handler, when appropriate.
- Current task.
- Task progress.
- Important needs.
- Interruptions.
- Reason for refusal.
- Available commands.

Only show actions that are currently meaningful and authorized.

Examples:

- "Take for Walk" when the player can lead the dog.
- "Release Dog" when the player currently holds the handling lease.
- "Resume Training" when a suspended session is valid.
- "Return Home" when the dog can meaningfully attempt it.

Do not show unavailable or opposite-state actions unnecessarily.

## 10.14 Multiplayer Acceptance Tests

Required scenarios:

1. Primary owner commands a bonded dog.
2. Unauthorized player attempts a command.
3. Trusted caretaker performs routine care.
4. Trusted trainer teaches an authorized command.
5. Two handlers issue conflicting commands.
6. Primary owner disconnects during training.
7. Secondary handler disconnects while leading the dog.
8. Dog enters autonomous self-care.
9. Dog interrupts work for urgent biological needs.
10. Dog avoids danger during a bathroom trip.
11. Owner reconnects while another handler is active.
12. Server restarts during a suspended task.
13. Two dogs attempt to retrieve the same item.
14. Pack command includes an untrained dog.
15. Native representation becomes unavailable.
16. Duplicate task requests are replayed.
17. StoreOffline mode attempts withdrawal and restoration.
18. Private relationship and task records survive restart.

Record PASS, FAIL, BLOCKED, or NOT TESTED.

Offline tests cannot establish dedicated-server correctness.

## 10.15 Implementation Restrictions

Do not enable gameplay task arbitration until the required native entity and server authority boundaries are proven.

The current Build 42.21 investigation concluded NO-GO for automatic native-to-private ownership continuity under the verified Lua boundary.

A database-authoritative design does not automatically overturn that finding.

Before implementation, Codex must prove:

- Safe binding between a logical dog and its native representation.
- One authoritative movement producer.
- Server-owned task validation.
- Safe handling of native reconstruction.
- Durable task and relationship persistence.
- Duplicate prevention across restarts.

Keep multiplayer ownership disabled until those requirements are satisfied.

---

# FINAL TASK ARBITRATION DIRECTIVE

**Every dog has one permanent logical identity, one authoritative active task, and at most one active handler lease.**

Primary ownership remains separate from secondary trust.

Trusted players may care for and train another player's dog without becoming its owner.

When the owner is offline, the default behavior is autonomous self-care rather than despawning.

All tasks must respect the dog's training, health, physical needs, personality, safety, and current circumstances.

The database preserves persistent state, while the server controls authorized actions and the native animal represents the dog physically.

**No client, handler, or competing AI system may independently override the server's authoritative task decision.**