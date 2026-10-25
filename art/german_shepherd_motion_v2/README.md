# German Shepherd skin and motion revision 2

Recorded Project Version: 0.2.0-dev.10

This replaces the user-rejected dev.9 candidate while retaining historical files.
The original coat and both variations keep their geometry, topology, UVs, normals,
textures and raccoon bone/bind contract. Only skin attributes change in GLBs.
All motion is authored locally.

- `source/shepherd_reweighted.blend`: all three editable revised skins.
- `source/shepherd_motion.blend`: rig and 47 original actions.
- `source/build_skin.py`: connected-region weights and lossless patching of
  only JOINTS_0/WEIGHTS_0 in the previous GLBs.
- `source/author_motion.py`: fitted walk/trot/rest and tail-health motion.
- `previews/`: cycle and pose reviews, not game screenshots.
  `rest-review.gif` replays LieDown forward and backward for inspection;
  it is not a recording of the GetUp clip.
- `validation/`: exact fingerprints and offline observations.

See [current integration and evidence](../../docs/SHEPHERD_MOTION_AND_TAIL_HEALTH.md).
The inherited 2.59-million-triangle sculpt is not optimized. Attachment/fold
compression remains a review concern. PZ import, speed, contact, transitions,
performance and multiplayer remain NOT TESTED. No deployment or publication.
