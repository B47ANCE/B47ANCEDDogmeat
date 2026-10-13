# Version inventory

Project Version: 0.1.0-dev.1

Canonical: root `VERSION`. Initial value supplied by the user; new project, no discovered predecessor.
Current M0R mirrors: README, current IMPLEMENTATION_PLAN, VERSIONING, thirteen contracts, M0R_SOURCE_EVIDENCE/HISTORICAL_RESEARCH_INDEX, docs/contracts JSON project_version fields and newest CHANGELOG entry. Exact selectors are in version-inventory.json.
No runtime metadata/code/packages exist. Add their exact mirrors when authorized implementation creates them.

The supplied [VERSION_POLICY.md](VERSION_POLICY.md) is authoritative. Checker provenance:
`C:/Users/willi/Desktop/Repositories/PZ-AI-Development-Framework/project-template/scripts/check_versions.py`.
The local copy must remain unchanged. Framework and dependency versions are independent of this project.

Former reports including VALIDATION and archived implementation plan, user handoff snapshots and earlier CD audit are historical evidence, not current version mirrors. Native build references and upstream versions
are classified by `version-inventory.json`, not synchronized to the Project Version.
Release artifacts are reserved as `dist/current/B47ANCEDDogTraining-<version>.zip`; their absence is deferred
in development and blocks release validation. This does not authorize packaging or finalize the provisional ID.

M0R retains0.1.0-dev.1 as a compatible documentation-only checkpoint with no shipped gameplay/save/API/configuration change. Future gameplay/release target is decided before implementation under VERSION_POLICY.md; additive MINOR scope and incompatible schema/API changes are assessed separately. Proposed store/marker/protocol schema1 is independent design data, not an implemented migration or the Project Version.
