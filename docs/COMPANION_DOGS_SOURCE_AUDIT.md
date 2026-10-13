# Companion Dogs source audit

Evidence date: 2026-10-12. Milestone 0 only. Source inspection is not runtime validation.

## Baseline and source scope

[VERIFIED] Workshop `3740052292`; technical ID `CompanionDogs`; `modversion=0.7.4`; `versionMin=42.18.0`. Root: `E:/Program Files (x86)/Steam/steamapps/workshop/content/108600/3740052292/mods/CompanionDogs/42/`. Its shared `CompanionDogs/Boot.lua` reports build 0.7.4 dated 2026-09-04; `skills/BreedAPI.lua` declares API 11. These are dependency versions, not this project's version.

The prior full family audit is preserved in `../research/CD_BACKEND_AUDIT_2026-10-12.md`; its file baseline contains 1,330 installed files across twelve Workshop items. Current source hashes/metadata are in `../research/SOURCE_MANIFEST.json`. Neither an installed file nor a declared dependency establishes activation in a save/server.

Source aliases: CD = the root above; L = `CD/media/lua/`. All references below are under L unless specified. No third-party implementation, balances, assets or persistence schemas are adopted. Public interface identifiers may be referenced for original interoperability. SOURCE CODE COPIED: NO. IMPLEMENTATION DERIVED FROM REFERENCE: NO.

## Subsystem map and preservation contract

| Surface | Source evidence | Existing behavior to preserve | Extension assessment |
|---|---|---|---|
| Construction | `shared/Definitions/animal/DogDefinitions.lua`; shared `kennel/Registry.lua:spawnDog` | Native IsoAnimal, adult/young types, age initialization, failed-spawn cleanup | VERIFIED native construction; do not replace entities |
| Breed registry | `shared/skills/Skills.lua`; `skills/BreedAPI.lua:registerBreed`; `skills/Species.lua` | Five core dogs, added breed/species recognition, voices and capability gates | VERIFIED public registration; existing breed rewriting is not a documented contract |
| Age/weight | Native AnimalData access; native Animal UI; CD growth/respawn records | Native age/weight and maturation | Read access VERIFIED; dog-specific load/weight calibration EXPERIMENTAL |
| Individual traits | `skills/Skills.lua:rollBreedGenes`; `skills/Lineage.lua`; `core/Mood.lua`, `State.lua` | Existing genetics, stress, loyalty and lineage | Independent confidence/anxiety records FEASIBLE; overriding breed-derived behavior EXPERIMENTAL |
| Skills/obedience | `skills/Skills.lua`, `Tricks.lua`; `CompanionDogs_Skills.lua` | Existing skill XP, obedience gates and tricks | New command-learning model FEASIBLE in isolation; authoritative replacement of every CD reward path EXPERIMENTAL |
| AI/commands | server `CompanionDogs_Companion.lua`, `CompanionDogs_Commands.lua`; server `systems/` | Follow/stay/guard, refusal, combat, hunting, feeding and care | Read/request interfaces exist; no general per-command policy middleware verified |
| Movement | server `Follow.lua`, `FollowStream.lua`, `NetAuthority.lua`, `FenceHop.lua`, `FallGuard.lua`; client movement code | Native pathfinding, steering, streaming and travel safeguards | Do not introduce competing per-tick movement; strict authority adapter EXPERIMENTAL |
| Ownership | shared `core/State.lua:ownerKey,isOwnedBy`; `Identity.lua`; server `Presence.lua` | Owner identity separate from transient network ID | Ownership read VERIFIED; delegated handlers/transfer lifecycle EXPERIMENTAL |
| Inventory | shared `bag/Bag.lua`, `bag/Items.lua`; server equip/bag commands | Cargo capacity, item properties, native inventory synchronization | Existing cargo VERIFIED; arbitrary container delivery EXPERIMENTAL |
| Health | server `Vet.lua`, `Upkeep.lua`, `GunGuard.lua`, `Fire.lua`; shared vet config | Existing ailments, care, needs, protective invincibility and optional death | Health read/model UI FEASIBLE; unified new injury writer EXPERIMENTAL |
| Breeding | server `CompanionDogs_Breeding.lua`; `Stash.lua`; shared lineage | Species-safe reproduction and young maturation | Preserve; identity binding on object replacement needs lifecycle proof |
| Save/load | shared `kennel/Kennel.lua`; server `CompanionDogs_Kennel.lua`, `Stash.lua`, `Presence.lua` | Snapshot, offline, carry/trailer recovery and canonical clone selection | Existing recovery VERIFIED; addon state survival not automatic |
| Pack | base active selection; optional DogPack | Base ownership and DogPack deployed roster | See separate audit; no second roster writer |
| UI | client `CompanionDogs_StatusUI.lua`, `ContextMenu.lua`, `RadialCommands.lua`, `Keybinds.lua` | Existing status/care/bag/kennel controls and bindings | Independent panel/radial FEASIBLE; universal tab/action registration not verified |
| Sounds/animation | breed voices; server animation code; native assets | Breed rigs, rest/sit/hit and care animations, localized notifications | Use native controls/public voice interface; new unique clips EXPERIMENTAL |
| Vehicle/RV | server stash/carry/recovery; client RV integration; optional DogPack travel | Single active stash and pack multi-animal travel | Preserve; no duplicate vehicle or inventory representation |

## Public seams versus internal interception

[VERIFIED] `registerBreed`, `registerSpecies`, `registerBuildingClass`, `registerStraySpawns` and `registerVoices` exist. The explicitly declared callback arrays `onHuntDelivered` and `onUpkeepStress` permit narrow original consumers. Registration existence is not a promise that every field or existing definition can be changed safely. No installed modding manual beyond source/API comments was found.

[VERIFIED] `CD.request`/`CD.sendAs` send actions, and `CD.Server` contains handlers. An accessible function is not automatically a supported authorization/filter extension. The request dispatcher invokes the selected handler directly. Overriding the client request helper would not protect the server against a custom client.

[UNKNOWN] A general official hook for “before any command”, “before any skill XP”, “animal replaced”, “owner transferred”, or “before every medical mutation” was not established. These gaps make a full training/health overhaul more invasive than a new breed add-on.

Recommended scope: an original server domain model plus read adapters and verified native/public callback use. Only after a contract spike may a version-pinned, narrowly scoped server interceptor be proposed. Every interceptor must have one installation path, detectable conflicts, original-call behavior and explicit fallback; do not globally redefine vanilla pathfinding or CD command tables wholesale.

## Authority conflicts relevant to this project

[VERIFIED] Main simulation is gated away from ordinary multiplayer client execution. However core follow movement defaults to a server-granted client position lease (`config/Motion.lua`, server `NetAuthority.lua`). Its reports are bounded, but they are positions, not solely intent. Strict dedicated authority therefore needs a proven server-driven path with leases disabled/revoked and no hidden re-enabling through tuning or another add-on.

[VERIFIED] CD server-side feeding does not require a valid Food reference in all paths and uses bounded client-reported nutrition. Physical care does not consistently establish actor range/duration. Zombie kill acknowledgments are not tied to the requesting recipient. These inherited entry points cannot be secured by hiding UI controls.

[VERIFIED] Existing CD skills/genes and its own snapshots are visible through synchronized ModData and scanning/status paths. B47ANCE hidden history cannot be placed in CD's public records. Prior training must not be reflected into CD skill levels before disclosure if that exposes it through existing UI/data inspection. A public derived level may be produced only under an explicit discovery policy.

[VERIFIED] CD snapshot restoration selectively preserves CD data; native object reconstruction can lose independent addon ModData. Bind an original record by a persistent dependency identity only after proving that UID survives carry, maturation, transfer and recovery. Do not rely on network IDs, names or owner-scoped tokens as universal identity.

## Dog-only scope

The original project extends canine behavior. CD also recognizes registered cats/rats. [VERIFIED] Species discrimination exists. Proposed adapters must explicitly select dog species and supported breeds, preserving cats/rats and unrelated animals. A registry function named “dog” is not sufficient canine discrimination. Mixed-breed predispositions should use capabilities and individual variation, never a guarantee of expertise from a breed/location/equipment label.

## Decision

Individual record/training logic and independent presentation have established implementation directions. Full behavior replacement is EXPERIMENTAL. A safe complete authority/lifecycle model is not yet established: affected gameplay implementation is BLOCKED at the design gate until the authority, privacy and lifecycle spikes pass. Existing CD recovery, cargo, rendering, breeding and veterinary behavior remain dependency-owned.

G6 NOT TESTED; G7 BLOCKED / NOT TESTED. The next independent verification is native/CD dedicated testing with two clients, ordinary/custom requests, authority handoff, carry, maturation, owner transfer and reconnect. No dependency files were modified.
