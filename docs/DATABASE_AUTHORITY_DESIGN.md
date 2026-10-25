# Database-authoritative canine design

Project Version: 0.2.0-dev.10

Status: DESIGN PROPOSAL; gameplay implementation blocked. The two latest user handoffs authorize this design revision, including natural bonding, independent secondary relationships, default offline self-care and one active task/handler lease. They do not enable ownership, SQLite, storage mode or a new native controller. Original raccoon presentation, schemas and runtime source remain unchanged.

## Authority and scope

The permanent dog is a private logical record keyed by `(worldId, dogId)`. A physical animal is a temporary server-associated representation with a process-local binding. The store owns permanent identity/relationships/history; the native engine remains the physical movement/collision/animation writer. One server controller chooses authorized logical work through a **proved** native control seam. It cannot become a second movement writer, teleport a dog or fabricate success.

This changes the proposed identity abstraction; it does not prove safe replacement. The earlier [Option A NO-GO](OWNERSHIP_GO_NO_GO_DECISION.md) remains valid for automatic native-to-private authenticity. Neither a database row nor a current-process map proves that no old saved body exists. No replacement on absence, copied-marker adoption or client-owned identity is permitted. Natural population jobs must reserve a private identity/creation receipt **before** their own authorized native construction; a scan discovering an unregistered animal cannot silently mint a canonical stray.

The latest supplement's priority hierarchy, eight public task states and `SelfCare` / `StoreOffline` option labels govern this proposal. The first supplied handoff ends during section 15; no missing continuation is invented. The complete task supplement supplies the arbitration requirements. Older contracts retain their baseline text and evidence; links identify this companion where proposed semantics changed. Existing offline ClaimDog rules are historical prototype behavior, not the new bonding design or an exposed gameplay endpoint.

## Components and trust boundaries

| Component | Owns / writes | Does not prove |
| --- | --- | --- |
| Private repository | Dog aggregate, relationships, ownership, task/transaction intents, tombstones, checkpoint lineage | Native origin, joint disk atomicity or absence of unloaded bodies |
| Authenticated actor adapter | Server-resolved principal, active connection/character episode, capability context | Any ID/name/role submitted in client args |
| Binding registry | Canonical key ↔ exact current native reference, server session, generation, lifecycle state, admission evidence | Durable authenticity by itself; no reference is persisted as authority |
| Relationship service | Bounded verified interaction receipts, bond/trust/familiarity, owner CAS, delegation | Native feeding/petting success from a UI click or client assertion |
| Task/lease coordinator | One active task, one handler lease, resource claims, interruption/commit receipts | A safe exclusive native task writer until verified |
| Native adapter | Server-validated observation/intent through audited APIs; native physical writer | Permanent dog identity from native ID/marker |
| Projection/UI service | Role-allowlisted visible relationship/activity/refusal data | Permission from UI availability or cached progress |

Clients submit bounded intent with a dog selector, action, expected revisions and session/request identity. The server resolves actor, private record, configuration, lifecycle, binding, permissions, cooperation, skills, equipment, reachability, lease and actual transaction evidence. Revalidate immediately before commit. A selector/task UUID is not authorization. Role-filtered results are rebuilt for each requester; never send private snapshots, Steam IDs, hidden traits, medical history or complete ACLs in ModData.

## Store feasibility decision

[VERIFIED — native/source] Build 42.21, Steam build 25485521. D01–D07 in [the source ledger](native-database-redesign-evidence.json) are bounded current findings. SQLite/JDBC implementation exists inside the game, but no suitable general Lua-exposed private SQLite connection/transaction API was verified in the inspected globals/exposure registry. Do not reuse the server account database, add tables there, open a JDBC connection, install a binding, bridge or external service.

**Selected design candidate: extend the existing private file-store architecture.** This means a logical database over original Lua records, not an implemented SQL database. Current PrivateStore only permits its narrow ownership/event changes; it cannot already commit the proposed health/task/relationship schema. Codec limits (1 MiB envelope, 8,192 nodes, depth 16, 16,384-byte string) and full-snapshot cost need explicit size/retention/load proof. No promise of unlimited dog history, high-frequency snapshots or atomic multi-file shards is made.

The proposed initial commit unit is one world-scoped aggregate containing dog rows, relationship rows, owner index, task/resource reservations and receipts. A single server coordinator serializes expected-revision updates and prepares a complete candidate before publication. A relationship reaching primary bond 100, owner assignment and its event must be one private commit unit. Cross-dog item/pack claims also need one shared transaction scope. Splitting tables into independent files would lose these guarantees without a new journal/coordinator proof.

Logical validation/CAS/unique constraints are feasible offline designs. Durable power-loss commit, atomic slot promotion and native/private coordination remain BLOCKED. Existing write/close/readback is not fsync; adding another checksum or generation is not a final-session seal. Future implementation must define prepare/native-effect/reconcile/commit phases, retain old data, and quarantine ambiguity. No migrated or empty store is initialized automatically.

## What must be proved before live work

1. Lossless authenticated server principal extraction, including connection-derived SteamID64; client helper is not a server adapter (D02/D03).
2. Safe managed native lifecycle: save exclusion **or** authoritative reconciliation/withdrawal/restoration with complete duplicate prevention, including worker/item/vehicle/corpse paths.
3. One native movement/control producer, authenticated physical interaction receipts and game-time catch-up ownership.
4. Private aggregate schema/transaction/migration and actual crash/dedicated restart evidence.

The missing requirements remain in [feasibility and lifecycle](OFFLINE_SELFCARE_LIFECYCLE.md). The smallest permitted continuation is offline aggregate/schema and authorization design, then a concrete native/API proof; no live writers or speculative guards. No new version is invented for this compatible design-only revision of unreleased dev.7. An implementation/migration version must be classified before that work begins.

Current native-baseline checks additionally FAIL for five changed loose class overrides. Packaged D01–D07 inputs match, but they do not attest effective runtime. [The validation record](DATABASE_REDESIGN_VALIDATION.md) preserves exact drift and gates; no installed files or historical hashes are repaired/rewritten.

Companions: [schema](PERSISTENT_CANINE_AND_RELATIONSHIP_SCHEMA.md), [bonding](NATURAL_BONDING_AND_PERMISSIONS.md), [tasks/leases](ACTIVE_TASK_AND_HANDLER_AUTHORITY.md), [sandbox](DATABASE_REDESIGN_SANDBOX.md), [acceptance](DATABASE_REDESIGN_VALIDATION.md). No third-party implementation is inspected or copied.
