"""Read-only root-account route inventory. Does not load or execute game classes."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
import zipfile

from inspect_class_api import inspect
from audit_server_accounts import check as check_accounts

ROOT = Path(__file__).resolve().parents[1]
LEDGER = ROOT / 'docs/native-account-binding-evidence.json'
CLASSES = (
    'zombie.network.GameServer', 'zombie.network.GameClient', 'zombie.chat.ChatUtility',
    'zombie.core.raknet.UdpConnection', 'zombie.core.raknet.UdpEngine',
    'zombie.characters.IsoPlayer', 'zombie.characters.IsoGameCharacter', 'zombie.characters.IsoZombie',
    'zombie.characters.animals.IsoAnimal', 'zombie.characters.component.NetworkZombieComponent',
    'zombie.popman.Ownership', 'zombie.network.statistics.data.NetworkStatistic',
    'zombie.network.statistics.data.Statistic', 'zombie.network.statistics.StatusManager',
    'zombie.Lua.LuaManager$GlobalObject', 'zombie.Lua.LuaManager$Exposer',
    'se.krka.kahlua.integration.expose.LuaJavaClassExposer',
)
TARGETS = ('Lzombie/core/raknet/UdpConnection;', 'Lzombie/network/IConnection;',
           'Lzombie/network/GameServer;', 'Lzombie/core/raknet/UdpEngine;')


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def descriptor_index(archive):
    result = []
    for path in sorted(archive.namelist()):
        if not path.startswith('zombie/') or not path.endswith('.class'):
            continue
        raw = archive.read(path)
        if not any(t[1:-1].encode() in raw for t in TARGETS):
            continue
        members = inspect(raw)
        for kind, key in (('method', 'public_methods'), ('field', 'public_fields')):
            for member in members[key]:
                descriptor = member['descriptor']
                if any(descriptor.endswith(t) if kind == 'method' else descriptor == t for t in TARGETS):
                    result.append({'path': path, 'kind': kind, 'name': member['name'], 'descriptor': descriptor})
    return result


def collect(game, javap, scratch):
    if not scratch.resolve().is_relative_to(ROOT / '.m0r-local'):
        raise ValueError('Raw output must remain in ignored .m0r-local')
    scratch.mkdir(parents=True, exist_ok=True)
    jar = game / 'projectzomboid.jar'
    inputs = []
    with zipfile.ZipFile(jar) as archive:
        index = descriptor_index(archive)
        for cls in CLASSES:
            path = cls.replace('.', '/') + '.class'
            raw = archive.read(path)
            inputs.append({'path': path, 'sha256': sha(raw), 'bytes': len(raw)})
            output = subprocess.check_output([str(javap), '-c', '-p', '-classpath', str(jar), cls])
            output = output.decode('cp1252').replace('\r\n', '\n')
            (scratch / (cls + '.txt')).write_text(output, encoding='utf-8', newline='\n')
            if cls == 'zombie.Lua.LuaManager$Exposer':
                exposed = set(re.findall(r'// class ([\w/$]+)\s+\d+: invokevirtual[^\n]+// Method setExposed:', output))
    candidates = ('zombie.network.GameServer', 'zombie.network.GameClient', 'zombie.chat.ChatUtility',
                  'zombie.core.raknet.UdpConnection', 'zombie.core.raknet.UdpEngine',
                  'zombie.characters.IsoPlayer', 'zombie.characters.IsoZombie', 'zombie.characters.animals.IsoAnimal')
    return {'jar_sha256': sha(jar.read_bytes()), 'inputs': inputs, 'descriptor_index': index,
            'literal_explicit_exposure': {c: c.replace('.', '/') in exposed for c in candidates},
            'scope': 'Direct public return/field descriptors; excludes generic collection contents, arbitrary object graphs, private/reflection routes and runtime dispatch. Explicit exposure is literal setExposed membership only.'}


def dedicated_observation(server):
    base = server / 'java'
    jar = base / 'projectzomboid.jar'
    inputs = []
    with zipfile.ZipFile(jar) as archive:
        for cls in CLASSES:
            path = cls.replace('.', '/') + '.class'
            loose = base / path
            inputs.append({'path': path, 'packaged_sha256': sha(archive.read(path)),
                           'loose_sha256': sha(loose.read_bytes()) if loose.exists() else None})
    return {'jar_sha256': sha(jar.read_bytes()), 'inputs': inputs}


def check():
    data = json.loads(LEDGER.read_text(encoding='utf-8'))
    errors = check_accounts()[1]
    if data['project_version'] != (ROOT / 'VERSION').read_text().strip():
        errors.append('Account binding research version differs')
    if data['status'] != 'BLOCKED_NO_VERIFIED_LUA_ROOT_ACCOUNT_ROUTE' or data['runtime_status'] != 'NOT TESTED':
        errors.append('Root binding disposition requires evidence review')
    for key in ('provider_adopted', 'ownership_enabled', 'live_task_control_enabled', 'runtime_probe_executed',
                'account_incarnation_proven', 'automatic_continuity_proven'):
        if data.get(key) is not False:
            errors.append('Unreviewed root binding claim: ' + key)
    if len(data['inputs']) != len(CLASSES) or {x['path'] for x in data['inputs']} != {c.replace('.', '/') + '.class' for c in CLASSES}:
        errors.append('Root account input inventory differs')
    if [v['id'] for v in data['findings']] != [f'B{i:02}' for i in range(1, 9)]:
        errors.append('Incomplete/duplicate root binding finding')
    expected_probes = {p.relative_to(ROOT).as_posix() for p in (ROOT / 'tests/runtime/account_binding').rglob('*.lua')}
    if len(expected_probes) != 3 or set(data['probe_sources']) != expected_probes:
        errors.append('Disposable probe source inventory differs')
    for path, expected in data['probe_sources'].items():
        relative = Path(path)
        if relative.is_absolute() or '..' in relative.parts or not path.startswith('tests/runtime/account_binding/'):
            errors.append('Unsafe probe source path'); continue
        if sha((ROOT / relative).read_bytes().replace(b'\r\n', b'\n')) != expected:
            errors.append('Probe applicability changed: ' + path)
    if data['G7'] != 'BLOCKED / NOT TESTED' or data['G8'] != 'BLOCKED':
        errors.append('Offline probe work is not dedicated runtime proof')
    policy = data['probe_contract']
    if (policy['read_only'] is not True or policy['auto_requests'] is not False or policy['writes_files'] is not False
            or policy['default_assembly_includes_probe'] is not False):
        errors.append('Probe scope/isolation claim requires review')
    if data['dedicated_layout_observation']['runtime_baseline_proven'] is not False:
        errors.append('Selected dedicated hashes are not complete launch/runtime proof')
    return data, errors


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--collect', action='store_true')
    parser.add_argument('--native', action='store_true')
    parser.add_argument('--game-root', type=Path)
    parser.add_argument('--dedicated-root', type=Path, help='Recheck selected java/ layout fingerprints; not full launch provenance')
    parser.add_argument('--javap', type=Path)
    parser.add_argument('--scratch', type=Path)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    if args.collect:
        if not all((args.game_root, args.javap, args.scratch, args.output)):
            parser.error('--collect needs --game-root, --javap, --scratch and --output')
        if not args.output.resolve().is_relative_to(ROOT / '.m0r-local'):
            parser.error('Collection output must remain in ignored .m0r-local')
        data = collect(args.game_root, args.javap, args.scratch)
        args.output.write_text(json.dumps(data, indent=2) + '\n', encoding='utf-8', newline='\n')
        print(json.dumps({'status': 'SOURCE INVENTORY ONLY', 'inputs': len(data['inputs']),
                          'direct_public_candidates': len(data['descriptor_index'])}))
        return 0
    data, errors = check()
    if args.native:
        if not args.game_root:
            parser.error('--native needs --game-root')
        jar = args.game_root / 'projectzomboid.jar'
        if sha(jar.read_bytes()) != data['jar_sha256']:
            errors.append('Packaged binding audit JAR changed')
        with zipfile.ZipFile(jar) as archive:
            for item in data['inputs']:
                if sha(archive.read(item['path'])) != item['sha256']:
                    errors.append('Binding source changed: ' + item['path'])
            if descriptor_index(archive) != data['descriptor_index']:
                errors.append('Public direct connection descriptor index changed')
    if args.dedicated_root:
        if dedicated_observation(args.dedicated_root) != data['dedicated_layout_observation']['fingerprints']:
            errors.append('Selected dedicated package/loose observations changed')
    print(json.dumps({'status': 'FAIL' if errors else 'BINDING RESEARCH CONSISTENT', 'errors': errors,
                      'runtime_status': data['runtime_status'], 'root_account_binding': 'BLOCKED',
                      'dedicated_selected_inputs_rechecked': len(CLASSES) if args.dedicated_root else 0,
                      'effective_runtime': 'UNKNOWN / BASELINE_DRIFT', 'G7': data['G7'], 'G8': data['G8']}, indent=2))
    return bool(errors)


if __name__ == '__main__':
    sys.exit(main())
