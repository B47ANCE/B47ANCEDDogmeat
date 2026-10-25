# Disposable root-account binding experiment

Project Version: 0.2.0-dev.12

This is an explicit, read-only diagnostic overlay for B47ANCEDDogmeat, excluded from ordinary assembly. It never grants ownership, installs a principal provider, writes a registry, restores a lease, spawns an animal or controls a task. Keep PersistenceTestMode off for this account-only experiment. The raccoon registration and deferred model remain unchanged.

**Runtime status: NOT TESTED.** The installed loose-class drift prevents a clean vanilla result. No server or client was launched. A human must supply an isolated, verified Build 42.21 / Steam 25485521 installation and two independently authenticated disposable clients before the dedicated experiment. Preserve the existing installation and real saves; do not remove overrides or copy account databases as part of staging. Probe visibility in a modified installation does not prove a vanilla API.

A separate installed dedicated server (app 380870 / build 25485538) has the same packaged JAR and 17 matching selected classes without loose overrides at those paths. Its complete launch provenance remains unverified. Use `audit_account_binding.py --dedicated-root '<verified server root>'` to recheck that bounded `java/` layout observation; do not pass the server root to the client-layout `--game-root` check. Clean client sessions and the dedicated runtime experiment are still outstanding.

## Prepare without installing or launching

From repository root, using the project's Python interpreter:

```powershell
python -B scripts/audit_account_binding.py
python -B scripts/audit_account_binding.py --native --game-root '<verified clean game root>'
python -B scripts/stage_account_probe.py --check
python -B scripts/stage_account_probe.py --output '.m0r-local/account-probe-run-01/B47ANCEDDogmeat'
```

The first two commands check source applicability, not runtime cleanliness. Also run the existing native baseline checks in `docs/SERVER_ACCOUNT_IDENTITY_ALTERNATIVE.md`; matching these 17 packaged inputs alone does not pass the installation gate. Explicit staging creates a new ignored tree with the ordinary 112 files plus three probe Lua files (115 total). Existing destinations are refused. There is no ZIP, installed-mod copy or launch step. Ordinary `build_loadable.py` excludes this overlay. Remove the probe only from the eventual disposable test installation after the experiment; source cleanup is not automatic.

## Run only in the isolated test environment

1. Record commit, game build, clean-baseline checks, server account policy and fresh test-world identity in a private run sheet. Use a new account DB and test profile, independently chosen local credentials, distinct accounts A/B and separate client sessions. Never put credentials, actual usernames, IPs, Steam IDs, raw server logs or a native DB in Git.
2. Install the explicitly staged tree only into the isolated test setup. Enable the approved Mod ID B47ANCEDDogmeat on that server and both clients. Start the server/clients only under the separately scoped disposable test operation. Require the fixed probe installation line on the server; missing initialization is a failed/incomplete test, not a negative account result.
3. In the test client's Lua console, call `B47AccountBindingSample('AC01', 0)`. Use the scenario label below and the actual local slot index 0–3. The helper sends nothing automatically. Server dispatch uses its callback actor; supplied account/principal/connection/role fields are ignored.
4. Record only the fixed `[B47AccountBindingProbe]` diagnostic line and manual scenario outcome. The server checks its current online-ID map against the exact actor, then tries visible GameServer, ChatUtility and player-owner routes. A non-nil candidate must contain the exact actor in the actor's current slot and return a nonempty no-argument root name. Output retains only codes and equality booleans; no account labels, IDs, native pointers or exception messages.
5. A process emits at most 64 samples. Duplicate bootstrap loading installs once. Restart resets the diagnostic count; it is not a principal/session identifier. A client can consume this disposable budget, so missing output after exhaustion is inconclusive. Keep this overlay out of production.

| Case | Operator action | Required observation / remaining proof |
| --- | --- | --- |
| AC01 | Correct login, then wrong credentials in a separate attempt | Correct actor produces a sample. Rejected login produces no actor; confirm the actual vanilla rejection privately. The probe cannot prove a rejection from absent output |
| AC02 | A/B each sample; repeat a manual send with forged username/root/principalId/role fields | Current callback actor stays connection-scoped; forged arguments do not change diagnostic routes or enter output. Do not send secrets as test arguments |
| AC03 | Disconnect and reconnect A; sample again | Fresh current actor passes the reference check. No prior pointer, principal or lease is restored; same-account continuity remains unproved |
| AC04 | Kill/replace a disposable character and sample | New actor is current; no old actor association. Root-account linkage needs an actually available candidate |
| AC05 | Add a supported co-op slot with a different alias and sample its real local index | Report root/actor equality separately from exact connection-slot membership. Alias equality is never authentication |
| AC06 | In a separate test profile set AllowCoop=false, then exercise supported slot-zero replacement | Record actual native acceptance/rejection and new actor routes. Do not infer native packet closure from this Lua probe or modify production policy |
| AC07 | Test allowed case variants/Unicode under the chosen disposable server policy | Record native acceptance and association observations; do not auto-normalize or merge names |
| AC08 | Rename a disposable native account using supported admin tooling, reconnect and sample | Record both native operation and fresh routes. No automatic alias/principal migration exists |
| AC09 | Delete/recreate a disposable native account with the same text and sample | Probe must remain UNPROVEN. Equal names cannot prove the same account incarnation or transfer dogs |
| AC10 | Exercise a reviewed disposable password/auth-policy reset | Vanilla owns credentials; never log/copy them. A root name alone cannot attest reset/revocation policy |
| AC11 | Gracefully restart the isolated server with its own retained test world/account DB; reconnect both clients | Require a new installation line and fresh samples. No mod identity state is written; this cannot prove persistent principal recovery or rollback detection |
| AC12 | Exercise missing/stale actor and missing/conflicting realm/roster conditions | Offline stale-actor refusal is covered. No realm/roster provider is implemented: those native-account persistence cases remain BLOCKED, not simulated PASS |

`API_ABSENT`, `NO_CONNECTION`, `SLOT_MISMATCH` and error codes are negative observations. `OBSERVED_UNPROVEN` means an association was readable in that environment only. It never means authenticated account/incarnation, universal coverage, restart continuity or a GO decision. Unanticipated visibility requires an exact exposure/provenance audit before use. Wrong-credential, replacement and lifecycle claims need native evidence beyond this probe. Ordinary-client reachability/adversarial packet closure remain separate gates; the helper sends only ordinary Lua commands.

If no root-account route becomes available, stop automatic provider implementation. The Lua-only alternative is an explicitly accepted operator-mediated enrollment and lifecycle process, potentially with per-session approval. That changes the trust/automation contract and is not implemented here. Do not add reflection, parse logs for identity, open native SQL, infer account ownership from aliases or revive rounded Steam IDs.

## Validation scope

`scripts/test_domain.py` runs 25 synthetic Lua probe cases plus the existing 406 cases: 431 offline cases. It checks real probe/entry-point code, stale/reference/slot refusal, forged arguments, redacted errors/logs, duplicate bootstrap and bounded requests. Python/Lupa Lua 5.1 is not PZ/Kahlua or a server. Source parity and offline passes do not execute the twelve native scenarios above. G6 NOT TESTED; G7 BLOCKED / NOT TESTED; stable G8 BLOCKED.
