"""Manual cached-login SteamCMD publisher; never restarts Steam or installs a mod."""
from pathlib import Path
import argparse, json, os, re, subprocess, sys, time
from audit_publication_target import audit, sha
from prepare_workshop import ROOT, configuration, payload, verify_archive, LABEL
from render_workshop import render, github_url


def read_vdf(path):
    tokens=[json.loads(x,strict=False) for x in re.findall(r'"(?:\\.|[^"\\])*"',path.read_text(encoding='utf-8-sig'),re.S)]
    if not tokens or tokens[0]!='workshopitem' or len(tokens)%2!=1: raise ValueError('Invalid VDF')
    keys=tokens[1::2]
    if len(keys)!=len(set(keys)): raise ValueError('Duplicate VDF keys')
    return dict(zip(keys,tokens[2::2]))


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--stage',type=Path,required=True)
    parser.add_argument('--steamcmd',type=Path,required=True)
    parser.add_argument('--game-root',type=Path,required=True)
    parser.add_argument('--account-env',default='DOGMEAT_STEAM_ACCOUNT')
    parser.add_argument('--new-item',action='store_true',help='Requires explicit user authorization for first creation')
    args=parser.parse_args()
    try:
        stage=args.stage.resolve();config=configuration()
        if not stage.is_relative_to(ROOT/'staging'): raise ValueError('Stage must be owned ignored project staging')
        if not args.steamcmd.is_file(): raise ValueError('Verified SteamCMD missing')
        account=os.environ.get(args.account_env,'')
        if not account or any(c.isspace() for c in account): raise ValueError('Cached account name unavailable; never supply a password/token')
        if (config['publishedfileid'] is None)!=args.new_item: raise ValueError('New/existing item authorization mismatch')
        subprocess.run(['git','fetch','origin'],cwd=ROOT,check=True,capture_output=True)
        head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
        remote=subprocess.check_output(['git','rev-parse','origin/main'],cwd=ROOT,text=True).strip()
        if head!=remote or subprocess.check_output(['git','status','--porcelain'],cwd=ROOT).strip():
            raise ValueError('Release source must be clean and exactly verified origin/main')
        manifest=json.loads((stage/'release-manifest.json').read_text(encoding='utf-8'))
        if manifest['source_commit']!=head or manifest['project_version']!=config['project_version']:
            raise ValueError('Stale release manifest')
        expected=payload();package=stage/manifest['package']
        verify_archive(package,expected)
        if sha(package.read_bytes())!=manifest['package_sha256'] or manifest['files']!={p:sha(v) for p,v in sorted(expected.items())}:
            raise ValueError('Archive or provenance mismatch')
        actual={p.relative_to(stage/'Contents').as_posix():p.read_bytes() for p in (stage/'Contents').rglob('*') if p.is_file()}
        if actual!=expected: raise ValueError('Stage content differs from authoritative source')
        target=audit(args.game_root)
        if target['errors']: raise ValueError('Vanilla target audit failed')
        vdf=stage/'upload.vdf';values=read_vdf(vdf)
        description=render((ROOT/'docs/WORKSHOP_DESCRIPTION.md').read_text(encoding='utf-8'),github_url(ROOT))
        note=(ROOT/'docs/WORKSHOP_CHANGELOG.md').read_text(encoding='utf-8').strip()+'\n'
        wanted={'appid':'108600','publishedfileid':config['publishedfileid'] or '0',
                'contentfolder':(stage/'Contents').as_posix(),'title':config['title'],
                'description':description,'changenote':note}
        if args.new_item: wanted['visibility']=config['visibility']
        if set(values)!=set(wanted)|{'previewfile'} or any(values.get(k)!=v for k,v in wanted.items()):
            raise ValueError('VDF target/content/description differs from approved source')
        preview=Path(values['previewfile'])
        if not preview.is_file() or preview.stat().st_size>=1_000_000: raise ValueError('Preview invalid')
        if LABEL not in description or LABEL not in note: raise ValueError('Missing MP testing warning')
        if sha(vdf.read_bytes())!=manifest['vdf_sha256']: raise ValueError('VDF changed after package preparation')
        for command in (['scripts/check_versions.py','--root','.','--release'],['scripts/validate_m0r.py'],['scripts/validate_foundation.py']):
            subprocess.run([sys.executable,'-B',*command],cwd=ROOT,check=True,stdout=subprocess.DEVNULL)
        checks=json.loads(subprocess.check_output(['gh','api','repos/B47ANCE/B47ANCEDDogmeat/commits/'+head+'/check-runs'],cwd=ROOT,text=True))['check_runs']
        if not checks or any(x['status']!='completed' or x['conclusion']!='success' for x in checks):
            raise ValueError('Release source CI incomplete or failed')
        attempt=stage/'upload-attempt.json'
        with attempt.open('x',encoding='utf-8') as file:
            json.dump({'source_commit':head,'workshop_id_before':config['publishedfileid'],
                       'new_item_explicit':args.new_item,'package_sha256':manifest['package_sha256'],
                       'preview_sha256':sha(preview.read_bytes()),'ci':[x['html_url'] for x in checks]},file,indent=2)
        log_path=ROOT/'.m0r-local/publication'/('steamcmd-'+head[:12]+'.log')
        log_path.parent.mkdir(parents=True,exist_ok=True)
        print('Starting the explicitly authorized Workshop test upload; Steam desktop remains unchanged.',flush=True)
        start=time.time()
        with log_path.open('xb') as log:
            process=subprocess.Popen([str(args.steamcmd),'+login',account,'+workshop_build_item',str(vdf),'+quit'],
                                     cwd=args.steamcmd.parent,stdin=subprocess.DEVNULL,stdout=log,stderr=subprocess.STDOUT)
            try: code=process.wait(timeout=240)
            except subprocess.TimeoutExpired:
                process.terminate();process.wait(timeout=15);code=-1
        output=log_path.read_text(encoding='utf-8',errors='replace')
        success=re.search(r'Success\.\s*Published File Id:\s*([1-9][0-9]+)',output,re.I)
        assigned=read_vdf(vdf).get('publishedfileid','0')
        verified=code==0 and success is not None and success[1]==assigned and assigned!='0'
        if config['publishedfileid'] is not None: verified=verified and assigned==config['publishedfileid']
        result={'project_version':config['project_version'],'source_commit':head,'workshop_id':assigned if assigned!='0' else None,
                'mod_id':'B47ANCEDDogmeat','appid':'108600','package_sha256':manifest['package_sha256'],
                'preupload_manifest_sha256':sha((stage/'release-manifest.json').read_bytes()),
                'steamcmd_exit_code':code,'verified_success':verified,'elapsed_seconds':round(time.time()-start,1),
                'G6':'NOT TESTED','G7':'BLOCKED / NOT TESTED','stable_G8':'BLOCKED','steam_desktop_restart':'NOT PERFORMED'}
        (stage/'publication-result.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8',newline='\n')
        # No login diagnostics, account name, credentials or full raw log in output.
        print(json.dumps(result,indent=2))
        if not verified:
            print('Upload failed/unconfirmed. Inspect private diagnostics and any assigned ID before retry; never repeat new-item creation blindly.')
            return 1
        print('VERIFIED SteamCMD upload. No Steam desktop restart performed.')
        return 0
    except (OSError,ValueError,KeyError,subprocess.CalledProcessError) as exc:
        print('Publication stopped: '+str(exc));return 1

if __name__=='__main__':sys.exit(main())
