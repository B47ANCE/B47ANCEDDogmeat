# CODEX HANDOFF — B47ANCE'd Dog Training

**Project:** B47ANCE'd Dog Training  
**Project Type:** Project Zomboid Build 42 mod  
**Initial Development Version:** `0.1.0-dev.1`  
**Proposed Mod ID:** `B47ANCEDDogTraining` — provisional  
**Primary Dependency:** Companion Dogs  
**Optional Dependencies:** Companion Dogs: DogPack, Drugs of 93, supported vehicle/animal equipment mods  
**Development Priority:** Dedicated-server-first  
**Status:** Design approved for technical investigation; implementation not yet authorized by source verification.

---

# 1. PROJECT OBJECTIVE

Develop a comprehensive, realistic canine training, behavior, welfare, health, and working-dog overhaul for Project Zomboid.

The mod must extend Companion Dogs rather than unnecessarily replacing its existing animal entities, AI, animations, inventory, and lifecycle systems.

The goal is to create persistent canine companions with individual personalities, hidden histories, learned commands, medical conditions, and specialized working abilities.

**Core philosophy:**

An untrained dog is a responsibility. A trained dog is an asset. A neglected dog can become a liability.

Dogs should improve the player's survival experience through companionship, utility, and specialized training. Their capabilities must be earned through time, experience, care, and reinforcement.

The experience must remain approachable. Players should be able to train dogs while performing ordinary survival activities.

Do not turn dog ownership into constant micromanagement.

## Non-negotiable requirements

- Dedicated-server authority over all persistent gameplay state.
- Full multiplayer support.
- Persistent individual dog identities.
- Randomized hidden starting obedience.
- Randomized personality and anxiety.
- Separate confidence and anxiety attributes.
- Breed predispositions subordinate to individual personality.
- No RPG-style dog perk allocation.
- Realistic positive-reinforcement training.
- Approximately 4–8 in-game weeks for complete training under normal conditions.
- Passive training during ordinary gameplay.
- Daily training XP limits.
- Advanced dog health and welfare systems.
- Integrated radial command menu and configurable hotkeys.
- Optional zombie infection and zombification.
- Multiple-dog pack management.
- Advanced working-dog and logistical capabilities.
- An accessible in-game manual.
- Compatibility with existing Companion Dogs functionality.
- No invented or unverified engine APIs.
- No deployment, Workshop publication, or changes to installed game files without explicit approval.

---

# 2. PHASE ZERO — MANDATORY SOURCE AUDIT

Do not begin implementing gameplay until the relevant source code has been inspected.

## 2.1 Identify installed dependencies

Locate and inspect:

1. Companion Dogs.
2. Companion Dogs: DogPack, if installed.
3. Drugs of 93, if installed.
4. Project Zomboid Build 42 Lua and Java-exposed APIs.
5. Vanilla skills, occupations, books, VHS, medical UI, inventory, vehicle, and animal systems.
6. Any relevant modded vehicle, animal handling, or physics systems.

Record exact versions, Workshop IDs, technical Mod IDs, file paths, and relevant source hashes.

Do not infer technical identifiers from display names.

## 2.2 Companion Dogs audit

Identify:

- Dog entity construction and spawning.
- Breed definitions.
- Age, weight, and existing traits.
- Current obedience and skill systems.
- AI behavior and command processing.
- Dog inventory and equipment.
- Health and damage handling.
- Animal movement and pathfinding.
- Player ownership and handler tracking.
- Existing pack behavior.
- Save/load mechanisms.
- Server/client ownership.
- Multiplayer synchronization.
- UI classes and extension points.
- Animations and sounds.
- World unloading and reloading.
- Vehicle interaction support.

Determine which features can be extended through supported interfaces and which would require interception or replacement.

Never overwrite original mod files.

## 2.3 Required audit deliverables

Produce:

- `COMPANION_DOGS_SOURCE_AUDIT.md`
- `DOGPACK_COMPATIBILITY_AUDIT.md`
- `DRUGS_OF_93_COMPATIBILITY_AUDIT.md`
- `VANILLA_API_AUDIT.md`
- `FEATURE_FEASIBILITY_MATRIX.md`
- `SERVER_AUTHORITY_DESIGN.md`
- `IMPLEMENTATION_PLAN.md`

Each proposed feature must be classified as:

- VERIFIED — source-supported
- FEASIBLE — implementation path established, runtime untested
- EXPERIMENTAL — requires prototype or engine investigation
- BLOCKED — no safe implementation path established

Do not describe source inspection as runtime validation.

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

Implement or integrate appropriate training equipment:

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

## 12.2 Drugs of 93 compatibility

Audit the actual installed mod and item definitions.

Identify exact FullTypes and relevant item tags.

Implement an optional compatibility adapter.

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

# 25. DEDICATED-SERVER AUTHORITY

All meaningful state must be server-owned.

The server validates:

- Dog identity.
- Handler identity.
- Command eligibility.
- Training progression.
- XP rewards.
- Medical state.
- Infection progression.
- Equipment use.
- Item transfers.
- Vehicle occupancy.
- Pack membership.
- AI task allocation.
- Death and reanimation.

Clients may request actions but cannot directly assign successful outcomes.

## 25.1 Networking

Implement request validation, synchronization, and appropriate rejection of:

- Invalid dog identifiers.
- Stale entity handles.
- Unauthorized handlers.
- Duplicate actions.
- Replayed reward requests.
- Impossible distances.
- Invalid item references.
- Invalid container interactions.
- Conflicting pack tasks.

Use verified multiplayer APIs.

## 25.2 Persistence

Persist:

- Dog identity.
- Breed and age.
- Personality.
- Confidence and anxiety.
- Health and injuries.
- Existing training.
- Learned commands.
- Dog skills.
- Handler relationships.
- Pack relationships.
- Equipment.
- Infection.
- Active task state where appropriate.
- Discovery records.
- Transport and kennel occupancy.

Ensure safe behavior during save/load and entity unload/reload.

Do not depend on client rendering for server AI.

---

# 26. SANDBOX SETTINGS

Proposed settings include:

- Training speed.
- Daily XP budget.
- Passive training XP multiplier.
- Prior training distribution.
- Working-dog rarity.
- Personality variability.
- Anxiety severity.
- Welfare difficulty.
- Grooming requirements.
- Leash difficulty.
- Dog injury severity.
- Canine Knox infection enabled.
- Infection transmission probability.
- Infection progression speed.
- Zombified dog behavior.
- Pack size limits.
- Dog conflicts.
- Advanced working tasks.
- Corpse hauling.
- Zombie redirection.
- Animal control vehicles.
- Specialized dog spawns.

All settings must be validated and documented.

Avoid exposing excessive configuration complexity to ordinary players.

---

# 27. DEVELOPMENT MILESTONES

## Milestone 0 — Audit

Deliver complete source and feasibility reports.

No gameplay implementation.

## Milestone 1 — Core identity and behavior

Implement:

- Persistent identity.
- Breed traits.
- Random personality.
- Separate confidence and anxiety.
- Hidden prior training.
- Handler relationships.
- Server synchronization.

## Milestone 2 — Training overhaul

Implement:

- Dog obedience progression.
- Individual commands.
- Human Dog Training skill.
- Daily XP cap.
- Passive training.
- Positive-reinforcement tools.
- Leash mechanics.
- Radial commands.

## Milestone 3 — Health and welfare

Implement:

- Veterinary health UI.
- Injuries.
- Grooming.
- Comfort.
- Safehouse care.
- Rehabilitation.

## Milestone 4 — Working-dog systems

Implement verified:

- Scent work.
- Tracking.
- Retrieval.
- Hunting assistance.
- Foraging assistance.
- Fishing assistance.
- Specialized training knowledge.

## Milestone 5 — Pack and logistics

Implement:

- Pack relationships.
- Dynamic leadership.
- Pack UI.
- Pack commands.
- Hauling.
- Container delivery.
- Corpse cleanup where feasible.

## Milestone 6 — Optional advanced systems

Investigate and implement only when feasible:

- Canine Knox infection.
- Zombified dogs.
- Zombie redirection.
- Advanced dragging physics.
- Kennel vehicles.
- Catch poles.
- Zombie restraint.
- Specialized distraction equipment.

## Milestone 7 — Compatibility and polish

Complete:

- DogPack integration.
- Drugs of 93 integration.
- Working-dog equipment compatibility.
- In-game manual.
- UI scaling.
- Dedicated-server testing.
- Multiplayer testing.
- Performance testing.
- Regression testing.

---

# 28. TESTING REQUIREMENTS

All major features require dedicated-server runtime validation.

Minimum tests:

- New dog generation.
- Hidden starting skills.
- Skill discovery.
- Multiple handlers.
- Multiple dogs.
- Training XP cap.
- Passive XP anti-farming.
- Dog injuries.
- Medical persistence.
- Grooming and rehabilitation.
- Safehouse routines.
- Pack leadership changes.
- Pack task allocation.
- Container item transfers.
- Vehicle kennel occupancy.
- Reconnect during training.
- Restart during active tasks.
- Unload/reload during dragging.
- Dog death.
- Optional infection and reanimation.
- Dependency missing or disabled.
- Client/server version mismatch.
- Linux case-sensitive loading.

Report each test as PASS, FAIL, BLOCKED, or NOT TESTED.

Never label an offline source audit as a successful multiplayer runtime test.

---

# 29. CODE QUALITY AND COMPATIBILITY

Follow these requirements:

- Use verified Build 42 APIs.
- Preserve original Companion Dogs files.
- Use isolated compatibility adapters.
- Avoid broad global monkey patches.
- Avoid unnecessary per-tick world scans.
- Use event-driven updates where practical.
- Limit AI search radius and work budgets.
- Prevent duplicate item and entity operations.
- Avoid stale references.
- Validate all server requests.
- Support Linux case-sensitive paths.
- Maintain clean client/shared/server separation.
- Keep UI rendering separate from gameplay authority.
- Provide diagnostic logging.
- Maintain backward-compatible persistence migrations.
- Do not silently discard unsupported data.

Any feature requiring engine modifications, inaccessible native APIs, or unverified physics behavior must be reported as blocked or experimental rather than simulated as complete.

---

# 30. IMMEDIATE CODEX INSTRUCTIONS

**Begin with Milestone 0 only.**

1. Locate the installed Companion Dogs source.
2. Locate DogPack and Drugs of 93 if present.
3. Verify exact versions and technical identifiers.
4. Inspect the relevant Build 42 APIs.
5. Produce the requested audit documents.
6. Identify existing features that must be preserved.
7. Identify safe extension points.
8. Identify dedicated-server authority boundaries.
9. Classify every proposed feature by feasibility.
10. Recommend a concrete architecture and implementation order.

Do not implement gameplay during this initial task.

Do not create a release package.

Do not deploy to the server.

Do not modify original dependency files.

Do not publish to the Steam Workshop.

If source files are unavailable, report the missing files and provide exact paths or instructions for obtaining the required evidence.

**The first deliverable is a verified technical foundation, not a playable mod.**

---

# FINAL PROJECT VISION

B47ANCE'd Dog Training should transform dogs from simple followers into individual, persistent survival companions.

A dog might be discovered frightened, injured, and untrained. Over weeks or months, the player can help it recover, learn its personality, discover its abilities, and develop a working relationship.

Another dog might already possess advanced training but be difficult for an inexperienced handler to understand.

Some dogs will excel at hunting. Others will be useful for detection, hauling, guarding, or companionship. Some will never be suited to dangerous working tasks.

Players should have meaningful reasons to rescue, rehabilitate, train, and care for their animals.

Every dog should feel different.

Every relationship should develop naturally.

And every working ability should have a practical place in Project Zomboid's survival gameplay.

**End of Codex handoff.**
