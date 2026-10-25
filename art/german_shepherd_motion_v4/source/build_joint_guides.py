"""Create a new editable guide scene from the corrected, linked forward-head rig."""
from pathlib import Path
import sys,bpy
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'art/german_shepherd_motion_v2/source'))
sys.path.insert(0,str(ROOT/'art/german_shepherd_motion_v3/source'))
import anatomy as fit
from head_rig import ATLAS,NECK_BASE,HEAD_FORWARD
OUT=Path(__file__).parent/'shepherd_joint_guides.blend'
assert not OUT.exists(),'Preserve user joint work; do not replace an existing scene'
bpy.ops.wm.open_mainfile(filepath=str(Path(__file__).parent/'shepherd_head_controls.blend'))
mesh=next(o for o in bpy.context.scene.objects if o.type=='MESH')
bpy.context.view_layer.update();placement=mesh.matrix_world.copy()
for obj in bpy.context.scene.objects:
    if obj!=mesh:obj.hide_set(True)
mesh.hide_select=True;mesh.lock_location=(True,)*3;mesh.lock_rotation=(True,)*3;mesh.lock_scale=(True,)*3
arm=bpy.data.armatures.new('Dogmeat_Editable_Joint_Guides')
rig=bpy.data.objects.new('EDIT THESE JOINT GUIDES',arm);bpy.context.scene.collection.objects.link(rig)
rig.matrix_world=placement;rig.show_in_front=True;arm.display_type='OCTAHEDRAL';arm.show_names=True
bpy.context.view_layer.objects.active=rig;rig.select_set(True)
bpy.ops.object.mode_set(mode='EDIT')
def bone(name,a,b,parent=None,connected=False):
    result=arm.edit_bones.new(name);result.head=a;result.tail=b;result.use_deform=False
    if parent:result.parent=parent;result.use_connect=connected
    return result
spine=bone('Body_Axis',(.42,.28,.08),(-.49,.035,.19))
neck=bone('Neck_Base_to_Atlas',NECK_BASE,ATLAS,spine,True)
bone('Head_Forward',ATLAS,Vector(ATLAS)-Vector(fit.BACK)*.27,neck,True)
for (side,part),(a,b,c,paw) in fit.LIMBS.items():
    if part=='rear':
        b=Vector(b)-Vector(fit.BACK)*.04;c=Vector(c)-Vector(fit.BACK)*.04
    labels=['Shoulder_Elbow','Elbow_Wrist','Wrist_Paw','Front_Toes'] if part=='front' else ['Hip_Stifle','Stifle_Hock','Hock_Paw','Rear_Toes']
    points=[a,b,c,paw,Vector(paw)-Vector(fit.BACK)*.065]
    parent=None
    for i,label in enumerate(labels):parent=bone(side+'_'+label,points[i],points[i+1],parent,i>0)
parent=None
for i,(a,b) in enumerate(zip(fit.TAIL,fit.TAIL[1:])):parent=bone('Tail_'+str(i+1),a,b,parent,i>0)
for b in arm.edit_bones:b.select=b.select_head=b.select_tail=False
active=arm.edit_bones['L_Stifle_Hock'];active.select=active.select_head=active.select_tail=True;arm.edit_bones.active=active
bpy.ops.object.mode_set(mode='OBJECT')
rig['purpose']='Nondeforming authoring guides. Mesh, UVs and native export skeleton remain unchanged. Save after moving joints; Codex can read these coordinates for fitting.'
rig['authoring_space']='Mesh local coordinates; rigid object placement retained from the verified v3 source'
text=bpy.data.texts.new('READ ME - Joint Positioning')
text.write('DOGMEAT MANUAL JOINT FITTING\n\nThe mesh uses frozen v3 skin and corrected forward head. This guide rig does not deform it. Rear stifle/hock guides are 0.04 units forward of v3.\nSelect EDIT THESE JOINT GUIDES, press Tab for Edit Mode.\nClick a bone endpoint (joint); press G to move. Use X/Y/Z to constrain.\nNumpad 1/3/7: front/side/top; Numpad 5 toggles perspective.\nCtrl+S saves your joint locations. Tell Codex when finished.\nDo not edit the linked source model.\nThese are authoring landmarks, not modifications to the native raccoon bind.\n')
center=placement@Vector((.08,.18,-.05));direction=placement.to_3x3()@(Vector(fit.SIDE)*4+Vector(fit.BACK)*.5+Vector((0,0,1))*.8)
for screen in bpy.data.screens:
    for area in screen.areas:
        if area.type=='VIEW_3D':
            space=area.spaces.active;space.shading.type='MATERIAL';space.overlay.show_floor=False
            view=space.region_3d;view.view_location=center;view.view_distance=.72;view.view_perspective='ORTHO'
            view.view_rotation=(-direction).to_track_quat('-Z','Y')
scene=bpy.context.scene;scene.unit_settings.system='METRIC';scene['source_checkpoint']='Frozen v3 skins, v4 forward-head pose and forward rear-joint guides'
bpy.context.preferences.filepaths.save_version=1
for library in bpy.data.libraries:library.filepath=bpy.path.relpath(library.filepath,start=str(OUT.parent))
bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.wm.save_as_mainfile(filepath=str(OUT),compress=True,relative_remap=False)
print('MANUAL_JOINT_EDITOR_READY',str(OUT),flush=True)
