# CODEX HANDOFF — English Mastiff Rigging, Animation & Native Asset Preparation

**Project:** B47ANCE'd Dogmeat  
**Technical Mod ID:** `B47ANCEDDogmeat`  
**Target Game:** Project Zomboid Build 42.21  
**Architecture:** Standalone, Lua-only, dedicated-server-first  
**Asset:** English Mastiff — Adult, Fawn, Black Mask  
**Source:** Previously generated Meshy AI model  
**Task:** Rigging, skinning, animation, optimization, and compatibility validation  
**Gameplay Implementation:** Not authorized  
**Native Test Carrier:** Preserve existing raccoon implementation

---

## 1. OBJECTIVE

Take the previously generated English Mastiff 3D model and prepare it for animation and eventual integration into B47ANCE'd Dogmeat.

Deliver:

- A complete quadruped skeleton.
- Correctly skinned mesh.
- Natural canine movement animations.
- Breed-appropriate heavy-body motion.
- Behavioral animations.
- Medical and injury animation foundations.
- Attachment points for collars, harnesses, armor, and bandages.
- Reusable canine animation conventions.
- Exported animation assets.
- A documented Project Zomboid compatibility assessment.

The Mastiff must retain its original breed appearance, coat, anatomy, proportions, and texture fidelity.

Do not regenerate the model unless the existing geometry is demonstrably unsuitable for rigging.

## 2. SOURCE ASSET INSPECTION

Before modifying anything, locate the existing English Mastiff assets.

Inspect:

- Original Meshy generation output.
- FBX, GLB, OBJ, or other available mesh files.
- Texture maps.
- Materials.
- UV coordinates.
- Polygon count.
- Mesh topology.
- Mesh orientation.
- Model dimensions.
- Existing skeleton, if present.
- Existing animation data, if present.

Identify whether the model is:

- Already rigged.
- Partially rigged.
- Static geometry only.
- Suitable for automatic rigging.
- In need of topology repair.

Preserve the original source asset unchanged.

Create working copies for processing.

If the model cannot be located, stop before generation or rigging and report the missing source.

## 3. TOOLCHAIN DISCOVERY

Inspect available tools and integrations.

Potential tools include:

- Blender.
- Blender Python scripting.
- Meshy AI rigging capabilities.
- Existing Dogmeat asset-processing scripts.
- Native Project Zomboid model tools.

Do not assume Meshy supports automatic quadruped rigging.

Verify actual provider capabilities before attempting remote operations.

Prefer a reproducible local Blender pipeline where available.

Do not install additional software or spend Meshy credits without authorization.

Document the selected toolchain and exact versions.

## 4. NATIVE PROJECT ZOMBOID ANIMATION AUDIT

Before finalizing the skeleton, inspect Build 42.21 animal animation requirements.

Determine:

- Supported model formats.
- Supported skeleton structures.
- Bone naming conventions.
- Animation clip formats.
- Animation registration requirements.
- Coordinate system.
- Scale.
- Root motion handling.
- Native animal animation states.
- Animation variable exposure.
- Client rendering requirements.
- Dedicated-server implications.

Do not assume that a generic Blender quadruped rig can be imported directly into Project Zomboid.

If the native animal animation system requires a particular skeleton, prioritize compatibility with the verified native format.

Do not modify native Java classes.

## 5. SKELETON DESIGN

Create an anatomically appropriate quadruped skeleton.

### Core skeleton

Include appropriate bones for:

- Root.
- Pelvis.
- Lower spine.
- Mid spine.
- Upper spine.
- Chest.
- Neck.
- Head.
- Jaw.
- Left and right ears.
- Tail base.
- Multiple tail segments.

### Front legs

Each front leg should support:

- Shoulder/scapula.
- Upper foreleg.
- Elbow.
- Forearm.
- Wrist/carpus.
- Paw.
- Optional toe controls.

### Rear legs

Each rear leg should support:

- Hip.
- Thigh.
- Stifle/knee.
- Lower leg.
- Hock.
- Paw.
- Optional toe controls.

Use anatomically appropriate joint directions.

Avoid humanoid armature assumptions.

## 6. SKINNING AND WEIGHT PAINTING

Bind the English Mastiff mesh to the skeleton.

Requirements:

- Smooth shoulder deformation.
- Natural elbow bending.
- Correct rear-leg articulation.
- Proper chest and abdomen deformation.
- Stable neck and head movement.
- Natural tail movement.
- Controlled facial and jowl deformation.
- No severe mesh clipping.
- No collapsing joints.
- No stretched paws.
- No detached geometry.

The Mastiff's loose skin and heavy jowls should move subtly without exaggerated cartoon deformation.

Use additional helper bones only when technically justified.

## 7. BREED-SPECIFIC MOTION PROFILE

The English Mastiff must feel physically heavy.

Movement characteristics:

- Deliberate acceleration.
- Strong weight transfer.
- Subtle body sway.
- Heavy but natural foot placement.
- Moderate stride length.
- Slower turning compared with athletic breeds.
- Reduced bounce during ordinary walking.
- Appropriate momentum during faster movement.

Do not make the Mastiff move like a small terrier, Greyhound, or German Shepherd.

Animation speed must be compatible with the game's actual movement speed.

Do not use animation playback speed to secretly alter gameplay statistics.

## 8. CORE LOCOMOTION ANIMATIONS

Create the following animation targets.

| Animation | Purpose |
|---|---|
| Idle Neutral | Default standing |
| Idle Breathing | Subtle breathing |
| Walk | Normal movement |
| Trot | Moderate movement |
| Run | Faster movement |
| Sprint / Gallop | Maximum appropriate movement |
| Turn Left | Directional transition |
| Turn Right | Directional transition |
| Start Moving | Acceleration |
| Stop Moving | Deceleration |
| Sit | Standing-to-sitting transition |
| Sit Idle | Seated state |
| Stand Up | Sitting-to-standing transition |
| Lie Down | Standing-to-lying transition |
| Lie Idle | Resting state |
| Get Up | Lying-to-standing transition |
| Sleep | Sleeping state |

Use looping clips where appropriate.

Transitions must avoid snapping between poses.

Foot placement should remain stable during stationary animations.

## 9. BEHAVIORAL ANIMATIONS

Create or plan:

- Bark.
- Growl.
- Whine.
- Pant.
- Sniff ground.
- Sniff object.
- Sniff air.
- Head tilt.
- Look around.
- Tail wag.
- Ears alert.
- Ears relaxed.
- Petting reaction.
- Eating.
- Drinking.
- Grooming.
- Scratching.
- Full-body shake.
- Urination.
- Defecation.
- Digging.
- Play bow.

Animations should support natural behavioral variation.

Avoid excessive repetitive movement.

## 10. TRAINING ANIMATIONS

Support Dogmeat's planned training system.

Required targets:

- Sit on command.
- Down on command.
- Stay.
- Heel.
- Recall.
- Place.
- Release.
- Target touch.
- Retrieve.
- Carry object.
- Drop object.
- Search.
- Silent alert.
- Guard stance.
- Disengage.
- Follow handler.

Some commands may reuse locomotion and idle clips rather than requiring entirely separate animations.

Do not create redundant clips unnecessarily.

## 11. WORKING-DOG ANIMATIONS

Prepare foundations for:

- Scent tracking.
- Hunting search.
- Retrieval.
- Carrying lightweight objects.
- Dragging bags.
- Dragging suitable loads.
- Guarding.
- Alerting.
- Navigating training obstacles.
- Climbing ramps.
- Entering doghouses.
- Exiting doghouses.
- Entering kennels.
- Exiting kennels.
- Using doggy doors.

Complex dragging, shared-load hauling, and native traversal remain experimental.

Do not claim those systems work merely because animation clips exist.

## 12. INJURY AND MEDICAL ANIMATIONS

Prepare condition-specific movement support.

Targets:

- Front-left limp.
- Front-right limp.
- Rear-left limp.
- Rear-right limp.
- Cautious walking.
- Pain reaction.
- Injured idle.
- Exhausted idle.
- Weak movement.
- Trembling.
- Scratching from irritation.
- Head shaking.
- Recovery transitions.

Injured locomotion must respect the actual affected limb.

Do not permit an injury animation to overwrite a critical movement restriction.

## 13. MEDICAL AND EQUIPMENT ATTACHMENTS

Create or document attachment points for:

- Collar.
- Lead.
- Harness.
- Backpack.
- Police K9 armor.
- Medical recovery harness.
- Protective cone.
- Head bandage.
- Neck bandage.
- Torso dressing.
- Front-leg wraps.
- Rear-leg wraps.
- Paw boots.
- Splints.
- Casts.

Attachment positions must remain stable during animations.

Do not create all equipment meshes during this task unless existing approved assets are available.

The deliverable is the rigging foundation and attachment specification.

## 14. ANIMATION PRIORITY

Define a deterministic animation priority model.

Suggested hierarchy:

1. Death/incapacitation.
2. Critical injury restrictions.
3. Active physical interactions.
4. Required locomotion.
5. Task-specific animations.
6. Medical discomfort.
7. Behavioral reactions.
8. Idle variation.

Animations must not conflict.

For example:

- Scratching must not interrupt active dragging.
- Barking should not force an impossible body pose.
- A severe limp must remain visible during movement.
- A dog using a doggy door should not simultaneously play an unrelated idle animation.

## 15. REUSABLE CANINE RIG

Investigate whether the English Mastiff rig can serve as one of several shared canine rig families.

Possible archetypes:

- Small companion.
- Terrier.
- Medium athletic.
- Shepherd.
- Retriever.
- Large mastiff.
- Giant working breed.

Do not assume a single rig works for every dog.

Preserve consistent naming and animation conventions where possible.

The English Mastiff should establish the large-mastiff archetype without forcing its proportions onto smaller breeds.

## 16. OPTIMIZATION

Optimize for real-time gameplay.

Initial targets:

- Approximately 8,000–15,000 triangles where feasible.
- 2048 × 2048 primary textures.
- Reasonable bone count.
- Efficient skinning.
- Minimal unnecessary materials.
- Reusable animation clips.
- No expensive simulated strand-fur systems.

These are starting targets, not verified Project Zomboid requirements.

Preserve visual quality while avoiding excessive geometry.

## 17. EXPORT AND ASSET ORGANIZATION

Use existing repository conventions.

Suggested staging structure:

assets/
  source/
    english_mastiff/
  rigged/
    english_mastiff/
  animations/
    english_mastiff/
  documentation/
    english_mastiff/

Keep original Meshy files intact.

Export working assets in verified suitable formats.

Include:

- Rigged mesh.
- Skeleton.
- Skin weights.
- Animation clips.
- Texture references.
- Material assignments.
- Attachment definitions.
- Toolchain metadata.
- Conversion instructions.

Do not restructure the repository unnecessarily.

## 18. VALIDATION

Perform automated and visual checks.

### Rig validation

- Required bones exist.
- Bone hierarchy is valid.
- No missing mesh bindings.
- Skin weights are normalized.
- No unintended disconnected geometry.
- Joint bending remains plausible.

### Animation validation

- Looping clips loop cleanly.
- Feet do not slide excessively.
- Paws remain grounded during idle.
- Sit/lie transitions are natural.
- Tail and ears move appropriately.
- Limb-specific limps use correct sides.
- No severe mesh clipping.

### Export validation

- Files reopen successfully.
- Skeleton remains intact.
- Animation clips retain correct names.
- Materials and textures remain linked.
- Scale and orientation are preserved.

### Native compatibility

- Document whether the model is actually loadable in Project Zomboid.
- Do not mark native compatibility PASS without a game runtime test.
- Do not mark dedicated multiplayer rendering PASS without a dedicated test.

## 19. REQUIRED DELIVERABLES

1. Rigged English Mastiff model.
2. Complete quadruped skeleton.
3. Skin-weighted mesh.
4. Core locomotion animation set.
5. Behavioral animation set, where feasible.
6. Injury animation foundations.
7. Equipment attachment definitions.
8. Exported animation assets.
9. Rigging and animation validation report.
10. Project Zomboid compatibility assessment.
11. Remaining blocker list.

## 20. DEVELOPMENT RESTRICTIONS

- Preserve the original Meshy source.
- Preserve the current raccoon test carrier.
- Do not implement dog spawning.
- Do not modify ownership or persistence code.
- Do not modify native Java classes.
- Do not install new dependencies without approval.
- Do not spend additional Meshy credits without approval.
- Do not deploy to a live server.
- Do not publish to Steam Workshop.
- Do not claim runtime compatibility without testing.
- Preserve unrelated working-tree changes.
- Verify the current project version rather than inventing one.

## 21. IMMEDIATE EXECUTION INSTRUCTIONS

1. Locate the English Mastiff model.
2. Inspect its mesh and textures.
3. Identify the available rigging toolchain.
4. Audit native Build 42 animal animation requirements.
5. Select a compatible skeleton strategy.
6. Rig and skin the model.
7. Produce the core animation set.
8. Prepare behavior and medical animation foundations.
9. Validate geometry, rigging, and exports.
10. Stage assets without modifying active gameplay.
11. Return a report identifying completed assets and unresolved native integration requirements.

If native skeleton compatibility cannot be established, produce a clearly labeled intermediate rig rather than falsely claiming a game-ready asset.

---

# FINAL DIRECTIVE

Transform the existing English Mastiff Meshy model into a believable, fully rigged canine character with a reusable large-breed animation foundation.

The Mastiff must move with the physical weight and proportions appropriate to its breed.

Maintain clean animation topology, accurate deformation, and compatibility with future Dogmeat training, veterinary, grooming, equipment, and working-dog systems.

**Deliver validated rigged assets without altering the current standalone gameplay foundation.**