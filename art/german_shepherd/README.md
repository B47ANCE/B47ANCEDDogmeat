# German Shepherd authoring candidate

Project Version: 0.1.0-dev.2

Asset revision: `gsd-v002`. Rebuilt 2026-10-14 from original authored geometry, with a shorter neck, broader cranium/muzzle, revised chest and paws, curved ear shells, eyelids/irises, mouth interior, teeth and a continuous tongue. The coat uses three 2048-pixel maps and skinned mesh guard hairs. This is an **unapproved authoring candidate**. The supplied realistic benchmark has **not been met**; structural checks are not visual acceptance.

![Actual Blender render](previews/german_shepherd.png)

## Benchmark and visual verdict

The user supplied the [CGTrader Dogs big pack](https://www.cgtrader.com/3d-model-packs/dogs-big-pack) and a detailed German Shepherd screenshot as the quality requirement. No commercial model, texture, rig or animation was acquired or incorporated. The original blockout is preserved at commit `38aef659dda253accc6c1062a7b123273f9404a4`, with original reports and a recovery record in [history/gsd-v001](history/gsd-v001/README.md).

The rebuild was inspected repeatedly in real Blender renders and independently reviewed against the supplied screenshot. It improves the first blockout, but still reads as a procedural/stylized dog. It must not be described as matching the commercial reference or ready for production.

| Area | Changes in v002 | Remaining visual gate |
|---|---|---|
| Anatomy | Broader head and chest, shorter neck, abdominal tuck, thicker forelegs and compact toes | Convincing skull/neck/shoulder proportions, joint transitions and pelvic anatomy still require sculpting refinement |
| Face | Eyelids, amber irises, nose/nostrils, lips, teeth and continuous tongue | Natural recessed sockets, facial planes, lip anatomy and nose integration remain below the reference |
| Ears | Closed curved shells with recessed front bowls | Insets/rims need more organic transitions and internal fur |
| Coat | Original generated fur detail mapped into albedo, tangent normal and roughness; skin-anchored mesh hairs | Regional grooming and fine strand detail need refinement; repeated/embossed patterns remain visible in close-ups |
| Silhouette | Ruff/haunch/tail hairs and toe shapes | More natural feathering and tail edges needed; current guard-hair mesh is costly |
| Deformation | Exact skin-root fur transfer; head/limb/tail and jaw/ear probes | Automatic triangulated weights and sparse poses do not establish animation-quality topology or locomotion |

The model's dense authoring groom is substantially above the reference pack's advertised 13,000–17,000 triangles per dog. It is a review master, **not an optimized game model**. PZ shader support and performance budgets remain unverified. Do not substitute increased polygon count or technical validation for the visual requirement.

## Files and evidence

| File | Purpose |
|---|---|
| [source/german_shepherd.blend](source/german_shepherd.blend) | Editable, packed Blender scene, original rig and preview studio |
| [interchange/german_shepherd.glb](interchange/german_shepherd.glb) | Skinned mesh review interchange; not verified PZ native format |
| [source/build_german_shepherd.py](source/build_german_shepherd.py) | Standalone builder and render orchestration |
| [source/shepherd_anatomy.py](source/shepherd_anatomy.py) | Original anatomical forms, facial details and matched rest-skeleton refinement |
| [source/shepherd_coat.py](source/shepherd_coat.py) | UV coat maps and exact skin-vertex-root mesh groom |
| [source/validate_german_shepherd.py](source/validate_german_shepherd.py) | Independent reopen/import checks and imported-GLB render |
| [textures/GENERATION.md](textures/GENERATION.md) | Built-in image-generation tool provenance and exact fur-detail prompt |
| [validation/asset_validation.json](validation/asset_validation.json) | Current build counts, pose measurements and output hashes |
| [validation/roundtrip_validation.json](validation/roundtrip_validation.json) | Independent source/import evidence and imported-preview hash |

Review the [head](previews/head_closeup.png), [paws](previews/paws_closeup.png), [coat](previews/coat_closeup.png), [side](previews/side.png), [front](previews/front.png), [rear](previews/rear.png), [clay](previews/clay.png), [posed three-quarter](previews/deformation_check.png), [posed side](previews/deformation_side.png), [160-pixel silhouette](previews/silhouette_160.png) and [reimported GLB](previews/imported_glb.png). These are actual model renders, not generated concept illustrations.

Measured current geometry: **230,061 triangles**, comprising 24,000 body triangles, 189,465 groom triangles (63,155 strands), and 16,596 facial/detail triangles across 63 objects. This is authoring detail, not an established PZ budget.

Authoring conventions remain metres, Z up, head +X, identity mesh/rig transforms. The original skeleton has 29 bones. Bone labels are independent authoring names, not verified PZ identifiers. The exported fur consists of actual colored mesh ribbons with skin weights; it does not depend on Blender hair particles or unexported procedural shading. Skin weights are normalized to at most four influences. The body is one closed connected outer mesh; intentionally open fur/ear inset surfaces are assessed separately.

## Reproduction and validation scope

Use a fresh standalone Blender-Python process. The builder resets that process's scene and overwrites only current owned asset outputs. Its source modules and original fur-detail PNG must remain together. Toolchain: Windows, CPython 3.13.7, Blender Python 5.2.2 LTS, NumPy and Pillow. These are authoring tools, never PZ runtime dependencies.

Exact commands used on this machine, from repository root:

```powershell
$assetPython = '.m0r-local/art-tools/python313/python.exe'
& $assetPython -B art/german_shepherd/source/build_german_shepherd.py
& $assetPython -B art/german_shepherd/source/validate_german_shepherd.py
$docsPython = 'C:/Users/willi/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe'
& $docsPython -B scripts/check_versions.py --root . --json
& $docsPython -B scripts/validate_m0r.py
& $docsPython -B scripts/audit_public_push.py
git diff --cached --check
```

The optional `--draft` produces three quick views and marks `DRAFT_ONLY`; `--no-render` produces no current preview proof. Complete validation rejects either checkpoint. Draft rejection was exercised during this rebuild. The full builder records the explicit eleven-view set rendered in that run, excluding stale leftover images. The separate validator renders the freshly imported GLB and records its hash.

[TESTED Windows offline, 0.1.0-dev.2 / gsd-v002] Source reopen, provenance and independent GLB roundtrip: **PASS**. Maximum sampled fur-root error under the four posed body tests: 0.000651 m. Source/import material maps, vertex colors, skin weights and facial ownership checks passed. The exporter drops weights at or below 0.0001 by its verified implementation; validation compares that normalized result and separately holds posed-position differences below 0.00002 m. Visual benchmark acceptance remains **NOT MET**.

Validation checks finite geometry, connected/manifold body, UVs, three packed/embedded material maps with live albedo/normal/roughness connections, normalized skin weights, hierarchy, dimensions, matching triangles/objects and posed source/import results. An initial barycentric weight interpolation failed the 3 mm fur-root motion limit; the groom was corrected to inherit exact body-vertex roots/weights. Sampled fur roots are checked against deformed skin, then matched to imported vertices for pose, weight and color comparison. Jaw/ear ownership includes a lower-tooth motion probe and an upper-tooth stationarity check. These structural probes are not a gait, corrective deformation, native animation or production art approval.

[RUNTIME GATE] PZ model import, scale/axes, native rig mapping, registration, complete enabled-state clips, corpse/avatar/attachments, LOD/performance and dedicated synchronization remain NOT TESTED. T-ASSET remains unpassed. G6 NOT TESTED; G7 BLOCKED / NOT TESTED; stable-release G8 BLOCKED. No game/server launch, deployment, runtime package, Workshop upload, stable tag or main merge was performed.

The project advances to 0.1.0-dev.2 as a compatible art-development checkpoint. No gameplay, API, save or sandbox behavior changed. M0R/native observations retain their original 0.1.0-dev.1 dates and scope; updated current contract headers do not refresh that evidence.
