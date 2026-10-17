# Server authority design

Proposed original architecture; not implemented or runtime-validated. Evidence date: 2026-10-12.

## Design gate

The desired authority model is clear, but a safe complete integration is not yet established. Affected gameplay implementation must STOP until private persistence, native/CD identity continuity and non-bypassable command/movement authority are proven. A UI-only restriction, public hidden-data table, or client-driven success report is not a permissible fallback.

Dependency evidence: [CD audit](COMPANION_DOGS_SOURCE_AUDIT.md), [DogPack audit](DOGPACK_COMPATIBILITY_AUDIT.md), [native audit](VANILLA_API_AUDIT.md). The handoff's strict authority is stronger than the installed CD follow-position lease model. That conflict is recorded, not waived.

## Ownership by subsystem

| Owner | Authoritative responsibilities | Must not own |
|---|---|---|
| Native PZ / CD adapter | Native animal existence, CD ownership, existing cargo, established movement/lifecycle and baseline veterinary state | New hidden training/personality outcomes |
| B47ANCE server domain | Persistent individual learning/history, separate confidence/anxiety, handler/discovery permissions, validated training sessions/budgets, task claims, additional approved welfare | Competing native animal instance, duplicate cargo or DogPack roster |
| DogPack adapter, when supported | Existing deployed roster, formation, roles and coordinated travel | B47ANCE command knowledge or biological universal alpha |
| Client presentation | Keybindings, radial/menu/HUD/manual, pending-action feedback, animations requested by verified results | XP, health, personality, item success, ownership or authoritative animal position |

Proposed modules are conceptual responsibilities, not copied dependency structure: dependency capabilities; private world store; identity resolution; individual learning; handler discovery; task arbitration; server requests; public projections; independent UI providers. Lua owns gameplay. A Java bridge may be considered only for a demonstrated private/durable persistence or engine capability gap under workspace policy.

## Stable identity and lifecycle

1. Server allocates an original persistent ID once, scoped to a persisted world identity and allocation state. Creation/resolution must be serialized and recoverable; no fresh random generation on every load.
2. Maintain a server-only binding from that ID to the verified persistent CD UID, with historical aliases if a proven lifecycle legitimately changes it. Neither network ID, display name nor owner token is canonical.
3. A native entity binding is temporary. Resolve the current animal and generation immediately before any commit. If unavailable/ambiguous, suspend or reject; never spawn a second animal merely because a chunk is unloaded.
4. Existing CD UID must be treated as read adapter input, not rewritten. If native/CD recovery produces competing instances, quarantine the B47ANCE binding until canonical selection is unambiguous.
5. Carry, trailer/vehicle/RV transitions, maturation and ownership transfers each require explicit detach/rebind evidence. Ownership transfer changes ACLs, not identity; former handlers lose active permission while their historical relationship persists.
6. Death marks a durable terminal record and cancels tasks/rewards. Optional reanimation would retain historical identity but create a separately validated hostile lifecycle, never preserve companion authorization. That entity path is currently BLOCKED.
7. Preserve orphaned records and migration diagnostics. Do not silently delete records because a dependency temporarily disappears.

## Private persistence and client projections

Hidden history/personality cannot reside in native/client-visible ModData or named global ModData. Proposed private store is server-memory plus a separately validated server-host persistence path. Native `getFileWriter/getFileReader` provides a cache-file candidate; durable world-local backups, rollback, flush/error handling and reconciliation remain EXPERIMENTAL. `getModFileWriter` is excluded because it writes installed mod content.

An original save envelope should carry a distinct schema, world identity, monotonic generation and integrity/error diagnostics. The record vocabulary and protocol will be designed independently; neither uses CD's private schema as a template. Never infer schema version from Project Version.

Private fields: intrinsic dispositions, undiscovered history/knowledge, full medical findings, unrevealed cue associations, precise eligibility/learning state and hidden odor experience. Public-to-observer: safe name/species/current visible activity and coarse alerts. Public-to-authorized-handler: discovered knowledge, known health findings, accessible equipment and own training feedback. Precise personality values should remain observations unless explicitly discovered by a supported mechanic.

All response projections use allowlists. Never attach a full internal record then remove a few fields. Per-handler discovery must survive a reconnect; discovering existing competence changes only that handler's knowledge, not dog XP. Permission changes invalidate cached projections. Diagnostic logs must not broadcast hidden records to ordinary clients.

## Request/commit contract

Each gameplay request names an action, an opaque persistent dog reference and bounded parameters. Derive the actor from the authenticated server callback. Re-resolve the native entity; validate schema/size/rate, revision, dog species/life state, handler rights, distance/floor/line of approach where relevant, equipment/item IDs, actual inventory, action duration, resources and current task.

Reject client-supplied owner, XP, genes, random roll, health result, nutritional benefit, task success or elapsed exercise time. Existing technical IDs and correlation IDs are not authorization. Deduplicate requests per actor/session and durable action identity where results survive restart. Rate-limiting and idempotence are different checks.

Commit by server-observed outcome. Consume the actual required resource once, advance state once, record the reward/transaction result, then notify affected clients. Repeated messages return the prior result or a stale-state refusal without repeating effects. Cancelled/interrupted actions award no unearned progress and do not partially consume unrelated inventory.

Default CD commands remain independently callable. Full overhaul therefore requires a source-pinned, proven command-policy seam that guards managed dogs on the server, including direct CD and DogPack entry points. Merely replacing a radial menu cannot enforce learning gates. No broad command-table replacement is proposed. Until the narrow seam is established, advanced managed behavior is BLOCKED.

## Learning and anti-farming

Separate command proficiency, cue familiarity, duration, distance, distraction and generalization from overall level. Overall obedience is a derived summary, never automatic mastery. Confidence, baseline anxiety disposition and current anxiety are independent dimensions. Breed affects physically plausible ranges and predispositions; individual behavior wins.

Rolling XP budget: persist accepted award events in game-world time across the last 24 in-game hours, with separate structured/passive totals and bounded aggregation. Keep enough granularity to enforce the configured rolling interval, not a midnight reset. Clamp budgets server-side; reject timestamps from the client. World-time rollback must be reconciled to the persisted generation/world identity before accepting awards.

Structured reward requires a server-observed exercise and valid reinforcement opportunity. Passive reward requires actual qualifying behavior over a bounded interval: successful recall, position adherence during real displacement, valid settle while a real work action occurs, or another explicit task. Nearness/idle presence is not proof. Check actual actor/dog displacement, obstruction and task state to prevent wall-walking and zero-motion farming. Repeated command packets cannot become repeated rewards.

The 28–56 day target is a calibration scenario, not a timer granting mastery. Measure a baseline new dog with regular effective training, then verify caps/personality/welfare influence. Previously trained dogs learn new cues faster but do not receive discovery XP. No perk-point allocation UI.

## Movement and task arbitration

Exactly one authoritative task lease per dog and one claimant per movable item/load. Logical claims use persistent dog/task identities; transient native handles are revalidated. Training, combat, care, reproduction and travel need explicit priority and interrupt rules. Safety interruption cancels/suspends rather than silently completing a task.

CD client position leases must be disabled and revoked for strict managed gameplay, with server-side capability diagnostics and prevention/detection of re-enable through tuning or another mod. Whether existing server follow/formation behavior remains correct is EXPERIMENTAL. No client prediction may write authoritative state. If strict movement cannot be established, stop affected tasks instead of accepting reports as outcomes.

DogPack remains the deployed movement provider if compatible. B47ANCE task eligibility may request existing movement only through an audited seam. Dynamic task/social influence is separate from its operational leader selection. Group commands evaluate every member independently.

## Health, inventory and transport

One health writer per condition. Initially expose CD conditions/read-only care context; do not concurrently run another hunger/infection/damage timer. New canine region records require an explicit damage arbiter and native/CD lifecycle contract before causing health changes. Human treatments are not canine suitability evidence. Grooming/comfort are welfare, not XP skills; recovery uses time/resources rather than instant resets.

Inventory delivery uses a serialized server transaction: validate ownership, source accessibility, destination permission/open state/capacity, weight/reach and item identity; lock/claim; move exactly once; persist result; synchronize through verified native APIs. On crash/reconnect, reconcile the real source/destination before retry. Never both spawn and remove by blind success messages. Corpse dragging, shared loads and real physical pulling remain experimental/blocked separately.

Transport occupancy belongs to one authoritative compartment/animal relation, never an independent dog item plus live dog plus recovery snapshot interpreted as three occupants. Native trailers and DogPack travel are preserved. New kennel compartments need actual vehicle definitions and capacity/ventilation/access evidence.

## Configuration candidates

Provisional namespace: `B47ANCEDDogTraining`; identifiers remain design proposals until the Mod ID is finalized. Stable settings must have localized name/tooltip, default, bounds/step, grouping, server interpretation and migration behavior. All 29 workspace-required Build 42 language folders need full key coverage with EN fallbacks when runtime content is created.

| Candidate group | Proposed default / bounded interpretation | Existing-save policy |
|---|---|---|
| Training rate | 1.0; proposed 0.25–4.0 | Future awards only, no retroactive XP |
| Structured daily budget | Conservative baseline; exact value pending calibration | Preserve accepted rolling history; new limit may temporarily exhaust budget |
| Passive training | 1.0 multiplier; proposed 0–2.0 | Future verified behavior only; no proximity reward |
| Prior training / working rarity | Conservative mixed population; probabilities bounded 0–1 | New dogs only; never reroll initialized identities |
| Personality variability / anxiety | Normal spread/severity; bounded profiles | Preserve intrinsic values; apply revised response tuning prospectively |
| Welfare/grooming/leash difficulty | Normal; simple grouped scales | Preserve existing conditions; clamp future progression |
| Injuries / rehabilitation | Conservative; only supported condition rates | No silent instant healing or accumulated surprise damage |
| Knox infection | Disabled | Explicit enablement affects future qualifying exposures only |
| Reanimation / zombie redirection / corpse hauling | Disabled and capability-gated | Unsupported engine path stays disabled even if setting requested |
| Pack size/conflicts | Supported provider limit; rare severe conflicts | Over-limit members remain owned; withdraw/suspend tasks rather than delete dogs |
| Transport/spawn adapters | Disabled until supported adapter is validated | Persist past spawn decisions/occupancy; no automatic mass respawn |

Exact progression budgets/injury probabilities are not invented during source audit. Sensible calibrated defaults are a Milestone 1/2 design gate. Do not expose per-byte protocol controls, UI coordinates, low-level AI tick counts, raw hidden trait tables or safety bounds as gameplay settings.

## Failure and acceptance gates

Missing dependency/version mismatch: diagnostics and gated actions; preserve private records. No server UI/render dependency. Missing dog: task suspended; no free respawn. Missing item/container: refusal before commit. Restart: load/migrate/reconcile before simulation. Unsupported future schema: quarantine/read-only, no data destruction. Dedicated client version mismatch: handshake refusal for B47ANCE actions.

Required proof before production gameplay: private-store confidentiality/durability; identity across every native/CD replacement; non-bypassable server action and XP policy; strict movement or a documented feature boundary satisfying authority; single health writer; antidupe transport/inventory; server sandbox values. Offline logic tests cannot close those native/runtime gates. G7 BLOCKED / NOT TESTED; G8 BLOCKED.
