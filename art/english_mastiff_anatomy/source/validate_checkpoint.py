"""Validate this WIP artifact's hashes and recorded offline evidence using stdlib.

No Blender execution, geometry acceptance, native support or runtime PASS is
implied. --freeze deliberately records the current inspected checkpoint; normal
validation is read-only. The known upper-lip/visual HOLD must remain explicit.
"""
import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parents[1]
MANIFEST = ROOT / "metadata/checkpoint.json"
BASE = "art/english_mastiff/interchange/english_mastiff.glb"
BASE_SHA = "37c8e1cc6e47f9ffde22aa93346e8d91f15fb4c3d90843e4cb278e2aab07bd31"
POSES = ["Jaw_00", "Jaw_05", "Jaw_15", "Jaw_30", "Jaw_45",
         "Tongue_Extend", "Tongue_Curl", "Tongue_Retract"]
TEETH = {"U_I": 6, "U_C": 2, "U_P": 8, "U_M": 4,
         "L_I": 6, "L_C": 2, "L_P": 8, "L_M": 6}
MODELS = [f"{folder}/english_mastiff_anatomy{suffix}.{ext}"
          for folder, ext in [("source", "blend"), ("interchange", "glb"),
                              ("interchange", "fbx")]
          for suffix in ["", "_tests"]]
PREVIEWS = ["neutral_whole", "neutral_head", "neutral_front", "jaw_05",
            "jaw_15", "jaw_30", "jaw_45", "tongue_extend", "tongue_curl",
            "tongue_retract", "eyes_blink", "eyes_gaze", "oral_components",
            "mouth_section"]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def owned_files():
    return sorted(MODELS + [f"previews/{name}.png" for name in PREVIEWS]
                  + [p.relative_to(ROOT).as_posix()
                     for p in (ROOT / "source").glob("*.py")]
                  + ["README.md", "metadata/construction.json",
                     "metadata/dentition.json", "validation/exports.json",
                     "validation/oral_clearance.json", "validation/deformation.json"])


def check_evidence():
    def require(condition, message):
        if not condition:
            raise ValueError(message)

    require(sha(REPO / BASE) == BASE_SHA, "Frozen em-v001 base changed")
    construction = read(ROOT / "metadata/construction.json")
    require(construction["asset_revision"] == "em-v004", "Wrong asset revision")
    require(construction["base_sha256"] == BASE_SHA, "Construction base mismatch")
    require(construction["meshy_credits_consumed"] == 0, "Unexpected paid operation")
    exports = read(ROOT / "validation/exports.json")
    require(exports["base_preserved"] and exports["base_sha256"] == BASE_SHA,
            "Base preservation evidence failed")
    require(set(exports["files"]) == {Path(p).name for p in MODELS},
            "Missing or unexpected six-format inspection")
    for relative in MODELS:
        result = exports["files"][Path(relative).name]
        require("error" not in result, f"Export reopen failed: {relative}")
        require(result["sha256"] == sha(ROOT / relative),
                f"Stale export evidence: {relative}")
        require(result["stable_during_inspection"], "Inspector modified model")
        require(result["mesh_count"] == 58 and result["triangles"] == 34246,
                f"Unexpected geometry inventory: {relative}")
        require(result["teeth"] == TEETH and not result["teeth_weight_errors"],
                f"Dentition inventory or rigid weights failed: {relative}")
        preservation = result["outside_head_preservation"]
        require(preservation["original_vertices_checked"] == 7769
                and preservation["original_uv_corners_checked"] == 24980
                and preservation["vertices_above_3e6"] == 0
                and preservation["uv_corners_above_3e6"] == 0,
                f"Outside-head preservation failed: {relative}")
        test = "_tests" in relative
        require(len(result["armatures"]) == int(test), "Unexpected armatures")
        if test:
            require(result["armatures"][0]["bone_count"] == 7,
                    "Test rig bone inventory failed")
            require(result["armatures"][0]["pose_transforms_max"] < 1e-5,
                    "Test rig not saved at neutral")
        blink_count = 0
        for mesh in result["mesh_stats"]:
            require(not any(mesh[k] for k in ["boundary", "wire", "nonmanifold",
                                              "nonfinite", "zero_area_triangles"]),
                    f"Structural defect: {relative}/{mesh['name']}")
            require(bool(mesh["uv_layers"]), "Missing UV layer")
            if test:
                require(mesh["weights_max"] <= 4 and mesh["unweighted_vertices"] == 0
                        and mesh["max_weight_sum_error"] < 1e-6,
                        f"Skin weights failed: {relative}/{mesh['name']}")
            for key in mesh["keys"]:
                if key["name"] == "Blink":
                    blink_count += 1
                    require(key["value"] == 0 and key["max_displacement"] > .01,
                            "Blink default or morph lost")
        require(blink_count == 2, "Two eyelid morphs required")

    test_sha = sha(ROOT / "source/english_mastiff_anatomy_tests.blend")
    oral = read(ROOT / "validation/oral_clearance.json")
    deformation = read(ROOT / "validation/deformation.json")
    for report in [oral, deformation]:
        require(report["blend"] == "source/english_mastiff_anatomy_tests.blend"
                and report["blend_sha256"] == test_sha, "Stale pose evidence")
    require([p["case"] for p in oral["poses"]] == POSES, "Missing sampled pose")
    require(not any(p["overlaps"] for p in oral["poses"]),
            "Recorded sampled oral contact check has intersections")
    require(not deformation["zeros"], "Zero-area deformation triangles")
    require(len(deformation["self_checks"]) == 24, "Missing lip/tongue self checks")
    require(deformation["facial_acceptance"] == "HOLD",
            "This checkpoint requires explicit known facial HOLD")
    return {"geometry": "58 meshes; 34,246 triangles; 42 teeth",
            "sampled_oral_contacts": "0 pairs in 8 poses, documented exclusions",
            "upper_lip_self_pairs": [r["oral_including_lip_nonadjacent_self_pairs"]
                for r in deformation["self_checks"]
                if r["part"] == "DM_CoatAndUpperHead"],
            "facial_visual_acceptance": "HOLD",
            "native_runtime": "NOT TESTED"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--freeze", action="store_true")
    args = parser.parse_args()
    summary = check_evidence()
    paths = owned_files()
    if args.freeze:
        data = {"asset_revision": "em-v004", "project_version": "0.2.0-dev.7",
                "status": "WORK IN PROGRESS / facial and visual HOLD",
                "evidence_environment": "Windows standalone Blender-Python 5.2.2 LTS",
                "base": BASE, "base_sha256": BASE_SHA,
                "meshy_credits_consumed": 0, "summary": summary,
                "files": {p: {"bytes": (ROOT / p).stat().st_size,
                               "sha256": sha(ROOT / p)} for p in paths}}
        MANIFEST.write_text(json.dumps(data, indent=2) + "\n",
                            encoding="utf-8", newline="\n")
    manifest = read(MANIFEST)
    if manifest["summary"] != summary or sorted(manifest["files"]) != paths:
        raise ValueError("Manifest inventory/evidence differs from checkpoint")
    folded = set()
    for relative, expected in manifest["files"].items():
        p = PurePosixPath(relative)
        if p.is_absolute() or ".." in p.parts or "\\" in relative:
            raise ValueError(f"Unsafe manifest path: {relative}")
        if relative.casefold() in folded:
            raise ValueError(f"Case-colliding manifest path: {relative}")
        folded.add(relative.casefold())
        actual = ROOT / relative
        if not actual.resolve().is_relative_to(ROOT.resolve()):
            raise ValueError(f"Manifest escapes checkpoint: {relative}")
        if actual.stat().st_size != expected["bytes"] or sha(actual) != expected["sha256"]:
            raise ValueError(f"Checkpoint bytes changed: {relative}")
    print(json.dumps({"checkpoint_integrity": "PASS", "files": len(paths), **summary}))


if __name__ == "__main__":
    main()
