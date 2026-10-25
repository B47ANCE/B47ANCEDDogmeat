"""Assemble a development mod from authoritative sources; no install, ZIP or upload."""
from pathlib import Path
import argparse
import json
import tempfile
import hashlib
import ntpath

ROOT = Path(__file__).resolve().parents[1]

def sources():
    inventory = json.loads((ROOT/'source-inventory.json').read_text(encoding='utf-8'))
    result = {}
    for relative in inventory['authoritative_lua']:
        path = Path(relative)
        if path.parts[1] in ('domain', 'native'):
            target = Path('42/media/lua/server').joinpath(*path.parts[2:])
        elif path.parts[1] == 'bootstrap':
            target = Path('42/media/lua').joinpath(*path.parts[2:])
        else:
            raise ValueError('Undeclared Lua source category')
        result[target.as_posix()] = ROOT/path
    for language in inventory['languages']:
        for category in inventory['localization_keys']:
            result[f'42/media/lua/shared/Translate/{language}/{category}.json'] = ROOT/f'src/localization/{language}/{category}.json'
    result['42/mod.info'] = ROOT/'src/metadata/mod.info'
    result['42/poster.png'] = ROOT/'src/metadata/poster.png'
    result['42/media/ui/B47ANCEDDogmeat_icon.png'] = ROOT/'src/metadata/media/ui/B47ANCEDDogmeat_icon.png'
    result['42/media/sandbox-options.txt'] = ROOT/'src/metadata/sandbox-options.txt'
    for entry in inventory.get('runtime_assets',[]):
        relative,target=entry['source'],entry['target']
        source=(ROOT/relative).resolve();destination=Path(target)
        if (not source.is_relative_to(ROOT) or ntpath.isabs(relative) or '\\' in relative or ':' in relative or '..' in Path(relative).parts
                or destination.is_absolute() or '..' in destination.parts or '\\' in target or ':' in target
                or not target.startswith('42/media/') or target in result):
            raise ValueError('Unsafe/duplicate runtime asset mapping')
        if source.suffix.lower() not in {'.glb','.png','.txt','.x','.xml'} or destination.suffix.lower()!=source.suffix.lower():
            raise ValueError('Unexpected runtime asset format')
        raw=source.read_bytes()
        if raw.startswith(b'version https://git-lfs.github.com/spec/v1'):
            raise ValueError('Runtime asset is an unhydrated Git LFS pointer: '+relative)
        if hashlib.sha256(raw).hexdigest()!=entry['sha256']:
            raise ValueError('Runtime asset hash differs: '+relative)
        result[target]=source
    if len({x.casefold() for x in result})!=len(result):raise ValueError('Case collision')
    return result

def assemble(destination):
    destination = destination.resolve()
    if destination.exists():
        raise ValueError('Output already exists; use a new directory. No cleanup/overwrite is automatic.')
    mapping = sources()
    if len({p.casefold() for p in mapping}) != len(mapping):
        raise ValueError('Case collision')
    destination.mkdir(parents=True)
    (destination/'common').mkdir()
    for relative, source in mapping.items():
        target = destination/relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(source.read_bytes())
    actual = {p.relative_to(destination).as_posix() for p in destination.rglob('*') if p.is_file()}
    if actual != set(mapping) or any((destination/p).read_bytes() != src.read_bytes() for p,src in mapping.items()):
        raise ValueError('Assembled source parity differs')
    return {'status':'SOURCE PARITY PASS','files':len(mapping),'mod_id':'B47ANCEDDogmeat',
            'version':(ROOT/'VERSION').read_text().strip(),'runtime':'NOT TESTED'}

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    group=parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--check',action='store_true')
    group.add_argument('--output',type=Path,help='New development tree; never point at an installed mod')
    args=parser.parse_args()
    if args.check:
        with tempfile.TemporaryDirectory(prefix='b47dog-layout-') as directory:
            result=assemble(Path(directory)/'B47ANCEDDogmeat')
    else:
        result=assemble(args.output)
        result['output']=str(args.output.resolve())
    print(json.dumps(result,indent=2))

if __name__=='__main__':
    main()
