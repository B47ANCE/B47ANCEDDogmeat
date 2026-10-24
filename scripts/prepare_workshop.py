"""Build and inspect an explicit Workshop test package. No upload, install or deletion."""
from pathlib import Path, PurePosixPath
import argparse, hashlib, json, re, subprocess, sys, tempfile, zipfile
from build_loadable import assemble, sources
from render_workshop import render, github_url

ROOT=Path(__file__).resolve().parents[1]
LABEL='MP testing build - dedicated multiplayer NOT TESTED'
PREFIX='mods/B47ANCEDDogmeat/'


def sha(data): return hashlib.sha256(data).hexdigest()


def configuration(root=ROOT):
    data=json.loads((root/'workshop.json').read_text(encoding='utf-8-sig'))
    inventory=json.loads((root/'source-inventory.json').read_text(encoding='utf-8'))
    if data['appid']!='108600' or data['mod_id']!='B47ANCEDDogmeat' or data['channel']!=LABEL:
        raise ValueError('Unexpected Workshop identity/channel')
    if data['visibility']!='0' or data['project_version']!=(root/'VERSION').read_text().strip():
        raise ValueError('Unexpected visibility/version')
    item=data['publishedfileid']
    if item is not None and (not isinstance(item,str) or not re.fullmatch(r'[1-9][0-9]{5,19}',item)):
        raise ValueError('Invalid assigned Workshop ID')
    if inventory['workshop_id']!=item: raise ValueError('Workshop ID differs from source inventory')
    return data


def payload():
    result={PREFIX+path:source.read_bytes() for path,source in sources().items()}
    declared={PREFIX+x['target'] for x in json.loads((ROOT/'source-inventory.json').read_text())['runtime_assets']}
    info=result[PREFIX+'42/mod.info'].decode('utf-8')
    if 'id=B47ANCEDDogmeat' not in info.splitlines() or 'require=' in info.lower():
        raise ValueError('Unexpected runtime identity/dependency')
    for path in result:
        if Path(path).suffix.lower() not in {'.lua','.json','.txt','.png','.info'} and not (path in declared and Path(path).suffix.lower() in {'.glb','.x','.xml'}):
            raise ValueError('Non-Lua runtime artifact: '+path)
    return result


def verify_archive(path, expected):
    with zipfile.ZipFile(path) as archive:
        names=archive.namelist()
        if len(names)!=len(set(names)) or len(names)!=len({n.casefold() for n in names}):
            raise ValueError('Duplicate/case-colliding archive members')
        for name in names:
            p=PurePosixPath(name)
            if p.is_absolute() or '..' in p.parts or '\\' in name or ':' in name or not name.startswith(PREFIX):
                raise ValueError('Unsafe archive path')
            if archive.getinfo(name).external_attr>>16 & 0o170000 == 0o120000:
                raise ValueError('Archive symlink')
        files={n for n in names if not n.endswith('/')}
        if files!=set(expected): raise ValueError('Unexpected/missing archive files')
        if archive.testzip() is not None: raise ValueError('Archive CRC failure')
        for name,raw in expected.items():
            if archive.read(name)!=raw: raise ValueError('Archive/source mismatch: '+name)
    return len(expected)


def vdf_string(value):
    if '\x00' in value or '\\n' in value: raise ValueError('Unsafe VDF text/literal newline escape')
    return '"'+value.replace('\\','\\\\').replace('"','\\"')+'"'


def build(output, preview=None):
    output=Path(output).resolve()
    if output.exists(): raise ValueError('Output exists; preserve prior packages and choose a new directory')
    config=configuration()
    description=render((ROOT/'docs/WORKSHOP_DESCRIPTION.md').read_text(encoding='utf-8'),github_url(ROOT))
    note=(ROOT/'docs/WORKSHOP_CHANGELOG.md').read_text(encoding='utf-8').strip()+'\n'
    if LABEL not in description or LABEL not in note or '\\n' in note or re.search(r'\b(?:TODO|TBD)\b',note):
        raise ValueError('Missing testing label or unreviewed change notes')
    if len(description.encode('utf-8'))>=8000 or not note.strip(): raise ValueError('Invalid description/changenote length')
    expected=payload()
    output.mkdir(parents=True)
    content=output/'Contents'
    assemble(content/'mods/B47ANCEDDogmeat')
    version=config['project_version'];package=output/f'B47ANCEDDogmeat-{version}.zip'
    with zipfile.ZipFile(package,'x',compression=zipfile.ZIP_DEFLATED) as archive:
        directory=zipfile.ZipInfo(PREFIX+'common/',(2000,1,1,0,0,0))
        directory.external_attr=(0o40755<<16)|0x10
        archive.writestr(directory,b'')
        for name,raw in sorted(expected.items()):
            info=zipfile.ZipInfo(name,(2000,1,1,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED
            info.external_attr=0o100644<<16
            archive.writestr(info,raw)
    verify_archive(package,expected)
    actual={p.relative_to(content).as_posix():p.read_bytes() for p in content.rglob('*') if p.is_file()}
    if actual!=expected: raise ValueError('Workshop stage/source mismatch')
    (output/'description.bbcode').write_text(description,encoding='utf-8',newline='\n')
    (output/'changenote.txt').write_text(note,encoding='utf-8',newline='\n')
    values={'appid':config['appid'],'publishedfileid':config['publishedfileid'] or '0',
            'contentfolder':content.as_posix(),'title':config['title'],'description':description,
            'changenote':note}
    # Visibility is explicit only at creation. Existing item visibility is preserved.
    if config['publishedfileid'] is None: values['visibility']=config['visibility']
    if preview:
        preview=Path(preview).resolve()
        if not preview.is_file() or preview.stat().st_size>=1_000_000:
            raise ValueError('Preview missing or at least 1 MB')
        values['previewfile']=preview.as_posix()
    text='"workshopitem"\n{\n'+''.join('  '+vdf_string(k)+' '+vdf_string(v)+'\n' for k,v in values.items())+'}\n'
    (output/'upload.vdf').write_text(text,encoding='utf-8',newline='\n')
    head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    manifest={'project_version':version,'source_commit':head,'appid':'108600','mod_id':'B47ANCEDDogmeat',
              'workshop_id':config['publishedfileid'],'new_item_authorization_required':config['publishedfileid'] is None,
              'package':package.name,'package_sha256':sha(package.read_bytes()),
              'files':{p:sha(raw) for p,raw in sorted(expected.items())},
              'thumbnail_sha256':sha((ROOT/'thumbnail.png').read_bytes()),
              'vdf_sha256':sha(text.encode()),'description_sha256':sha(description.encode()),
              'changenote_sha256':sha(note.encode()),'game_build':'42.21 / Steam 25485521',
              'validation':'Offline artifact parity PASS; target audit and fresh source/CI checks required before upload',
              'G6':'NOT TESTED','G7':'BLOCKED / NOT TESTED','stable_G8':'BLOCKED'}
    (output/'release-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8',newline='\n')
    return manifest


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    group=parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--check',action='store_true');group.add_argument('--output',type=Path)
    parser.add_argument('--preview',type=Path)
    args=parser.parse_args()
    try:
        if args.check:
            with tempfile.TemporaryDirectory(prefix='dogmeat-workshop-check-') as tmp: result=build(Path(tmp)/'package')
        else: result=build(args.output,args.preview)
        print(json.dumps({k:result[k] for k in ('project_version','source_commit','package_sha256','workshop_id','G7','stable_G8')},indent=2))
        return 0
    except (OSError,ValueError,KeyError,zipfile.BadZipFile) as exc:
        print('FAIL: '+str(exc));return 1

if __name__=='__main__':sys.exit(main())
