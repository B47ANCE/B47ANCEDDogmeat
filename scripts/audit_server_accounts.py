"""Inspect vanilla account evidence as data; no PZ, DB or account API execution.

Default checks the research contract and unchanged production boundaries.
--native rehashes installed evidence only. --collect uses javap and stores raw
method inspection beneath ignored scratch. These checks never grant identity.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
import zipfile
from validate_database_authority_proof import check as check_previous_proof

ROOT = Path(__file__).resolve().parents[1]
LEDGER = ROOT / 'docs/native-account-identity-evidence.json'
CLASSES = (
    'zombie.network.GameServer', 'zombie.network.ServerWorldDatabase',
    'zombie.network.ServerWorldDatabase$LogonResult', 'zombie.network.ServerOptions',
    'zombie.network.packets.connection.LoginPacket', 'zombie.network.packets.connection.GoogleAuthPacket',
    'zombie.network.packets.connection.GoogleAuthRequestPacket',
    'zombie.network.packets.connection.ConnectPacket', 'zombie.network.packets.connection.ConnectCoopPacket',
    'zombie.network.packets.connection.ConnectedCoopPacket',
    'zombie.network.packets.NetworkUserActionPacket', 'zombie.core.raknet.UdpConnection',
    'zombie.characters.IsoPlayer', 'zombie.characters.IsoGameCharacter',
    'zombie.Lua.LuaManager$GlobalObject', 'zombie.Lua.LuaManager$Exposer',
    'se.krka.kahlua.integration.expose.LuaJavaClassExposer',
)
LUA = ('media/lua/server/ClientCommands.lua',)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def collect(game, javap, scratch):
    scratch = scratch.resolve()
    if not scratch.is_relative_to(ROOT / '.m0r-local'):
        raise ValueError('Raw inspection must remain under repository .m0r-local')
    scratch.mkdir(parents=True, exist_ok=True)
    jar = game / 'projectzomboid.jar'
    inputs = []
    with zipfile.ZipFile(jar) as archive:
        for cls in CLASSES:
            path = cls.replace('.', '/') + '.class'
            raw = archive.read(path)
            inputs.append({'container': 'projectzomboid.jar', 'path': path,
                           'sha256': sha(raw), 'bytes': len(raw)})
            text = subprocess.check_output([str(javap), '-c', '-p', '-classpath', str(jar), cls]).decode('cp1252')
            (scratch / (cls + '.txt')).write_text(text, encoding='utf-8', newline='\n')
        cls = 'zombie.network.packets.connection.ConnectCoopPacket'
        text = subprocess.check_output([str(javap), '-v', '-p', '-classpath', str(jar), cls]).decode('cp1252')
        (scratch / (cls + '-metadata.txt')).write_text(text, encoding='utf-8', newline='\n')
    for path in LUA:
        raw = (game / path).read_bytes()
        inputs.append({'container': 'game-root', 'path': path, 'sha256': sha(raw), 'bytes': len(raw)})
    manifest = (game.parent.parent / 'appmanifest_108600.acf').read_text(encoding='utf-8')
    build = re.search(r'"buildid"\s+"(\d+)"', manifest).group(1)
    return {'jar_sha256': sha(jar.read_bytes()), 'steam_build': build, 'inputs': inputs}


def check():
    d = json.loads(LEDGER.read_text(encoding='utf-8'))
    errors = check_previous_proof()
    if d['project_version'] != (ROOT / 'VERSION').read_text().strip():
        errors.append('Account research version differs')
    if d['status'] != 'DESIGN_FEASIBLE_AUTOMATIC_ACCOUNT_BINDING_BLOCKED' or d['runtime_status'] != 'NOT TESTED':
        errors.append('Account provider disposition needs review')
    for key in ('provider_adopted', 'runtime_adapter_installed', 'ownership_enabled',
                'live_task_control_enabled', 'automatic_incarnation_detection_proven',
                'callback_username_is_universal_account_id', 'leases_survive_restart', 'credential_material_stored'):
        if d.get(key) is not False:
            errors.append('Unsafe/unreviewed account provider claim: ' + key)
    if d['G6'] != 'NOT TESTED' or d['G7'] != 'BLOCKED / NOT TESTED' or d['G8'] != 'BLOCKED':
        errors.append('Account investigation is not runtime evidence')
    expected = {cls.replace('.', '/') + '.class' for cls in CLASSES} | set(LUA)
    if {v['path'] for v in d['inputs']} != expected or len(d['inputs']) != len(expected):
        errors.append('Account inspection inventory differs')
    if [v['id'] for v in d['claims']] != [f'A{i:02}' for i in range(1, 11)]:
        errors.append('Missing/duplicate account source finding')
    if [v['id'] for v in d['runtime_cases']] != [f'AC{i:02}' for i in range(1, 13)]:
        errors.append('Missing account runtime scenario')
    for case in d['runtime_cases']:
        if case['status'] != 'NOT TESTED':
            errors.append('Account runtime case promoted without evidence')
    policy = d['proposed_registry']
    if (policy['status'] != 'PROPOSAL_NOT_IMPLEMENTED' or policy['key'] != ['accountRealmId', 'principalId']
            or policy['auto_rebind_by_username'] is not False or policy['auto_migrate_legacy_owners'] is not False
            or policy['client_identity_accepted'] is not False or policy['native_account_binding_required'] is not True):
        errors.append('Unsafe account registry design')
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
        d = collect(args.game_root, args.javap, args.scratch)
        args.output.write_text(json.dumps(d, indent=2) + '\n', encoding='utf-8', newline='\n')
        print(json.dumps({'status': 'SOURCE COLLECTION ONLY', 'inputs': len(d['inputs']), 'steam_build': d['steam_build']}))
        return 0
    d, errors = check()
    checked = 0
    if args.native:
        if not args.game_root:
            parser.error('--native requires --game-root')
        jar = args.game_root / 'projectzomboid.jar'
        if sha(jar.read_bytes()) != d['jar_sha256']:
            errors.append('Packaged account source JAR changed')
        with zipfile.ZipFile(jar) as archive:
            for item in d['inputs']:
                path = Path(item['path'])
                if path.is_absolute() or '..' in path.parts or item['container'] not in ('projectzomboid.jar', 'game-root'):
                    errors.append('Unsafe account source path/container')
                    continue
                raw = archive.read(item['path']) if item['container'] == 'projectzomboid.jar' else (args.game_root / path).read_bytes()
                checked += 1
                if sha(raw) != item['sha256']:
                    errors.append('Account source changed: ' + item['path'])
    print(json.dumps({'status': 'FAIL' if errors else 'ACCOUNT RESEARCH CONSISTENT', 'errors': errors,
                      'inputs_rehashed': checked, 'provider_adopted': d['provider_adopted'],
                      'automatic_binding': 'BLOCKED; design only', 'runtime_status': d['runtime_status'],
                      'effective_runtime': 'UNKNOWN / BASELINE_DRIFT',
                      'G6': d['G6'], 'G7': d['G7'], 'G8': d['G8']}, indent=2))
    return bool(errors)


if __name__ == '__main__':
    sys.exit(main())
