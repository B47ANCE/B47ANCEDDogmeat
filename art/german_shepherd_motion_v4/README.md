# German Shepherd canine movement revision 4

Recorded Project Version: 0.2.0-dev.12

Motion-only revision using the frozen v3 original/Coat1/Coat2 GLBs and skin
weights. No geometry, topology, UV, texture, native bind or animal identity change.
The 47 clip names remain compatible with the existing Shepherd action/animation
graphs. Vanilla raccoons and the separate persistence test carrier are unchanged.

- Both rear stifle/hock landmarks move 0.04 source units forward along -BACK.
  Hip/paw landmarks stay fixed; calf length is preserved.
- Walking order is LH, LF, RH, RF. Run is a diagonal trot. Paw recovery meets
  support velocity smoothly, and rest wrist interpolation preserves length.
- The neutral head faces torso-forward. Look retains independent full yaw/pitch,
  with half yaw shared by Neck to reduce ruff stretching.
- Tail segments sway laterally with a fixed root; existing health height and
  nine blend anchors retain their meaning. Dead remains static.

Editable sources:

- `source/shepherd_motion.blend`: native rig and all original actions.
- `source/shepherd_head_controls.blend`: linked, forward-neutral head control.
  Select `GSD_Head_Control`; local Z is yaw, local X pitch. Zero restores forward.
- `source/shepherd_joint_guides.blend`: nondeforming joint guides over the linked
  model. Both `Stifle_Hock` guides use the forward adjustment. Edit Mode and G
  move guides; save a working copy to preserve this checkpoint. These guide
  bones do not change the native export skeleton or automatically rebake clips.
- Keep the frozen sibling `german_shepherd_motion_v3/source/shepherd_reweighted.blend`
  available: the small control/guide scenes link its protected mesh data.

`previews/` contains actual rendered frames and walk/trot/look/rest loops.
`validation/` contains offline decoded-asset checks, not PZ playback evidence.
The manifest binds authoring sources, external frozen inputs and outputs by SHA-256.

Visual acceptance remains pending. The resting rear ankle/haunch contour is
still stiff, the ruff compresses during the large correction from the supplied
sideways head, and an extended tail exposes the source's narrow proximal shape.
Numerical bounds do not certify anatomical realism. Each model retains 2.59M
triangles. PZ import, state blending, speed/foot sliding, health replication,
performance, saves and dedicated multiplayer remain NOT TESTED.

See [research](../../docs/CANINE_MOVEMENT_RESEARCH_AUDIT.md) and
[current integration and validation](../../docs/SHEPHERD_MOTION_AND_TAIL_HEALTH.md).
Ownership/live tasks remain disabled. No deploy, launch, merge or publication.
