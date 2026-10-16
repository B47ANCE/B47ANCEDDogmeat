import bpy
import bmesh
import collections, hashlib, json, math, re, sys, shutil
from pathlib import Path
from mathutils import Vector
from mathutils.kdtree import KDTree
ROOT=Path(__file__).resolve().parents[1]
REPO=ROOT.parents[1]
PRIVATE=REPO/'.m0r-local/english-mastiff-plan'
LIFT=.6689440608
BASE=REPO/'art/english_mastiff/interchange/english_mastiff.glb'
EXPECTED_BASE='37c8e1cc6e47f9ffde22aa93346e8d91f15fb4c3d90843e4cb278e2aab07bd31'

def load(path):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    if path.suffix=='.blend':bpy.ops.wm.open_mainfile(filepath=str(path))
    elif path.suffix=='.fbx':
        private_path=PRIVATE/'fbx-import'/path.name
        private_path.parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(path,private_path)
        bpy.ops.import_scene.fbx(filepath=str(private_path))
    else:bpy.ops.import_scene.gltf(filepath=str(path))
    return sorted([o for o in bpy.context.scene.objects if o.type=='MESH' and o.name.startswith('DM_')],key=lambda o:o.name)

def outside(v):return not(v.z>.78 and v.y<-.50)

def corners(o,lift=0):
    layer=o.data.uv_layers.active
    result=[]
    if not layer:return result
    for p in o.data.polygons:
        for li in p.loop_indices:
            co=o.matrix_world@o.data.vertices[o.data.loops[li].vertex_index].co
            co.z+=lift
            if outside(co):result.append((tuple(co),tuple(layer.data[li].uv)))
    return result

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=str(BASE))
base_obj=next(o for o in bpy.context.scene.objects if o.type=='MESH')
base_verts=[tuple((base_obj.matrix_world@v.co)+Vector((0,0,LIFT))) for v in base_obj.data.vertices if outside((base_obj.matrix_world@v.co)+Vector((0,0,LIFT)))]
base_corners=corners(base_obj,LIFT)

def preservation(meshes):
    body=next((o for o in meshes if o.name=='DM_CoatAndUpperHead'),None)
    if not body:return {'error':'No body'}
    points=[body.matrix_world@v.co for v in body.data.vertices]
    kd=KDTree(len(points))
    for i,p in enumerate(points):kd.insert(p,i)
    kd.balance()
    distances=[kd.find(Vector(p))[2] for p in base_verts]
    new_corners=corners(body)
    cornerkd=KDTree(len(new_corners))
    for i,(co,uv) in enumerate(new_corners):cornerkd.insert(Vector(co),i)
    cornerkd.balance()
    failures=[];worst=0
    for co,uv in base_corners:
        matches=cornerkd.find_range(Vector(co),3e-6)
        error=min((math.dist(uv,new_corners[i][1]) for _,i,_ in matches),default=float('inf'))
        worst=max(worst,error)
        if error>3e-6:failures.append({'co':co,'uv':uv,'best_uv_error':error})
    return {'original_vertices_checked':len(base_verts),'max_nearest_position_error':max(distances),'vertices_above_3e6':sum(x>3e-6 for x in distances),'original_uv_corners_checked':len(base_corners),'uv_corners_above_3e6':len(failures),'max_uv_error':worst,'first_uv_failures':failures[:5]}

def stats(path):
    old_hash=hashlib.sha256(path.read_bytes()).hexdigest()
    meshes=load(path)
    output={'sha256':old_hash,'mesh_count':len(meshes),'mesh_names':[o.name for o in meshes]}
    output['teeth']=dict(collections.Counter((re.match(r'DM_Tooth_([UL])_[LR]_([ICPM])\d',o.name).groups() if re.match(r'DM_Tooth_([UL])_[LR]_([ICPM])\d',o.name) else ('?','?')) for o in meshes if o.name.startswith('DM_Tooth_')))
    output['teeth']={f'{a}_{b}':n for (a,b),n in output['teeth'].items()}
    arms=[o for o in bpy.context.scene.objects if o.type=='ARMATURE']
    output['armatures']=[{'name':o.name,'bone_count':len(o.data.bones),'bones':[b.name for b in o.data.bones],'pose_transforms_max':max((max(max(abs(x) for x in p.location),max(abs(x-1) for x in p.scale),p.matrix_basis.to_quaternion().angle) for p in o.pose.bones),default=0)} for o in arms]
    output['mesh_stats']=[]
    for o in meshes:
        d=o.data;d.calc_loop_triangles()
        bm=bmesh.new();bm.from_mesh(d)
        edgecounts={'raw_boundary':sum(e.is_boundary for e in bm.edges)}
        bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-6)
        edgecounts.update({'boundary':sum(e.is_boundary for e in bm.edges),'wire':sum(e.is_wire for e in bm.edges),'nonmanifold':sum(not e.is_manifold for e in bm.edges)})
        bm.free()
        sums=[];maxweights=0;unweighted=0;badgroups=0
        for v in d.vertices:
            gs=[g.weight for g in v.groups if g.weight>1e-7]
            if gs:sums.append(sum(gs));maxweights=max(maxweights,len(gs))
            else:unweighted+=1
        keydata=[{'name':k.name,'value':k.value,'max_displacement':max(((a.co-b.co).length for a,b in zip(k.data,d.shape_keys.key_blocks[0].data)),default=0)} for k in d.shape_keys.key_blocks] if d.shape_keys else []
        arm_mods=[m for m in o.modifiers if m.type=='ARMATURE']
        eval_delta=0
        if arm_mods:
            eo=o.evaluated_get(bpy.context.evaluated_depsgraph_get());em=eo.to_mesh()
            if len(em.vertices)==len(d.vertices):eval_delta=max(((a.co-b.co).length for a,b in zip(em.vertices,d.vertices)),default=0)
            eo.to_mesh_clear()
        output['mesh_stats'].append({'name':o.name,'vertices':len(d.vertices),'triangles':len(d.loop_triangles),'uv_layers':[u.name for u in d.uv_layers],'materials':[m.name if m else None for m in d.materials],**edgecounts,'nonfinite':sum(not all(math.isfinite(c) for c in v.co) for v in d.vertices),'zero_area_triangles':sum(t.area<1e-13 for t in d.loop_triangles),'weights_max':maxweights,'unweighted_vertices':unweighted,'max_weight_sum_error':max((abs(s-1) for s in sums),default=0),'keys':keydata,'rest_evaluated_delta':eval_delta})
    output['triangles']=sum(x['triangles'] for x in output['mesh_stats'])
    output['images']=[{'name':i.name,'size':list(i.size),'packed':bool(i.packed_file),'has_data':i.has_data,'filename':Path(i.filepath).name,'packed_sha256':hashlib.sha256(i.packed_file.data).hexdigest() if i.packed_file else None} for i in bpy.data.images if i.type=='IMAGE']
    output['materials']=[{'name':m.name,'images':[n.image.name for n in m.node_tree.nodes if n.type=='TEX_IMAGE' and n.image] if m.use_nodes else [],'principled':any(n.type=='BSDF_PRINCIPLED' for n in m.node_tree.nodes) if m.use_nodes else False} for m in bpy.data.materials]
    output['outside_head_preservation']=preservation(meshes)
    output['teeth_weight_errors']=[]
    if arms:
        for o in meshes:
            if not o.name.startswith('DM_Tooth_'):continue
            expected='DM_Head' if o.name.startswith('DM_Tooth_U_') else 'DM_Jaw'
            for v in o.data.vertices:
                gs={o.vertex_groups[g.group].name:g.weight for g in v.groups if g.weight>1e-7}
                if gs!={expected:1.0}:
                    output['teeth_weight_errors'].append({'name':o.name,'vertex':v.index,'groups':gs})
                    break
    output['stable_during_inspection']=hashlib.sha256(path.read_bytes()).hexdigest()==old_hash
    return output

report={'environment':bpy.app.version_string,'base_sha256':hashlib.sha256(BASE.read_bytes()).hexdigest(),'base_preserved':hashlib.sha256(BASE.read_bytes()).hexdigest()==EXPECTED_BASE,'files':{}}
paths=[ROOT/'source/english_mastiff_anatomy.blend',ROOT/'source/english_mastiff_anatomy_tests.blend',ROOT/'interchange/english_mastiff_anatomy.glb',ROOT/'interchange/english_mastiff_anatomy.fbx',ROOT/'interchange/english_mastiff_anatomy_tests.glb',ROOT/'interchange/english_mastiff_anatomy_tests.fbx']
for path in paths:
    try:
        report['files'][path.name]=stats(path)
        s=report['files'][path.name]
        print('SCOUT',path.name,'meshes',s['mesh_count'],'triangles',s['triangles'],'bones',[a['bone_count'] for a in s['armatures']],'preserve',s['outside_head_preservation'],'images',[(i['name'],i['packed'],i['has_data']) for i in s['images']],flush=True)
    except Exception as e:
        import traceback
        report['files'][path.name]={'error':str(e),'traceback':traceback.format_exc()}
        print('ERROR',path.name,e,flush=True)
(ROOT/'validation/exports.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8',newline='\n')
