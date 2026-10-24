"""Verify declared runtime asset hashes and their recorded authoring contract."""
import argparse,hashlib,json,struct
from pathlib import Path
from build_loadable import sources,ROOT

def check(all_files=False):
    folder=ROOT/'art/german_shepherd_native'
    report=json.loads((folder/'validation/native-bind.json').read_text())
    assert report['runtime']=='NOT TESTED' and report['bone_nodes']==34 and report['deforming_bones']==25
    assert report['bind_reference']=='Rac_Idle01 frame zero'
    manifest=json.loads((folder/'manifest.json').read_text())
    assert report['project_version']==manifest['recorded_project_version']
    mapping=sources();checked=0
    for variant in report['variants'].values():
        model=variant['model'];path=mapping['42/media/models_X/Skinned/'+model+'.glb'];raw=path.read_bytes()
        assert hashlib.sha256(raw).hexdigest()==variant['glb_sha256']
        magic,version,length=struct.unpack_from('<III',raw);assert magic==0x46546c67 and version==2 and length==len(raw)
        size,kind=struct.unpack_from('<II',raw,12);assert kind==0x4e4f534a
        doc=json.loads(raw[20:20+size]);assert len(doc['skins'])==1 and not doc.get('animations')
        assert len(doc['skins'][0]['joints'])==25
        assert doc['accessors'][doc['meshes'][0]['primitives'][0]['indices']]['count']==2590138*3
        assert variant['unchanged_source_geometry_uv'] and variant['geometry_uv_source_sha256']==variant['geometry_uv_bound_sha256']
        assert variant['max_influences']<=4 and variant['unweighted_vertices']==0
        assert variant['glb_uv_max_error']<2e-7 and variant['glb_position_max_error_after_inverse_alignment']<3e-5
        texture=mapping['42/media/textures/Body/'+model+'.png'].read_bytes()
        assert texture.startswith(b'\x89PNG\r\n\x1a\n');checked+=1
    if all_files:
        for relative,expected in manifest['files'].items():
            path=(folder/relative).resolve();assert path.is_relative_to(folder.resolve())
            assert hashlib.sha256(path.read_bytes()).hexdigest()==expected,relative
    motion=ROOT/'art/german_shepherd_motion'
    if all_files and (motion/'manifest.json').exists():
        for relative,expected in json.loads((motion/'manifest.json').read_text())['files'].items():
            path=(motion/relative).resolve();assert path.is_relative_to(motion.resolve())
            assert hashlib.sha256(path.read_bytes()).hexdigest()==expected,relative
    print(json.dumps({'status':'OFFLINE PASS','models':checked,'runtime':'NOT TESTED',
        'historical_dev8_native_gait_acceptance':'HOLD',
        'current_motion':'Original dog-pivot candidate; see motion checkpoint; PZ NOT TESTED',
        'all_checkpoint_files':all_files}))

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--all',action='store_true');args=parser.parse_args();check(args.all)
