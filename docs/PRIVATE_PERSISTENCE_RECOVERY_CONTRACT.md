# Private persistence and recovery contract

Project Version: 0.2.0-dev.9

Latest user-directed database/relationship/task proposal: [PERSISTENT_CANINE_AND_RELATIONSHIP_SCHEMA.md](PERSISTENT_CANINE_AND_RELATIONSHIP_SCHEMA.md). Its logical identity, natural bonding, offline self-care and task/lease semantics supplement/supersede corresponding proposed design details below; no runtime capability or historical evidence is upgraded. The baseline body is preserved.

The current [loadable persistence diagnostic](NATIVE_BOOTSTRAP_TEST.md) adds a single explicit operator-confirmed first-store attempt, receipt-first preservation and one temporary carrier. No automatic new-world inference or uncertain retry exists. The operator asserts a new disposable world; missing files alone never authorize it. Private records remain private, but the native marker cannot prove multiplayer provenance. Dedicated ownership preparation is blocked. The [identity audit](NATIVE_IDENTITY_AUTHORITY.md) adds read-only recovery summaries from the private snapshot, so missing or forged markers cannot select the displayed saved UUID. No schema migration or auto-rebind occurs.

M0R design, 2026-10-12. FEASIBLE conservative storage protocol; crash/power-loss durability and coordinated native saves EXPERIMENTAL. Transactional gameplay is BLOCKED until reconciliation/durability acceptance. Lua-only; no Java bridge fallback. [Evidence](M0R_SOURCE_EVIDENCE.md), [identity](CANINE_IDENTITY_CONTRACT.md), [tasks](TASK_ARBITRATION_CONTRACT.md).

## Current implementation boundary

The 0.2.0-dev.3 [native pairing adapter](NATIVE_PAIRING_LIFECYCLE.md) reads an existing strict anchor during OnInitGlobalModData and allows one pending checkpoint publication after ownership-only private readback. Duplicate events/live reads do not promote it; native saving/restart remains a runtime gate. The preceding 0.2.0-dev.2 prototype reads native markers and prepares ownership-only private snapshots. Both slots must validate, and selection requires an exact trusted operator-paired checkpoint. It preserves a newer unpaired slot and refuses corruption instead of repairing automatically. It never initializes missing stores, updates native markers, registers save hooks or claims readback as a durable save. See [implementation and tests](NATIVE_PERSISTENCE_SLICE.md) for the exact format, technical bounds, single-coordinator limitation and remaining native gates. The following full protocol remains the design target.

## Privacy and location

Hidden records live only in server memory and a server-host private file store. Native global ModData can be requested by table name in inspected source, so it contains at most a nonsecret world/checkpoint anchor; animal/player ModData contains only the nonsecret binding marker. Client projections are built from an explicit role allowlist, never by serializing the private record and removing fields. Server logs and diagnostics omit hidden values, medical findings, private player data and full ACL records.

Candidate path using getFileWriter/getFileReader: <server cache>/Lua/B47ANCEDDogTraining/<worldUUID>/slot-a.json and slot-b.json, with bounded immutable receipt segments. Components are server-generated UUIDs/fixed names; never raw account/save/user input. Allowed .json extension and relative path semantics are source-supported. getCurrentSaveName identifies the native save-directory locator, not durable world identity. Startup readers use createIfNull=false; a missing file must not be converted into an apparently empty valid record. getModFileWriter is excluded because installed mod directories are not world-private storage.

The original M0R proposed storeSchema=1, markerSchema=1 and protocolSchema=1 independently of Project Version. The current [native/private slice](NATIVE_PERSISTENCE_SLICE.md) implements a bounded snapshot/marker schema 1 and preparation protocol subset; full automatic native pairing, transactions, migrations and durable receipts remain unimplemented. The envelope records world UUID, native-save locator fingerprint, store schema, checkpoint token, predecessor token, sequence, allocation epoch/highwater, accepted animal binding-token chains, record count, payload byte length, canonical payload checksum and transaction receipts. Serialize in a defined key order with explicit numeric/string limits and a documented pure-Lua checksum implementation selected in the prototype. The checksum detects accidental corruption; it is not authentication or a substitute for filesystem permissions. Unsupported future schema becomes read-only/quarantined; migrations preserve originals, are explicit and tested, and never silently discard fields.

## Atomic-write limitation and candidate recovery strategy

The verified writer returns a LuaFileWriter backed by PrintWriter. Its exposed write/writeln/close operations do not establish fsync, durable error reporting or atomic rename. append=false overwrites a destination. Therefore no atomic-write guarantee is asserted. Readback can detect some failure/corruption, not prove data survived power loss. Do not expose atomic rename or flush APIs that have not been established.

Candidate sequence: preserve the last validated slot; write the inactive slot completely; close; read back and validate checksum/length/schema/world/predecessor; record its prepared checkpoint; request/observe the native world-save/checkpoint operation only through a proved Lua seam; then reconcile the public anchor and private slot. Keep both predecessor and prepared versions until their native pairing is verified. A highest-sequence private file alone is never selected as current. Receipts are bounded and retained until no supported replay/backup window can need them; compaction requires a verified checkpoint and preserves unresolved claims.

No reliable dedicated save completion/durability event has been proved. The 0.2.0-dev.3 source audit establishes the narrower existing-anchor read/trust path: native load precedes its event, and received network tables do not automatically replace the authoritative map. Actual native persistence and effective class loading still require runtime proof. They are explicit prototype investigations. If Lua cannot safely correlate completion, the candidate cannot promise automatic cross-store recovery. Lua-only alternative: operator-quiesced paired backup/restore plus conservative startup quarantine whenever pairing is not provable. This preserves private records and blocks ambiguous gameplay; it does not claim atomic live-world saves or satisfy automatic recovery by assertion.

## World/save pairing

Create world identity once in an explicitly recognized new-world initialization, not whenever a file is absent. Candidate public world ModData anchor carries only worldId/checkpointToken/schema; no secrets. Fresh packaged inspection finds incoming global-data packets emit a separate receive table without automatically replacing the authoritative map. Never register a receive-to-anchor copier; loaded-anchor capture remains separate from an in-memory pending update. The private store keeps the authoritative expected anchor, locator and predecessor chain. A copied save, server reset, missing anchor or changed locator triggers recovery review rather than silently binding an unrelated private directory.

Paired backup procedure, operator-run only: quiesce new mod commits; reconcile in-flight transactions; establish a matched checkpoint with the proved native save mechanism; stop or safely freeze the world using separately authorized operator procedure; back up native save and corresponding private directory together; produce a manifest of checkpoint/schema and file hashes; restore both while stopped; validate before simulation. Ordinary world-only backups are incomplete for this private-store candidate. M0R does not run backups or change server configuration.

| Startup / crash condition | Required result |
|---|---|
| Native anchor and valid private slot match | Rebind identities; reconcile receipts before accepting gameplay |
| Prepared private slot newer than native anchor | Preserve prepared data; evaluate predecessor and native real state, never blindly advance |
| Native world newer than private slot | Stop affected actions; reconcile exact physical records or restore paired checkpoint |
| World-only or private-only rollback | Detect mismatch and quarantine; no new identity, budget reset or replay reward |
| Truncated/invalid slot | Preserve damaged bytes; consider matching valid predecessor; never parse partial records as defaults |
| Both slots missing/corrupt on existing world | Quarantine managed identities; explicit operator recovery, never reroll |
| Missing private record for public dog marker | Quarantine that dog and claims; no auto-adoption or replacement |
| Stale private record without native representation | Retain detached/tombstone/recovery state; no automatic respawn |
| Unknown schema / foreign world / ambiguous generations | Read-only preservation and blocked writes |
| Exact paired backup restore | Restore native and private checkpoint together; invalidate transient sessions/routes; prove no duplicate items/dogs |

## Transaction receipts and commit boundary

Each restart-sensitive action has a server-generated durable transaction identity plus an actor/session dedup token, dog ID/generation, target/item identity, source/destination fingerprint, preconditions, intent/config revision, phase and observed result. Client action tokens are not authority. Phases: PREPARED → PHYSICAL_COMMIT → OBSERVED → RECEIPTED → PROJECTED. Serialize source/item/door claims and recheck ACL, reach, capacity and actual native item quantity before commit.

Crash reconciliation inspects physical source/destination and saved dog state as candidate evidence, never proof from location alone. An item can return to its source through another legitimate operation or rollback. Decide committed/uncommitted only from matching receipt/checkpoint, exclusive claim and sufficient exact pre/post transition evidence; both/neither/source-only/destination-only remains ambiguous when that evidence is missing. Quarantine without automatic retry/reward. Never blindly remove/recreate, refund, award again, or accept client success. Item durability/consumption and waste cleanup need the same proof before cleaning, construction, reinforcement or retrieval. Biological discharge pairs need reduction with a unique elimination receipt and configured physical result. No irreversible item mutation is offered while its restart semantics are unresolved.

Reward receipts persist accepted server-observed events and rolling game-time windows. Rate limits limit traffic; idempotence prevents repeated commits. On protocol/session restart, old tokens cannot create new rewards. Reconnection never refreshes budgets; rollback remains a recovery operation before accepting awards.

## Acceptance and retained limitation

T-PRIVACY probes named global tables, synchronized animal/player markers, packets, projections and client logs. T-RECOVERY tests partial writes, missing files, future schemas, both one-sided restores, wrong world, kill/crash at every phase, paired restore and native-save ordering. T-TRANSACTION tests repeated packets, full inventory, concurrent handlers, death/unload and commit-before-receipt failure. Readback checks are offline candidates; actual process-crash, dedicated restart, Linux path/permissions and power-loss behavior remain NOT TESTED. Any unresolved pairing/error-observation gap blocks automatic durable gameplay claims and has no Java escape route.
