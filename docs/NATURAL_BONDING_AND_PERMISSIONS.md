# Natural bonding and player permissions

Project Version: 0.2.0-dev.9

Design proposal; no live bond/ownership writer or arbitrary Claim action is enabled. A permanent dog may have one primary owner and many independent secondary relationships. A native marker, actor-supplied SteamID, sub-bond percentage or UI button cannot establish ownership.

## Verified interactions, progress and first primary bond

Calm proximity, appropriate feeding, accepted petting and repeated positive experiences can contribute. Personality, willingness, confidence, anxiety, current stress/needs and recent interaction history determine eligibility/cooperation. The controller needs trusted native dog/player observations and a safely bound representation. Current raccoon diagnostic explicitly disables petting/pickup; it is not a ready-made bonding API.

Proximity contributes only within bounded server-observed eligible time windows, diminishing/capped contributions and a daily budget. It is not unlimited per-tick progress or obedience/training XP. Feeding requires a verified appropriate item, source inventory, quantity/consumption receipt and actual native interaction; petting requires accepted native completion. Client button presses, claimed durations, repeated packets, cancelled animations, stale positions and rejected food do not count. Receipt/task/session deduplication, cooldowns and server-owned budgets prevent replay/farming. Exact rates/thresholds other than the fixed 100% primary requirement await balancing and server sandbox design before implementation.

When an **unowned** dog reaches 100 bond through valid accumulated evidence: validate current aggregate/relationship/config revisions and principal; CAS the unique primary-owner slot; commit ownership, relationship and one bond-completion receipt in the same private transaction. Only after committed safe binding may the server expose naming/companion UI and request a **loose-follow intent** through the sole native control seam. Commit uncertainty quarantines effects; it never grants permission from a pending UI result. Two eligible players cannot both become owner. The losing relationship is retained as secondary; full secondary bond never transfers ownership.

Bonding does not grant obedience levels, reset learned cues/personality or make recall reliable. Loose following can be interrupted by scents, animals, fear, obstacles and ordinary distractions; untrained dogs can get lost. A collar identifies/provides an attachment point; only a real attached lead provides physical handling, and reliable off-lead behavior needs training. Neither item teleports or makes wandering impossible. Lost/unavailable native contact retains ownership/history; reunion/recovery needs the separately proved lifecycle.

## Secondary trust, consent and competence

| Relationship | Candidate interactions | Mandatory additional checks |
| --- | --- | --- |
| Unfamiliar | Limited safe approach/interaction | Dog willingness and safe proximity |
| Acquaintance | Feeding, accepted petting | Real resources/accepted interaction; no authority shortcut |
| Friendly | Routine permitted care | Relevant owner policy and current welfare |
| Trusted Caretaker | Grooming, walking, shelter, welfare/housebreaking and permitted examinations/treatment | Owner grant, skill/equipment/suitability; lease for active handling |
| Trusted Trainer | Teach/reinforce obedience, agility, working skills, confidence/socialization | Owner training grant, knowledge, canine learning state and validated training receipt |
| Trusted Handler | Temporary permitted travel/work commands | Action-scoped grant, cooperation/training/equipment, active exclusive lease |

Tier thresholds are provisional and must not be inferred solely from a scalar bond. Permission = owner/server authorization **and** relationship/cooperation eligibility **and** applicable competence/equipment/safety/lifecycle checks. Trust affects willingness; it does not grant restricted administration. Positive secondary feeding/petting/grooming/walking/care/training histories accumulate per dog-player relationship without changing the primary slot.

Rename, ownership transfer, deletion of the primary bond, exclusive cosmetics and permanent removal remain owner/admin policy operations, not side effects of trusted care. Restricted equipment and dangerous working tasks require their specific authorization; a broad handler tier cannot bypass it. A 100% secondary bond is still secondary. Training/caretaker work while the owner is offline remains allowed only with the relevant sandbox permission and owner delegation; disabling it stops new work and safely resolves in-flight receipts without erasing history.

Revocation/owner transfer increments ACL/fence revisions, invalidates stale queued requests and projections, and safely ends incompatible leases/tasks. Never undo already consumed food/items or grant a second reward. Bond history can remain after revocation without retaining active capabilities. Owner reconnect preserves trusted players' committed care/training and location; it does not reset welfare or automatically steal an active lease.

## Naming, cosmetic entitlement and UI

Naming appears only after primary ownership commits and current actor/binding checks pass. The companion interface shows only accessible dogs, relevant activity/handler/progress/needs/refusals and currently meaningful commands. An unavailable/busy dog does not get misleading opposing-state controls.

Cosmetic popup additionally requires server-held entitlement for the authenticated primary Steam principal and an approved available original model. Client SteamID/URL/model assertions are rejected. Original breed/appearance/seed are immutable; a cosmetic override cannot change genetics, scale, abilities, armor or ownership. No entitlement service/model download or production popup is implemented; models remain deferred.

Refusal labels and option tooltips require translation keys/all 29 explicit English fallbacks before runtime implementation. The [design index](contracts/database_redesign.json) reserves key proposals; these are not registered UI strings or new runtime options today.
