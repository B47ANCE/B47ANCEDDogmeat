"""Read-only serialized tail-root blend audit; prints JSON and writes no assets.

Requires NumPy. Run from any directory; --root can override the repository root.
This samples authored frames and health blends, not native game playback or
between-frame/state-transition blending. Distances are source authoring units.
"""
import argparse
import hashlib
import json
import re
from pathlib import Path

import numpy as np


def read_clip(path):
    text = path.read_text(encoding="utf-8")
    name = re.search(r"AnimationSet\s+(\w+)\s*\{", text)[1]
    fps = int(re.search(r"AnimTicksPerSecond\s*\{\s*(\d+);", text)[1])
    bones = {}
    for block in re.split(r"\bAnimation\s*\{\s*\{\s*", text)[1:]:
        bone = block.split("}", 1)[0].strip()
        tracks = {}
        for match in re.finditer(
            r"AnimationKey\s+K\d\s*\{\s*(\d+);\s*(\d+);([^}]+)\}", block
        ):
            keys = [
                (int(k[1]), tuple(float(v) for v in k[2].split(",")))
                for k in re.finditer(r"(\d+);\d+;([^;]+);;", match[3])
            ]
            assert len(keys) == int(match[2])
            tracks[int(match[1])] = keys
        bones[bone] = tracks
    return name, fps, bones


def read_bind(path):
    text = path.read_text(encoding="utf-8").split("AnimationSet")[0]
    frames = []
    for match in re.finditer(r"\bFrame\s+(\w+)\s*\{", text):
        depth, index = 1, match.end()
        while depth:
            depth += (text[index] == "{") - (text[index] == "}")
            index += 1
        matrix = re.search(
            r"FrameTransformMatrix\s*\{\s*([^}]+)", text[match.end():index]
        )
        values = [float(x) for x in matrix[1].strip().rstrip(";").split(",")]
        frames.append(
            (match[1], match.start(), index, np.array(values).reshape(4, 4).T)
        )
    parents, rest = {}, {}
    for name, start, end, local in frames:
        enclosing = [f for f in frames if f[1] < start < f[2]]
        parent = max(enclosing, key=lambda f: f[1])[0] if enclosing else None
        parents[name] = parent
        rest[name] = rest[parent] @ local if parent else local
    assert len(parents) == 34
    return parents, rest


def quat(values):
    value = np.array(values)
    value[1:] *= -1  # Inverse of our DirectX quaternion-conjugation export.
    return value / np.linalg.norm(value)


def matrix(q, position):
    w, x, y, z = q / np.linalg.norm(q)
    return np.array([
        [1 - 2*(y*y + z*z), 2*(x*y - w*z), 2*(x*z + w*y), position[0]],
        [2*(x*y + w*z), 1 - 2*(x*x + z*z), 2*(y*z - w*x), position[1]],
        [2*(x*z - w*y), 2*(y*z + w*x), 1 - 2*(x*x + y*y), position[2]],
        [0, 0, 0, 1.0],
    ])


def audit(root, subdivisions=100):
    motion = root / "art/german_shepherd_motion_v2/anims"
    native = root / "art/german_shepherd_motion_v2"
    bind_report = json.loads((native / "validation/native-bind.json").read_text())
    parents, rest = read_bind(motion / "B47Dogmeat_Idle_Low.x")
    coordinate_map = np.array(bind_report["native_to_authoring"])
    inverse_map = np.linalg.inv(coordinate_map)
    inverse_bind = np.linalg.inv(rest["Bip01_Tail"])
    pivot = np.r_[bind_report['tail_root'],1.]
    suffixes = ("Low", "H125", "H25", "H375", "H50", "H625", "H75", "H875", "High")
    chain, name = [], "Bip01_Tail"
    while name:
        chain.append(name)
        name = parents[name]
    chain.reverse()

    def global_frame(bones, frame_index, include_tail=True):
        result = np.eye(4)
        for bone in chain if include_tail else chain[:-1]:
            result = result @ matrix(
                quat(bones[bone][0][frame_index][1]),
                bones[bone][2][frame_index][1],
            )
        return result

    maximum_all = {"error": 0}
    maximum_anchor = 0
    minimum_dot = 1
    frame_count = sample_count = 0
    per_clip = {}
    for kind in ("Idle", "Look", "Walk", "Run"):
        anchors = [read_clip(motion / f"B47Dogmeat_{kind}_{s}.x")[2] for s in suffixes]
        neutral = read_clip(motion / f"B47Dogmeat_{kind}_Neutral.x")[2]
        count = len(anchors[0]["Bip01_Tail"][0])
        frame_count += count
        maximum = {"error": 0}
        # Only the tail differs between anchors. This justifies sharing its
        # parent global matrix rather than blending unaffected ancestor tracks.
        for anchor in anchors:
            for bone in chain[:-1]:
                assert anchor[bone] == neutral[bone], (kind, bone)
        for frame_index in range(count):
            expected = (
                coordinate_map @ global_frame(neutral, frame_index)
                @ inverse_bind @ inverse_map @ pivot
            )[:3]
            parent_global = global_frame(anchors[0], frame_index, False)
            for segment, (low, high) in enumerate(zip(anchors, anchors[1:])):
                qa = quat(low["Bip01_Tail"][0][frame_index][1])
                qb = quat(high["Bip01_Tail"][0][frame_index][1])
                pa = np.array(low["Bip01_Tail"][2][frame_index][1])
                pb = np.array(high["Bip01_Tail"][2][frame_index][1])
                dot = np.dot(qa, qb)
                if dot < 0:
                    qb, dot = -qb, -dot
                minimum_dot = min(minimum_dot, float(dot))
                for index in range(subdivisions + 1):
                    fraction = index / subdivisions
                    # Observed PZMath.slerp uses trig SLERP only when
                    # 1 - abs(dot) > .1. HelperFunctions normalizes its result.
                    if 1 - dot > .1:
                        theta = np.arccos(dot)
                        q = (np.sin((1-fraction)*theta)*qa
                             + np.sin(fraction*theta)*qb) / np.sin(theta)
                    else:
                        q = (1-fraction)*qa + fraction*qb
                    blended = parent_global @ matrix(q, (1-fraction)*pa + fraction*pb)
                    actual = (
                        coordinate_map @ blended @ inverse_bind @ inverse_map @ pivot
                    )[:3]
                    error = float(np.linalg.norm(actual - expected))
                    sample_count += 1
                    if index in (0, subdivisions):
                        maximum_anchor = max(maximum_anchor, error)
                    if error > maximum["error"]:
                        maximum = dict(error=error, frame=frame_index,
                                       segment=segment, fraction=fraction,
                                       health=(segment+fraction)/8,
                                       shift=(actual-expected).tolist())
        per_clip[kind] = dict(frames=count, maximum=maximum)
        if maximum["error"] > maximum_all["error"]:
            maximum_all = dict(kind=kind, **maximum)
    hashes = {}
    for variant in bind_report["variants"].values():
        path = native / "models" / (variant["model"] + ".glb")
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        assert digest == variant["glb_sha256"], path
        hashes[path.name] = digest
    return dict(
        sampled_maximum=maximum_all,
        per_clip=per_clip,
        max_anchor_error=maximum_anchor,
        min_adjacent_quat_dot=minimum_dot,
        frame_samples=frame_count,
        blend_samples=sample_count,
        source_clip_count=len(list(motion.glob("*.x"))),
        audit_source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        clip_sha256={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(motion.glob("*.x"))},
        units="source authoring coordinates",
        method="serialized local PRS; shortest-path NLERP/SLERP; compare tail-root skin transform to neutral same frame",
        limitations="double precision emulation; finite health grid; authored frames only; no temporal or state-transition blending; not PZ runtime evidence",
        immutable_models_match_recorded_sha256=hashes,
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--subdivisions", type=int, default=100)
    args = parser.parse_args()
    assert args.subdivisions > 0
    report = audit(args.root, args.subdivisions)
    assert report["sampled_maximum"]["error"] < 0.0041
    assert report["max_anchor_error"] < 1e-6
    report["status"] = "OFFLINE PASS"
    report["project_version"] = (args.root / "VERSION").read_text().strip()
    print(json.dumps(report, indent=2))
