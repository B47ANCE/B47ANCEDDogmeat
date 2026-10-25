# Option A ownership decision

Project Version: 0.2.0-dev.10

**NO-GO — trustworthy automatic native-to-private ownership continuity is unavailable through the verified Lua boundary on the inspected Build 42.21.** Do not enable multiplayer ownership or add speculative guards. Neither GO nor CONDITIONAL GO is justified. This is the engineering decision for the required guarantees and current evidence, not a universal impossibility theorem about every future Lua design or game build.

Decision date: 2026-10-14. Actual starting HEAD/upstream `fda2538e64624babbd1606b4e53a0935d80c02f9`; docs/m0r-contracts was 0 ahead/0 behind upstream, 15 ahead/0 behind origin/main. Only the pre-existing AGENTS.md modification was dirty; it remains preserved/excluded. Root VERSION is 0.2.0-dev.7. Option A is compatible source-investigation/documentation/test work within this unreleased version, with unchanged runtime/save/config/API contracts and no invented version.

## Why this is the decision

1. **Missing trusted persisted origin key.** Animal serialization stores ModData, mutable animalId/itemId and virtual group/state. The superclass UID is regenerated on construction and not in that format; entity net ID is positional; online IDs are simulator references. None binds the same legitimate physical animal to private P across restart. A02/A03/A10 in [the hashed evidence ledger](native-save-load-evidence.json).
2. **Missing complete policy seam.** Native factory load and worker admission bypass the nine selected action wrappers. No sufficient pre-admission Lua callback with trusted origin/transition evidence was established in these paths. A05/A06; [seam assessment](EXCLUSIVE_ADMISSION_SEAM_ASSESSMENT.md).
3. **Missing previous-session/save attestation.** Native animal save at dedicated offset 71 and global data save at 146 are ordered calls, not a durable joint transaction. OnInitGlobalModData predates animal initialization; SP OnPostSave also follows caught save failure; inspected pause events run on clients. No final exclusive durable session seal is established. A04/A07/A08/A09.
4. **Additional marker checks cannot solve equal evidence.** A copy can present the same diagnostic observation and private checkpoint under the stated copy-reachability premise. The fresh-VM witness confirms the current boundary sees no differentiator and quarantines both. It does not prove a native client exploit; a certified complete upstream cut could change the premise, but none exists. [Authenticity assessment](PREVIOUS_SESSION_AUTHENTICITY_PROOF.md).
5. **Required runtime proof is absent.** 375 offline cases and CI cannot establish native authenticity, ordinary-client exploit closure, durability or vanilla compatibility. G6 NOT TESTED; G7 BLOCKED / NOT TESTED; G8 BLOCKED. Current local effective pristine runtime is also unverified. [Results](ADVERSARIAL_IDENTITY_TEST_RESULTS.md).

Selected ordinary pickup/trailer actions are restrictable; the complete adult/world-only lifecycle is not proven because save/load/streaming remain mandatory. Therefore narrowing the proposal does not earn CONDITIONAL GO. Reconstruction classifications are in [NATIVE_RECONSTRUCTION_PROVENANCE.md](NATIVE_RECONSTRUCTION_PROVENANCE.md).

## Smallest sufficient engine/API requirement — specification only

The missing capability is an **engine-owned authenticated animal lifecycle binding** exposed to server Lua, with these semantics:

- A persistent per-animal origin identity allocated/validated by the authoritative engine, inaccessible to client assignment, distinct from public ModData, and not duplicated by ordinary copy/load/import operations. Restoring the legitimate world animal must retain it; unauthorized duplicate/import must be separately identifiable or rejected before authorization. A random read-only string alone is insufficient if serialized copies retain it without engine validation.
- A server-side pre-admission/transition policy callback, or equivalent complete engine enforcement, covering load/worker return/item/vehicle/hutch/growth/corpse paths in the declared supported lifecycle. It must carry trusted origin/source/target/generation evidence and support refusal/quarantine before companion authority. Unmanaged animals retain vanilla behavior.
- A recoverable native save-generation/lifecycle receipt bound to private commit and explicit success/failure/quiescence ordering. For guarantees including coordinated backup freshness, an independent retained trusted monotonic reference or explicit rollback semantics is also necessary.

These are required semantics, **not existing method names or an implementation proposal to patch Java**. A single engine API could bundle them; no custom Java/JAR/agent/native modification is authorized. Revisit only if the vanilla engine exposes an adequate verified contract or a concrete Lua-only mechanism supplies all equivalent guarantees. Actual SP/dedicated adversarial evidence would still be required.

## Operator-controlled alternative — not enabled or approved

Retain private logical dog/ownership/history records; after restart keep physical bodies unbound. An operator could explicitly choose a representation after an auditable review, with a private reconciliation receipt and no auto-respawn/first-match adoption. This accepts operator judgment about physical continuity and **changes the automatic same-legitimate-animal contract**. It requires user scope approval before design/implementation. Current diagnostic has no such association command or bypass.

The eight requested deliverables are this decision, [trace](NATIVE_SAVE_LOAD_AUTHORITY_TRACE.md), [seam](EXCLUSIVE_ADMISSION_SEAM_ASSESSMENT.md), [authenticity](PREVIOUS_SESSION_AUTHENTICITY_PROOF.md), [reconstruction](NATIVE_RECONSTRUCTION_PROVENANCE.md), [prototype disposition](LUA_ONLY_OWNERSHIP_PROTOTYPE.md), [test results](ADVERSARIAL_IDENTITY_TEST_RESULTS.md) and [disposable procedure](DISPOSABLE_RUNTIME_TEST_PROCEDURE.md).

No production runtime code changes, speculative guards, ownership enablement, model/growth/gameplay expansion, installed game/dependency changes, launch/deployment, Workshop upload, stable archive/tag or PR merge. The next action is a concrete vanilla API capability change or an explicit alternative-contract scope decision; continuing to add marker checks is not a resolution.
