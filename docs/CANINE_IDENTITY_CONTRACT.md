# Canonical canine identity contract

Project Version: 0.2.0-dev.8

Latest user-directed database/relationship/task proposal: [DATABASE_AUTHORITY_DESIGN.md](DATABASE_AUTHORITY_DESIGN.md). Its logical identity, natural bonding, offline self-care and task/lease semantics supplement/supersede corresponding proposed design details below; no runtime capability or historical evidence is upgraded. The baseline body is preserved.

[VERIFIED packaged source, 2026-10-14] Native ObjectModDataPacket accepts client animal marker load/wipe. A private-record byte match is diagnostic only, not identity provenance. Dedicated ownership preparation is blocked. The [current authority investigation](NATIVE_IDENTITY_AUTHORITY.md) preserves private-ID reporting across absent/altered observations and evaluates a server-assigned native integer without promoting it to authority. The [loadable persistence diagnostic](NATIVE_BOOTSTRAP_TEST.md) reserves one expected test identity before constructor side effects and never retries/respawns on uncertainty.

M0R design, 2026-10-12. FEASIBLE identity domain; lifecycle carriers EXPERIMENTAL; maturation rebinding BLOCKED until a safe Lua path is demonstrated. [Evidence](M0R_SOURCE_EVIDENCE.md), [private recovery](PRIVATE_PERSISTENCE_RECOVERY_CONTRACT.md), [MP tests](MULTIPLAYER_ACCEPTANCE_MATRIX.md).

## Current implementation boundary

The [native/private foundation](NATIVE_PERSISTENCE_SLICE.md) implements read-only marker matching. The [0.2.0-dev.3 lifecycle adapter](NATIVE_PAIRING_LIFECYCLE.md) adds detached/dead observations and same-handle return after revalidation; unexplained new handles remain quarantined. Dead/detached animals refuse actions, while duplicates and foreign/missing private bindings quarantine; ID/handle capacity exhaustion stops the session. This does not establish identity through unloaded/replaced handles, allocate or stamp a dog, or prove native save/restart continuity. Those lifecycle routes remain gated below.

## Identity and allocation

Proposed permanent key: a persisted world UUID plus a server-minted dog UUID from the vanilla Lua-exposed getRandomUUID(). UUIDs are checked against the allocation ledger, live bindings and tombstones before use; bounded collision retry fails safely. Allocate a reserved private record before invoking a validated native spawn. Record reserved → spawned → bound phases and reconcile after crash; a reservation never authorizes blind replacement spawning. Allocation history is retained with tombstones; never recycle a dead dog's key or infer it from animalId, network ID, display/owner name, chunk location or breed.

The default native animalId is a supporting hint: the inspected initializer uses Rand.Next(10000). The exposed setAnimalID(int) can assign a value above that range, and native save/load preserves it. Such an allocator remains a candidate until inbound cloning/admission and lifecycle integrity are established; the current implementation does not assign or trust that value. It cannot independently recover a lost marker or serve as a world-unique permanent key. Binding generation advances only on an observed verified representation replacement/rebinding, not reconnect, UI requests or ordinary save. Entity handles are transient. The current generation, record revision and authenticated actor permissions are re-resolved immediately before every action commit.

Allocation highwater is the durable sequence of reserved ledger entries within an allocation epoch, not the UUID itself. Persist epoch/sequence/reservation before spawn; failed reservation remains consumed. The UUID-key ledger handles collisions while sequence/predecessor proves ordering. Refuse overflow rather than silently rounding; paired restore/fork changes allocation/session epoch before new work.

## Public carrier and private record

Candidate native animal ModData marker: a namespace table containing only dogId, worldId, bindingGeneration, schema identifier and bindingToken. These identifiers are nonsecret and confer no permission. bindingToken identifies accepted creation/representation-transition provenance, not the latest global store/world checkpoint. Retain its accepted chain; an unloaded animal can legitimately carry an older binding token while the world checkpoint advances. Do not rewrite every unloaded carrier or quarantine solely because its token predates the global checkpoint. No traits, histories, medical findings, cue knowledge, rewards or ACLs belong in this marker. The user approved technical Mod ID/namespace B47ANCEDDogmeat on 2026-10-14; b47dogtest/grey is the temporary raccoon diagnostic registration. Original canine registration/assets remain a separate acceptance gate.

Native save/load serializes animal ModData in inspected source. That is a candidate carrier, not proof across every transition or proof against client tampering. Server discovery compares the marker with its private authoritative binding, expected native type and transition record. Never accept a client marker, UID, generation or owner field as authoritative. Tamper/duplicate/missing carrier suspends affected actions.

Private identity fields include dogId, worldId, lifecycle state, current generation, current representation kind, native hint aliases, transition receipt, current checkpoint, initializedAtGameHour and terminal tombstone. Historical handler relationships survive transfer; active permissions and per-handler projections are recalculated.

## Transition contract

| Transition | Source-supported candidate | Required reconciliation / exit | Current gate |
|---|---|---|---|
| Initial controlled spawn | addAnimal plus native ModData | Reserved ID binds exactly one new live instance; two clients observe same dog | EXPERIMENTAL |
| Native save/load | IsoAnimal.save/load serializes marker candidate | Reattach to matching private record and accepted binding-token chain within a recovered world/store checkpoint; no fresh initialization | EXPERIMENTAL |
| Chunk unload/reload | Native animal manager lifecycle | One representation, generation unchanged unless verified replacement; stale routes discarded | EXPERIMENTAL |
| Carry into inventory | Native AnimalInventoryItem embeds the animal | Validate source dog and real target item; exactly one active representation; private mode changes once | EXPERIMENTAL |
| Release from inventory | Fresh six-argument IsoGridSquare.AddWorldInventoryItem animal branch constructs replacement and invokes copyFrom; marker-copy source path established | Prove exact item removal, one representation, lifecycle receipt/generation and restart behavior before enabling | EXPERIMENTAL; transaction/runtime NOT TESTED |
| Trailer add/remove | Native embedded animal and vehicle replacement/copy path | Unique compartment occupancy; preserve marker, clock and exact physical item/animal count | EXPERIMENTAL |
| Other vehicles / RV / kennel | No universal representation path established | Separate source evidence, native occupancy and antidupe acceptance before support | BLOCKED |
| Growth / maturation | AnimalData.grow creates a new animal and preserves native animalId | No demonstrated ModData transfer in inspected growth path; prove an exposed server transition seam or definition-safe no-replacement route | BLOCKED |
| Ownership transfer / pack change | B47ANCE server-domain operation | Identity unchanged; ACL revision changes, old projections revoked; histories retained | FEASIBLE, awaits persistence/ACL proof |
| Death / corpse conversion | Native terminal/corpse behavior | Tombstone once, cancel leases/rewards, reconcile cargo; prove marker/identity lookup on corpse as needed | EXPERIMENTAL |
| Optional reanimation | No proved canine hostile entity path | Retain historical dog ID, separately authorized hostile lifecycle, remove companion authority | BLOCKED |
| Backup rollback / world recovery | Matched checkpoint and paired backup candidate | Reconcile native world and private store before writes; never choose largest generation blindly | EXPERIMENTAL |

The historical native audit's broad claim that growth copies native ModData is not accepted for this contract. Fresh packaged AnimalData.grow inspection shows new construction and animalId transfer without a demonstrated ModData copy in that route. IsoAnimal.copyFrom copying ModData does not establish that grow calls copyFrom. Preserve the historical report unchanged and record this narrower finding in the new evidence index.

## Binding state machine and ambiguity

States: RESERVED, LIVE, STORED_ITEM, STORED_VEHICLE, DETACHED_PENDING, TERMINAL, UNBOUND, RECOVERING, QUARANTINED. Exactly one of live/item/vehicle owns world presence or occupancy. A detached transition retains the original record and receipt; it never invents another dog. Missing marker on a managed species is UNBOUND, not automatically adopted. Marker with missing private record is QUARANTINED, not a fresh randomized dog. Duplicate marker, foreign world or unaccepted binding-token/generation quarantines all competing bindings and relevant item/task commits; never select whichever object was seen first. Global checkpoint recovery is a separate world/store check.

Operator recovery is explicit: preserve records/diagnostics, inspect known native representations, validate a paired backup or approved evidence-backed rebind, and log nonsecret decision/revision. No automatic merge based only on the small native animalId, coordinates, name or breed. A recovered dog cannot earn rewards or move shared items until its binding and store are unambiguous.

An approved paired rollback/fork starts a fresh allocation/session epoch before new reservations or commands. Existing dog IDs stay unchanged; restored allocation/receipt counters are never reused as current-session tokens. Use bounded exact integer sequences or validated decimal-string encoding, rejecting overflow before Lua-number precision is lost. This is an additional anti-replay boundary, not a substitute for matching world/private checkpoints.

## Smallest proof and growth alternative

Propose one original medium adult dog, one controlled server spawn, no population/growth/skills/XP/reproduction changes, initially one handler plus one observer. This isolates identity, native movement, projections and private save recovery. An adult-only/no-growth prototype is permissible only through a verified species definition/native configuration that avoids replacement; it is a limited research experiment, not fulfillment of puppy/maturation requirements. If no such configuration is proved, lifecycle proof is blocked. Never patch the class, pause all vanilla animals globally or pretend maturity is supported.

T-IDENTITY must exercise ordinary save/restart/reconnect/unload, duplicate/missing markers, two simultaneous allocations and marker tampering. T-TRANSPORT separately proves carry/release/trailer and each later transport route before transport gameplay. T-GROWTH is mandatory before puppy/maturation support; T-DEATH and T-RECOVERY precede claiming the complete lifecycle.
