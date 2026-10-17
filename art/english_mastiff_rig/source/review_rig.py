"""Evaluate actual baked assets and render selected poses; fresh bpy process only."""
import argparse
import hashlib
import json
import math
from pathlib import Path
import sys

import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'source'))
import build_rig
build_rig.skeleton()


def action_curves(action):
    return [c for layer in action.layers for strip in layer.strips
            for bag in strip.channelbags for c in bag.fcurves]


def coordinates(mesh):
    evaluated = mesh.evaluated_get(bpy.context.evaluated_depsgraph_get())
    data = evaluated.to_mesh()
    points = [evaluated.matrix_world @ v.co for v in data.vertices]
    evaluated.to_mesh_clear()
    return points


def aim(obj, target):
    obj.rotation_euler = (Vector(target)-obj.location).to_track_quat('-Z', 'Y').to_euler()


def studio():
    scene = bpy.context.scene
    scene.render.engine = 'CYCLES'
    scene.cycles.device = 'CPU'
    scene.cycles.samples = 12
    scene.cycles.use_denoising = True
    scene.render.resolution_x = 640
    scene.render.resolution_y = 640
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = 'PNG'
    scene.world = bpy.data.worlds.new('MastiffReview')
    scene.world.use_nodes = True
    bg = next(n for n in scene.world.node_tree.nodes if n.type == 'BACKGROUND')
    bg.inputs['Color'].default_value = (.16, .16, .16, 1)
    bg.inputs['Strength'].default_value = .7
    for name, pos, energy in [('Key', (3, -4, 5), 850), ('Fill', (-3, -2, 3), 550), ('Rim', (1, 3, 4), 800)]:
        light = bpy.data.lights.new(name, 'AREA')
        light.energy, light.size = energy, 4
        obj = bpy.data.objects.new(name, light)
        scene.collection.objects.link(obj)
        obj.location = pos
        aim(obj, (0, 0, .65))
    camera = bpy.data.objects.new('ReviewCamera', bpy.data.cameras.new('ReviewCamera'))
    scene.collection.objects.link(camera)
    camera.data.type, camera.data.ortho_scale = 'ORTHO', 2.45
    camera.location = (4, -5, 2.5)
    aim(camera, (0, 0, .62))
    scene.camera = camera
    # A real ground surface helps expose penetration and missing paw contacts.
    bpy.ops.mesh.primitive_plane_add(size=200, location=(0, 0, -.006))
    plane = bpy.context.object
    plane.name = 'ReviewGround'
    mat = bpy.data.materials.new('ReviewGround')
    mat.diffuse_color = (.07, .075, .08, 1)
    plane.data.materials.append(mat)
    return camera


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', default='source/english_mastiff_rig.blend')
    parser.add_argument('--label', default='blend')
    parser.add_argument('--render', action='store_true')
    args = parser.parse_args()
    path = (ROOT / args.input).resolve()
    if not path.is_relative_to(ROOT) or not args.label.replace('_', '').isalnum():
        raise ValueError('Invalid asset path/label')
    bpy.ops.wm.read_factory_settings(use_empty=True)
    if path.suffix == '.blend':
        bpy.ops.wm.open_mainfile(filepath=str(path))
    elif path.suffix == '.glb':
        bpy.ops.import_scene.gltf(filepath=str(path))
    elif path.suffix == '.fbx':
        bpy.ops.import_scene.fbx(filepath=str(path))
    else:
        raise ValueError('Unsupported input')
    scene = bpy.context.scene
    # glTF import creates an Icosphere custom-bone display helper, not asset geometry.
    meshes = [o for o in scene.objects if o.type == 'MESH' and any(m.type == 'ARMATURE' for m in o.modifiers)]
    arms = [o for o in scene.objects if o.type == 'ARMATURE']
    if len(meshes) != 1 or len(arms) != 1:
        raise ValueError('Expected one rigged model: '+str([(o.name, o.type) for o in scene.objects]))
    mesh, arm = meshes[0], arms[0]
    arm.animation_data.use_nla = False
    specs = json.loads((ROOT / 'metadata/clips.json').read_text())['clips']
    actions = {}
    for spec in specs:
        matches = [a for a in bpy.data.actions if a.name.endswith(spec['name'])]
        if len(matches) != 1:
            raise ValueError('Missing/ambiguous action '+spec['name']+': '+str([a.name for a in bpy.data.actions]))
        actions[spec['name']] = matches[0]
    weights = [[g.weight for g in v.groups if g.weight > 1e-7] for v in mesh.data.vertices]
    weighted = {g.name for g in mesh.vertex_groups}
    mesh.data.calc_loop_triangles()
    report = {'asset_revision': 'em-rig-v001', 'environment': 'Windows offline Blender-Python '+bpy.app.version_string,
              'input': args.input, 'input_sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
              'vertices': len(mesh.data.vertices), 'triangles': len(mesh.data.loop_triangles),
              'bones': sorted(b.name for b in arm.data.bones),
              'hierarchy': {b.name: b.parent.name if b.parent else None for b in arm.data.bones},
              'max_influences': max(map(len, weights)), 'unweighted_vertices': sum(not x for x in weights),
              'max_weight_sum_error': max(abs(sum(x)-1) for x in weights),
              'missing_weight_bones': sorted(weighted-set(arm.data.bones.keys())),
              'textures': [{'size': list(i.size), 'name': i.name} for i in bpy.data.images if i.type == 'IMAGE'],
              'clips': [], 'native': 'NOT TESTED', 'self_intersections': 'NOT TESTED by this structural evaluator',
              'artist_deformation_signoff': 'PENDING'}
    foot_names = {key: leg['bones'][4] for key, leg in build_rig.LEGS.items()}
    for spec in specs:
        action = actions[spec['name']]
        arm.animation_data.action = action
        scene.frame_start, scene.frame_end = 1, spec['frames']
        positions, feet, minimum_z, max_edge_ratio, min_edge_ratio = [], [], [], 1, 1
        rest_edges = [(e.vertices[0], e.vertices[1],
                       (mesh.data.vertices[e.vertices[0]].co-mesh.data.vertices[e.vertices[1]].co).length)
                      for e in mesh.data.edges]
        nonfinite = 0
        # Evaluate every baked frame's paw coordinates; geometry at quarter points.
        for frame in range(1, spec['frames']+1):
            scene.frame_set(frame)
            bpy.context.view_layer.update()
            feet.append({k: list(arm.matrix_world @ arm.pose.bones[n].head) for k, n in foot_names.items()})
            if frame in sorted(set([1, spec['frames'], 1+(spec['frames']-1)//4,
                                    1+(spec['frames']-1)//2, 1+3*(spec['frames']-1)//4])):
                points = coordinates(mesh)
                nonfinite += sum(not all(math.isfinite(x) for x in p) for p in points)
                minimum_z.append(min(p.z for p in points))
                for a, b, length in rest_edges:
                    if length > .005:
                        ratio = (points[a]-points[b]).length/length
                        max_edge_ratio = max(max_edge_ratio, ratio)
                        min_edge_ratio = min(min_edge_ratio, ratio)
                if frame in (1, spec['frames']):
                    positions.append(points)
        seam = max((a-b).length for a, b in zip(*positions)) if spec['loop'] else None
        curves = action_curves(action)
        report['clips'].append({'name': spec['name'], 'frames': spec['frames'],
                                'fcurves': len(curves), 'nonfinite_points': nonfinite,
                                'sampled_minimum_mesh_z': min(minimum_z),
                                'sampled_edge_ratio_min': min_edge_ratio,
                                'sampled_edge_ratio_max': max_edge_ratio,
                                'loop_position_seam': seam, 'feet': feet})
    if args.render:
        camera = studio()
        views = [('IdleBreathing', 1), ('Walk', 10), ('Trot', 7), ('Gallop', 5),
                 ('Sit', 61), ('LieDown', 73), ('SniffGround', 1), ('LimpFL', 12)]
        renders = []
        for kind, frame in views:
            arm.animation_data.action = actions['DM_EM_'+kind]
            scene.frame_set(frame)
            camera.location = (4, -5, 2.5)
            aim(camera, (0, 0, .62))
            destination = ROOT / 'previews' / (kind+'.png')
            destination.parent.mkdir(exist_ok=True)
            scene.render.filepath = str(destination)
            bpy.ops.render.render(write_still=True)
            renders.append({'path': destination.relative_to(ROOT).as_posix(),
                            'sha256': hashlib.sha256(destination.read_bytes()).hexdigest()})
        # Orthographic side sequence from actual walk action for motion inspection.
        arm.animation_data.action = actions['DM_EM_Walk']
        scene.render.resolution_x, scene.render.resolution_y = 480, 360
        camera.data.ortho_scale = 2.35
        camera.location = (5, 0, 1.2)
        aim(camera, (0, 0, .63))
        for frame in range(1, 37, 3):
            scene.frame_set(frame)
            destination = ROOT / 'previews/walk' / ('%03d.png' % frame)
            destination.parent.mkdir(exist_ok=True)
            scene.render.filepath = str(destination)
            bpy.ops.render.render(write_still=True)
        report['renders'] = renders
    # Feet are retained separately to keep the public summary readable.
    report_path = ROOT / 'validation' / (args.label+'_review.json')
    report_path.write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8', newline='\n')
    print(json.dumps({'report': report_path.name, 'bones': len(report['bones']), 'clips': len(actions),
                      'worst_edge_ratio': max(c['sampled_edge_ratio_max'] for c in report['clips']),
                      'lowest_z': min(c['sampled_minimum_mesh_z'] for c in report['clips']),
                      'maximum_loop_seam': max(c['loop_position_seam'] or 0 for c in report['clips'])}))


if __name__ == '__main__':
    main()
