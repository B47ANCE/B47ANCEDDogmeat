"""Freeze motion provenance and replace only the 47 explicit clip mappings."""
from pathlib import Path
import hashlib,json
ROOT=Path(__file__).resolve().parents[3];OUT=ROOT/'art/german_shepherd_motion_v4';MODEL=ROOT/'art/german_shepherd_motion_v3'
def digest(path):
    with path.open('rb') as stream:return hashlib.file_digest(stream,'sha256').hexdigest()
def write(path,data):path.write_text(json.dumps(data,indent=2)+'\n',encoding='utf-8',newline='\n')
def main():
    version=(ROOT/'VERSION').read_text().strip()
    assert json.loads((OUT/'validation/motion.json').read_text())['project_version']==version
    bind=json.loads((MODEL/'validation/native-bind.json').read_text())
    inventory=json.loads((ROOT/'source-inventory.json').read_text())
    for variant in bind['variants'].values():
        relative='art/german_shepherd_motion_v3/models/'+variant['model']+'.glb'
        entries=[i for i in inventory['runtime_assets'] if i['source']==relative]
        assert len(entries)==1 and entries[0]['sha256']==variant['glb_sha256']==digest(ROOT/relative)
    dependencies=[MODEL/'source/shepherd_reweighted.blend',MODEL/'source/head_rig.py',
        MODEL/'validation/native-bind.json',MODEL/'validation/head-deformation.json',
        *sorted((MODEL/'models').glob('*.glb')),
        ROOT/'art/german_shepherd_motion_v2/source/anatomy.py',
        ROOT/'art/german_shepherd_native/source/build_native.py',ROOT/'art/german_shepherd_native/source/native_clip_reader.py']
    files={p.relative_to(OUT).as_posix():digest(p) for p in sorted(OUT.rglob('*'))
        if p.is_file() and p.name!='manifest.json' and p.suffix not in ('.pyc','.blend1') and '__pycache__' not in p.parts}
    write(OUT/'manifest.json',{'asset_revision':'gsd-canine-motion-v004','recorded_project_version':version,
        'runtime':'NOT TESTED','model_checkpoint':'art/german_shepherd_motion_v3',
        'geometry_uv_textures_unchanged':True,'skin_attributes_revised':False,
        'visual_acceptance':'Offline review candidate; PZ NOT TESTED',
        'external_input_sha256':{p.relative_to(ROOT).as_posix():digest(p) for p in dependencies},'files':files})
    entries=[i for i in inventory['runtime_assets'] if not (i['source'].startswith('art/german_shepherd_motion') and '/anims/' in i['source'])]
    assert len(entries)==46
    clips=sorted((OUT/'anims').glob('*.x'));assert len(clips)==47
    for clip in clips:entries.append({'source':clip.relative_to(ROOT).as_posix(),'target':'42/media/anims_X/Raccoon/'+clip.name,'sha256':digest(clip)})
    assert len(entries)==93 and len({i['target'] for i in entries})==93
    inventory['runtime_assets']=entries;write(ROOT/'source-inventory.json',inventory)
    print('Frozen v3 models verified; 47 v4 clips mapped; 46 other mappings preserved; no assembly/deploy')
if __name__=='__main__':main()
