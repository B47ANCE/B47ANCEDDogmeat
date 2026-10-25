# Database authority proof decision and validation

Project Version: 0.2.0-dev.11

**NO-GO.** Secure automatic persistent multiplayer dogs cannot yet be enabled under the required Lua-only authority/lifecycle guarantees. The new audit confirms a connection-scoped command player and useful native action candidates, but does not establish a lossless server principal, authentic lifecycle/reconciliation, exclusive task producer or durable native/private commit. Existing Option A NO-GO remains effective. Neither GO nor CONDITIONAL GO is justified by the test-only transaction experiment.

This is a scoped conclusion about inspected Build 42.21 / Steam 25485521 and the required contracts, not a universal impossibility claim about all future vanilla Lua APIs. Do not continue adding speculative admission guards or marker checks. Reopen live work only for a concrete sufficient vanilla capability or an explicitly accepted different lifecycle contract, then actual runtime evidence. Missing origin/durable lifecycle semantics are specified in [the earlier decision](OWNERSHIP_GO_NO_GO_DECISION.md); they are not authorization for Java patches.

## Scope and provenance

Latest supplied [proof request](requirements/DATABASE_AUTHORITY_NATIVE_LIFECYCLE_REQUEST.md) narrows the preceding offline store/bond/lease continuation to foundational investigation and bounded proofs. It expressly forbids bonding gameplay and live permissions in this task. All 21 production Lua files, runtime metadata/options, raccoon registration, schema 1, deferred art/model and the existing dirty user AGENTS.md are preserved. The store experiment lives only in tests/ and cannot be assembled by the production inventory.

Read references: the handoff's `DATABASE_AUTHORITATIVE_CANINE_DESIGN.md` resolves to the actual [DATABASE_AUTHORITY_DESIGN.md](DATABASE_AUTHORITY_DESIGN.md); all seven design companions, prior ownership NO-GO, source trace and seam assessment were inspected. No absent filename/content was assumed. Earlier reports/hashes remain their original observations. Current entries in README, implementation plan, validation and changelog link this revision.

Starting branch `docs/m0r-contracts`, HEAD/upstream `56a391c1ca2073e1d4db40f851b7b23e01241ba9`, upstream 0 ahead/0 behind; origin/main 17 ahead/0 behind. Freshness REVIEW was explained by only the pre-existing AGENTS.md edit. Origin remains public B47ANCE/B47ANCEDDogmeat. Same unreleased 0.2.0-dev.7 is retained as directed: compatible proof/test/documentation work, no production behavior/save/config/API change; the ongoing development line remains additive MINOR. No stable tag/package, merge or release is authorized.

## Deliverables and evidence

1. [Authenticated principal](AUTHENTICATED_PRINCIPAL_PROOF.md) — connection actor candidate; lossless principal unresolved.
2. [Native lifecycle](NATIVE_MANAGED_LIFECYCLE_PROOF.md) — exclusion/reconciliation and duplicate prevention still blocked.
3. [Movement and interactions](SERVER_MOVEMENT_INTERACTION_PROOF.md) — vanilla path/action candidates, no sole controller or physical receipt proof.
4. [Private-store durability](PRIVATE_DATABASE_DURABILITY_PROOF.md) — tested logical transaction subset, precise crash/rollback limitations.
5. [Native override drift](NATIVE_OVERRIDE_DRIFT_REPORT.md) — five historical failures plus two further package/loose differences; no installed edits.
6. [Blocker matrix](DATABASE_AUTHORITY_BLOCKER_MATRIX.md) — D1–D8 classifications, no runtime PASS.
7. [Disposable runtime plan](DISPOSABLE_RUNTIME_VALIDATION_PLAN.md) — procedures and prerequisites only.
8. This NO-GO decision — no gameplay enablement.

[The new ledger](database-authority-proof-evidence.json) binds 31 inputs (21 packaged classes, seven loose classes, three vanilla Lua files), production Lua fingerprints, request bytes and P01–P10 method/line anchors. Raw class/disassembly/logs stay ignored and no private player data is used. External override provenance/license are unknown; independent clean-room reviewer signoff is pending in draft PR #1. No external code/assets imported.

## Reproducible checks

Run from the repository root; `python` below denotes the verified bundled interpreter, not an assumed PATH installation:

```powershell
$proofPython = 'C:/Users/willi/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe'
$proofGame = 'E:/Program Files (x86)/Steam/steamapps/common/ProjectZomboid'
$proofJavap = 'C:/Users/willi/Desktop/Work/Project Zomboid/Mod Repositories/Last Known Address/build/toolchain/jdk-25.0.4.1+1/bin/javap.exe'
& $proofPython -B scripts/check_versions.py --root . --json
& $proofPython -B scripts/validate_database_design.py
& $proofPython -B scripts/validate_database_authority_proof.py
& $proofPython -B scripts/validate_m0r.py
& $proofPython -B scripts/validate_foundation.py
& $proofPython -B scripts/test_domain.py
& $proofPython -B scripts/build_loadable.py --check
& $proofPython -B scripts/collect_database_authority_proof.py --game-root $proofGame --javap $proofJavap --scratch .m0r-local/database-authority-proof --output .m0r-local/database-authority-proof/recheck.json
& $proofPython -B scripts/validate_database_authority_proof.py --native --game-root $proofGame
& $proofPython -B scripts/validate_m0r.py --native --game-root $proofGame
& $proofPython -B scripts/validate_foundation.py --native --game-root $proofGame
& $proofPython -B scripts/audit_public_push.py
git diff --cached --check
```

Results: versions, design/proof structure, non-native contracts/foundation, 406 Windows offline Lua cases (31 added), 112-file disposable source assembly and public-push audit PASS. Native checks **FAIL** on the retained historical loose overrides. New proof input fingerprints match, but its native check deliberately reports the untrusted drift baseline as BLOCKED. A matching observation hash is not pristine runtime. Existing historical manifests are not refreshed. Source assembly is a disposable parity check, no archive/deploy. Public CI has no game installation and proves offline scope only.

G6 **NOT TESTED**; G7 **BLOCKED / NOT TESTED**; stable-release G8 **BLOCKED**. SelfCare remains approved design default; StoreOffline disabled; handler leases remain session-only design authority; natural bonds remain offline rules/fixtures. No game/server launch, live deployment, Workshop upload, new gameplay option/controller/permission, automatic respawn, training, veterinary system, pack, growth, model/animation or PR #1 merge.
