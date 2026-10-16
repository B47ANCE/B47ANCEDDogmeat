"""Bounded local cleanup/export of the original textured Meshy dog; no paid API.

Fresh standalone Blender-Python only. Preserve service files; remove only tiny
one-face fins after welding coincident UV-seam vertices. Refuse other defects.
"""
import hashlib
import json
from pathlib import Path
import sys

import bpy
import bmesh
from mathutils import Vector

sys.path.insert(0, str(Path(__file__).resolve().parent))
from inspect_english_mastiff import inspect_mesh

ROOT = Path(__file__).resolve().parents[1]


def main():
    original = ROOT / 'source/meshy_textured.glb'
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=str(original))
    objects = [o for o in bpy.context.scene.objects if o.type == 'MESH']
    if len(objects) != 1:
        raise ValueError('Expected this inspected single-mesh source')
    obj = objects[0]
    before = inspect_mesh(obj)
    bounds = [obj.matrix_world @ Vector(p) for p in obj.bound_box]
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bmesh.ops.remove_doubles(bm, verts=list(bm.verts), dist=1e-6)
    deleted = []
    for _ in range(4):
        fins = [f for f in bm.faces if f.calc_area() < 1e-4
                and any(e.is_boundary for e in f.edges)
                and any(len(e.link_faces) == 3 for e in f.edges)
                and all(len(e.link_faces) in (1, 3) for e in f.edges)]
        if not fins:
            break
        deleted.extend({'area_source_units_squared': f.calc_area(),
                        'center_source_units': list(f.calc_center_median())} for f in fins)
        if len(deleted) > 8:
            raise ValueError('Repair exceeds the reviewed local scope')
        bmesh.ops.delete(bm, geom=fins, context='FACES')
    if any(not e.is_manifold for e in bm.edges):
        raise ValueError('Remaining geometry requires manual review; do not invent a clean result')
    bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
    bm.to_mesh(obj.data)
    bm.free()
    obj.data.update()
    bpy.context.view_layer.update()
    after = inspect_mesh(obj)
    if (after['welded_nonmanifold_edges'] or after['zero_area_triangles'] or after['nonfinite_coordinates']
            or len(after['welded_components_vertices']) != 1 or not 8000 <= after['triangles'] <= 15000):
        raise ValueError('Cleaned geometry fails this asset target')
    after_bounds = [obj.matrix_world @ Vector(p) for p in obj.bound_box]
    delta = max((a-b).length for a, b in zip(bounds, after_bounds))
    if delta > 1e-6:
        raise ValueError('Cleanup unexpectedly changed the source bounds')
    destination = ROOT / 'interchange'
    destination.mkdir(exist_ok=True)
    for image in bpy.data.images:
        if image.type == 'IMAGE' and image.has_data:
            image.pack()
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    glb = destination / 'english_mastiff.glb'
    fbx = destination / 'english_mastiff.fbx'
    bpy.ops.export_scene.gltf(filepath=str(glb), export_format='GLB', use_selection=True,
                              export_animations=False)
    # FBX cannot preserve glTF's packed channel graph. Give its exporter the
    # provider's separate scalar PNGs through direct Principled inputs instead.
    material = obj.data.materials[0].copy()
    material.name = 'EnglishMastiff_FBX_PBR'
    obj.data.materials[0] = material
    shader = next(n for n in material.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
    for socket, filename in [('Roughness', 'roughness.png'), ('Metallic', 'metallic.png')]:
        image = bpy.data.images.load(str(ROOT / 'source/meshy_textured_textures' / filename))
        image.colorspace_settings.name = 'Non-Color'
        image.pack()
        node = material.node_tree.nodes.new('ShaderNodeTexImage')
        node.image = image
        material.node_tree.links.new(node.outputs['Color'], shader.inputs[socket])
    bpy.ops.export_scene.fbx(filepath=str(fbx), use_selection=True, object_types={'MESH'},
                             add_leaf_bones=False, bake_anim=False, path_mode='COPY', embed_textures=True)
    report = {'project_version': (ROOT.parents[1] / 'VERSION').read_text().strip(), 'asset_revision': 'em-v001',
              'environment': 'Windows standalone Blender-Python ' + bpy.app.version_string + '; not PZ',
              'input': 'source/meshy_textured.glb', 'input_sha256': hashlib.sha256(original.read_bytes()).hexdigest(),
              'processing': 'Weld coincident geometry vertices at 1e-6 source units, preserve per-loop UVs; delete reviewed tiny one-face fins; recalculate normals. No remesh, sculpt, resizing, rig or animation.',
              'before': before, 'after': after, 'removed_fins': deleted,
              'bounds_maximum_delta_source_units': delta, 'physical_scale': 'NOT CALIBRATED',
              'outputs': [{'path': p.relative_to(ROOT).as_posix(), 'bytes': p.stat().st_size,
                           'sha256': hashlib.sha256(p.read_bytes()).hexdigest()} for p in (glb, fbx)],
              'surface_check': 'PASS for tested edge/manifold/finite/area/component checks; self-intersection and deformation NOT TESTED',
              'pz_compatibility': 'NOT TESTED'}
    (ROOT / 'validation/local_cleanup.json').write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8', newline='\n')
    print(json.dumps({'removed_fins': len(deleted), 'triangles': after['triangles'],
                      'welded_nonmanifold_edges': after['welded_nonmanifold_edges'], 'bounds_delta': delta}))


if __name__ == '__main__':
    main()
