"""Verify declared runtime asset hashes and their recorded authoring contract."""
import argparse,hashlib,json,struct
from pathlib import Path
from build_loadable import sources,ROOT

def check_motion_mapping(inventory):
    """Reject a valid but stale motion checkpoint being packaged by mistake."""
    motion=ROOT/'art/german_shepherd_motion_v4'
    clips={p.name:p for p in (motion/'anims').glob('*.x')};assert len(clips)==47
    entries=[i for i in inventory['runtime_assets'] if i['target'].startswith('42/media/anims_X/Raccoon/B47Dogmeat_')]
    assert len(entries)==47 and {Path(i['target']).name for i in entries}==set(clips)
    for item in entries:
        path=clips[Path(item['target']).name]
        assert item['source']==path.relative_to(ROOT).as_posix(),'Stale motion checkpoint'
        assert item['sha256']==hashlib.sha256(path.read_bytes()).hexdigest()
    models=[i for i in inventory['runtime_assets'] if i['target'].startswith('42/media/models_X/Skinned/B47Dogmeat_GSD_')]
    assert len(models)==3 and all(i['source'].startswith('art/german_shepherd_motion_v3/models/') for i in models)

def check(all_files=False):
    check_motion_mapping(json.loads((ROOT/'source-inventory.json').read_text()))
    folder=ROOT/'art/german_shepherd_motion_v3'
    report=json.loads((folder/'validation/native-bind.json').read_text())
    assert report['runtime']=='NOT TESTED' and report['bone_nodes']==34 and report['deforming_bones']==25
    assert report['bind_reference']=='Rac_Idle01 frame zero'
    manifest=json.loads((folder/'manifest.json').read_text())
    assert report['project_version']==manifest['recorded_project_version']
    motion=ROOT/'art/german_shepherd_motion_v4'
    motion_manifest=json.loads((motion/'manifest.json').read_text())
    assert motion_manifest['recorded_project_version']==(ROOT/'VERSION').read_text().strip()
    assert motion_manifest['skin_attributes_revised'] is False
    mapping=sources();checked=0
    for variant in report['variants'].values():
        model=variant['model'];path=mapping['42/media/models_X/Skinned/'+model+'.glb'];raw=path.read_bytes()
        assert hashlib.sha256(raw).hexdigest()==variant['glb_sha256']
        magic,version,length=struct.unpack_from('<III',raw);assert magic==0x46546c67 and version==2 and length==len(raw)
        size,kind=struct.unpack_from('<II',raw,12);assert kind==0x4e4f534a
        doc=json.loads(raw[20:20+size]);assert len(doc['skins'])==1 and not doc.get('animations')
        proof=report['skin_attribute_proof'][model]
        assert proof['all_non_skin_bytes_unchanged']
        masked=bytearray(raw);binary_offset=28+size
        for mesh in doc['meshes']:
            for primitive in mesh['primitives']:
                for attribute in ('JOINTS_0','WEIGHTS_0'):
                    accessor=doc['accessors'][primitive['attributes'][attribute]]
                    view=doc['bufferViews'][accessor['bufferView']]
                    width={5121:1,5123:2,5126:4}[accessor['componentType']]*4
                    assert view.get('byteStride',width)==width
                    start=binary_offset+view.get('byteOffset',0)+accessor.get('byteOffset',0)
                    masked[start:start+accessor['count']*width]=b'\0'*(accessor['count']*width)
        assert hashlib.sha256(masked).hexdigest()==proof['unchanged_non_skin_bytes_sha256']
        assert len(doc['skins'][0]['joints'])==25
        assert doc['accessors'][doc['meshes'][0]['primitives'][0]['indices']]['count']==2590138*3
        assert variant['unchanged_source_geometry_uv'] and variant['geometry_uv_source_sha256']==variant['geometry_uv_bound_sha256']
        assert variant['max_influences']<=4 and variant['unweighted_vertices']==0
        assert variant['glb_uv_max_error']<2e-7 and variant['glb_position_max_error_after_inverse_alignment']<3e-5
        texture=mapping['42/media/textures/Body/'+model+'.png'].read_bytes()
        assert texture.startswith(b'\x89PNG\r\n\x1a\n');checked+=1
    if all_files:
        for relative,expected in motion_manifest['files'].items():
            path=(motion/relative).resolve();assert path.is_relative_to(motion.resolve())
            assert hashlib.sha256(path.read_bytes()).hexdigest()==expected,relative
        for relative,expected in motion_manifest['external_input_sha256'].items():
            path=(ROOT/relative).resolve();assert path.is_relative_to(ROOT.resolve())
            assert hashlib.sha256(path.read_bytes()).hexdigest()==expected,relative
        for relative,expected in manifest.get('external_input_sha256',{}).items():
            path=(ROOT/relative).resolve();assert path.is_relative_to(ROOT.resolve())
            assert hashlib.sha256(path.read_bytes()).hexdigest()==expected,relative
        for relative,expected in manifest['files'].items():
            path=(folder/relative).resolve();assert path.is_relative_to(folder.resolve())
            assert hashlib.sha256(path.read_bytes()).hexdigest()==expected,relative
    if all_files:
        for historical in ('german_shepherd_native','german_shepherd_motion','german_shepherd_motion_v2'):
            checkpoint=ROOT/'art'/historical
            for relative,expected in json.loads((checkpoint/'manifest.json').read_text())['files'].items():
                path=(checkpoint/relative).resolve();assert path.is_relative_to(checkpoint.resolve())
                assert hashlib.sha256(path.read_bytes()).hexdigest()==expected,relative
    print(json.dumps({'status':'OFFLINE PASS','models':checked,'runtime':'NOT TESTED',
        'historical_dev8_native_gait_acceptance':'HOLD',
        'historical_dev9_visual_acceptance':'REJECTED by user',
        'current_motion':'Canine movement v4; frozen v3 skins; PZ NOT TESTED',
        'all_checkpoint_files':all_files}))

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--all',action='store_true');args=parser.parse_args();check(args.all)
