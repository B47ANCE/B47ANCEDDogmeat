"""Read supplied FBX surfaces/UVs without modifying or replacing the selected rig."""
import hashlib,json
from pathlib import Path
import bpy
import numpy as np

ROOT=Path(__file__).resolve().parents[1]

def capture():
    obj=next(o for o in bpy.data.objects if o.type=='MESH')
    mesh=obj.data
    def array(collection,property,width,dtype):
        value=np.empty(len(collection)*width,dtype=dtype)
        collection.foreach_get(property,value)
        return value.reshape(-1,width)
    assert all(len(p.vertices)==3 for p in mesh.polygons)
    return {'co':array(mesh.vertices,'co',3,np.float32),
            'indices':array(mesh.loops,'vertex_index',1,np.int32).ravel(),
            'uv':array(mesh.uv_layers.active.data,'uv',2,np.float32),
            'triangles':len(mesh.polygons)}

def signatures(data):
    # Ignore vertex/triangle order and UV seam splits. Compare triangle corners
    # by supplied local position at 1e-5 precision; no mesh coordinates are edited.
    positions=np.rint(data['co'][data['indices']].astype(np.float64)*1e5).astype('<i4')
    keys=positions.view('V12').reshape(-1,3)
    order=np.argsort(keys,axis=1)
    triangles=np.ascontiguousarray(np.take_along_axis(keys,order,axis=1)).view('V36').ravel()
    triangle_order=np.argsort(triangles,kind='stable')
    uv=np.take_along_axis(data['uv'].reshape(-1,3,2),order[:,:,None],axis=1)
    return hashlib.sha256(triangles[triangle_order].tobytes()).hexdigest(),uv[triangle_order].reshape(-1,2)

bpy.ops.wm.open_mainfile(filepath=str(ROOT/'source/selected_shepherd_rigged.blend'))
base=capture();base_signature,base_uv=signatures(base)
report={'asset_revision':'gsd-selected-coats-v001','environment':'Blender '+bpy.app.version_string+' offline',
        'geometry_comparison':'Unordered triangle corners, local positions quantized to 1e-5; UVs aligned by geometry',
        'base_vertices':len(base['co']),'base_triangles':base['triangles'],
        'base_geometry_signature':base_signature,'coats':{},'runtime':'NOT TESTED'}
for name in ['variation_1','variation_2']:
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.fbx(filepath=str(ROOT/'coats'/name/'supplied.fbx'))
    data=capture();signature,uv=signatures(data)
    assert signature==base_signature,'Supplied surface geometry differs'
    delta=np.abs(uv-base_uv)
    entry={'vertices':len(data['co']),'triangles':data['triangles'],
           'canonical_geometry_signature':signature,'geometry_matches_at_1e_5':True,
           'aligned_uv_max_error':float(delta.max()),'aligned_uv_mean_error':float(delta.mean()),
           'aligned_uv_corners_within_1e_5':float(np.mean(np.max(delta,axis=1)<=1e-5)),
           'texture_swap_compatible':bool(np.max(delta)<=1e-5),
           'rigged':False,'disposition':'Preserve supplied mesh and matching maps; no texture swap or UV edits'}
    report['coats'][name]=entry
(ROOT/'coats/compatibility.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8',newline='\n')
print('COAT_COMPATIBILITY',json.dumps(report))
