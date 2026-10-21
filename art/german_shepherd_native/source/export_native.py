"""Complete/recheck exports from the saved neutral rig without replacing it."""
import importlib.util,json,struct
from pathlib import Path
import bpy
HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('build_native',HERE/'build_native.py')
builder=importlib.util.module_from_spec(spec);spec.loader.exec_module(builder)
OUT=builder.OUT
bpy.ops.wm.open_mainfile(filepath=str(HERE/'shepherd_native.blend'))
rig=next(o for o in bpy.data.objects if o.type=='ARMATURE')
objects=[o for o in bpy.data.objects if o.type=='MESH']
for obj in objects:
    for other in bpy.data.objects:other.select_set(False)
    obj.select_set(True);rig.select_set(True);bpy.context.view_layer.objects.active=rig
    path=OUT/'models'/(obj.name+'.glb')
    if not path.exists():
        bpy.ops.export_scene.gltf(filepath=str(path),export_format='GLB',use_selection=True,export_animations=False,export_skins=True,export_rest_position_armature=True,export_def_bones=False,export_materials='EXPORT',export_image_format='AUTO',export_apply=False)
    raw=path.read_bytes();length=struct.unpack_from('<I',raw,12)[0];doc=json.loads(raw[20:20+length])
    if len(doc['skins'][0]['joints'])==34:
        builder.restrict_skin(path,{b.name for b in rig.data.bones if b.use_deform})
    else:assert len(doc['skins'][0]['joints'])==25
    for other in objects:other.hide_render=other!=obj
    bpy.context.scene.render.filepath=str(OUT/'previews'/(obj.name+'_neutral.png'))
    bpy.ops.render.render(write_still=True)
print('EXPORTS COMPLETE; source BLEND unchanged')
