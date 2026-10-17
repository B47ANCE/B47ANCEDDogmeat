"""Read-only independent anatomical geometry audit; reports only private output."""
import bpy
import bmesh
import importlib.util
import itertools
import json
import math
from pathlib import Path
from mathutils.bvhtree import BVHTree

root=Path(__file__).resolve().parents[1]
repo=root.parents[1]
spec=importlib.util.spec_from_file_location('anatomy_builder',root/'source/build_anatomy.py')
mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
blend=root/'source/english_mastiff_anatomy_tests.blend'
bpy.ops.wm.open_mainfile(filepath=str(blend))
rig=bpy.data.objects['DM_AnatomyTestRig']
rig.animation_data.action=None
rig.animation_data.use_nla=False
meshes=[o for o in bpy.context.scene.objects if o.type=='MESH']

def surface(obj,material=None):
    ev=obj.evaluated_get(bpy.context.evaluated_depsgraph_get())
    m=ev.to_mesh();m.calc_loop_triangles()
    vertices=[obj.matrix_world@v.co for v in m.vertices]
    faces=[tuple(t.vertices) for t in m.loop_triangles if material is None or m.polygons[t.polygon_index].material_index==material]
    tree=BVHTree.FromPolygons(vertices,faces,all_triangles=True,epsilon=1e-8)
    ev.to_mesh_clear()
    return vertices,faces,tree

struct=[]
for o in meshes:
    m=o.data;m.calc_loop_triangles();bm=bmesh.new();bm.from_mesh(m)
    row={'name':o.name,'vertices':len(m.vertices),'triangles':len(m.loop_triangles),
         'nonfinite':sum(not math.isfinite(x) for v in m.vertices for x in v.co),
         'zero_area_triangles':sum((m.vertices[t.vertices[1]].co-m.vertices[t.vertices[0]].co).cross(m.vertices[t.vertices[2]].co-m.vertices[t.vertices[0]].co).length<1e-12 for t in m.loop_triangles),
         'boundary_edges':sum(e.is_boundary for e in bm.edges),'nonmanifold_edges':sum(not e.is_manifold for e in bm.edges),
         'uv_layers':len(m.uv_layers)}
    bm.free();struct.append(row)

def collide(a,b):
    matches=a[2].overlap(b[2])
    return len(matches)

cases=[(f'Jaw_{a:02d}',a,'rest') for a in (0,5,15,30,45)]
cases += [('Tongue_Extend',30,'extend'),('Tongue_Curl',30,'curl'),('Tongue_Retract',15,'retract')]
poses=[]
for case,angle,tongue in cases:
    mod.set_pose(rig,angle,tongue)
    surfaces={o.name:surface(o) for o in meshes}
    surfaces['UpperLining']=surface(bpy.data.objects['DM_CoatAndUpperHead'],1)
    surfaces['LowerLining']=surface(bpy.data.objects['DM_Mandible'],1)
    names=list(surfaces)
    teeth=[n for n in names if n.startswith('DM_Tooth_')]
    overlaps=[]
    for a,b in itertools.combinations(teeth,2):
        n=collide(surfaces[a],surfaces[b])
        if n:overlaps.append({'a':a,'b':b,'triangle_pairs':n,'kind':'teeth_cross_arch' if a.split('_')[2]!=b.split('_')[2] else 'teeth_same_arch'})
    for a in teeth:
        for b in ['DM_Tongue','UpperLining','LowerLining']+[n for n in names if n.startswith('DM_PalatalRidge_')]:
            n=collide(surfaces[a],surfaces[b])
            if n:overlaps.append({'a':a,'b':b,'triangle_pairs':n,'kind':'tooth_oral_surface'})
    for b in ['DM_Gums_Upper','DM_Gums_Lower','UpperLining','LowerLining']+[n for n in names if n.startswith('DM_PalatalRidge_')]:
        n=collide(surfaces['DM_Tongue'],surfaces[b])
        if n:overlaps.append({'a':'DM_Tongue','b':b,'triangle_pairs':n,'kind':'tongue_oral_surface'})
    poses.append({'case':case,'angle':angle,'tongue_mode':tongue,'overlaps':overlaps})

import hashlib
out={'blend':blend.relative_to(root).as_posix(),'blend_sha256':hashlib.sha256(blend.read_bytes()).hexdigest(),'blender':bpy.app.version_string,
     'structural':struct,'poses':poses,
     'collision_method':'Evaluated triangle meshes, mathutils.BVHTree overlap epsilon1e-8; detects surface intersections, not full containment or minimum clearance.',
     'excluded':'All original coat surfaces; own gum/tooth root embed pairs. Lining rows reported without automatic root/hinge exemption. Adjacent surfaces and intentional attachments require manual review.'}
output=root/'validation/oral_clearance.json'
output.write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8',newline='\n')
print(json.dumps({'report':str(output),'meshes':len(meshes),'structural_failures':[r for r in struct if r['nonfinite'] or r['zero_area_triangles'] or r['nonmanifold_edges']],
 'poses':[{'case':p['case'],'overlaps':len(p['overlaps']),'pairs':p['overlaps']} for p in poses]}))
