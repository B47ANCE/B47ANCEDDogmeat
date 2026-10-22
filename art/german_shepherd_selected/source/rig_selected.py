"""Rig-only binding: same native raccoon hierarchy; supplied geometry is immutable."""
import bpy, numpy as np, json, hashlib, math
from pathlib import Path
from mathutils import Matrix, Vector
r=Path(__file__).resolve().parents[3];out=r/'art/german_shepherd_selected'
d=json.loads((r/'.m0r-local/shepherd-rig/inspection.json').read_text())
assert not (out/'source/selected_shepherd_rigged.blend').exists(), 'Existing authored rig is protected; build a new asset revision'
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=str(out/'original/selected_shepherd.glb'))
obj=next(o for o in bpy.data.objects if o.type=='MESH');obj.name='B47Dogmeat_GermanShepherd'
mesh=obj.data

def geometry_hash():
 h=hashlib.sha256()
 for collection,property,width,dtype in [(mesh.vertices,'co',3,np.float32),(mesh.loops,'vertex_index',1,np.int32),(mesh.polygons,'loop_total',1,np.int32)]:
  a=np.empty(len(collection)*width,dtype=dtype);collection.foreach_get(property,a);h.update(a.tobytes())
 for layer in mesh.uv_layers:
  a=np.empty(len(layer.data)*2,dtype=np.float32);layer.data.foreach_get('uv',a);h.update(a.tobytes())
 return h.hexdigest()

original=geometry_hash();coords=np.empty(len(mesh.vertices)*3,dtype=np.float32);mesh.vertices.foreach_get('co',coords);coords=coords.reshape(-1,3)
# Original rigging landmarks only: no vertices, normals, UVs or textures are edited.
heads={'Dummy01':(0,0,0),'Translation_Data':(0,0,0),'Bip01':(.46,0,.1),'Bip01_Pelvis':(.46,0,.1),
       'Bip01_Spine':(.1,0,.13),'Bip01_Neck':(-.4,0,.22),'Bip01_Head':(-.64,0,.43),'Bip01_HeadNub':(-.89,0,.34),
       'Bip01_Tail':(.64,0,.02),'Bip01_Tail1':(.76,0,-.25),'Bip01_Tail2':(.91,0,-.48),'Bip01_TailNub':(.96,0,-.58)}
for side,sign in [('L',1),('R',-1)]:
 for name,point in {'Thigh':(.49,.15,.02),'Calf':(.55,.18,-.28),'Foot':(.67,.19,-.6),'Toe0':(.56,.2,-.77),'Toe0Nub':(.43,.2,-.77),
                    'Clavicle':(-.35,.15,.16),'UpperArm':(-.4,.17,-.13),'Forearm':(-.45,.18,-.44),'Hand':(-.49,.19,-.73),'Finger0':(-.57,.19,-.79),'Finger0Nub':(-.66,.19,-.79)}.items():
  heads[f'Bip01_{side}_{name}']=(point[0],point[1]*sign,point[2])
assert set(heads)=={b['name'] for b in d['bones']}
arm=bpy.data.armatures.new('B47Dogmeat_RaccoonRig');rig=bpy.data.objects.new('B47Dogmeat_RaccoonRig',arm);bpy.context.collection.objects.link(rig)
bpy.context.view_layer.objects.active=rig;rig.select_set(True);obj.select_set(False);bpy.ops.object.mode_set(mode='EDIT')
# Keep native orientation axes while fitting only joint locations to the new animal.
C=Matrix(((1,0,0,0),(0,0,-1,0),(0,1,0,0),(0,0,0,1)))
R=Matrix.Rotation(math.pi/2,4,'Z');Q=Matrix.Rotation(-math.pi/2,4,'Z');globals={}
for spec in d['bones']:
 name=spec['name'];local=Matrix(np.array(spec['local_matrix_row_major']).reshape(4,4).T.tolist())
 globals[name]=globals[spec['parent']]@local if spec['parent'] else local
 eb=arm.edit_bones.new(name);basis=R@C@globals[name]@Q;basis.translation=Vector(heads[name]);eb.matrix=basis
 children=[b['name'] for b in d['bones'] if b['parent']==name]
 length=(Vector(heads[children[0]])-Vector(heads[name])).length if children else .04
 eb.length=max(length,.025)
 if spec['parent']:eb.parent=arm.edit_bones[spec['parent']]
 eb.use_connect=False
bpy.ops.object.mode_set(mode='OBJECT');rig.show_in_front=True
# Segment guides are weight-paint scaffolding, not mesh geometry or new bones.
ends={'Bip01_Pelvis':(.64,0,.1),'Bip01_Spine':heads['Bip01_Neck'],'Bip01_Neck':heads['Bip01_Head'],'Bip01_Head':heads['Bip01_HeadNub'],
      'Bip01_Tail':heads['Bip01_Tail1'],'Bip01_Tail1':heads['Bip01_Tail2'],'Bip01_Tail2':heads['Bip01_TailNub']}
for side in ['L','R']:
 for chain in [('Thigh','Calf','Foot','Toe0','Toe0Nub'),('Clavicle','UpperArm','Forearm','Hand','Finger0','Finger0Nub')]:
  for a,b in zip(chain,chain[1:]):ends[f'Bip01_{side}_{a}']=heads[f'Bip01_{side}_{b}']
names=list(ends);n=len(coords);best_d=np.full((n,4),1e9,dtype=np.float32);best_i=np.zeros((n,4),dtype=np.int16)
for index,name in enumerate(names):
 a=np.array(heads[name],dtype=np.float32);b=np.array(ends[name],dtype=np.float32);delta=b-a
 t=np.clip(((coords-a)@delta)/max(float(delta@delta),1e-8),0,1)
 distance=np.sum((coords-(a+t[:,None]*delta))**2,axis=1)
 # Prevent one leg binding to its opposite side, preserving a small central blend.
 if '_L_' in name:distance+=np.maximum(-coords[:,1],0)**2*20
 if '_R_' in name:distance+=np.maximum(coords[:,1],0)**2*20
 columns=np.concatenate((best_d,distance[:,None]),axis=1);ids=np.concatenate((best_i,np.full((n,1),index,dtype=np.int16)),axis=1)
 order=np.argsort(columns,axis=1)[:,:4];best_d=np.take_along_axis(columns,order,axis=1);best_i=np.take_along_axis(ids,order,axis=1)
weights=np.exp(-(best_d-best_d[:,0,None])/.012);weights/=weights.sum(axis=1,keepdims=True)
quant=np.rint(weights*255).astype(np.int16);quant[:,0]+=255-quant.sum(axis=1)
# The existing muzzle/tongue/ears follow the raccoon head; no new mouth anatomy.
head=(coords[:,0]<-.58)&(coords[:,2]>.05);best_i[head]=names.index('Bip01_Head');quant[head]=[255,0,0,0]
for index,name in enumerate(names):
 vg=obj.vertex_groups.new(name=name)
 for column in range(4):
  active=(best_i[:,column]==index)&(quant[:,column]>0);indices=np.flatnonzero(active);values=quant[active,column]
  for value in np.unique(values):vg.add(indices[values==value].tolist(),float(value)/255,'REPLACE')
obj.parent=rig;mod=obj.modifiers.new('NativeRaccoonSkin','ARMATURE');mod.object=rig
assert geometry_hash()==original
# All vertices are bound to at most four normalized native influences.
assert np.all(quant.sum(axis=1)==255) and np.all(quant>=0)
for image in bpy.data.images:
 if image.has_data:image.pack()
rig['animation_reference']='Raccoon';rig['native_hierarchy_match']=True;obj['geometry_sha256_before_and_after_rig']=original
obj['user_constraint']='No mesh, UV or texture edits; rig/weights only'
# Neutral review scene. Camera/light objects are excluded from model export.
scene=bpy.context.scene;scene.world=bpy.data.worlds.new('ReviewWorld');scene.world.use_nodes=True
next(x for x in scene.world.node_tree.nodes if x.type=='BACKGROUND').inputs['Color'].default_value=(.14,.14,.14,1)
center=Vector((0,0,0));span=2.0
for index,(location,energy) in enumerate([((3,-4,5),1200),((-3,-2,3),800),((2,4,3),1000)]):
 light=bpy.data.lights.new('ReviewLight'+str(index),'AREA');light.energy=energy;light.size=5
 lo=bpy.data.objects.new(light.name,light);scene.collection.objects.link(lo);lo.location=location;lo.rotation_euler=(center-lo.location).to_track_quat('-Z','Y').to_euler()
cam=bpy.data.cameras.new('ReviewCamera');co=bpy.data.objects.new('ReviewCamera',cam);scene.collection.objects.link(co);co.location=(5,-8,3.2);co.rotation_euler=(center-co.location).to_track_quat('-Z','Y').to_euler();cam.type='ORTHO';cam.ortho_scale=2.65;scene.camera=co
scene.render.engine='CYCLES';scene.cycles.samples=12;scene.render.resolution_x=900;scene.render.resolution_y=900;scene.render.resolution_percentage=100
bpy.ops.wm.save_as_mainfile(filepath=str(out/'source/selected_shepherd_rigged.blend'),compress=True)
for o in bpy.context.selected_objects:o.select_set(False)
obj.select_set(True);rig.select_set(True);bpy.context.view_layer.objects.active=rig
# Export only our dog mesh and new armature. No vanilla meshes or clips are exported.
bpy.ops.export_scene.fbx(filepath=str(out/'rigged/B47Dogmeat_GermanShepherd.fbx'),use_selection=True,object_types={'ARMATURE','MESH'},add_leaf_bones=False,bake_anim=False,axis_forward='-Z',axis_up='Y',path_mode='COPY',embed_textures=False)
report={'asset_revision':'gsd-selected-rig-v001','blender':bpy.app.version_string,'vertices':len(mesh.vertices),'triangles':sum(len(p.vertices)-2 for p in mesh.polygons),'geometry_sha256_before':original,'geometry_sha256_after':geometry_hash(),'geometry_uv_topology_unchanged':True,'bone_count':len(arm.bones),'native_bone_names_and_parents_match':all(arm.bones[b['name']].parent.name==b['parent'] if b['parent'] else arm.bones[b['name']].parent is None for b in d['bones']),'bind_joint_positions':'Fitted to the supplied dog without editing mesh; native names/hierarchy retained','max_vertex_influences':4,'unweighted_vertices':int(np.count_nonzero(quant.sum(axis=1)==0)),'weight_sum_error':float(np.max(np.abs(quant.sum(axis=1)/255-1))),'runtime':'NOT TESTED','native_animations_bundled':False,'native_model_replaced':False}
(out/'validation/rig-validation.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8',newline='\n')
scene.render.filepath=str(out/'previews/rigged_neutral.png');bpy.ops.render.render(write_still=True)
# Independent deformation probe, not a shipped clip or edit to the mesh.
rig.pose.bones['Bip01_Head'].rotation_mode='XYZ';rig.pose.bones['Bip01_Head'].rotation_euler[1]=.12
rig.pose.bones['Bip01_L_Forearm'].rotation_mode='XYZ';rig.pose.bones['Bip01_L_Forearm'].rotation_euler[2]=.12
rig.pose.bones['Bip01_Tail1'].rotation_mode='XYZ';rig.pose.bones['Bip01_Tail1'].rotation_euler[1]=.15
scene.render.filepath=str(out/'previews/rigged_deformation_probe.png');bpy.ops.render.render(write_still=True)
print('RIG_VALIDATION',json.dumps(report))
