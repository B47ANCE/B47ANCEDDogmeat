"""Reopen own Blender source, export with unchanged embedded textures, and audit FBX."""
from pathlib import Path
import bpy,numpy as np,json,hashlib
r=Path(__file__).resolve().parents[3];out=r/'art/german_shepherd_selected'
bpy.ops.wm.open_mainfile(filepath=str(out/'source/selected_shepherd_rigged.blend'))
obj=next(o for o in bpy.data.objects if o.type=='MESH');rig=next(o for o in bpy.data.objects if o.type=='ARMATURE')
expected={b.name:(b.parent.name if b.parent else None) for b in rig.data.bones}
texture_hashes={i.name:hashlib.sha256(i.packed_file.data).hexdigest() for i in bpy.data.images if i.packed_file}
for o in bpy.context.selected_objects:o.select_set(False)
obj.select_set(True);rig.select_set(True);bpy.context.view_layer.objects.active=rig
path=out/'rigged/B47Dogmeat_GermanShepherd_embedded.fbx'
# Existing export is preserved; validate it again without replacing its bytes.
if not path.exists():
    bpy.ops.export_scene.fbx(filepath=str(path),use_selection=True,object_types={'ARMATURE','MESH'},add_leaf_bones=False,bake_anim=False,axis_forward='-Z',axis_up='Y',path_mode='COPY',embed_textures=True)
source_coords=np.empty(len(obj.data.vertices)*3,dtype=np.float32);obj.data.vertices.foreach_get('co',source_coords)
original_count=len(obj.data.vertices);triangles=sum(len(p.vertices)-2 for p in obj.data.polygons)
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.fbx(filepath=str(path),use_anim=False)
meshes=[o for o in bpy.data.objects if o.type=='MESH'];rigs=[o for o in bpy.data.objects if o.type=='ARMATURE'];assert len(meshes)==1 and len(rigs)==1
obj,rig=meshes[0],rigs[0];actual={b.name:(b.parent.name if b.parent else None) for b in rig.data.bones}
assert actual==expected,{'expected':expected,'actual':actual}
coords=np.empty(len(obj.data.vertices)*3,dtype=np.float32);obj.data.vertices.foreach_get('co',coords)
assert len(coords)==len(source_coords)
# FBX axes are represented by object matrices; compare local coordinates separately.
error=float(np.max(np.abs(coords-source_coords)))
unweighted=0;max_influences=0;max_error=0
for v in obj.data.vertices:
 weights=[g.weight for g in v.groups if g.weight>0]
 if not weights:unweighted+=1
 max_influences=max(max_influences,len(weights));max_error=max(max_error,abs(sum(weights)-1))
images=[]
for i in bpy.data.images:
 raw=i.packed_file.data if i.packed_file else Path(bpy.path.abspath(i.filepath)).read_bytes()
 images.append({'name':i.name,'dimensions':list(i.size),'sha256':hashlib.sha256(raw).hexdigest()})
report={'asset_revision':'gsd-selected-rig-v001','fbx':path.relative_to(r).as_posix(),'bytes':path.stat().st_size,'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'reopened_in':'Blender '+bpy.app.version_string,'mesh_count':len(meshes),'rig_count':len(rigs),'bone_count':len(actual),'bone_names_parents_roundtrip_match':actual==expected,'vertices':len(obj.data.vertices),'triangles':sum(len(p.vertices)-2 for p in obj.data.polygons),'source_vertex_count':original_count,'source_triangles':triangles,'local_position_max_error':error,'unweighted_vertices':unweighted,'max_influences':max_influences,'weight_sum_max_error':max_error,'images':images,'packed_source_image_hashes':texture_hashes,'all_original_texture_bytes_preserved':set(texture_hashes.values())=={i['sha256'] for i in images},'runtime':'NOT TESTED; native playback/axes/scale not proven by FBX roundtrip'}
assert report['triangles']==triangles and unweighted==0 and max_influences<=4 and max_error<1e-5
(out/'validation/fbx-roundtrip.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8',newline='\n')
print('ROUNDTRIP',json.dumps(report))
