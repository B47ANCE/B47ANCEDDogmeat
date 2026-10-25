"""Revise only the head/neck split; retain every other v2 skin influence."""
from pathlib import Path
import bpy,hashlib,json,sys,importlib.util
import numpy as np
HERE=Path(__file__).resolve().parent;OUT=HERE.parent;ROOT=OUT.parents[1]
BASE=ROOT/'art/german_shepherd_motion_v2'
sys.path.insert(0,str(HERE));sys.path.insert(0,str(BASE/'source'))
spec=importlib.util.spec_from_file_location('skin_v2',BASE/'source/build_skin.py')
helper=importlib.util.module_from_spec(spec);spec.loader.exec_module(helper);helper.OUT=OUT
from head_rig import reweight_head

def main():
 bpy.ops.wm.open_mainfile(filepath=str(BASE/'source/shepherd_reweighted.blend'))
 objects=[o for o in bpy.data.objects if o.type=='MESH'];reference=next(o for o in objects if o.name.endswith('Coat2'))
 co=helper.array(reference.data.vertices,'co',3,np.float32);names=[g.name for g in reference.vertex_groups]
 previous=np.zeros((len(co),len(names)),np.float32)
 for vertex in reference.data.vertices:
  for group in vertex.groups:previous[vertex.index,group.group]=group.weight
 authored,head_proof=reweight_head(co,names,previous)
 report=json.loads((BASE/'validation/native-bind.json').read_text(encoding='utf-8'))
 report.update(project_version=(ROOT/'VERSION').read_text(encoding='utf-8').strip(),asset_revision='gsd-rest-head-v003',
  environment='Blender '+bpy.app.version_string+' offline',runtime='NOT TESTED',
  prior_skin_checkpoint='art/german_shepherd_motion_v2',head_weight_proof=head_proof,skin_attribute_proof={})
 for obj in objects:
  before=helper.mesh_hash(obj.data);target=helper.array(obj.data.vertices,'co',3,np.float32);selected=helper.mapping(co,target)
  assert np.array_equal(co[selected],target)
  current=authored[selected]
  # Preserve all other vertex groups. Replace only these two names/weights.
  for name in ('Bip01_Head','Bip01_Neck'):
   i=names.index(name);group=obj.vertex_groups[name];group.remove(list(range(len(target))))
   values=np.rint(current[:,i]*255).astype(np.uint8);indices=np.flatnonzero(values);indices=indices[np.argsort(values[indices])];values=values[indices]
   for chunk in np.split(indices,np.flatnonzero(values[1:]!=values[:-1])+1):
    if len(chunk):group.add(chunk.tolist(),float(current[chunk[0],i]),'REPLACE')
  assert helper.mesh_hash(obj.data)==before
  record=helper.patch_glb(BASE/'models'/(obj.name+'.glb'),co,authored,names,report)
  report['skin_attribute_proof'][obj.name]=record
  variant=next(v for v in report['variants'].values() if v['model']==obj.name)
  assert variant['geometry_uv_bound_sha256']==before
  variant.update(glb_sha256=record['glb_sha256'],max_influences=int((current>0).sum(axis=1).max()),
   unweighted_vertices=int((current.sum(axis=1)==0).sum()),max_weight_sum_error=float(np.abs(current.sum(axis=1)-1).max()))
  print('REWEIGHTED_HEAD',obj.name,record['glb_sha256'],flush=True)
 bpy.context.preferences.filepaths.save_version=0
 bpy.ops.wm.save_as_mainfile(filepath=str(HERE/'shepherd_reweighted.blend'),compress=True)
 (OUT/'validation/native-bind.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8',newline='\n')
 print('HEAD_SKIN_COMPLETE',flush=True)

if __name__=='__main__':main()
