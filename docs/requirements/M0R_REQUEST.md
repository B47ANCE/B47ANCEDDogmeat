# CODEX HANDOFF — Milestone 0R: Standalone Architecture Contract Resolution

**Project:** B47ANCE'd Dog Training  
**Current Version:** `0.1.0-dev.1`  
**Target:** Project Zomboid Build 42.21  
**Architecture:** Standalone, Lua-only, dedicated-server-first  
**Status:** Pre-implementation investigation  
**Authority:** This task supplements the standalone master handoff and supersedes obsolete Companion Dogs integration assumptions.

## Objective

Resolve the eight gaps identified in the standalone master handoff review.

Do not reduce the project's approved gameplay scope. Instead, establish the technical contracts, dependency ordering, and acceptance criteria required to implement it safely.

Companion Dogs and DogPack are not dependencies.

Preserve previous reports as historical research.

## 1. Native canine feasibility

Audit the native Build 42 animal system and determine whether an original canine species can be registered and operated without Java modifications.

Investigate:

- Species registration and definitions.
- Original dog model, skeleton, and animation requirements.
- Dedicated-server spawning and simulation.
- Server-authoritative movement.
- Navigation and collision.
- Damage and death.
- Save/load and streaming.
- Pristine versus modified engine behavior.

Select one minimal prototype dog configuration.

Do not create the prototype yet. Produce its exact technical requirements and acceptance tests.

If a requirement cannot be implemented through supported Lua and existing assets, classify it BLOCKED and propose a Lua-compatible alternative without silently reducing the feature's intended behavior.

## 2. Field ownership and task arbitration

Create a field-by-field authority matrix.

Distinguish:

- Native-owned state.
- B47ANCE-owned state.
- Native state read by B47ANCE.
- Derived presentation values.
- Shared operations requiring arbitration.

Define one authoritative writer per mutable field.

Investigate how the mod can safely schedule canine tasks without fighting native animal behavior.

Document interruption, cancellation, resume, and recovery semantics.

## 3. Canonical identity

Design an original persistent dog identity.

Do not assume native `animalId` is globally unique.

Specify:

- ID allocation.
- Native binding carrier.
- Entity-generation tracking.
- Collision handling.
- Duplicate detection.
- Rebinding after load.
- Carrying.
- Growth and maturation.
- Trailer and vehicle transport.
- Death.
- World recovery.

An ambiguous identity must fail safely rather than create a replacement dog.

## 4. Private persistence and backup recovery

Design a world-scoped private persistence system that cannot be read through public ModData requests.

Specify:

- Storage location.
- World identity.
- Schema version.
- Atomic write strategy.
- Backup compatibility.
- Corruption detection.
- Crash recovery.
- Rollback handling.
- Missing-record handling.
- Stale-record quarantine.
- Transaction receipts.

Investigate how world saves and private records can be restored consistently.

Do not assume generation counters alone solve rollback mismatches.

## 5. Correct milestone prerequisites

Rebuild the milestone dependency graph.

Move foundational work ahead of its first consumer.

In particular:

- Handler authorization precedes filtered client projections.
- Identity continuity includes transport before transport-related gameplay.
- Inventory transaction safety precedes cleaning, construction, equipment consumption, and retrieval.
- Task arbitration precedes autonomous needs, training, and working-dog tasks.
- Native collision and navigation proof precedes doggy-door traversal.
- Zombie traversal feasibility precedes promises of crawl-through behavior.

Produce explicit entry and exit criteria for each milestone.

## 6. Sandbox and localization contracts

Create a complete sandbox setting registry.

For every setting specify:

- Stable technical identifier.
- Display name.
- Description.
- Type.
- Default.
- Minimum.
- Maximum.
- Step or allowed values.
- Server authority.
- Change behavior for existing saves.
- Dependencies and conflicts.

Preserve the project's required 29-language localization coverage.

Design localization keys and fallback behavior from the first implementation slice.

Do not defer foundational localization design until release polishing.

## 7. Biology and task interruption

Define physiological simulation rules for:

- Loaded dogs.
- Unloaded dogs.
- Carried dogs.
- Kenneled dogs.
- Transported dogs.
- Offline dogs.
- Dogs in inactive chunks.

Specify how elapsed game time affects hunger, thirst, fatigue, bladder, bowel, stress, and recovery.

Define bounded catch-up calculations.

Establish task priorities for urgent needs, injuries, danger, and handler commands.

Specify behavior when no safe bathroom location exists.

Separate sandbox controls for physiology, housebreaking progression, autonomous bathroom behavior, and physical waste generation.

## 8. Release scope and measurable acceptance

Define a minimum playable release that proves the standalone canine lifecycle without removing later features from the roadmap.

Include:

- Required core features.
- Deferred advanced features.
- Performance budgets.
- Training calibration scenarios.
- Multiplayer tests.
- Save/restart tests.
- Keyboard controls.
- Controller controls.
- Alternatives to hover-only interactions.
- In-game manual requirements.
- Verified doggy-door security behavior.

Do not advertise experimental mechanics as completed features.

## 9. Correct project documentation

Audit the current README and other current project entry points.

Remove instructions that incorrectly describe the mod as a Companion Dogs add-on.

Keep historical reports intact and clearly labeled.

Update the current feature traceability matrix so every approved feature maps to:

- Requirement identifier.
- Technical dependency.
- Planned milestone.
- Feasibility classification.
- Acceptance test.
- Implementation status.

## 10. Required deliverables

Produce:

1. `STANDALONE_CANINE_FEASIBILITY.md`
2. `NATIVE_STATE_OWNERSHIP_MATRIX.md`
3. `CANINE_IDENTITY_CONTRACT.md`
4. `PRIVATE_PERSISTENCE_RECOVERY_CONTRACT.md`
5. `TASK_ARBITRATION_CONTRACT.md`
6. `MILESTONE_DEPENDENCY_GRAPH.md`
7. `SANDBOX_SETTINGS_REGISTRY.md`
8. `LOCALIZATION_CONTRACT.md`
9. `CANINE_BIOLOGY_TIME_MODEL.md`
10. `MINIMUM_PLAYABLE_RELEASE.md`
11. `MULTIPLAYER_ACCEPTANCE_MATRIX.md`
12. `FEATURE_TRACEABILITY_MATRIX.md`
13. `M0R_VALIDATION.md`

Update the README and implementation plan to reflect the standalone architecture.

## 11. Validation and restrictions

- Preserve `0.1.0-dev.1` unless an approved versioning decision requires a change.
- Keep repositories public and free of credentials or sensitive logs.
- Commit and push authorized documentation iterations to GitHub.
- Do not implement Java modifications.
- Do not copy third-party dog-mod implementation code.
- Do not modify installed game files.
- Do not deploy to singleplayer or dedicated servers.
- Do not publish to Steam Workshop.
- Do not claim runtime success from offline inspection.

Classify evidence as VERIFIED, FEASIBLE, EXPERIMENTAL, BLOCKED, or NOT TESTED.

Do not mark G6 or G7 PASS without actual game and dedicated-server evidence.

## Final instruction

Complete Milestone 0R as a documentation and technical-contract task.

Return the exact remaining blockers, their supporting source evidence, and the smallest standalone Lua-only dog prototype that could prove native spawning, identity, server movement, persistence, and multiplayer synchronization.

**Do not begin gameplay implementation until the prototype scope is reviewed and approved.**
