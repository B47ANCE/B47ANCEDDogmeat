# Implementation plan

Project Version: 0.1.0-dev.1

Milestone 0 documentation checkpoint, 2026-10-12. No gameplay implementation is authorized in this task. Proposed technical ID `B47ANCEDDogTraining` remains provisional. No existing project/version was found; the user supplied the initial version. Initial creation is not a PATCH/MINOR/MAJOR upgrade from a released mod. Subsequent additive gameplay is MINOR scope; save/API incompatibilities require explicit classification and migration decisions.

## Deliverables and decisions

The seven requested reports are complete as a source-supported technical foundation:

1. [COMPANION_DOGS_SOURCE_AUDIT.md](COMPANION_DOGS_SOURCE_AUDIT.md)
2. [DOGPACK_COMPATIBILITY_AUDIT.md](DOGPACK_COMPATIBILITY_AUDIT.md)
3. [DRUGS_OF_93_COMPATIBILITY_AUDIT.md](DRUGS_OF_93_COMPATIBILITY_AUDIT.md)
4. [VANILLA_API_AUDIT.md](VANILLA_API_AUDIT.md)
5. [FEATURE_FEASIBILITY_MATRIX.md](FEATURE_FEASIBILITY_MATRIX.md)
6. [SERVER_AUTHORITY_DESIGN.md](SERVER_AUTHORITY_DESIGN.md)
7. This implementation plan.

Companion Dogs/CD add-ons and DogPack are present; DrugsOf93 is present. Exact IDs/versions/paths/hashes are recorded rather than inferred from names. Native current build is 42.21 and has a modified loose animal class; older 42.20.3 evidence remains historical. There is no general ragdoll, canine reanimation, arbitrary compartment truck or complete pre-command policy API established.

Preferred architecture: native CD entities and existing lifecycle, an original server-owned dog domain model, a private persistent store plus filtered per-handler projections, one movement/task writer, narrow version-pinned dependency adapters and independent ISUI. Public breed/callback registration can be reused as interfaces; dependency implementation, balances, text and assets cannot be copied.

## Stop gates before production gameplay

| Gate | Required concrete investigation | Pass criterion | Current status |
|---|---|---|---|
| R1 — private persistence | Server-only cache-file candidate, world/save scope, crash/backup rollback, confidential projections | Hidden data unreachable through native global/animal/player requests; restored record/generation consistent with world | EXPERIMENTAL / NOT TESTED |
| R2 — identity | Native/CD UID through spawn, carry, maturation, stash/trailer/RV, reconnect, transfer, death | One original dog ID, one canonical entity binding; no regeneration/duplication/loss | EXPERIMENTAL / NOT TESTED |
| R3 — command/reward policy | Non-bypassable server seam around managed dog commands and all training rewards | Direct CD/DogPack requests cannot grant unearned skills/actions or bypass physical care checks | BLOCKED until safe seam demonstrated |
| R4 — strict movement | Disable/revoke owner leases; exercise server follow and DogPack formation fallback | Clients submit intent only; consistent server collision/path results and bounded synchronization | EXPERIMENTAL / NOT TESTED |
| R5 — health writer | Map CD veterinary/needs authority, identify narrow extension or agreed exclusive ownership | No competing illness/damage/needs progression; no human anatomical/medical substitution | EXPERIMENTAL / NOT TESTED |
| R6 — inventory/transport | Real item/container/occupancy transaction including retry/crash | Exactly once movement with native identity/capacity/permission checks | EXPERIMENTAL / NOT TESTED |

R1–R4 block affected identity/training gameplay. R5 blocks health changes, not independent read-only health UI. R6 blocks new delivery/transport, not passive observation. Prototype work must be explicitly authorized as a later bounded slice; it is not part of this delivery. Actual client/server launch remains human-operated and separately authorized. No automatic deployment.

## Recommended bounded order

### Next investigation slice: capability and persistence contract

After authorization, establish only dependency detection, handshake, private-store proof and read-only identity resolver in an isolated development source tree. Start without optional DogPack/Drugs adapters, then add DogPack observations. No training XP, new injuries, spawn population changes or entity replacement.

Offline acceptance: deterministic world/store binding; corruption/unknown-schema quarantine; filtered projections; dedup/rate checks; identity alias conflicts; unsupported dependency gating; case-sensitive module references. Dedicated acceptance: save/restart/reconnect/unload/carry/maturation identity continuity; global named-table disclosure attempts; authoritative state without rendering; no duplicate entities. This becomes a concrete reviewable R1/R2 result, not permission to proceed past other blockers.

### Milestone 1: identity, personality and discovered observations

Resolve R1/R2 and command boundaries relevant to observations. Initialize records once, distinguish confidence/disposition/current anxiety, randomize prior histories and support handler-specific discovery. Keep initial observations coarse; no public raw trait tables. Breed predispositions remain subordinate to individual variation. Read existing CD animal age/sex/weight/health rather than creating a second animal model.

Acceptance: no reroll after reconnect/restart; no raw history in packets/ModData; transferring handler access preserves identity; discovering knowledge gives zero XP. Single-dog path first; DP roster read adapter separately tested.

### Milestone 2A: one foundational training exercise

After R3/R4, implement one exercise, preferably recall on a verified server movement path with a conditioned reinforcement action. Add individual cue/proficiency, rolling structured/passive budget and actual observed completion. Do not implement all commands in one patch. Keep CD skills/rewards under an explicit policy so old command paths cannot bypass learning.

Acceptance: actor rights, stale dog, out-of-range, cancelled exercise, repeated packet, missing treat, disconnected handler and already-rewarded action all refuse/resolve safely. No stationary-nearness reward; no wall-walking success. Persist budget over 24 game hours, restart and rollback. Dedicated behavior must PASS before expanding commands.

### Milestone 2B: survivor skill and positive-reinforcement content

Implement verified CustomPerks registration, then books and original training knowledge. Occupations and VHS require their own registration/code spikes. Add clicker conditioning, whistle and treat equipment one at a time, with conflict-aware bindings, radial and clear failure feedback. Tone/vibration cue equipment waits for sensitivity and presentation proof. Calibrate 28–56 game days against ordinary regular practice, not forced unlock timers.

### Milestone 3: health presentation before health replacement

Provide read-only dog health/welfare panel and discovered findings first. Resolve R5 before regional injuries/grooming/rehabilitation affect health. Choose which existing CD conditions remain primary and how new ones interact; do not disable whole-world CD veterinary behavior without an explicit compatibility decision. Canine treatment suitability requires separate reviewed evidence; human/DO93 effect code is insufficient.

### Milestone 4: real working tasks

Start with bounded real-item scent training/search and existing game retrieval primitives after R6. Add optional DrugsOf93 target adapter using verified FullTypes. Then downed-game retrieval/native tracks, foraging indication and ordinary dropped fishing-equipment recovery. True environmental scent propagation and water retrieval stay separate experiments. No synthetic fetch reward may substitute for moving an actual designated item when the task promises retrieval.

### Milestone 5: DogPack and logistics

Use DogPack as sole deployed roster/formation/travel writer when supported. Add private pair relationships and task-specific influence; keep operational leader and social behavior distinct. Group commands validate each member. Real container delivery follows exactly-once transaction proof. Do not expand its current deployment bound or add corpse/shared-load hauling without a separate native/performance contract.

### Milestone 6: optional advanced experiments

Each feature is isolated and off by default: alternate-lore illness (without reanimation initially), zombie attraction/escape, constrained dragging, catch poles or verified kennel vehicles. Native canine reanimation, true ragdoll/shared-load physics and zombie restraint remain blocked until their exact capability gap is resolved. A narrow Java bridge may be investigated only when verified Lua/exposed APIs are inadequate. No armed-explosive transport.

### Milestone 7: integration and release gates

Publish only implemented manual chapters and context help. Complete 29-language key coverage, UI scaling/controller accessibility, dependency/version mismatch handling, Linux path checks, performance and regression testing. Preserve complete player-facing failure reasons and capability diagnostics.

For every gameplay slice: focused offline logic/authority tests, broader relevant regressions, operator client tests, dedicated server with at least two clients, join/reconnect/save/unload scenarios. G6 PASS does not prove G7. Require G7 PASS before G8. Packaging and publication are outside current authorization; never manufacture release work while runtime gates remain unverified.

## Initial exclusions and independent decisions

- Canine scope only; cats/rats remain preserved and unmanaged unless a future extension is requested.
- No new breeds/assets invented to satisfy the spawn examples. French Bulldog is an unfulfilled asset requirement.
- No default dependence on optional DrugsOf93, DogPack or vehicle mods. Missing integration disables its capability and preserves records.
- No client-written XP/medical/identity outcome; no unverifiable UI “success”.
- No broad global monkey patches, constant full-world scans or duplicate animal/cargo/roster simulation.
- No exact medical probabilities, clinical treatment doses or universal physical force formulas invented during audit.
- No existing-save reroll of hidden attributes; no silent discard of unsupported schemas.

## Version discipline

Root VERSION is canonical. Current mirrors are inventoried in `version-inventory.json`; the framework checker is copied unchanged under `scripts/check_versions.py`. Dependency versions, game build, data/API versions and historical user handoff remain separately classified. Future mod.info/code/localization/manual/package mirrors must be explicitly added when they actually exist; no empty mod source is invented now.

Before/after future implementation run `python scripts/check_versions.py --root .`. After authorized packaging and runtime gates, run `--release`; missing packages or mismatch blocks G8. The artifact rule is reserved now, so development checks defer absent packages and release checks cannot falsely pass a documentation-only project.

## Current conclusion

Milestone 0 reports delivered with explicit evidence limits. The intended design is viable in parts, but the complete overhaul is not yet source/runtime-authorized. The next useful work is the bounded R1–R4 contract investigation, followed by a single dog/command slice. Current G6 NOT TESTED; G7 BLOCKED / NOT TESTED; G8 BLOCKED.
