"""Read-only retention check for the two user-supplied additional coats."""
from pathlib import Path
import hashlib,json
ROOT=Path(__file__).resolve().parent
def digest(path):
    h=hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda:stream.read(1024*1024),b''):h.update(block)
    return h.hexdigest()
manifest=json.loads((ROOT/'manifest.json').read_text(encoding='utf-8'))
for name,expected in manifest['files'].items():
    path=(ROOT/name).resolve()
    assert path.is_relative_to(ROOT) and path.is_file(),name
    assert digest(path)==expected,'Changed file or unhydrated Git LFS: '+name
provenance=json.loads((ROOT/'source-provenance.json').read_text(encoding='utf-8'))
compat=json.loads((ROOT/'compatibility.json').read_text(encoding='utf-8'))
for name in ['variation_1','variation_2']:
    coat=provenance['coats'][name]
    assert len(coat['archives'])==2 and all(a['crc']=='PASS' for a in coat['archives'])
    assert set(coat['maps'])=={'base_color','normal','roughness','metallic'}
    for role,entry in coat['maps'].items():
        assert entry['dimensions']==[2048,2048]
        assert digest(ROOT/name/(role+'.png'))==entry['sha256']
    members=[m for a in coat['archives'] for m in a['members']]
    assert digest(ROOT/name/'supplied.fbx')==next(m['sha256'] for m in members if m['name'].endswith('.fbx'))
    bases=[m['sha256'] for m in members if m['name'].endswith('_texture.png')]
    assert len(bases)==2 and len(set(bases))==1
    assert compat['coats'][name]['geometry_matches_at_1e_5'] is True
    assert compat['coats'][name]['texture_swap_compatible'] is False
    assert compat['coats'][name]['rigged'] is False
print('COAT RETENTION PASS:',len(manifest['files']),'files; distinct UV layouts; runtime NOT TESTED')
