# English Mastiff Blender anatomy checkpoint

Project Version: 0.2.0-dev.7

Asset revision: **em-v004**, authored locally in Blender-Python 5.2.2 LTS on
2026-10-16. **WORK IN PROGRESS / facial acceptance HOLD.** The missing structures
have been modeled; this is not an approved finished character or native game asset.

The user requested Blender additions to the retained Meshy base. This separate
copy derives from [em-v001](../english_mastiff/README.md); all three earlier
geometry candidates and the stopped full-body rig remain unchanged. This work
uses **zero additional Meshy credits**. No remote rigging, motion or new generation
was used. Python/Blender are development tools, not runtime mod dependencies.

## Modeled structures

- A real curved lip incision, separate mandibular exterior and new inner lining;
  upper palate, oral floor, posterior walls and palatal ridges.
- Separate upper/lower gingival arches, including a basal lower ridge supporting
  the raised dental crest. Forty-two individually modeled teeth: upper 20/lower
  22, with distinct incisors, canines, premolars and molars. Roots embed in gums.
- An independent closed tongue with 25 longitudinal rows and 16 points per
  cross-section, plus root/middle/tip controls and an underside/rounded tip.
- Separate eyeballs and eyelid meshes, eye rotation bones and two Blink morphs.
  Blink defaults to zero in every saved format. Facial appearance still needs
  finishing; morph survival does not establish native morph support.
- A temporary seven-bone head/jaw/tongue/eye test rig. It is not a full-body rig.
  No production locomotion clips or native animation registration were added.

The mouth frame is fitted to the asymmetric source head: 30 degrees of authoring
yaw with local origin `(0,-0.8,0)` mapped to `(0.05,-0.8,0)`. The body returns to
its original coordinates, with a ground translation of +0.6689440608 Z. Physical
scale is **NOT CALIBRATED**. The current source contains **34,246 triangles in 58
mesh parts**; this exceeds the earlier 23,000-triangle planning estimate. No
runtime LOD or performance acceptance is implied.

## Files and actual previews

| File | Purpose |
| --- | --- |
| [Anatomical source](source/english_mastiff_anatomy.blend) | Rig-free editable geometry and materials |
| [Deformation test source](source/english_mastiff_anatomy_tests.blend) | Temporary skin, eight source pose presets and eye controls |
| [Static GLB](interchange/english_mastiff_anatomy.glb) / [FBX](interchange/english_mastiff_anatomy.fbx) | Generic anatomical interchange |
| [Test GLB](interchange/english_mastiff_anatomy_tests.glb) / [FBX](interchange/english_mastiff_anatomy_tests.fbx) | Temporary skin/morph interchange; no baked motion library |
| [Dentition](metadata/dentition.json) / [construction](metadata/construction.json) | Semantic inventory, source SHA, frame and modeling provenance |
| [Export checks](validation/exports.json) | Independent six-format reopen and preservation checks |
| [Oral clearance](validation/oral_clearance.json) / [deformation](validation/deformation.json) | Actual sampled contacts, self-intersections and neutral visibility |

These are renders of the actual meshes, with no generated or painted-over
geometry previews:

- [Neutral whole model](previews/neutral_whole.png), [head](previews/neutral_head.png)
  and [direct front](previews/neutral_front.png).
- Jaw [5](previews/jaw_05.png), [15](previews/jaw_15.png),
  [30](previews/jaw_30.png) and [45](previews/jaw_45.png) degree samples.
- Tongue [extension](previews/tongue_extend.png), [curl](previews/tongue_curl.png)
  and [retraction](previews/tongue_retract.png).
- [Oral parts with exterior hidden](previews/oral_components.png),
  [actual section](previews/mouth_section.png), [blink](previews/eyes_blink.png)
  and [eye rotation](previews/eyes_gaze.png).

## Evidence and remaining work

[TESTED — Windows standalone Blender, not PZ] All six files reopen with the
expected parts, tooth counts, UVs and morphs. Test-format skin weights are normalized, with
at most two influences; upper teeth are rigid to Head and lower teeth to Jaw.
The source is finite, closed/manifold after welding interchange seams, and has
no zero-area triangles in the recorded export checks. The original base SHA is
unchanged. Outside the declared head surgery region, original body positions
and UVs are preserved within the recorded roundtrip tolerances.

The original three embedded 2K coat maps remain in BLEND/GLB. FBX uses the
provider's original separate 2K roughness/metallic maps because its exporter
does not translate the packed glTF channel graph. Oral materials are authored
Principled colors/roughness values; a finished oral texture atlas is not claimed.

**Acceptance remains HOLD.** The upper inner-lip transition folds during jaw
opening. Neutral renders also expose residual lining slivers near the muzzle
and attachment seams; eyelid form, eye shading and oral surfacing need further
local retopology/finishing. This has not met the requested commercial visual
benchmark. Use the machine-readable reports for exact current collision counts;
structural integrity and successful export are not a visual/deformation PASS.

The final eight sampled tooth/tongue/lining clearance checks report zero surface
intersection pairs within their documented exclusions. The upper inner lip still
has 33, 80, 129 and 209 nonadjacent triangle pairs at 5, 15, 30 and 45 degrees;
lower lining and tongue self-checks report zero in these samples. These results
are offline surface samples, not a complete motion sweep or containment proof.

The next modeling slice is the upper inner-lip/corner topology and its head/jaw
attachment, followed by complete collision-free jaw/tongue sweeps, natural lip
closure, blink/gaze fitting and final material/UV review. Preserve the complete
anatomical source; derive a reduced native mesh only after its contract is proved.
Earlier full-body clips remain unapproved and were not reused as accepted motion.

Native skeleton mapping, multi-mesh/material binding, morph support, calibrated
scale, animation registration and rendering are **NOT TESTED**. No model is
activated, no gameplay/saves/ownership/task control is changed, and the approved
raccoon carrier remains in use. No new gameplay sandbox option applies to this
isolated art work. G6 NOT TESTED; G7 BLOCKED / NOT TESTED; stable G8 BLOCKED.

## Reproduce and inspect

Run from the repository root with the existing isolated Blender-Python runtime:

```powershell
$artPython = '.m0r-local/art-tools/python313/python.exe'
& $artPython -B art/english_mastiff_anatomy/source/build_anatomy.py --render
& $artPython -B art/english_mastiff_anatomy/source/inspect_exports.py
& $artPython -B art/english_mastiff_anatomy/source/inspect_oral_clearance.py
& $artPython -B art/english_mastiff_anatomy/source/inspect_deformation.py
python -B art/english_mastiff_anatomy/source/validate_checkpoint.py
```

The builder resets only its own fresh process and overwrites em-v004 owned
outputs; it never edits em-v001 or the game. Inspectors do not change models.
FBX extraction is copied into ignored private scratch before import. Derived
`.fbm` folders from an earlier inspection are excluded from the checkpoint.
The hash manifest freezes this work-in-progress evidence, including its known
failures; it does not grant anatomy, animation or release acceptance.
After a deliberate rebuild, rerun all three inspectors and use the validator's
`--freeze` switch to record new hashes. Its exit status concerns checkpoint
integrity; it always reports this revision's facial/visual HOLD separately.
