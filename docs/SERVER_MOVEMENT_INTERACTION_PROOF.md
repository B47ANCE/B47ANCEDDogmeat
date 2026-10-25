# Server movement and interaction proof

Project Version: 0.2.0-dev.10

**D3 BLOCKED; D4 EXPERIMENTAL.** Source-supported movement and timed-action candidates exist. No exclusive, session-fenced canine controller or recoverable physical interaction receipt has been proved. No movement/bond/training controller, timed-action wrapper or network endpoint is added.

[P07–P09](database-authority-proof-evidence.json) record exact packaged methods and loose vanilla Lua lines. This audit reads the selected vanilla surfaces, not external mod implementations. The raccoon remains the approved carrier; current registration disables petting and the relevant managed attachment action is already refused. No setting exposes these candidates as gameplay.

| Required operation | Source observation | Proof still needed |
| --- | --- | --- |
| Follow | IsoAnimal.pathToCharacter delegates to PathFindBehavior2 then pathToAux; BaseAnimalBehavior.update calls followChr. Attached-player follow uses native walkToChr and can detach at distance | One authorized task producer, simulator execution side, safe owner/handler identity, observed progress and two-client synchronization |
| Stay / cancellation | Timed actions call behavior:setBlockMovement and restore it on stops/completion | No exclusive ownership token or complete arbitration with native emergency/needs/worker paths. A boolean or repeated path request is not a safe controller lease |
| Return to assigned area | pathToLocation is a native navigation candidate with attachment restrictions | Verified destination/home/access, obstacle failure, interruption, chunk unloading and no teleport |
| Feeding | ISFeedAnimalFromHand:isValid checks food membership; complete invokes feedFromHand and sendFeedAnimalFromHand. Native feedFromHand calls AnimalData.eatItem and mutates acceptance/stress/vanilla XP | Actual quantity/consumption and target identity, accepted outcome, cancellation/replay safety, private commit recovery and no duplicate rewards. complete returning true is not that receipt |
| Petting | ISPetAnimal has distance validity, complete and pettingFinished animEvent paths. Native petAnimal has a client/timer early return and native side effects | Accepted eligible event and exactly one observation across both paths/repeated callbacks. Do not count client clicks, animation or a no-op return as bond progress |
| Calm proximity | Server-loaded positions are candidate observations | Authenticated actor/bound dog, bounded eligible windows, willingness/stress, caps/diminishing budgets, no idle/training XP. No proximity loop implemented |
| Drinking / resting | AnimalData and native behavior own animal needs and physical actions | Verified resource use/finished rest and exactly one time owner; no second simulator or invented supplies |
| Equipment / lead | ISAttachAnimalToPlayer.complete changes attached-player membership/native data; native follow reads it | Real equipment transaction, permission/lease, disconnection cleanup and complete synchronization. Managed path remains refused |

Native path calls are physical intent candidates, not permission or success. Other vanilla behavior methods also choose paths. An external per-tick follow/stay loop could compete with those producers; it is not proposed. Direct position setters, teleport, animation-only completion and client-provided duration/resource/bond values are excluded.

Natural bonding remains the approved design: bounded calm proximity, actual feeding and accepted petting; one primary at 100; naming and loose follow only after committed owner plus trusted binding; real collar/lead for early control. Independent secondary bonds never transfer ownership. Rates/budgets require reviewed server sandbox configuration before activation. One finite session-only handler lease is still a design requirement, not live permission. Owner reconnect alone must not steal an eligible handler's work.

Obstacle navigation, cancellation, chunk loss, handler disconnect and multiple observers remain **[RUNTIME GATE] / NOT TESTED**. A valid private task can be suspended without issuing physical instructions. No source finding here resolves binding, native/private checkpoint or full lifecycle guarantees.
