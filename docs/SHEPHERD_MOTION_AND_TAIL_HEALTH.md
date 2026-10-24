# Shepherd motion and tail health

Project Version: 0.2.0-dev.9

Development decision, 2026-10-24: continue the compatible additive 0.2.0 MINOR
prerelease. Correct presentation and add an optional health cue. No save schema,
ownership contract, native animal type, supplied geometry, UV or texture changes.

## Implemented source

The three existing Shepherd types now select their own `b47germanshepherd`
animation set **and action group**. They retain the native raccoon 34-node bone
hierarchy and the same model-specific inverse binds. Thirty-one original clips are
authored locally and use unique `B47Dogmeat_` names. Vanilla raccoon models,
definitions, action group and motion files are untouched. No native clip motion,
mesh, skin weights, Java class or third-party animation is redistributed.

The old failure was proportional: native raccoon translations drove a much
longer-legged mesh around raccoon joint pivots. The new authoring code constructs
rigid transforms around dog joint landmarks, solves fixed-length limbs for a
planted-foot walk and diagonal trot, and converts those transforms into the
existing bone space. Root movement remains native. It does not stretch bones,
modify vertices, change UVs, or regenerate/remesh the model.

Idle/look, walk/run, pathfinding/wait, wall following, resting/getting up, eating,
hit response and death/ground states have original clip mappings. Rest uses an
extended relaxed pose, rather than extreme folded-leg IK. Death ends at a static
corpse pose. Fence climbing is explicitly disabled for the Shepherd definitions
because this iteration does not supply a valid climbing traversal clip/event.
This does not disable climbing for ordinary raccoons.

Source and editable actions: `art/german_shepherd_motion/source`. The small
`shepherd_motion.blend` contains the rig and all 31 actions; the unchanged meshes
and materials remain in `art/german_shepherd_native/source/shepherd_native.blend`.
Running the authoring script loads the model checkpoint without saving it, writes
the actions/exports, and optionally renders all supplied coat variations. The
original coat shares identical source-space geometry positions and motion.

## Health cue and configuration

`B47ANCEDDogmeat.TailHealthIndicator` is a server sandbox boolean, default **true**.
Its name and tooltip have explicit English fallback entries in all 29 supported
localization folders; this is not a claim of 29 completed translations.

- At high native health the tail is raised; at low health it hangs lower.
- The cue operates while standing, looking, walking or running. Rest, eating,
  hit response and death use their natural authored poses.
- Unknown, invalid or unavailable health produces the neutral tail. Disabling
  the option also restores neutral presentation without changing health.
- All three registered Shepherd types are eligible. There is no claimed tamed
  status or ownership prerequisite: authenticated ownership remains disabled.
- Existing saves need no migration. Presentation is rediscovered and recomputed;
  no health copy, animation flag or cache is persisted.

The client reads `animal:getHealth()`, the same native value used by the vanilla
animal UI. **Native replicated health is not proof of strict server authority:**
the native simulation can delegate animal ownership to a client. This feature
only writes its own local animation scalar. It has no health setter, client
command, save field, ownership admission or task controller.

The scalar reserves zero for neutral/unknown and uses `1 + clamp(health,0,1)` for
known health. This prevents unavailable data from looking like zero health.
Identical full-body clips with different tail poses are synchronized and blended
along five nondegenerate counterclockwise triangles. Health poses at 0%, 25%,
50%, 75% and 100% reduce translation drift when the engine blends bones whose
native pivots differ from the dog. Every non-tail channel is identical across
all health anchors. Serialized local-position/quaternion blend checks cover
85,244 samples; maximum tail-root shift is 0.0039901 source authoring units
(regression bound 0.0041). Previews use the same steady-state blend calculation.
Temporal and state-transition blending remain runtime gates. Native idle/sit/run condition specificity
is preserved; no competing health-only state can override a sit or run state.

Reloading the Lua module removes its previous callbacks and neutralizes its
cache, so callbacks do not accumulate. Invalid sandbox values disable the cue.

No animal-update Lua event was found. A bounded client `OnTick` scanner reads at
most 16 nearby squares and 64 moving-object entries per callback, shared across
all local player slots. The transient cache holds at most 128 Shepherds and
updates at most every 250 ms. It rejects dead, distant, unloaded or removed
objects using `isExistInTheWorld()`. Clearing a cache returns neutral presentation.
These work bounds, 24-tile discovery radius and 180 ms easing time are internal
presentation/safety constants, not hidden health or gameplay balance settings.
Discovery/replication latency and scan cost still require game measurement.

## Verified contracts and limitations

[VERIFIED, source inspection] Build 42.21 / Steam build 25485521:

- `IsoAnimal.initType` uses the definition's animset for both animation set and
  action group. The new group includes all referenced states and native variable/
  event transitions. ActionGroup has no group-level inheritance.
- The native `Raccoon` animation mesh has an `animationDirectory=Raccoon` without
  a prefix filter. Unique mod clips in `media/anims_X/Raccoon` join the dictionary.
- X animation loading uses MakeLeftHanded with no FBX/GLTF scale modifier. Every
  export includes all 34 channels, explicit 30 ticks/second, unit scales and a
  fixed `Translation_Data` root. Float tokens contain decimal points, as required
  by the independent Assimp X reader.
- Vanilla animal UI and petting code demonstrate health reads and animation
  variable writes. Native packets encode health at hundredth precision. Source
  inspection does not establish timing or dedicated observer correctness.

`art/german_shepherd_motion/validation/source-evidence.json` records fingerprints
and method/call evidence. The older dev.8 native-motion renders and reports remain
unchanged historical evidence of the rejected direct-raccoon gait.

[TESTED, offline] Complete-cycle channel/loop checks, fixed limb lengths, planted
foot targets, zero root travel, static corpse, tail-only anchor differences,
action-group closure and actual independent Assimp parser acceptance are checked.
Source mesh/UV hashes and all original runtime GLB bytes remain unchanged. Both
coats have rendered walk/run cycles, health samples, rest transitions and death.
These establish an offline corrected-motion candidate, not production animation
acceptance inside Project Zomboid.

[RUNTIME GATE] Test actual PZ import/basis/scale, native motion speed and foot
sliding, animation transitions and collision/ground contact, health changes and
remote observers, cache discovery/unload/reload, sandbox-off behavior, native
save/reload, dedicated reconnect/restart, and ordinary raccoons remaining intact.
Every model still has 2,590,138 triangles. No geometry reduction was authorized;
loading, memory and frame rate remain material runtime gates. Raccoon sounds and
autonomy remain; this does not add companion AI. Modified native installations
remain unsupported; use a pristine disposable test environment.

G6 NOT TESTED. G7 BLOCKED / NOT TESTED. Stable G8 BLOCKED. No game/server launch,
deployment, Workshop upload or merge is included in this iteration.

## Reproducible validation

From the repository root, using the recorded local Blender 4.5.3 LTS and Python:

```text
blender --background --factory-startup --python art/german_shepherd_motion/source/author_motion.py -- --preview
python -B art/german_shepherd_motion/source/build_animset.py
python -B art/german_shepherd_motion/source/build_review_sheets.py
python -B scripts/test_shepherd_motion.py
python -B scripts/check_tail_blends.py
python -B scripts/check_motion_imports.py --module-directory <local-assimp-py-1.1.0-directory>
python -B scripts/test_domain.py
python -B scripts/test_asset_boundaries.py
python -B scripts/test_publication.py
python -B scripts/check_native_assets.py --all
python -B scripts/validate_m0r.py
python -B scripts/validate_foundation.py
python -B scripts/build_loadable.py --check
python -B scripts/check_versions.py --root . --json
```

The independent parser exposes hierarchy/mesh data, not animation metadata. Its
parse success is paired with separate exported channel/duration/matrix checks.
CI installs `assimp_py==1.1.0` and `numpy==2.3.5` as offline development
dependencies; neither is a mod dependency. Source assembly uses disposable temporary output, not an install
or release package. Historical proof normalization permits only the exact appended
tail sandbox block while still fingerprinting the unchanged diagnostic prefix;
the original NO-GO proof records and protected gameplay Lua remain intact.
