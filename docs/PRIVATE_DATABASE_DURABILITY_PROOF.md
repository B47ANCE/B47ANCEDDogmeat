# Private database durability proof

Project Version: 0.2.0-dev.9

**D5 FEASIBLE for the tested logical transaction subset; D6 EXPERIMENTAL for fault handling. Durable native/private atomic commit remains BLOCKED.** This is a Lua file-store experiment, not SQLite. No JDBC, service, binding or production migration is added.

## What was implemented and tested

`tests/lua/database_store_fixture.lua` is an isolated original test fixture using the existing canonical bounded Codec, Guard and Identity utilities. It is outside src/, absent from source-inventory and the loadable assembly, and has no engine calls or runtime caller. Its fixture envelope/schema are intentionally separate from production ownership snapshot schema 1 and the full proposed canine schema. Alice/Bob, bond 90 and increment 10 are synthetic transaction inputs, not authenticated players or tuned progression defaults.

One world-scoped aggregate contains dogs, independent relationships, unique primary-owner index and receipts. Canonical `(worldId,dogId)` keys, exact fields, bounded revisions and cross-table ownership consistency are validated before sealing. Eight dogs, eight relationships per dog and 32 receipts are **fixture safety bounds**, not proposed server population/history limits. Existing Codec limits still apply. No claim of production capacity, retention or high-frequency persistence is made.

The only mutation experiment accepts an explicit synthetic actor and expected aggregate/dog/relationship revisions. It prepares one complete candidate containing the bond increment, first-owner CAS and receipt. The selected in-memory snapshot remains unchanged; there is no private/native promotion. Two sequential coordinators opened on the old bytes cannot both prepare: the second detects disk change. This assumes one serialized writer; it is not a multi-process lock or filesystem CAS.

[TESTED — Windows offline Lua 5.1 through Lupa 2.6, disposable files] 31 added cases, 406 total, including two separate-VM prepare/recover phases:

- First 100 bond, unique owner/index/event in one candidate; stale aggregate/dog/relationship revisions; competing stale writer; secondary 100 without transfer.
- Exact receipt replay after reopen returns the prior result without writing; changed request under that receipt refuses. No physical exactly-once guarantee follows.
- Missing/mismatched synthetic context, malformed/future/contradictory aggregate, persisted active-lease field, foreign world, detached reads and ambiguous same-checkpoint slots refuse.
- Injected exception before write, partial write, exception after complete write and readback corruption preserve selected bytes and lock the writing session. A complete prepared candidate may exist even when the caller received failure; automatic effect retry is unsafe.
- Exact external checkpoint pairing, pending preparation, private-only rollback refusal, repeated reopen and fresh-VM retention/replay.
- Synthetic fixture revision 0 → 1 conversion is detached/idempotent; invalid/future and existing production-schema shapes are refused. This does not migrate real dog records or fabricate natural-bond history for old claims.
- A mathematical synthetic SteamID collision confirms why string identity cannot be reconstructed from a rounded double. It is not a Kahlua/runtime authentication test.

## Actual recovery and durability guarantees

| Boundary | Established behavior / remaining limitation |
| --- | --- |
| Logical candidate | All related changes validated/sealed together before I/O; contradictions are refused |
| Inactive-slot write | Only one inactive file is written; old selected bytes retained. Write exception/readback failure locks this session |
| Reopen | Both slots must decode and match world; exact externally supplied checkpoint selects. No newest-sequence heuristic or automatic empty repair |
| Corruption | Malformed/missing/ambiguous files preserve evidence and refuse. Checksums detect tested accidental damage; they are not authentication/MACs |
| Private rollback | New external pair against restored old private files refuses. Restoring both files **and** pair consistently can succeed as old data; no independent anti-rollback reference exists |
| Native pairing | Pairing in the fixture is a trusted test input. It does not prove native save success, body origin, all saved representations or durable completion |
| Power loss | Python file write/close and Lua fault injection are not abrupt process/power tests. A storage stack may lose/reorder acknowledged data. No fsync, atomic rename/promotion or crash-durable multi-file transaction proved |
| Production adapter | P10: GlobalObject.getFileWriter wraps PrintWriter in LuaFileWriter; write/close delegate. Current PZCache adds bounded readback; swallowed PrintWriter errors remain possible. Readback is preparation, never durable native commit |

The current production PrivateStore still allows only its ownership/event/ledger subset. It is byte-unchanged. The experiment is not suitable as a drop-in replacement: full record categories, resource claims, durable tombstones, retention/capacity, real migration and a reviewed commit/reconciliation protocol remain required. No active handler lease or native pointer is durable authority; restart requires fresh session/binding/permission validation. No live lease service was added.

Rollback support is limited to preserving original fixture bytes and explicit diagnostic pairing. Downgrades and production migration are not promised. Never use real player saves for these tests. [Runtime procedures](DISPOSABLE_RUNTIME_VALIDATION_PLAN.md) separate source/offline work from future real crash/restart evidence.

Exact commands are recorded in [the decision/validation entry](DATABASE_AUTHORITY_GO_NO_GO.md). Offline transaction feasibility does not change Option A NO-GO, D1–D4 or G6–G8.
