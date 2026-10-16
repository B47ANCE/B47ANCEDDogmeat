# CODEX HANDOFF — English Mastiff 3D Model via Meshy AI

**Project:** B47ANCE'd Dogmeat  
**Technical Mod ID:** `B47ANCEDDogmeat`  
**Target:** Project Zomboid Build 42.21  
**Architecture:** Standalone, Lua-only, dedicated-server-first  
**Asset:** Adult English Mastiff  
**Asset Type:** Original canine 3D model, textures, and supporting metadata  
**Generation Provider:** Meshy AI  
**Workflow:** Codex → Meshy integration → Asset inspection → Dogmeat asset staging  
**Gameplay Implementation:** Not authorized by this handoff

---

## 1. Objective

Use the user's existing Meshy AI subscription and configured integration to generate an anatomically accurate English Mastiff model suitable for eventual use in B47ANCE'd Dogmeat.

The model must accurately represent the breed's enormous size, broad head, deep chest, muscular frame, loose skin, and short coat.

Generate a clean, optimized 3D asset that can be prepared for Project Zomboid's native animal animation system.

Do not automatically integrate the model into the active mod or replace the existing raccoon test carrier.

## 2. Meshy Integration Discovery

Before generating anything:

1. Inspect the available Meshy AI integration or CLI configuration.
2. Identify supported generation methods.
3. Verify authentication without printing API keys.
4. Identify the available subscription features and generation credit requirements.
5. Determine whether text-to-3D, multi-image-to-3D, remeshing, texturing, and rigging are supported.
6. Inspect existing Dogmeat asset conventions.
7. Check whether reusable canine rigs, skeletons, or animations already exist.

Do not assume Meshy has a particular CLI command or API endpoint.

Use the actual installed integration's documented commands.

Do not install additional dependencies without authorization.

Before consuming paid Meshy credits, report the expected cost if available and obtain approval unless the user has already authorized that specific generation.

## 3. Primary Meshy Generation Prompt

Create a realistic, anatomically accurate adult English Mastiff dog as a high-quality, game-ready 3D character for Project Zomboid.

The dog must be unmistakably an English Mastiff, not a Bullmastiff, Cane Corso, Boerboel, or other mastiff-type breed.

### Anatomy

- Very large, heavy-boned adult English Mastiff.
- Massive, broad, square-shaped head.
- Wide skull with prominent cheeks.
- Short, broad, deep muzzle.
- Pronounced but natural facial wrinkles.
- Slightly loose jowls and lips.
- Dark brown, expressive eyes.
- Medium-sized V-shaped ears hanging naturally beside the head.
- Thick, powerful neck.
- Very broad shoulders.
- Deep, wide chest.
- Large ribcage.
- Long, strong torso.
- Substantial muscular hindquarters.
- Thick, sturdy legs with large natural paws.
- Heavy but proportionate body mass.
- Long, thick tail tapering toward the tip and hanging naturally downward.

The dog should appear enormous and powerful while retaining believable canine anatomy.

Avoid extreme obesity, exaggerated bodybuilding proportions, or cartoonishly oversized features.

### Coat

Generate the classic fawn English Mastiff coloration.

- Short, dense, smooth coat.
- Warm golden-fawn body.
- Dark black muzzle and facial mask.
- Dark shading around the eyes.
- Naturally darker ears.
- Subtle variations in tan and fawn across the body.
- Realistic short-fur texture.
- Natural coat color transitions.
- No artificial shine or plastic appearance.

The coat should be represented primarily through textures and normal maps rather than individually modeled fur.

### Pose

- Full-body standing quadruped.
- Neutral, relaxed posture.
- All four paws naturally planted on the same plane.
- Head facing forward.
- Mouth closed.
- Calm expression.
- Ears relaxed.
- Tail hanging naturally.
- Legs positioned for later skeletal rigging.
- No exaggerated movement or dramatic posing.

### Geometry

- Complete closed body mesh where appropriate.
- Clean topology.
- Correctly separated limbs.
- Anatomically correct joints.
- No fused legs or overlapping duplicate geometry.
- Defined muzzle, ears, paws, and tail.
- Appropriate edge flow around joints.
- Optimized for real-time game rendering.
- Suitable for later animation and deformation.

### Textures

Generate realistic PBR textures.

Prioritize:

- Base color/albedo.
- Normal map.
- Roughness.
- Appropriate material definition.

The model should remain visually recognizable at an isometric gameplay distance.

### Presentation

One complete adult English Mastiff.

No collar, leash, harness, armor, clothing, accessories, scenery, props, platform, text, or additional animals.

Neutral background.

Prioritize breed accuracy, anatomy, clean geometry, and game optimization.

---

## 4. Negative Prompt

Avoid:

Cartoon, stylized, fantasy creature, Cane Corso, Bullmastiff, Boerboel, Great Dane, oversized ears, erect ears, narrow head, long pointed muzzle, slim athletic shepherd build, exaggerated wrinkles, excessive loose skin, extreme obesity, deformed joints, extra limbs, missing paws, duplicate tail, curled tail, exaggerated muscles, long fur, fluffy coat, plastic textures, open mouth, tongue hanging out, sitting, running, aggressive pose, clothing, collar, harness, accessories, scenery, multiple dogs.

---

## 5. Target Asset Specifications

| Property | Target |
|---|---|
| Breed | English Mastiff |
| Age | Adult |
| Initial coat | Fawn with black mask |
| Pose | Neutral standing |
| Geometry | Optimized, riggable |
| Triangle target | Approximately 8,000–15,000 |
| Texture resolution | 2048 × 2048 |
| Materials | PBR |
| Preferred export | FBX or GLB |
| Rigging | Deferred pending native skeleton audit |
| Animations | Deferred |
| Scale | Calibrate against verified Dogmeat/native animal scale |

These are initial asset targets, not verified Build 42 compatibility specifications.

If the generation tool cannot satisfy them, report the limitation instead of silently claiming compliance.

## 6. Additional Coat Variants

Design the asset pipeline so the same compatible English Mastiff body can eventually support:

- Fawn with black mask.
- Apricot with black mask.
- Brindle with black mask.

Do not generate three separate meshes unless geometry differences require them.

The first requested deliverable is the classic fawn model.

## 7. Asset Inspection

After generation, inspect:

- Full-body anatomy.
- Breed accuracy.
- Polygon and triangle counts.
- Mesh topology.
- UV mapping.
- Texture availability.
- Material assignments.
- Orientation.
- Scale.
- Rigging suitability.
- Visible defects.

Pay particular attention to the Mastiff's head, muzzle, jowls, ears, chest, and legs.

Reject obvious breed mismatches and major geometry defects.

Do not automatically consume additional paid credits for retries without authorization.

## 8. Project Zomboid Compatibility Audit

Investigate:

- Native animal model formats.
- Model registration.
- Skeleton requirements.
- Animation compatibility.
- Bone naming and hierarchy.
- Material handling.
- Scale and orientation.
- Texture constraints.
- LOD requirements.
- Client asset loading.
- Dedicated-server implications.

Meshy exports are intermediate assets.

Do not claim a GLB or FBX is immediately usable by Project Zomboid without conversion and runtime proof.

No Java modifications are permitted.

## 9. Asset Staging

Place generated assets in an isolated development directory, following existing repository conventions.

Suggested organization:

assets/
  source/
    english_mastiff/
  processed/
    english_mastiff/
  documentation/
    english_mastiff/

This is a suggested structure, not permission to restructure the repository.

Retain:

- Original Meshy output.
- Processed mesh.
- Texture files.
- Generation settings.
- Prompt.
- Asset metadata.
- Model inspection report.
- Relevant generation job identifiers.

Do not commit credentials or sensitive provider data.

Respect repository asset-size and public-distribution rules.

## 10. Dogmeat Gameplay Compatibility

The model must not introduce or modify gameplay statistics.

Appearance is independent from:

- Dog identity.
- Breed ancestry records.
- Weight.
- Strength.
- Fitness.
- Endurance.
- Personality.
- Anxiety.
- Confidence.
- Training.
- Health.
- Movement authority.
- Collision.
- Ownership.
- Relationships.

Do not derive gameplay hitboxes or movement capabilities from an unverified cosmetic mesh.

The model must be compatible with the planned injury, bandage, grooming, and equipment visual systems where technically feasible.

## 11. Validation

Report:

- Meshy generation success/failure.
- Generation cost or credit usage, if available.
- Asset filenames and hashes.
- Triangle count.
- Texture resolution.
- Material inventory.
- Model dimensions.
- Geometry defects.
- Breed fidelity assessment.
- Rigging readiness.
- Project Zomboid compatibility status.

Use PASS, FAIL, BLOCKED, or NOT TESTED.

An asset-generation success does not establish in-game compatibility.

## 12. Restrictions

- Do not modify the existing raccoon test carrier.
- Do not implement dog spawning.
- Do not implement animations or rigging without a verified target.
- Do not modify game binaries.
- Do not introduce Java mods.
- Do not deploy to the live game or server.
- Do not publish to Steam Workshop.
- Do not modify ownership or persistence code.
- Do not alter the current project version merely because an asset was generated.
- Preserve unrelated working-tree changes.

## 13. Required Deliverables

1. Generated English Mastiff model.
2. Available PBR textures.
3. Meshy generation metadata.
4. Asset inspection report.
5. Native model compatibility assessment.
6. Recommended conversion and rigging steps.
7. List of remaining blockers.

## 14. Execution Order

1. Inspect the Meshy integration.
2. Verify account access and generation capabilities.
3. Review Dogmeat asset conventions.
4. Confirm expected paid generation cost.
5. Submit the approved English Mastiff prompt.
6. Retrieve the generated model.
7. Inspect geometry and textures.
8. Stage assets separately from active runtime files.
9. Assess Project Zomboid compatibility.
10. Return the model and inspection report.

**Do not replace the raccoon or activate the English Mastiff in-game during this task.**

---

# Final Directive

Generate a realistic adult English Mastiff with a classic fawn coat and black facial mask.

The dog must have the massive, powerful proportions characteristic of the breed while remaining anatomically believable and suitable for future skeletal animation.

Preserve Dogmeat's standalone architecture and current gameplay foundation.

**The deliverable is an inspected 3D asset, not a playable canine implementation.**