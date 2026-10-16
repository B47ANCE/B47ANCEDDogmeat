"""Render actual original mouth geometry and midline sections; fresh bpy only.

Neutral review material and temporary section cuts are never saved to the
service files or exported as a replacement model.
"""
import hashlib
import json
from pathlib import Path
import sys

import bpy
import bmesh
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'source'))
from inspect_english_mastiff import aim

bpy.ops.wm.open_mainfile(filepath=str(ROOT / 'source/english_mastiff_geometry_preview.blend'))
scene = bpy.context.scene
meshes = [o for o in scene.objects if o.type == 'MESH']
material = bpy.data.materials.new('NeutralGeometryReview')
material.use_nodes = True
shader = next(n for n in material.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
shader.inputs['Base Color'].default_value = (.24, .24, .24, 1)
shader.inputs['Roughness'].default_value = .7
for mesh in meshes:
    mesh.data.materials.clear()
    mesh.data.materials.append(material)
report = json.loads((ROOT / 'validation/geometry_preview.json').read_text())
low = Vector(report['source_bounds']['minimum'])
high = Vector(report['source_bounds']['maximum'])
span = high-low
target = Vector((0, low.y+.12*span.y, low.z+.76*span.z))
camera = scene.camera
camera.data.ortho_scale = span.z*.62
folder = ROOT / 'previews/mouth'
folder.mkdir(parents=True, exist_ok=True)
renders = []


def render(name, offset):
    camera.location = target+Vector(offset)*max(span)
    aim(camera, target)
    path = folder / (name+'.png')
    scene.render.filepath = str(path)
    bpy.ops.render.render(write_still=True)
    renders.append({'path': path.relative_to(ROOT).as_posix(),
                    'sha256': hashlib.sha256(path.read_bytes()).hexdigest()})


for name, offset in [('front', (0, -3, .1)), ('side', (3, -.2, .1)),
                     ('three_quarter', (2, -3, .1)), ('underside', (0, -3, -1))]:
    render(name, offset)
for mesh in meshes:
    bm = bmesh.new()
    bm.from_mesh(mesh.data)
    # Bisect in local space using the world midline; applies to every component.
    inverse = mesh.matrix_world.inverted()
    origin = inverse @ Vector((0, 0, 0))
    normal = mesh.matrix_world.to_3x3().transposed() @ Vector((1, 0, 0))
    bmesh.ops.bisect_plane(bm, geom=list(bm.verts)+list(bm.edges)+list(bm.faces),
                          plane_co=origin, plane_no=normal, clear_outer=True, dist=1e-6)
    bm.to_mesh(mesh.data)
    bm.free()
render('midline_section', (3, 0, 0))
data = {'asset_revision': 'em-v003-preview', 'source_model_sha256': report['sha256'],
        'environment': 'Windows standalone Blender-Python '+bpy.app.version_string+'; not PZ',
        'scope': 'Actual service geometry, neutral review shading, temporary render-only midline cut; no invented anatomy or saved model changes',
        'renders': renders, 'geometry_acceptance': 'REQUIRES VISUAL/COMPONENT ASSESSMENT'}
(ROOT / 'validation/mouth_views.json').write_text(json.dumps(data, indent=2)+'\n', encoding='utf-8', newline='\n')
print('Five actual mouth/section views rendered; original model bytes unchanged.')
