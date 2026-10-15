# B47ANCE'd Dog Training

Project Version: 0.2.0-dev.7

Standalone, Lua-only, dedicated-server-first Build42.21 project. M0R contracts remain the technical baseline. A [rebuilt German Shepherd authoring candidate, coat and rig](art/german_shepherd/README.md) exists as gsd-v002 for visual and pipeline review; it has not met the user's realistic visual quality benchmark. The [first feature foundation](docs/FEATURE_FOUNDATION.md) implements offline Lua ownership, naming, handler permissions and private projections. The [native/private persistence prototype](docs/NATIVE_PERSISTENCE_SLICE.md) adds native observation, private identity matching and inactive-slot save preparation. The [loaded-anchor/lifecycle adapter](docs/NATIVE_PAIRING_LIFECYCLE.md) connects explicit native load/start/death events, exact checkpoint recovery and one pending native anchor. The [loadable persistence diagnostic](docs/NATIVE_BOOTSTRAP_TEST.md) now adds an explicit first-store operation, native raccoon test registration and admin menu. The [multiplayer identity investigation](docs/NATIVE_IDENTITY_AUTHORITY.md) now reports recovered private identity independently of untrusted carrier observations. The [server admission guard](docs/NATIVE_ADMISSION_GUARD.md) now refuses nine selected Lua representation transitions and latches integrity failures. In-game save/load remains NOT TESTED; complete native admission coverage and production multiplayer ownership remain blocked. Companion Dogs and DogPack are not dependencies or asset sources.
User-approved technical Mod ID: `B47ANCEDDogmeat` (2026-10-14). The temporary raccoon carrier is approved for save/load testing; the original model is unchanged.

Start with [the current plan](docs/IMPLEMENTATION_PLAN.md), [M0R validation](docs/M0R_VALIDATION.md), [native evidence](docs/M0R_SOURCE_EVIDENCE.md) and [132 current traceability rows](docs/FEATURE_TRACEABILITY_MATRIX.md). The [historical research index](docs/HISTORICAL_RESEARCH_INDEX.md) labels former add-on records; their bytes and observed evidence remain unchanged.

## Current contracts

1. [Standalone canine feasibility](docs/STANDALONE_CANINE_FEASIBILITY.md)
2. [Field ownership](docs/NATIVE_STATE_OWNERSHIP_MATRIX.md)
3. [Canonical identity](docs/CANINE_IDENTITY_CONTRACT.md)
4. [Private persistence/recovery](docs/PRIVATE_PERSISTENCE_RECOVERY_CONTRACT.md)
5. [Task arbitration](docs/TASK_ARBITRATION_CONTRACT.md)
6. [Milestone prerequisites](docs/MILESTONE_DEPENDENCY_GRAPH.md)
7. [Sandbox settings](docs/SANDBOX_SETTINGS_REGISTRY.md)
8. [Localization](docs/LOCALIZATION_CONTRACT.md)
9. [Biology/game-time](docs/CANINE_BIOLOGY_TIME_MODEL.md)
10. [Minimum playable candidate/full roadmap](docs/MINIMUM_PLAYABLE_RELEASE.md)
11. [Multiplayer acceptance](docs/MULTIPLAYER_ACCEPTANCE_MATRIX.md)
12. [Feature traceability](docs/FEATURE_TRACEABILITY_MATRIX.md)
13. [M0R validation/blockers](docs/M0R_VALIDATION.md)

## Source, generated outputs and validation

Authoritative current source is README, VERSION, CHANGELOG, version-inventory.json, current docs/contracts JSON, current Markdown contracts and scripts/validate_m0r.py. Original art source is art/german_shepherd/source (editable .blend and original build/validation scripts), with the original texture and intentional review outputs documented in its asset README. Authoritative feature source is src/domain/B47Dog and src/native/B47Dog; prepared English fallback strings are src/localization across all 29 languages. Exact files and commands are declared in source-inventory.json. Authoritative bootstrap and metadata sources are src/bootstrap and src/metadata. scripts/build_loadable.py assembles and verifies a new B42 development tree without installation or an archive. The retained .m0r-local/loadable-0.2.0-dev.4/B47ANCEDDogmeat tree is an older diagnostic output; current source assembly is validated in disposable temporary output. No Workshop ID exists.

research contains immutable local inspection artifacts excluded from public Git; raw game classes/assets/decompiled code must never ship. .m0r-local authoring/baselines and managed .agents guidance are also local-only. Current contracts preserve all101 original IDs and add31 native/core requirements; the 79-setting catalog remains future design data. The runtime test mode has one default-off server option, an admin context menu and 36 explicit fallback keys across 29 languages (1,044 entries); source-inventory.json declares the exact runtime subset.

From repository root:

```powershell
$m0rPython = 'C:/Users/willi/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe'
& $m0rPython -B scripts/check_versions.py --root . --json
& $m0rPython -B scripts/validate_m0r.py
& $m0rPython -B scripts/validate_foundation.py
& $m0rPython -B scripts/test_domain.py
& $m0rPython -B scripts/validate_m0r.py --native --game-root 'E:/Program Files (x86)/Steam/steamapps/common/ProjectZomboid'
& $m0rPython -B scripts/validate_foundation.py --native --game-root 'E:/Program Files (x86)/Steam/steamapps/common/ProjectZomboid'
& $m0rPython -B scripts/audit_public_push.py
```

Old validate_audit/collect_evidence commands are historical add-on tools that can overwrite research; they are not current standalone validation. The user authorized feature development on 2026-10-14 and deferred model refinement. The registered raccoon persistence diagnostic is the current test slice; production gameplay remains blocked by native identity authority and persistence gates. No automatic game/server launch, deployment, release archive or Workshop publication.

Public repository: [B47ANCE/B47ANCEDDogmeat](https://github.com/B47ANCE/B47ANCEDDogmeat). Current contracts use the docs/m0r-contracts review branch. GitHub CI checks version/contracts, source/localization/art integrity and actual Lua 5.1 domain tests on Ubuntu; that is offline validation, not Linux PZ/dedicated proof. Native inspection remains local. Public pushes are audited for sensitive/generated/native files and do not authorize main merge or release.

The user supplied the initial 0.1.0-dev.1 scaffold version. Current 0.2.0-dev.7 continues additive MINOR development with server-side completion guards, guarded recovery/provisioning and adversarial admission/restart tests. The prior 0.2.0-dev.6 added approved branding. No storage schema or raccoon registration changes. The art checkpoint remains tested 0.1.0-dev.2; no model files changed.
Future additive training functionality is MINOR scope; dependency versions, PZ builds and data schemas remain independent.
G6 and G7 are NOT TESTED; G8 is BLOCKED. The current 373 offline Lua/file/event tests do not validate authenticated game actors, native dog lifecycle, durable world saves or multiplayer behavior.

The [native continuity audit](docs/BLOCKER_RESOLUTION_REPORT.md) adds a central refusal policy and nine lifecycle/security documents. ADMIT remains unreachable. The 59 direct native constructor sites and worker/deserializer paths show gaps beyond the nine hooks; a fresh process cannot attest prior-session authenticity. Same dev.7 is retained for this unreleased guard revision. [Operator procedures](docs/MULTIPLAYER_OWNERSHIP_TEST_PLAN.md) distinguish current negative tests from blocked positive ownership acceptance.

The input handoff is preserved as a historical requirements artifact under `docs/USER_HANDOFF.md`.
Evidence records are immutable snapshots; they do not establish dedicated runtime correctness.
