"""Reopen and independently validate the saved atlas control; no asset writes."""
from pathlib import Path
import bpy,numpy as np,json,hashlib,math
from mathutils import Matrix,Vector
ROOT=Path(__file__).resolve().parents[3];HERE=Path(__file__).resolve().parents[1]/'validation';path=Path(__file__).resolve().parent/'shepherd_head_controls.blend'
bpy.ops.wm.open_mainfile(filepath=str(path));rig=next(o for o in bpy.context.scene.objects if o.type=='ARMATURE');mesh=next(o for o in bpy.context.scene.objects if o.type=='MESH');control=bpy.data.objects['GSD_Head_Control']
assert len(rig.data.bones)==34;assert all('Control'not in b.name for b in rig.data.bones)
assert len([c for c in rig.pose.bones['Bip01_Head'].constraints if c.type=='COPY_TRANSFORMS'])==1
assert control.rotation_mode=='XYZ';assert np.max(np.abs(np.array(control.matrix_basis)-np.eye(4)))<1e-7
assert mesh.data.library is not None;assert any(m.type=='ARMATURE'and m.object==rig for m in mesh.modifiers)
source=np.empty(len(mesh.data.vertices)*3,np.float32);mesh.data.vertices.foreach_get('co',source)
positions_hash=hashlib.sha256(source.astype('<f4').tobytes()).hexdigest();assert positions_hash=='922021f025bf8c04afc86bad63de0e89da9296984a85660f06fdf71766b4cc34'
rest={b.name:b.matrix_local.copy()for b in rig.data.bones};placement=mesh.matrix_world.copy();atlas=Vector((-.745,.015,.435));pitchaxis=Vector((.25296,-.96748,0)).normalized();up=Vector((0,0,1))
def around(p,angle,axis):return Matrix.Translation(p)@Matrix.Rotation(math.radians(angle),4,axis)@Matrix.Translation(-p)
def err(a,b):return max(abs(a[r][c]-b[r][c])for r in range(4)for c in range(4))
results=[]
for yaw,pitch in [(0,0),(-25,0),(25,0),(0,-15),(0,15),(25,12),(-25,-12),(0,0)]:
 control.matrix_basis=Matrix.Rotation(math.radians(yaw),4,'Z')@Matrix.Rotation(math.radians(pitch),4,'X');bpy.context.view_layer.update()
 D=around(atlas,yaw,up)@around(atlas,pitch,pitchaxis)@around(atlas,-70.04851073581948,up);worldD=placement@D@placement.inverted()
 expected=worldD@rig.matrix_world@rest['Bip01_Head'];actual=rig.matrix_world@rig.pose.bones['Bip01_Head'].matrix
 headerror=err(actual,expected);neckerror=err(rig.pose.bones['Bip01_Neck'].matrix,placement@around(atlas,-35+.5*yaw,up)@placement.inverted()@rest['Bip01_Neck'])
 nuberror=err(rig.matrix_world@rig.pose.bones['Bip01_HeadNub'].matrix,worldD@rig.matrix_world@rest['Bip01_HeadNub'])
 print('CONTROL_DIAGNOSTIC',yaw,pitch,'errors',headerror,neckerror,nuberror,flush=True)
 results.append({'yaw':yaw,'pitch':pitch,'head_expected_source_pivot_error':headerror,'neck_expected_shared_yaw_error':neckerror,'head_nub_follow_error':nuberror})
for b in rig.data.bones:assert err(b.matrix_local,rest[b.name])==0
report={'project_version':(ROOT/'VERSION').read_text(encoding='utf-8').strip(),'audit_source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'evidence':'Blender 4.5.3 offline, reopened saved linked control scene, independently composed author-space atlas rotations','runtime':'NOT TESTED','blend_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'control':control.name,'linked_mesh_source':mesh.data.library.filepath,'source_position_sha256':positions_hash,'bones':34,'helper_bones_added':0,'native_rest_matrices_unchanged':True,'mesh_armature_modifier_targets_local_rig':True,'samples':results,'zero_return_error':results[-1]['head_expected_source_pivot_error']}
maximum=max(max(c['head_expected_source_pivot_error'],c['neck_expected_shared_yaw_error'],c['head_nub_follow_error'])for c in results)
report['max_error']=maximum;report['status']='PASS - reopened independent atlas control' if maximum<2e-6 else 'FAIL - controller does not rotate around the supplied author-space atlas'
(HERE/'reopened-head-controls-audit.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8',newline='\n');print('REOPENED_HEAD_CONTROLS',json.dumps(report),flush=True)
assert maximum<2e-6,report['status']
