"""Refresh this authoring checkpoint and explicit runtime mappings, never deploy."""
from pathlib import Path
import hashlib,json
ROOT=Path(__file__).resolve().parents[3];OUT=ROOT/'art/german_shepherd_motion_v2'
def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def write(path,data):path.write_text(json.dumps(data,indent=2)+'\n',encoding='utf-8',newline='\n')
def main():
    files={p.relative_to(OUT).as_posix():digest(p) for p in sorted(OUT.rglob('*'))
        if p.is_file() and p.name!='manifest.json' and p.suffix not in ('.pyc','.blend1') and '__pycache__' not in p.parts}
    write(OUT/'manifest.json',{'asset_revision':'gsd-skin-motion-v002','recorded_project_version':(ROOT/'VERSION').read_text().strip(),
        'runtime':'NOT TESTED','historical_sources':['art/german_shepherd_native','art/german_shepherd_motion'],
        'geometry_uv_textures_unchanged':True,'skin_attributes_revised':True,'visual_acceptance':'Review candidate; not PZ verified','files':files})
    inventory=json.loads((ROOT/'source-inventory.json').read_text());entries=[]
    for item in inventory['runtime_assets']:
        if '/anims/' in item['source'] and item['source'].startswith('art/german_shepherd_motion'):continue
        if item['source'].startswith('art/german_shepherd_native/models/'):
            item['source']=item['source'].replace('art/german_shepherd_native/models/','art/german_shepherd_motion_v2/models/')
        item['sha256']=digest(ROOT/item['source']);entries.append(item)
    for clip in sorted((OUT/'anims').glob('*.x')):
        entries.append({'source':clip.relative_to(ROOT).as_posix(),'target':'42/media/anims_X/Raccoon/'+clip.name,'sha256':digest(clip)})
    assert len(entries)==93 and len({i['target'] for i in entries})==93
    inventory['runtime_assets']=entries;write(ROOT/'source-inventory.json',inventory)
    print('Checkpoint hashes refreshed; 93 explicit runtime assets; no assembly/deploy')
if __name__=='__main__':main()
