# B47ANCE'd Dog Training

Project Version: 0.1.0-dev.1

Standalone, Lua-only, dedicated-server-first Build42.21 project. M0R contracts remain the technical baseline. An [original adult German Shepherd blockout, coat and authoring rig](art/german_shepherd/README.md) exists for pipeline review; it does not meet the user's realistic visual quality benchmark. No playable mod, native asset registration, runtime source or packages exist. Companion Dogs and DogPack are not dependencies or asset sources.
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

Authoritative current source is README, VERSION, CHANGELOG, version-inventory.json, current docs/contracts JSON, current Markdown contracts and scripts/validate_m0r.py. Original art source is art/german_shepherd/source (editable .blend and original build/validation scripts), with the original texture and intentional review outputs documented in its asset README. There is no runtime src/Contents/mod.info tree. Future runtime layout must be reviewed before prototype implementation. The existing inventory reserves dist/current/B47ANCEDDogTraining-<version>.zip without authorizing packaging or finalizing the ID. The folder/public repository name B47ANCEDDogmeat does not finalize the technical Mod ID. No Workshop ID exists in this scaffold.

research contains immutable local inspection artifacts excluded from public Git; raw game classes/assets/decompiled code must never ship. .m0r-local authoring/baselines and managed .agents guidance are also local-only. Current contracts preserve all101 original IDs and add31 native/core requirements; the79-setting/303-key catalogs are design data, not runtime implementation.

From repository root:

```powershell
$m0rPython = 'C:/Users/willi/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe'
& $m0rPython -B scripts/check_versions.py --root . --json
& $m0rPython -B scripts/validate_m0r.py
& $m0rPython -B scripts/validate_m0r.py --native --game-root 'E:/Program Files (x86)/Steam/steamapps/common/ProjectZomboid'
& $m0rPython -B scripts/audit_public_push.py
```

Old validate_audit/collect_evidence commands are historical add-on tools that can overwrite research; they are not current standalone validation. Review and approve the bounded Lua-only prototype before gameplay implementation. No automatic game/server launch, deployment, packaging or Workshop publication.

Public repository: [B47ANCE/B47ANCEDDogmeat](https://github.com/B47ANCE/B47ANCEDDogmeat). Current contracts use the docs/m0r-contracts review branch. GitHub CI checks version/documentation on Ubuntu only; that is offline validation, not Linux PZ/dedicated proof. Native inspection remains local. Public pushes are audited for sensitive/generated/native files and do not authorize main merge or release.

Initial project creation, not an upgrade from an existing release. This version is supplied by the user.
Future additive training functionality is MINOR scope; dependency versions, PZ builds and data schemas remain independent.
G6 and G7 are NOT TESTED; G8 is BLOCKED. Do not implement gameplay from this scaffold without resolving the design gates.

The input handoff is preserved as a historical requirements artifact under `docs/USER_HANDOFF.md`.
Evidence records are immutable snapshots; they do not establish dedicated runtime correctness.
