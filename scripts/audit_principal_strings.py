"""Bounded read-only SteamID string/exposure inventory; never load game classes.

--collect uses javap as a file inspector and writes raw text only under ignored
scratch. Default checks the committed evidence/scope; --native rehashes its game
inputs and rebuilds the descriptor index. None of these modes authenticates a
player or turns a source observation into runtime proof.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
import zipfile
from inspect_class_api import inspect

ROOT = Path(__file__).resolve().parents[1]
LEDGER = ROOT / 'docs/native-principal-string-evidence.json'
CLASSES = (
    'zombie.Lua.LuaManager', 'zombie.Lua.LuaManager$GlobalObject', 'zombie.Lua.LuaManager$Exposer',
    'zombie.Lua.KahluaNumberConverter', 'zombie.Lua.KahluaNumberConverter$NumberToLuaConverter',
    'zombie.characters.IsoPlayer', 'zombie.characters.IsoLivingCharacter', 'zombie.characters.IsoGameCharacter',
    'zombie.characters.NetworkUser', 'zombie.characters.NetworkUsers',
    'zombie.characters.NetworkCharacterAI', 'zombie.characters.NetworkPlayerAI',
    'zombie.core.raknet.UdpConnection', 'zombie.core.znet.SteamUser', 'zombie.core.znet.SteamUtils',
    'zombie.core.znet.SteamFriend', 'zombie.network.GameServer', 'zombie.network.Server',
    'zombie.network.packets.RequestNetworkUsersPacket', 'zombie.network.packets.NetworkUsersPacket',
    'zombie.savefile.ServerPlayerDB', 'se.krka.kahlua.integration.expose.ReturnValues',
    'se.krka.kahlua.integration.expose.LuaJavaClassExposer',
    'se.krka.kahlua.converter.KahluaConverterManager',
)
LUA = ('media/lua/client/ISUI/AdminPanel/ISUsersList.lua',)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def descriptor_index(archive):
    strings, receivers, references = [], [], []
    for path in sorted(archive.namelist()):
        if not path.startswith('zombie/') or not path.endswith('.class'):
            continue
        raw = archive.read(path)
        if b'zombie/characters/NetworkUsers' in raw:
            references.append(path)
        if not any(s in raw for s in (b'team', b'core/raknet/UdpConnection',
                                     b'savefile/ServerPlayerDB', b'characters/NetworkUser')):
            continue
        members = inspect(raw)
        for method in members['public_methods']:
            name, descriptor = method['name'], method['descriptor']
            if 'steam' in name.lower() and descriptor.endswith('Ljava/lang/String;'):
                strings.append({'path': path, 'name': name, 'descriptor': descriptor})
            if descriptor.endswith(('Lzombie/core/raknet/UdpConnection;',
                                    'Lzombie/savefile/ServerPlayerDB;', 'Lzombie/characters/NetworkUser;')):
                receivers.append({'path': path, 'kind': 'method', 'name': name, 'descriptor': descriptor})
        for field in members['public_fields']:
            if field['descriptor'] in ('Lzombie/core/raknet/UdpConnection;',
                                       'Lzombie/savefile/ServerPlayerDB;', 'Lzombie/characters/NetworkUser;'):
                receivers.append({'path': path, 'kind': 'field', 'name': field['name'],
                                  'descriptor': field['descriptor']})
    return {'steam_named_public_string_methods': strings,
            'public_connection_or_identity_receivers': receivers, 'network_users_referencing_classes': references,
            'scope': 'Packaged zombie public descriptors and literal references only; not complete call graph, Lua exposure or runtime proof'}


def collect(game, javap, scratch):
    scratch = scratch.resolve()
    if not scratch.is_relative_to(ROOT / '.m0r-local'):
        raise ValueError('Raw inspection output must remain beneath repository .m0r-local')
    scratch.mkdir(parents=True, exist_ok=True)
    inputs = []
    jar = game / 'projectzomboid.jar'
    with zipfile.ZipFile(jar) as archive:
        index = descriptor_index(archive)
        for cls in CLASSES:
            path = cls.replace('.', '/') + '.class'
            raw = archive.read(path)
            inputs.append({'container': 'projectzomboid.jar', 'path': path, 'sha256': sha(raw), 'bytes': len(raw)})
            output = subprocess.check_output([str(javap), '-c', '-p', '-classpath', str(jar), cls]).decode('cp1252')
            (scratch / (cls + '.txt')).write_text(output, encoding='utf-8', newline='\n')
            if cls == 'zombie.Lua.LuaManager$Exposer':
                exposed = sorted(set(re.findall(
                    r'// class ([\w/$]+)\s+\d+: invokevirtual[^\n]+// Method setExposed:', output)))
    for path in LUA:
        raw = (game / path).read_bytes()
        inputs.append({'container': 'game-root', 'path': path, 'sha256': sha(raw), 'bytes': len(raw)})
    relevant = ('zombie/characters/NetworkUser', 'zombie/characters/NetworkUsers',
                'zombie/characters/IsoGameCharacter', 'zombie/characters/IsoPlayer',
                'zombie/core/raknet/UdpConnection', 'zombie/network/GameServer',
                'zombie/savefile/ServerPlayerDB', 'zombie/core/znet/SteamUtils',
                'zombie/core/znet/SteamUser', 'zombie/core/znet/SteamFriend')
    return {'jar_sha256': sha(jar.read_bytes()), 'inputs': inputs, 'descriptor_index': index,
            'explicit_exposure_for_candidates': {cls: cls in exposed for cls in relevant},
            'exposure_scope': 'Literal class then setExposed calls in packaged LuaManager.Exposer; not a universal exposure proof'}


def check():
    d = json.loads(LEDGER.read_text(encoding='utf-8'))
    errors = []
    if d['project_version'] != (ROOT / 'VERSION').read_text().strip():
        errors.append('Principal audit version differs')
    if d['status'] != 'BLOCKED_NO_VERIFIED_LOSSLESS_SERVER_PATH' or d['runtime_status'] != 'NOT TESTED':
        errors.append('Principal source/runtime disposition needs review')
    for key in ('ownership_enabled', 'live_task_control_enabled', 'principal_adapter_installed', 'reflection_bypass_used'):
        if d.get(key) is not False:
            errors.append('Principal proof boundary differs: ' + key)
    if d['D1'] != 'BLOCKED' or d['G6'] != 'NOT TESTED' or d['G7'] != 'BLOCKED / NOT TESTED' or d['G8'] != 'BLOCKED':
        errors.append('Principal/runtime gate overclaim')
    prior = json.loads((ROOT / 'docs/database-authority-proof-evidence.json').read_text(encoding='utf-8'))
    for group in ('production_sources', 'production_metadata', 'historical_manifests'):
        for path, expected in prior[group].items():
            from validate_database_authority_proof import baseline_bytes
            if sha(baseline_bytes(path,(ROOT / path).read_bytes())) != expected:
                errors.append('Source/evidence applicability changed: ' + path)
    if [c['id'] for c in d['candidates']] != [f'S{i:02}' for i in range(1, 10)]:
        errors.append('Incomplete/duplicate principal candidate disposition')
    return d, errors


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--collect', action='store_true')
    parser.add_argument('--native', action='store_true')
    parser.add_argument('--game-root', type=Path)
    parser.add_argument('--javap', type=Path)
    parser.add_argument('--scratch', type=Path)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    if args.collect:
        if not all((args.game_root, args.javap, args.scratch, args.output)):
            parser.error('--collect requires --game-root, --javap, --scratch and --output')
        result = collect(args.game_root, args.javap, args.scratch)
        args.output.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8', newline='\n')
        print(json.dumps({'status': 'SOURCE INVENTORY ONLY', 'inputs': len(result['inputs']),
                          'string_candidates': len(result['descriptor_index']['steam_named_public_string_methods'])}))
        return 0
    d, errors = check()
    checked = 0
    if args.native:
        if not args.game_root:
            parser.error('--native requires --game-root')
        jar = args.game_root / 'projectzomboid.jar'
        if sha(jar.read_bytes()) != d['jar_sha256']:
            errors.append('Packaged audit JAR changed')
        with zipfile.ZipFile(jar) as archive:
            for item in d['inputs']:
                path = Path(item['path'])
                if path.is_absolute() or '..' in path.parts or item['container'] not in ('projectzomboid.jar', 'game-root'):
                    errors.append('Invalid principal source inventory path/container')
                    continue
                checked += 1
                raw = archive.read(item['path']) if item['container'] == 'projectzomboid.jar' else (args.game_root / item['path']).read_bytes()
                if sha(raw) != item['sha256']:
                    errors.append('Principal source changed: ' + item['path'])
            if descriptor_index(archive) != d['descriptor_index']:
                errors.append('Principal descriptor/reference inventory changed')
    print(json.dumps({'status': 'FAIL' if errors else 'SOURCE AUDIT CONSISTENT', 'errors': errors,
                      'inputs_rehashed': checked, 'D1': d['D1'], 'runtime_status': d['runtime_status'],
                      'effective_runtime': 'UNKNOWN / BASELINE_DRIFT; matching packaged evidence is not runtime validation',
                      'G6': d['G6'], 'G7': d['G7'], 'G8': d['G8']}, indent=2))
    return bool(errors)


if __name__ == '__main__':
    sys.exit(main())
