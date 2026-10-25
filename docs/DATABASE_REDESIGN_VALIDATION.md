# Database/relationship/task redesign validation

Project Version: 0.2.0-dev.11

Baseline: `72b542a622e1d519cfb8912a0a4960311f388cb1`, Build 42.21 packaged Core version fields 42/21 and Steam build 25485521. Source/runtime applicability remains limited to exact inspected hashes; actual pristine SP/dedicated evidence is absent. The [source ledger](native-database-redesign-evidence.json) records D01–D07. No actual database, relationship/task controller, migration, runtime sandbox option or new game test is implemented.

## Evidence and invariants

Current results: existing 375 Windows offline Lua 5.1/Lupa 2.6 cases PASS; original guarded diagnostic source unchanged. Structural design validation checks field categories, states, priority order, primary-owner/lease invariants, five setting proposals, localization declarations and all 18 required scenario definitions. **A structurally valid design is not a simulated feature PASS.** Existing tests retain their prior refusal/retention scope; no new test count is used as evidence for live bonding or SQLite.

## Installed native baseline drift

**Native checks FAIL; no historical hashes are replaced.** `validate_m0r.py --native` reports changed loose IsoAnimal.class. `validate_foundation.py --native` reports changed loose GameWindow, IsoWorld, LuaEventManager and GameLoadingState (repeated across overlapping old manifests). The current packaged JAR and all 15 D01–D07 audit inputs still match. Each of the five loose files also differs from its packaged counterpart; actual effective/pristine runtime is UNKNOWN. The source ledger records exact previous/current/package hashes. No game/dependency file is changed by this task.

| Feature / evidence | Previous → current | Risk / required action | Result |
| --- | --- | --- | --- |
| Effective animal identity baseline | Historical loose IsoAnimal hash → different loose bytes | No renewed effective identity/API guarantee; operator supplies a verified pristine baseline before runtime work | FAIL / RUNTIME GATE |
| Save/load/callback ordering | Four historical loose save/load classes → different loose bytes | Packaged trace cannot certify effective overrides; separate compatibility/runtime evidence required | FAIL / RUNTIME GATE |
| Database/principal/enum source audit | Recorded packaged JAR/member hashes → unchanged | D01–D07 remain packaged-source findings only; no exposure/runtime promotion | Packaged inputs MATCH |
| Mod source/schema/diagnostic assembly | src/ unchanged; existing 375-case offline scope retained | No deployed mod migration or native compatibility fix is attempted | Offline checks separate |

The non-native contract/foundation checks, 375 Lua cases, design consistency, version consistency and 112-file assembly pass independently. The native invocation rehashes 44 original inputs and 551 later manifest entries; the failures are reported above, not treated as successful validation. Public CI cannot inspect this machine's loose files.

## Required task/handler dedicated scenarios

| ID | Scenario | Required observation | Current result |
| --- | --- | --- | --- |
| TA01 | Primary owner commands bonded dog | Authenticated permission, verified body, one native intent/lease | BLOCKED / NOT TESTED |
| TA02 | Unauthorized command | No task/movement/private disclosure or state mutation | BLOCKED / NOT TESTED |
| TA03 | Trusted caretaker care | Owner grant + dog acceptance + real resource receipt; no owner change | BLOCKED / NOT TESTED |
| TA04 | Trusted trainer teaches authorized command | Skill/cooperation + real exercise/reinforcement; one XP receipt | BLOCKED / NOT TESTED |
| TA05 | Conflicting handlers | One accepted task/lease/fence; rejected actor gets meaningful refusal | BLOCKED / NOT TESTED |
| TA06 | Owner disconnects during training | Release owner's lease, reconcile repetition/claims, no unearned XP | BLOCKED / NOT TESTED |
| TA07 | Secondary disconnects while leading | Lease promptly fenced/released, no indefinite control | BLOCKED / NOT TESTED |
| TA08 | Autonomous self-care | Physical presence, real supplies, safe native control; no freebies | BLOCKED / NOT TESTED |
| TA09 | Urgent biological work interrupt | Needs interrupt Stay/work safely; no infinite holding | BLOCKED / NOT TESTED |
| TA10 | Danger during bathroom trip | Safety priority, permitted alternative/accident, no teleport | BLOCKED / NOT TESTED |
| TA11 | Owner reconnects with active handler | Preserve current body/location/care; explicit owner preemption only after validation | BLOCKED / NOT TESTED |
| TA12 | Restart during suspended task | No old active lease/pointer; revalidate target/body/claims, no automatic reward | BLOCKED / NOT TESTED |
| TA13 | Two dogs retrieve same item | One shared claim/physical transfer and one receipt | BLOCKED / NOT TESTED |
| TA14 | Pack includes untrained dog | Per-dog capability/refusal; no inherited skills or competing writer | BLOCKED / NOT TESTED |
| TA15 | Native representation unavailable | Fence/suspend/quarantine; retain identity, no replacement spawn | BLOCKED / NOT TESTED |
| TA16 | Duplicate/replayed task request | Idempotent result, no second completion/XP/transfer | BLOCKED / NOT TESTED |
| TA17 | StoreOffline withdraw/restore | Durable coordinated checkpoint, no old body/conflict, one authorized restore | BLOCKED / NOT TESTED |
| TA18 | Private relationship/task restart | Exact retained owner/sub-bonds/history/task intent; old leases invalid | BLOCKED / NOT TESTED |

Also required before implementation: simultaneous 100% first bond owner-CAS; 100% sub-bond no transfer; proximity/feed/pet farming/replay; client forged SteamID/bond/food receipt; split-screen/account presence; unsafe/no-resource self-care with real waste; migration old/new/corrupt/unknown schema; native/private one-sided and paired rollback; death interruption/tombstone; natural-spawn replay; cosmetic-entitlement forgery; revocation/owner preemption mid item commit; all withdrawal/restoration crash boundaries. These remain acceptance definitions, not test results.

## Bounded implementation order

1. Review this proposal and the independent logical schema. Offline aggregate validation/owner-CAS/lease/task-state proposal tests may be implemented as a separate slice without registering gameplay.
2. Prove lossless authenticated server principal extraction and safe native lifecycle/control/resource receipts. A database/native counterpart transaction is still required; absence is not proof. Keep existing NO-GO and do not add speculative live guards.
3. Define exact schema migration/backup/size/retention protocol, configuration bounds and role projections; validate disposable fixture migrations and repeated reloads without actual player saves.
4. Only after boundaries are proved, implement one naturally earned bond and one safe task with the raccoon, then actual SP and headless/two-client dedicated save/restart/reconnect/adversarial tests. Optional StoreOffline/growth/care subsystems each retain separate gates.

For future authorized operator work, use [DISPOSABLE_RUNTIME_TEST_PROCEDURE.md](DISPOSABLE_RUNTIME_TEST_PROCEDURE.md) for exact isolated save/cache setup, paired backups, admin/ordinary clients and negative identity fixtures. The redesigned positive steps need reviewed instrumentation/implementation first; current UI cannot test them. No production/live server, actual player data or forced process interruption is authorized here.

## Commands and gates

```powershell
$designPython = 'C:/Users/willi/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe'
& $designPython -B scripts/check_versions.py --root . --json
& $designPython -B scripts/validate_database_design.py
& $designPython -B scripts/validate_m0r.py --native --game-root 'E:/Program Files (x86)/Steam/steamapps/common/ProjectZomboid'
& $designPython -B scripts/validate_foundation.py --native --game-root 'E:/Program Files (x86)/Steam/steamapps/common/ProjectZomboid'
& $designPython -B scripts/test_domain.py
& $designPython -B scripts/build_loadable.py --check
& $designPython -B scripts/audit_public_push.py
git diff --cached --check
```

G6 NOT TESTED; G7 BLOCKED / NOT TESTED; stable G8 BLOCKED. Public source push/CI is backup/offline evidence only. No deployment, game/server launch, Workshop publication, stable packaging, main merge or model work. Existing user AGENTS.md remains preserved/excluded. Version stays dev.7 for this compatible proposal-only revision; implementation/migration version remains undecided.
