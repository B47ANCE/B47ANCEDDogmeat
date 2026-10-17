"""Inspect/render a Meshy interchange in a fresh standalone Blender-Python process.

Never run in an unsaved interactive scene. This script resets only its own
process and writes beneath the selected asset directory; no game access.
"""
import argparse
import hashlib
import json
import math
from pathlib import Path

import bpy
import bmesh
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[1]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def inspect_mesh(obj):
    mesh = obj.data
    mesh.calc_loop_triangles()
    bm = bmesh.new()
    bm.from_mesh(mesh)
    raw_boundary = sum(e.is_boundary for e in bm.edges)
    bmesh.ops.remove_doubles(bm, verts=list(bm.verts), dist=1e-6)
    remaining = set(bm.verts)
    components = []
    while remaining:
        stack = [remaining.pop()]
        size = 0
        while stack:
            v = stack.pop()
            size += 1
            for edge in v.link_edges:
                other = edge.other_vert(v)
                if other in remaining:
                    remaining.remove(other)
                    stack.append(other)
        components.append(size)
    result = {'name': obj.name, 'vertices': len(mesh.vertices), 'polygons': len(mesh.polygons),
              'triangles': len(mesh.loop_triangles), 'uv_layers': len(mesh.uv_layers),
              'raw_boundary_edges': raw_boundary,
              'welded_boundary_edges': sum(e.is_boundary for e in bm.edges),
              'welded_nonmanifold_edges': sum(not e.is_manifold for e in bm.edges),
              'welded_components_vertices': sorted(components, reverse=True),
              'nonfinite_coordinates': sum(not all(math.isfinite(x) for x in v.co) for v in mesh.vertices),
              'zero_area_triangles': sum(t.area < 1e-12 for t in mesh.loop_triangles),
              'materials': [m.name if m else None for m in mesh.materials]}
    bm.free()
    return result


def aim(obj, target):
    obj.rotation_euler = (Vector(target) - obj.location).to_track_quat('-Z', 'Y').to_euler()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', type=Path, default=ROOT / 'source/meshy_preview.glb')
    parser.add_argument('--label', default='geometry_preview')
    parser.add_argument('--render', action='store_true')
    args = parser.parse_args()
    args.input = args.input.resolve()
    if not args.input.resolve().is_relative_to(ROOT) or not args.label.replace('_', '').isalnum():
        raise ValueError('Input/label must stay within this asset')
    bpy.ops.wm.read_factory_settings(use_empty=True)
    if args.input.suffix.lower() == '.glb':
        bpy.ops.import_scene.gltf(filepath=str(args.input.resolve()))
    elif args.input.suffix.lower() == '.fbx':
        bpy.ops.import_scene.fbx(filepath=str(args.input.resolve()))
    else:
        raise ValueError('Expected GLB or FBX')
    scene = bpy.context.scene
    meshes = [o for o in scene.objects if o.type == 'MESH']
    if not meshes:
        raise ValueError('No actual model geometry')
    bpy.context.view_layer.update()
    points = [o.matrix_world @ Vector(p) for o in meshes for p in o.bound_box]
    low = Vector(tuple(min(p[i] for p in points) for i in range(3)))
    high = Vector(tuple(max(p[i] for p in points) for i in range(3)))
    dimensions = high-low
    report = {'project_version': (ROOT.parents[1] / 'VERSION').read_text().strip(),
              'asset_revision': 'em-v001', 'stage': args.label,
              'environment': 'Windows standalone Blender-Python ' + bpy.app.version_string + '; not PZ',
              'source': args.input.relative_to(ROOT).as_posix(), 'sha256': sha(args.input),
              'meshes': [inspect_mesh(o) for o in meshes],
              'dimensions_blender_units': list(dimensions), 'physical_scale': 'NOT CALIBRATED',
              'source_bounds': {'minimum': list(low), 'maximum': list(high)},
              'armatures': sum(o.type == 'ARMATURE' for o in scene.objects),
              'animations': len(bpy.data.actions), 'textures': [], 'renders': [],
              'pz_compatibility': 'NOT TESTED', 'rigging_readiness': 'UNRIGGED; deformation NOT TESTED'}
    report['triangles'] = sum(m['triangles'] for m in report['meshes'])
    report['materials'] = []
    for material in bpy.data.materials:
        if material.use_nodes:
            report['materials'].append({'name': material.name,
                'nodes': [{'name': n.name, 'type': n.bl_idname,
                           'image': n.image.name if n.type == 'TEX_IMAGE' and n.image else None}
                          for n in material.node_tree.nodes],
                'links': [{'from': l.from_node.name+'.'+l.from_socket.name,
                           'to': l.to_node.name+'.'+l.to_socket.name}
                          for l in material.node_tree.links]})
    for im in bpy.data.images:
        if im.type == 'IMAGE':
            report['textures'].append({'name': im.name, 'size': list(im.size), 'channels': im.channels,
                                       'colorspace': im.colorspace_settings.name})
    (ROOT / 'validation').mkdir(exist_ok=True)
    if args.render:
        center = (low+high)*0.5
        span = max(dimensions)
        scene.render.engine = 'CYCLES'
        scene.cycles.device = 'CPU'
        scene.cycles.samples = 12
        scene.cycles.use_denoising = True
        scene.render.resolution_x = scene.render.resolution_y = 640
        scene.render.resolution_percentage = 100
        scene.render.image_settings.file_format = 'PNG'
        scene.world = bpy.data.worlds.new('ReviewWorld')
        scene.world.use_nodes = True
        scene.world.node_tree.nodes['Background'].inputs['Color'].default_value = (0.22, 0.22, 0.22, 1)
        scene.world.node_tree.nodes['Background'].inputs['Strength'].default_value = 0.5
        scene.view_settings.view_transform = 'AgX'
        for name, offset, power, size in [('Key', (2, -3, 4), 700, 4), ('Fill', (-3, -2, 2), 400, 3),
                                          ('Rim', (1, 3, 3), 600, 3)]:
            light = bpy.data.lights.new(name, 'AREA')
            light.energy = power*span*span
            light.shape = 'DISK'
            light.size = size*span
            obj = bpy.data.objects.new(name, light)
            scene.collection.objects.link(obj)
            obj.location = center + Vector(offset)*span
            aim(obj, center)
        camera_data = bpy.data.cameras.new('ReviewCamera')
        camera_data.type = 'ORTHO'
        camera_data.ortho_scale = span*1.3
        camera = bpy.data.objects.new('ReviewCamera', camera_data)
        scene.collection.objects.link(camera)
        scene.camera = camera
        views = {'three_quarter': (3, -5, 2.3), 'axis_x_positive': (5, 0, 0.3),
                 'axis_x_negative': (-5, 0, 0.3), 'axis_y_positive': (0, 5, 0.3),
                 'axis_y_negative': (0, -5, 0.3)}
        folder = ROOT / 'previews' / args.label
        folder.mkdir(parents=True, exist_ok=True)
        for name, offset in views.items():
            camera.location = center + Vector(offset)*span
            aim(camera, center)
            target = folder / (name+'.png')
            scene.render.filepath = str(target)
            bpy.ops.render.render(write_still=True)
            report['renders'].append({'path': target.relative_to(ROOT).as_posix(), 'sha256': sha(target)})
        for im in bpy.data.images:
            if im.type == 'IMAGE' and im.has_data:
                im.pack()
        target = ROOT / 'source' / ('english_mastiff_'+args.label+'.blend')
        bpy.ops.wm.save_as_mainfile(filepath=str(target))
        report['editable_source'] = {'path': target.relative_to(ROOT).as_posix(), 'sha256': sha(target)}
    output = ROOT / 'validation' / (args.label+'.json')
    output.write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8', newline='\n')
    print(json.dumps({'triangles': report['triangles'], 'meshes': report['meshes'],
                      'dimensions_blender_units': report['dimensions_blender_units'],
                      'textures': report['textures'], 'report': str(output)}))


if __name__ == '__main__':
    main()
