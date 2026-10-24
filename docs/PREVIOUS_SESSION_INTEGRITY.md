# Previous-session integrity

Project Version: 0.2.0-dev.9

**BLOCKED.** A clean current-process hook check cannot certify the prior process. A matching restored native marker, private checkpoint and mutable animal integer can all describe a replayed representation. The independent private record remains useful; its association with the returning body is unproved.

## Existing protection and limits

| Mechanism | Established scope | What it cannot prove |
| --- | --- | --- |
| Private world/dog UUID | Server record namespace; foreign-world marker refusal | Which native body owns copied public bytes |
| Private genesis receipt | Written before experimental first spawn; uncertainty stops repeat provisioning | Constructor outcome or all future native admission routes |
| Exact native checkpoint/private slots | One captured loaded anchor selects exact world/checkpoint/sequence; no highest-sequence guess; malformed/ambiguous slots refused | Public native anchor freshness or coordinated world/private rollback |
| Inactive-slot preparation/readback | Bounded bytes, checksum/strict schema, retained baseline, prepared-pending state; interruption can fail closed | Atomic native/private disk transaction, fsync, power-loss durability or final native-save success |
| Lifecycle token/generation | Diagnostic mismatch/duplicate correlation | Replay of the complete signed or unsigned marker together with copied native state |
| Process hook latch | Detects missing/displaced selected hooks before/after project boundaries; no retry | An earlier unobserved import/save/crash or a fresh process with hooks restored |

Source references are [coverage C02–C12/C19](NATIVE_ADMISSION_COVERAGE.md), `GlobalModData`, `ServerMap.QueuedQuit` and StartPause/StopPause packet classes in [the evidence manifest](native-continuity-evidence.json). The private store, checkpoint and receipt code is original Lua; no native code is patched.

## Counterexample that remains open

1. A previous process has unguarded native reconstruction or briefly displaced Lua hooks.
2. A copied carrier with the legitimate public marker enters native state.
3. Native state saves it; the process exits/crashes before the mod records a conflict.
4. The next process has intact hooks, matching private slots and matching native checkpoint.
5. First observation is the copy. First-observation-wins, UUID/token equality and current-process integrity all accept the same public evidence as an honest restart would provide.

The new policy quarantines both histories. Offline separate-VM tests demonstrate loss of the old latch and continued refusal, not a successful detector of this history. A “last clean” bit written after observation leaves the same unobserved interval. A hash/HMAC cannot distinguish replay of authentic bytes.

## Journal/seal candidate — design only

An eventual session journal would have to durably write and read back ARMED before any admission-capable work, record exclusive server lifecycle transactions, and keep crash/dirty/unknown sessions quarantined. A clean seal would require a source-proved boundary after the final relevant native save and after admission is quiescent, with ordering/durability across the private and native files. The next boot must bind that seal to exactly the loaded native generation. Repeated saves, shutdown races and crash before/after each write need explicit recovery states. No such seal is implemented or claimed.

[VERIFIED — packaged source] `ServerMap.QueuedQuit` invokes QueuedSaveAll(true) before teardown. `OnServerStartSaving`/`OnServerFinishSaving` in inspected StartPause/StopPause packet methods are **client process notifications**, not proof of a dedicated final save seal. Other save notifications do not establish exclusive quiescence or durable cross-file commit. PrintWriter close/readback is not fsync proof. The necessary Lua-only seal boundary remains [UNKNOWN].

## Rollback and recovery rules

- Native-only or private-only restore, foreign locator, checkpoint mismatch, malformed/truncated private data and interrupted preparation enter recovery without deleting or selecting the newest slot by sequence.
- Restoring an internally consistent old native/private pair can open the old private snapshot. Without independent retained monotonic evidence it cannot prove freshness. The central policy still quarantines the physical carrier. This is an explicit replay limitation, not a detected rollback PASS.
- A backup consists of the stopped disposable world's native save **and** its exact locator/receipt/private slot files. Keep the pair and provenance together; never repair a live save by copying one side, rewriting a marker or clicking Initialize again.
- Server operator/private files/installed server code are trusted. Malicious-host tampering is outside the ordinary-client threat model. Client-writable native fields are not elevated because the server subsequently persisted them.
- Operator reconciliation of retained logical identity with a physical animal is a possible separate Lua-only workflow, but changes automatic same-native-dog semantics. It requires explicit design/scope approval; it is not an implemented recovery shortcut.

[RUNTIME GATE] Clean stop/restart, process failure, partial backup restore, full paired rollback and two-client replay must be tested on exact pristine client/dedicated builds after the required native provenance seam exists. Current build tests only refusal and evidence retention; G6 NOT TESTED, G7 BLOCKED / NOT TESTED, G8 BLOCKED.
