"""Read-only vanilla publication target audit; never certifies a modified runtime."""
from pathlib import Path
import argparse, hashlib, json, re, sys, zipfile

ROOT = Path(__file__).resolve().parents[1]
LEDGER = 'docs/database-authority-proof-evidence.json'
CHANGED = ('zombie/GameWindow.class','zombie/iso/IsoWorld.class','zombie/Lua/LuaEventManager.class',
           'zombie/gameStates/GameLoadingState.class','zombie/characters/animals/IsoAnimal.class')


def sha(data):
    return hashlib.sha256(data).hexdigest()


def review_input(item, archive, game, observed):
    """Historical environment observations never substitute for packaged API proof."""
    path = item['path']
    if Path(path).is_absolute() or '..' in path.replace('\\','/').split('/') or ':' in path:
        raise ValueError('Unsafe evidence path')
    container = item.get('container', item.get('kind', 'projectzomboid.jar'))
    if container in ('projectzomboid.jar', 'jar_entry'):
        actual = sha(archive.read(path))
        if actual != item['sha256']:
            raise ValueError('Vanilla packaged input changed: '+path)
        return 'packaged'
    if container not in ('game-root','loose','file'):
        raise ValueError('Unknown evidence container: '+container)
    raw = (game/path).read_bytes()
    if path.endswith('.class'):
        # Only separately recorded/inspected overrides can be classified as known
        # environment observations. Their packaged counterparts must also match.
        record = observed.get(path)
        if record is None or sha(raw) != record['current_loose_sha256']:
            raise ValueError('Unreviewed loose override: '+path)
        if sha(archive.read(path)) != record['packaged_sha256']:
            raise ValueError('Override packaged counterpart changed: '+path)
        return 'known_modified_environment'
    if sha(raw) != item['sha256']:
        raise ValueError('Vanilla loose input changed: '+path)
    return 'vanilla_file'


def audit(game, root=ROOT):
    root, game = Path(root), Path(game)
    proof = json.loads((root/LEDGER).read_text(encoding='utf-8'))
    errors = []
    observed = {x['path']:x for x in proof['drift']}
    counts = {'packaged':0,'vanilla_file':0,'known_modified_environment':0}
    records = []
    jar = game/'projectzomboid.jar'
    if sha(jar.read_bytes()) != proof['jar_sha256']:
        errors.append('Vanilla JAR changed')
    build_text = (game.parent.parent/'appmanifest_108600.acf').read_text(encoding='utf-8')
    build = re.search(r'"buildid"\s+"(\d+)"',build_text)
    if not build or build[1] != proof['steam_build']:
        errors.append('Steam build differs from recorded target')
    for path, expected in proof['production_sources'].items():
        if sha((root/path).read_bytes().replace(b'\r\n',b'\n')) != expected:
            errors.append('Diagnostic runtime changed since authority review: '+path)
    inventory = json.loads((root/'source-inventory.json').read_text(encoding='utf-8'))
    admission = inventory['native_admission_guard']
    if admission['ownership_ready'] is not False or admission['admit_implemented'] is not False:
        errors.append('Ownership/admission enablement requires a new authority review')
    if proof['decision'] != 'NO-GO' or proof['ownership_enabled'] or proof['live_task_control_enabled']:
        errors.append('Historical authority NO-GO must remain intact')
    manifests = sorted((root/'docs').glob('native-*-evidence.json'))
    manifests += [root/'docs/contracts/native_evidence.json', root/LEDGER]
    with zipfile.ZipFile(jar) as archive:
        for file in manifests:
            data=json.loads(file.read_text(encoding='utf-8'))
            for item in data.get('inputs',data.get('sources',[])):
                if not isinstance(item,dict) or 'sha256' not in item or 'path' not in item:
                    continue
                try:
                    kind=review_input(item,archive,game,observed)
                    counts[kind]+=1
                except (OSError,KeyError,ValueError) as exc:
                    errors.append(file.name+': '+str(exc))
        for path in CHANGED:
            item=observed[path]
            actual=sha((game/path).read_bytes())
            packaged=sha(archive.read(path))
            if actual != item['current_loose_sha256'] or packaged != item['packaged_sha256']:
                errors.append('Reviewed override observation changed: '+path)
            records.append({'path':path,'loose_sha256':actual,'packaged_sha256':packaged,
                            'matches_newer_observation':actual==item['current_loose_sha256'],
                            'normalized_method_differences':item['changed_normalized_method_count'],
                            'runtime_effect':'UNKNOWN; modified installation unsupported'})
    return {'status':'FAIL' if errors else 'VANILLA PUBLICATION SOURCE PASS',
            'version':(root/'VERSION').read_text().strip(),'target':'vanilla Build 42.21 / Steam '+proof['steam_build'],
            'jar_sha256':sha(jar.read_bytes()),'counts':counts,'overrides':records,
            'environment':'Read-only bytes/source audit; game code never executed',
            'local_modified_installation':'BLOCKED / NOT CERTIFIED',
            'scope':'Guarded default-off raccoon diagnostic distribution only; no ownership/live tasks',
            'G6':'NOT TESTED','G7':'BLOCKED / NOT TESTED','stable_G8':'BLOCKED','errors':errors}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--game-root',type=Path,required=True)
    parser.add_argument('--output',type=Path)
    args=parser.parse_args()
    try: result=audit(args.game_root)
    except (OSError,ValueError,KeyError,zipfile.BadZipFile) as exc:
        print('FAIL: '+str(exc));return 1
    text=json.dumps(result,indent=2)+'\n'
    if args.output:
        if args.output.exists(): raise ValueError('Refusing to overwrite prior evidence')
        args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(text,encoding='utf-8',newline='\n')
    print(text)
    return bool(result['errors'])

if __name__=='__main__': sys.exit(main())
