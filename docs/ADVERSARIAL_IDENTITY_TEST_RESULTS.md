# Adversarial identity evidence — Option A

Project Version: 0.2.0-dev.8

[TESTED — Windows offline] Lua 5.1 through Lupa 2.6, disposable real fixture files and separate Lua VMs; **375 PASS, 0 failed**, including the two new evidence-equivalence phases. No native animal serialization, game process, packet, native duplication or dedicated concurrency was executed. Original baseline fda2538 had 373 tests; that earlier result remains historical. Source evidence is separate in [native-save-load-evidence.json](native-save-load-evidence.json).

The new witness passes equal canonical observation/private bytes/anchor into NativeRuntime/NativeSession/NativeAnimal/policy across two fresh VMs. Different mock UID/handles do not authenticate either. Both are QUARANTINE; private record unchanged; no private writes; forged actor ownership preparation refused. The mathematical conclusion is conditional on equal observed evidence; the test does not prove a native client exploit can produce that evidence.

## Requested negative cases and exact evidence location

| Case | Actual tested boundary/fixture | Result and scope |
| --- | --- | --- |
| Exact duplicate representation | save_load_equivalence_spec:honest/:copy; continuity_spec copy-first; identity_authority_spec duplicate observations | PASS refusal for identical mock observation; **actual complete native clone NOT TESTED** |
| Copied identity marker / arrival A/B | continuity_spec copy-first/original-after; existing identity/storage/admission suites | PASS conflict/quarantine, no winner or private allocation; native arrival ordering NOT TESTED |
| Forged marker | continuity_spec forged token, unknown private dog, earlier world; identity_authority_spec | PASS actual Lua runtime/session refusal; native packet NOT TESTED |
| Replayed native integer | continuity_spec integer collision; new equivalence witness equal nativeId | PASS no authority from integer; no native ID writer added |
| Stale checkpoint | continuity_spec previous-session checkpoint mismatch; pairing_spec | PASS recovery/refusal without private mutation |
| Old world/new private; new world/old private | storage_spec exact checkpoint/slot selection; pairing_spec nonmatching native anchor; continuity_spec private-only prepared state | PASS mocked anchor/private-slot mismatch behavior; actual world backup replay NOT TESTED |
| Paired old world/private rollback | continuity_spec coordinated paired backup rollback | Old private snapshot can recover; physical authority Q. **Freshness not detected**; no false rollback-detection PASS |
| Interrupted save / partial write | storage_spec swallow/partial/readback/close fixtures; continuity_spec interrupted private bytes | PASS private refusal/retention; native save interruption/power loss NOT TESTED |
| Missing/corrupt private store | storage_spec missing, malformed, truncated/checksum fixtures; pairing/provision recovery suites | PASS private recovery cannot authorize; no native auto-respawn. Real world/cache restore NOT TESTED |
| Repeat/concurrent requests | continuity_spec repeated calls/reentrant admission/census; provision_spec challenge/replay; admission_spec wrapper reentry/integrity | PASS serial/reentrant Lua tests; **parallel dedicated/client scheduling NOT TESTED** |
| Client claims another player's dog | ownership_spec ACL/owned-claim rejection; continuity broker unauthorized/no Admit endpoint; new witness Mallory prepare | PASS domain/broker/dedicated-runtime refusal; authenticated game actor/packet chain NOT TESTED |
| Inventory reconstruction | admission_spec actual managed completion wrappers; continuity_spec inventory_release route; new equal-state witness | PASS mock refusal; no native item serializer/drop executed |
| Trailer reconstruction | admission_spec add/remove completions; continuity_spec trailer_release and vehicle_load routes | PASS refusal; native trailer/vehicle restore NOT TESTED |
| Growth replacement | continuity_spec simulated replacement marker loss and growth route | PASS refusal; real native maturation NOT TESTED/unsupported |
| Native death/recovery | continuity_spec death/live return; pairing lifecycle; separate-VM prior-session suites | PASS conservative fake death/detachment refusal; durable native terminal transaction/reanimation NOT TESTED |
| Private disclosure / vanilla controls | continuity_spec broker reply excludes owner/history, unauthorized silent; admission_spec unrelated delegation | PASS offline projection/scope controls; real network privacy and vanilla compatibility NOT TESTED |

Existing suites exercise project modules and their boundaries, not only helper outputs. Fixture world/marker/actor/history data is synthetic; native objects are explicit fakes. Source proof of a bypass and mocked refusal are different evidence categories. The requested actual native versions of these cases remain in [the disposable procedure](DISPOSABLE_RUNTIME_TEST_PROCEDURE.md), not marked successful here.

## Exact validation

Run from repository root:

```powershell
$optionAPython = 'C:/Users/willi/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe'
& $optionAPython -B scripts/check_versions.py --root . --json
& $optionAPython -B scripts/validate_m0r.py --native --game-root 'E:/Program Files (x86)/Steam/steamapps/common/ProjectZomboid'
& $optionAPython -B scripts/validate_foundation.py --native --game-root 'E:/Program Files (x86)/Steam/steamapps/common/ProjectZomboid'
& $optionAPython -B scripts/test_domain.py
& $optionAPython -B scripts/build_loadable.py --check
& $optionAPython -B scripts/audit_public_push.py
git diff --cached --check
```

Current source remains 21 Lua files (9 domain/9 native/3 bootstrap), 112 assembled files, 1,044 fallback entries and 30 frozen art files. Version, source/hash, contract/localization, disposable assembly and public checks are offline evidence only. M0R rehashed 44 native inputs; foundation rehashed 536 manifest entries including overlapping historical evidence, with 38 inputs in the new save/load ledger. No broad constructor inventory is rerun. G6 NOT TESTED; G7 BLOCKED / NOT TESTED; stable G8 BLOCKED. Final exact-commit push/CI status is reported separately.
