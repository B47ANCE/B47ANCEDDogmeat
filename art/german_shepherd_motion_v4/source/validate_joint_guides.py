"""Reopen the manual fitting scene and verify the requested rear joint shift."""
from pathlib import Path
import bpy,hashlib,json
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[3];HERE=Path(__file__).resolve().parent
path=HERE/'shepherd_joint_guides.blend';bpy.ops.wm.open_mainfile(filepath=str(path))
if bpy.context.object and bpy.context.object.mode!='OBJECT':bpy.ops.object.mode_set(mode='OBJECT')
guide=bpy.data.objects['EDIT THESE JOINT GUIDES']
mesh=next(o for o in bpy.context.scene.objects if o.type=='MESH')
assert mesh.data.library is not None and mesh.hide_select
assert all(not b.use_deform for b in guide.data.bones)
back=Vector((.96748,.25296,0)).normalized()
original={'L':[(.451202,.136585,-.24),(.625738,.202348,-.56)],
          'R':[(.339772,.454671,-.24),(.478176,.490376,-.56)]}
results={}
for side,points in original.items():
    bone=guide.data.bones[side+'_Stifle_Hock'];expected=[Vector(p)-back*.04 for p in points]
    error=max((bone.head_local-expected[0]).length,(bone.tail_local-expected[1]).length)
    assert error<2e-6 and bone.use_connect
    assert (guide.data.bones[side+'_Hock_Paw'].head_local-bone.tail_local).length<2e-6
    results[side]={'stifle':list(bone.head_local),'hock':list(bone.tail_local),'expected_forward_shift':.04,'max_error':error}
report={'project_version':(ROOT/'VERSION').read_text().strip(),'status':'OFFLINE PASS',
        'runtime':'NOT TESTED','scope':'Nondeforming authoring guides; no runtime skeleton edits',
        'source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'blend_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'linked_mesh':mesh.data.library.filepath,'rear_guides':results}
(HERE.parent/'validation/joint-guides.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8',newline='\n')
print('JOINT_GUIDES_PASS',json.dumps(results),flush=True)
