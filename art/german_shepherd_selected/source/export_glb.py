"""Export the rig with original glTF PBR materials; no mesh/material edits."""
import bpy,hashlib,json,struct
from pathlib import Path
r=Path(__file__).resolve().parents[3];out=r/'art/german_shepherd_selected'
bpy.ops.wm.open_mainfile(filepath=str(out/'source/selected_shepherd_rigged.blend'))
for o in bpy.data.objects:o.select_set(o.type in {'MESH','ARMATURE'})
path=out/'rigged/B47Dogmeat_GermanShepherd.glb';assert not path.exists()
bpy.ops.export_scene.gltf(filepath=str(path),export_format='GLB',use_selection=True,export_animations=False,export_skins=True,export_texcoords=True,export_normals=True,export_materials='EXPORT',export_image_format='AUTO',export_apply=False)

def images(data):
 length,kind=struct.unpack_from('<II',data,12);d=json.loads(data[20:20+length]);offset=20+length+8;result=[]
 for image in d.get('images',[]):
  view=d['bufferViews'][image['bufferView']];start=offset+view.get('byteOffset',0);raw=data[start:start+view['byteLength']]
  result.append({'mime_type':image['mimeType'],'sha256':hashlib.sha256(raw).hexdigest(),'bytes':len(raw)})
 return d,result
original,expected=images((out/'original/selected_shepherd.glb').read_bytes());actual,found=images(path.read_bytes())
report={'asset_revision':'gsd-selected-rig-v001','format':'GLB with skin','path':path.relative_to(r).as_posix(),'bytes':path.stat().st_size,'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'skins':len(actual.get('skins',[])),'joint_count':len(actual['skins'][0]['joints']),'animations':len(actual.get('animations',[])),'image_payloads':found,'all_original_image_payloads_preserved':{i['sha256'] for i in found}=={i['sha256'] for i in expected},'runtime':'NOT TESTED'}
assert report['skins']==1 and report['joint_count']==34 and report['animations']==0
(out/'validation/glb-export.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8',newline='\n')
print('GLB_EXPORT',json.dumps(report))
