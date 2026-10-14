"""Read-only source, localization and frozen-art checks for the offline feature slice."""
from pathlib import Path
import hashlib
import json
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
MODULES = {f'src/domain/B47Dog/{name}.lua' for name in ('Access', 'Guard', 'Ownership', 'Projection')}


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
        errors.append('Source inventory differs from bounded ownership slice')
    if inventory['languages'] != catalog['languages'] or inventory['localization_root'] != 'src/localization':
        errors.append('Localization source/language declaration differs from contract')
    if inventory['runtime_registration'] is not None or inventory['workshop_id'] is not None:
        errors.append('Unexpected native registration/Workshop identity in offline domain slice')
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
            if 'src/domain/' + module + '.lua' not in MODULES:
                errors.append('Unknown/case-wrong require in ' + relative + ': ' + module)
        # Deliberately small pure-domain boundary, not a general Lua security scanner.
        if re.search(r'\b(?:Events|ModData|SandboxVars|IsoAnimal|io|os|debug|luajava)\s*[.:\[]|'
                     r'\b(?:sendClientCommand|sendServerCommand|getFileWriter|getFileReader|addAnimal|loadstring|dofile|loadfile)\s*\(', code):
            errors.append('Engine/storage/dynamic execution outside approved domain: ' + relative)
    for forbidden in ('dist', 'Contents', 'media', 'mod.info'):
        if (ROOT / forbidden).exists():
            errors.append('Unexpected runtime/distribution root: ' + forbidden)
    return errors


def main():
    errors = check_source()
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
              'lua_modules': len(MODULES), 'languages': len(inventory['languages']),
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
