# Lossless server SteamID64 path audit

Project Version: 0.2.0-dev.10

**D1 remains BLOCKED: no safe lossless Lua-only server actor path was established on the inspected Build 42.21 / Steam 25485521.** Native string-valued Steam IDs exist, including one built from a server connection. The missing link is a verified Lua-accessible, current authenticated actor-to-string route. No principal adapter, ownership permission or live task controller is installed.

2026-10-14 baseline HEAD/upstream `41192a9df906654628f8a09b33823d65fa6c29ab`, branch docs/m0r-contracts; upstream 0 ahead/0 behind, main 18 ahead/0 behind. Only the existing user AGENTS.md change was dirty; preserved/excluded. This is compatible source-audit/tooling/documentation work within unreleased 0.2.0-dev.7, with no production API/save/config or version change. The ongoing development line remains additive MINOR.

## What was traced

[The fingerprinted ledger](native-principal-string-evidence.json) binds 24 packaged classes and the vanilla client user-list Lua file. A reproducible whole-JAR **descriptor index** finds 20 public Steam-named String-returning methods, public connection/identity receiver candidates and exactly three packaged classes referencing NetworkUsers. This is a bounded candidate index, not complete control/data-flow proof. Methods with other names, reflection, third-party components and future builds are outside that completeness claim. Selected method bodies, inheritance, exposure registration and return conversion were inspected as data; no PZ or server code was executed.

| Candidate | Verified source finding | Result for incoming server actor |
| --- | --- | --- |
| S01 `player:getSteamID()` | Native long → ReturnValues.push → KahluaConverterManager → registered Long/long NumberToLuaConverter → doubleValue | Lossy for arbitrary SteamID64. tostring, formatting, arithmetic or a later native string conversion cannot recover rounded bits |
| S02 `getSteamIDFromUsername` | Native helper converts long to string before Lua, but checks GameClient.client | Dedicated branch returns nil; no server adapter |
| S03 `getCurrentUserSteamID` | Local Steam SDK string path, explicitly excluded when GameServer.server | Not the command sender; dedicated branch returns nil |
| S04 `getUsers()` → `NetworkUser:getSteamid()` | Getter returns a String directly; vanilla client ISUsersList uses these APIs. NetworkUsersPacket.write builds server records, including String.valueOf(connection.getSteamId()), in a local map, then serializes it | Promising lossless native conversion, but **not a server Lua registry**. getUsers reads NetworkUsers.instance.users; the observed population path is incoming packet parse, not the server writer's local map. Neither a stale/client mirror nor a DB username match supplies current actor/session proof |
| S05 `player:getOwner()` → connection description | Exposed IsoGameCharacter getter returns null; IsoLivingCharacter/IsoPlayer do not override it. UdpConnection.getDescription formats its own long as a string in native server code | No player-to-connection receiver via this getter. UdpConnection/GameServer are also absent from the inspected explicit exposure allowlist. A zombie simulation owner is not a player account binding; no world scan or description parser added |
| S06 ServerPlayerDB.getNetworkUserSteamID | Native String-returning saved networkPlayers query; file-readability change and SQL connection commit inside method | No verified Lua binding or current connection attestation; not a safe read-only authentication helper. No account/save database was opened or queried |
| S07 SteamUtils.convertSteamIDToString | Native long-to-string conversion exists | A Lua number argument is already rounded; no verified composition with the raw connection long before the Lua boundary. No Java/bridge/helper added |
| S08 reflection helpers | LuaManager.validateReflectionAccess requires Core.debug and rejects Class/ClassLoader/Lookup targets. Field.get still passes a Long through return conversion | Debug reflection is not the production principal boundary. No debug flag, class loading, security bypass or reflective invocation used |
| S09 other String IDs | SteamFriend, local SDK, browser Server, banned-ID and saved-row surfaces appear in the index | Source identity or freshness differs from the authenticated current sender. None is accepted as a principal |

`getOnlinePlayers()` does have a server branch returning GameServer.getPlayers; it supplies current player references but no lossless Steam string. `getConnectedPlayers()` delegates to GameClient. Display names, owner IDs, client Steam strings, permissions and bond values are not trusted. No fallback to username identity is silently introduced.

## The NetworkUser near-match

[VERIFIED — packaged source, S04] GlobalObject.getUsers calls NetworkUsers.instance.getUsers at offsets 0–3. NetworkUser.getSteamid returns its String field at 1–4. The server packet writer resolves the player's connection at 61, obtains its Steam long at 108 and uses String.valueOf(long) at 111 **before** the Lua boundary. That conversion is lossless in the native string-producing path.

The writer's map is local: records and counters are assembled, values are passed to NetworkUsers.send at 226, and the method returns. It does not assign that map to NetworkUsers.instance.users. In the inspected JAR, only GlobalObject, NetworkUsers and NetworkUsersPacket contain literal references to NetworkUsers. The singleton starts with an empty ArrayList; parse clears/refills it from the received buffer. Packet processing then notifies OnNetworkUsersReceived on the client side. requestUsers sends only under GameClient.client and its server handling requires SeeNetworkUsers. This is an admin synchronization interface, not authenticated request-principal extraction. No assumption is made that the running server list must always be empty under every mod/packet state.

The writer also merges existing whitelist/userlog rows; for a pre-existing row it marks the row online rather than always replacing its Steam string with the connection's current ID. Therefore even a fetched admin list needs more than `isOnline` and matching username. Client-returned rows or a new owner/Steam argument cannot close this gap. The investigation does not install interception of a native writer by changing a Lua table; native-to-native dispatch does not gain a Lua callback that way.

## Binding and precision boundary

[VERIFIED — packaged source] The earlier GameServer.receiveClientCommand trace still establishes a connection-resolved callback player, with null rejection before OnClientCommand. It does not expose the connection to that callback or stringify its ID. The new return-path inspection confirms that ReturnValues.push calls manager.fromJavaToLua at offset 14. The Long converter registration and doubleValue step retain the earlier precision finding; the existing offline adjacent-ID collision is a mathematical witness, not an executed Kahlua test.

The exposure index records literal class/setExposed calls: NetworkUser, SteamFriend, IsoPlayer and IsoGameCharacter are present; NetworkUsers, UdpConnection, GameServer, ServerPlayerDB, SteamUser and SteamUtils are absent. LuaManager.Exposer.shouldExpose tests membership in that set. LuaJavaClassExposer.exposeLikeJava also checks shouldExpose and disallowed status before binding. Public Java signatures alone are insufficient. This audit does not attempt to defeat those boundaries or claim every possible future binding is absent.

The required interface is a vanilla server Lua getter/callback that returns the current authenticated sending connection's SteamID64 **already as a String**, with enough connection/slot/episode/session evidence to reject stale actors and handle reconnect/character replacement. This describes required semantics, not an existing API name or authorization to patch the engine. A Native String getter on a cached record alone is insufficient. A manually maintained account mapping would be a different trust contract requiring separate approval; none is implemented.

## Validation and disposition

All 21 production Lua files, runtime metadata/options, nine prior native manifests, raccoon registration and frozen model/art are unchanged. No gameplay setting is added: precision, identity and current-session validation are mandatory technical boundaries, not configurable bypasses. Existing ownership/task refusal remains in force.

Exact commands from the repository root (the Python variable denotes the bundled interpreter):

```powershell
$identityPython = 'C:/Users/willi/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe'
$identityGame = 'E:/Program Files (x86)/Steam/steamapps/common/ProjectZomboid'
$identityJavap = 'C:/Users/willi/Desktop/Work/Project Zomboid/Mod Repositories/Last Known Address/build/toolchain/jdk-25.0.4.1+1/bin/javap.exe'
& $identityPython -B scripts/check_versions.py --root . --json
& $identityPython -B scripts/audit_principal_strings.py --collect --game-root $identityGame --javap $identityJavap --scratch .m0r-local/principal-string-audit --output .m0r-local/principal-string-audit/recheck.json
& $identityPython -B scripts/audit_principal_strings.py
& $identityPython -B scripts/audit_principal_strings.py --native --game-root $identityGame
& $identityPython -B scripts/validate_m0r.py
& $identityPython -B scripts/validate_foundation.py
& $identityPython -B scripts/test_domain.py
& $identityPython -B scripts/build_loadable.py --check
& $identityPython -B scripts/validate_database_authority_proof.py --native --game-root $identityGame
& $identityPython -B scripts/validate_m0r.py --native --game-root $identityGame
& $identityPython -B scripts/validate_foundation.py --native --game-root $identityGame
& $identityPython -B scripts/audit_public_push.py
git diff --cached --check
```

[TESTED — offline] Version/contracts/source/assembly and the existing 406 Lua regression cases pass. New source checks and 25 input fingerprints match; no mock principal success is counted as authentication. Whole-JAR candidate-index and repeated selected-source collection are reproducible. API findings are recorded as local library drafts. Source consistency means recorded bytes match, never D1 PASS.

Native baseline checks still **FAIL** on the five historical overrides. Two additional loose/package differences remain recorded in [NATIVE_OVERRIDE_DRIFT_REPORT.md](NATIVE_OVERRIDE_DRIFT_REPORT.md); no override repair, copying or analysis extension was attempted here. Effective clean runtime remains UNKNOWN. Raw javap outputs stay ignored; no native code, actual Steam IDs, player logs, private DB contents or credentials are published.

D1 **BLOCKED**; [overall NO-GO](DATABASE_AUTHORITY_GO_NO_GO.md) retained. G6 NOT TESTED; G7 BLOCKED / NOT TESTED; stable G8 BLOCKED. The [disposable identity cases](DISPOSABLE_RUNTIME_VALIDATION_PLAN.md) remain unexecuted: two players, reconnect, character replacement, forged/missing/stale identity and unauthorized dog access need a sufficient interface first. No game/server launch, deploy, Workshop upload, main merge or model work occurred. Continue only when a concrete lossless authenticated vanilla seam or an explicitly accepted alternative trust contract is available.
