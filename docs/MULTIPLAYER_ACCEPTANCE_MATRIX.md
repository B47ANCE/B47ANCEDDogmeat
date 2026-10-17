# Multiplayer and lifecycle acceptance matrix

Project Version: 0.2.0-dev.7

New B-IDENTITY blocker, 2026-10-14: clients can load/wipe animal ModData through the native ObjectModDataPacket route. A matching marker alone is not provenance. Require forged/copied marker tests and an independently validated Lua-only authority solution before enabling ownership/gameplay. The [loadable persistence diagnostic](NATIVE_BOOTSTRAP_TEST.md) has only privileged Inspect/Provision commands, and dedicated ownership preparation refuses UntrustedNativeMarker.

Current [native identity investigation](NATIVE_IDENTITY_AUTHORITY.md): 274 offline tests do not clear T-IDENTITY. Extend it with clone-first restart, high/duplicate assigned native integers, erased markers saved before restart, and private identity recovery with no loaded carrier. Private record recovery and physical admission are separate acceptance claims.

M0R test specification, 2026-10-12. All gameplay tests below are NOT TESTED. No game/server was launched. Offline/source assertions are separately labeled. T-* identifiers are stable acceptance contracts, not test executions. [Milestones](MILESTONE_DEPENDENCY_GRAPH.md), [source index](M0R_SOURCE_EVIDENCE.md), [minimum candidate](MINIMUM_PLAYABLE_RELEASE.md).

## Environments and evidence record

For relevant rows test pristine SP, local hosted MP, two distinct clients on a headless dedicated server, and Linux dedicated. Record exact Project Version, commit, game build/class hashes, source/model identifiers, operating system/hardware, sandbox/capability revision, role/account fixture, reproducible steps, observed expected/actual result and bounded nonsecret logs. No player identifiers, credentials or raw server logs enter public Git. Source inspection or Windows path checks cannot mark Linux/native behavior PASS. G6 SP/host evidence and G7 dedicated evidence remain separate.

Common procedure: establish clean matched world/store fixture → exercise the row with owner/authorized handler/unauthorized second actor as relevant → reconnect/late join → save/restart → unload/reload → check server record and both clients → repeat packets/races/invalid parameters → assert exact dog/item/waste count and no private-field exposure. Record PASS/FAIL/BLOCKED/NOT TESTED per environment and scenario. Every dependent gameplay slice waits for applicable dedicated proof.

| ID | Scope / earliest milestone | Reproducible scenario and expected result | Environment / current result |
|---|---|---|---|
| T-ENVIRONMENT | M1A | Inspect actual client/server invocation and class baseline; no required loose injected classes/custom JAR/agent; compare pristine vs modified separately | Source partial; runtime NOT TESTED |
| T-REGISTRY | M1A | Register original shared animal tables before native cache materialization; invalid/missing type/breed fails cleanly; exactly one authorized spawn; unrelated vanilla animals intact | SP/host/dedicated/Linux; NOT TESTED |
| T-ASSET | M1A | Original model/skeleton/skin/animation/avatar loads on both clients; every reachable enabled state, root motion, interruption/death, corpse and UI references resolve | Client plus dedicated two-client observation; NOT TESTED |
| T-NATIVE | M1A | Native server route to valid tile, blocked edge/window/stairs, collision and cancellation; no client position control, teleport or two writers; late join sees same result | Two-client headless dedicated/Linux; NOT TESTED |
| T-AUTH | M1B | Observer cannot command/read private fields; claim/grant/transfer/revoke serialized; old handler loses queued replies/permissions; spoofed actor names ignored | SP/host/two-client dedicated; NOT TESTED |
| T-PROTOCOL | M1B | Wrong version/schema, oversized/invalid action, stale dog/generation/revision, replay/rate spam and reconnect old session refuse safely; unknown future store preserved | Offline protocol then dedicated; NOT TESTED |
| T-PRIVACY | M1B | Request public named tables and inspect animal/player ModData, packets, projection caches and client logs; only nonsecret anchors/allowlisted role fields appear | Two-client dedicated adversarial; NOT TESTED |
| T-IDENTITY | M1B | Spawn/save/load/unload/reconnect allocate once; duplicate/missing/foreign marker, UUID collision fixture and competing lookup quarantine without respawn/reroll | Offline domain then dedicated/Linux; NOT TESTED |
| T-RECOVERY | M1B | Torn slots/missing record/future schema/world-only/private-only rollback/paired restore/wrong world/partial native save; matched checkpoint required before mutation | Offline faults plus operator dedicated crash/restart/Linux; NOT TESTED |
| T-TRANSPORT | M1C, later vehicles M7 | Carry/drop-release/trailer full inventory, reconnect mid-transition, concurrent pickup, unload/restart; one native representation and original dog ID/clock; other vehicle route separately proved | SP/host/two-client dedicated/Linux; NOT TESTED |
| T-GROWTH | Before puppy/maturation | Native growth in world/item/trailer; original marker transfers/rebinds through proved Lua seam; native animalId alone never repairs lost marker | BLOCKED source seam; runtime NOT TESTED |
| T-DEATH | M1 lifecycle; later hostile M8 | Death during path/care/inventory commit; one tombstone, no obedience/reward, exact cargo/corpse reconciliation; corpse/item round trip separately tested | Two-client dedicated/restart; NOT TESTED |
| T-TASK | M1C | Native flee/follow/need competes with task, same-priority replacement, timeout, cancel/disconnect/transfer/death, resource removal and restart; safe interruption/resume, no stale pointer | BLOCKED exclusive seam; runtime NOT TESTED |
| T-TRANSACTION | M1C before consumers | Crash/retry every prepare/physical/receipt/project phase; two claimants/full destination/closed container; exactly one real item or quarantine, no blind refund/recreate | Offline receipts then dedicated crash/restart; NOT TESTED |
| T-BIOLOGY | M2/M3 | Loaded/unloaded/inactive/carried/kenneled/vehicle/offline modes, equal game hours at 4-hour/default day length, rate changes, puppy/senior/ill/anxious fixtures; no duplicate native catch-up or indefinite holding | Offline integration then SP/dedicated/Linux; NOT TESTED |
| T-WASTE | M2 | Urine/feces creates physical valid-surface object once, safe carrier anchor, persistence/decay/cleanup and duplicate discharge; bounded catch-up accumulation, no stale transported tile | BLOCKED physical anchor proof; runtime NOT TESTED |
| T-TRAINING | M3 | Independent cues/knowledge/discovery, prior trained/new cue, structured/passive rolling caps, two-session calibration, idle/wall/packet/reconnect exploits and actual resource consumption | Offline rewards then SP/two-client dedicated; NOT TESTED |
| T-CUES | M3 | Spoken/hand/whistle/conditioned clicker/tone/vibration sensitivity; actual duration/distance/distraction behaviors; audible world attraction and silent cues remain silent | Client observation + dedicated sound/authority; NOT TESTED |
| T-HEALTH | M2 health sub-slices | Native vs extension condition writer, region injury attribution, safe original grooming/treatments, resources and slow rehabilitation; disease-specific zoonosis only after review | Suitability/source gate then dedicated; NOT TESTED |
| T-POPULATION | M2 population sub-slices | Reload same decision key never respawns; configured limits, independent breed/personality/history/housebreaking distribution; absent POI adapter fails cleanly; no guaranteed police dog | Offline distribution/receipts then dedicated/Linux; NOT TESTED |
| T-HOME | M4 | Safehouse/custom home/zone ACL, reachable actual food/water/rest, no instant need reset, blocked/locked exit, no safe potty tile, danger and return to prior task | SP/two-client dedicated/restart; NOT TESTED |
| T-DOOR | M4 | Supported vanilla/player-built/modded types; install/remove/repair exact items; fit/direction/lock/barricade/electronic ACL/power loss; opposite dogs and unload mid-crossing; main door intact | BLOCKED selective collision seam; runtime NOT TESTED |
| T-SECURITY | M5 | Independently prove noise/investigation/damage/dog alert; fit/locked/reinforced/barricaded flap; crawling only through valid native transition, no replacement/teleport or whole-door bypass | BLOCKED crawl seam; other behavior NOT TESTED |
| T-SCENT | M6 | Real trained target odors, samples/discrimination/false alerts/indication; people vs wildlife and environment proof; no knowledge of hidden fish/items | Offline registry then dedicated; NOT TESTED |
| T-WORK | M6 | Designated real-item retrieval, downed game/resource indication/fishing equipment/water recovery/guard; permissions/reach/capacity and observed successful physical result | SP/two-client dedicated; NOT TESTED |
| T-PACK | M7 | Per-dog proficiency/lease; social influence/disputes, simultaneous conflicting group orders, member unload/death/transfer; no universal alpha or inherited mastery | Two-client dedicated/performance/restart; NOT TESTED |
| T-LOGISTICS | M7 | Real container delivery, corpse/load claims, paired hauling and contamination restrictions; one load, original identity, no duplication in crash/reconnect | Dedicated/transaction/health/physics gates; NOT TESTED |
| T-ADVANCED | M8 | Separate proof for Knox/hostile reanimation/collar, true shared physics, zombie redirection/restraint, multi-kennel truck, lure/launcher/projectile landing; no armed explosive dog transport | Individually BLOCKED/EXPERIMENTAL; NOT TESTED |
| T-SANDBOX | Every slice | Server config validation, default/bounds/enum normalization, hot changes, disabled transitions, existing-save preservation, absent optional adapter and capability override refusal | Offline schema then dedicated; NOT TESTED |
| T-LOCALIZATION | Every slice | JSON/key/fallback/placeholder parity in all 29 languages, translated actions/refusals/manual and dynamic names; no missing player strings | Offline coverage then client UI; NOT TESTED |
| T-INPUT | M1B onward | Keyboard/controller equivalents to hover, conflict-free keys, focus/confirm/cancel/help/pin, radial hold/toggle, 720p/1080p/1440p and 100/150/200% scale | Client/controllers; NOT TESTED |
| T-PERFORMANCE | Each slice / M9 | 1/8/32 dogs, 100 waste records, measured scheduler/path/custom-network budgets, 60-minute growth and restarts; native baseline separate | Dedicated/Linux benchmark; NOT TESTED |
| T-COMPATIBILITY | Each integration / M9 | No dog-mod dependency; optional Drugs93/map/vehicle adapter absent/version mismatch; original IDs case-correct; no foreign entity adoption/writer conflict | Source plus dedicated/Linux; NOT TESTED |
| T-VERSION | M0R / every iteration | Canonical VERSION/current mirrors/change record consistent; exact evidence version; --release only after authorized artifacts | Windows offline current check only |
| T-RELEASE | M9 | Exact source/artifact provenance, no Java/JAR runtime dependency, safe package members/CRC/case/hashes, manual claims match passed features, G7 before G8 | BLOCKED; no artifacts authorized |

## Blocker identifiers used by traceability

| ID | Exact unresolved condition | Resolution gate |
|---|---|---|
| B-ENV | Effective/pristine client and dedicated class/API baseline not demonstrated | T-ENVIRONMENT |
| B-ASSET | Original GSD standing mesh/coat/authoring rig partially authored; native definition, rig mapping, enabled-state animations/corpse/avatar and PZ loading remain unproved | T-REGISTRY/T-ASSET |
| B-TASK | No proved Lua-exclusive arbitration over native movement/behavior | T-NATIVE/T-TASK |
| B-IDENTITY | Client-resistant native carrier provenance and complete release/streaming/growth/transport/death binding observation not proved | T-IDENTITY/T-TRANSPORT/T-GROWTH/T-DEATH |
| B-STORE | Native world/private-store pairing and crash-durable receipts unproved | T-PRIVACY/T-RECOVERY |
| B-INVENTORY | Exactly-once real physical item commits/recovery unproved | T-TRANSACTION |
| B-WASTE | Persistent replicated physical waste and carrier/offscreen anchor unproved | T-WASTE/T-BIOLOGY |
| B-DOOR | No selective closed-door dog aperture/collision transition proved | T-DOOR |
| B-ZOMBIE | No closed-door zombie crawl/squeeze transition or canine hostile entity proved | T-SECURITY/T-ADVANCED |
| B-HEALTH | Condition-specific native writer/region attribution/canine treatment evidence missing | T-HEALTH |
| B-SCENT | Target-specific scent/trail/environment/water reach evidence incomplete | T-SCENT/T-WORK |
| B-PHYSICS | No Lua-safe constrained/shared physics/drag/restraint/projectile contract proved | T-LOGISTICS/T-ADVANCED |
| B-VEHICLE | No original verified special compartment/vehicle occupancy path | T-TRANSPORT/T-ADVANCED |
| B-RUNTIME | No actual operator SP/dedicated/Linux validation on implementation | Relevant G6/G7 rows |

T-* coverage specifies what must pass; none of these scenarios was executed by the documentation validator. G6 NOT TESTED; G7 BLOCKED / NOT TESTED; G8 BLOCKED.
