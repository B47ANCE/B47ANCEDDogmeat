# Shepherd motion and tail health

Project Version: 0.2.0-dev.12

Compatible visual correction within the additive 0.2.0 MINOR prerelease.
The user rejected dev.9's animations and tail on 2026-10-24. Its numerical
checks established export contracts, not acceptable deformation. The dev.8
native rig, dev.9 motion and dev.10 skin/motion directories remain unchanged historical checkpoints.

## Current source

`art/german_shepherd_motion_v4` contains 47 original motion clips and linked
editable controls. All three models and their weights are reused byte-for-byte
from frozen v3. Geometry, topology, normals, UVs, textures, native bone names,
hierarchy and inverse binds are unchanged. V3 remains the historical dev.11
skin checkpoint; its evidence is not relabeled as dev.12 validation.

The [canine movement audit](CANINE_MOVEMENT_RESEARCH_AUDIT.md) records primary
research, measured repository defects and design limits. V3's positive phase
offsets reversed its intended walk into LH/RF/RH/LF. V4's explicit touchdown
phases produce LH/LF/RH/RF; Run remains a diagonal trot. Swing fore-aft velocity
meets the support velocity at toe-off and touchdown, with smooth vertical lift.
Walking/trotting duty factors 0.64/0.46 are authored parameters, not measured
Shepherd constants. The trot uses 0.08 body lowering, 0.20 stride half-range and 0.09 lift to avoid
excessive crouch. Native navigation still controls actual travel speed.

Both rear stifle and hock pivots move 0.04 source units forward along -BACK.
Hips and paws stay at their fitted source landmarks. Equal translation preserves
calf length; hip/stifle and hock/paw lengths are recomputed. Surface section
inspection supports this bounded trial; it does not establish internal bone
anatomy. Front-rest wrist interpolation now retains its original segment length.
Rest settles forequarters and haunches in stages and retains an open rear stance.
The haunch drops 0.46 source units, the hock target uses 0.18 UP and the outward
knee pole uses 0.3. Dead retains 0.03 UP / 0.13 BACK rear relaxation.

The source skull points about 70.05 degrees away from torso forward. Every clip
now applies a corrected neutral around the existing atlas: Neck -35 degrees,
Head -70.0485107358 degrees. The face remains rigid; the shared ruff blends the
turn. Look adds +/-25-degree yaw and +/-12-degree pitch around forward axes. Neck
shares half of Look yaw to reduce ruff stretch while Head reaches the full turn.
The linked `source/shepherd_head_controls.blend` exposes `GSD_Head_Control`:
local Z yaw, local X pitch, zero for the corrected forward neutral.
`source/shepherd_joint_guides.blend` exposes nondeforming fitted joints with both
Stifle_Hock guides moved forward. These helpers add no runtime bones. Existing
private manual joint edits are preserved separately.

Tail sway uses successive segment yaw amplitudes of 4/8/12 degrees, delayed
progressively toward the tip. The root stays attached and segment lengths remain
fixed. Rest reduces sway; Dead is static. High-health target angles are -10/-12/-35 degrees, reducing the abrupt root
bend. Health elevation and the nine anchors retain their presentation meaning. The original supplied extended-tail
silhouette, neck-ruff compression and angular hip/hock contours still need visual
acceptance; numerical checks are not an anatomy certification.

The three existing types retain their own `b47germanshepherd` animation set and
action group, with the 34-node/25-deforming-bone raccoon contract. Vanilla raccoon
definitions and clips are untouched. No native motion tracks, meshes/weights,
Java classes or third-party animation are shipped. Native navigation owns
movement; Translation_Data stays fixed. Shepherd climbing remains disabled.

## Health cue and authority

`B47ANCEDDogmeat.TailHealthIndicator` remains a server sandbox boolean, default
true, with English fallback text in all 29 language folders. No new configuration
or save schema is introduced in dev.12.

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

Current walk, trot, head and rest loops use actual v4 Blender frames; GetUp
is rendered independently. The exported-X audit checks every gait frame against
actual skinned sole contacts, fitted joint connections, unchanged limb lengths
and torso-relative head direction. The full-surface audit checks every Walk/Run
and LieDown/GetUp frame, plus selected look/health/death poses. Independent head
checks cover all ten Look clips and intervening half frames. Packaging tests
reject stale v3 clip mappings while requiring the unchanged v3 models.

Recorded dev.12 offline results (2026-10-25; Blender 4.5.3 LTS, Python 3.12.14,
NumPy 2.3.5, Lupa 2.6 / Lua 5.1 and assimp_py 1.1.0):

| Check | Result |
| --- | --- |
| Domain / asset-boundary / publication regressions | 465 / 12 / 18 tests PASS; temporary packaging only |
| Motion graph and preserved mapping / independent metric regressions | 15 / 8 tests PASS |
| Independent exported gait and Assimp import | All 47 clips PASS |
| Full-surface deformation | 185 samples PASS, including every exported gait/rest/death frame; maximum edge extension 0.053144 source units |
| Neutral head and ten Look clips | 1,810 samples PASS; rigid-face pair-distance error at most 1.06e-7 source units |
| Tail anchor blends | 170,488 samples PASS; maximum root drift 0.001400 source units (bound 0.0041) |
| Saved head controls / forward joint guides | Reopened and independently checked PASS; native rest matrices unchanged |
| Version / authoritative source parity | 92 current version mirrors PASS; 207 runtime source files match |

The exact commands are below. Numerical results come from the adjacent v4 JSON
reports; the final walk/trot/look/rest previews use the same exported authoring
parameters. Hock/haunch stiffness, neck-ruff compression and the narrow extended
tail base still require visual review. No numerical threshold certifies those
contours as final-quality anatomy.

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
blender --background --factory-startup --python art/german_shepherd_motion_v4/source/author_motion.py -- --preview
blender --background --factory-startup --python art/german_shepherd_motion_v4/source/build_head_controls.py
blender --background --factory-startup --python art/german_shepherd_motion_v4/source/validate_head_controls.py
blender --background --factory-startup --python art/german_shepherd_motion_v4/source/build_joint_guides.py
python -B scripts/check_head_deformation.py --skip-previous --reference art/german_shepherd_motion_v3/validation/head-deformation.json --output art/german_shepherd_motion_v4/validation/head-deformation.json
blender --background --factory-startup --python art/german_shepherd_motion_v4/source/validate_joint_guides.py
python -B scripts/test_shepherd_motion.py
python -B scripts/test_motion_metrics.py
python -B scripts/audit_exported_motion.py
python -B scripts/check_motion_imports.py --module-directory <assimp-py-1.1.0-directory>
python -B scripts/check_tail_blends.py
python -B scripts/check_skin_deformation.py
python -B scripts/test_domain.py
python -B scripts/test_asset_boundaries.py
python -B scripts/test_publication.py
python -B art/german_shepherd_motion_v4/source/make_reviews.py
python -B art/german_shepherd_motion_v4/source/finalize_checkpoint.py
python -B scripts/check_native_assets.py --all
python -B scripts/validate_m0r.py
python -B scripts/validate_foundation.py
python -B scripts/build_loadable.py --check
python -B scripts/check_versions.py --root . --json
```

Authoring changes require refreshed checkpoint/source-inventory hashes. The guide
builder refuses to overwrite an existing scene, protecting manual edits. Do not
rerun historical v3 writers as part of this motion-only revision.
Assimp, NumPy and Blender are development tools only. Assembly/package tests use
disposable temporary outputs, not installed mods or published archives.
