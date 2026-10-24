# German Shepherd original motion checkpoint

Recorded project version: 0.2.0-dev.9. Asset revision: gsd-motion-v001.

Original locally authored dog motion on the existing raccoon bone hierarchy.
The original and both supplied coat GLBs, source geometry, UVs, weights and bind
matrices remain unchanged in `../german_shepherd_native`.

- `source/author_motion.py`: dog pivots, fixed-length gait, rest and tail health
  anchors, X export, matrix round-trip checks and actual Blender renders.
- `source/shepherd_motion.blend`: the shared rig and editable original actions;
  load the immutable model checkpoint through the script for textured previews.
- `source/build_animset.py`: our own action group and animation graph generator.
- `source/build_review_sheets.py`: review sheets/GIFs assembled from actual renders.
- `anims/`: 31 uniquely named X clips; no copied native animation tracks.
- `previews/`: both coats at eight walk and eight trot phases, five health anchors and four intermediate levels,
  rest transitions and death. The review floor is never a runtime model.
- `validation/`: geometry/gait/export checks, independent importer and source
  fingerprints. `manifest.json` binds this checkpoint's files.

The earlier direct-raccoon gait is historical rejected evidence. This checkpoint
corrects the offline movement candidate and adds optional tail-health presentation.
Runtime import, speed/contact, saves, health replication and multiplayer are NOT
TESTED. The model remains 2.59 million triangles; performance is unmeasured.

See [the current integration contract](../../docs/SHEPHERD_MOTION_AND_TAIL_HEALTH.md)
for configuration, authority boundaries, exact checks and the runtime test plan.
