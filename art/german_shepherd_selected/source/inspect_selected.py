"""Read native skeleton as technical data; import supplied mesh without editing it."""
import bpy, json, re, hashlib, argparse, sys
from pathlib import Path
from mathutils import Matrix
import numpy as np

r=Path(__file__).resolve().parents[3]
out=r/'art/german_shepherd_selected'
parser=argparse.ArgumentParser();parser.add_argument('--game-root',type=Path,required=True)
args=parser.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
game=args.game_root
text=(game/'media/models_X/Skinned/Raccoon_Body.x').read_text()
# Brace depth tracks actual Frame nesting while ignoring mesh/template blocks.
tokens=re.finditer(r'\bFrame\s+(\w+)\s*\{|\bFrameTransformMatrix\s*\{([^}]+)\}|[{}]',text)
depth=0;stack=[];bones=[]
for match in tokens:
 value=match.group()
 if value.startswith('Frame '):
  name=match[1];parent=stack[-1][0] if stack else None
  stack.append((name,depth));depth+=1
  if name!='Raccoon':bones.append({'name':name,'parent':parent if parent!='Raccoon' else None})
 elif value.startswith('FrameTransformMatrix'):
  if stack and stack[-1][0]!='Raccoon':
   matrix=[float(x) for x in re.findall(r'[-+]?\d*\.?\d+(?:[eE][-+]?\d+)?',match[2])]
   assert len(matrix)==16;bones[-1]['local_matrix_row_major']=matrix
 elif value=='{':depth+=1
 elif value=='}':
  depth-=1
  while stack and stack[-1][1]==depth:stack.pop()
skin=set(re.findall(r'SkinWeights\s*\{\s*"([^"]+)"',text))
assert skin <= {x['name'] for x in bones}
# Fresh background process only; no user scene is touched.
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=str(out/'original/selected_shepherd.glb'))
meshes=[x for x in bpy.data.objects if x.type=='MESH']
assert len(meshes)==1
obj=meshes[0];obj.name='B47Dogmeat_GermanShepherd'
coords=np.empty(len(obj.data.vertices)*3,dtype=np.float32);obj.data.vertices.foreach_get('co',coords);coords=coords.reshape(-1,3)
matrix=np.array(obj.matrix_world);world=coords[::max(1,len(coords)//10000)]@matrix[:3,:3].T+matrix[:3,3]
C=Matrix(((1,0,0,0),(0,0,-1,0),(0,1,0,0),(0,0,0,1)))
globals={}
for bone in bones:
 local=Matrix(np.array(bone['local_matrix_row_major']).reshape(4,4).T.tolist())
 globals[bone['name']]=(globals[bone['parent']]@local if bone['parent'] else local)
heads={k:list((C@m).translation) for k,m in globals.items()}
report={'blender':bpy.app.version_string,'vertices':len(obj.data.vertices),'polygons':len(obj.data.polygons),'triangles':sum(len(p.vertices)-2 for p in obj.data.polygons),'mesh_object_matrix':[list(row) for row in obj.matrix_world],'local_bounds':[coords.min(axis=0).tolist(),coords.max(axis=0).tolist()],'world_sample_bounds':[world.min(axis=0).tolist(),world.max(axis=0).tolist()],'bone_count':len(bones),'skin_bone_count':len(skin),'heads_blender_space':heads,'bones':bones,'native_source_sha256':hashlib.sha256((game/'media/models_X/Skinned/Raccoon_Body.x').read_bytes()).hexdigest(),'materials':[m.name for m in obj.data.materials],'images':[{'name':i.name,'size':list(i.size)} for i in bpy.data.images]}
(r/'.m0r-local/shepherd-rig').mkdir(parents=True,exist_ok=True)
(r/'.m0r-local/shepherd-rig/inspection.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8',newline='\n')
# Render preview of the untouched imported object; camera/light add no mesh edits.
from mathutils import Vector
mins=world.min(axis=0);maxs=world.max(axis=0);center=Vector(((mins+maxs)/2).tolist());span=float(max(maxs-mins))
scene=bpy.context.scene
scene.world=bpy.data.worlds.new('Neutral');scene.world.use_nodes=True
bg=next(n for n in scene.world.node_tree.nodes if n.type=='BACKGROUND');bg.inputs['Color'].default_value=(.12,.12,.12,1)
for index,(position,power,size) in enumerate([((2,-3,4),900,5),((-3,-1,2),600,4),((1,4,3),800,3)]):
 light=bpy.data.lights.new('Light'+str(index),'AREA');light.energy=power;light.shape='DISK';light.size=size*span
 lo=bpy.data.objects.new(light.name,light);scene.collection.objects.link(lo);lo.location=center+Vector(position)*span;lo.rotation_euler=(center-lo.location).to_track_quat('-Z','Y').to_euler()
cam=bpy.data.cameras.new('ReviewCamera');co=bpy.data.objects.new('ReviewCamera',cam);scene.collection.objects.link(co)
co.location=center+Vector((2.5,-4,1.6))*span;co.rotation_euler=(center-co.location).to_track_quat('-Z','Y').to_euler();cam.type='ORTHO';cam.ortho_scale=span*1.4;scene.camera=co
scene.render.engine='CYCLES';scene.cycles.samples=12;scene.render.resolution_x=900;scene.render.resolution_y=900;scene.render.resolution_percentage=100
scene.render.filepath=str(out/'previews/selected_original.png');bpy.ops.render.render(write_still=True)
print('INSPECTION',json.dumps({k:report[k] for k in ['vertices','triangles','local_bounds','bone_count','skin_bone_count','images']}))
