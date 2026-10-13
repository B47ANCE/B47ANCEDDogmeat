# Feature feasibility matrix

Evidence date: 2026-10-12. Every classification is about the proposed feature, not a runtime PASS.

VERIFIED = relevant behavior/interface exists in inspected source. FEASIBLE = an original implementation direction is established, but runtime is untested. EXPERIMENTAL = prototype/engine or integration investigation remains necessary. BLOCKED = no safe implementation path is established. A VERIFIED primitive does not upgrade a larger feature automatically.

References: CD = [Companion Dogs audit](COMPANION_DOGS_SOURCE_AUDIT.md); DP = [DogPack audit](DOGPACK_COMPATIBILITY_AUDIT.md); V = [vanilla audit](VANILLA_API_AUDIT.md); D93 = [drug audit](DRUGS_OF_93_COMPATIBILITY_AUDIT.md); A = [authority design](SERVER_AUTHORITY_DESIGN.md).

Shared gates: P private durable state; I native/CD persistent identity; C authoritative command/reward interception; M strict server movement; H single health writer; T transactional inventory/transport. These are unresolved integration gates, not new APIs. FEASIBLE domain/presentation work still waits for the corresponding gates before gameplay implementation.

## Features mapped to handoff sections

| ID | Handoff | Proposed feature | Classification | Source-supported direction / remaining gate |
|---|---|---|---|---|
| F01 | 1,25 | Dedicated authority/full MP compatibility | BLOCKED | CD client leases and unguarded legacy requests conflict; C/M/P/I and dedicated evidence required |
| F02 | 2 | Exact dependency/native identification and source hashes | VERIFIED | Current metadata, manifests and native binary inspection; activation still unknown |
| F03 | 3 | Identity through save/restart/reconnect/unload | EXPERIMENTAL | Native ModData + CD UID/recovery observed; I/P continuity and rollback spike |
| F04 | 3 | Identity through ownership transfer/transport/pack changes/death | EXPERIMENTAL | Explicit alias/lifecycle binding; no universal transfer event established |
| F05 | 3.1 | Breed/sex/age/weight generation | EXPERIMENTAL | Native/CD representations verified; native bounds, initialization order and recovery need I |
| F06 | 3.1 | Physical condition/strength/fitness/endurance potentials | FEASIBLE | Original private domain profile; no extra native attribute setter assumed; P/I prerequisites |
| F07 | 3.1 | Learning aptitude/intelligence | FEASIBLE | Original learning response model; P and balanced individual variability |
| F08 | 3.1 | Confidence separate from anxiety disposition/current anxiety | FEASIBLE | Original separate records and response functions; CD stress is not equivalent; P/C |
| F09 | 3.1 | Sociability/independence/handler attachment | FEASIBLE | Original relationship/behavior profile; P/I/C |
| F10 | 3.1 | Food/play motivation/prey drive/energy/noise sensitivity | FEASIBLE | Original reinforcement/sensitivity model; real outcomes need C/M; P |
| F11 | 3.1,4 | Prior experiences/training/possible working history | FEASIBLE | Server generation and per-handler discovery; no source location guarantees; P |
| F12 | 3.2 | Breed predispositions subordinate to personality | EXPERIMENTAL | CD computes capabilities/genes from breeds; policy integration C needed |
| F13 | 3.3 | Gradual socialization/trauma/rehabilitation/aging changes | EXPERIMENTAL | Original time/event model; actual trauma/success observations and H/C |
| F14 | 4 | Hidden untrained/partial/advanced/hunting/police/military/detection histories | FEASIBLE | Original probability profiles, no deterministic breed assignment; P |
| F15 | 4.1 | Discover skills by observation without gaining dog XP | EXPERIMENTAL | Per-handler projection path; prevent CD scan/UI/skills disclosure and reward bypass, C/P |
| F16 | 4.2 | Spoken/hand/whistle/vibration/previous cue recognition | EXPERIMENTAL | Original cue records; animation/signal/eligibility and C |
| F17 | 4.2 | Faster cue transfer for an already known behavior | FEASIBLE | Original learning logic; hidden behavior remains private; P/C |
| F18 | 5 | 28–56 day training target | EXPERIMENTAL | Calibration scenario, not an unlock timer; offline simulation plus actual game time/progression |
| F19 | 5.1 | Overall levels 0–10 without automatic command mastery | FEASIBLE | Derived summary of original command records; existing CD level gates need C |
| F20 | 5.2 | Cue/proficiency/duration/distance/distraction/generalization records | FEASIBLE | Private persistent per-command model; P/C |
| F21 | 5.2 | Reinforcement/handler familiarity/practice/known cue history | FEASIBLE | Server observations and original records; P/C |
| F22 | 5.3 | Rolling 24-game-hour structured/passive XP budgets | FEASIBLE | World age and bounded award ledger direction; P/C rollback/replay tests |
| F23 | 5.3 | Prevent command/idle/wall/reconnect/packet XP farming | EXPERIMENTAL | Real behavior, time and reward ownership must be validated through native/CD paths |
| F24 | 5.4 | Loose-leash/heel passive training while scavenging | EXPERIMENTAL | Native attachment and displacement observations; M/C |
| F25 | 5.4 | Calm during Mechanics/mat during Carpentry | EXPERIMENTAL | Verified timed-action domain; specific server-observable completion and settle location |
| F26 | 5.4 | Door waiting/building follow/successful recall/safehouse settling | EXPERIMENTAL | Native/CD navigation plus safehouse access; M/C; no proximity-only XP |
| F27 | 6 | Standard leash/long line/harness | EXPERIMENTAL | Native attachment exists; equipment semantics and leash length must coexist with M/T |
| F28 | 6 | Clicker/whistle/treat pouch/treats | FEASIBLE | Original items, conditioning and reinforcement records; native sound and item APIs; C/T |
| F29 | 6 | Toys/retrieval dummy/mat/target stick | FEASIBLE | Original item/task definitions; real retrieval/presentation remains M/T |
| F30 | 6 | Conditioned vibration/tone collar and sensitivity | EXPERIMENTAL | Non-punitive cue model feasible; equipment interaction/animation proof needed |
| F31 | 6 | No multiplier stacking; condition clickers | FEASIBLE | Single bounded reinforcement resolver; P/C |
| F32 | 6,20 | Audible devices/spoken cues attract zombies; silent cues remain silent | EXPERIMENTAL | Native addSound verified; cue timing, audio/attraction replication and calibration |
| F33 | 7 | Handling based on dog/player condition, weight and terrain | EXPERIMENTAL | Native attachment/stats exist; M and calibrated handling model |
| F34 | 7 | Pull player/interrupt movement/loss of balance | EXPERIMENTAL | No verified safe canine force/stumble path; physics/animation spike |
| F35 | 8 | Human Dog Training skill separate from canine skill | FEASIBLE | Native CustomPerks loader and Lua exposure verified; dedicated/save test required |
| F36 | 8 | Reading behavior/prior training and specialized-handler knowledge | FEASIBLE | Separate original knowledge/discovery model; P/C |
| F37 | 8.1 | Dog Trainer and K9 Handler occupations | EXPERIMENTAL | Native profession definition path verified; registry/load/cost and mod interaction |
| F38 | 8.2 | Training books 1–5/behavior/leash manuals | FEASIBLE | Native reading/SkillBook and original item path; custom perk binding |
| F39 | 8.2 | Detection/hunting/police/military/veterinary manuals | FEASIBLE | Original knowledge items; appropriate original distributions; no automatic occupation mastery |
| F40 | 8.2 | Obedience VHS | EXPERIMENTAL | Native recorded media registration verified; custom XP/knowledge code route unresolved |
| F41 | 9 | Veterinary interface inspired by human health UI | FEASIBLE | Independent ISUI panel, own dog-region diagram/projections; no human body substitution |
| F42 | 9.1 | Head/neck/torso/abdomen/legs/paws/tail injury regions | EXPERIMENTAL | Custom records/panel feasible; regional native damage attribution H not established |
| F43 | 9.2 | Scratches/lacerations/bites/bleeding/infection/fractures/sprains/pain | EXPERIMENTAL | CD has related conditions; unified condition/damage ownership H required |
| F44 | 9.2 | Dehydration/malnutrition/fatigue/temperature exposure | EXPERIMENTAL | Native/CD needs exist; extend one writer with calibrated welfare |
| F45 | 9.2 | Parasites/skin irritation/coat matting/age mobility | EXPERIMENTAL | Existing CD parasites/age; new original condition model H and coat-specific evidence |
| F46 | 9.2 | Canine medical suitability | BLOCKED | Human medicine/DO93 effects are not canine suitability evidence; separate veterinary review |
| F47 | 9.3 | Brushing/bathing/drying/coat inspection/mat removal | EXPERIMENTAL | Original timed care; CD bath exists; coat rules H/C/T and animation |
| F48 | 9.3 | Parasite treatment/paw inspection/general hygiene | EXPERIMENTAL | CD/native care primitives; no duplicate disease timers; H |
| F49 | 9.3 | Only specifically modeled zoonotic transmission | BLOCKED | No disease-specific canine-to-player evidence/model established |
| F50 | 9.4 | Injured/neglected stray generation and months-long rehabilitation | EXPERIMENTAL | Native/CD generation and condition lifecycle; H/P, balance over time |
| F51 | 10 | Optional exposure/incubation/symptoms/terminal Knox illness | EXPERIMENTAL | Original alternate-lore server model; H/P, conservative default disabled |
| F52 | 10 | Hostile canine reanimation attacking players/dogs/NPCs | BLOCKED | No verified native canine zombie entity/attack/sync path; retain history, revoke commands |
| F53 | 11 | Canine fitness/endurance/running/strength/agility skills | EXPERIMENTAL | Original activity records; native physical limits/movement not proven |
| F54 | 11 | Obedience/stealth/impulse control/pack coordination | FEASIBLE | Original behavior proficiency model; C/M/DP gates for actual behavior |
| F55 | 11 | Scent/tracking/search/discrimination skills | EXPERIMENTAL | CD scent and native tracks exist; real bounded server observations needed |
| F56 | 11 | Retrieval/hauling/guarding/hunting/foraging/fishing/herding/assistance | EXPERIMENTAL | Partial CD capabilities; each actual task separately gated below |
| F57 | 11 | Comfort as welfare; age/size/health/fatigue capability limits | FEASIBLE | Original capability resolver; H and calibrated physiological constraints |
| F58 | 12 | Modular learned odor registry | FEASIBLE | Original target registrations using verified public identifiers; not automatic categories |
| F59 | 12 | Narcotics targets through optional DO93 adapter | FEASIBLE | D93 FullType/tag inventory; odor validity/accessibility still EXPERIMENTAL |
| F60 | 12 | Gunpowder/ammunition/specific object scent | EXPERIMENTAL | Need explicit scent-bearing FullTypes and trained odor contract |
| F61 | 12 | Wildlife/people tracking scent | EXPERIMENTAL | Native real animal tracks available; human scent persistence/search path not established |
| F62 | 12.1 | Staged introduction/discrimination/false alerts/indication/proofing | FEASIBLE | Original server training model; actual target observation C/M/P |
| F63 | 12.1 | Environmental scent effects | EXPERIMENTAL | No proven odor plume/occlusion model; weather input alone is insufficient |
| F64 | 13 | Locate downed game/retrieve suitable small prey | EXPERIMENTAL | Existing CD hunting/delivery; training gating, task claims and T |
| F65 | 13 | Natural-resource indication/designated search areas | EXPERIMENTAL | Foraging domain exists; actual server knowledge/permission boundary |
| F66 | 13 | Locate dropped fishing equipment | FEASIBLE | Ordinary trained-item search when actually accessible; C/M/T |
| F67 | 13 | Floating retrieval/fishing assistance beyond dropped items | EXPERIMENTAL | Water movement/item reach and injury/sync unresolved; no hidden fish knowledge |
| F68 | 14 | Lightweight carrying/appropriate saddlebag transport | VERIFIED existing CD primitive | Training/capacity rules require an original adapter and T |
| F69 | 14 | Designated-item retrieval/drop zones/familiar-player delivery | EXPERIMENTAL | Existing CD retrieval differs from strict real-item transfer; M/C/T |
| F70 | 14.1 | Deposit into open basket/crate/reachable open trunk | EXPERIMENTAL | Native container access/capacity APIs; real path/open state/permissions and T |
| F71 | 15 | Drag bags/backpacks/small loads | EXPERIMENTAL | No validated constrained-drag/animation/collision transaction yet |
| F72 | 15 | True ragdoll dragging/cooperative multi-dog loads | BLOCKED | No verified exposed physics/ownership path; do not claim cosmetic movement is physics |
| F73 | 15.1 | Corpse zone collection/destination/individual claims | EXPERIMENTAL | Logical server task claims feasible; safe corpse movement remains unresolved |
| F74 | 15.1 | Corpse contamination/injury restrictions | EXPERIMENTAL | Original condition model requires H and disease-specific design |
| F75 | 16 | Zombie attraction/redirection/escape/recall/disengagement | EXPERIMENTAL | addSound + CD navigation primitives; density/collision/ownership proof needed |
| F76 | 17 | Squeaky toys/audible and remote lures/deliver-retreat tasks | EXPERIMENTAL | Sound and items exist; deployment activation/safe retreat C/M/T |
| F77 | 17 | Toy launcher/compatible thrown objects | EXPERIMENTAL | Need actual projectile/landing/item identity and server trajectory APIs |
| F78 | 17 | Optional explosive projectile interoperability | BLOCKED | No selected dependency/interface audited; armed-explosive dog transport excluded |
| F79 | 18 | Affiliation/familiarity/cooperation/tension/resources/preference/influence | FEASIBLE | Original bounded pair relationships; P/I and DP ownership boundary |
| F80 | 18.1 | Dynamic task leadership/uncommon disputes | EXPERIMENTAL | Model feasible; interaction with DP selectable operational leader and real behavior |
| F81 | 18.2 | Follow/stay/search/guard/recall/disengage group orders | EXPERIMENTAL | DP commands exist; independently validated proficiency C/M |
| F82 | 18.2 | Return home/retrieve/haul/clear bodies group tasks | EXPERIMENTAL | New task arbitration; individual capability, home ACL, M/T; dragging gates retained |
| F83 | 19 | Paw icon, expandable vertical list, hover/pinned panels | FEASIBLE | Independent ISUI provider and filtered snapshots; no gameplay rendering dependency |
| F84 | 19.1 | Overview/health/training/skills/behavior/welfare/equipment/relationships/tasks | FEASIBLE | Independent discovered-state tabs, read adapters; P projection policy |
| F85 | 19.2 | UI scaling/controller/tooltips/state-aware menu/failure explanations | FEASIBLE | Native ISUI/radial/menu support; device/resolution tests remain mandatory |
| F86 | 20 | Hold radial/F-key configurable bindings/no overwrite | FEASIBLE | Native radial and keybinding surfaces; coordinate CD emote/binding hooks |
| F87 | 20 | Sit/down/stay/heel/recall/place/release | EXPERIMENTAL | Stay/recall primitives exist; distinct reliable behaviors and cue gates C/M/animation |
| F88 | 20.1 | Overhead named speech and vanilla vocalization | EXPERIMENTAL | Existing shout route; exact text/audio/cue replication and conflict verification |
| F89 | 21 | Home/safehouse eat/drink/rest/sleep/stress recovery/social settle | EXPERIMENTAL | CD feed/rest/care and SafeHouse permission candidates; H/M/T, no instant reset |
| F90 | 22 | Probabilistic residential/rural/police/military/shelter/POI spawns | EXPERIMENTAL | CD spawn registries verified; override-versus-addition, decision keys and sandbox schema |
| F91 | 22 | Additional breeds such as French Bulldog | BLOCKED current assets | Not found in audited installed CD set; new original/licensed assets and native registration needed |
| F92 | 23 | Catch poles/portable kennels/crates/harness/protective gear | EXPERIMENTAL | Humane restraint/equipment concept; authority, animation and welfare contracts unresolved |
| F93 | 23.1 | 8–10 compartment kennel truck with size/comfort/ventilation/identity | BLOCKED | No selected verified vehicle definition/compartment API; native trailer only |
| F94 | 23.2 | Optional zombie pole restraint/escape/grapple | BLOCKED | No verified safe collision/targeting/server attack interaction |
| F95 | 24 | UI manual/in-world handbook/tooltips/first-time guidance/troubleshooting | FEASIBLE | Original localized ISUI/book content; document implemented capability only |
| F96 | 25.1 | Invalid/stale/unauthorized/replayed/conflicting request rejection | FEASIBLE own protocol | Native transport verified; protect all affected legacy paths through C before gameplay |
| F97 | 25.2 | Schema migrations/restart/backup/unknown data preservation | EXPERIMENTAL | Private durable store P and CD lifecycle I not yet proven |
| F98 | 26 | Grouped server-authoritative sandbox options/localization/save policy | FEASIBLE | Vanilla sandbox/CD use verified; proposed configuration assessment in A |
| F99 | 27 | Bounded milestones and optional advanced feature gates | FEASIBLE planning | Concrete dependency order in implementation plan; no gameplay started |
| F100 | 28,29 | Dedicated/multi-client/performance/regression/Linux validation | BLOCKED execution | No runtime authorization/evidence; concrete scenarios specified, offline checks do not PASS G7 |
| F101 | 30 | Seven Milestone 0 technical documents only | VERIFIED deliverable scope | Documentation/research, not playable mod or release |

## Scope decisions

No client authority fallback. No supernatural target knowledge, instant rehabilitation, rigid alpha model, inherited advanced group proficiency, canine human-body/dosing substitution or armed-explosive transport. Conservative optional systems remain disabled until their native capability passes.

The verified existing primitive set is intentionally smaller than the complete vision. A source-supported standalone record model does not resolve private-save durability or third-party policy interception. The first playable slice cannot responsibly include health overhaul, dragging, zombification or large packs.

No project source or upstream assets have been implemented from these classifications. G6 NOT TESTED; G7 BLOCKED / NOT TESTED; G8 BLOCKED. Experimental/blocked rows have a specific remaining gate; none is relabelled a PASS merely because a related native class exists.
