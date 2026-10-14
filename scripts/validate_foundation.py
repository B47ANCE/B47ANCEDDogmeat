"""Read-only source, localization, frozen-art and optional native-evidence checks."""
from pathlib import Path
import argparse
import hashlib
import json
import re
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[1]
DOMAIN = {f'src/domain/B47Dog/{name}.lua' for name in
          ('Access', 'Guard', 'Ownership', 'Projection', 'Codec', 'Identity', 'Snapshot', 'PrivateStore')}
NATIVE = {f'src/native/B47Dog/{name}.lua' for name in
          ('PZCache', 'NativeAnimal', 'NativeSession', 'NativeCheckpoint', 'NativeRuntime')}
MODULES = DOMAIN | NATIVE


def no_duplicates(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError('Duplicate JSON key: ' + key)
        result[key] = value
    return result


def read(path):
    return json.loads(path.read_text(encoding='utf-8'), object_pairs_hook=no_duplicates)


def check_source():
    errors = []
    inventory = read(ROOT / 'source-inventory.json')
    catalog = read(ROOT / 'docs/contracts/localization_keys.json')
    if set(inventory['authoritative_lua']) != MODULES:
        errors.append('Source inventory differs from bounded feature slice')
    if inventory['languages'] != catalog['languages'] or inventory['localization_root'] != 'src/localization':
        errors.append('Localization source/language declaration differs from contract')
    if inventory['runtime_registration'] is not None or inventory['workshop_id'] is not None:
        errors.append('Unexpected runtime registration/Workshop identity in unregistered prototype')
    adapter = inventory.get('native_event_adapter', {})
    if (adapter.get('entry') != 'B47Dog/NativeRuntime.install' or adapter.get('automatic_bootstrap') is not None
            or adapter.get('events') != ['OnInitGlobalModData', 'OnServerStarted', 'OnCharacterDeath']):
        errors.append('Explicit native event adapter inventory differs')
    allowed = MODULES | {f'src/localization/{lang}/{category}.json'
                        for lang in catalog['languages'] for category in ('UI', 'Sandbox')}
    found = {p.relative_to(ROOT).as_posix() for p in (ROOT / 'src').rglob('*') if p.is_file()}
    if found != allowed:
        errors.append('Unexpected/missing source paths: ' + str(sorted(found ^ allowed)))
    if len({p.casefold() for p in found}) != len(found):
        errors.append('Source case collision')
    for relative in MODULES:
        path = ROOT / relative
        if not path.is_file():
            continue
        code = path.read_text(encoding='utf-8')
        for module in re.findall(r'\brequire\s*\(?\s*["\']([^"\']+)["\']', code):
            candidates = {'src/domain/' + module + '.lua', 'src/native/' + module + '.lua'} & MODULES
            if len(candidates) != 1 or (relative in DOMAIN and not candidates <= DOMAIN):
                errors.append('Unknown/case-wrong require in ' + relative + ': ' + module)
        # Deliberately bounded source checks, not a general Lua security scanner.
        if re.search(r'\b(?:SandboxVars|io|os|debug|luajava)\s*[.:\[]|'
                     r'\b(?:sendClientCommand|sendServerCommand|getModFileWriter|addAnimal|loadstring|dofile|loadfile)\s*\(', code):
            errors.append('Unexpected runtime registration, write or dynamic execution: ' + relative)
        if re.search(r'\bEvents\s*[.:\[]', code) and relative != 'src/native/B47Dog/NativeRuntime.lua':
            errors.append('Event API outside explicit runtime adapter: ' + relative)
        if re.search(r'\bModData\s*[.:\[]', code) and relative != 'src/native/B47Dog/NativeCheckpoint.lua':
            errors.append('Native anchor API outside checkpoint adapter: ' + relative)
        if relative in DOMAIN and re.search(r'\b(?:IsoAnimal)\s*[.:\[]|'
                     r'\b(?:getFileWriter|getFileReader|getCurrentSaveName|getRandomUUID|instanceof|isServer|isClient)\b', code):
            errors.append('Engine/storage/dynamic execution outside approved domain: ' + relative)
        if relative in NATIVE:
            allowed_api = {'isServer', 'isClient', 'getCurrentSaveName', 'getFileReader', 'getFileWriter',
                           'instanceof', 'getRandomUUID', 'Events', 'ModData', 'getCell'}
            if not set(re.findall(r'\bapi\.([A-Za-z_][A-Za-z0-9_]*)', code)) <= allowed_api:
                errors.append('Unreviewed native API reference: ' + relative)
        if relative == 'src/native/B47Dog/NativeRuntime.lua':
            events = set(re.findall(r'api\.Events\.([A-Za-z_][A-Za-z0-9_]*)\.Add\(', code))
            if events != {'OnInitGlobalModData', 'OnServerStarted', 'OnCharacterDeath'}:
                errors.append('Native adapter event registrations changed')
        if relative == 'src/native/B47Dog/NativeCheckpoint.lua':
            if set(re.findall(r'api\.ModData\.([A-Za-z_][A-Za-z0-9_]*)', code)) != {'get'}:
                errors.append('Unreviewed anchor creation/import API')
    for forbidden in ('dist', 'Contents', 'media', 'mod.info'):
        if (ROOT / forbidden).exists():
            errors.append('Unexpected runtime/distribution root: ' + forbidden)
    return errors


def check_native(game_root):
    errors, checked = [], 0
    inputs = []
    for name in ('native-persistence-evidence.json', 'native-pairing-evidence.json'):
        inputs.extend(read(ROOT / 'docs' / name)['inputs'])
    with zipfile.ZipFile(game_root / 'projectzomboid.jar') as jar:
        for item in inputs:
            relative = Path(item['path'])
            if relative.is_absolute() or '..' in relative.parts:
                errors.append('Unsafe native evidence path')
                continue
            if item['container'] == 'projectzomboid.jar':
                actual = hashlib.sha256(jar.read(item['path'])).hexdigest()
            elif item['container'] == 'game-root':
                digest = hashlib.sha256()
                with (game_root / relative).open('rb') as stream:
                    for block in iter(lambda: stream.read(1024 * 1024), b''):
                        digest.update(block)
                actual = digest.hexdigest()
            else:
                errors.append('Unknown native evidence container')
                continue
            checked += 1
            if actual != item['sha256']:
                errors.append('Native input changed: ' + item['path'])
    return errors, checked


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--native', action='store_true', help='Rehash installed inputs without executing game code')
    parser.add_argument('--game-root', type=Path)
    args = parser.parse_args()
    if args.native and not args.game_root:
        parser.error('--native requires --game-root')
    errors = check_source()
    checked = 0
    if args.native:
        native_errors, checked = check_native(args.game_root)
        errors.extend(native_errors)
    inventory = read(ROOT / 'source-inventory.json')
    catalog = read(ROOT / 'docs/contracts/localization_keys.json')['english_fallback']
    translations = 0
    for language in inventory['languages']:
        for category, keys in inventory['localization_keys'].items():
            if category not in ('UI', 'Sandbox') or len(set(keys)) != len(keys):
                errors.append('Invalid localization category/key inventory')
                continue
            relative = f'src/localization/{language}/{category}.json'
            data = read(ROOT / relative)
            expected = {key: catalog[key] for key in keys}
            if data != expected:
                errors.append('Fallback key/value parity differs: ' + relative)
            translations += len(data)
    # Every action/refusal emitted today has an explicit prepared localized label.
    ui_keys = set(inventory['localization_keys']['UI'])
    for action in ('InspectDog', 'ClaimDog', 'RenameDog', 'GrantHandler', 'RevokeHandler', 'TransferDog'):
        if 'UI_B47ANCEDDogTraining_Action_' + action not in ui_keys:
            errors.append('Missing action label: ' + action)
    for reason in ('Unauthorized', 'Unavailable', 'Stale', 'Invalid', 'Protocol', 'Capability', 'Recovery'):
        if 'UI_B47ANCEDDogTraining_Reason_' + reason not in ui_keys:
            errors.append('Missing refusal label: ' + reason)
    art = read(ROOT / 'docs/art-checkpoint.json')
    for relative, expected in art['files'].items():
        if not relative.startswith('art/german_shepherd/') or '..' in Path(relative).parts:
            errors.append('Invalid frozen art path')
            continue
        data = (ROOT / relative).read_bytes()
        if Path(relative).suffix in ('.md', '.json', '.py'):
            data = data.replace(b'\r\n', b'\n')
        if hashlib.sha256(data).hexdigest() != expected:
            errors.append('Frozen art changed: ' + relative)
    output = {'status': 'STATIC PASS' if not errors else 'FAIL',
              'project_version': (ROOT / 'VERSION').read_text(encoding='utf-8').strip(),
              'lua_modules': len(MODULES), 'pure_domain_modules': len(DOMAIN), 'native_modules': len(NATIVE),
              'native_inputs_rehashed': checked, 'languages': len(inventory['languages']),
              'fallback_entries': translations, 'frozen_art_files': len(art['files']),
              'environment': 'Offline source/data checks; no native loading or gameplay',
              'errors': errors, 'G6': 'NOT TESTED', 'G7': 'BLOCKED / NOT TESTED', 'G8': 'BLOCKED'}
    print(json.dumps(output, indent=2))
    return bool(errors)


if __name__ == '__main__':
    try:
        sys.exit(main())
    except (OSError, ValueError, KeyError) as exc:
        print('FAIL: ' + str(exc))
        sys.exit(1)
