# CODEX HANDOFF — Meshy AI English Mastiff with Complete Animatable Anatomy

**Project:** B47ANCE'd Dogmeat  
**Mod ID:** `B47ANCEDDogmeat`  
**Target:** Project Zomboid Build 42.21  
**Provider:** Meshy AI, through the configured Codex integration  
**Asset:** Adult English Mastiff  
**Purpose:** Fully modeled, riggable canine character with functional mouth anatomy  
**Architecture:** Standalone, Lua-only, dedicated-server-first

## 1. Objective

Generate a realistic, anatomically accurate adult English Mastiff with complete external anatomy and sufficient modeled internal mouth structures for advanced canine animation.

The model must be suitable for future:

- Biting and releasing.
- Barking and growling.
- Panting.
- Drinking.
- Eating and chewing.
- Licking.
- Fetching and carrying objects.
- Yawning.
- Whining and vocalization.
- Sniffing.
- Facial expressions.
- Walking, running, sitting, lying down, and sleeping.
- Grooming and scratching.
- Injury and medical animations.

Prioritize animation-ready anatomy over a visually impressive but unusable static sculpture.

## 2. Meshy Integration

Codex must inspect the configured Meshy AI integration and determine the available generation, remeshing, texturing, and export capabilities.

Use the user's existing Meshy subscription.

Do not assume Meshy automatically creates rig-ready mouth interiors, separate tongues, jaw bones, or animation controls.

If the provider cannot generate these reliably, produce the best available base mesh and identify the exact Blender or other local modeling steps required.

Do not claim the asset is fully animation-ready until its geometry and deformation capabilities have been inspected.

## 3. Primary Meshy Generation Prompt

Create a highly realistic, anatomically accurate, full-body adult English Mastiff dog as a game-ready 3D character intended for advanced skeletal and facial animation.

This must be a genuine English Mastiff, not a Bullmastiff, Cane Corso, Boerboel, Great Dane, or generic mastiff-type dog.

### Breed anatomy

- Very large, powerful, heavy-boned adult English Mastiff.
- Massive, broad, square-shaped head.
- Wide skull and pronounced cheek structure.
- Short, broad, deep muzzle.
- Natural facial wrinkles and loose skin folds.
- Heavy but realistic jowls and lips.
- Thick, muscular neck.
- Broad shoulders and deep chest.
- Large ribcage and substantial torso.
- Powerful front and rear legs.
- Large, anatomically accurate paws.
- Natural long tail hanging downward.
- Medium-sized folded V-shaped ears.
- Deep brown eyes and black nose.

The dog should look massive and physically powerful without appearing obese, exaggerated, or cartoonish.

### Complete mouth and jaw anatomy

The mouth must be modeled as functional three-dimensional geometry, not a flat texture.

Include:

- Anatomically shaped upper jaw.
- Separate lower jaw/mandible suitable for rotation.
- Complete mouth cavity.
- Upper and lower gum structures.
- Distinct upper and lower teeth.
- Prominent canine teeth.
- Incisors.
- Premolars and molars.
- Fully modeled tongue.
- Tongue root, middle section, and tip.
- Hard palate.
- Dark interior mouth surfaces.
- Flexible lips and jowls.
- Realistic mouth corners.

The jaw must be capable of opening and closing without severe mesh intersection.

The tongue must have sufficient geometry to support extending, curling, retracting, and contacting objects.

The lips and jowls must support subtle deformation during barking, panting, biting, and chewing.

Teeth must be actual geometry, not painted details.

### Facial animation readiness

Prepare geometry suitable for:

- Jaw opening and closing.
- Lip movement.
- Jowl movement.
- Tongue extension.
- Tongue curling.
- Panting.
- Yawning.
- Growling.
- Barking.
- Licking.
- Chewing.
- Biting.
- Object gripping.
- Eye blinking.
- Eye movement.
- Ear movement.
- Nose and muzzle expressions.

Do not bake the facial expression into one fixed pose.

### Body animation readiness

Create clean anatomical geometry around:

- Neck.
- Shoulders.
- Elbows.
- Wrists.
- Front paws.
- Spine.
- Hips.
- Knees.
- Hocks.
- Rear paws.
- Tail.

The mesh must support quadruped locomotion and natural weight transfer.

### Coat

Use a traditional English Mastiff fawn coat:

- Warm golden-fawn body.
- Deep black facial mask.
- Dark ears.
- Subtle shading around the eyes.
- Short, dense, smooth fur.
- Realistic PBR fur textures.
- Natural roughness and surface detail.

Avoid excessive individually modeled fur.

The model should be compatible with later Brindle and Black texture variants using the same UV layout.

### Neutral pose

- Full-body standing quadruped.
- All four paws naturally planted on a level surface.
- Head facing forward.
- Mouth gently closed in a neutral resting position.
- Tail hanging naturally.
- Ears relaxed.
- No dramatic expression.
- No exaggerated body posture.

The mouth interior must remain complete and accessible for later rigging even though the default pose has a closed mouth.

### Geometry requirements

- Clean, animation-friendly topology.
- Distinct jaw, tongue, and tooth geometry.
- Properly connected or intentionally separated anatomical components.
- Good edge flow around mouth corners, cheeks, jaw, neck, and joints.
- No fused upper and lower jaws.
- No teeth merged into the tongue.
- No tongue merged into the mouth floor.
- No collapsed mouth cavity.
- No duplicate or missing limbs.
- No intersecting internal mouth geometry in neutral pose.
- Suitable for later skeletal rigging, skinning, and facial controls.

### Presentation

Generate one complete adult English Mastiff.

No collar, leash, armor, harness, clothing, accessories, scenery, platform, text, or additional animals.

Prioritize accurate anatomy, functional mouth geometry, rigging suitability, and realistic appearance.

## 4. Negative Prompt

Avoid:

Cartoon, stylized, fantasy animal, Cane Corso, Bullmastiff, Boerboel, Great Dane, narrow muzzle, pointed face, erect ears, slim body, excessive obesity, exaggerated wrinkles, permanently open mouth, permanently exposed tongue, painted teeth, flat mouth texture, missing gums, missing tongue, fused jaw, fused teeth, malformed mouth cavity, deformed joints, extra limbs, missing paws, duplicate tail, unrealistic proportions, plastic fur, exaggerated facial expression, clothing, accessories, scenery, multiple dogs.

## 5. Mouth Anatomy Acceptance Requirements

Codex must inspect the resulting model for actual geometry.

| Component | Requirement |
|---|---|
| Upper jaw | Anatomically defined and stable |
| Lower jaw | Separately controllable through later rigging |
| Mouth cavity | Actual recessed 3D geometry |
| Teeth | Separate geometry, recognizable canine dentition |
| Tongue | Modeled with sufficient topology for deformation |
| Gums | Visible upper and lower gum surfaces |
| Lips | Suitable topology for opening and facial movement |
| Jowls | Deformable without major clipping |
| Mouth corners | Appropriate edge loops for opening |
| Palate | Actual interior surface |

If a component is missing, mark it FAIL or INCOMPLETE.

Do not substitute a texture-only representation while claiming full modeled anatomy.

## 6. Proposed Facial Rig

Prepare for a later rig containing:

- Head.
- Lower jaw.
- Tongue root.
- Tongue middle.
- Tongue tip.
- Upper lip controls.
- Lower lip controls.
- Left and right jowl controls.
- Left and right ear controls.
- Left and right eyelid controls.
- Left and right eye controls.

Use verified Project Zomboid compatibility requirements before finalizing the actual bone hierarchy.

Additional facial bones or shape keys may be used where supported.

## 7. Animation Requirements

The finished model should eventually support the following animation groups.

### Mouth and facial actions

- Bite.
- Release bite.
- Bark.
- Growl.
- Pant.
- Lick nose.
- Lick object.
- Lick player.
- Drink water.
- Eat food.
- Chew.
- Yawn.
- Whine.
- Sniff.
- Hold retrieved object.
- Release retrieved object.

### Body actions

- Idle.
- Walk.
- Trot.
- Run.
- Sit.
- Down.
- Stay.
- Sleep.
- Get up.
- Tail wag.
- Scratch.
- Shake.
- Urinate.
- Defecate.
- Limp.
- Carry object.
- Drag object.

This task generates the geometry foundation. Do not claim these animations already exist.

## 8. Texture and Material Requirements

Target:

- 2048 × 2048 primary textures.
- PBR base color.
- Normal map.
- Roughness map.
- Separate appropriate mouth materials.
- Teeth material.
- Tongue material.
- Gum material.
- Eye material.

Avoid excessive material draw calls.

Preserve consistent UV coordinates for later coat variants.

## 9. Optimization

The complete model should remain suitable for real-time gameplay.

The previous 8,000–15,000 triangle target may need revision because the mouth interior now requires actual geometry.

Codex should inspect the generated result and propose separate budgets for:

- External body.
- Head and facial geometry.
- Teeth.
- Tongue.
- Mouth cavity.
- Optional detail levels.

Do not sacrifice required mouth anatomy merely to satisfy an arbitrary polygon count.

Investigate level-of-detail strategies for isometric gameplay.

## 10. Validation

Perform visual and geometry checks.

Required checks:

- Jaw can rotate without severe clipping.
- Tongue is geometrically independent enough to deform.
- Teeth remain positioned correctly.
- Mouth interior is not hollow or missing.
- Mouth closes naturally.
- Face retains recognizable English Mastiff proportions.
- Body remains anatomically correct.
- Model has valid UVs.
- Materials are properly assigned.
- No severe nonmanifold or disconnected defects.
- Asset can be reopened in the selected modeling software.

Do not mark actual animation compatibility PASS until rigging and animation tests are completed.

## 11. Project Zomboid Compatibility

Audit Build 42.21 native animal model requirements.

Determine:

- Skeleton compatibility.
- Animation format.
- Bone limits.
- Facial bone support.
- Jaw animation support.
- Tongue animation support.
- Material compatibility.
- Model scale.
- Export format.
- Runtime asset loading.

If Project Zomboid does not support the full facial rig, preserve the complete source model and document a reduced runtime rig.

Do not modify native Java classes.

## 12. Deliverables

1. English Mastiff full-body 3D model.
2. Complete modeled mouth interior.
3. Separate or riggable lower jaw.
4. Modeled tongue, teeth, gums, and palate.
5. Original fawn coat textures.
6. PBR material inventory.
7. Geometry inspection report.
8. Facial rigging feasibility report.
9. Project Zomboid compatibility assessment.
10. Remaining modeling and animation requirements.

## 13. Restrictions

- Do not modify Dogmeat gameplay code.
- Do not modify ownership or persistence systems.
- Do not replace the raccoon test carrier.
- Do not implement spawning.
- Do not modify game binaries.
- Do not introduce Java mods.
- Do not deploy to the live server.
- Do not publish to Workshop.
- Preserve original source assets and unrelated working-tree changes.
- Do not consume additional paid Meshy credits without approval.

## Final Directive

Generate a complete, anatomically accurate English Mastiff designed for advanced canine animation.

**The mouth must be real modeled geometry, including a movable lower jaw, teeth, gums, tongue, and interior cavity.**

The model must support eventual biting, drinking, panting, licking, barking, chewing, fetching, and carrying animations.

If Meshy cannot produce the required internal anatomy, document the missing geometry and prepare a precise follow-up modeling plan.

**Do not label a static model animation-ready without verifying its anatomy and topology.**