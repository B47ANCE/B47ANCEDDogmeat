# B47ANCE'd Dog Training

Project Version: 0.2.0-dev.1

Standalone, Lua-only, dedicated-server-first Build42.21 project. M0R contracts remain the technical baseline. An [rebuilt German Shepherd authoring candidate, coat and rig](art/german_shepherd/README.md) exists as gsd-v002 for visual and pipeline review; it has not met the user's realistic visual quality benchmark. The [first feature foundation](docs/FEATURE_FOUNDATION.md) implements offline Lua ownership, naming, handler permissions and private projections. No playable mod, native registration or packages exist. Companion Dogs and DogPack are not dependencies or asset sources.
Provisional technical Mod ID: `B47ANCEDDogTraining`; not registered or packaged.

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

Authoritative current source is README, VERSION, CHANGELOG, version-inventory.json, current docs/contracts JSON, current Markdown contracts and scripts/validate_m0r.py. Original art source is art/german_shepherd/source (editable .blend and original build/validation scripts), with the original texture and intentional review outputs documented in its asset README. Authoritative feature source is src/domain/B47Dog; prepared English fallback strings are src/localization across all 29 languages. Exact files and commands are declared in source-inventory.json. There is no loadable media/Contents/mod.info tree; native integration remains gated. The existing inventory reserves dist/current/B47ANCEDDogTraining-<version>.zip without authorizing packaging or finalizing the ID. The folder/public repository name B47ANCEDDogmeat does not finalize the technical Mod ID. No Workshop ID exists in this scaffold.

research contains immutable local inspection artifacts excluded from public Git; raw game classes/assets/decompiled code must never ship. .m0r-local authoring/baselines and managed .agents guidance are also local-only. Current contracts preserve all101 original IDs and add31 native/core requirements; the79-setting/304-key catalogs remain design data. This slice consumes two configuration policies and prepares 13 UI/eight Sandbox fallback keys across 29 languages; native option/UI loading is not implemented.

From repository root:

```powershell
$m0rPython = 'C:/Users/willi/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe'
& $m0rPython -B scripts/check_versions.py --root . --json
& $m0rPython -B scripts/validate_m0r.py
& $m0rPython -B scripts/validate_foundation.py
& $m0rPython -B scripts/test_domain.py
& $m0rPython -B scripts/validate_m0r.py --native --game-root 'E:/Program Files (x86)/Steam/steamapps/common/ProjectZomboid'
& $m0rPython -B scripts/audit_public_push.py
```

Old validate_audit/collect_evidence commands are historical add-on tools that can overwrite research; they are not current standalone validation. The user authorized feature development on 2026-10-14 and deferred model refinement. The offline domain slice is active; live adapters must satisfy their documented authority and persistence gates. No automatic game/server launch, deployment, packaging or Workshop publication.

Public repository: [B47ANCE/B47ANCEDDogmeat](https://github.com/B47ANCE/B47ANCEDDogmeat). Current contracts use the docs/m0r-contracts review branch. GitHub CI checks version/contracts, source/localization/art integrity and actual Lua 5.1 domain tests on Ubuntu; that is offline validation, not Linux PZ/dedicated proof. Native inspection remains local. Public pushes are audited for sensitive/generated/native files and do not authorize main merge or release.

The user supplied the initial 0.1.0-dev.1 scaffold version. Current 0.2.0-dev.1 starts additive MINOR feature development. The art checkpoint remains tested 0.1.0-dev.2; no model files changed.
Future additive training functionality is MINOR scope; dependency versions, PZ builds and data schemas remain independent.
G6 and G7 are NOT TESTED; G8 is BLOCKED. Domain tests do not validate authenticated game actors, native dog identity, durable saves or multiplayer behavior.

The input handoff is preserved as a historical requirements artifact under `docs/USER_HANDOFF.md`.
Evidence records are immutable snapshots; they do not establish dedicated runtime correctness.
