# Growth and doghouse identity feasibility

Project Version: 0.2.0-dev.7

**No growth gameplay implemented.** The approved future design remains: a puppy enters an assigned compatible doghouse at a growth milestone and emerges with the next age model, preserving canonical identity, owner/handlers, personality/hidden training, health/history and equipment without a duplicate or loss. The temporary test carrier remains the raccoon.

## Native replacement findings

[VERIFIED — packaged Build 42.21 bytecode] `AnimalData.checkStages()` returns when nextStage is absent (92/123); selects the sex-dependent next stage and calls grow at 120. `AnimalData.grow(String)` allocates a **different IsoAnimal** (NEW 58, constructor 92). It copies native age/time/counter, attachment, hunger/thirst, acceptance list, stress, genome, custom name, sex and vehicle fields and sets the native integer at 304. The inspected method does **not** call copyFrom or copy ModData.

The world branch deletes the original at 540, adds the replacement to world at 545 and registers it at 564. The inventory branch removes the matching AnimalInventoryItem at 488 and deletes the original at 495. The vehicle branch invokes replaceGrownAnimalInTrailer at 583 and deletes the temporary new body at 588. These are not one project-controlled atomic identity transaction. Native integer retention cannot substitute for private identity/history/equipment transfer. See the hashed AnimalData/BaseVehicle inputs in [native-continuity-evidence.json](native-continuity-evidence.json).

Native worker return calls updateStatsAway and can reach growth indirectly. A postfact scan is insufficient to guarantee the old representation was quiescent, capture all state before replacement, prevent both bodies acting, or recover an interrupted replacement. No sufficient Lua pre/post growth transaction seam is verified.

The current test definition has one stage with ageToGrow=60 and **no nextStage/nextStageMale**, with mate/babyType absent and adult male test initialization. [INFERRED from the inspected condition] ordinary stage progression should stop without a successor. Runtime definition parsing and forced/debug callers remain untested. This is a research restriction, not a guarantee growth can never be forced and not a removal of the future puppy design.

## Required future doghouse transaction

1. Server validates threshold, exact current private ID/revision, living body, assigned compatible house and a proved exclusive transition seam. Clients submit only intent.
2. Reserve house/transition and write a private intent containing old generation, expected replacement, ownership/history/equipment references and recovery state before native mutation.
3. Quiesce the original; account for inventories/equipment through real authoritative receipts. A hidden/stationary flag alone is not exclusive quiescence.
4. Replace through a proved supported native operation, validate exactly one target with trusted provenance and the same private ID, then durably commit native/private pairing and release reservations.
5. Recover each interruption point deterministically. Never guess from nearest breed/age, adopt the first marker, reroll personality, duplicate inventory, or respawn because a body is absent. Ambiguous states quarantine with evidence intact.

This is a design obligation, not runnable pseudocode or a new writer. Required tests include interruption before intent, after intent, after native removal, after replacement, before/after private commit, repeated requests, two clients, house destruction/occupancy, death and restart. No transition may PASS until SP/dedicated evidence establishes same canonical identity and at most one actionable body. Current policy rejects growth and G6/G7 remain NOT TESTED/BLOCKED.
