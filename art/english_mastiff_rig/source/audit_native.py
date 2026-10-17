"""Read-only installed-animal evidence; writes portable observations, never native assets."""
import argparse
import hashlib
import json
import re
import xml.etree.ElementTree as ET
from pathlib import Path
import zipfile

ROOT = Path(__file__).resolve().parents[1]


def sha(data):
    return hashlib.sha256(data).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--game-root', type=Path, required=True)
    args = parser.parse_args()
    game = args.game_root.resolve()
    body = game / 'media/models_X/Skinned/Raccoon_Body.x'
    text = body.read_text()
    stack, hierarchy = [], []
    for match in re.finditer(r'Frame\s+(\w+)\s*\{|[{}]', text):
        if match.group(1):
            parent = next((n for n in reversed(stack) if n), None)
            hierarchy.append({'name': match.group(1), 'parent': parent})
            stack.append(match.group(1))
        elif match[0] == '{':
            stack.append(None)
        else:
            stack.pop()
    skin_names = re.findall(r'SkinWeights\s*\{\s*"([^"]+)"', text)
    clips = []
    for path in sorted((game / 'media/anims_X/Raccoon').glob('*.x')):
        content = path.read_text()
        rate = re.search(r'AnimTicksPerSecond\s*\{\s*(\d+)', content)
        clips.append({'path': path.relative_to(game).as_posix(),
                      'sha256': sha(path.read_bytes()), 'bytes': path.stat().st_size,
                      'header': content[:16], 'ticks_per_second': int(rate[1]) if rate else None,
                      'animation_sets': re.findall(r'AnimationSet\s+(\w+)', content)})
    nodes = []
    for path in sorted((game / 'media/AnimSets/raccoon').rglob('*.xml')):
        xml = ET.parse(path).getroot()
        nodes.append({'path': path.relative_to(game).as_posix(), 'sha256': sha(path.read_bytes()),
                      'name': xml.findtext('m_Name'), 'clip': xml.findtext('m_AnimName'),
                      'speed_scale': xml.findtext('m_SpeedScale'),
                      'deferred_bone': xml.findtext('m_DeferredBoneName'),
                      'conditions': [{c.tag: c.text for c in n} for n in xml.findall('m_Conditions')],
                      'transitions': [{c.tag: c.text for c in n} for n in xml.findall('m_Transitions')],
                      'events': [{c.tag: c.text for c in n} for n in xml.findall('m_Events')]})
    files = ['media/models_X/Skinned/Raccoon_Body.x',
             'media/scripts/generated/models_animals.txt',
             'media/scripts/generated/animations_meshes.txt',
             'media/lua/shared/Definitions/animal/RaccoonDefinitions.lua',
             'media/shaders/animalEffect.vert', 'media/shaders/animalEffect.frag']
    jar = game / 'projectzomboid.jar'
    classes = ['zombie/core/skinnedmodel/model/FileTask_AbstractLoadModel.class',
               'zombie/core/skinnedmodel/model/FileTask_LoadMesh.class',
               'zombie/core/skinnedmodel/model/FileTask_LoadAnimation.class',
               'zombie/core/skinnedmodel/model/ModelMesh.class',
               'zombie/core/skinnedmodel/model/jassimp/ProcessedAiScene.class',
               'zombie/core/skinnedmodel/animation/AnimationPlayer.class']
    with zipfile.ZipFile(jar) as archive:
        class_hashes = {name: sha(archive.read(name)) for name in classes}
    report = {
        'asset_revision': 'em-rig-v001', 'tested_project_version': '0.2.0-dev.7',
        'environment': 'read-only Windows installed Build 42.21 / Steam 25485521 source inspection; not runtime',
        'files': [{'path': p, 'sha256': sha((game / p).read_bytes())} for p in files],
        'jar_sha256': sha(jar.read_bytes()), 'packaged_classes': class_hashes,
        'native_frames': hierarchy, 'weighted_frame_names': skin_names,
        'clips': clips, 'anim_nodes': nodes,
        'observations': {
            'formats': 'Inspected raccoon body and 13 animation clips use DirectX text X. FileTask_AbstractLoadModel bytecode explicitly recognizes existing .fbx, .glb (glTF) and .x paths. This is source support, not proof this particular new skin/animation asset loads.',
            'skeleton': '35 named frames, 25 weighted names; Bip01 hierarchy is quadruped despite arm-style front-leg names. No jaw/ear or three-spine match.',
            'shader': 'animalEffect.vert uses MatrixPalette[60] and four vertex weights; fragment shader samples one Texture, with native vertex lighting. No normal/metallic/roughness sampler in this inspected shader.',
            'registration': 'Raccoon_Body -> Skinned/Raccoon_Body; static=false, shader=animalEffect, animationsMesh=Raccoon. Raccoon animation mesh references animationDirectory=Raccoon; animal definitions select animset=raccoon.',
            'states': 'XML observations include bMoving, animalRunning, idleAction and native transitions/events. No new variables or Lua animation setters implemented.',
            'root_motion': 'Native AnimationPlayer exposes deferred movement/rotation and counter-rotation descriptors. Clip-to-world ownership, deferred axis, extraction and speed match remain UNKNOWN for this new rig.',
            'scale_axes': 'New authoring rig retains source Blender units, +X animal-left, -Y forward, Z up; translates source minimum Z to floor only. Native handedness, model scale and exact importer bind transformation are NOT CALIBRATED.',
            'dedicated': 'Authoring-only assets are excluded from mod assembly. No server skeleton/visual state changes; eventual clip intent/state must be server-controlled with client rendering tested through join/rejoin.',
        },
        'strategy': 'Original 42-bone intermediate large-mastiff rig; four influences maximum, sockets as non-joint empties. Not a copied/rebranded native rig. Semantic correspondence only, no claimed native retarget or bind-pose match.',
        'native_client': 'NOT TESTED', 'dedicated': 'NOT TESTED',
        'remaining': ['exact import axes/units/bind matrices', 'native export conversion and model/animation registration',
                      'deferred movement and authoritative speed calibration', 'animalEffect texture adaptation',
                      'attachment render/socket API', 'corpse/skeleton presentation', 'client and dedicated runtime loading'],
    }
    destination = ROOT / 'validation/native_audit.json'
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8', newline='\n')
    print(json.dumps({'frames': len(hierarchy), 'weighted_names': len(skin_names),
                      'clips': len(clips), 'nodes': len(nodes), 'report': destination.name}))


if __name__ == '__main__':
    main()
