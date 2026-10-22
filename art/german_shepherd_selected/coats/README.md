# German Shepherd coat variations 1 and 2

Asset revision: gsd-selected-coats-v001. Recorded runtime baseline: 0.2.0-dev.7.
User selection date: 2026-10-21. Authoring-only intake; no runtime version/payload change.

The user supplied these as the first and second additional coat variations for the selected German Shepherd. Preserve those labels and the original selected coat independently. Each variation directory contains the byte-exact supplied FBX and four matching 2048x2048 PNG maps, plus an actual Blender review render. No generated/repainted textures, geometry edits, UV changes, rig replacement or paid job occurred. Original ZIPs remain unchanged in the user's Downloads; their filenames, SHA-256, CRC results and every member hash are recorded in source-provenance.json. OBJ/MTL source members are inventoried rather than redundantly committed; each OBJ archive's base-color bytes match that coat's FBX archive map.

- Variation 1: FBX archive timestamp 1021185341; OBJ archive without the filename suffix `(1)`.
- Variation 2: FBX archive timestamp 1021190310; OBJ archive with the filename suffix `(1)`.

## Compatibility result

[TESTED: Blender 4.5.3 offline] Each FBX has 1,294,771 imported vertices and 2,590,138 triangles. The original GLB-based rig has 1,425,959 vertices because format-specific vertex/seam indexing differs. An order-independent triangle-corner comparison at 1e-5 local-coordinate precision matches both supplied surfaces to the original. This is a tolerance-based comparison, not byte-identical mesh proof.

UVs aligned by the matching triangle geometry differ substantially for both coats: no corresponding corners fall within 1e-5 UV tolerance. These maps must stay with their matching supplied UVs. They are **not direct texture swaps** on the original rig. The original rig and material remain untouched, and the additional FBXs remain unrigged. Future binding should use each supplied mesh/UV layout with the same verified raccoon bone contract, without overwriting the original model or vanilla raccoons. No UV transfer, rebake or mesh editing was used to force compatibility.

The previews render the supplied FBX geometry and exact PNG maps in a temporary review scene using the original rig checkpoint's lighting/camera. That scene is not saved over any source. These are static authoring previews, not native animation or game evidence. Separate Dogmeat animal registration, full animation playback, performance, SP and dedicated MP remain [RUNTIME GATE] / NOT TESTED. Ownership and live task control stay disabled. G7 BLOCKED / NOT TESTED; stable G8 BLOCKED. No packaging, deployment or Workshop publication.

## Reproduction

Run from the repository root after `git lfs pull`, using verified local executables:

```text
blender --background --factory-startup --python art/german_shepherd_selected/coats/inspect_coats.py
blender --background --factory-startup --python art/german_shepherd_selected/coats/render_coats.py
python -B art/german_shepherd_selected/coats/check_coats.py
python -B art/german_shepherd_selected/source/check_asset.py
python -B scripts/check_versions.py --root .
python -B scripts/validate_m0r.py
python -B scripts/validate_foundation.py
python -B scripts/audit_public_push.py
git diff --cached --check
```

The inspection writes compatibility.json from actual imports; the preview command writes only preview.png files. Hash checks detect changes in retained inputs, sources, evidence and previews. They do not independently prove PZ loading or multiplayer behavior. Use a new asset revision when deliberately changing retained evidence.
