"""Reopen editable source and independently import GLB in a fresh bpy process.

Offline authoring checks only. This does not test Project Zomboid's importer,
native rigs, animation states, species registration, gameplay or multiplayer.
"""
from pathlib import Path
import hashlib
import json
import struct

import bpy
import bmesh
import numpy as np
from mathutils import Quaternion, Vector
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
PROJECT = ROOT.parents[1]


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def points(obj):
    bpy.context.view_layer.update()
    evaluated = obj.evaluated_get(bpy.context.evaluated_depsgraph_get())
    mesh = evaluated.to_mesh()
    result = np.array([tuple(evaluated.matrix_world @ v.co) for v in mesh.vertices])
    evaluated.to_mesh_clear()
    return result


def inventory(source):
    meshes = sorted([o for o in bpy.context.scene.objects if o.type == 'MESH' and o.name.startswith('GSD_')], key=lambda o: o.name)
    rigs = [o for o in bpy.context.scene.objects if o.type == 'ARMATURE']
    require(len(rigs) == 1, 'Exactly one original rig required')
    rig = rigs[0]
    require(len(meshes) == 42 and len(rig.data.bones) == 29, 'Model/rig inventory changed')
    require('GSD_CoatBody' in [o.name for o in meshes], 'Main body missing')
    body = bpy.data.objects['GSD_CoatBody']
    bm = bmesh.new()
    bm.from_mesh(body.data)
    if not source:
        # glTF stores separate vertices at UV seams. Weld only this disposable
        # topology-check copy; preserve the actual imported/exported mesh.
        bmesh.ops.remove_doubles(bm, verts=list(bm.verts), dist=1e-6)
    require(all(e.is_manifold for e in bm.edges), 'Body has a nonmanifold edge')
    require(all(f.calc_area() > 1e-10 for f in bm.faces), 'Body has degenerate faces')
    seen = set()
    components = 0
    for v in bm.verts:
        if v in seen:
            continue
        components += 1
        queue = [v]
        seen.add(v)
        while queue:
            current = queue.pop()
            for edge in current.link_edges:
                nxt = edge.other_vert(current)
                if nxt not in seen:
                    seen.add(nxt)
                    queue.append(nxt)
    bm.free()
    require(components == 1, 'Coat body must be a single connected outer surface')
    unweighted = badsum = excessive = 0
    for obj in meshes:
        require(obj.parent is rig, 'Mesh is not parented to original rig: ' + obj.name)
        require(any(m.type == 'ARMATURE' and m.object is rig for m in obj.modifiers), 'Skin modifier missing')
        require(all(np.isfinite(tuple(v.co)).all() for v in obj.data.vertices), 'Nonfinite mesh')
        for v in obj.data.vertices:
            weights = [g.weight for g in v.groups if g.weight > 0]
            unweighted += len(weights) == 0
            badsum += abs(sum(weights) - 1) > 1e-5
            excessive += len(weights) > 4
        if source:
            require(obj.get('project_version') == (PROJECT / 'VERSION').read_text().strip(), 'Stale binary version property')
            require(np.allclose(obj.matrix_world, np.eye(4), atol=1e-7), 'Nonidentity source mesh transform')
    require(unweighted == badsum == excessive == 0, 'Invalid skin weights')
    require(body.data.uv_layers.active is not None, 'No UVs')
    uvs = np.array([tuple(u.uv) for u in body.data.uv_layers.active.data])
    require(np.isfinite(uvs).all() and uvs.min() >= -1e-6 and uvs.max() <= 1 + 1e-6, 'Invalid UV coordinates')
    texture = [n.image for mat in body.data.materials if mat.use_nodes
               for n in mat.node_tree.nodes if n.type == 'TEX_IMAGE' and n.image]
    require(len(texture) == 1 and tuple(texture[0].size) == (1024, 1024), 'Missing coat texture')
    if source:
        require(texture[0].packed_file is not None, 'Editable source needs packed coat texture')
        require(texture[0].filepath.startswith('//'), 'Texture path must be portable')
        require(rig.get('project_version') == (PROJECT / 'VERSION').read_text().strip(), 'Stale rig version property')
        require(np.allclose(rig.matrix_world, np.eye(4), atol=1e-7), 'Nonidentity source rig transform')
    require(not bpy.data.actions, 'Unexpected authored/imported animation clips')
    allpoints = np.concatenate([points(o) for o in meshes])
    neutral = points(body)
    motions = {}
    for name, angle, axis in [('head', .35, (0, 0, 1)), ('front_lower_L', .50, (0, 1, 0)),
                             ('rear_lower_R', -.45, (0, 1, 0)), ('tail_2', .5, (0, 0, 1))]:
        bone = rig.pose.bones[name]
        bone.rotation_mode = 'QUATERNION'
        # Both source and import may have different object-axis conventions.
        world_basis = rig.matrix_world.to_3x3() @ bone.bone.matrix_local.to_3x3()
        bone.rotation_quaternion = Quaternion((world_basis.inverted() @ Vector(axis)).normalized(), angle)
        posed = points(body)
        delta = np.linalg.norm(posed - neutral, axis=1)
        require(np.isfinite(posed).all() and (delta > .001).sum() > 10 and .005 < delta.max() < .25,
                'Pose failed: ' + name)
        motions[name] = round(float(delta.max()), 6)
        bone.rotation_quaternion = (1, 0, 0, 0)
        bpy.context.view_layer.update()
    return {
        'mesh_objects': len(meshes), 'total_triangles': sum(sum(len(p.vertices) - 2 for p in o.data.polygons) for o in meshes),
        'bones': sorted(b.name for b in rig.data.bones),
        'bone_parent_map': {b.name: b.parent.name if b.parent else None for b in rig.data.bones},
        'body_components': components, 'topology_check_weld_tolerance_m': 0 if source else 1e-6,
        'bounds_min_m': allpoints.min(axis=0).round(6).tolist(),
        'bounds_max_m': allpoints.max(axis=0).round(6).tolist(),
        'pose_max_displacement_m': motions, 'skin_weight_check': 'PASS', 'uv_texture_check': 'PASS',
    }


def inspect_glb(path):
    data = path.read_bytes()
    magic, version, length = struct.unpack_from('<4sII', data, 0)
    require(magic == b'glTF' and version == 2 and length == len(data), 'Invalid GLB header')
    jsonlen, jsontype = struct.unpack_from('<I4s', data, 12)
    require(jsontype == b'JSON', 'Missing glTF JSON')
    doc = json.loads(data[20:20 + jsonlen])
    require(len(doc.get('skins', [])) == 1 and len(doc['skins'][0]['joints']) == 29, 'GLB skin inventory')
    require(len(doc.get('images', [])) == 1 and 'bufferView' in doc['images'][0], 'Texture must be embedded')
    require(not doc.get('animations') and not doc.get('cameras'), 'Unexpected animations/cameras')
    require(not doc.get('extensions', {}).get('KHR_lights_punctual'), 'Studio lights leaked into GLB')
    require(not any('uri' in b for b in doc.get('buffers', [])), 'External GLB buffer')
    require(all('extras' not in n for n in doc['nodes']), 'Unexpected private metadata in GLB')
    for mesh in doc['meshes']:
        for primitive in mesh['primitives']:
            require(primitive.get('mode', 4) == 4, 'Interchange mesh must be triangulated')
            require('JOINTS_0' in primitive['attributes'] and 'WEIGHTS_0' in primitive['attributes'], 'Missing skin data')
    return {'embedded_textures': len(doc['images']), 'skins': len(doc['skins']), 'joint_count': 29,
            'external_resources': 0, 'studio_objects_exported': 0, 'clips_exported': 0}


def main():
    build = json.loads((ROOT / 'validation' / 'asset_validation.json').read_text())
    require(build.get('preview_status') == 'RENDERED_THIS_BUILD',
            'Complete asset validation requires previews rendered in this build; run builder without --no-render')
    require(build['project_version'] == (PROJECT / 'VERSION').read_text().strip(), 'Stale build report')
    for relative, record in build['files'].items():
        p = ROOT / relative
        require(hashlib.sha256(p.read_bytes()).hexdigest() == record['sha256'], 'Stale provenance hash: ' + relative)
    for p in (ROOT / 'previews').glob('*.png'):
        with Image.open(p) as im:
            im.verify()
    bpy.ops.wm.open_mainfile(filepath=str(ROOT / 'source' / 'german_shepherd.blend'))
    source = inventory(True)
    envelope = inspect_glb(ROOT / 'interchange' / 'german_shepherd.glb')
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=str(ROOT / 'interchange' / 'german_shepherd.glb'))
    imported = inventory(False)
    require(source['bones'] == imported['bones'], 'Bone names lost')
    require(source['bone_parent_map'] == imported['bone_parent_map'], 'Bone hierarchy changed')
    require(source['total_triangles'] == imported['total_triangles'], 'Triangle count changed')
    for key in ['bounds_min_m', 'bounds_max_m']:
        require(np.allclose(source[key], imported[key], atol=2e-5), 'Bounds changed: ' + key)
    for bone, displacement in source['pose_max_displacement_m'].items():
        require(abs(displacement - imported['pose_max_displacement_m'][bone]) < 2e-5,
                'Roundtrip deformation changed: ' + bone)
    report = {
        'project_version': (PROJECT / 'VERSION').read_text().strip(), 'asset_revision': build['asset_revision'],
        'environment': 'Offline Blender Python ' + bpy.app.version_string,
        'blend_reopen': 'PASS', 'glb_import_roundtrip': 'PASS', 'provenance_hash_check': 'PASS',
        'preview_provenance': 'RENDERED_THIS_BUILD',
        'source': source, 'glb_envelope': envelope, 'imported': imported,
        'G6': 'NOT TESTED', 'G7': 'BLOCKED / NOT TESTED', 'G8': 'BLOCKED',
        'scope': 'Blender authoring and review interchange only; no native PZ importer/state validation.',
        'validator_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    }
    (ROOT / 'validation' / 'roundtrip_validation.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print('PASS: editable source, packed texture, original hierarchy, normalized skins, bounds and four deformation probes survived GLB roundtrip.', flush=True)


if __name__ == '__main__':
    main()
