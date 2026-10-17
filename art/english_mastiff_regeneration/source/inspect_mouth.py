"""Actual-mesh closeups and section inspection; no generation/rigging/edit of input."""
import json
from pathlib import Path
import sys
import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'source'))
from inspect_english_mastiff import aim

bpy.ops.wm.open_mainfile(filepath=str(ROOT / 'source/english_mastiff_geometry_preview.blend'))
scene = bpy.context.scene
mesh = next(o for o in scene.objects if o.type == 'MESH')
for polygon in mesh.data.polygons:
    polygon.use_smooth = True
material = bpy.data.materials.new('NeutralGeometryReview')
material.use_nodes = True
shader = next(n for n in material.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
shader.inputs['Base Color'].default_value = (.24, .24, .24, 1)
shader.inputs['Roughness'].default_value = .7
mesh.data.materials.clear()
mesh.data.materials.append(material)
report = json.loads((ROOT / 'validation/geometry_preview.json').read_text())
low = Vector(report['source_bounds']['minimum'])
high = Vector(report['source_bounds']['maximum'])
span = high-low
target = Vector((0, low.y+.12*span.y, low.z+.73*span.z))
camera = scene.camera
camera.data.ortho_scale = span.z*.56
folder = ROOT / 'previews/mouth'
folder.mkdir(parents=True, exist_ok=True)
for name, offset in [('front', (0, -3, .1)), ('side', (3, -.2, .1)),
                     ('three_quarter', (2, -3, .1)), ('underside', (0, -3, -1))]:
    camera.location = target+Vector(offset)*max(span)
    aim(camera, target)
    scene.render.filepath = str(folder / (name+'.png'))
    bpy.ops.render.render(write_still=True)
# A section is only a view of the original geometry, not a remeshed deliverable.
# Remove the animal-left half in the isolated review process to expose cavity walls.
import bmesh
bm = bmesh.new()
bm.from_mesh(mesh.data)
bmesh.ops.bisect_plane(bm, geom=list(bm.verts)+list(bm.edges)+list(bm.faces),
                      plane_co=(0, 0, 0), plane_no=(1, 0, 0), clear_outer=True, dist=1e-6)
bm.to_mesh(mesh.data)
bm.free()
camera.location = target+Vector((3, 0, 0))*max(span)
aim(camera, target)
scene.render.filepath = str(folder / 'midline_section.png')
bpy.ops.render.render(write_still=True)
print('Five original-geometry mouth views rendered; input bytes unchanged; no rigging.')
