# English Mastiff complete-anatomy assessment and modeling plan

Project Version: 0.2.0-dev.11

Decision, 2026-10-16: **local anatomy added; facial/visual acceptance INCOMPLETE;
production rigging and native activation HOLD**.
The latest [complete-anatomy request](requirements/ENGLISH_MASTIFF_ANATOMY_REQUEST.md)
governs the target: a neutral, gently closed mouth with complete modeled anatomy
inside, no permanently exposed tongue. It supersedes the earlier open-mouth
preview pose. The user later approved one additional 20-credit static preview;
no automatic follow-up is authorized. Its explicit fallback applies:
retain the best available base, identify missing geometry
and provide a precise local modeling plan when Meshy is unreliable. The user's
later instruction to use Blender authorizes executing that local fallback.

## Executed local Blender slice

[em-v004](../art/english_mastiff_anatomy/README.md) is a separate working copy of
the original textured base. Codex authored the mouth incision, mandibular mesh,
palate/floor/posterior lining, 42 individual teeth, upper/lower gingiva,
independent tongue, eyeballs and blinking eyelids locally in Blender-Python
5.2.2 LTS. The source includes a temporary seven-bone jaw/tongue/eye test rig and
eight pose presets, plus rig-free BLEND and generic FBX/GLB checkpoints. This
consumed zero additional Meshy credits and preserves all prior assets.

[TESTED — offline Windows Blender] Six-format reopening verifies the semantic
parts, UVs, expected teeth, normalized weights and Blink morphs. The original
body/coat evidence is retained; FBX receives the original separate scalar maps
to replace unsupported packed-channel export. Actual neutral, mouth section,
jaw/tongue and eye renders are retained. Exact source-bound reports are linked
from the asset README; old preview/rig reports have not been relabeled.

**This is a work-in-progress anatomical checkpoint.** Upper inner-lip folds,
residual lining slivers/attachment seams and unfinished eye/lid shading/form
block final facial and visual acceptance. Successful export or manifoldness
does not waive these defects. Finish local lip/corner topology and clearance
before production animation. No claim of commercial-quality matching,
collision-free complete motion, native morph/material support or game readiness.

No production Lua, save, ownership, task control, carrier or runtime metadata
changed. Continue using the raccoon. G6 NOT TESTED; G7 BLOCKED / NOT TESTED;
stable G8 BLOCKED.

The original textured [em-v001](../art/english_mastiff/README.md) remains the
better retained appearance/coat checkpoint. The separately approved
[em-v002-preview](../art/english_mastiff_regeneration/README.md) supplies actual
open-mouth reference geometry, but fails complete-anatomy acceptance.
The later [em-v003-preview](../art/english_mastiff_anatomy_preview/README.md)
also fails anatomy acceptance: 23,865 triangles, 52 boundary edges and
80 non-manifold edges. Actual sectioning shows a head-shell void rather than
verified bounded oral anatomy. None is a complete animatable character;
no follow-up texturing or rigging is claimed.

## Historical retained em-v002 component inspection

Evidence: em-v002-preview GLB/FBX reimports, five whole-model renders and
[five mouth/section views](../art/english_mastiff_regeneration/previews/mouth).
Source hash bcc89ccfc1b4b904ce3c371abe4c69516eccfa92dd9ab1789c888579aa536ef3.
The welded surface is one 7,799-vertex component: no separately identified jaw,
tongue, tooth or eye objects. One connected component alone does not forbid
skinning; it also does not prove the requested structures are independent.

| Component | Status | Actual evidence / missing work |
| --- | --- | --- |
| Upper jaw | INCOMPLETE | Broad upper muzzle present; dental arch and stable inner anatomy not established |
| Lower jaw | INCOMPLETE | Lower-mouth volume visible; no identified mandible region/hinge or closing test |
| Complete mouth cavity | INCOMPLETE | A real recessed cavity is visible in section; complete anatomical walls and floor not established |
| Teeth | FAIL | No recognizable complete canine/incisor/premolar/molar set or separate tooth geometry verified |
| Tongue | INCOMPLETE | Tongue-like lobe present; independent root/middle/tip topology and deformation not established |
| Gums | FAIL | Distinct upper and lower gum structures not verified |
| Lips | INCOMPLETE | Outer lip/jowl mass present; usable opening loops and closed lip seal not established |
| Jowls | INCOMPLETE | Breed-like volume present; controlled deformation and clearance not tested |
| Mouth corners | INCOMPLETE | No accepted corner edge flow or jaw-opening deformation test |
| Hard palate | INCOMPLETE | Cavity roof visible; anatomically defined palate surface not verified |
| Eyes / eyelids | INCOMPLETE | Visible eye regions; independent eye rotation and blink geometry not established |
| Neutral closed mouth | FAIL | Preview was generated open; natural closure has not been demonstrated |

Other checks: 15,601 triangles, one UV set, no non-finite positions or zero-area
triangles, 18 welded boundary edges and 28 non-manifold edges. Both GLB and FBX
reopen in Windows standalone Blender-Python 5.2.2 LTS. Surface/self-intersection,
deformation, dental occlusion, likeness and native loading have no acceptance
PASS. Material inventory: this preview has no textures/materials; em-v001 has
one PBR material and four external 2K maps. Its coat is not evidence of oral
materials on the replacement.

## Provider and toolchain findings

[VERIFIED - configured tool schemas, reviewed 2026-10-16] Text-to-3D preview
supports Meshy-7.1, target polygon count, triangle/quad remeshing and FBX/GLB.
The prompt field accepts at most 800 characters; the full handoff is a
requirements specification, not a valid single API prompt. No independent
negative-prompt field, dental formula, jaw-part, tongue-part or mouth-control
parameter exists in the inspected text-generation schema.

Smart-topology models expose part-separated triangle output, but no inspected
schema guarantees the named oral anatomy or semantic component separation.
Remesh changes topology; it is not a documented mouth-reconstruction operation.
Refine/retexture supplies PBR maps and UV controls; painted teeth do not fulfill
missing geometry. Conversion supplies file formats, not anatomy. No proposed
mode was submitted to test this experimentally.

The [official rigging API](https://docs.meshy.ai/en/api/rigging) documents
humanoid/biped inputs and excludes non-humanoid assets. The current user policy
also prohibits all Meshy rigging, skinning, animation-library clips, retargeting
and text-to-motion even if credits are approved. Author all motion through
Blender/local tools; report unavailable local/native contracts as blockers.
The three observed geometry requests do not prove every possible
Meshy generation fails; they demonstrate that this workflow has not reliably
delivered the requested oral anatomy.

Use the already installed standalone Blender-Python 5.2.2 LTS for deterministic
local modeling. No dependencies were installed. Paid history: first preview
20 + original texture 10 + replacement preview 20 + complete-anatomy preview 20
= 70 credits. The latest job consumed its approved 20 credits;
documentation/inspection consumes zero additional credits.
Any new permitted static generation, remesh,
texture or conversion job requires separate explicit approval. Meshy motion
operations remain prohibited; approval for credits cannot enable them.

## Original Blender plan and remaining acceptance criteria

This is the original plan used to start em-v004. Its implemented subset and
remaining defects are recorded above and in the asset README; these steps are
not an assertion that deformation, finished surfacing or native export passed.

1. Create an em-v004 editable working copy of em-v001. Keep all service outputs,
   em-v001, em-v002-preview, em-v003-preview and the stopped rig experiment
   unchanged. Treat the open preview as owned geometric reference,
   not a source of accepted mouth
   topology. Preserve existing body proportions, fawn coat and body UVs.
2. Isolate the head and inspect section views. Mark the upper/lower lip borders,
   both mouth corners, mandibular body and both temporomandibular hinge regions.
   Remove internal fused caps only in the working copy. Rebuild the opening with
   continuous lip-rim loops and inner cheek transitions; upper and lower lips
   may touch at rest but must not be welded across the opening.
3. Model distinct upper and lower dental arches. Attach upper palate/gums rigidly
   to the skull; attach lower gums and mandibular floor to the mandible. Connect
   flexible inner cheeks at the corners with sufficient loops for opening.
   Close all unintended holes with anatomically meaningful surfaces; preserve
   intentionally separate parts instead of globally welding the oral mesh.
4. Model recognizable individual teeth, with roots embedded in gums and crown
   clearance. Use the adult canine arrangement as a reference target: 42 teeth,
   20 upper and 22 lower, with incisors, canines, premolars and molars. Each side
   has upper I3/C1/P4/M2 and lower I3/C1/P4/M3. This is an art-reference target,
   not a medical simulation or an assertion about every individual dog.
   See [WSAVA Global Dental Guidelines, oral anatomy](https://onlinelibrary.wiley.com/doi/10.1111/jsap.13132).
   Model canine and chewing tooth silhouettes rather than using identical cones.
   Group upper teeth under the head and lower teeth under the jaw; do not assign
   one bone per tooth.
5. Build a separate tongue mesh with a rounded tip, underside and defined root.
   Add longitudinal/transverse loops for root/middle/tip controls and curling.
   Keep it separate from teeth and mouth floor; fit its relaxed shape fully
   inside the gently closed mouth. Keep attachment/root continuity intentional.
6. Provide separate eyeballs and eyelid rims where the original surface cannot
   blink or rotate. Retopologize the mouth corners, cheeks, jowls and eye loops
   locally. Preserve external likeness; bake/project the existing appearance
   only after the new geometry passes inspection.
7. Test temporary jaw/tongue controls in the working copy solely for geometry
   acceptance. Fit the jaw pivot to both hinge regions. Inspect proposed art
   test poses at 0/5/15/30/45 degrees, then yawning/closure as appropriate to
   the actual geometry. These are sampling angles, not established biological
   limits or gameplay settings. Check upper/lower tooth contact, lip seal,
   palate, jowl and tongue intersections in front/side/underside sections.
   Exercise tongue extension, retraction and curling without enamel penetration.
8. Normalize at most four weights per exported vertex. Teeth remain rigid;
   jaw/tongue/lips/jowls must not borrow unrelated limb weights. Inspect shoulder,
   hip, elbow, hock and neck bends as well as deep sit/lie poses before adopting
   any earlier motion. The stopped procedural clips have no final acceptance.
9. Freeze the master UV layout only after anatomy/deformation approval. Keep
   logical source materials for coat, mouth lining, gums, teeth, tongue and eyes.
   Use 2K body PBR and a separate oral authoring atlas if needed. Derive all fawn,
   brindle and black coats from that same accepted UV master; do not promise
   texture variants already exist. Bake a reduced runtime atlas only after the
   native material/mesh route is verified.
10. Export a rig-free anatomical checkpoint and a separate temporary deformation
    test scene. Reopen FBX and GLB, verify part names, UVs, material assignments,
    normalized weights, bind transforms, scales and poses; retain hash manifests
    and actual renders. Only then resume production rig/animation work.

## Proposed geometry and facial budgets

These are authoring estimates, not verified PZ limits.

| Region | Proposed LOD0 triangles | Purpose |
| --- | ---: | --- |
| External body excluding head | 9,000 | Existing silhouette, limbs and tail |
| Head and facial surface | 6,000 | Lip/corner/eyelid loops and jowls |
| Teeth | 4,200 | All tooth classes, individual rigid crowns |
| Tongue | 1,200 | Root/middle/tip bending and curling |
| Cavity, palate and gums | 2,600 | Complete inner surfaces and arches |
| Total | 23,000 | Initial estimate; anatomy governs revisions |

Proposed LOD1: 10,000–14,000 triangles; simplify body, hidden tooth surfaces and
inner cavity while retaining visible canine/tongue silhouette. Proposed LOD2:
5,000–8,000 triangles with reduced oral detail. No automatic LOD switching or
multi-LOD runtime loading is established. Store LODs as separate authoring
variants until the native renderer, visible screen size and performance are
measured. Do not remove required anatomy from the complete source model.

A facial design could extend the original 42-bone concept with tongue root/
middle/tip (3), upper/lower lip controls per side (4), upper/lower eyelids per
side (4), and two eyes (2): 55 total, including its existing jaw, head, ears and
jowls. This is a proposed count, not a finalized native skeleton. Helpers and
export-added joints must fit the same total. Use source-only corrective shape
keys where useful; native morph/shape-key support remains UNKNOWN.

## Native Build 42.21 assessment

Evidence is the [installed asset/loader ledger](../art/english_mastiff_rig/validation/native_audit.json):
client Steam build 25485521, packaged JAR SHA-256
e1a69eb743ede60b213a0fe7f8b83d4fcab773036d256cc4543a336f3b058a33.

| Concern | Source observation and remaining gate |
| --- | --- |
| Skeleton | Inspected raccoon uses 35 frames/25 weighted names; no verified jaw/tongue match. New canine hierarchy and bind strategy remain unproved |
| Clip/model formats | Raccoon uses text X; FileTask_AbstractLoadModel explicitly recognizes FBX, GLB/glTF and X paths. Particular Mastiff loading is NOT TESTED |
| Bone/weight budget | animalEffect.vert has MatrixPalette[60] and four skin-weight/index lanes. This bounds the inspected shader, not every engine/importer limit |
| Jaw / tongue / eyes | Ordinary weighted-bone motion is a plausible source strategy, INFERRED; no native facial clip/control or client result is verified |
| Materials | animalEffect.frag samples one Texture and uses native lighting; no normal/roughness/metallic sampler there. Multi-mesh oral materials and runtime atlas binding remain UNKNOWN |
| Scale / axes | Authoring -Y forward, Z up; original source units retained. Native scale/handedness/bind conversion remain uncalibrated |
| Root motion / speed | Native deferred movement descriptors exist, but new clips, authoritative travel and playback matching remain UNKNOWN |
| Animation registration | Native model/animationsMesh/animset XML links observed. No new canine registration or state writer implemented |
| Reduced rig | Proposed 55-joint budget is conservative against this shader; actual native hierarchy/import and animation evaluation still require proof |
| Client / dedicated | NOT TESTED. No game/server launch, spawn, deployment, new task control or visual synchronization experiment |

Preserve the complete source even if the native runtime needs fewer facial
controls. A reduced export must document dropped controls and re-bake their
motion where supported; never call a source-only capability a working native
feature. Live motion/gameplay decisions remain server authoritative. No new
sandbox option is appropriate for these unregistered authoring artifacts.

## Deliverable status

| Requested output | Current result |
| --- | --- |
| Full-body Mastiff | Original textured base preserved in em-v004; final likeness/visual approval pending |
| Complete mouth / riggable jaw | Modeled opening and jaw; upper transition/deformation acceptance INCOMPLETE |
| Tongue, teeth, gums, palate | Actual separate meshes and complete reference dentition added locally; final fit/finish HOLD |
| Fawn textures / PBR inventory | Original 2K coat retained; colored oral source materials, no finished oral atlas |
| Geometry inspection | Actual new Blender renders, six-format reopening and source-bound hash/check reports |
| Facial feasibility / native assessment | Seven-bone temporary controls and Blink morphs; full facial/native acceptance unproved |
| Remaining modeling requirements | Upper lip/corner retopology, closure, complete motion clearance and visual/material finishing |
| Existing animations | Stopped full-body experiment unchanged; eight new source-only anatomical test presets |

The Blender fallback has been executed as an editable draft; a finished
animatable character is not claimed. No further paid operation, runtime
dependency, gameplay/save/ownership change, native binary modification,
deployment or Workshop publication.
G6 NOT TESTED; G7 BLOCKED / NOT TESTED; stable G8 BLOCKED.
