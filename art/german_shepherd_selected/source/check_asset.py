"""Verify the retained rig-only asset's exact bytes and recorded acceptance scope."""
from pathlib import Path
import hashlib,json,sys
ROOT=Path(__file__).resolve().parents[1]

def digest(path):
 h=hashlib.sha256()
 with path.open('rb') as stream:
  for part in iter(lambda:stream.read(1024*1024),b''):h.update(part)
 return h.hexdigest()

def main():
 manifest=json.loads((ROOT/'validation/asset-manifest.json').read_text(encoding='utf-8'))
 errors=[]
 for relative,expected in manifest['files'].items():
  path=(ROOT/relative).resolve()
  if not path.is_relative_to(ROOT) or not path.is_file():errors.append('Missing/unsafe asset path: '+relative);continue
  if digest(path)!=expected:errors.append('Hash differs (hydrate Git LFS if needed): '+relative)
 rig=json.loads((ROOT/'validation/rig-validation.json').read_text())
 fbx=json.loads((ROOT/'validation/fbx-roundtrip.json').read_text())
 glb=json.loads((ROOT/'validation/glb-export.json').read_text())
 if rig['geometry_sha256_before']!=rig['geometry_sha256_after'] or rig['geometry_uv_topology_unchanged'] is not True:errors.append('Geometry/UV contract differs')
 if rig['bone_count']!=34 or fbx['bone_count']!=34 or glb['joint_count']!=34:errors.append('Native bone count differs')
 if not (rig['native_bone_names_and_parents_match'] and fbx['bone_names_parents_roundtrip_match'] and glb['native_names_and_parents_match']):errors.append('Native hierarchy mismatch')
 if rig['unweighted_vertices'] or fbx['unweighted_vertices'] or fbx['max_influences']>4 or fbx['weight_sum_max_error']>1e-5:errors.append('Invalid skin weights')
 if rig['triangles']!=2590138 or fbx['triangles']!=rig['triangles'] or fbx['local_position_max_error']!=0:errors.append('Topology/position acceptance differs')
 if glb['all_original_image_payloads_preserved'] is not True or glb['animations']!=0:errors.append('GLB texture/no-bundled-clip acceptance differs')
 if rig['native_model_replaced'] is not False or rig['native_animations_bundled'] is not False:errors.append('Native asset boundary differs')
 print(json.dumps({'status':'FAIL' if errors else 'OFFLINE ASSET PASS','files_hashed':len(manifest['files']),'bone_count':34,'triangles':rig['triangles'],'geometry_uv_unchanged':not errors,'fbx_material_limit':'Only diffuse roundtrips; original complete PBR retained in BLEND/GLB','runtime':'NOT TESTED','errors':errors},indent=2))
 return bool(errors)

if __name__=='__main__':sys.exit(main())
