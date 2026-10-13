# Canine biology and game-time model

Project Version: 0.1.0-dev.1

M0R design, 2026-10-12. FEASIBLE bounded extension model; native reconciliation and physical offscreen elimination EXPERIMENTAL. Rates and thresholds below are provisional game-balance calibration values, not veterinary claims. [Ownership](NATIVE_STATE_OWNERSHIP_MATRIX.md), [task priorities](TASK_ARBITRATION_CONTRACT.md), [settings](SANDBOX_SETTINGS_REGISTRY.md).

## Clock and field ownership

Use authoritative elapsed game-world hours (candidate getGameTime():getWorldAgeHours()). Never accept client time or elapsed wall-clock time. A stopped or paused world advances no needs; a running server advances world time even when a handler is offline. Native hunger/thirst/fatigue/health/growth remain native-owned. Read and reconcile native load/catch-up behavior; never advance those fields again. B47ANCE owns distinct bladder/bowel fullness, urgency, extension stress, location preferences and learning/event history. Baseline anxiety and personality are persistent traits, not transient stress or replacement native stress.

Each owning domain persists lastAppliedGameHour, configurationRevision, authoritative representation/mode, current state and committed event sequence. Negative elapsed time, a changed world binding or mismatched checkpoint enters [recovery](PRIVATE_PERSISTENCE_RECOVERY_CONTRACT.md). Do not silently reset clocks or award retroactive XP.

## Representation matrix

| Representation | Native needs | B47ANCE elapsed-time rule | Physical action / waste rule |
|---|---|---|---|
| Loaded live dog | Native simulation; read current values | Integrate known intake/activity/care and extension rates once | Real current valid tile, safe route and server-observed discharge |
| Unloaded / inactive chunk | Native persistence/catch-up, exact semantics to prove | Integrate only known mode/events; no guessed feeding, care, fights or paths | Durable physical-waste descriptor requires proved safe anchor; no stale-tile spawn |
| Carried animal inventory item | Native embedded animal semantics to prove | Same ID/clock; confinement modifiers, no locomotion | Carrier/kennel receptacle must be physically represented and persistent; unsupported anchor blocks this behavior |
| Kennel / crate | Native representation and resources to prove | Same clock; known confinement/ventilation/rest only | Valid kennel waste object/receptacle and cleanup transaction; no free bathroom trip |
| Trailer / vehicle compartment | Native embedded animal/occupancy | Same clock; proved containment and stress conditions | Waste attached to proved compartment anchor, never former world position |
| Handler offline, dog loaded | Native simulation continues | Ordinary server game time; handler absence grants no resource/reward | Native-safe autonomous task only if trained, permitted and capability proven |
| Server stopped / world paused | No advancing game time | No wall-time catch-up | No offscreen objects/events |
| Dead dog | Native terminal state | No living needs progression; preserve tombstone/history | Reconcile existing committed waste/items; no new living behavior |
| Living quarantined dog | Native system remains authoritative; mod commits suspended | Retain unapplied elapsed intervals/known modes for conservative recovery, never erase time | Pending physiology/waste accounting remains unresolved; no free indefinite-holding claim or invented objects |

## Bounded integration

For an owned continuous field f, integrate the known piecewise-constant rate over authoritative elapsed game time, then clamp its physical range. Bladder/bowel use normalized 0..1 storage plus a separate overdue/urgency state; saturation is not permission to retain forever. Intake and discharge are distinct committed events. The same event and elapsed interval must never be applied twice.

Provisional computation budget: resolve at most 24 known one-hour recent segments; aggregate older constant-mode intervals analytically once. Configuration/mode/event changes define exact breakpoints; merge only equivalent intervals. If more breakpoints exist, process bounded work batches without dropping elapsed time or committing partially advanced clocks as complete. Rates may use age/size/known intake/sleep/activity/stress/illness. Missing observations select documented conservative uncertainty, not an invented successful meal or injury. Native-state gaps block native-rate modifications.

Offline analytical acceptance compares one continuous integration with split/reload integration: normalized field difference at most 0.000001, identical committed event count/IDs, no replay award. This is a proposed future logic-test tolerance; no biology implementation or test has run in M0R. Four-hour-day and default-day worlds must produce equal state for equal game hours.

## Urgency, accident and waste

Provisional urgency thresholds: signal at 0.65, seek relief at 0.80, emergency at 0.95. Calibrate by age, size and known health under sandbox need-frequency interpretation. Danger/critical care can stop the route; emergency relief preempts Stay/work. Notify once per urgency transition with bounded reminders, consider safe alternate reachable relief tiles, and eventually discharge on the actual valid surface. No command permits indefinite holding. AccidentLikelihood=0 removes avoidable stochastic mistakes, not bodily emergencies.

A discharge requires one recoverable exactly-once logical journal record coupling owned need decrement to a unique elimination receipt and the configured physical result. This is a design requirement, not a proved filesystem or cross-store atomic primitive. With PhysicalWasteEnabled=true, create a real persistent replicated urine puddle or feces object at a verified tile/surface, with type, accounted volume, age, stable ID and cleanup/decay state. For inactive chunks, a deferred physical-object descriptor is acceptable only if its persistence, anchor and eventual single materialization are proven. No purely textual or invisible-stat accident substitutes for required physical waste in the enabled core profile. If a carrier/offscreen anchor is unsupported, record an unresolved event and block lifecycle acceptance; do not silently discharge at a stale tile or reset need. With the explicit PhysicalWasteEnabled=false sandbox opt-out, commit a configured_no_object elimination receipt; physiological discharge can complete without a new world object, while existing cleanup/decay remains active.

Catch-up never spawns one object per missed tick. Bounded spatial/temporal consolidation may combine compatible waste while preserving accounted type/volume/age and physical cleanup consequences. No unlimited permanent accumulation; normal decay and capped materialization batches remain required. These technical budgets are internal safety limits, not micro-settings. Their geometry and object API contract is EXPERIMENTAL.

## Learning and switch semantics

Housebreaking levels 0..5 are independent of obedience, breed and police/military history. Reward only a real server-observed suitable elimination plus eligible reinforcement; one accident never erases all proficiency. A previously housebroken dog can retain its skill when progression is disabled.

Four independent server controls are proposed: EliminationPhysiologyEnabled (B47ANCE extension only), HousebreakingProgressionEnabled (new learning), AutonomousBathroomTripsEnabled (self-directed routes), and PhysicalWasteEnabled (future waste creation). Disabling extension physiology freezes retained fullness with a transition timestamp, cancels obsolete queued urgency intents/signals/routes and prevents faked natural elimination XP; re-enable accrues only enabled intervals. Manual take-out can still occur, but no reward without eligible real discharge. Disabling learning preserves proficiency; disabling autonomy keeps manual take-out and emergency physiology meaningful while physiology is enabled. Disabling physical waste is an explicit sandbox opt-out from future objects, not a technical workaround for missing capability. Existing waste stays cleanable/decays normally. The core acceptance profile has all four enabled.

Feeding/drinking/rest and recovery use actual accessible resources and elapsed time. Existing conditions are never instantly erased. Unsupported canine treatments remain blocked; no human dosage or pharmacology substitution. T-BIOLOGY, T-WASTE and T-RECOVERY require loaded/unloaded/carried/kenneled/transported/offline modes, old intervals, repeated loads, conflicting clocks, locked exits, danger, illness, senior/puppy cases, cleanup and physical object persistence.
