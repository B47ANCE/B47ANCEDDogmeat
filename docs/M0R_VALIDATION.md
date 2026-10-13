# M0R validation and remaining blockers

Project Version: 0.1.0-dev.1

Date: 2026-10-12. Environment: Windows offline documentation/native source inspection. No gameplay prototype/assets implemented, PZ/server launched, deployment, package or Workshop publication. G6 NOT TESTED; G7 BLOCKED / NOT TESTED; G8 BLOCKED.

## Compatibility and evidence

Current/target documentation version remains0.1.0-dev.1: compatible documentation correction/architecture design, no shipped gameplay/save/API/configuration surface changed. Future gameplay/release target requires its own decision. Current mirrors are inventoried; historical results retain their observed versions. Old implementation plan is preserved verbatim before the authorized current-entry update.

[M0R_SOURCE_EVIDENCE.md](M0R_SOURCE_EVIDENCE.md) records exact signatures/lines/bytecode offsets and44 current hashes. Native Lua registry/spawn/model, nonclient updates/synchronization, marker save/load/carry/trailer/corpse and cache-file primitives exist. Larger original canine, task/lifecycle/private durability/physical waste/door capabilities remain unproved. Fresh native growth replacement does not demonstrate marker transfer; broad old ModData-growth assertion stays historical.

## Exact commands

From repository root:

```powershell
$m0rPython = 'C:/Users/willi/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe'
& $m0rPython -B scripts/check_versions.py --root . --json
& $m0rPython -B scripts/validate_m0r.py
& $m0rPython -B scripts/validate_m0r.py --native --game-root 'E:/Program Files (x86)/Steam/steamapps/common/ProjectZomboid' --baseline
& $m0rPython -B scripts/audit_public_push.py
git diff --cached --check
```

Before-edit version check: PASS at0.1.0-dev.1, declared mirrors only; absent packages deferred. Post-edit version consistency: PASS. [TESTED Windows offline] Current structural/native check: STATIC PASS; thirteen required docs,132 IDs/original101 names,79 setting schemas/parents/bounds,303 keys/29-language policy,35 acceptance scenario definitions,11 preserved historical Markdown hashes and44 native input hashes; no errors. Two local managed .agents skill files changed concurrently outside M0R authoring and were preserved; these ignored guidance files are not product source or historical audit reports. All other protected pre-edit files remain unchanged. The validator is read-only and does not execute acceptance scenarios, canine behavior, native Lua logic, medical balance or Linux runtime. Old validate_audit.py was not run because it rewrites historical add-on evidence.

## Gates

| Gate | Current result |
|---|---|
| G0 requirements | Contracts/traceability documented; calibration/release endpoint decisions explicit |
| G1 reconnaissance | Partial source evidence; native/pristine gaps remain |
| G2 design/prototype approval | REVIEW REQUIRED; no code authorization |
| G3 gameplay implementation | NOT STARTED |
| G4 static documentation | STATIC PASS, Windows offline current contract/version/source checks only |
| G5 offline gameplay logic | NOT TESTED; no gameplay code |
| G6 actual client | NOT TESTED |
| G7 dedicated gameplay | BLOCKED / NOT TESTED |
| G8 release | BLOCKED; no artifacts authorized; --release not run |

## Blockers and required Lua-only proof

| Blocker | Evidence | Next proof / alternative proposal |
|---|---|---|
| B-ENV/B-ASSET | E-ENVIRONMENT/REGISTRY/ASSET | Actual pristine client/dedicated baseline, early registry loading, original rig/model/clips/avatar; no required agent/JAR |
| B-TASK | E-NATIVE | Prove exclusive scheduling/native interruption; flags alone compete with native behavior. Native-autonomy/handler-led alternative needs review |
| B-IDENTITY | E-IDENTITY/CARRY/TRAILER/GROWTH/DEATH | Complete carried release/lifecycle observation and marker preservation; growth loses demonstrated marker path. Conditional verified adult/no-growth research representation only |
| B-STORE/B-INVENTORY | E-FILES/PRIVACY | Cache writer lacks proved atomic rename/fsync/error guarantees; matched world/private checkpoints and exact receipts. Paired operator backup/quarantine is limited alternative |
| B-WASTE | E-WORLD | Persistent replicated real urine/feces, valid offscreen/carrier anchors and cleanup; no textual/stat substitute in enabled core |
| B-DOOR/B-ZOMBIE | E-DOOR/ZOMBIE | Selective closed-door native dog/crawler transition missing. Actual-open-door/distinct structure requires scope review and is not a flap |
| B-HEALTH | E-NATIVE/DEATH | One condition/region writer and reviewed canine treatment suitability; no human pharmacology |
| B-SCENT/B-PHYSICS/B-VEHICLE | E-CONTENT/NATIVE/TRAILER/ZOMBIE | Per-target/water/physical-load/projectile/grapple/special-compartment proof; blocked scope retained |
| B-RUNTIME | No operator evidence | SP/host/two-client headless dedicated/Linux/restart/recovery on exact implemented revision |

## Smallest prototype proposal and review stop

[STANDALONE_CANINE_FEASIBILITY.md](STANDALONE_CANINE_FEASIBILITY.md) defines one original medium adult dog with conditional no-growth representation, one controlled server spawn/original ID/private record, authenticated owner-handler-observer, native route observation and two-client native sync. Prove save/unload/reload/reconnect/restart and corrupted/mismatched store refusal. No XP, population automation, doggy doors, treatments or inventory gameplay. Carry/trailer/growth are separate bounded proofs before consumers. Original enabled-state assets and pristine authority are prerequisites. Do not begin code until this scope is reviewed/approved.

## Public repository evidence

Approved destination: [B47ANCE/B47ANCEDDogmeat](https://github.com/B47ANCE/B47ANCEDDogmeat), created and verified PUBLIC. Authentication succeeded for B47ANCE via HTTPS. Documentation review branch: docs/m0r-contracts; commit/push verification pending below. No stable tag/shared-main merge authorized. Audit staged/tracked content before push; exclude raw research/decompiled classes, local authoring/baselines/managed skills, artifacts, credentials and private diagnostics. Public docs backup does not establish runtime readiness.

[TESTED Windows offline] Staged/tracked audit: PASS,48 intended public files, no suspected secret/native/private/generated paths or case collisions. Staged whitespace check PASS; immutable CRLF/hard-break reports are protected by attributes. Public CI runs version/documentation checks on Ubuntu with official checkout v7.0.1 pinned to3d3c42e5aac5ba805825da76410c181273ba90b1. This is offline Python/document validation, not Linux dedicated runtime evidence. Native/source and report hashes remain local/provenance metadata; raw binaries/research are excluded.
