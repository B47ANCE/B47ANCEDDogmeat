"""Small editable head-control scene linked to the immutable geometry source.

The Empty and constraint are authoring helpers only, never exported to the game.
Rotate GSD_Head_Control local Z for yaw and local X for pitch. Zero is bind pose.
"""
from pathlib import Path
import bpy,json,math,sys
from mathutils import Matrix,Vector
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from head_rig import ATLAS,HEAD_PITCH,HEAD_FORWARD

def main():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    source=HERE/'shepherd_reweighted.blend'
    with bpy.data.libraries.load(str(source),link=True) as (available,selected):
        selected.objects=['B47Dogmeat_NativeRaccoonRig','B47Dogmeat_GSD_Coat2']
    objects=[]
    for linked in selected.objects:
        obj=linked.copy();bpy.context.scene.collection.objects.link(obj);objects.append(obj)
    rig=next(o for o in objects if o.type=='ARMATURE');mesh=next(o for o in objects if o.type=='MESH')
    rig.animation_data_clear();rig.show_in_front=True
    for bone in rig.pose.bones:
        bone.matrix_basis=Matrix.Identity(4)
        for constraint in list(bone.constraints):bone.constraints.remove(constraint)
    for modifier in mesh.modifiers:
        if modifier.type=='ARMATURE':modifier.object=rig
    if mesh.parent:mesh.parent=rig
    # Linked object copies initially expose stale world matrices. Evaluate the
    # actual mesh placement before fitting a source-space atlas control.
    bpy.context.view_layer.update()
    axes=Matrix((HEAD_PITCH,tuple(-x for x in HEAD_FORWARD),(0,0,1))).transposed()
    orientation=mesh.matrix_world.to_quaternion().to_matrix()@axes
    space=bpy.data.objects.new('GSD_Head_Space',None);bpy.context.scene.collection.objects.link(space)
    space.matrix_world=Matrix.LocRotScale(mesh.matrix_world@Vector(ATLAS),orientation.to_quaternion(),Vector((1,1,1)))
    space.empty_display_size=.01;space.hide_select=True
    control=bpy.data.objects.new('GSD_Head_Control',None);bpy.context.scene.collection.objects.link(control)
    control.empty_display_type='CIRCLE';control.empty_display_size=.07
    control.parent=space;control.matrix_basis=Matrix.Identity(4)
    bpy.context.view_layer.update()
    atlas_world=mesh.matrix_world@Vector(ATLAS)
    assert (control.matrix_world.translation-atlas_world).length<1e-7
    control.rotation_mode='XYZ';control.lock_location=(True,True,True);control.lock_scale=(True,True,True)
    control['instructions']='Rotate local Z (yaw) or local X (pitch). Tested independent limits: yaw +/-25 degrees; pitch +/-15 degrees. Helpers are not runtime bones.'
    target=bpy.data.objects.new('GSD_Head_Target',None);bpy.context.scene.collection.objects.link(target)
    target.empty_display_type='PLAIN_AXES';target.empty_display_size=.015;target.hide_select=True
    target.parent=control;target.matrix_parent_inverse=control.matrix_world.inverted()
    target.matrix_basis=rig.matrix_world@rig.data.bones['Bip01_Head'].matrix_local
    constraint=rig.pose.bones['Bip01_Head'].constraints.new('COPY_TRANSFORMS')
    constraint.name='AuthoringAtlasControl';constraint.target=target;constraint.target_space='WORLD';constraint.owner_space='WORLD'
    bpy.context.view_layer.update()
    rest=rig.data.bones['Bip01_Head'].matrix_local
    error=max(abs(rig.pose.bones['Bip01_Head'].matrix[r][c]-rest[r][c]) for r in range(4) for c in range(4))
    assert error<2e-6,error
    baseline=control.matrix_basis.copy();samples=[]
    for axis,angle in [('Z',-25),('Z',25),('X',-15),('X',15)]:
        control.matrix_basis=baseline@Matrix.Rotation(math.radians(angle),4,axis)
        bpy.context.view_layer.update()
        expected=control.matrix_world@target.matrix_parent_inverse@target.matrix_basis
        actual=rig.matrix_world@rig.pose.bones['Bip01_Head'].matrix
        difference=max(abs(actual[r][c]-expected[r][c]) for r in range(4) for c in range(4))
        assert difference<2e-6,difference
        samples.append({'local_axis':axis,'degrees':angle,'head_world_matrix_error':difference})
    control.matrix_basis=baseline;bpy.context.view_layer.update()
    for obj in bpy.context.selected_objects:obj.select_set(False)
    control.select_set(True);bpy.context.view_layer.objects.active=control
    scene=bpy.context.scene;scene['scope']='Editable linked head rig only; native skeleton, geometry and UVs unchanged. No game acceptance.'
    scene['controls']='GSD_Head_Control: local Z yaw, local X pitch; use quaternion/local-axis transforms around supplied atlas.'
    scene.unit_settings.system='METRIC'
    scene.transform_orientation_slots[0].type='LOCAL'
    for screen in bpy.data.screens:
        for area in screen.areas:
            if area.type=='VIEW_3D':
                area.spaces.active.region_3d.view_distance=1.2
                area.spaces.active.region_3d.view_location=mesh.matrix_world@Vector((-.25,0,.1))
                area.spaces.active.shading.type='MATERIAL'
    bpy.context.preferences.filepaths.save_version=0
    bpy.ops.wm.save_as_mainfile(filepath=str(HERE/'shepherd_head_controls.blend'),compress=True,relative_remap=True)
    for library in bpy.data.libraries:library.filepath=bpy.path.relpath(library.filepath)
    bpy.ops.wm.save_as_mainfile(filepath=str(HERE/'shepherd_head_controls.blend'),compress=True)
    (HERE.parent/'validation/head-controls.json').write_text(json.dumps({'environment':'Blender '+bpy.app.version_string+' offline',
        'runtime':'NOT TESTED','bind_head_matrix_error':error,'samples':samples,
        'linked_source':'shepherd_reweighted.blend','exported_control_bones':0},indent=2)+'\n',encoding='utf-8',newline='\n')
    print('HEAD_CONTROLS_PASS',flush=True)

if __name__=='__main__':main()
