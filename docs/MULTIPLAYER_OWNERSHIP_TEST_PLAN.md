# Native continuity operator test plan

Project Version: 0.2.0-dev.8

Status: **NOT EXECUTED.** No PZ/client/server was launched or deployed for this audit. Current build is for negative/refusal diagnostics; it cannot pass positive multiplayer ownership acceptance. These instructions are a plan for separately authorized disposable testing, not authorization to change a live server or install/launch now.

## Preconditions and evidence sheet

Use a new empty disposable save and isolated cache/profile; never a real player save. Operator supplies the actual supported pristine Build 42.21 client and dedicated installation/launcher baseline, with no required injected classes/agent/custom JAR. Current local loose-class/launcher drift blocks a claim of pristine runtime. Record exact game/JAR/launcher/class hashes and enabled mod list. Do not fix the installation as part of this test plan.

Build only from an exact committed revision after all offline checks in [BLOCKER_RESOLUTION_REPORT.md](BLOCKER_RESOLUTION_REPORT.md) pass. Deployment, server modification and startup need separate user authorization. For the current default-off diagnostic, explicitly enable server sandbox `B47ANCEDDogmeat.PersistenceTestMode=true` only on that disposable world; record the setting and Mod ID B47ANCEDDogmeat. The diagnostic native type is b47dogtest, breed grey, raccoon presentation. Do not disable guard checks, edit installed classes or attach an ownership-enabling harness.

For each case record: case ID, exact commit/version, build/hashes, SP or dedicated/OS, operator/time, server settings, authenticated actor roles, pre/post saved dog UUID and counts, native representation/marker observation, expected/actual refusal, private revision/checkpoint, number of actionable bodies, errors, paired backup identifiers and result. Keep raw logs/player names/private store contents local. Redacted results may be shared; never commit real logs, world saves or credentials.

Discover the exact per-world receipt/locator/slot paths using [NATIVE_BOOTSTRAP_TEST.md](NATIVE_BOOTSTRAP_TEST.md) and the current PZCache/NativeProvision source; record them before destructive fixture tests. With the test process stopped, back up **both** native world files and all its corresponding private cache files. Hash/label each pair. Restart tests always use the same isolated world/profile/cache pair. Missing/corrupt tests operate on disposable copies; never delete the baseline or auto-initialize a damaged world.

## SP diagnostic sequence

1. SP01: Create NEW world with test mode enabled, living character on a loaded ground-floor tile. Right-click and choose **Dog save/load test...**. Confirm **Initialize this disposable test world?** exactly once. Record carrier/private IDs and WAITING_INITIAL_NATIVE_RELOAD; no message counts as native-save success. If Recovery/Unavailable occurs, preserve evidence and stop provisioning attempts.
2. SP02: Save and quit normally. Close the process, relaunch the same disposable save/cache and use the same menu. Expected after successful paired load: private ID retained; any exact loaded carrier match is diagnostic only; admission ADMIT count is **0**, QUARANTINE may be positive. If native/private recovery fails, it must refuse without creating another body. Record actual result either way; this is not native continuity PASS.
3. SP03: Repeat normal stop/restart twice. Compare private UUID/revision/history hashes and body counts. Repeated inspection cannot create another carrier, alter ownership or prepare a new checkpoint. “Loaded matches” is not authenticated identity.
4. SP04: Move away until operator evidence confirms chunk unload/virtualization, save/quit while away, then return after reload. Record reference/online-ID changes, disappearance/reappearance and catch-up behavior. Missing body must retain private data and cause no respawn. Exact-looking return remains unverified. A distance estimate without unload evidence is NOT TESTED for streaming.
5. SP05: Try ordinary pickup, attach, hutch put/grab, trailer add/remove and generic animal-item drop where the vanilla UI offers them. Current managed transitions must not execute or gain ownership. Lack of a UI option is only reachability evidence, not a successful server refusal test. Repeat equivalent actions with unmanaged vanilla animals; record expected vanilla outcomes and errors. Do not force an unavailable managed route by bypassing guards.

## Dedicated and two-client sequence

1. MP01: Start the separately authorized NEW dedicated world. Join client A as authenticated admin and client B as ordinary player using separate accounts. Confirm server-only diagnostic authorization: B has no usable Initialize/Inspect response; A can provision once through the existing menu. Record server files/counters before/after both requests.
2. MP02: A provisions the raccoon, both observe native synchronization, then save and stop normally. Restart dedicated server; A and B rejoin. Record recovered private UUID, loaded diagnostic counts, server errors and synchronized body observations. ADMIT must remain 0; neither actor receives companion authority. A visual raccoon on both clients is synchronization evidence only.
3. MP03: Disconnect/reconnect B, then A; reconnect in reverse order and inspect. Repeat Inspect rapidly and from both actors. Expected: ordinary requests denied/silent, throttle/busy behavior bounded, no duplicate provisioning, no ownership change, no extra private writes. Single Lua VM reentry tests are not a substitute for this scheduling/network test.
4. MP04: Repeat MP02 with server restart while both clients are away and after confirmed chunk virtualization. Record native unload/save/load order; verify no auto-respawn or ID allocation when body unavailable. Do not infer state ownership from vanilla simulator ownership handoff.
5. MP05: Attempt managed carry/trailer/hutch/attachment using legitimate client actions; confirm refusal on server and no private mutation. Exercise vanilla unmanaged controls on the same server. Managed **positive** carry/release, trailer reconstruction and vehicle restore tests are BLOCKED until that transition has a proved supported implementation; current refusal is not positive continuity PASS.
6. MP06: Ordinary-client protocol tests submit unsupported command names, replayed/expired ProvisionConfirm, malformed intent and unauthorized Inspect using a reviewed, operator-owned diagnostic client harness on this disposable world. Use the exact existing service payload schema, never client-built trusted context. The production client UI does not provide a raw packet injector; if a harness is absent, record this case BLOCKED rather than pretending menu clicks test it. Expected: silent/refused unauthorized operations, no record disclosure, allocation or writes.

## Adversarial identity and recovery fixtures

Every fixture below starts from a separate stopped copy of the known baseline pair. Record what the operator changed and restore that copy after the case. Never run these against a live/shared gameplay world.

| Case | Procedure | Expected current behavior / evidence limits |
| --- | --- | --- |
| ID01 Forged/foreign marker | Reviewed bounded test harness changes only the disposable carrier marker using the actual verified ModData API; record old/new marker and source actor | Invalid/foreign identity cannot authorize, no invented private ID. Admin mutation is not proof ordinary-client packet reachability |
| ID02 Exact copy, both orders | Operator harness creates a second test representation and copies the entire public marker; census copy-before-original and original-before-copy, saving a separate fixture for each | No winner or ADMIT; conflict rejected, private history unchanged. Constructor via admin harness tests ambiguity, not a client exploit |
| ID03 Saved copy/restart | Stop/save the ID02 fixture with only the copy observable; restart with intact guards | Public equality must not become authority. Current policy Q. Native admission prevention still BLOCKED |
| ID04 Client marker attack | Review vanilla ObjectModData packet direction/authentication, then use an operator-controlled non-admin client test harness limited to the disposable target; retain redacted server receipt evidence | Must not grant private ownership. Without a reviewed harness and actual server receipt, label NOT TESTED; server-side admin simulation does not satisfy this case |
| RC01 Missing private slot/locator | With process stopped, move ONE disposable fixture file to a retained backup, then reload | Recovery/refusal, no automatic Initialize/replacement; preserve remaining bytes |
| RC02 Corrupt/truncated slot | Edit a COPY of one slot to truncated/invalid bytes, keeping original retained; reload | Refuse ambiguous/corrupt data. Never silently choose highest sequence or delete it |
| RC03 One-sided rollback | Combine old native world with newer private files, then inverse, on separate copies | Mismatch/refusal without automatic repair; compare exact checkpoints |
| RC04 Paired rollback | Restore a complete internally consistent older native/private pair | Old private record may recover; physical authority still refused. Explicitly record that freshness is **not detected** |
| RC05 Interrupted save | Only with separate operator approval, interrupt a disposable process at reviewed private/native save boundaries; retain pre/post pairs and errors | Recovery or refusal without duplication/data destruction. If timing not demonstrated, do not claim boundary coverage; offline truncated-file test is different |
| LC01 Death | Let test carrier die through ordinary supported native behavior in isolated fixture; inspect/save/restart | Never authorize corpse/reanimated representation or auto-respawn; private record retained. Durable terminal correctness remains BLOCKED |
| LC02 Item/trailer/hutch existing-state restore | Only a reviewed fixture built without changing production guards; record native item/list content and subsequent load/release | No authorization even if native bypass creates a body. Requires separately reviewed fixture tooling; ordinary route refusal alone does not cover deserialization |
| LC03 Growth replacement | Source audit and offline replacement simulation only for current build | Native positive growth test BLOCKED: no supported growth feature/seam. Do not add stages or doghouse gameplay to make it run |

The exact harness and fixture revision must be recorded and reviewed before use; this plan does not invent a Lua event, console command or shipped packet tool. Source-supported methods do not by themselves authorize a live mutation. Private owner/history values in offline tests are synthetic. Real player data stays local.

## Acceptance and stop rules

Current negative suite succeeds only if no request/marker creates private authority, no ambiguous recovery spawns/deletes a dog, vanilla controls work and evidence remains intact. Any unexpected write, duplicate actionable body, owner grant, unauthorized data disclosure or guard drift is a failure: stop that fixture, retain paired files/logs and investigate; do not bypass checks to continue.

Positive milestone acceptance additionally needs trusted returning-vs-copy discrimination, previous-session proof, exact canonical identity through **every declared supported** transition, no unrelated vanilla regression, actual SP and dedicated two-client evidence. Attach precise scenarios/commit/environment, not just screenshots. G6 and G7 cannot PASS from this document, offline tests or CI. G7 remains BLOCKED / NOT TESTED and stable G8 BLOCKED.
