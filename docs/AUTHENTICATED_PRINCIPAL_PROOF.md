# Authenticated principal proof

Project Version: 0.2.0-dev.7

**D1 BLOCKED.** The packaged command path associates a Lua callback with a player from the sending connection. A complete lossless SteamID64 + current connection + character episode + server session adapter has not been established. No gameplay principal adapter is installed.

Baseline: 2026-10-14, HEAD `56a391c1ca2073e1d4db40f851b7b23e01241ba9`, Build 42.21 / Steam build 25485521. [P01–P04 and input hashes](database-authority-proof-evidence.json) describe packaged-source observations. The [override report](NATIVE_OVERRIDE_DRIFT_REPORT.md) separately limits effective-runtime claims.

| Candidate | Source observation | Authority / limitation |
| --- | --- | --- |
| OnClientCommand player | GameServer.receiveClientCommand resolves slot through getPlayerFromConnection at 66; slot -1 uses getAnyPlayerFromConnection at 77. Null returns before dispatch. Callback at 217–228 receives module, command, resolved player, argument table | Connection-scoped player is a useful source-supported seam. Slot/argument selection is not permission. Recheck current presence, episode and dog ACL at use; runtime validation absent |
| getSteamIDFromUsername | GlobalObject method checks Steam mode and GameClient.client; native long-to-string conversion is inside that client branch | Returns null on the inspected dedicated branch. Cannot be the server adapter |
| IsoPlayer.getSteamID | Native return type long. KahluaNumberConverter.install registers boxed Long at 105–115 and primitive long at 199–210; NumberToLuaConverter.fromJavaToLua uses Number.doubleValue at 10 | Numeric read followed by tostring/format/string conversion cannot generally recover all original bits. Adjacent synthetic decimal IDs collide in the offline mathematical witness; this is not an executed Kahlua test |
| GameServer.getConnectionFromPlayer / UdpConnection | Native connection methods and a long Steam field exist; their native signatures are observable | No verified Lua callable route providing the authenticated Steam ID as a decimal string before numeric conversion. Native public visibility alone does not establish exposure |
| getPlayerInfo | Packaged helper builds diagnostic movement/network fields | No lossless authenticated Steam principal supplied in the inspected method. Display names, mutable ModData and client owner/Steam fields remain unacceptable |

Required future DTO: canonical principal decimal string, server-generated session ID, authenticated current connection/slot, character episode, presence set and current private authorization context. None may be accepted from client arguments. For account presence, aggregate all valid slots/connections; one slot leaving is not necessarily account offline. A new character cannot inherit a stale episode lease. Non-Steam identity requires an explicit separately reviewed policy, never an implicit username fallback.

The test fixtures use the literal labels Alice/Bob and `synthetic=true`. They do not authenticate anyone and cannot be called from runtime source. Forged/missing synthetic actor contexts are refused only to test a transaction precondition; that result does not resolve D1.

Two simultaneous players, reconnect, death/replacement, forged SteamID args, missing identity, stale connection and unauthorized access all remain **[RUNTIME GATE] / NOT TESTED**. [Disposable procedures](DISPOSABLE_RUNTIME_VALIDATION_PLAN.md) specify expected refusals. No actual account IDs or player logs are published.
