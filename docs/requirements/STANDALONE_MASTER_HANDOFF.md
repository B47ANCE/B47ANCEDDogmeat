# B47ANCE'd Dog Training — Authoritative Standalone Codex Master Specification

**Project version:** `0.1.0-dev.1` (preserve canonical `VERSION`)  
**Technical Mod ID:** `B47ANCEDDogTraining` (proposed, not finalized)  
**Target:** Project Zomboid Build 42.21; revalidate on future builds  
**Architecture:** **STANDALONE ORIGINAL DOG MOD** — no Companion Dogs or DogPack dependency  
**Priority:** Headless dedicated-server-first; multiplayer, persistence, and Linux compatibility  
**Document role:** Supersedes the dependency-based `USER_HANDOFF.md` for future design; historical reports stay unchanged.  
**Status:** Requirements and research authorization; no gameplay, runtime success, deployment, packaging, or publication implied.

## Authority and precedence

1. The user's latest decision is definitive: this is **not** an add-on to Companion Dogs. Never create dependency or integration assumptions from older audits.
2. Preserve the **gameplay intentions** in the historical handoff, but replace all dependency-specific implementation with original, native-first design.
3. Existing source audits are evidence only for the exact inspected versions, environment, and APIs. Their Companion Dogs-specific R1–R6 blockers do **not** automatically apply to the standalone implementation; corresponding native capabilities still need proof.
4. The installed Build 42.21 client has a loose modified `IsoAnimal.class` that differs from the packaged class; determine effective runtime class on client **and dedicated server**, and validate against a pristine install before claiming vanilla support.
5. Never invent native hooks, animation states, dog rigs, movement authority, zombie traversal, or network semantics. Source evidence is not runtime proof.
6. Treat all named mechanics below as **design requirements**; where technically unproven, mark EXPERIMENTAL/BLOCKED and do not fake them with teleportation, item duplication, or client-authoritative outcomes.
7. Keep one authoritative root `VERSION`, independent persistence schema and network protocol versions, and the existing version inventory/checker policy. Do not rewrite historical validation.

## Definition of done

A feature is not DONE until source capability, standalone implementation, offline tests, actual client behavior, two-client dedicated MP, restart/reconnect/unload, and headless Linux are documented as appropriate. Distinguish VERIFIED (source), FEASIBLE (design), EXPERIMENTAL (requires spike), BLOCKED (no safe path), and runtime PASS/FAIL/NOT TESTED.

---
# 1. STANDALONE NATIVE ANIMAL FOUNDATION

## 1.1 Core dependency policy

The only mandatory gameplay foundation is Project Zomboid Build 42. The mod must provide its own dog species/entity definitions, spawn and population policy, AI, navigation/task arbitration, obedience and working skills, health/welfare extensions, pack roster, handler permissions, UI, equipment, and save/network state. Reuse **verified native** animal APIs, models/rig interfaces, inventory, sounds, pathfinding, vehicle actions, and world objects when safe. Do not duplicate vanilla animals or replace game classes. Companion Dogs and Companion Dogs: DogPack are **not** required, do not own any data, and do not supply runtime code/assets. Future optional co-installation investigation is separate, not a milestone prerequisite.

## 1.2 Mandatory native proof inventory

Audit the **effective** native Build 42.21 implementation of `IsoAnimal`, `AnimalData`, animal species/definition registration, `addAnimal`, native AI and navigation, movement synchronization, pathfinding, collisions, animation rig and asset registration, animal carrying/growth/death, world spawn, item/vehicle representations, save/load and world chunk lifecycle. Record exact Lua-facing signatures, actual call sites, native class precedence, class/source hashes, and server versus client execution. Compare packaged versus loose `IsoAnimal.class`; inspect additional JARs/agents only insofar as they change the effective animal contract. Do not assume the local modified environment represents pristine vanilla.

## 1.3 Original dog construction

Define the smallest dog entity that can be spawned once, named, moved, observed by two clients, saved, unloaded, reloaded, transported and recovered without duplicate entity creation. Prefer native species and animal creation mechanisms when proved. If the engine cannot support an independent canine rig/model or dedicated movement, produce a blocker and smallest isolated prototype plan, not a client-only fake animal.

## 1.4 Original domain boundaries

- **Native engine:** entity lifetime, physical world presence, collision, supported movement and animation, native item/vehicle interfaces.
- **B47ANCE server domain:** permanent dog ID, original private history/personality, handler ACLs, command knowledge and rewards, welfare/housebreaking, task arbitration, pack relationships, scent registry, doggy door/waste records.
- **Clients:** visible animations, overhead cues, radial/sidebar/health UI, local input, server-approved projections and effects; never authoritative success.
- **Optional adapters:** verified external item identifiers only (e.g. Drugs of '93), explicitly off when dependency absent; never mandatory.

# 2. SERVER-FIRST ENGINEERING CONTRACT

## 2.1 Dog identity and save contract

Allocate a world-scoped, durable, unique dog ID once. Bind it to current native entity/UID and generation; never use network ID, display name, owner name or chunk address as the permanent identity. Re-resolve before every action commit. Explicitly test spawn, carry, release, trailer, vehicle/RV, growth, chunk unload, handler transfer, death, reconnect, restart, and backup rollback. Ambiguous or duplicate bindings are quarantined, not silently respawned. Historical relationships remain attached to the dog after ownership changes, but access permissions are recalculated.

## 2.2 Private storage and projection

Keep undiscovered histories, precise traits, prior cue knowledge, sensitive medical findings and server-side rewards out of client-synchronized animal/player ModData and publicly requestable named global ModData. Audit and prove a world-scoped private server persistence mechanism (native file writer is a candidate, not proof). Persist schema, world ID, monotonic generation, integrity/backup metadata, atomic or recoverable writes, migrations and corruption quarantine. Send **allowlisted** per-handler projections, not complete records with fields removed. Reject unauthorized requests; clear stale projections after ownership change.

## 2.3 Network command protocol

Every client request supplies a bounded action, opaque dog reference, parameters and deduplication token. Server derives the actor from the authenticated callback and validates permissions, proximity/floor, state, cue familiarity, equipment, actual item identity/quantity, stamina, distraction, revision, task lease and timing. Server observes outcomes; clients cannot report XP, elapsed practice, movement success, health, damage, nutrition, identity or item transfer results. Separate rate limits from idempotence. Persist action receipts for restart-sensitive transactions. Reject replay, stale handles, unauthorized commands and contradictory tasks.

## 2.4 One simulation writer

For each dog, exactly one authoritative movement/task owner. Implement priority and interruption: immediate danger > injury/care > controlled handler commands > work > biological needs > rest/social idle, subject to realistic emergency exceptions. Avoid client position leases and duplicate per-tick controllers. Prove native server movement, pathfinding and collision under headless MP. A dog blocked by geometry must fail or replan, never teleport through a solid object.

## 2.5 Health and inventory authority

One server writer for dog health/needs. Do not apply human BodyDamage anatomy or human drug dosage. Inventory and hauling require permission, reachability, capacity, weight, unique item/corpse claims, and exactly-once server commits. Reconcile after disconnect, chunk unload, crash and restart. Never create an item in the destination before valid removal/commit from source.

## 2.6 Performance and compatibility

Bound AI update budgets, scent queries, pathfinding requests, world-waste objects, zombie-door evaluations, and network traffic. No global per-tick scans or uncontrolled population growth. Preserve vanilla UI and keybindings unless the user explicitly changes them. Support Linux path case sensitivity, headless server without UI/render dependencies, disabled optional adapters, and clean failure when native capability is absent.

---
# 3. INDIVIDUAL DOG IDENTITY AND GENERATION

Every dog must receive a persistent server-generated identity.

The identity must survive:

- World saves.
- Server restarts.
- Client reconnects.
- Dog ownership transfers.
- Dog transport.
- World unloading and reloading.
- Pack membership changes.
- Injury, death, and optional zombification.

Avoid generating duplicate identities.

## 3.1 Randomized starting attributes

Generate individual values for:

- Breed.
- Age.
- Sex, where supported.
- Weight.
- Physical condition.
- Strength potential.
- Fitness potential.
- Endurance potential.
- Intelligence/learning aptitude.
- Confidence.
- Anxiety disposition.
- Current anxiety.
- Sociability.
- Independence.
- Food motivation.
- Play motivation.
- Prey drive.
- Energy requirements.
- Noise sensitivity.
- Handler attachment tendency.
- Existing training.
- Previous experiences.
- Possible working-dog history.

These values must not all be exposed immediately to the player.

## 3.2 Breed and personality separation

Breed traits represent relatively stable physical characteristics and predispositions.

Personality traits represent individual behavioral characteristics.

Personality must take precedence over breed stereotypes when resolving behavior.

Example:

An adult Cane Corso may have high confidence and low anxiety.

A young German Shepherd may have low confidence and high anxiety.

Both are valid outcomes.

Breed traits must not automatically guarantee confidence, intelligence, obedience, or working ability.

## 3.3 Personality development

Personality can gradually change through:

- Positive training.
- Environmental exposure.
- Trauma.
- Rehabilitation.
- Handler relationships.
- Neglect.
- Socialization.
- Aging.
- Repeated successful experiences.

Breed predispositions remain stable, although physical capabilities may change with age or health.

Avoid instant personality transformations.

---

# 4. HIDDEN PREVIOUS TRAINING

Dogs must spawn with randomized existing obedience and specialized knowledge.

A newly discovered dog may be:

- Completely untrained.
- Partially trained.
- Well-trained.
- Previously trained for hunting.
- Previously trained for police work.
- Previously trained for military work.
- Previously trained for scent detection.
- Exceptionally experienced.

Previous training is not guaranteed by breed or spawn location.

## 4.1 Discovery mechanics

The player must discover existing training through observation and interaction.

Examples:

- A dog naturally walks in heel position.
- A dog responds to an unfamiliar hand signal.
- A dog performs a trained alert behavior.
- A dog retrieves an item without instruction.
- A dog responds to a whistle.
- A dog demonstrates previous scent-detection training.

Existing skills remain hidden until reasonably identified.

Discovering a skill must not award new dog XP.

## 4.2 Previous cue differences

Dogs may recognize:

- Spoken commands.
- Hand signals.
- Whistles.
- Conditioned vibration cues.
- Other previously learned signals.

A dog may know a behavior without recognizing the new handler's preferred cue.

Teaching a new cue for an already learned behavior should be faster than teaching the behavior from scratch.

---

# 5. TRAINING PROGRESSION

Target complete training time:

**28–56 in-game days under regular, effective training conditions.**

This is a balancing target, not an automatic unlock timer.

Starting experience, anxiety, personality, care quality, breed tendencies, and handler knowledge affect progression.

Previously trained dogs may require less time to reach practical reliability.

## 5.1 Dog obedience levels

| Level | General capability |
|---|---|
| 0 | No confirmed obedience |
| 1 | Name recognition, leash introduction |
| 2 | Sit, Down |
| 3 | Heel and leash manners |
| 4 | Recall and Stay |
| 5 | Place and foundational obedience |
| 6 | Directed movement and basic retrieval |
| 7 | Advanced retrieval and search |
| 8 | Silent alerting and specialized work |
| 9 | Guarding, remote tasks, complex distractions |
| 10 | Advanced working companion |

These are progression guidelines.

Individual commands require independent learning and proofing. A dog's overall level must not instantly unlock mastery of every command.

## 5.2 Individual command records

Track:

- Cue association.
- Execution proficiency.
- Duration.
- Distance.
- Distraction tolerance.
- Environmental generalization.
- Reinforcement history.
- Handler familiarity.
- Last successful practice.
- Known cue types.

## 5.3 Daily XP cap

Implement a server-authoritative rolling 24-in-game-hour XP budget.

Separate:

- Structured training.
- Passive training.

Prevent:

- Repeated command spam.
- Idle XP farming.
- Wall-walking exploits.
- Duplicate reward packets.
- XP duplication after reconnects.
- Client-authored XP modifications.

Provide sandbox multipliers.

## 5.4 Passive training

Award small, meaningful XP for successful behavior during normal gameplay.

Examples:

- Loose-leash walking while scavenging.
- Remaining calm while the player works on Mechanics.
- Staying on a mat during Carpentry.
- Waiting at doors.
- Following appropriately through buildings.
- Returning when recalled.
- Settling quietly inside a safehouse.

Passive XP must be earned through verified behavior, not simply by remaining near the player.

---

# 6. POSITIVE-REINFORCEMENT EQUIPMENT

Implement original training equipment using native item systems where supported:

- Standard leash.
- Long training line.
- Harness.
- Clicker.
- Whistle.
- Treat pouch.
- Training treats.
- Toys.
- Retrieval dummy.
- Training mat.
- Target stick.
- Vibration collar.
- Tone collar.

Equipment should affect cue consistency, reinforcement timing, and training effectiveness.

Avoid unlimited XP multiplier stacking.

Clickers must be conditioned before they provide their full benefit.

Vibration collars must function as conditioned, non-punitive tactile cues. Model individual sensitivity; vibration is not automatically comfortable or effective.

Audible training devices must interact with zombie sound attraction through verified game APIs.

Silent devices must not generate fictional audible sound events.

---

# 7. LEASH AND PHYSICAL HANDLING

Leashes must have meaningful gameplay consequences.

Handling difficulty depends on:

- Dog weight.
- Dog strength.
- Dog acceleration.
- Training.
- Anxiety and arousal.
- Player Strength.
- Player Fitness.
- Player exhaustion.
- Terrain.
- Leash or harness equipment.

Large, untrained dogs may pull the player, interrupt movement, or cause loss of balance.

Well-trained dogs should be easier to handle.

A leash is especially important for newly discovered dogs.

Do not implement unrealistic force calculations without validation.

Use a gameplay model calibrated through testing.

---

# 8. HUMAN DOG TRAINING SKILL

Add a survivor Dog Training skill if technically feasible.

This skill represents the player's ability to:

- Interpret canine behavior.
- Recognize previous training.
- Deliver reinforcement correctly.
- Teach commands.
- Manage anxiety.
- Handle difficult dogs.
- Identify specialized working-dog behavior.

The human skill is separate from the dog's obedience and individual working skills.

A novice handler may discover an advanced working dog without knowing how to use its existing abilities.

## 8.1 Occupations

Proposed occupations:

**Dog Trainer**
- General obedience knowledge.
- Positive-reinforcement expertise.
- Improved canine handling.
- Better understanding of stress and behavior.

**K9 Handler**
- Specialized working-dog knowledge.
- Familiarity with police canine procedures.
- More advanced detection and handling knowledge.

Occupation bonuses must be balanced against vanilla occupation costs and existing modded occupations.

## 8.2 Books, magazines, and VHS

Proposed educational items:

- Dog Training Volumes 1–5.
- Canine Behavior Manual.
- Obedience Training VHS.
- Leash Handling Guide.
- Scent Detection Handbook.
- Hunting Dog Field Guide.
- Police K9 Operations Manual.
- Military Working Dog Manual.
- Veterinary Behavior Reference.

General dog trainers must not automatically understand specialized military or police procedures.

Specialized manuals should spawn in appropriate locations with randomized rarity.

---

# 9. CANINE HEALTH AND VETERINARY CARE

Create a readable veterinary interface inspired by the player's existing health panel.

Audit the vanilla health UI before selecting an implementation approach.

## 9.1 Body regions

Proposed regions:

- Head.
- Neck.
- Torso.
- Abdomen.
- Front legs.
- Rear legs.
- Paws.
- Tail.

Track region-specific injuries where technically supported.

## 9.2 Medical conditions

Support:

- Scratches.
- Lacerations.
- Bites.
- Bleeding.
- Fractures.
- Sprains.
- Pain.
- Wound infection.
- Dehydration.
- Malnutrition.
- Fatigue.
- Temperature exposure.
- Parasites.
- Skin irritation.
- Coat matting.
- Age-related mobility decline.

Do not automatically apply human medicine rules to dogs.

Medical treatments must have validated canine suitability.

## 9.3 Grooming

Add:

- Brushing.
- Bathing.
- Drying.
- Coat inspection.
- Mat removal.
- Parasite treatment.
- Paw inspection.
- General hygiene care.

Grooming needs depend on coat type, environment, health, and individual condition.

Neglect can reduce comfort and contribute to appropriate medical complications.

Only specifically modeled zoonotic diseases or parasites should transmit to players.

## 9.4 Rehabilitation

Stray dogs can spawn injured, malnourished, dirty, anxious, or otherwise neglected.

Recovery should take realistic amounts of time.

Severe rehabilitation may require months of in-game care.

Do not instantly restore all conditions through one interaction.

---

# 10. OPTIONAL CANINE ZOMBIE INFECTION

Add a configurable alternate-lore system allowing dogs to contract the Knox infection.

Default enablement must be a sandbox decision, with a conservative default recommended.

Distinguish:

- Ordinary wound infection.
- Knox infection.
- Non-infectious injury.

Proposed progression:

1. Exposure.
2. Incubation.
3. Symptoms.
4. Terminal deterioration.
5. Death.
6. Optional reanimation.

Infected dogs may become hostile to players, other dogs, and NPCs.

Reanimated dogs must not remain controllable companions.

Persist identity history without retaining active obedience authority.

Investigate compatibility with vanilla zombie targeting, animal attacks, animations, and multiplayer entity synchronization.

Do not assume vanilla supports infected canine entities.

Treat this subsystem as experimental until runtime-proven.

---

# 11. CANINE WORKING SKILLS

Dogs require their own persistent skills.

Proposed categories:

**Physical**
- Fitness.
- Endurance.
- Running.
- Strength.
- Agility.

**Behavioral**
- Obedience.
- Stealth.
- Impulse control.
- Pack coordination.

**Senses and detection**
- Scent work.
- Tracking.
- Search.
- Detection discrimination.

**Utility**
- Retrieval.
- Hauling.
- Guarding.
- Hunting assistance.
- Foraging assistance.
- Fishing assistance.
- Herding and controlled redirection.
- Handler assistance.

Comfort is a welfare condition, not a skill.

Skill advancement must depend on successful relevant activity.

Physical capability must remain limited by age, size, health, fatigue, and realistic individual differences.

---

# 12. SCENT DETECTION

Create a modular scent-target registry.

A dog must learn particular target odors rather than automatically recognizing arbitrary item categories.

Support:

- Narcotics.
- Gunpowder-related odors.
- Selected ammunition-related odors.
- Wildlife.
- People.
- Specific trained objects.
- Other verified scent-bearing items.

## 12.1 Training

Use staged scent introduction and positive reinforcement.

Track:

- Odor recognition.
- Odor discrimination.
- False alerts.
- Search proficiency.
- Environmental proofing.
- Trained indication behavior.
- Handler cue familiarity.

Detection must be affected by reasonable environmental factors where implementable.

## 12.2 Optional Drugs of 93 scent-target compatibility

Audit the actual installed mod and item definitions.

Identify exact FullTypes and relevant item tags.

Implement an optional read-only item-identifier/odor mapping adapter; the standalone mod must work with Drugs of 93 absent. Never import its pharmacology or treat human medicines as dog-safe.

Police or military dogs may spawn with existing narcotics-detection experience, but this must remain randomized.

Do not assume every police dog is trained for narcotics detection.

---

# 13. HUNTING, FORAGING, AND FISHING ASSISTANCE

Implement working-dog assistance grounded in existing Project Zomboid systems.

Potential functions:

- Follow wildlife scent trails.
- Locate downed game.
- Retrieve suitable small game.
- Indicate nearby natural resources.
- Locate dropped fishing equipment.
- Retrieve suitable floating objects.
- Assist with designated search areas.

Do not give dogs supernatural knowledge of hidden fish, wildlife, or items.

Audit vanilla hunting, foraging, fishing, and animal APIs before implementation.

---

# 14. ADVANCED RETRIEVAL AND LOGISTICS

Advanced dogs may:

- Retrieve designated items.
- Carry lightweight objects.
- Deliver items to familiar players.
- Move items to designated drop-off points.
- Assist with hauling.
- Transport appropriate bags.
- Deposit items into accessible containers.

## 14.1 Container interaction

Support:

- Open baskets.
- Accessible crates.
- Designated drop-off zones.
- Open vehicle trunks where physically reachable.

Do not allow dogs to magically open arbitrary locked or closed containers.

Validate:

- Item ownership.
- Container capacity.
- Reachability.
- Dog carrying capacity.
- Item accessibility.
- Server inventory authority.

Avoid item duplication.

---

# 15. DRAGGING AND CORPSE CLEANUP

Investigate an advanced dragging system for:

- Backpacks.
- Bags.
- Small loads.
- Appropriate equipment.
- Corpses.
- Cooperative multi-dog hauling.

The desired presentation is physically believable dragging with appropriate animation, collision, and object movement.

True ragdoll physics is an investigation target, not an assumed engine capability.

Prefer a safe, server-authoritative constrained-dragging system if full ragdoll physics is unsupported.

## 15.1 Corpse cleanup

Allow advanced trained dogs to receive:

- Collection zone.
- Destination zone.
- Eligible load types.
- Safety restrictions.

Dogs should claim tasks individually.

Prevent two dogs from unintentionally duplicating or moving the same corpse.

Support coordinated hauling only if source and runtime investigation establish a safe implementation.

Dog size, strength, stamina, terrain, and load mass determine feasibility.

Corpse handling must carry appropriate contamination and injury risks.

---

# 16. ZOMBIE REDIRECTION

Investigate a high-level working-dog task inspired by herding behavior.

A dog may attempt to attract and redirect part of a zombie group toward a designated location.

This is not literal livestock herding.

Implement through verified zombie attraction, navigation, and avoidance mechanics.

Consider:

- Dog speed.
- Confidence.
- Training.
- Fatigue.
- Zombie density.
- Escape routes.
- Obstacle navigation.
- Handler recall.
- Safe disengagement.

No dog should be guaranteed to survive a large horde.

Breed predispositions influence suitability but must not guarantee success.

A small companion breed should generally be poorly suited to this task.

This feature remains experimental pending pathfinding and AI feasibility testing.

---

# 17. DISTRACTION EQUIPMENT

Explore:

- Squeaky toys.
- Audible lures.
- Remote-activated sound devices.
- Dog-carried deployable lures.
- Toy launchers.
- Compatible thrown objects.

Advanced dogs may be trained to deliver a lure, retreat, and return to the handler.

Do not require dogs to remain beside an activated lure.

Investigate a Chuckit-style launcher for compatible thrown objects.

Any explosive-projectile compatibility must be a separately audited optional system with realistic restrictions, server authority, and safe item handling.

Do not train dogs to transport armed explosives.

---

# 18. PACK MANAGEMENT

Implement persistent multi-dog pack relationships.

Track:

- Pack membership.
- Individual handler relationships.
- Social affiliation.
- Familiarity.
- Cooperation.
- Tension.
- Resource conflicts.
- Preferred companions.
- Social influence.
- Situational leadership.

## 18.1 Dynamic leadership

The player does not manually select a universal alpha dog.

Instead, dogs develop dynamic social influence and task-specific leadership.

Leadership can change based on:

- Confidence.
- Experience.
- Relationships.
- Task proficiency.
- Health.
- Group familiarity.

Allow occasional disputes and conflicts.

Do not use a rigid, constant alpha-dominance model as the biological basis for domestic dog behavior.

Serious fights should be uncommon and influenced by social incompatibility, stress, and resource competition.

## 18.2 Pack commands

Support group commands where appropriate:

- Follow.
- Stay.
- Return Home.
- Search.
- Retrieve.
- Guard.
- Haul.
- Clear Bodies.
- Disengage.

Each dog must independently evaluate its training and ability to comply.

Never grant an untrained dog advanced behavior merely because another pack member knows it.

---

# 19. PACK MANAGEMENT UI

Add a compact dog-paw icon to the left-side interface.

Hovering over the icon expands the pack list.

Display individual dogs in an organized vertical list.

Each dog entry should show concise, readable information such as:

- Name.
- Breed.
- Current activity.
- Health status.
- Stress indicators.
- Location or availability.
- Important alerts.

Hovering over an individual dog reveals additional information.

Clicking opens or pins its detailed panel.

## 19.1 Detailed panels

Provide:

- Overview.
- Health.
- Training.
- Skills.
- Behavior.
- Welfare.
- Equipment.
- Handler relationships.
- Pack relationships.
- Active tasks.

Initially hidden attributes must remain hidden until discovered.

## 19.2 UI principles

- Vanilla-inspired presentation.
- Readable at different resolutions.
- Mouse and controller support where feasible.
- Scalable UI.
- Clear tooltips.
- Minimal clutter.
- Context-sensitive actions.
- No redundant or impossible menu options.
- Immediate explanations for failed commands.
- Safe fallback when a dependency is missing.

Use state-aware context menus.

Examples:

Show "Attach Leash" only when applicable.

Show "Detach Leash" only when attached.

Show "Train Recall" only when the dog and handler can meaningfully attempt that exercise.

---

# 20. COMMAND RADIAL AND HOTKEYS

Implement a configurable hold-to-open radial command menu.

Foundational commands:

- Sit.
- Down.
- Stay.
- Heel.
- Recall.
- Place.
- Release.

Advanced commands appear contextually when available.

Allow configurable keyboard bindings, including F-keys.

Do not overwrite existing keybindings without user consent.

## 20.1 Overhead speech

Spoken commands should display overhead text.

Example:

"Rex, Sit!"

Investigate reuse of appropriate vanilla player vocalizations, such as the existing "Hey" sound.

Spoken commands must generate appropriate sound events for zombies.

Silent cues must not generate audible speech.

---

# 21. SAFEHOUSE CARE AND COMFORT

When entering a recognized safehouse or assigned home area, dogs should evaluate their needs and available resources.

Possible autonomous actions:

- Drink from accessible water.
- Eat appropriate food.
- Move to assigned resting area.
- Rest.
- Sleep.
- Recover from stress.
- Settle near familiar companions.

Needs must recover through simulated time and available resources.

Do not instantly reset health, hunger, thirst, or anxiety.

Respect ownership and access permissions.

Support configured home zones when vanilla safehouses are unavailable.

---

# 22. BREED- AND LOCATION-WEIGHTED SPAWNS

Implement weighted spawning by building type, region, and optional registered POIs.

Examples:

**Urban residential**
- Pugs.
- French Bulldogs.
- Family companion breeds.
- Mixed breeds.

**Rural**
- Hunting dogs.
- Farm dogs.
- Herding breeds.
- Mixed breeds.

**Police facilities**
- German Shepherds.
- Belgian Malinois.
- Labradors.
- Other possible breeds.

**Military locations**
- Working breeds.
- Mixed breeds.
- Possible specialized working dogs.

**Shelters and kennels**
- Broad breed distribution.
- Highly variable training and welfare.

All associations must remain probabilistic.

A police station does not guarantee a police dog.

A dog at a police station does not guarantee advanced training.

A police vest does not guarantee police training.

Provide sandbox configuration and optional map-specific POI adapters.

---

# 23. ANIMAL CONTROL EQUIPMENT

Investigate:

- Humane animal catch poles.
- Portable kennels.
- Dog crates.
- Animal transport equipment.
- Specialized harnesses.
- Police canine protective equipment.

Catch poles should be last-resort restraint equipment, not positive-reinforcement training tools.

Capture success and animal welfare consequences must be modeled.

## 23.1 Animal control trucks

Investigate specialized kennel trucks with multiple compartments.

Target configurations may support approximately 8–10 small compartments, with fewer occupants when larger kennels are required.

Each compartment needs:

- Unique occupancy.
- Dog size restrictions.
- Comfort.
- Ventilation.
- Transport stress.
- Secure containment.
- Persistent occupant identity.

Avoid duplicating dogs through vehicle inventories.

## 23.2 Zombie restraint

Investigate an optional zombie-restraint interaction inspired by pole-based grappling.

Keep this separate from animal training.

Require verified collision, targeting, escape, and server-authority mechanics.

Do not assume a restrained zombie becomes permanently harmless.

---

# 24. IN-GAME MANUAL

The mod must include a complete in-game guide.

Players should not need to visit the Steam Workshop page to understand the systems.

Provide:

1. An accessible Help/Manual control in the dog UI.
2. A readable in-world training handbook where supported.
3. Contextual tooltips.
4. First-time guidance.
5. Clear command failure explanations.

Manual chapters:

- Finding and rescuing dogs.
- Understanding personality.
- Confidence versus anxiety.
- Discovering previous training.
- Basic obedience.
- Advanced training.
- Positive reinforcement.
- Leash handling.
- Dog health.
- Grooming.
- Infection.
- Working-dog skills.
- Scent detection.
- Hunting and foraging.
- Retrieval and hauling.
- Pack management.
- Kennel vehicles.
- Troubleshooting.

The manual must accurately reflect implemented features.

Do not document speculative systems as functional.

---

# 25. PHYSICAL ELIMINATION, HOUSEBREAKING & SANITATION — CORE FEATURE

This is a **core biological system**, not optional flavor or a late compatibility patch.

## 25.1 Separate needs and physiology

Every dog maintains persistent bladder fullness, bowel fullness, urgency, last elimination, learned location preferences and housebreaking state. Progression varies with age (puppy/adult/senior), body size, water/food intake, activity, sleep, stress/anxiety, illness and individual variation. Needs continue during simulated time, with bounded catch-up after unloading; avoid instantly filling/emptying needs or double-applying time on reload. No dog can hold indefinitely. Need urgency must coexist with fatigue, safety, training and pack behavior.

## 25.2 Physical waste in the world

- **Urination:** spawn a real, visible, server-owned puddle at a valid tile/surface with stable ID, wetness, drying/decay, cleanup and optional bounded odor.
- **Defecation:** spawn a physical server-owned feces object with stable ID, location, age, collection, disposal, decay and cleanup.
- No merely textual 'accident' events, invisible stats-only waste, duplicated objects after reload, or unlimited permanent accumulation.
- Use verified world-object persistence/replication, not assumed APIs. Avoid object creation inside inaccessible geometry or unsupported surfaces.
- Cleaning tools may include verified vanilla mop/bucket/cleaner/shovel/scoop/waste-bag equivalents; audit actual FullTypes and consumption semantics before implementation.
- Hygiene/comfort/odor effects must have clear, bounded rules. Do not invent pathogen transmission, insect attraction or parasite spread without a reviewed mechanism.

## 25.3 Housebreaking progression

Independent of overall obedience, stages: **0 untrained; 1 surface familiarity; 2 learning designated area; 3 usually signals/seeks area; 4 reliable in normal conditions; 5 generalized across environments**. Generate previous proficiency independently of police/military history and breed. A former household pet may already be housebroken; an outdoor working dog may require adaptation. Positive reinforcement and successful real elimination in a suitable area increase reliability; punishment must not grant training bonuses. Failed access, illness, anxiety, confinement, puppy physiology and extreme urgency can still cause accidents; do not erase all proficiency for one accident.

## 25.4 Signaling and handler interaction

Signals include pacing, whining, door-waiting, sniffing, circling, seeking handler and body-language cues, chosen by temperament and history. Display contextual UI alerts such as 'needs to go outside' or 'waiting at the door' without constant spam. State-aware actions: Take Outside, Set/Change/Remove Potty Area, Practice Housebreaking, Reward Successful Elimination, Clean Waste. Award XP only after a server-observed event, not from clicking a button.

## 25.5 Potty zones and autonomous routine

Player assigns persistent outdoor relief area(s), with bounds, valid tiles, safehouse/home association and permissions. Multiple dogs can share a zone. A sufficiently trained dog evaluates urgency, available exits, accessible doggy doors, route safety and current tasks, travels to a valid relief tile, eliminates, creates physical waste, and returns indoors/continues prior task. Blocked exits cause a signal, alternative route or eventual accident. Dogs must not deliberately path through an obvious zombie horde solely to satisfy a bathroom need. Avoid route recomputation each tick. Track and cancel stale tasks after restart/unload.

## 25.6 Sandbox and tests

Settings: housebreaking enabled, training speed, need frequency, accident likelihood, waste persistence/decay, sanitation severity, autonomous bathroom trips. Tests: puppy/adult/senior, illness/anxiety, pre-housebroken dog, multiple dogs one zone, blocked door, locked flap, danger outside, cleaning, decay, reconnect/restart, duplicate elimination request, headless MP.

# 26. INSTALLABLE DOGGY DOORS — CORE FEATURE

## 26.1 Door compatibility and installation

Goal: retrofit as many vanilla, player-built and modded wooden/metal/glass/interior/exterior/reinforced doors as engine geometry allows. Audit actual door classes, sprite/collision, damage, barricade and pathfinding; **do not promise literally every door**. Unsupported door types get a clear reason. Variants: small, medium, large, extra-large, reinforced and electronic. Opening eligibility uses actual dog dimensions rather than breed names. Appropriate tools/materials/carpentry/metalworking/electrical skills vary by door and type; verify vanilla item IDs and timed-action completion.

## 26.2 Access control

Modes: bidirectional, entry-only, exit-only, locked, authorized-collar electronic. Electronic units have verified power/battery model and configurable safe behavior on power loss; do not assume a collar detects infection. Door ownership, configuration, damage, installation, access ACL, power and authorized collar IDs are server-owned and persistent. Actions Install/Remove/Repair/Lock/Unlock/Configure are visible only when meaningful. The main door's ordinary open/closed/locked function must remain intact.

## 26.3 Dog learning and traversal

Dog must learn flap use; confidence, anxiety, size and positive reinforcement influence approach/hesitation. Route planner verifies opening size, mode, lock, direction, permissions, obstruction and safe destination. Perform a coherent native or proven custom traversal transition with collision; never simply disable whole-door collision or teleport through a solid door. Restore original task after traversal; handle two dogs approaching opposite sides, chunk unload and power loss mid-task. Dog-door use integrates with housebreaking, feeding, homecoming and rest.

## 26.4 Security and durability

Door size creates meaningful tradeoffs: small openings limit animal access, larger openings may invite zombie entry. Flap/lock/reinforcement have bounded durability and repair; barricades block flap only if actual geometry obstructs it. Optional emergency lockdown must use physical/server-authorized behavior. Warn players in manual that large dog doors are security vulnerabilities.

# 27. ZOMBIE DOGGY-DOOR INTERACTION — EXPERIMENTAL ADVANCED FEATURE

## 27.1 Eligibility and stimuli

Zombies may notice sound, dog movement, visible activity or an accessible opening according to verified perception mechanics. Evaluate zombie body dimensions/posture, flap size, lock/damage state, reinforcement, barricade and actual collision. Most adult zombies cannot fit small flaps; reaching/scratching/damaging is distinct from passing. Larger openings may allow crawling/squeezing if supported.

## 27.2 Traversal and damage

Sequence: detect/investigate → approach → validate fit → attempt crawl/squeeze → success, obstruction, retreat or flap/door damage → resume native AI. Audit vanilla window/fence crawling, low-obstacle transitions, zombie pathfinding, door damage, animation state and server replication. Do not teleport zombies, spawn a replacement inside, globally remove door collision, or mark success merely because an animation exists. If full traversal is blocked, implement only independently proven damage/investigation and leave traversal BLOCKED.

## 27.3 Sound, dog alert and infection

Flap movement, scratching, scraping, banging and damage may create verified world sound events; trained dogs may issue silent alerts, bark, retreat, investigate or seek handler based on perception, confidence and cue knowledge. Barking can attract more zombies. Optional alternate-lore infected dogs may use compatible openings and still possess valid electronic collars, but infected-dog reanimation is itself unproven and separately gated.

## 27.4 Acceptance

Small opening rejects oversized adult; crawling eligibility works when proved; locked/reinforced/blocked doors resist appropriately; barricade coverage respects actual geometry; no zombie duplicates, teleporting, permanent collision bypass or stuck entity; consistent two-client observations and dedicated restart/unload; audio/dog alert behavior uses genuine perception. Sandbox toggle and difficulty controls. Keep feature disabled or omitted if native traversal cannot be proven.

---
# 28. STANDALONE MILESTONE PLAN AND STOP GATES

**M0R — Architecture reset and native feasibility (current authorized work):** archive historical dependency assumptions without rewriting evidence; audit native animal species/rig/AI/movement, effective packaged versus loose class, private persistence, original dog identity, and MP authority. Produce `STANDALONE_ARCHITECTURE_DECISION.md`, `NATIVE_CANINE_ENTITY_FEASIBILITY.md`, `NATIVE_ANIMAL_MULTIPLAYER_AUDIT.md`, `ANIMAL_ANIMATION_AND_MODEL_AUDIT.md`, `ANIMAL_IDENTITY_PERSISTENCE_AUDIT.md`, `MODIFIED_ENGINE_COMPATIBILITY.md`, `STANDALONE_FEATURE_FEASIBILITY_MATRIX.md`, `STANDALONE_IMPLEMENTATION_PLAN.md`. No gameplay code until separate approval.

**M1 — Minimal original dog proof:** one original canine entity, identity, server movement, private store, filtered projection, safe spawn/save/load/unload, two-client dedicated sync; verify no Companion Dogs installed. No advanced skills.

**M2 — Biology and basic welfare:** randomized traits/history, baseline needs, read-only health, hunger/thirst/rest, bladder/bowel, physical urine/feces and cleaning, performance budgets.

**M3 — Handling and training:** handler ACL/bond, cue records, recall/sit/stay/heel, positive reinforcement, rolling XP budget, leash, discovery, human skill/knowledge, housebreaking and potty zones.

**M4 — Doggy doors and autonomy:** door support matrix, installation/access, trained dog traversal, safehouse routines and autonomous bathroom trips.

**M5 — Security interactions:** flap damage, zombie investigation and alerts, then **only if proven** zombie crawling traversal.

**M6 — Working dogs:** scent categories, training samples, retrieval, hunting/foraging/fishing assistance, optional Drugs of '93 target adapter, guard/alert.

**M7 — Pack/logistics/transport:** original roster and social model, formations, transactional container delivery, dragging/corpse cleanup, humane capture and kennels.

**M8 — Experimental advanced features:** infected dogs/reanimation, true physics dragging/shared loads, zombie redirection, catch-pole zombie restraint, multi-kennel trucks, specialized decoys and throwers.

**M9 — Release readiness:** manual, controller/keyboard UX, sandbox validation, accessibility/scaling, performance, migration, Linux, full SP and dedicated MP regressions, version and packaging checks. Release only with explicit user authorization.

## Standalone proof gates

- **S1 Entity:** original dog species/entity/model exists without third-party dog mods.
- **S2 Authority:** server is sole writer of simulation, movement/task and rewards.
- **S3 Identity:** stable through spawn, carry, maturation, transport, unload, reconnect and restart.
- **S4 Privacy:** hidden fields inaccessible through public ModData, packets, logs and unauthorized requests.
- **S5 Commands:** actor rights, stale references, replay, timing and resources validated server-side.
- **S6 Movement:** real path/collision and client synchronization on headless dedicated server.
- **S7 Health:** one canine health/needs writer, no human-medical substitution.
- **S8 Inventory:** exactly-once physical item/container transactions, no duplication.
- **S9 World objects:** persistent synchronized waste, potty zones and doggy doors.
- **S10 Packs:** one movement/task writer per dog; group eligibility individually validated.
- **S11 Zombies:** no geometry bypass, fake crawl or duplicate zombie.
- **S12 Compatibility:** Linux headless, pristine engine, optional dependencies absent, save migrations.

## Required test matrix

For each milestone, run relevant SP, local hosted MP, **two-client dedicated MP**, reconnect, restart, chunk unload/reload and Linux tests. Include unauthorized second handler, two handlers competing for one dog, repeated packets, backup rollback, private-table request, transport with full inventory, dog death during task, concurrent pack orders, simultaneous dogs at flap, closed/locked exits, blocked potty zone, waste cleanup/restart, zombie flap damage/traversal, and 4-hour-day time scaling. Track observed PASS/FAIL/BLOCKED/NOT TESTED with logs and reproducible steps. Never promote offline source audit to runtime PASS.

# 29. SANDBOX AND USER EXPERIENCE CONTRACT

Offer grouped, documented sandbox settings with sensible defaults and no excessive mandatory configuration: spawn/population and location weighting; breed/personality and prior training distributions; learning speed, structured/passive 24-hour budgets; dog care, grooming, illness, injuries, anxiety, hunger/thirst; leash force; pack size/social conflict; scent/working skills; animal control/kennels; bladder/bowel frequency, housebreaking, waste decay/odor and sanitation; potty autonomy; doggy door types/security/power; zombie flap attacks/traversal; optional canine Knox infection/reanimation; advanced dragging and zombie redirection. Disabled features must not leave stale timers or orphaned world objects. Include mouse/controller UI, configurable F-keys and hold-radial, overhead speech with genuine zombie-attracting sound, silent cues, left paw hover roster/pinnable details, clear failure feedback, state-aware Common Sense Context Menus, and an in-game manual covering **implemented** features including sanitation and safehouse security.

# 30. VERSION, IP, AND OPERATING CONSTRAINTS

- Preserve canonical `0.1.0-dev.1` and root `VERSION`; technical ID `B47ANCEDDogTraining` remains provisional until explicitly approved. Follow `VERSION_POLICY.md` and `VERSIONING.md`, with independently versioned save/network schemas.
- Historical `COMPANION_DOGS_SOURCE_AUDIT.md`, `DOGPACK_COMPATIBILITY_AUDIT.md`, `SERVER_AUTHORITY_DESIGN.md`, `IMPLEMENTATION_PLAN.md` and `VALIDATION.md` are immutable evidence of **the former add-on architecture**. Do not silently repurpose their R1–R6 statuses as proof of standalone blockers or solutions.
- The original `USER_HANDOFF.md` is a feature provenance record, not current architecture authority. This document supersedes dependency and implementation assumptions while preserving the gameplay requirements.
- Use verified native public interfaces; no copied third-party source, assets, balance tables, or schemas. Do not alter installed game files, Workshop mods, live server, or research artifacts. Do not delete `research` following previously denied cleanup.
- Only separately authorized, bounded proof-of-concept code may follow M0R. No packaging, publication, deployment or claim of G6/G7/G8 PASS without actual runtime evidence.

# 31. IMMEDIATE CODEX TASK — DO THIS FIRST

1. Read this master specification and all eleven uploaded Milestone 0 documents, including original `USER_HANDOFF.md`, feasibility matrix, native audit, validation, and version policy.
2. Record the standalone architecture decision. Identify every prior Companion Dogs/DogPack dependency assumption and retire it **without deleting historical reports**.
3. Extract a requirement-by-requirement **traceability matrix** mapping each original feature and the three new systems to a standalone subsystem, feasibility status, native evidence, milestone, gate, test, and unresolved decision. Retain original 101-feature IDs where useful and append new IDs; do not pretend old classifications remain valid.
4. Re-audit native Build 42.21 effective animal classes, species registration, model/animation, AI, server movement, identity, persistence, world objects, doors, crawling, and zombie pathfinding. Compare modified and pristine engine behavior.
5. Provide the eight M0R audit reports, a native API evidence table, a dependency-free architecture diagram, explicit blockers, and a **smallest safe standalone dog prototype proposal**.
6. **Stop for review.** No gameplay implementation, package, deployment, dependency modification or Workshop publication until separately approved.

**Final vision:** a standalone, living canine ecosystem where physical needs, trust, training, individuality, work, pack behavior, sanitation and home security interact meaningfully. A trained dog can leave through a learned doggy door to use its designated relief area, but the same opening may become a genuine zombie vulnerability. Implement that experience without sacrificing dedicated-server correctness, native collision, persistence, or player agency.
