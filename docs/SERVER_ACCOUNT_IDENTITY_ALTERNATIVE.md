# Server-authenticated account identity alternative

Project Version: 0.2.0-dev.10

**Server accounts are a feasible identity design candidate, but an automatic account provider is still BLOCKED.** Their names reach Lua as strings and avoid SteamID64 precision loss. A callback player's username is not yet proved to identify the connection's authenticated account on every supported creation/replacement path, and equal names do not prove the same account incarnation after deletion or recreation. No provider is adopted and no ownership/task controller is enabled.

This investigation is explicitly authorized by the 2026-10-15 request to examine server accounts as an alternative. It does not silently replace the earlier SteamID64 contract. It provides a proposed trust model and source-supported restrictions, not a runtime GO or CONDITIONAL GO. Existing native dog lifecycle/save/control blockers remain independent.

## Baseline and scope

Starting branch docs/m0r-contracts, HEAD/upstream `68fb883bc26941adf34f32039d896f5cff34ccb7`; upstream 0 ahead/0 behind, main 19 ahead/0 behind. Only the existing AGENTS.md user edit was dirty; preserved and excluded. Build 42.21 / Steam 25485521 packaged JAR still matches the previous fingerprint. Effective runtime remains UNKNOWN because of the recorded loose overrides. No installed file was changed; no real player save, account database, server profile or credential was opened.

Canonical version stays 0.2.0-dev.7 for compatible research/documentation/offline audit tooling; production behavior, save/config and public API remain unchanged. The ongoing development line is additive MINOR. Adopting another principal provider would require an explicit version/identity-migration decision; this investigation performs none.

[The ledger](native-account-identity-evidence.json) binds 17 packaged classes and vanilla server ClientCommands.lua, ten findings A01–A10, the candidate registry and twelve unexecuted runtime cases. Raw javap output remains ignored. Findings are native/source observations, with inferred risks labelled separately; no class is executed by the inspection tools.

## Source trace: account authentication to Lua

| Step | Established packaged-source observation | Trust implication |
| --- | --- | --- |
| Normal login — A01 | LoginPacket.processServer calls ServerWorldDatabase.authClient at 792. Its authorized branch at 853 proceeds through configured authentication/second-factor handling; connection root username and slot-zero name are assigned at 994/1006 | The vanilla server can authenticate a local account according to its credential policy. The mod must not accept an account, password, role or owner identity from command args |
| Native account policy — A01/A07 | Existing account lookup uses a world-scoped LOWER(username) comparison; password/auth-method/second-factor branches vary. Open enrollment and initial account creation are separate from proving an existing account | An admitted name is not proof of a particular human or external Steam account. An account alternative needs an explicit protected-account/enrollment policy; no universal credential-strength claim is made |
| Normal primary player — A02 | ConnectPacket.parse supplies IConnection.getUserName() to GameServer.receivePlayerConnect. The common method assigns playerIndex, current connection player reference and supplied name to IsoPlayer.username | A normal primary connect has a useful account-to-player source path |
| Command actor — A03 | receiveClientCommand resolves the player from the sending connection slot; -1 selects its first non-null slot. OnClientCommand receives that player, module, command and args | The callback is connection-scoped. It does not separately provide root account name, native account row/incarnation ID or connection proof |
| Lua name read — A04 | getUsername() calls the two-boolean overload with false/false, returning the unformatted username field. Vanilla server ClientCommands.lua uses player:getUsername() | Lossless string access and a source-supported server caller exist. Avoid display name, localized/disguised-name overloads and client-supplied fields |
| Co-op/replacement — A05/A06 | ConnectCoopPacket.parse reads a separate slot name at 137, checks currently connected name collisions, writes the slot array at 372 or 623, then passes it to receivePlayerConnect at 797. No separate authClient call is observed in this method | A server-created player's name can represent a slot alias rather than independently authenticated account credentials. Current username alone is not a proved universal principal |

The co-op path is annotated with LoginOnServer capability and server handling. That is not demonstrated proof that every supplied slot name belongs to the root authenticated account. Packet eligibility, native state checks and actual ordinary-client reachability remain **[RUNTIME GATE]**; this source trace is **not a demonstrated impersonation exploit** or a complete network security audit.

The distinction persists even for slot zero: AllowCoop=false rejects nonzero slots in this method, while zero is allowed; dead-slot replacement reaches its name-handling branch. UdpConnection.getUserName() reads the root field, while getUserName(index)/setUserName(index,name) use a separate array. Therefore `player:getPlayerNum()==0` plus disabling extra co-op players is insufficient proof of root-account identity. No speculative packet wrapper or callback-name heuristic is added.

The earlier [Steam string audit](STEAMID64_SERVER_PATH_AUDIT.md) found no verified Lua player-to-root-connection route through getOwner or the explicit GameServer/UdpConnection bindings. A server account alternative needs the **root account association**, even though it no longer needs a Steam long. The normal path is promising; the supported lifecycle as a whole remains unproved.

## What can persist across reconnect and restart

Native ServerWorldDatabase creates/opens a persistent database under the server's cache database path, scopes account operations by native world/server context, and stores whitelist rows. The normal login path adds missing users or updates credentials after its authentication flow. Retaining that database can support reauthentication after restart. This is source evidence, not a successful restart test or permission to query its SQL connection from Lua.

A **proposed** mod registry would assign an opaque server-generated principal UUID, scoped by a retained accountRealmId. Names and reviewed aliases are lookup attributes, not the permanent identity key. Dog records continue to use `(worldId,dogId)` and reference that private principal, preserving relationships/history independently of current player objects. Same text on another server/realm must never link accounts. Changing server profile, restoring another account DB, cloning a world or losing realm/registry files requires explicit reconciliation, not a fresh empty registry. The roster, principal keys and full aliases/ACLs stay private; public ModData and client projections cannot carry authority or expose the complete registry.

| Event | Required continuity rule |
| --- | --- |
| Reconnect | Recover the same principal only after fresh native account association and current connection membership. New connection/session fence; no old transient pointer or handler lease |
| Server restart | Recover the exact private realm/registry checkpoint; reauthenticate and rebind current actor. Permanent principal survives; session authority does not |
| Character death/replacement | Keep account principal only if account incarnation and root binding remain valid. Create a new character episode, fence old contexts and retain dog history; no dog respawn |
| Case variation | Authentication compares names case-insensitively in the inspected query. Exact-case private keys could split one account. Canonical spelling/alias policy must match verified native semantics; do not assume Lua lower/Unicode normalization is equivalent |
| Rename — A08 | Native changeUsername updates the existing whitelist row by id. Proposed reviewed atomic alias migration can preserve principal while fencing old contexts. No auto-adoption by similar/new spelling |
| Delete/recreate — A08 | Native removeUser deletes the row. A new account using the same name must receive a new principal/incarnation unless an explicit reviewed recovery proves continuity; it cannot inherit dogs by text equality |
| Death removal — A09 | DropOffWhiteListAfterDeath may attempt account removal for eligible non-exempt players. The source passes serverName as the world argument; actual row matching/removal must be verified. Require a lifecycle policy instead of assuming character death never affects accounts |
| Password/auth-mode reset | Vanilla owns credential validation. Retain or revoke principal association according to an audited account-lifecycle decision; never store/copy password, hash, OTP key, token or IP in mod records |
| Uncertain account/registry rollback | Preserve principals, dogs and relationships; refuse association. Restoring account/private records together may defeat freshness detection without an independent trusted reference; no anti-rollback guarantee is invented |

The native whitelist row id is useful evidence that names can be renamed while a row persists. It is not a verified Lua-visible account identifier for the callback. LogonResult exposes authorization/role/second-factor information, but no account UUID/incarnation. NetworkUser remains an admin synchronization record, not an authoritative current-account adapter. Neither a private UUID nor a locally incremented generation detects an unobserved native deletion/recreation. That gap needs a verified lifecycle feed or an explicitly trusted operator process.

The current private store still has its narrow ownership/event schema. The earlier transaction fixture supports logical aggregate feasibility only. This candidate requires a separate reviewed registry schema, receipts, migration, capacity/retention and paired recovery protocol. Native account changes and private registry changes have no proved joint transaction: a partial rename/delete must suspend association pending reconciliation, never fall back to matching a name. Existing offline owner strings and synthetic Alice/Bob fixtures must not be reinterpreted as authenticated accounts. No owner, bond, delegated permission or cosmetic entitlement is transferred by this investigation.

## Candidate trust contract and configuration

1. The server resolves current actor from the vanilla callback; command args are intent only.
2. A verified adapter must associate that exact current player with the connection's authenticated root account, account realm and incarnation evidence. Unknown alias/episode/connection status refuses. An online-player census alone proves presence, not account provenance.
3. A private, explicitly enrolled roster maps that account evidence to one principal UUID. No client-chosen UUID/name and no automatic association solely by matching username. Name reuse preserves the old principal's tombstone/history and starts a separate identity.
4. The coordinator creates a fresh process session, connection membership and character-episode context; requests/leases carry server revisions and fences. Reconnect/restart/permission changes invalidate old authority. Account-presence sets include all verified sessions; one character disconnect is not automatically account offline.
5. Relationships/ownership remain private server state. Neither a readable username nor a principal UUID grants permission without ACL, binding, native lifecycle and operation checks. All current ownership/task refusal stays in place.

Open, AllowCoop, AllowNonAsciiUsername, native authentication modes and DropOffWhiteListAfterDeath are existing server-policy inputs to assess, not mod settings changed here. AllowCoop=false alone cannot close the slot-zero gap. Any future provider choice would be meaningful shared gameplay configuration and require a server-authoritative sandbox setting with explicit existing-save behavior. No option, default change or hidden bypass is registered. Realm UUIDs, schema/revision equality, fences and mandatory refusal are technical invariants, not tunable gameplay controls.

A **Lua-only operator-mediated alternative** could use a private UUID roster with explicit server-operator attestation of each current account association and recorded rename/recreation transitions. It changes the trust/automation contract and may require per-session review; it is not automatic server account authentication. No association UI/command, secret exchange or manual override is implemented or authorized for gameplay here. A native lifecycle feed or stable account-string/row-id getter would reduce that operational burden; no new engine API is invented as an existing method.

## Decision and next proof

| Capability | Investigation result |
| --- | --- |
| Read current player name as an exact Lua string | [VERIFIED — source] Feasible; avoids SteamID64 rounding |
| Normal authenticated primary connection → account label | [VERIFIED — source] Useful normal-path trace; runtime NOT TESTED |
| Every callback player → authenticated root account | BLOCKED; alias/replacement paths need authoritative distinction |
| Preserve a private principal across sessions/restarts | [INFERRED] Feasible logical registry design; no production implementation or native restart proof |
| Detect rename/delete/recreate/incarnation automatically | BLOCKED; no verified Lua lifecycle/immutable-account identifier feed |
| Adopt server accounts for live ownership | NOT ADOPTED / NO-GO for automatic activation under current evidence |

The next sufficient proof is a read-only current callback-player-to-root-account association that survives slot replacement without trusting the slot's chosen label, plus a reviewed native account-incarnation/roster lifecycle protocol. After that, run all twelve AC01–AC12 scenarios in the ledger: correct/wrong credentials, two accounts/forged args, reconnect, death/replacement, co-op alias, slot-zero replacement with AllowCoop=false, case/Unicode, rename, delete/recreate, auth-policy reset, restart/rollback and missing/conflicting realm/roster/actor. Each remains **NOT TESTED**. Use disposable accounts/worlds with redacted evidence; no real account DB or production server changes are authorized by this plan.

Historical SteamID64 D1 remains BLOCKED; a different principal provider must be evaluated explicitly rather than relabelling its old evidence. Native dog identity, one physical controller and native/private durability remain blocked independently. G6 NOT TESTED; G7 BLOCKED / NOT TESTED; stable G8 BLOCKED. The raccoon and all 21 production Lua files, runtime metadata/options, old manifests, models and artwork remain unchanged. No game/server launch, deploy, Workshop publish or PR merge.

## Focused root-account binding follow-up — 2026-10-15

The user's subsequent “do it” authorizes the bounded next proof. Starting HEAD/upstream `a214c2b7af30adfe241168fa575eead709918aa5`, 0 ahead/0 behind; main 20 ahead/0 behind. The existing AGENTS.md edit is preserved. Version stays 0.2.0-dev.7 for compatible test/research tooling; no production/save/config/API change or provider adoption.

[The focused ledger](native-account-binding-evidence.json) records 17 packaged fingerprints, eight findings B01–B08 and 20 direct public connection/server/engine descriptor candidates. This is a bounded descriptor/receiver audit, not a whole-object-graph impossibility proof. It includes IConnection returns, which the earlier Steam-specific descriptor selection did not include; none was found in this direct public selection. No copied game code is distributed.

| Route | Source result | Disposition |
| --- | --- | --- |
| GameServer.getConnectionFromPlayer | Native player-object-to-address map, nil guard, active connection lookup; official [native API reference](https://www.projectzomboid.com/modding/zombie/network/GameServer.html) also lists the method | Promising native capability; no literal explicit Lua exposure or verified Lua receiver established |
| ChatUtility.findConnection(short) | Searches server engine connections by slot player ID | No literal explicit exposure or verified Lua receiver. Name overload matches slot text and does not authenticate a root |
| IsoPlayer inherited getOwner / IsoAnimal | Base getter returns nil; no selected-class override | Cannot supply a player-to-connection binding |
| IsoZombie / NetworkZombieComponent ownership | Simulation owner/owner-player can refer to a connection/player | Separate zombie availability, simulation assignment, exact actor membership and Lua receiver still matter. No scanning, reassignment or ownership inference added |
| getGameClient, its connection/engine, getClientUsername/getOnlineUsername | Client singleton/state; own client engine; client-flag name or local display name | Not the dedicated server's current connection roster |
| getPlayerByOnlineID | Server IDToPlayerMap lookup | Supports current actor-reference checking; does not establish root account/incarnation |
| MP status/statistics | Client-gated status and stored local/remote statistics tables | No verified authenticated-account feed |

LuaManager.Exposer.shouldExpose tests its explicit class set. The inspected literal registrations include IsoPlayer/IsoZombie/IsoAnimal, but not GameServer, GameClient, ChatUtility, UdpConnection or UdpEngine. This registration observation is not an actual Lua invocation, nor proof that every possible indirect exposure is absent. No reflection/exposure bypass, mutable native registry or client-authored identity is used.

The concrete deliverable is a [read-only disposable Lua experiment and AC01–AC12 run sheet](../tests/runtime/account_binding/README.md). Its normal build is excluded from production; explicit staging assembles 115 files (112 ordinary plus three diagnostic scripts). It checks current actor reference, candidate connection membership at the exact slot and raw root/actor equality, while always returning UNPROVEN. It ignores claimed identity/role/connection arguments, redacts identifiers and exception text, installs once and caps diagnostic samples. Even a positive association cannot establish account incarnation, deletion/recreation or paired rollback continuity.

[TESTED — Windows offline Lua 5.1/Lupa 2.6] 25 additional cases exercise the actual probe, server bootstrap and client helper; 431 total cases pass. Ordinary 112-file assembly and explicit 115-file probe assembly pass. Seventeen packaged input hashes and the repeated descriptor collection match. All 21 production Lua sources, runtime metadata/options, prior evidence, raccoon and art remain unchanged. These results do not execute native authentication or AC01–AC12.

**Automatic root-account binding remains BLOCKED.** The known native baseline failures prevent a clean dedicated experiment on the present installation. No server/client was launched and no installed files, native accounts or real saves were changed. A clean isolated installation plus two independent disposable clients is the remaining runtime gate, followed by authenticated account lifecycle/incarnation evidence or an explicitly accepted operator-mediated contract. No runtime/ownership GO follows from this diagnostic. G6 NOT TESTED; G7 BLOCKED / NOT TESTED; stable G8 BLOCKED.

A separate installed dedicated-server application was located read-only: Steam app 380870, build 25485538, `java/projectzomboid.jar` layout. Its complete packaged JAR fingerprint matches the client package, all 17 selected class fingerprints match, and no loose override exists at those 17 paths. This is a useful source-compatible candidate, not an absent server installation or a full pristine/runtime PASS. The selected client baseline still fails; complete dedicated launch/classpath provenance and two clean independent client sessions remain unverified. No startup script, loader, server profile, account DB or third-party implementation was executed or changed.

Additional exact commands from the repository root:

```powershell
& $accountPython -B scripts/audit_account_binding.py --collect --game-root $accountGame --javap $accountJavap --scratch .m0r-local/account-binding-proof --output .m0r-local/account-binding-proof/recheck.json
& $accountPython -B scripts/audit_account_binding.py
& $accountPython -B scripts/audit_account_binding.py --native --game-root $accountGame
& $accountPython -B scripts/audit_account_binding.py --dedicated-root 'E:/Program Files (x86)/Steam/steamapps/common/Project Zomboid Dedicated Server'
& $accountPython -B scripts/stage_account_probe.py --check
```

The variables are defined in the command block below. Explicit staging is available via `--output` under ignored .m0r-local only; no installation, archive or launch occurs.

## Exact validation commands

From the repository root:

```powershell
$accountPython = 'C:/Users/willi/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe'
$accountGame = 'E:/Program Files (x86)/Steam/steamapps/common/ProjectZomboid'
$accountJavap = 'C:/Users/willi/Desktop/Work/Project Zomboid/Mod Repositories/Last Known Address/build/toolchain/jdk-25.0.4.1+1/bin/javap.exe'
& $accountPython -B scripts/check_versions.py --root . --json
& $accountPython -B scripts/audit_server_accounts.py --collect --game-root $accountGame --javap $accountJavap --scratch .m0r-local/account-identity-audit --output .m0r-local/account-identity-audit/recheck.json
& $accountPython -B scripts/audit_server_accounts.py
& $accountPython -B scripts/audit_server_accounts.py --native --game-root $accountGame
& $accountPython -B scripts/validate_m0r.py
& $accountPython -B scripts/validate_foundation.py
& $accountPython -B scripts/test_domain.py
& $accountPython -B scripts/build_loadable.py --check
& $accountPython -B scripts/validate_database_authority_proof.py --native --game-root $accountGame
& $accountPython -B scripts/validate_m0r.py --native --game-root $accountGame
& $accountPython -B scripts/validate_foundation.py --native --game-root $accountGame
& $accountPython -B scripts/audit_public_push.py
git diff --cached --check
```

[TESTED — offline] Source contract/version checks, 18 input fingerprints and repeated source collection match; existing 406 Lua 5.1/Lupa regression cases and 112-file disposable assembly pass. No additional mock authentication tests are treated as proof. API findings are recorded as local library drafts. Native baseline checks retain the previous five loose-override failures and effective-runtime uncertainty; [the earlier drift report](NATIVE_OVERRIDE_DRIFT_REPORT.md) is not rewritten. Source consistency and CI cannot prove account authentication, malicious-client closure or dedicated reconnect/restart behavior.
