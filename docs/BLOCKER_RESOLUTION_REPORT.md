# Multiplayer ownership blocker report

Project Version: 0.2.0-dev.9

Latest database-authoritative proposal is documented in [DATABASE_AUTHORITY_DESIGN.md](DATABASE_AUTHORITY_DESIGN.md) and [DATABASE_REDESIGN_VALIDATION.md](DATABASE_REDESIGN_VALIDATION.md). Native Option A NO-GO is retained. No database/lease/controller gameplay has been enabled; prior report evidence below retains its exact scope.

Option A follow-up at baseline `fda2538e64624babbd1606b4e53a0935d80c02f9`: [OWNERSHIP_GO_NO_GO_DECISION.md](OWNERSHIP_GO_NO_GO_DECISION.md) is the current architectural decision (NO-GO), with 375 offline cases and no production runtime change. The report below retains its prior 373-test validation scope and earlier source baseline verbatim. No prior evidence is upgraded.

Audit date: 2026-10-14. Implementation/source baseline: `6518be2aa7afaa71d70e3ff4b28b68dc01e21a63`, branch docs/m0r-contracts, [draft PR #1](https://github.com/B47ANCE/B47ANCEDDogmeat/pull/1). **The technical milestone is not resolved. Multiplayer ownership remains disabled.** Native physical continuity and previous-session authenticity are not proved; larger offline coverage does not change that conclusion.

This revises the existing unreleased dev.7 guard slice at the user's direction, without inventing a version. It remains compatible additive MINOR development scope; private/marker schemas stay 1, no deployed save migration, no model/registration changes. Prior dev.7 evidence at 6518be2 remains a historical checkpoint, not this revision's test result.

## Delivered investigation and bounded changes

The nine requested documents are [coverage](NATIVE_ADMISSION_COVERAGE.md), [canonical identity](CANONICAL_IDENTITY_CONTRACT.md), [previous-session integrity](PREVIOUS_SESSION_INTEGRITY.md), [central guard](SERVER_ADMISSION_GUARD.md), [Lua feasibility](LUA_ONLY_FEASIBILITY.md), [lifecycle matrix](ANIMAL_LIFECYCLE_MATRIX.md), [growth feasibility](GROWTH_IDENTITY_FEASIBILITY.md), [operator test plan](MULTIPLAYER_OWNERSHIP_TEST_PLAN.md) and this report.

Source inspection inventories 59 direct IsoAnimal construction instructions across 136 candidate packaged classes, including generic factory restore, worker return, item/corpse construction, native drops, vehicle/hutch load, growth, births and randomized world origins. [Metadata index](native-construction-index.json) and [hash manifest](native-continuity-evidence.json) preserve reproducible evidence, not engine source. Client-only constructors are distinguished from server ingress; constructor search is not a complete call graph.

The central original Lua policy now serves selected transition scope checks, runtime admission requests, census and dedicated ownership preparation. Explicit Q/REJECT/DEFER decisions preserve private records; ADMIT cannot be emitted. Authority, route, checkpoint and hook checks surround assessment; reentry is refused. Admin Inspect reports counts without exposing private ownership/history. All 29 language sources include the new explicit English fallback. No public Admit/ownership endpoint or persisted certificate is added.

## Resolution ledger

| Obligation | Result | Evidence / remaining condition |
| --- | --- | --- |
| Correctly scope nine guards | [VERIFIED] selected Lua actions only | Native internal calls/deserializers/worker/growth bypass them |
| Central explicit policy | [TESTED — offline] refusal boundary implemented | No ADMIT; no claim every native path dispatches it |
| Client marker cannot independently authorize | [TESTED — offline] dedicated refusal maintained | Real packet/security behavior NOT TESTED |
| Preserve private canonical identity/history | [TESTED — offline] retained on all new refusal fixtures | Native physical binding still unproved |
| Genuine saved body versus exact copy | BLOCKED | Both histories can present same public persisted evidence |
| Previous-session integrity | BLOCKED | No verified exclusive native admission cut/final durable session seal |
| Save/stream/reconnect continuity | BLOCKED / NOT TESTED | No runtime SP/dedicated evidence or authenticated native provenance |
| Carry/trailer/vehicle/hutch | Unsupported for managed dog authority | Ordinary guarded actions refused; native restore remains uncovered |
| Growth and doghouse | Research complete for inspected method; gameplay BLOCKED | Native replaces body without demonstrated ModData/private transaction; future design preserved |
| Death/recovery | BLOCKED | No durable terminal transaction or authenticated rebind |
| Unmanaged vanilla behavior | [TESTED — offline] delegation/scope controls | Actual compatibility requires SP/dedicated controls |
| Lua-only runtime | [VERIFIED] source inventory | No custom Java/JAR/agent or dependency modification |
| G6 / G7 / G8 | NOT TESTED / BLOCKED / BLOCKED | Exact runtime/operator evidence still required |

## Validation commands and environment

Windows offline, bundled Python, Lupa 2.6 Lua 5.1; native inputs inspected/rehashed, never loaded as game code. Run from repository root:

```powershell
$continuityPython = 'C:/Users/willi/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe'
& $continuityPython -B scripts/check_versions.py --root . --json
& $continuityPython -B scripts/validate_m0r.py --native --game-root 'E:/Program Files (x86)/Steam/steamapps/common/ProjectZomboid'
& $continuityPython -B scripts/validate_foundation.py --native --game-root 'E:/Program Files (x86)/Steam/steamapps/common/ProjectZomboid'
& $continuityPython -B scripts/test_domain.py
& $continuityPython -B scripts/build_loadable.py --check
& $continuityPython -B scripts/audit_public_push.py
git diff --cached --check
```

Constructor metadata reproduction additionally uses `scripts/audit_native_construction.py --game-root <verified-game-root> --javap <verified-javap-executable> --check docs/native-construction-index.json`. Javap is a read-only inspection tool, not a shipped dependency. No real player saves or logs are opened.

Current offline validation: 373 Lua/file/event cases PASS, 0 failed; all 21 Lua files compile (9 domain, 9 native, 3 bootstrap); 1,044 explicit fallback entries (36 keys × 29 languages); all 30 frozen art hashes unchanged. Assembler verifies 112 files in disposable temporary output without installation or archive creation. M0R contract checks retain 132 feature IDs, 79 future setting schemas and original acceptance meanings. M0R rehashed 44 native inputs; foundation rehashed 498 manifest entries (including overlapping historical scopes), of which the current continuity manifest has 247 unique inputs. The independent constructor inventory reproduction matched all 136 candidate class hashes and 59 direct NEW sites. These are source checks, not runtime acceptance.

The 41 added cases exercise actual runtime/session/file/broker boundaries: copied/forged/foreign/missing IDs, both duplicate arrival orders, native integer replay, stale checkpoint, paired old rollback, partial private preparation/truncation, repeated/reentrant requests, growth/reconstruction simulation, death/streaming, getter-induced drift, unauthorized clients and separate-VM loss of the prior latch. They demonstrate refusal/retention. No actual native growth, packet, world save, restart or concurrent dedicated execution was tested.

## Next smallest safe step and delivery limits

Establish a source-proved exclusive server genesis/admission seam and previous-session binding on a pristine supported runtime; then execute the disposable negative plan and any newly supported positive lifecycle tests. The proposed adult/world-only restriction still leaves native deserialize/worker/restart obligations open. If Lua cannot close them, present the explicit operator-reconciliation contract alternative for a scope decision. Do not silently replace the same-legitimate-dog requirement with marker equality or automatic respawn.

Existing uncommitted AGENTS.md is preserved and excluded from this revision's commit. Raccoon, model/artwork and prior reports remain intact. No installed game/dependency changes, game/server launch, local/live deployment, Workshop upload, stable package/tag or shared-main merge is authorized or performed. Public branch backup/CI are verified separately on the final commit; a push is not G6/G7 evidence.
