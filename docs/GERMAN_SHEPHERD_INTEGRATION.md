# German Shepherd native integration

Project Version: 0.2.0-dev.8

Development decision, 2026-10-21: continue the additive MINOR 0.2.0 scope at
0.2.0-dev.8. The published 0.2.0-dev.7 diagnostic is an immutable historical
distribution. This iteration adds independent Shepherd animal definitions and
rigs the two additional supplied coats. It changes no ownership, handler, private
store, marker or intent schema and migrates no existing raccoon or b47dogtest.

The original selected rig and supplied coat archives remain preserved. The new
`art/german_shepherd_native` checkpoint contains the original coat and both added
coats, one shared 34-node raccoon hierarchy and 25 deforming bones. Original mesh
coordinates, topology and each coat's distinct UV layout remain hash-identical.
Only rig, weights and reversible mesh object alignment are authored. No welding,
remeshing, decimation, UV transfer or texture repainting occurred.

Each mesh/UV layout requires a separate native animal type, because native breeds
select textures while bodyModel belongs to the animal definition. All three types
share a German Shepherd group and reference the installed Raccoon animation
mesh and raccoon animation set. No vanilla type/model registration is replaced.

Authority scope: native AnimalCheats admin spawning, native simulation and native
save/replication only. No automatic population spawns, client-owned gameplay,
custom ownership admission or live task control. Registration must remain stable
for loading saves; it is not controlled by a toggle that could remove definitions
from an existing save. New balance or population behavior is outside this slice;
no additional gameplay sandbox option is warranted for static model registration.

## Rig and native loading evidence

[VERIFIED, source inspection] Build 42.21 / Steam 25485521. Native clips include
joint translations, so the old dog-fitted authoring skeleton is not sufficient for
direct playback. `ProcessedAiScene.applyToMesh` shares referenced animation clips
but creates skinning data using the new mesh's own bind/offset matrices.
`AnimationPlayer.getSkinTransforms` uses that mesh's offsets; the render instance
passes its own `model.tag`. Therefore this checkpoint binds to native
`Rac_Idle01` frame zero, with matching model-specific inverse binds. It keeps the
same bone names and parents without copying a native mesh, native weights, or
animation clips into the mod. Local pose previews read installed clips in memory.

The X importer reflects Z and conjugates its animation quaternions; the engine
also requests MakeLeftHanded. The GLB basis accounts for the different import
route. Upstream Assimp 3.3.1 and 5.3.1 corroborate this conversion; the exact
bundled Assimp source revision is UNKNOWN. Local exported-matrix checks are
evidence of the authoring conversion, not actual PZ loading.

[VERIFIED, source inspection] Model scripts use `animalEffect`, `static=false`
and `animationsMesh=Raccoon`; definitions use `animset="raccoon"`. The engine
loader supports GLB. Diffuse maps are explicit `media/textures/Body/*.png` files.
The animal shader uses diffuse textures and four bone influences, not the full
PBR material. Original normal/roughness/metallic maps remain in the authoring
checkpoint. Blender PBR previews therefore do not represent the in-game shader.
The original coat's GLB embeds JPEG; `extract_diffuse.py` decodes its exact RGB
pixels to the PNG container required by this mapping, without repainting,
resizing or flipping. Both variation diffuse PNGs are the supplied exact bytes.

## Registration and limits

| Native type | Coat | Body model |
| --- | --- | --- |
| b47gsdoriginal | Original | B47Dogmeat_GSD_Original |
| b47gsdcoat1 | Variation 1 | B47Dogmeat_GSD_Coat1 |
| b47gsdcoat2 | Variation 2 | B47Dogmeat_GSD_Coat2 |

All appear under `b47germanshepherd` through the existing native administrator
animal menu. The existing server `animal/add` route requires AnimalCheats;
clients do not receive a new trusted mutation path. All three keys are checked
before any registration, so collisions fail without partially replacing types.
The 29 localization folders carry explicit English fallbacks for the seven new
labels; this is not a claim of 29 completed translations.

These are adult-only native presentation/simulation candidates. They inherit
raccoon autonomy, sounds and balance. Breeding, carrying, petting, attachment and
transport are disabled in the definitions. Corpse/skeleton model slots use the
same own whole-body asset as an explicit placeholder; butcher yields are empty.
There is no automatic population distribution. Existing raccoon and `b47dogtest`
definitions, diagnostic gates and all prior production Lua remain unchanged.

[TESTED, offline] See `art/german_shepherd_native/validation/native-bind.json`
for exact geometry/UV preservation, native hierarchy, bind matrices, normalized
four-influence skinning and export checks. The two supplied coats each contain
1,294,771 vertices and 2,590,138 triangles. No optimization was authorized; loading
cost and frame rate are unmeasured and remain a material performance gate.

[RUNTIME GATE / visual HOLD] Rest shape is preserved, but locally sampled native
walk/run motions still show leg/tail distortion from the raccoon proportions.
The assets are rigged integration candidates, not accepted production canine
animation. A dedicated Shepherd motion set on the same bone hierarchy is the
next animation option; no copied native clips or alternative motion service is
included here. Complete clip/transition acceptance remains pending.

On a separately authorized pristine disposable PZ installation: verify admin
group/type/coat enumeration, all three diffuse/mesh bindings, camera scale,
idle/walk/run/turn/lie/death transitions, ordinary raccoons unchanged, native
save/reload, dedicated client join/rejoin and restart. Measure memory/frame rate
with one and several instances. Do not infer persistent ownership from native
animal saves. G6 NOT TESTED; G7 BLOCKED / NOT TESTED; stable G8 BLOCKED.

No deployment or publication occurred. Current document version headers identify
the current contract edition; historical source hashes, observed versions and
runtime limits remain bound to their original evidence. The old proof checker
normalizes only current version headers to its recorded dev.7 edition; it still
rejects substantive historical changes and all unreviewed production additions.

## Validation commands and results (2026-10-21)

All Python commands below use the locally installed Python runtime; Blender
commands use Blender 4.5.3 LTS. The game root is passed explicitly and read only.

| Command | Result / scope |
| --- | --- |
| `blender --background --factory-startup --python art/german_shepherd_native/source/validate_native.py -- --game-root <game>` | PASS: 3 exact source mesh/UV hashes, 34-node hierarchy, 25 inverse binds, normalized four-influence exports; not PZ |
| `blender --background --factory-startup --python art/german_shepherd_native/source/preview_native_clips.py -- --game-root <game>` | Four actual local samples; rest shape retained, locomotion visual HOLD |
| `python -B scripts/check_native_assets.py --all` | PASS: runtime model hashes/structure and retained checkpoint hashes |
| `python -B scripts/test_domain.py` | 439 PASS in offline Lua 5.1/Lupa 2.6, including 8 registration cases |
| `python -B scripts/test_asset_boundaries.py` | 11 PASS: traversal, case collision, LFS pointer/hash rejection, historical-header normalization/tamper boundaries |
| `python -B scripts/validate_m0r.py` | STATIC PASS; source, 29-language fallback inventory, historical evidence and assembly boundaries |
| `python -B scripts/test_publication.py` | 18 PASS using disposable package fixtures; no release artifact retained or uploaded |
| `python -B scripts/build_loadable.py --check` | 121 files, exact disposable source parity; no installation |
| `python -B scripts/check_versions.py --root . --json` | PASS: current canonical version/mirrors; no stable-release check claimed |

Separate read-only actual vanilla-definition test preserved all 12 raccoon sound
entries in independent cloned breed tables for each Shepherd. Complete game
registry, rendering, sound playback, simulation and dedicated tests are NOT TESTED.
