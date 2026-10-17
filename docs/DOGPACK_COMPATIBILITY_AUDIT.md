# DogPack compatibility audit

Evidence date: 2026-10-12. Source-supported integration assessment, not multiplayer proof.

[VERIFIED] Workshop `3796123931`; ID `CompanionDogsPack`; installed `modversion=0.9.3`; dependency `CompanionDogs`; metadata game minimum `42.18.0`. Root: `E:/Program Files (x86)/Steam/steamapps/workshop/content/108600/3796123931/mods/CompanionDogsPack/42/`.

Shared `CompanionDogsPack_Core.lua` declares data version 5 and a minimum/maximum CD version of 0.7.4. `compatibilityAudit` also checks required runtime interfaces. Its old 0.7.1 README is historical; current code and metadata determine compatibility. Exact hashes are in `../research/SOURCE_MANIFEST.json`.

## What it owns

[VERIFIED] DogPack owns deployed membership, roles, formation settings, leader selection, cohesion, some relationship/activity records, queues and travel recovery. Server modules separate roster, commands, movement, activity, travel and hook installation. Client modules supply HUD, pack UI and formation UI. Its configured deployment limit is bounded to one through four in the inspected shared implementation; default is three. The handoff's eventual larger packs are not an existing DogPack capacity guarantee.

Source references: `shared/CompanionDogsPack_Core.lua`; server `CompanionDogsPack_Server.lua`; server `CompanionDogsPack/ServerRoster.lua`, `ServerCommands.lua`, `ServerRuntime.lua`, `ServerMovement.lua`, `ServerTravel.lua`, `ServerActivity.lua`, `ServerHooks.lua`.

## Hook collision surface

[VERIFIED] Hook installation retains and wraps core functions including companion update, movement authority, carrying/stashing, combat capability/damage, sentinel radius and dismissal behavior. Role policy changes what an animal can do. Formation movement temporarily adjusts follow policy and client lease tuning. Multi-animal vehicle travel deliberately avoids the core singleton stash slot.

[INFERRED] Two overhauls independently wrapping these functions can produce order-dependent behavior, duplicated simulation or incorrect restore policy. Calling DogPack's internal install functions without its expected services is not a safe integration shortcut. Pinning versions catches some incompatibility, not callback-order or dedicated correctness.

## Integration contract proposed for B47ANCE

1. CD retains native entities and authoritative ownership. DogPack, when supported, remains the only deployed-roster/formation/travel writer.
2. B47ANCE owns individual learning, handler familiarity, private personality/discovery and task-specific eligibility. It requests existing deployment actions through a verified adapter instead of duplicating records.
3. B47ANCE pack relationships use persistent dog pairs, independent of transient roster slots. Merge/split/transfers must preserve identity and reconcile access.
4. Existing DogPack leader selection is operational formation leadership. The handoff's dynamic social/task influence is a separate concept; never relabel the selected leader as a biological alpha.
5. Group training commands expand to individually validated tasks. An untrained member receives a refusal/pending-training result rather than another dog's proficiency.
6. Exactly one movement producer per animal. If strict authority disables CD leases, DogPack formations must be tested on the remaining server path. No training task can silently acquire competing movement.
7. No DogPack: single active companion training and a read-only list of other owned dogs can continue. Multiple simultaneous task deployments remain unavailable until an original pack path is approved; optional dependency cannot become a hidden mandatory requirement.
8. Unsupported DogPack version: disable the pack adapter and affected pack commands with a readable reason; never corrupt/remove its records. Core incompatibility must block training actions that cannot be made safe.

## Feature assessment

| Feature | Classification | Reason / remaining evidence |
|---|---|---|
| Detect module/version and inspect deployed dogs | VERIFIED interface presence | Activation and load phase still need runtime proof |
| Read existing roster for independent UI | FEASIBLE | Original provider; no write ownership overlap |
| Individual learning/discovery per deployed dog | FEASIBLE domain logic | Identity/private persistence prerequisites apply |
| Group basic orders through existing DogPack commands | EXPERIMENTAL | Training eligibility must survive existing command/role paths |
| Dynamic relationship/task influence | FEASIBLE pure model; integration EXPERIMENTAL | Must not compete with DogPack leadership writer |
| Large packs beyond existing limit | EXPERIMENTAL | No verified extension for arbitrary deployment size; performance and transport |
| Coordinated corpse hauling | BLOCKED | No verified shared-load/corpse-physics authority path |
| Pack travel while training | EXPERIMENTAL | Atomic suspend/rebind/cancel across stash/RV/reconnect |
| Server-only movement with formations | EXPERIMENTAL | Existing lease coupling and fallback require dedicated spike |

## Dedicated test contract

G7 BLOCKED / NOT TESTED. Required scenarios: two owners and multiple deployed dogs; deploy/withdraw/dismiss last member; simultaneous roles and basic orders; loaded/unloaded member; carry and maturation; full vehicle seats and restore; RV entry/exit; disconnect during transition; no duplicate animal or UID; no stale training rewards; late join; dependency/version mismatch; Linux case-sensitive loading; bounded CPU/network sampling.

Installed optional context: PROJECT RV Interior `PROJECTRVInterior42`, Workshop `3543229299`, version 2.3; Visible Vehicle Coupling `VisibleVehicleCouplingB42`, Workshop `3807182783`, version 1.2. Their presence establishes neither dog-compatible compartments nor safe hauling. Their selected source/metadata are hashed; narrow evidence inspection found teleport/travel and coupling domains, not a verified multi-kennel or canine force API. No selected kennel-truck definition or supported canine ragdoll API was established.

SOURCE CODE COPIED: NO. IMPLEMENTATION DERIVED FROM REFERENCE: NO. Only original adapters to verified interfaces are proposed. No source patching, deployment or runtime test occurred.
