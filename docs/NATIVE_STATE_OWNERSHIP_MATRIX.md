# Native state ownership matrix

Project Version: 0.2.0-dev.8

Current source correction: the native animal marker is client-writable through ObjectModDataPacket. The table below is the intended ownership contract; its native marker implementation does not enforce that sole-writer claim. Dedicated ownership/gameplay preparation is blocked. The [identity authority investigation](NATIVE_IDENTITY_AUTHORITY.md) also rejects trusting an assigned native integer without complete reconstruction/admission controls; private logical identity recovery remains separate.

M0R contract, 2026-10-12. Status: FEASIBLE domain design; native arbitration EXPERIMENTAL. This assigns intended ownership, not proved runtime behavior. Lua-only. See [source evidence](M0R_SOURCE_EVIDENCE.md), [task contract](TASK_ARBITRATION_CONTRACT.md) and [identity contract](CANINE_IDENTITY_CONTRACT.md).

## Ownership rules

The dedicated server commits shared gameplay. Native ownership means the native authoritative animal subsystem performs the mutation; B47ANCE may request a supported native operation after validation, but cannot run a second timer or position writer. Client interpolation and animation are projections, never success evidence. A field with no proven safe native seam is read-only and its affected feature is blocked.

| Field / operation | Ownership class | Sole authoritative writer | Persistence / synchronization | B47ANCE access and arbitration |
|---|---|---|---|---|
| World position, facing, velocity and physical collision | Native-owned | Native server animal movement | Native animal save/network lifecycle | Read position; submit validated path intent only through proved seam; never set client positions |
| Native network handle and manager ID | Native-owned | Native lifecycle manager | Native transient protocol | Resolve current instance only; never permanent identity |
| Native animalId | Native state read by B47ANCE | Native creation/load/copy | Native save; uniqueness not established | Diagnostic binding hint only; never dog ID or sole lookup key |
| Species, breed definition and native sex | Native-owned | Native spawn/definition path | Native animal state | Select validated registered definitions once at spawn; no reroll on reload |
| Age, growth and native weight | Native-owned | Native AnimalData/growth | Native save and replacement | Read; verify original marker through maturation; no second growth clock |
| Baseline hunger, thirst, fatigue, native health and death | Native-owned | Native AnimalData / authoritative damage path | Native save/sync | Read-only until a condition-specific Lua seam is proved; do not advance native catch-up again |
| Native reproduction/pregnancy, genetic and growth data | Native-owned | Native animal subsystem | Native lifecycle | Preserve native fields; no breeding extension in M1; audit eligibility before population policy |
| Animal inventory-item/live/trailer representation | Shared operation | Native authoritative transition | Native item/vehicle/animal save | Server validates, reserves, invokes native transition, then reconciles dog ID; exactly one representation |
| Permanent dog ID and allocation high-water | B47ANCE-owned | Server identity allocator | Private world store plus nonsecret public binding | Allocate once before committed spawn; never trust client-supplied identity |
| Binding marker, generation and binding provenance token | Intended B47ANCE ownership; native authority BLOCKED | Server intent; clients can alter current native marker | Client-writable native ModData; diagnostic nonsecret allowlist only | Validate retained accepted binding chain independently of current global checkpoint; verify carries/copies; client copies cannot authorize |
| Identity lifecycle, tombstone and quarantine | B47ANCE-owned | Server lifecycle coordinator | Private store | Serial transitions; quarantine ambiguous observations without respawn |
| Precise traits, hidden history and prior knowledge | B47ANCE-owned | Server initialization/learning domain | Private store only | Generate once; never full-record ModData or packet serialization |
| Intrinsic anxiety/confidence and individual motivations | B47ANCE-owned | Server personality domain | Private store | Distinct from native stress; no breed-deterministic outcomes |
| Extension situational stress and welfare conditions | B47ANCE-owned | Server welfare domain | Private store | Own only explicitly distinct extension fields; no duplicate native stress timer |
| Extension bladder/bowel, urgency and last-applied time | B47ANCE-owned | Server biology domain | Private store and elimination receipts | Field-specific elapsed-game-time integration; no client timestamps |
| Housebreaking 0–5, preferred surfaces and potty zones | B47ANCE-owned | Server learning/home domain | Private records / server-owned zone records | Independent from obedience, breed and working history |
| Handler ACL, ownership and historical relationship | B47ANCE-owned | Server authorization domain | Private store | Stable account/character policy; revoke old active rights and projections on transfer |
| Per-handler discoveries | B47ANCE-owned | Server observed-discovery domain | Private per-handler record | Observation grants discovery, never new dog XP |
| Cue records, proficiency and dog working skills | B47ANCE-owned | Server learning domain | Private store | Only server-observed eligible practice; no automatic group mastery |
| Human training perk XP / knowledge | Shared operation | Native server XP system through validated action | Native player persistence | Server verifies event and dedup; custom perk registration/load still requires proof |
| Rolling structured/passive reward ledger | B47ANCE-owned | Server reward arbiter | Private durable receipts | Separate budgets over 24 game hours; revision/time rollback recovery precedes awards |
| Current task, priority, lease and interruption state | B47ANCE-owned | Server task arbiter | Durable logical intent; transient native route | Native behavior seam required; no second competing native movement decision |
| Item/load/door reservations and receipts | B47ANCE-owned | Server transaction coordinator | Private receipts, validated public item/object identity | One claimant; physical source/destination reconciliation on retry/restart |
| Physical items and container contents | Native-owned | Native authoritative inventory operation | Native item/container save/sync | Validate real items, permission, reach, capacity and weight; no create-before-remove shortcut |
| Door base state/collision/barricades | Native-owned | Native door/world subsystem | Native world objects | Never disable whole-door collision or override normal lock/open function |
| Flap installation, mode, ACL, power policy and durability extension | B47ANCE-owned | Server door domain | Proved persistent replicated world-object record | Installation/repair uses inventory transaction; traversal needs proved native collision transition |
| Physical urine/feces identity, age and cleanup receipt | B47ANCE-owned | Server sanitation domain | Proved physical world object plus private receipt | One elimination-to-object relationship; no waste at stale transported position |
| Zombie position, perception, crawl and damage | Native-owned | Native zombie subsystem | Native network/world state | Bounded verified stimuli/requests only; no replacement zombies or collision bypass |
| Packs, pair relationships and task-specific influence | B47ANCE-owned | Server pack domain | Private bounded records | Per-dog task writer remains unique; no universal alpha or inherited skills |
| Spawn decisions and population ledger | B47ANCE-owned | Server population coordinator | Private durable decision/identity ledger | Deterministic decision key plus reserved ID; no repeated population spawn on chunk reload |
| Sandbox effective configuration and revision | B47ANCE-owned interpretation | Server configuration interpreter | Server sandbox plus configuration-transition record | Clients receive effective capability/value projection; server clamps/rejects invalid values |
| Coarse visible status / discovered health / eligibility | Derived presentation | Server allowlisted projection builder | Bounded actor-specific packets | No undiscovered raw traits, histories, exact health findings or rewards |
| UI layout, input bindings, accessibility and local animation display | Derived local presentation | Each client | Local preferences | No custom gameplay networking for UI coordinates; rendering cannot own shared state |

## Handler and projection contract from M1

Roles are observer, authorized handler, owner and operator. Observers receive only physically visible coarse status. Handlers receive their discovered fields and permitted actions. Owners manage grants/transfers, with server-validated proximity and ownership. Operator repair is an explicit audited recovery operation, not a client command. Proposed ACL account key is the exact canonical server-authenticated username from the server OnClientCommand player object, namespaced to the world; vanilla ClientCommands.lua:137/156/1296/1307 uses player:getUsername() in this callback domain. Never accept an owner/account string from client args or use a display name. Account rename/reuse requires explicit operator migration rather than silent reassignment. Confirm uniqueness/authentication/lifecycle on Steam and non-Steam dedicated fixtures before acceptance.

HandlerPermissionMode controls owner-only versus owner-and-explicit-grants. OwnerAfterCharacterDeath controls retained account access versus requiring a new validated claim; both preserve dog ID and prior relationships. Human perk XP remains native character-owned and is never inherited by a new character. Private relationship/discovery episodes use a server-created episode identity tied to proved native character lifecycle observations; old histories remain attached to the dog and are not automatically exposed to a new character. Safe new-character detection is an explicit T-AUTH verification gate, not a guessed hook or trusted client ModData UUID.

An initial unclaimed dog can be inspected without exposing hidden records. Claiming requires a server-observed reachable interaction; ownership acquisition, cooperative grants, transfer and revocation are serialized revisions. Each response carries opaque dog reference, binding generation, record revision, protocol version and allowlisted role projection. Protocol mismatch refuses mod actions. Unknown future schema preserves records and disables writes. Disconnect cancels actor-bound pending intent; reconnect receives a fresh projection after authorization. Permission removal invalidates projection caches and queued replies.

## Arbitration acceptance

Tests T-AUTH, T-NATIVE, T-TASK, T-PRIVACY and T-PROTOCOL in [the MP matrix](MULTIPLAYER_ACCEPTANCE_MATRIX.md) must demonstrate that native updates and B47ANCE tasks do not independently select conflicting destinations or advance the same need. Instrument field writers with bounded diagnostics containing dog reference/revision and capability status, never hidden traits or private records. Source existence of a path or block-movement method is not an exclusive lease guarantee.
