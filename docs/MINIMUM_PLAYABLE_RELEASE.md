# Minimum playable development candidate and full roadmap

Project Version: 0.2.0-dev.7

M0R scope design, 2026-10-12. This is a candidate acceptance contract, not a release announcement or approval. M1 is a research prototype. The minimum candidate does not replace the full approved feature roadmap or mean 1.0 completion. No release version is invented: the historical M0R checkpoint was 0.1.0-dev.1 and the current compatible art checkpoint is 0.1.0-dev.2; a future gameplay/release iteration needs its own compatibility classification and reviewed version decision.

## Required minimum candidate

Use a pristine Lua-only native canine implementation with original registered assets, server movement/damage/lifecycle and unambiguous ID/private record; authorized naming/care, owner/handler roles and allowlisted UI; verified carry/release/trailer, unload/reload/reconnect/restart and death. Puppy/maturation support cannot be claimed until its replacement-marker gate passes; the full approved roadmap retains it.

Playable core requires food/water/rest/welfare, distinct bladder/bowel, real persistent urine/feces/cleaning, independent housebreaking/potty zones/signals, foundation Sit/Down/Stay/Heel/Recall/Place/Release with real server-observed behavior, positive reinforcement and anti-farming rolling budgets, human knowledge entry, genuine audible/silent cues, supported leash behavior, installable mechanical doggy doors with physical size/mode/lock/access/traversal and basic safehome/relief autonomy. Essential localized manual, keyboard/controller access, state-aware actions and clear refusals ship with the corresponding feature. If selective flap passage, physical sanitation or safe authority is blocked, this core candidate is BLOCKED. An ordinary open door is a proposed alternative, not silent fulfillment of a flap.

## Deferred but retained approved scope

All [traceability rows](FEATURE_TRACEABILITY_MATRIX.md) remain obligations: complete trait/history variability and evolution; all original breeds and weighted locations/POIs; training equipment/cue conditioning, force/stumble, occupations/books/VHS; full veterinary regions/conditions/grooming/rehabilitation with reviewed suitability; all working/scent/tracking/search/foraging/fishing/retrieval/hauling/guarding; original packs/social influence/group commands; containers/corpses/dragging/shared loads; capture/kennels/compartment trucks; reinforced/electronic doors and security; zombie investigation/damage/crawl; optional Knox infection/reanimation, redirection, restraint/lures/throwers and separately audited projectile interoperability. Deferred means not yet implemented, not removed or promised complete.

## Training calibration scenarios

Provisional fixture: healthy initially untrained adult mixed-type, documented neutral traits, baseline handler skill/knowledge, proper resources, two ten-game-minute structured sessions per day plus bounded verified passive activity. Test each foundation cue independently with duration/distance/distraction criteria. Target 95/100 successful safe familiar trials and at least 80/100 declared trained-generalization trials across four unfamiliar contexts. Practice uses authoritative game time and actual behavior; no day-count unlock.

The master 28–56-game-day complete-training target is preserved. Its exact definition across foundation proficiency and specialized work remains a REVIEW DECISION: do not silently redefine it as foundation cues only or guarantee every specialized skill in that interval. The fixture measures foundation progress first; later working-skill scenarios must state the intended endpoint and baseline. Compare prior-trained/new-cue cohort (faster cue learning, zero discovery XP) and high-anxiety/ill/neglected cohort (slower until appropriate care/time), structured/passive caps, 4-hour-day scaling and adversarial idle/wall/replay trials. These are acceptance targets, not observed balance.

## Performance acceptance targets

Provisional benchmark: 1/8/32 loaded dogs, two clients, 100 active waste records, simultaneous safe movement, ten-minute warm-up and twenty-minute sample; observe sixty-minute bounded growth/restart behavior. Report hardware/build/settings, native baseline and mod cost separately.

| Surface | Proposed internal budget | Measurement / failure rule |
|---|---|---|
| B47ANCE Lua scheduler | p95 <=2ms, p99 <=5ms per 50ms slice at 32 dogs | Instrument bounded own work; budget breach blocks candidate pending tuning |
| Path requests | <=2 per moving dog/second; <=20 globally/second | Fair bounded queue; obstacle change can request replanning without per-tick scans |
| Custom projection traffic | <=1KiB per dog/observer/second steady state | Count native traffic separately; coalesce unchanged projections |
| Record/object growth | Bounded by configured population and proved decay/retention | No indefinite waste/receipt/task/relationship accumulation; preserve unresolved recovery data |
| World/scent/zombie lookup | Spatially bounded tasks | No global per-tick world, inventory or zombie traversal |

These figures are provisional capacity/performance gates, not measured PASS or gameplay sandbox knobs. Runtime/native API constraints may require a reviewed revision; never hide a failed benchmark by changing numbers after testing without a decision record.

## Input, accessibility and manual

Mouse hover may expand a paw roster but is never sole access. Keyboard focus opens the roster/details/help/pin/context actions; configurable unclaimed F-keys and hold/toggle radial alternatives preserve existing bindings. Controller uses a reachable roster toggle, directional navigation, confirm/cancel, radial-stick selection and close/help/pin actions. Unsupported controller behavior blocks the declared candidate requirement rather than disappearing under 'where feasible'. Test 720p/1080p/1440p and 100/150/200 percent scale, no clipped critical controls, clear focus and failure states.

The in-game manual includes installed capability status, finding/claiming dogs, privacy/ACLs, traits/history discovery, positive reinforcement/cues, care/welfare/housebreaking/waste, supported doors/modes/security, transport/recovery and troubleshooting. Implemented chapters only; advanced blocked chapters may clearly describe unavailable roadmap capability. Warn about actual proven door noise/damage/entry; never claim zombie-proof small flaps or crawler entry from size alone. Ordinary main-door locks/collision remain intact.

## Release evidence

[MP matrix](MULTIPLAYER_ACCEPTANCE_MATRIX.md) requires two-client headless dedicated, Linux, restart/unload/transport/death/recovery, malicious requests and configured feature transitions. Offline checks and SP do not prove dedicated behavior. G6 NOT TESTED; G7 BLOCKED / NOT TESTED; G8 BLOCKED. Packaging/publication need separate authorization after applicable runtime gates and --release version/artifact checks. A public documentation push is backup/review evidence only.
