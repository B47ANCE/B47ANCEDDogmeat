"""Read-only evaluated lip/lining/tongue self intersections and neutral rays."""
import bpy,json,importlib.util,collections,hashlib
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
root=Path(__file__).resolve().parents[1];repo=root.parents[1];p=root/'source/build_anatomy.py'
s=importlib.util.spec_from_file_location('builder',p);mod=importlib.util.module_from_spec(s);s.loader.exec_module(mod)
blend=p.parent/'english_mastiff_anatomy_tests.blend';bpy.ops.wm.open_mainfile(filepath=str(blend))
rig=bpy.data.objects['DM_AnatomyTestRig'];rig.animation_data.action=None;rig.animation_data.use_nla=False
zeros=[]
for o in bpy.context.scene.objects:
 if o.type!='MESH':continue
 m=o.data;m.calc_loop_triangles()
 for t in m.loop_triangles:
  vs=[m.vertices[k].co for k in t.vertices];a=(vs[1]-vs[0]).cross(vs[2]-vs[0]).length
  if a<1e-12:zeros.append({'name':o.name,'tri':list(t.vertices),'poly':t.polygon_index,'material':m.polygons[t.polygon_index].material_index,'cross_length':a,'world_coords':[list(v)for v in vs]})
rows=[]
for ang,mode in [(0,'rest'),(5,'rest'),(15,'rest'),(30,'rest'),(45,'rest'),(30,'extend'),(30,'curl'),(15,'retract')]:
 mod.set_pose(rig,ang,mode)
 for n in ['DM_CoatAndUpperHead','DM_Mandible','DM_Tongue']:
  o=bpy.data.objects[n];ev=o.evaluated_get(bpy.context.evaluated_depsgraph_get());m=ev.to_mesh();m.calc_loop_triangles();vs=[o.matrix_world@v.co for v in m.vertices];tris=[t for t in m.loop_triangles if n=='DM_Tongue'or m.polygons[t.polygon_index].material_index in(1,2)];fs=[tuple(t.vertices)for t in tris];tr=BVHTree.FromPolygons(vs,fs,all_triangles=True,epsilon=0)
  pairs=[(a,b)for a,b in tr.overlap(tr)if a<b and not set(fs[a])&set(fs[b])];counts=collections.Counter();examples=[]
  for a,b in pairs:
   mats=tuple(sorted((m.polygons[tris[a].polygon_index].material_index,m.polygons[tris[b].polygon_index].material_index)));counts[str(mats)]+=1
   if len(examples)<2:examples.append({'material_pair':mats,'triangles':[fs[a],fs[b]],'source_mouth_a':[list(mod.mouth_point(o.data.vertices[k].co))for k in fs[a]],'source_mouth_b':[list(mod.mouth_point(o.data.vertices[k].co))for k in fs[b]]})
  rows.append({'angle':ang,'mode':mode,'part':n,'oral_including_lip_nonadjacent_self_pairs':len(pairs),'pairs_by_material':dict(counts),'examples':examples});ev.to_mesh_clear()
mod.set_pose(rig);deps=bpy.context.evaluated_depsgraph_get();visibility=[]
for camera,pos in {'oblique':Vector((.9,-2,1.2)),'global_front':Vector((0,-2,1.04)),'mouth_front':mod.world_point((0,-2,1.04))}.items():
 visible=[]
 for o in bpy.context.scene.objects:
  if o.type!='MESH'or not(o.name.startswith('DM_Tooth_')or o.name in['DM_Tongue','DM_Gums_Upper','DM_Gums_Lower']):continue
  ev=o.evaluated_get(deps);m=ev.to_mesh();m.calc_loop_triangles();count=0
  for tri in m.loop_triangles:
   point=o.matrix_world@sum((m.vertices[k].co for k in tri.vertices),Vector())/3;res=bpy.context.scene.ray_cast(deps,pos,(point-pos).normalized(),distance=(point-pos).length+.001)
   if res[0]and res[4].name==o.name:count+=1
  if count:visible.append({'name':o.name,'visible_triangle_centroids':count})
  ev.to_mesh_clear()
 visibility.append({'camera':camera,'oral_visible':visible})
out={'blend':blend.relative_to(root).as_posix(),'blend_sha256':hashlib.sha256(blend.read_bytes()).hexdigest(),'blender':bpy.app.version_string,'facial_acceptance':'HOLD' if any(r['oral_including_lip_nonadjacent_self_pairs'] for r in rows) else 'Sampled checks only; visual/native acceptance separate','zeros':zeros,'self_checks':rows,'neutral_visibility':visibility,'scope':'Lining1/lip2/tongue evaluated surface self-intersections; shared vertex indices excluded; epsilon0. Original coat excluded. Neutral camera-to-triangle-centroid visibility samples are not exhaustive. Surface tests do not prove containment or minimum clearance.'}
path=root/'validation/deformation.json';path.write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8',newline='\n')
print(json.dumps({'report':str(path),'facial_acceptance':out['facial_acceptance'],'zero_triangle_count':len(zeros),'self':[{'angle':r['angle'],'mode':r['mode'],'part':r['part'],'pairs':r['oral_including_lip_nonadjacent_self_pairs']}for r in rows],'neutral':visibility}))
