# Offline self-care and database lifecycle

Project Version: 0.2.0-dev.12

Approved **design default**: Remain in World — Self-Care (`SelfCare`). Optional `StoreOffline` is not enabled. Current diagnostic behavior is unchanged and does not implement these policies. A database logical record/session binding proposal does not overturn Option A. Active native lifecycle, movement control and durability remain gated.

## Required lifecycle operations

| State / transition | Authoritative operation and recovery rule |
| --- | --- |
| WILD | Server-controlled population reservation/creation receipt, immutable identity; no auto-adoption of arbitrary native strays |
| WILD → BONDING | First eligible verified relationship event; multiple players may progress independently |
| BONDING → OWNED_ACTIVE | Unique unowned-primary CAS at verified 100%; commit owner/relationship/event once, then permit naming/loose-follow intent |
| OWNED_ACTIVE → OWNER_OFFLINE_SELFCARE | Server account presence reaches offline; release owner lease, preserve authorized secondary work, commit intent/state; activate only through proved native control |
| OWNER_OFFLINE_SELFCARE → OWNED_ACTIVE | Authenticated owner presence returns and binding valid; retain location/welfare/medical/caretaker progress and current compatible handler; no teleport |
| Owned state → WITHDRAW_PENDING | Store mode only after all capability gates pass; block new noncritical work, resolve all leases/claims and snapshot actual trusted state |
| WITHDRAW_PENDING → STORED_OFFLINE | Only after recoverable private checkpoint **and** verified physical absence from every managed representation/save route; receipt required |
| STORED_OFFLINE → RESTORE_PENDING | Authenticated owner, matching world/record/terminal state, no live/pending/virtual/item/vehicle conflict; reserve exactly one authorized creation transition |
| RESTORE_PENDING → OWNED_ACTIVE | Validate exact resulting body/binding/private transaction, publish once; uncertain construction never retries or spawns again |
| Any uncertain transition → QUARANTINED | Preserve record/history and pending receipts; deny privileged actions; no automatic delete/replacement or highest-generation guess |
| Living state → DECEASED | Verified death/terminal transaction, durable tombstone; cancel/fence leases, reconcile cargo/tasks and forbid ordinary live restoration |

Lifecycle and representation availability are separate. Chunk-unloaded/unseen does not mean stored, deceased or permission to create a new body. Binding registry fields include world/dog, current native reference, session, entity generation, logical lifecycle and verified admission evidence; these references are never durable proof. QUARANTINED can return only through a separately proved reviewed reconciliation; no automatic transition is proposed. Terminal corruption/uncertainty preserves history and refuses live recovery.

## Default self-care

When safely supported, offline dogs remain physically encounterable and vulnerable. The sole arbiter chooses accessible appropriate real food/water and applies only verified consumption receipts. No free food/hydration, training XP or serious-condition cures. One field/clock owner prevents duplicate native catch-up and private simulation. No invented offscreen resource use, waste object or medical recovery.

Prefer assigned safehouse territory, indoor bed, doghouse or compatible kennel according to familiarity/weather/health/comfort. Respect stable home permissions, real doors/flaps, size, reachability and threats. Essential food/water/bathroom/doghouse trips and emergency escape may leave the safehouse; attempt return afterward. A home restriction cannot trap a dog in lethal danger, make it invulnerable or teleport it through a closed door.

Use a trained potty area when accessible; delay only safely or allow real accidents when blocked. Actual urine/feces and sanitation remain required features with their own physical/writer gates. Rest supports appropriate natural recovery, not automatic cure of serious injury, infection or parasites. If supplies/routes are unavailable, seek permitted alternatives and distress/suffer real consequences; survival is not guaranteed.

Trusted caretakers/trainers may continue only with relationship cooperation, owner permission, skills/resources and the relevant offline settings. Their committed progress survives owner reconnect. Eligible future puppy/doghouse transitions preserve the same logical identity/relationships/health/training/history and equipment, but remain blocked until safe entity replacement. No growth implementation or model work occurs here.

## New lifecycle feasibility audit

| Required capability | Bounded evidence | Current result |
| --- | --- | --- |
| Exclude managed animals from normal native restoration | D04: IsoObject.Serialize() returns true; no per-managed override/switch verified; native Java calls cannot be intercepted by a Lua table replacement | UNKNOWN / BLOCKED; no save exclusion implemented |
| Withdraw before native save | D05: IsoAnimal.delete removes world/square/update lists; worker removal marks last saved cell changed, but returns if cell coordinates unavailable | Source mutation exists; not a durable all-representations withdrawal/atomic receipt. BLOCKED |
| Reconcile before duplicate provisioning | Earlier source trace covers worker, saved cells, item/vehicle/hutch/corpse routes; no complete pre-admission receipt | BLOCKED; loaded-only census is insufficient |
| Bind without copied public marker | Exact current server reference may correlate within one process; durable body origin still absent | Current session registry cannot certify prior sessions. BLOCKED |
| Stay active across restart without ambiguity | Option A identity/serialization/callback findings unchanged | NO-GO under verified boundary; database alone does not change it |

No stored mode, automatic restore, native purge, global animal disable or first-match adoption is implemented. Before any physical creation, prove private row/pending transactions, active bindings **and all relevant saved representations** are reconciled. Missing or offline alone never permits provision. An explicit operator-selected logical association would change semantics and requires a separate approved contract; it is not the default self-care implementation or a hidden recovery shortcut.

Store-mode crashes require evidence at every point: before intent, after private prepare, before/after native withdrawal, before terminal stored commit; then before restore reservation, after constructor, before binding/commit and after publication. Ambiguity retains both records/receipts and disables authority. Neither SQLite nor private file CAS establishes atomicity with native saves. Dedicated restart/rollback/death evidence is mandatory before enabling either lifecycle policy.
