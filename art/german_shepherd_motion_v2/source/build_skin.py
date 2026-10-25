"""Revise only skin attributes; preserve frozen GLB geometry and source meshes.

Blender --background --factory-startup --python this.py. No installed game input.
The prior native checkpoint remains immutable and supplies the same bone/bind
contract. Editable output includes all three supplied coats with revised weights.
"""
import bpy,hashlib,json,struct,sys
import numpy as np
from pathlib import Path
HERE=Path(__file__).resolve().parent;OUT=HERE.parent;ROOT=OUT.parents[1]
sys.path.insert(0,str(HERE));sys.path.insert(0,str(ROOT/'art/german_shepherd_native/source'))
from build_native import array,mesh_hash
from generate_tail_field import generate_tail_field
from generate_limb_correction import generate_limb_correction
from anatomy import weights
BASE=ROOT/'art/german_shepherd_native'

def digest(data):return hashlib.sha256(data).hexdigest()
def keys(co):return np.ascontiguousarray(np.rint(co*1e6).astype('<i8')).view('V24').ravel()
def mapping(source,target):
    source_keys=keys(source);order=np.argsort(source_keys);sorted_keys=source_keys[order]
    target_keys=keys(target);indices=np.searchsorted(sorted_keys,target_keys)
    assert np.all(indices<len(order)) and np.array_equal(sorted_keys[indices],target_keys)
    return order[indices]

def patch_glb(path,co,authored,names,report):
    raw=path.read_bytes();size,kind=struct.unpack_from('<II',raw,12)
    assert kind==0x4e4f534a
    doc=json.loads(raw[20:20+size]);offset=28+size;binary=bytearray(raw[offset:])
    skin_names=[doc['nodes'][i]['name'] for i in doc['skins'][0]['joints']]
    assert len(skin_names)==25 and set(skin_names)==set(names)
    allowed=[]
    def accessor(index):
        a=doc['accessors'][index];v=doc['bufferViews'][a['bufferView']]
        dtype={5121:'u1',5123:'<u2',5125:'<u4',5126:'<f4'}[a['componentType']]
        width={'SCALAR':1,'VEC2':2,'VEC3':3,'VEC4':4}[a['type']];item=np.dtype(dtype).itemsize
        start=v.get('byteOffset',0)+a.get('byteOffset',0)
        assert v.get('byteStride',width*item)==width*item
        return np.ndarray((a['count'],width),dtype=dtype,buffer=binary,offset=start),start,a
    transform=np.array(report['native_to_authoring'])@np.diag([1,1,-1,1])
    for mesh in doc['meshes']:
        for primitive in mesh['primitives']:
            attributes=primitive['attributes'];positions,_,_=accessor(attributes['POSITION'])
            restored=positions@transform[:3,:3].T+transform[:3,3]
            selected=mapping(co,restored);error=float(np.max(np.abs(co[selected]-restored)))
            # Native float32 alignment roundtrip stays within half of the
            # source's six-decimal coordinate grid; exact key matching above is
            # mandatory. No coordinates are rewritten.
            assert error<5e-7,error
            ordered=authored[selected][:,[names.index(n) for n in skin_names]]
            keep=np.argsort(ordered,axis=1)[:,-4:][:,::-1];values=np.take_along_axis(ordered,keep,axis=1)
            joints,start,a=accessor(attributes['JOINTS_0']);joints[:]=keep;allowed.append((start,start+joints.nbytes))
            output,start,a=accessor(attributes['WEIGHTS_0']);assert a['componentType']==5126 and not a.get('normalized')
            output[:]=values;allowed.append((start,start+output.nbytes))
            assert np.allclose(output.sum(axis=1),1,atol=1e-7)
    # Byte comparison, not a newly exported mesh: everything outside skin data
    # (positions, topology, UVs, normals, embedded images, nodes and binds) stays.
    immutable=bytearray(raw[offset:]);comparison=bytearray(binary)
    for start,end in allowed:immutable[start:end]=b'\0'*(end-start);comparison[start:end]=b'\0'*(end-start)
    assert immutable==comparison
    result=raw[:offset]+binary;target=OUT/'models'/path.name;target.write_bytes(result)
    return {'glb_sha256':digest(result),'prior_glb_sha256':digest(raw),
        'unchanged_non_skin_bytes_sha256':digest(raw[:offset]+immutable),
        'changed_attributes':['JOINTS_0','WEIGHTS_0'],'source_mapping_max_error':error,
        'all_non_skin_bytes_unchanged':True}

def main():
    bpy.ops.wm.open_mainfile(filepath=str(BASE/'source/shepherd_native.blend'))
    objects=[o for o in bpy.data.objects if o.type=='MESH'];reference=next(o for o in objects if o.name.endswith('Coat2'))
    co=array(reference.data.vertices,'co',3,np.float32);edges=array(reference.data.edges,'vertices',2,np.int32)
    field,tail,field_report=generate_tail_field(co,edges);names=[g.name for g in reference.vertex_groups]
    limb_fields,limb_report=generate_limb_correction(co,edges)
    authored=weights(co,names,field,limb_fields);report=json.loads((BASE/'validation/native-bind.json').read_text())
    report.update(project_version=(ROOT/'VERSION').read_text().strip(),asset_revision='gsd-skin-motion-v002',
        environment='Blender '+bpy.app.version_string+' offline',runtime='NOT TESTED',
        frozen_bind_checkpoint='art/german_shepherd_native',tail_field=field_report,
        tail_root=[.59,.37,.08],limb_field=limb_report,skin_attribute_proof={})
    for obj in objects:
        before=mesh_hash(obj.data);target=array(obj.data.vertices,'co',3,np.float32);selected=mapping(co,target)
        assert np.array_equal(co[selected],target)
        current=authored[selected];obj.vertex_groups.clear()
        for i,name in enumerate(names):
            group=obj.vertex_groups.new(name=name);values=np.rint(current[:,i]*255).astype(np.uint8)
            indices=np.flatnonzero(values);indices=indices[np.argsort(values[indices])];values=values[indices]
            for chunk in np.split(indices,np.flatnonzero(values[1:]!=values[:-1])+1):
                if len(chunk):group.add(chunk.tolist(),float(current[chunk[0],i]),'REPLACE')
        assert mesh_hash(obj.data)==before
        record=patch_glb(BASE/'models'/(obj.name+'.glb'),co,authored,names,report)
        report['skin_attribute_proof'][obj.name]=record
        variant=next(v for v in report['variants'].values() if v['model']==obj.name)
        assert variant['geometry_uv_bound_sha256']==before
        variant['glb_sha256']=record['glb_sha256'];variant['max_influences']=int((current>0).sum(axis=1).max())
        variant['unweighted_vertices']=int((current.sum(axis=1)==0).sum())
        print('REWEIGHTED',obj.name,record['glb_sha256'],flush=True)
    bpy.context.preferences.filepaths.save_version=0
    bpy.ops.wm.save_as_mainfile(filepath=str(HERE/'shepherd_reweighted.blend'),compress=True)
    (OUT/'validation/native-bind.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8',newline='\n')
    print('SKIN_COMPLETE',flush=True)

if __name__=='__main__':main()
