"""Independently reopen every skeleton-only FBX in a fresh reset scene."""
import hashlib
import json
from pathlib import Path
import bpy

ROOT = Path(__file__).resolve().parents[1]
specs = json.loads((ROOT / 'metadata/clips.json').read_text())['clips']
bones = {b['name']: b['parent'] for b in json.loads((ROOT / 'metadata/rig.json').read_text())['bones']}
results = []
for spec in specs:
    path = ROOT / 'animations' / (spec['name']+'.fbx')
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.fbx(filepath=str(path))
    arms = [o for o in bpy.context.scene.objects if o.type == 'ARMATURE']
    assert len(arms) == 1
    arm = arms[0]
    hierarchy = {b.name: b.parent.name if b.parent else None for b in arm.data.bones}
    assert hierarchy == bones
    assert len(bpy.data.actions) == 1 and bpy.data.actions[0].name.endswith(spec['name']), [a.name for a in bpy.data.actions]
    action = bpy.data.actions[0]
    duration = (action.frame_range[1]-action.frame_range[0])/bpy.context.scene.render.fps
    assert abs(duration-spec['seconds']) < 1/24+1e-6
    results.append({'name': spec['name'], 'sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
                    'bones': len(hierarchy), 'seconds': duration, 'action': action.name,
                    'status': 'PASS offline reimport; no native/artist approval'})
report = {'environment': 'Windows standalone Blender-Python '+bpy.app.version_string, 'clips': results}
(ROOT / 'validation/standalone_clips.json').write_text(json.dumps(report, indent=2)+'\n',
                                                      encoding='utf-8', newline='\n')
print(json.dumps({'status': 'PASS', 'individually_reimported_fbx_clips': len(results)}))
