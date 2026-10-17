# CODEX HANDOFF — Database-Authoritative Canine Lifecycle & Multiplayer Relationships

**Project:** B47ANCE'd Dogmeat  
**Technical Mod ID:** `B47ANCEDDogmeat`  
**Reported Version:** `0.2.0-dev.7` — verify canonical VERSION  
**Target:** Project Zomboid Build 42.21  
**Architecture:** Standalone, Lua-only, dedicated-server-first  
**Temporary Test Carrier:** Vanilla raccoon  
**Dog Models:** Deferred  
**Development Status:** Architecture redesign and bounded feasibility investigation  
**Deployment:** Not authorized

---

# 1. OBJECTIVE

Design a database-authoritative canine persistence and relationship system.

The database must become the permanent source of truth for all B47ANCE'd dog records.

Native Project Zomboid animals will represent dogs physically in the game world, but native IDs, client-writable markers, and transient entity handles must not be trusted as permanent dog identities.

The system must support:

- Naturally spawned stray dogs.
- Natural bonding through proximity, feeding, and petting.
- Primary ownership after reaching 100% bond.
- Naming after bonding.
- Loose following before obedience training.
- Physical collars and leads.
- Persistent primary and secondary relationships.
- Trusted caretakers, trainers, and handlers.
- Autonomous self-care when the owner is offline.
- Optional offline despawning controlled by server sandbox settings.
- Persistent canine health, genetics, training, inventory, and welfare.
- Safe dedicated-server lifecycle management.

**Critical:** A database-authoritative design is a new architectural proposal. It does not automatically resolve the previously documented native identity NO-GO.

Do not enable multiplayer ownership until the revised lifecycle is proven.

---

# 2. ARCHITECTURAL CHANGE

The previous architecture attempted to authenticate a native animal restored from Project Zomboid's save system against a private dog record.

The latest investigation concluded that this cannot currently meet the required guarantees through the verified Build 42.21 Lua interfaces.

The revised architecture separates:

1. Permanent logical dog identity.
2. Server-owned persistent dog records.
3. Temporary native animal representations.
4. Session-specific entity bindings.
5. Player relationship and authorization records.

## 2.1 Database authority

The database owns the permanent canine record.

It must not rely on native `animalId`, public ModData, or a client-provided identity marker as its authoritative key.

## 2.2 Native animal representation

The native animal provides:

- World position.
- Physical movement.
- Collision.
- Animation.
- Physical interaction.
- Native rendering.
- Supported native animal behavior.

Its association with a permanent dog record must be established and validated by the server.

## 2.3 Server canine controller

An original Lua server controller coordinates:

- Dog provisioning.
- Identity binding.
- Bonding.
- Relationship updates.
- Task arbitration.
- Offline self-care.
- Health and welfare progression.
- Persistence.
- Recovery.
- Withdrawal.
- Authorized restoration.

Do not introduce a second independent movement writer.

Do not copy Companion Dogs or DogPack implementations.

---

# 3. DATABASE DESIGN

Investigate a private, server-owned persistent store.

SQLite is a candidate only if a suitable Lua-only interface is verified.

Otherwise, investigate extending the existing private file-store architecture.

Do not introduce a Java bridge, custom JAR, native library, or external database service without separate approval.

## 3.1 Permanent dog records

Each dog record must include:

### Identity

- Canonical dog ID.
- Name.
- Creation origin.
- Original breed.
- Age.
- Sex, where supported.
- Permanent identity metadata.

### Genetics and appearance

- Breed ancestry.
- Physical characteristics.
- Coat phenotype.
- Appearance seed.
- Original appearance.
- Authorized cosmetic model override.

### Personality

- Confidence.
- Anxiety disposition.
- Current anxiety.
- Sociability.
- Independence.
- Learning aptitude.
- Motivations.
- Energy requirements.
- Other individual behavioral traits.

### Training

- Overall obedience.
- Individual command knowledge.
- Recognized cues.
- Training XP.
- Working skills.
- Previous training history.
- Reinforcement records.
- Daily XP budgets.

### Health

- Injuries.
- Illnesses.
- Parasites.
- Treatments.
- Medical history.
- Current medical condition.
- Recovery state.

### Welfare

- Hunger.
- Thirst.
- Fatigue.
- Bladder.
- Bowel.
- Comfort.
- Hygiene.
- Stress.
- Sleep requirements.

### Equipment and inventory

- Collar.
- Lead.
- Harness.
- Armor.
- Medical equipment.
- Carried items.
- Inventory transaction records.

### Home and world state

- Assigned safehouse.
- Assigned doghouse.
- Assigned potty area.
- Last trusted location.
- Current task.
- Current lifecycle state.

### Persistence

- Record schema version.
- Record revision.
- World identity.
- Last committed checkpoint.
- Recovery metadata.

Keep schema versioning independent of the project's SemVer.

---

# 4. PLAYER RELATIONSHIP DATABASE

Relationships must be stored separately from physical animal entities.

Every dog can maintain individual relationships with multiple players.

Use authenticated server-side player identities.

SteamID64 must be obtained from the authenticated connection, not from a client-submitted value.

## 4.1 Relationship records

Store:

- Canonical dog ID.
- Authenticated player identity.
- Bond strength.
- Relationship type.
- Familiarity.
- Trust.
- Known commands and cue familiarity.
- Interaction history.
- Authorized capabilities.
- Last interaction.
- Relevant owner permissions.

One dog may have one primary owner and multiple secondary relationships.

A secondary bond must never automatically replace the primary owner.

---

# 5. NATURAL PRIMARY BONDING

Dogs must not be claimed through an arbitrary ownership button.

Players earn ownership through normal interactions.

## 5.1 Bonding activities

Bonding increases through:

- Spending calm time near the dog.
- Feeding appropriate food.
- Petting.
- Repeated positive experiences.

Bonding must depend on the dog's personality, anxiety, confidence, and willingness to interact.

Proximity alone must not award unlimited bonding progress.

Petting and feeding must be validated server-side.

Prevent repeated-action farming and client-authored relationship values.

## 5.2 Bond progression

Bond strength ranges from 0 to 100.

Exact progression rates must be balanced later.

A dog can become familiar with a player before reaching full ownership.

## 5.3 Reaching 100% bond

When an unowned dog reaches 100% primary bonding:

1. Server validates the relationship.
2. Server confirms the dog has no conflicting primary owner.
3. Primary ownership is committed to the database.
4. Player gains permission to name the dog.
5. Dog becomes an owned companion.
6. Dog begins loosely following the player.
7. Dog becomes available in the owner's companion interface.
8. If the player's SteamID has authorized custom models, the cosmetic selection popup becomes available.

Bonding must not grant obedience levels or erase existing training.

---

# 6. LOOSE FOLLOWING & GETTING LOST

A bonded dog should naturally want to remain near its owner.

However, bonding does not automatically teach reliable following.

An untrained dog may:

- Investigate scents.
- Stop unexpectedly.
- Chase animals.
- Become distracted.
- Wander away.
- Lose sight of its owner.
- Become frightened.
- Fail to respond to recall.
- Get lost in urban environments.

## 6.1 Collar and lead

A collar provides identification and an attachment point.

A lead provides physical handling and reduces the likelihood of the dog wandering away.

A collar alone must not magically prevent a dog from becoming lost.

Reliable off-lead following requires training.

## 6.2 Ownership persistence

A lost dog remains associated with its owner in the database.

Losing physical contact must not automatically erase ownership.

Recovery and reunion mechanics require a separately verified entity lifecycle.

---

# 7. SECONDARY BONDS

Other players may develop their own relationships with an owned dog.

These are called sub-bonds.

Sub-bonds develop through:

- Calm proximity.
- Feeding.
- Petting.
- Grooming.
- Walking.
- Appropriate medical care.
- Positive training experiences.
- Repeated safe interactions.

The dog may become increasingly comfortable with a secondary player.

Sub-bond progression must be individual to each dog-player relationship.

## 7.1 Relationship capabilities

Proposed progression:

| Relationship | Possible capabilities |
|---|---|
| Unfamiliar | Limited safe interaction |
| Acquaintance | Feeding and accepted petting |
| Friendly | Routine care and familiarity |
| Trusted Caretaker | Grooming, walking, shelter and welfare care |
| Trusted Trainer | Teaching and reinforcing commands |
| Trusted Handler | Authorized working commands and temporary handling |

Thresholds are provisional.

Trust affects canine cooperation.

Ownership permissions determine which actions are authorized.

Both checks are required.

## 7.2 Ownership restrictions

Secondary handlers must not automatically:

- Rename the dog.
- Transfer ownership.
- Delete the primary bond.
- Change exclusive cosmetic models.
- Remove the dog permanently from its owner.
- Override restricted equipment.
- Assign dangerous working tasks without permission.

A 100% sub-bond is not a primary ownership transfer.

---

# 8. TRUSTED CARETAKERS & TRAINERS

The system must support multiplayer players who specialize in animal care.

## 8.1 Trusted caretakers

Qualified trusted players may:

- Feed dogs.
- Provide water.
- Groom dogs.
- Clean kennels.
- Walk dogs.
- Assist with housebreaking.
- Perform permitted medical examinations.
- Provide appropriate treatment.
- Return dogs to assigned homes.

## 8.2 Trusted trainers

Qualified trusted players may:

- Teach foundational obedience.
- Practice existing commands.
- Reinforce learned behaviors.
- Conduct agility training.
- Improve working skills.
- Help with confidence and socialization.
- Perform authorized advanced training.

Actual success depends on the player's training knowledge and the dog's individual learning state.

## 8.3 Trusted handlers

Authorized handlers may temporarily direct a dog during work or travel.

Only one active handler should control the dog's movement/task lease at a time.

Lease acquisition, release, timeout, and disconnect handling must be server-authoritative.

An active lease must not transfer primary ownership.

---

# 9. OFFLINE OWNER SANDBOX POLICY

Implement a server sandbox setting controlling what happens to bonded dogs when their primary owner disconnects.

## 9.1 Default: Remain in World — Self-Care

**This is the approved default behavior.**

The dog remains physically present in the world.

It continues autonomous survival behavior.

Its ownership and relationships remain stored in the database.

Other players can encounter and interact with it.

Trusted caretakers and trainers may continue appropriate activities.

## 9.2 Optional: Store Dog While Owner Offline

Server owners may select a mode that safely withdraws the physical dog when its primary owner disconnects.

The permanent database record remains intact.

The dog may be restored when the owner reconnects, subject to proven lifecycle safety.

This mode must not be enabled until safe withdrawal and restoration are demonstrated.

## 9.3 Proposed stable sandbox identifiers

- `B47ANCEDDogmeat.OfflineCompanionMode`
  - `RemainInWorldSelfCare` — default.
  - `StoreWhenOwnerOffline` — optional.

- `B47ANCEDDogmeat.OfflineSafehouseRestriction`
  - Boolean.
  - Default: true.

- `B47ANCEDDogmeat.OfflineDoghouseGrowth`
  - Boolean.
  - Default: true, once growth is implemented and safe.

- `B47ANCEDDogmeat.AllowTrustedOfflineCaretakers`
  - Boolean.
  - Proposed default: true.

- `B47ANCEDDogmeat.AllowTrustedOfflineTraining`
  - Boolean.
  - Proposed default: true, subject to permissions and skill requirements.

These identifiers are proposals. Audit the actual sandbox registration format before finalizing them.

Document how changing a setting affects existing dogs and active sessions.

---

# 10. AUTONOMOUS SELF-CARE

When the primary owner disconnects, a dog in the default mode enters Self-Care Mode.

## 10.1 Hunger

The dog searches for accessible, appropriate food.

It must consume real available resources.

No free food generation.

## 10.2 Thirst

The dog searches for accessible water.

It must use real available water sources.

No free hydration.

## 10.3 Bathroom needs

The dog uses its trained potty area when accessible.

It may use a compatible doggy door.

If the relief area is inaccessible or unsafe, it may postpone the trip or have an accident.

Actual urine and feces must remain part of the existing sanitation design.

## 10.4 Sleep and shelter

The dog prefers:

- Assigned indoor bed.
- Assigned doghouse.
- Compatible kennel.
- Other suitable shelter.

Comfort, weather, health, and familiarity affect its choice.

## 10.5 Growth

Eligible puppies may use their assigned doghouse for future growth-stage transitions.

The intended animation is:

1. Puppy enters doghouse.
2. Growth transition occurs.
3. Dog emerges using its next age-appropriate model.

The same canonical dog identity, relationships, health, training, and history must persist.

Do not implement growth until entity replacement and lifecycle continuity are proven.

## 10.6 Danger avoidance

Offline dogs should avoid obvious threats.

They may:

- Retreat.
- Hide.
- Return to shelter.
- Avoid zombie concentrations.
- Abandon unsafe tasks.

They must not become invulnerable.

## 10.7 Health

Dogs may rest and recover naturally.

They must not automatically cure serious injuries, parasites, or infections without appropriate treatment.

---

# 11. SAFEHOUSE BEHAVIOR

If a dog is left inside a safehouse, its default home territory should remain that safehouse.

It may leave for essential needs:

- Food.
- Water.
- Bathroom.
- Assigned outdoor doghouse.
- Eligible growth transition.

After completing the need, it should attempt to return.

## 11.1 Safehouse boundaries

Respect:

- Assigned home identity.
- Door access.
- Doggy door access.
- Safehouse permissions.
- Dog size.
- Reachable paths.
- Nearby danger.

Do not teleport the dog through inaccessible doors.

## 11.2 Unavailable resources

If no suitable resource is available:

- Dog searches permitted alternatives.
- Dog communicates distress when appropriate.
- Dog may eventually suffer consequences.

Self-care does not guarantee survival.

## 11.3 Owner reconnect

When the owner reconnects:

- Validate the authenticated player.
- Restore normal active-owner behavior.
- Preserve the dog's current location.
- Preserve current welfare and medical state.
- Preserve interactions with trusted caretakers.
- Do not teleport the dog to its owner.

The player may need to return to the safehouse to retrieve it.

---

# 12. DATABASE-AUTHORITATIVE LIFECYCLE

Define explicit lifecycle states.

Proposed states:

- `WILD`
- `BONDING`
- `OWNED_ACTIVE`
- `OWNER_OFFLINE_SELFCARE`
- `WITHDRAW_PENDING`
- `STORED_OFFLINE`
- `RESTORE_PENDING`
- `QUARANTINED`
- `DECEASED`

Each state transition must have one authoritative server operation.

Do not allow a client to directly set lifecycle state.

## 12.1 Bonding transition

Commit primary ownership once.

Reject conflicting simultaneous ownership attempts.

## 12.2 Owner disconnect

For Self-Care Mode:

- Release the owner's active command lease.
- Persist relationship/session changes.
- Switch the dog to autonomous self-care.
- Keep the physical animal active where safely supported.

For Store Mode:

- Suspend tasks.
- Checkpoint state.
- Safely withdraw the physical animal.
- Commit the stored lifecycle state.

If withdrawal cannot be proven, quarantine instead of assuming success.

## 12.3 Owner reconnect

For an active world dog:

- Resolve the database record.
- Validate the current session binding.
- Resume normal owner interaction.

For a stored dog:

- Validate ownership.
- Validate world and record state.
- Prove no conflicting native body remains.
- Restore only through an approved provisioning path.

## 12.4 Death

Death must create a durable terminal record.

A deceased dog must never be restored alive through ordinary reconnect recovery.

Optional zombification requires a separate lifecycle contract.

---

# 13. NATIVE ENTITY BINDING

The database's canonical dog ID is permanent.

A native animal entity is a session-specific physical representation.

## Required investigation

Determine whether managed native animals can be:

1. Safely excluded from ordinary native restoration.
2. Safely withdrawn before native save.
3. Identified and reconciled before duplicate provisioning.
4. Bound to database records without trusting copied markers.
5. Kept physically active across restarts without ambiguous identity.

Do not assume any of these capabilities exists.

## 13.1 Binding registry

Maintain a server-only runtime binding between:

- Canonical dog ID.
- Current native entity reference.
- Current session.
- Entity generation.
- Lifecycle state.
- Verified admission evidence.

The runtime binding must never be treated as durable proof by itself.

## 13.2 Duplicate prevention

Before provisioning a physical animal:

- Check the permanent record.
- Check active bindings.
- Check pending lifecycle transitions.
- Reconcile existing native representations.
- Reject ambiguous cases.

Never spawn a second animal simply because the original is temporarily unavailable.

## 13.3 Existing NO-GO

The previous Option A investigation established that native-body authenticity could not be proven through the inspected Lua boundary.

This finding remains valid.

A database does not automatically remove the indistinguishable-copy problem.

The revised design must prove a new safe lifecycle boundary before enabling automatic multiplayer ownership.

---

# 14. DATABASE DURABILITY & RECOVERY

Investigate:

- Atomic record updates.
- World-scoped storage.
- Schema migrations.
- Backup compatibility.
- Crash recovery.
- Save ordering.
- Corruption detection.
- Interrupted withdrawal.
- Interrupted restoration.
- Conflicting world/database generations.

Generation counters alone are insufficient to establish authenticity.

Do not claim that SQLite or a private file store provides atomicity across native world saves unless a coordinated transaction mechanism is proven.

## Recovery policy

When evidence is ambiguous:

- Preserve the permanent dog record.
- Disable privileged ownership actions.
- Quarantine the binding.
- Report a useful diagnostic.
- Do not delete the dog history.
- Do not create a replacement body automatically.

---

# 15. TASK ARBITRATION

Every dog must have one authoritative active task controller.

Proposed priority:

1. Immediate danger.
2. Critical health and survival needs.
3. Valid primary-owner commands