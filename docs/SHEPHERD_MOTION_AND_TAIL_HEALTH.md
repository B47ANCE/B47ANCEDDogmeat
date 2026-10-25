# Shepherd motion and tail health

Project Version: 0.2.0-dev.10

Compatible visual correction within the additive 0.2.0 MINOR prerelease.
The user rejected dev.9's animations and tail on 2026-10-24. Its numerical
checks established export contracts, not acceptable deformation. The dev.8
native rig and dev.9 motion directories remain unchanged historical checkpoints.

## Current source

`art/german_shepherd_motion_v2` contains revised skin weights for the original
Shepherd and both supplied coats, and 47 locally authored motion clips. Geometry,
topology, normals, each coat's UV layout, textures, bone names/hierarchy and
inverse binds remain unchanged. Runtime GLBs change only JOINTS_0 and WEIGHTS_0
attribute bytes. The source BLEND retains all three editable skins; the smaller
motion BLEND contains the rig and actions.

The supplied stance is asymmetric and rotated about 14.65 degrees from the
previously assumed axis. Both rear paws have positive source Y: a sign-only
left/right split assigned both to one leg. Broad spatial tail masks also assigned
hindquarter fur to the tail, while some tail vertices followed the rear legs.

The correction uses fitted landmarks, connected tail/lower-leg regions and
continuous surface-distance blending at attachments. Continuous joint planes
distribute elbow/knee/wrist/hock weights; continuous four-influence reduction
avoids abrupt changes when the active bone set changes. Connectivity welding is
analysis only; source vertices are not welded or moved.

Motion uses reachable limb targets, continuous toe-off rotation, modest shoulder
and pelvis movement, a four-beat walk and diagonal trot. Rest settles forequarters
and haunches in stages, with flat paws and a grounded tail curve. Death rolls into
a static pose with separately relaxed limbs and a fitted head turn; its floor
correction evaluates the actual weighted surface.
These remain authored candidates, not production animation or native speed proof.

The three existing types retain their own `b47germanshepherd` animation set and
action group, with the 34-node/25-deforming-bone raccoon contract. Vanilla raccoon
definitions and clips are untouched. No native motion tracks, meshes/weights,
Java classes or third-party animation are shipped. Native navigation owns
movement; Translation_Data stays fixed. Shepherd climbing remains disabled.

## Health cue and authority

`B47ANCEDDogmeat.TailHealthIndicator` remains a server sandbox boolean, default
true, with English fallback text in all 29 language folders. No new configuration
or save schema is introduced in dev.10.

- High native health raises the tail; low health lowers it.
- Unknown/invalid health and a disabled option select neutral.
- Standing, looking, walking and trotting use the cue. Rest, eating, hit and
  death states use their authored poses.
- All three Shepherd types qualify. This does not assert taming or ownership.

The unchanged client module reads native `getHealth()` and writes only its local
animation scalar. Native simulation can delegate animal control to clients;
replicated native health is not proof of strict server authority. This feature
has no health setter, command, persistence field, ownership admission or task
controller. Ownership and live tasks remain disabled.

Zero selects neutral; 1+health selects known health. Nine anchors at eighth
intervals use synchronized full-body clips with identical non-tail channels.
The serialized blend audit measures 170,488 samples; its maximum is recorded in
`validation/tail-blends.json`. Intermediate previews emulate that blend.
Temporal and state-transition blending remain PZ gates.

Existing scanner/cache limits remain unchanged: 16 squares/64 object entries per
callback across local players, 128 cached Shepherds, 250 ms updates, 24-tile radius
and 180 ms easing. These are internal presentation/work limits. Cache state is
transient; saves need no migration. Reload removes previous callbacks.

## Evidence and limits

[VERIFIED, source] Build 42.21 / Steam build 25485521 contracts remain recorded in
the immutable dev.9 `validation/source-evidence.json`: independent action group
required, unique B47Dogmeat clips load from the Raccoon animation directory,
X loading needs explicit float tokens, native health/animation accessors exist.
No game API or authority claim changes in this correction.

[TESTED, offline] Current checks recompute model hashes, unchanged non-skin bytes,
geometry/UV fingerprints, paw assignment, weight normalization, serialized mesh
deformation, hierarchy/loops, fixed-length IK, health-anchor isolation, graph
closure and actual independent Assimp parser acceptance. Reports identify exact
source/model hashes. Numerical regression bounds are not visual acceptance.

Complete 24-frame walk/trot reviews and transition/tail samples are retained in
the v2 checkpoint. The supplied sculpt still compresses around deeply folded
limbs and attachments; those limits are visible in previews. Successful exports
and a few good still images do not establish acceptable animation.

[RUNTIME GATE] Actual PZ import/basis/scale, speed/foot sliding, transitions,
collision/ground contact, health changes/remote observers, cache lifecycle,
sandbox-off behavior, native saves and dedicated reconnect/restart are NOT TESTED.
Each model retains 2,590,138 triangles: memory and frame rate are material gates.
Raccoon sounds/autonomy remain. Use a pristine disposable installation; modified
native installations remain unsupported. G6 NOT TESTED; G7 BLOCKED / NOT TESTED;
stable G8 BLOCKED.

No deployment, game/server launch, merge or Workshop upload is included.
Workshop item 3822584314 still contains the historical dev.7 diagnostic.

## Reproduction

From the repository root with Blender 4.5.3 and Python/NumPy:

```text
blender --background --factory-startup --python art/german_shepherd_motion_v2/source/build_skin.py
blender --background --factory-startup --python art/german_shepherd_motion_v2/source/author_motion.py -- --preview
python -B art/german_shepherd_motion_v2/source/build_animset.py
python -B scripts/test_shepherd_motion.py
python -B scripts/check_motion_imports.py --module-directory <assimp-py-1.1.0-directory>
python -B scripts/check_tail_blends.py
python -B scripts/check_skin_deformation.py
python -B scripts/test_domain.py
python -B scripts/test_asset_boundaries.py
python -B scripts/test_publication.py
python -B art/german_shepherd_motion_v2/source/make_reviews.py
python -B art/german_shepherd_motion_v2/source/finalize_checkpoint.py
python -B scripts/check_native_assets.py --all
python -B scripts/validate_m0r.py
python -B scripts/validate_foundation.py
python -B scripts/build_loadable.py --check
python -B scripts/check_versions.py --root . --json
```

Authoring changes require refreshed checkpoint/source-inventory hashes.
Assimp, NumPy and Blender are development tools only. Assembly/package tests use
disposable temporary outputs, not installed mods or published archives.