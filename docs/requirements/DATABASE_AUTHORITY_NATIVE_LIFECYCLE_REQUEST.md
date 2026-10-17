# CODEX HANDOFF — Database Authority & Native Lifecycle Proof

**Project:** B47ANCE'd Dogmeat  
**Technical Mod ID:** `B47ANCEDDogmeat`  
**Reported Version:** `0.2.0-dev.7`  
**Target Game:** Project Zomboid Build 42.21  
**Architecture:** Standalone, Lua-only, dedicated-server-first  
**Temporary Test Carrier:** Vanilla raccoon  
**Current Status:** Database-authoritative design complete; gameplay implementation blocked

## 1. OBJECTIVE

Resolve or conclusively characterize the remaining technical blockers preventing secure, persistent multiplayer dogs.

Investigate four foundational capabilities:

1. Authenticated server-side player identity.
2. Native animal lifecycle control and duplicate prevention.
3. Server-authoritative physical interactions and movement.
4. Durable private database transactions and recovery.

The desired architecture is:

**Private logical dog record → Server canine controller → Native physical animal representation**

The database owns permanent identity, relationships, ownership, training, health, and persistent state.

The native engine owns physical movement, collision, animation, and appropriate world interactions.

Do not create competing physical-state writers.

## 2. EXISTING EVIDENCE

Read the latest repository documents before beginning.

Required references:

- `DATABASE_AUTHORITATIVE_CANINE_DESIGN.md`
- `PERSISTENT_CANINE_AND_RELATIONSHIP_SCHEMA.md`
- `NATURAL_BONDING_AND_PERMISSIONS.md`
- `ACTIVE_TASK_AND_HANDLER_AUTHORITY.md`
- `OFFLINE_SELFCARE_LIFECYCLE.md`
- `DATABASE_REDESIGN_SANDBOX.md`
- `DATABASE_REDESIGN_VALIDATION.md`
- `OWNERSHIP_GO_NO_GO_DECISION.md`
- `NATIVE_SAVE_LOAD_AUTHORITY_TRACE.md`
- `EXCLUSIVE_ADMISSION_SEAM_ASSESSMENT.md`

Discover exact paths in the repository.

Do not assume the documents' names or locations establish their contents.

Preserve previous NO-GO findings unless new source or runtime evidence directly resolves them.

## 3. VERIFY CURRENT ENVIRONMENT

Before implementation:

1. Verify repository root and current branch.
2. Read canonical `VERSION`.
3. Record actual HEAD.
4. Inspect working-tree changes.
5. Preserve the existing uncommitted `AGENTS.md` modification.
6. Recheck source and native hashes.
7. Investigate the five changed loose native class overrides.
8. Distinguish packaged Build 42.21 behavior from modified local runtime behavior.

Do not overwrite or remove native overrides.

Do not modify installed game files.

Report environmental drift before interpreting new test results.

## 4. AUTHENTICATED PLAYER IDENTITY

Investigate a trustworthy server-side principal adapter.

Required identity:

- Authenticated SteamID64 when available.
- Server connection identity.
- Current character/player episode.
- Server session.
- Relevant ownership and permission context.

The server must derive the actor from authenticated connection information.

Never trust:

- Client-submitted SteamID.
- Player display name.
- Client-supplied owner ID.
- Client-submitted permission flags.
- Client-supplied bond progress.

### Required proof

Demonstrate that the server can associate an incoming request with the correct authenticated player.

Test:

- Two simultaneous players.
- Reconnect.
- Character death and replacement.
- Forged SteamID arguments.
- Missing identity.
- Stale connection.
- Unauthorized dog access.

If no trustworthy Lua-exposed identity path exists, retain BLOCKED status.

## 5. NATIVE ANIMAL LIFECYCLE

Investigate whether the mod can safely manage physical dog representations without relying on native animal IDs as permanent identity.

The database must remain authoritative for the logical dog.

The native animal is a temporary representation.

### Required investigation

Trace:

- Authorized animal creation.
- Native save.
- Native restoration.
- Chunk streaming.
- Worker reconstruction.
- Carrying.
- Inventory conversion.
- Trailer and vehicle transport.
- Growth and maturation.
- Death.
- Despawning.
- Reprovisioning.

Determine whether managed native animals can be:

1. Excluded from ordinary native restoration; or
2. Authentically reconciled before any replacement is created.

A missing native reference must not trigger automatic spawning.

### Duplicate prevention

Prove that:

- One logical dog cannot have two active native bodies.
- Copied markers cannot authorize ownership.
- A stale native body cannot be silently adopted.
- A restored native body cannot coexist with an automatically spawned replacement.
- Ambiguous representations are quarantined.

Do not introduce speculative admission guards.

The existing Option A NO-GO remains effective until an alternative lifecycle is actually proven.

## 6. SERVER MOVEMENT AND PHYSICAL INTERACTIONS

Investigate one authoritative movement and task-control mechanism.

The server must decide the dog's authorized logical task.

The native engine remains the physical movement writer.

Do not directly compete with vanilla movement updates.

### Movement proof

Investigate:

- Follow.
- Stay.
- Return to assigned area.
- Movement cancellation.
- Navigation around obstacles.
- Chunk unloading.
- Handler disconnect.
- Multiple players observing movement.

### Interaction proof

Investigate server-observed:

- Feeding.
- Petting.
- Calm proximity.
- Drinking.
- Resting.
- Equipment use.

A client click must not independently prove successful interaction.

### Bonding evidence

Future bonding progression must use verified interaction receipts.

The intended rules remain:

- Calm proximity contributes small amounts.
- Feeding contributes meaningful progress.
- Accepted petting contributes progress.
- At 100% primary bond, the dog can be named and becomes owned.
- The dog loosely follows the owner.
- A collar and lead provide practical early-game control.

Do not implement bonding gameplay during this proof task.

## 7. PRIVATE DATABASE DURABILITY

The proposed database is currently a private Lua file-store architecture, not verified SQLite.

Do not add JDBC, external services, native libraries, or custom Java integration.

### Required investigation

Define and test:

- World-scoped storage.
- Canonical dog identity.
- Relationship records.
- Ownership assignment.
- Transaction revisions.
- Atomic logical updates.
- Crash recovery.
- Corruption handling.
- Backup rollback.
- Schema migration.
- Save checkpoint reconciliation.

### Commit guarantees

The design must support atomic logical operations such as:

- Bond reaches 100%.
- Primary owner is assigned.
- Relationship event is recorded.

These must commit together.

A partial operation must not leave a dog with contradictory ownership state.

### Durability limitations

Write/close/readback is not equivalent to guaranteed power-loss durability.

Do not claim atomic disk persistence without verified file-system semantics.

If a stronger Lua-only durability mechanism is unavailable, document the actual guarantees and failure modes.

## 8. OFFLINE OWNER DESIGN

Preserve the approved sandbox modes.

### Default: SelfCare

When the owner disconnects:

- Dog remains in the world.
- Dog manages hunger and thirst.
- Dog rests and seeks shelter.
- Dog uses appropriate bathroom areas.
- Dog remains within its assigned safehouse where practical.
- Dog leaves for essential needs when safe.
- Dog may use its assigned doghouse.
- Trusted secondary handlers may care for it.

### Optional: StoreOffline

The dog is withdrawn when the owner disconnects and restored when the owner returns.

This mode must remain disabled until safe native withdrawal and restoration are proven.

Do not implement either mode during this foundational investigation.

## 9. TRUSTED SECONDARY HANDLERS

Preserve independent per-player sub-bonds.

Secondary players may eventually become:

- Trusted caretakers.
- Trusted trainers.
- Trusted handlers.

Trust alone does not transfer ownership.

The server must validate both relationship eligibility and owner delegation permissions.

Only one active handler lease may exist per dog.

Do not implement gameplay permissions until authenticated principal extraction and authoritative dog binding are proven.

## 10. PROOF-OF-CONCEPT LIMITS

If a verified native/API seam is found, implement only the smallest isolated proof needed.

Use the existing raccoon carrier.

Permitted scope:

- Read-only native observations.
- Authenticated principal extraction.
- Private-store transaction fixtures.
- Lifecycle diagnostics.
- Narrow source-supported proof code.

Do not:

- Enable multiplayer ownership.
- Spawn replacement dogs automatically.
- Implement training.
- Implement veterinary systems.
- Implement offline self-care AI.
- Implement pack behavior.
- Implement dog models or animations.
- Implement puppy growth.
- Deploy to production.

## 11. REQUIRED DELIVERABLES

Produce:

1. `AUTHENTICATED_PRINCIPAL_PROOF.md`
2. `NATIVE_MANAGED_LIFECYCLE_PROOF.md`
3. `SERVER_MOVEMENT_INTERACTION_PROOF.md`
4. `PRIVATE_DATABASE_DURABILITY_PROOF.md`
5. `NATIVE_OVERRIDE_DRIFT_REPORT.md`
6. `DATABASE_AUTHORITY_BLOCKER_MATRIX.md`
7. `DISPOSABLE_RUNTIME_VALIDATION_PLAN.md`
8. `DATABASE_AUTHORITY_GO_NO_GO.md`

Update the implementation plan and validation records without rewriting historical evidence.

## 12. ACCEPTANCE GATES

| Gate | Required result |
|---|---|
| D1 | Authenticated player identity proven |
| D2 | Safe native managed-animal lifecycle proven |
| D3 | One authoritative movement producer proven |
| D4 | Server-observed physical interactions proven |
| D5 | Private database transaction contract proven |
| D6 | Crash and rollback behavior characterized |
| D7 | Singleplayer runtime validation |
| D8 | Two-client dedicated multiplayer validation |

Each gate must be classified:

- VERIFIED
- FEASIBLE
- EXPERIMENTAL
- BLOCKED
- NOT TESTED

Do not classify a gate as runtime PASS based on offline tests.

## 13. GO / NO-GO DECISION

At completion, provide one of:

**GO:** All mandatory authority boundaries and runtime acceptance requirements have been demonstrated.

**CONDITIONAL GO:** A restricted lifecycle has been proven and its limitations are explicitly documented. Do not enable it without user approval.

**NO-GO:** Required Lua-only authority or lifecycle guarantees cannot be established.

A design proposal or increasing offline test count does not justify GO.

## 14. REPOSITORY AND VERSIONING

- Preserve the current canonical version unless a justified implementation version is authorized.
- Preserve existing uncommitted changes.
- Do not rewrite historical reports.
- Do not modify installed native classes.
- Do not introduce Java or external database dependencies.
- Do not deploy to live servers.
- Do not publish to Workshop.
- Do not merge PR #1 without approval.
- Follow existing CI, version, and public-push validation requirements.

## 15. IMMEDIATE EXECUTION ORDER

1. Read the current architecture and NO-GO reports.
2. Verify repository, version, and modified native environment.
3. Investigate authenticated server principal extraction.
4. Investigate native lifecycle exclusion/reconciliation.
5. Investigate movement and physical interaction receipts.
6. Investigate private database durability.
7. Implement only source-justified, bounded proofs.
8. Prepare disposable singleplayer and dedicated-server procedures.
9. Produce the eight reports.
10. Issue a defensible GO, CONDITIONAL GO, or NO-GO decision.

Do not continue indefinitely if the necessary native authority interface does not exist.

---

# FINAL DIRECTIVE

B47ANCE'd Dogmeat is a standalone canine simulation with database-authoritative logical identities and native physical animal representations.

Natural bonding establishes ownership. Secondary bonds support multiplayer caretakers and trainers. Offline Self-Care is the default server policy.

The immediate engineering objective is to prove that these systems can operate without duplicating dogs, exposing private data, or trusting client-controlled ownership claims.

**Preserve the existing NO-GO until new evidence actually resolves it.**