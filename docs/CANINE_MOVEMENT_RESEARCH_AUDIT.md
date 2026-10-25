# Canine movement research and animation audit

Project Version: 0.2.0-dev.12

Research date: 2026-10-25. Scope: original Shepherd presentation, preserving
source geometry, UVs, skin weights and the native raccoon skeleton contract.
This is an animation design audit, not a veterinary assessment or PZ runtime test.

## Primary evidence

| Source | Observed evidence | Authoring implication and limit |
| --- | --- | --- |
| [Catavitello et al., 2015, inter-segment coordination in six dogs](https://pmc.ncbi.nlm.nih.gov/articles/PMC4517757/) | Observed walking footfalls follow hind limb, same-side forelimb, opposite hind limb, opposite forelimb; trot pairs diagonal limbs. | Use explicit touchdown phases so the authored walk follows that lateral sequence. Keep contralateral pairs half a cycle apart and trot diagonals together. |
| [Fischer et al., 2018, three-dimensional canine hindlimb kinematics](https://pmc.ncbi.nlm.nih.gov/articles/PMC6242825/) | Biplanar fluoroscopy and 3D registration compare four breeds. Hip, stifle and hock have distinct phase-dependent motion. Breed differences and skin-marker errors limit direct angle comparisons. Malinois/Whippet pelvic yaw is small during stance. | Coordinate the rear joints and keep body yaw restrained. Use qualitative timing, not a copied measured trajectory or a claim that one breed's angle curve is a universal canine rig. |
| [Yoshikawa et al., 2021, functional assessment and gait phases](https://www.jstage.jst.go.jp/article/jvms/83/1/83_20-0127/_article) | The study separates initial contact, loading response, middle stance, pre-swing, early swing and late swing while examining joint angles and muscle activity in walking Beagles. | Distinguish support, push-off, clearance and placement in authored motion. This supplies phase reasoning, not Shepherd-specific speeds or a prescribed animation duration. |
| [Miao et al., 2026, German Shepherd forelimb/hindlimb kinematics](https://www.frontiersin.org/journals/veterinary-science/articles/10.3389/fvets.2026.1878605/full) | Four adult male Shepherds were measured. Trot uses diagonal support; hip extension during stance is followed by swing flexion. Stifle and tarsal motion are coordinated rather than a single rigid lower-leg motion. The small cohort and marker-based method limit generalization. | Preserve a diagonal trot and coordinated hindlimb recovery. These are qualitative constraints for independent authoring; the reported clinical interpretations are outside this task. |
| [Wada et al., 1993, tail EMG and kinematics](https://pubmed.ncbi.nlm.nih.gov/8411184/) | Seven treadmill dogs showed alternating left/right muscle activity corresponding to lateral tail motion in walking and trotting. The abstract describes a different pattern during galloping. | Add bounded lateral sway to walking/trotting. Selected amplitudes and timing are artistic parameters, not measured values from this abstract. The existing Run slot remains a trot, not a newly claimed gallop. |

No external motion tracks, model assets, paper figures or third-party mod code
are copied. Sources inform independently authored curves. Published angle
definitions are not assumed equivalent to our simplified rig landmarks.

## Repository findings before correction

- [VERIFIED, source] V3 tail yaw is only `0.015 * sin(...)` radians, less than
  one degree. This explains the weak visible sway without requiring a runtime
  networking or health change.
- [VERIFIED, source] The fitted source head forward vector is approximately
  `(-0.09235, -0.99573, 0)`, while torso forward is approximately
  `(-0.96748, -0.25296, 0)`. Neutral faces about 70 degrees away from travel.
  V3 head turns are relative to that sideways source direction.
- [VERIFIED, source] Paw targets, knee solving and distal-limb rotations are
  authored separately. The audit must verify their shared joint positions and
  actual exported contact trajectories, not just individual segment lengths.
- [VERIFIED, source] V3 adds its listed Walk offsets to time, reversing the
  intended order into LH, RF, RH, LF. V4 subtracts explicit touchdown phases
  to produce LH, LF, RH, RF. Trot retains diagonal pairs. Swing fore-aft
  velocity now meets support velocity at both boundaries rather than snapping
  between constant-speed stance and zero-speed easing.
- [INFERRED] Visible rear-leg defects can arise from footfall timing, mismatched
  joint endpoints, an unstable bend plane or rigid ankle recovery. Numerical
  and rendered comparisons are required before selecting a correction.

## Implemented correction and measured scope

- [TESTED, offline] The v3 authored joint endpoints were already coherent to
  about 1.1e-6 source units. The audit did not establish a general disconnected
  hind-chain defect. A real front-rest wrist interpolation error shortened that
  segment by up to 0.004918; normalizing its blended direction removes it.
- [TESTED, offline] Triangle-plane sections place the new stifle/hock pivots
  inside the source contours after the 0.04 forward shift. At 0.06 the left hock
  nearly reaches the surface, so that larger trial was rejected. This measures
  source-surface fit, not the anatomical location of unseen bones.
- [TESTED, offline] Moving the pivots initially pushed rear-foot vertices below
  the lying floor. Raising the rest hock target to 0.18 UP, reducing outward pole
  to 0.3 and settling the rear pelvis by 0.46 clears this failure while retaining
  the original 0.16 rear paw reach. Dead extends rear reach to 0.13 BACK and
  relaxes the head by 8 degrees as the body rolls.
- [TESTED, offline] The trot trial uses 0.08 body lowering, 0.20 stride half-range
  and 0.09 paw lift. Its deepest rear-knee angles improve from roughly 84/90 to
  92/98 degrees while retaining reachable targets. These are fitted-rig angles,
  not asserted veterinary measurements.
- [TESTED, offline] Forward neutral uses a -70.04851-degree total Head yaw about
  the atlas, with -35 degrees on Neck. Look shares half its additional yaw with
  Neck while Head reaches the full yaw/pitch target. This reduces ruff stretching;
  it does not erase the source's neck asymmetry.
- [INFERRED, rendered review] The walking sequence is more readable and the
  corrected trot has less rear-leg compression. Rest still looks stiff around
  the hock/haunch; the ruff deforms and the extended proximal tail stays narrow.
  These are explicit visual limits, not failures hidden by numerical PASS labels.

## Acceptance contract

The new checkpoint is `art/german_shepherd_motion_v4`; frozen v3 models and
weights are reused. Head alignment must be measured against torso forward in
the exported neutral pose, with Look excursions relative to that new neutral.
The original bind headers remain unchanged. Full-face rigidity, neck surface
deformation, floor clearance and saved manual head-control behavior need checks.

Tail sway must have measurable lateral travel relative to the pelvis while
retaining connected, fixed-length segments, unchanged health-anchor isolation,
the existing root-drift bound and a static Dead state. Sway is presentation;
native health ownership and the server sandbox option remain unchanged.

Every exported Walk/Run frame must be inspected numerically for limb connection,
floor/contact behavior, continuous swing and loop closure. Actual rendered
walk, trot, head and rest sequences provide visual review in addition to tests.
Artistic curve parameters remain internal implementation details; no new shared
gameplay behavior or sandbox setting is introduced.

[RUNTIME GATE] PZ playback, speed/foot sliding, state blending, remote observers,
native health, saves and dedicated restart remain NOT TESTED. G6 NOT TESTED;
G7 BLOCKED / NOT TESTED; stable G8 BLOCKED. Research and Blender playback do not
establish native correctness. No deploy, game/server launch or publication.
