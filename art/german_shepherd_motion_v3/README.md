# German Shepherd rest and head revision 3

Recorded Project Version: 0.2.0-dev.11

This checkpoint continues the supplied original coat and both coat variations.
Geometry, topology, normals, UVs, textures, native bone hierarchy and inverse
binds remain unchanged. Runtime models only receive revised skin attributes.
The dev.8, dev.9 and dev.10 checkpoints remain immutable.

- `source/shepherd_reweighted.blend`: all three editable skins.
- `source/shepherd_motion.blend`: native rig and 47 locally authored actions.
- `source/shepherd_head_controls.blend`: small editable scene linked to the
  reweighted source in this directory. Select `GSD_Head_Control`; rotate local
  Z for yaw or local X for pitch. Zero rotation restores the supplied head pose.
  Keep both BLEND files together. Independent yaw +/-25 degrees and pitch
  +/-15 degrees are the inspected ranges, not unlimited deformation guarantees.
- `source/head_rig.py`: source-fitted atlas and continuous Head/Neck field.
  The face, mouth and ears follow Head together; ruff weights transition to
  Neck. The authoring control/constraint is not exported into the game.
- `source/author_motion.py`: fitted motion using the unchanged native skeleton.
- `previews/`: actual Blender frames; `look.gif` shows the authored head cycle.
  `rest-review.gif` uses actual LieDown and GetUp frames.
- `validation/`: reproducible offline observations and exact input hashes.

The supplied skull points in a different direction from the torso. Its fitted
atlas pivot and pitch axis permit rotation independently of the Neck bone.
The Look clip turns through +/-25 degrees yaw and +/-12 degrees pitch. Eating
uses a separate neck bend and head nod. This is authored presentation, not a
new gameplay aiming or ownership controller.

The rest correction uses rear paw shift +.16 BACK, hock-up .135 and outward
knee pole .50. This removes the acute tuck without changing leg weights. Dead
uses .03 UP / .10 BACK rear relaxation. Some angular hip/ankle contours remain;
these poses are for visual/runtime review rather than a claim of finished polish.

See [current integration and evidence](../../docs/SHEPHERD_MOTION_AND_TAIL_HEALTH.md).
PZ rendering, transition blending, speed, contact, performance and multiplayer
are NOT TESTED. Each model retains 2.59 million triangles. No deployment,
game/server launch, merge or Workshop publication is part of this iteration.
