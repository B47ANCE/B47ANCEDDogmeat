# German Shepherd native rig candidate

Asset revision: gsd-native-rig-v001

Recorded project version: 0.2.0-dev.8

The original selected Shepherd and both supplied coat variations are bound to
one 34-node raccoon hierarchy, with 25 deforming bones and four influences per
vertex. Each original mesh and UV layout is retained exactly in the editable
BLEND. GLB positions include reversible object alignment; the validator inverts
that alignment before comparing every triangle corner and UV to the input.
Source originals remain unchanged under `../german_shepherd_selected`.

- `source/shepherd_native.blend`: all three meshes and the shared armature.
- `models/`: separate self-contained skinned GLBs, with no animation clips.
- `previews/`: actual neutral and locally sampled native pose renders.
- `validation/native-bind.json`: matrix, geometry/UV and skinning results.
- `validation/clip-samples.json`: installed clip fingerprints and sample times.
- `manifest.json`: retained checkpoint file hashes.

The bind reference is native Rac_Idle01 frame zero. Own inverse binds are used
by the installed engine while sharing the native animation library. The nine
unweighted hierarchy helpers are retained as nodes, not extra anatomical joints.
Both coat meshes have 2,590,138 triangles. No simplification or PBR repainting was
performed. PZ's animal shader uses the separately mapped diffuse texture only.
The original GLB's JPEG is decoded to pixel-identical RGB PNG for that native
texture mapping; `validation/original-diffuse.json` records the conversion.

**Visual HOLD:** native locomotion still distorts the long legs and tail. These
are inspectable rig/integration candidates, not completed canine animation or
game-performance proof. The raccoon remains a separate unchanged animal. All
three new native type IDs and the remaining runtime test procedure are documented
in [the integration contract](../../docs/GERMAN_SHEPHERD_INTEGRATION.md).

Reproduction uses Blender 4.5.3 LTS. `build_native.py -- --game-root <installed
game>` requires a fresh output checkpoint and preserves the input files. Local
`validate_native.py` reimports every original to compare exact data. Local
`preview_native_clips.py` reads installed animation data in memory, saves only
renders/fingerprints and never exports native clips. No PZ process is launched.

Offline checks do not establish PZ/SP/dedicated playback, save/load or performance.
The published Workshop dev.7 item has not been updated by this work.
