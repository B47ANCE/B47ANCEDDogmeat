"""Compare native bind offsets, exact Blender geometry/UV retention and GLB geometry."""
import argparse,hashlib,importlib.util,json,struct,sys
from pathlib import Path
import bpy,numpy as np
from mathutils import Matrix,Quaternion,Vector
HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('builder',HERE/'build_native.py');b=importlib.util.module_from_spec(spec);spec.loader.exec_module(b)
parser=argparse.ArgumentParser();parser.add_argument('--game-root',type=Path,required=True);args=parser.parse_args(sys.argv[sys.argv.index('--')+1:])
sys.path.insert(0,str(HERE))
bones,bind,offsets,native_hash,idle_hash=b.playback_contract(args.game_root)
bpy.ops.wm.open_mainfile(filepath=str(HERE/'shepherd_native.blend'))
rig=next(o for o in bpy.data.objects if o.type=='ARMATURE');objects={o.name:o for o in bpy.data.objects if o.type=='MESH'}
hierarchy={x.name:x.parent.name if x.parent else None for x in rig.data.bones}
assert hierarchy=={x['name']:x['parent'] for x in bones}
placement=next(iter(objects.values())).matrix_world.copy();P=placement.inverted()@b.C@b.H
report={'asset_revision':'gsd-native-rig-v001','project_version':(b.ROOT/'VERSION').read_text().strip(),
 'environment':'Blender '+bpy.app.version_string+' offline; no PZ execution','native_source_sha256':native_hash,'idle_bind_source_sha256':idle_hash,'bind_reference':'Rac_Idle01 frame zero',
 'hierarchy_names_and_parents_match':True,'bone_nodes':34,'deforming_bones':25,
 'helper_bones':'Nine zero-weight hierarchy helpers; not native anatomical bind positions',
 'native_to_authoring':[list(row) for row in P],'mesh_object_transform':[list(row) for row in placement],
 'alignment_scale':float(P.to_scale().length/(3**.5)),'variants':{},'runtime':'NOT TESTED'}

def glb(path):
 raw=path.read_bytes();length=struct.unpack_from('<I',raw,12)[0];doc=json.loads(raw[20:20+length]);binary=raw[28+length:]
 def accessor(aid):
  a=doc['accessors'][aid];v=doc['bufferViews'][a['bufferView']];width={'SCALAR':1,'VEC2':2,'VEC3':3,'VEC4':4,'MAT4':16}[a['type']];dtype={5121:'u1',5123:'<u2',5125:'<u4',5126:'<f4'}[a['componentType']]
  assert 'byteStride' not in v
  return np.frombuffer(binary,dtype=dtype,count=a['count']*width,offset=v.get('byteOffset',0)+a.get('byteOffset',0)).reshape(-1,width)
 return doc,accessor

for name,suffix in [('original','Original'),('variation_1','Coat1'),('variation_2','Coat2')]:
 obj=objects['B47Dogmeat_GSD_'+suffix];mesh=obj.data;before=b.mesh_hash(mesh)
 # Read input separately; do not modify either mesh datablock.
 known=set(bpy.data.objects)
 if name=='original':bpy.ops.import_scene.gltf(filepath=str(b.INPUT/'original/selected_shepherd.glb'))
 else:bpy.ops.import_scene.fbx(filepath=str(b.INPUT/'coats'/name/'supplied.fbx'))
 source=next(o for o in bpy.data.objects if o not in known and o.type=='MESH')
 assert b.mesh_hash(source.data)==before,'Geometry/UV change: '+name
 for added in list(bpy.data.objects):
  if added not in known:bpy.data.objects.remove(added,do_unlink=True)
 doc,accessor=glb(b.OUT/'models'/(obj.name+'.glb'));skin=doc['skins'][0]
 assert not doc.get('animations') and len(skin['joints'])==25
 joint_names=[doc['nodes'][i]['name'] for i in skin['joints']];assert set(joint_names)==set(offsets)
 ibms=accessor(skin['inverseBindMatrices']).reshape(-1,4,4).transpose(0,2,1)
 max_bind=max(float(np.max(abs(ibms[i]-np.array(b.H@offsets[n]@b.H)))) for i,n in enumerate(joint_names))
 assert max_bind<3e-5,('Native bind mismatch',name,max_bind)
 parents={child:i for i,node in enumerate(doc['nodes']) for child in node.get('children',[])};world={}
 def global_matrix(index):
  if index not in world:
   node=doc['nodes'][index]
   if 'matrix' in node:local=Matrix(np.array(node['matrix']).reshape(4,4).T.tolist())
   else:
    q=node.get('rotation',[0,0,0,1]);local=Matrix.LocRotScale(Vector(node.get('translation',[0,0,0])),Quaternion((q[3],q[0],q[1],q[2])),Vector(node.get('scale',[1,1,1])))
   world[index]=global_matrix(parents[index])@local if index in parents else local
  return world[index]
 max_joint=max(float(np.max(abs(np.array(global_matrix(node))-np.array(b.H@bind[n]@b.H)))) for node,n in zip(skin['joints'],joint_names))
 assert max_joint<3e-5,('Native joint mismatch',name,max_joint)
 primitive=doc['meshes'][0]['primitives'][0];indices=accessor(primitive['indices']).ravel();positions=accessor(primitive['attributes']['POSITION'])
 transform=np.array(P@b.H);restored=positions@transform[:3,:3].T+transform[:3,3]
 co=b.array(mesh.vertices,'co',3,np.float32);loops=b.array(mesh.loops,'vertex_index',1,np.int32).ravel()
 assert len(indices)==len(loops)
 max_position=float(np.max(abs(restored[indices]-co[loops])))
 uv=accessor(primitive['attributes']['TEXCOORD_0']).copy();uv[:,1]=1-uv[:,1]
 uv_error=float(np.max(abs(uv[indices]-b.array(mesh.uv_layers.active.data,'uv',2,np.float32))))
 assert max_position<3e-5 and uv_error<2e-7,('Export geometry/UV mismatch',name,max_position,uv_error)
 weights=accessor(primitive['attributes']['WEIGHTS_0']);joints=accessor(primitive['attributes']['JOINTS_0'])
 assert np.all(joints<25) and np.all(np.sum(weights>0,axis=1)<=4) and np.all(weights>=0)
 weight_error=float(np.max(abs(weights.sum(axis=1)-1)));assert weight_error<2e-6
 normals=accessor(primitive['attributes']['NORMAL']);tris=positions[indices].reshape(-1,3,3)
 crosses=np.cross(tris[:,1]-tris[:,0],tris[:,2]-tris[:,0]);normal=normals[indices].reshape(-1,3,3).mean(axis=1)
 dot=np.einsum('ij,ij->i',crosses,normal);nonzero=np.linalg.norm(crosses,axis=1)>1e-12
 winding=float(np.mean(dot[nonzero]>0));assert winding>.98,('Export winding inconsistent',winding)
 report['variants'][name]={'model':obj.name,'source_vertices':len(mesh.vertices),'source_triangles':len(mesh.polygons),
  'geometry_uv_source_sha256':before,'geometry_uv_bound_sha256':b.mesh_hash(mesh),'unchanged_source_geometry_uv':True,
  'glb_position_max_error_after_inverse_alignment':max_position,'glb_uv_max_error':uv_error,
  'native_inverse_bind_max_error':max_bind,'native_joint_global_max_error':max_joint,'positive_winding_fraction':winding,
  'max_influences':int(np.sum(weights>0,axis=1).max()),'unweighted_vertices':int(np.count_nonzero(weights.sum(axis=1)==0)),
  'max_weight_sum_error':weight_error,'glb_sha256':hashlib.sha256((b.OUT/'models'/(obj.name+'.glb')).read_bytes()).hexdigest()}
(b.OUT/'validation/native-bind.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8',newline='\n')
print('NATIVE_BIND_VALIDATION',json.dumps(report))
