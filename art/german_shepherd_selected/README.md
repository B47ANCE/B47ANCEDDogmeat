# Selected German Shepherd — rig-only authoring checkpoint

Recorded runtime baseline: 0.2.0-dev.7
Asset revision: gsd-selected-rig-v001
Selection date: 2026-10-21

The user supplied the Meshy German Shepherd GLB and FBX archive and explicitly requested rigging only: preserve the model, use the raccoon's rigging contract, and eventually register a separate Dogmeat animal. This checkpoint implements the rigging/binding work. It does not replace any vanilla raccoon or activate a model in the current diagnostic. Runtime source/package version remains unchanged because this is an independently identified authoring checkpoint; the published 0.2.0-dev.7 payload is untouched.

## Outputs

- source/selected_shepherd_rigged.blend: editable, neutral 34-bone fitted rig with the supplied mesh/materials and packed textures.
- rigged/B47Dogmeat_GermanShepherd.glb: rigged interchange with all three original embedded JPEG payloads unchanged; no bundled animation clips.
- rigged/B47Dogmeat_GermanShepherd_embedded.fbx: skinned native-export candidate. Reopened in Blender with exact bone names/parents, vertex/triangle counts and positions. The FBX roundtrip retains the diffuse texture only; metallic/roughness and normal payloads remain intact in BLEND/GLB and supplied originals. No material conversion or texture editing was performed to work around FBX limitations.
- original/: byte-for-byte supplied GLB and every FBX ZIP member. The original supplied ZIP remains unchanged in Downloads; its SHA/CRC/member provenance is recorded. Large assets use scoped Git LFS; run git lfs pull after checkout.
- previews/: actual original, neutral-rig and small head/foreleg/tail deformation renders. These are Blender evidence, not PZ screenshots or a complete animation acceptance test.
- validation/: source hashes, native-reference fingerprints, rig/deformation/export evidence and an explicit file manifest.

No vertex, triangle, UV, texture pixel, mouth, ear, fur feature or topology was edited, retopologized or decimated. The model retains 1,425,959 vertices and 2,590,138 triangles. The before/after mesh/topology/UV hash is identical. Every vertex is bound, with at most four normalized influences.

## Raccoon contract and separate-animal boundary

The installed Raccoon_Body model declares animationsMesh = Raccoon; that animation mesh references Skinned/Raccoon_Body and animationDirectory = Raccoon. The animal definition uses animset = raccoon. The rig matches all 34 native bone names and parent relationships, including non-weighted roots/nubs; the source native skin uses 25 bones. Bone axes are derived from the installed technical skeleton data and joint positions are fitted to the Shepherd. Exact original raccoon bind-joint positions are not claimed, because the animal proportions differ. Full native clip deformation still needs acceptance testing.

Only the supplied dog and its compatible fitted armature are exported. No vanilla raccoon mesh, texture, animation clip, XML graph or raw game file is redistributed. Runtime integration must define a distinct Dogmeat model and animal type while referencing the installed Raccoon animation set. It must not overwrite Raccoon_Body, raccoonboar, raccoonsow or raccoonkit. The existing custom b47dogtest diagnostic remains unchanged during this rig-only slice. No new spawning, ownership, breeding, save schema or live task behavior is enabled here.

## Validation and limits

Blender 4.5.3 LTS, isolated background processes. Live Blender MCP was unavailable; no user scene was opened, replaced or edited. Source GLB starts unskinned and has no animation clips. Bone names/parents match independently through FBX reimport and GLB node inspection. FBX vertex position maximum error is 0; weight-sum maximum error is about 5.22e-8. GLB has one skin, 34 joints and no clips; all original image payload hashes match.

A small independent FK pose probe was rendered for head, foreleg and tail; it is not saved as a shipped animation or presented as native raccoon playback. No native locomotion/idle/death/carry sequence or PZ loading/scale/axes/attachment/remote-observer test was executed. The very high polygon count is preserved at the user's instruction and has no performance acceptance result. Do not call the asset game-ready from these checks.

Commands from repository root (use the verified local Blender/Python paths):

```text
blender --background --factory-startup --python art/german_shepherd_selected/source/inspect_selected.py -- --game-root <verified-game-root>
blender --background --factory-startup --python art/german_shepherd_selected/source/rig_selected.py
blender --background --factory-startup --python art/german_shepherd_selected/source/validate_fbx.py
blender --background --factory-startup --python art/german_shepherd_selected/source/export_glb.py
python -B art/german_shepherd_selected/source/check_asset.py
python -B scripts/check_versions.py --root .
python -B scripts/validate_m0r.py
python -B scripts/validate_foundation.py
python -B scripts/audit_public_push.py
git diff --cached --check
```

Rig/export builders protect existing authored outputs; create a separate asset revision for a rebuild. inspect_selected.py regenerates ignored local native-frame observations; validate_fbx.py can recheck the existing FBX without replacing it. The initial nonembedded FBX and unpacked reimport texture cache are ignored intermediates, not retained final deliverables. Raw native observations stay local.

No further paid Meshy job, texture generation, model editing, game/server launch, deployment or Workshop upload occurred. G6 NOT TESTED; G7 BLOCKED / NOT TESTED; stable G8 BLOCKED. Original user inputs, older Shepherd/Mastiff/Husky work, thumbnail and icon are preserved.
