"""Update local authored skin weights with hash-verified immutable meshes."""
from pathlib import Path
import sys,bpy,numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parent))
import build_native as b
from author_weights import weights
bpy.ops.wm.open_mainfile(filepath=str(b.OUT/'source/shepherd_native.blend'))
for obj in [o for o in bpy.data.objects if o.type=='MESH']:
 before=b.mesh_hash(obj.data);names=[g.name for g in obj.vertex_groups]
 mapped=weights(b.array(obj.data.vertices,'co',3,np.float32),names)
 obj.vertex_groups.clear()
 for i,name in enumerate(names):
  group=obj.vertex_groups.new(name=name)
  for value in np.unique(mapped[:,i]):
   if value>0:group.add(np.flatnonzero(mapped[:,i]==value).tolist(),float(value),'REPLACE')
 assert before==b.mesh_hash(obj.data)
bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(b.OUT/'source/shepherd_native.blend'),compress=True)
print('WEIGHTS UPDATED; all original mesh/UV hashes unchanged')
