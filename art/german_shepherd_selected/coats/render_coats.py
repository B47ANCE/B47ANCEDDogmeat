"""Render supplied coat FBXs with exact supplied maps; never save/edit their meshes."""
import bpy
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
for name in ['variation_1','variation_2']:
    bpy.ops.wm.open_mainfile(filepath=str(ROOT/'source/selected_shepherd_rigged.blend'))
    for obj in list(bpy.data.objects):
        if obj.type in {'MESH','ARMATURE'}:bpy.data.objects.remove(obj,do_unlink=True)
    bpy.ops.import_scene.fbx(filepath=str(ROOT/'coats'/name/'supplied.fbx'))
    obj=next(o for o in bpy.data.objects if o.type=='MESH')
    # Preview material only. Do not save this scene or alter original FBX/materials.
    material=bpy.data.materials.new(name+'_Review');material.use_nodes=True
    nodes=material.node_tree.nodes;links=material.node_tree.links
    shader=next(n for n in nodes if n.type=='BSDF_PRINCIPLED')
    for role,socket in [('base_color','Base Color'),('roughness','Roughness'),('metallic','Metallic'),('normal','Normal')]:
        tex=nodes.new('ShaderNodeTexImage');tex.image=bpy.data.images.load(str(ROOT/'coats'/name/(role+'.png')),check_existing=False)
        if role!='base_color':tex.image.colorspace_settings.name='Non-Color'
        output=tex.outputs['Color']
        if role=='normal':
            normal=nodes.new('ShaderNodeNormalMap');links.new(output,normal.inputs['Color']);output=normal.outputs['Normal']
        links.new(output,shader.inputs[socket])
    obj.data.materials.clear();obj.data.materials.append(material)
    bpy.context.scene.render.filepath=str(ROOT/'coats'/name/'preview.png')
    bpy.ops.render.render(write_still=True)
