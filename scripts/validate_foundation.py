"""Read-only source, localization, frozen-art and optional native-evidence checks."""
from pathlib import Path
import argparse
import hashlib
import json
import re
import sys
import zipfile
from build_loadable import assemble
import tempfile
from validate_database_design import check as check_database_design
from validate_database_authority_proof import check as check_database_authority_proof
from audit_principal_strings import check as check_principal_strings
from audit_server_accounts import check as check_server_accounts
from audit_account_binding import check as check_account_binding

ROOT = Path(__file__).resolve().parents[1]
DOMAIN = {f'src/domain/B47Dog/{name}.lua' for name in
          ('Access', 'Guard', 'Ownership', 'Projection', 'Codec', 'Identity', 'Snapshot', 'PrivateStore', 'AdmissionPolicy')}
NATIVE = {f'src/native/B47Dog/{name}.lua' for name in
          ('PZCache', 'NativeAnimal', 'NativeSession', 'NativeCheckpoint', 'NativeRuntime',
           'NativeAuthority', 'NativeProvision', 'NativeTestService', 'NativeAdmissionGuard')}
BOOTSTRAP = {'src/bootstrap/shared/B47DogRegistration.lua','src/bootstrap/server/B47DogBootstrap.lua',
             'src/bootstrap/client/B47DogTestMenu.lua','src/bootstrap/shared/B47ShepherdRegistration.lua',
             'src/bootstrap/client/B47ShepherdTailHealth.lua'}
MODULES = DOMAIN | NATIVE | BOOTSTRAP
VANILLA_REQUIRES = {'Definitions/animal/RaccoonDefinitions','Definitions/animal/AnimalAvatarDefinition',
                    'Definitions/animal/AnimalPartsDefinitions','ISUI/ISModalDialog'}
VANILLA_REQUIRES |= {'TimedActions/Animals/' + name for name in
                     ('ISPickupAnimal','ISAddAnimalInTrailer','ISRemoveAnimalFromTrailer',
                      'ISAttachAnimalToPlayer','ISAttachAnimalToTree','ISPutAnimalInHutch','ISHutchGrabAnimal')}
VANILLA_REQUIRES |= {'TimedActions/ISDropWorldItemAction','TimedActions/ISDropVehicleItemAction'}


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
    errors = (check_database_design() + check_database_authority_proof()
              + check_principal_strings()[1] + check_server_accounts()[1] + check_account_binding()[1])
    inventory = read(ROOT / 'source-inventory.json')
    catalog = read(ROOT / 'docs/contracts/localization_keys.json')
    if set(inventory['authoritative_lua']) != MODULES:
        errors.append('Source inventory differs from bounded feature slice')
    if inventory['languages'] != catalog['languages'] or inventory['localization_root'] != 'src/localization':
        errors.append('Localization source/language declaration differs from contract')
    registration = inventory['runtime_registration']
    if registration.get('mod_id') != 'B47ANCEDDogmeat' or registration.get('native_type') != 'b47dogtest':
        errors.append('Unexpected runtime identity')
    from prepare_workshop import configuration
    try:
        configuration()
    except (ValueError, KeyError, OSError) as exc:
        errors.append('Workshop identity invalid: '+str(exc))
    adapter = inventory.get('native_event_adapter', {})
    if (adapter.get('entry') != 'B47Dog/NativeRuntime.install' or adapter.get('automatic_bootstrap') != 'src/bootstrap/server/B47DogBootstrap.lua'
            or adapter.get('events') != ['OnInitGlobalModData', 'OnServerStarted', 'OnGameStart', 'OnCharacterDeath']):
        errors.append('Explicit native event adapter inventory differs')
    admission = inventory.get('native_admission_guard', {})
    admission_actions = ['ISPickupAnimal','ISAddAnimalInTrailer','ISRemoveAnimalFromTrailer',
                         'ISAttachAnimalToPlayer','ISAttachAnimalToTree','ISPutAnimalInHutch',
                         'ISHutchGrabAnimal','ISDropWorldItemAction','ISDropVehicleItemAction']
    if (admission.get('entry') != 'B47Dog/NativeAdmissionGuard.install'
            or admission.get('guarded_actions') != admission_actions
            or admission.get('coverage') != 'LUA_ACTIONS_ONLY' or admission.get('ownership_ready') is not False
            or admission.get('central_policy') != 'B47Dog/AdmissionPolicy'
            or admission.get('runtime_decision_entry') != 'B47Dog/NativeRuntime.assessAdmission'
            or admission.get('admit_implemented') is not False):
        errors.append('Selected admission guard inventory/authority differs')
    continuity_docs = ('NATIVE_ADMISSION_COVERAGE', 'CANONICAL_IDENTITY_CONTRACT',
                       'PREVIOUS_SESSION_INTEGRITY', 'SERVER_ADMISSION_GUARD',
                       'LUA_ONLY_FEASIBILITY', 'ANIMAL_LIFECYCLE_MATRIX',
                       'GROWTH_IDENTITY_FEASIBILITY', 'MULTIPLAYER_OWNERSHIP_TEST_PLAN',
                       'BLOCKER_RESOLUTION_REPORT')
    for name in continuity_docs:
        if not (ROOT / 'docs' / (name + '.md')).is_file():
            errors.append('Missing native continuity deliverable: ' + name)
    option_a_docs = ('NATIVE_SAVE_LOAD_AUTHORITY_TRACE', 'EXCLUSIVE_ADMISSION_SEAM_ASSESSMENT',
                     'PREVIOUS_SESSION_AUTHENTICITY_PROOF', 'NATIVE_RECONSTRUCTION_PROVENANCE',
                     'LUA_ONLY_OWNERSHIP_PROTOTYPE', 'ADVERSARIAL_IDENTITY_TEST_RESULTS',
                     'DISPOSABLE_RUNTIME_TEST_PROCEDURE', 'OWNERSHIP_GO_NO_GO_DECISION')
    for name in option_a_docs:
        if not (ROOT / 'docs' / (name + '.md')).is_file():
            errors.append('Missing Option A deliverable: ' + name)
    authority_evidence = read(ROOT / 'docs/native-save-load-evidence.json')
    if (authority_evidence.get('decision') != 'NO-GO'
            or authority_evidence.get('positive_prototype_implemented') is not False
            or authority_evidence.get('ownership_enabled') is not False):
        errors.append('Option A authority disposition differs from reviewed evidence')
    for relative, expected in authority_evidence['project_sources_at_baseline'].items():
        path = Path(relative)
        if path.is_absolute() or '..' in path.parts or not relative.startswith('src/'):
            errors.append('Unsafe Option A baseline source path')
            continue
        actual = hashlib.sha256((ROOT / path).read_bytes().replace(b'\r\n', b'\n')).hexdigest()
        if actual != expected:
            errors.append('Option A source applicability requires review: ' + relative)
    construction = read(ROOT / 'docs/native-construction-index.json')
    sites = construction['direct_constructor_sites']
    if construction.get('scope') != 'DIRECT_NEW_ONLY_NOT_GRAPH_CLOSURE' or not sites:
        errors.append('Invalid constructor inventory scope')
    unique = set()
    for site in sites:
        key = (site['class'], site['method'], site['new_offset'])
        if key in unique or not isinstance(site['new_offset'], int) or site['new_offset'] < 0:
            errors.append('Invalid/duplicate constructor metadata')
        unique.add(key)
    guard_source = (ROOT/'src/native/B47Dog/NativeAdmissionGuard.lua').read_text(encoding='utf-8')
    if re.findall(r'\{name="([A-Za-z0-9_]+)",source=', guard_source) != admission_actions:
        errors.append('Selected admission hooks differ from declared contract')
    bootstrap_source = (ROOT/'src/bootstrap/server/B47DogBootstrap.lua').read_text(encoding='utf-8')
    for action in admission_actions:
        prefix = '' if action in ('ISDropWorldItemAction','ISDropVehicleItemAction') else 'Animals/'
        if 'require "TimedActions/' + prefix + action + '"' not in bootstrap_source:
            errors.append('Missing case-correct vanilla admission dependency: ' + action)
    allowed = MODULES | set(inventory['metadata_sources']) | {f'src/localization/{lang}/{category}.json'
                        for lang in catalog['languages'] for category in ('UI', 'Sandbox', 'IGUI')}
    allowed |= {x['source'] for x in inventory['runtime_assets'] if x['source'].startswith('src/')}
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
            if relative in BOOTSTRAP and module in VANILLA_REQUIRES:
                continue
            candidates = {'src/domain/' + module + '.lua', 'src/native/' + module + '.lua',
                          'src/bootstrap/shared/' + module + '.lua'} & MODULES
            if len(candidates) != 1 or (relative in DOMAIN and not candidates <= DOMAIN):
                errors.append('Unknown/case-wrong require in ' + relative + ': ' + module)
        # Deliberately bounded source checks, not a general Lua security scanner.
        if re.search(r'\b(?:io|os|debug|luajava)\s*[.:\[]|'
                     r'\b(?:getModFileWriter|loadstring|dofile|loadfile)\s*\(', code):
            errors.append('Unexpected runtime registration, write or dynamic execution: ' + relative)
        if re.search(r'\bEvents\s*[.:\[]', code) and relative not in BOOTSTRAP | {'src/native/B47Dog/NativeRuntime.lua'}:
            errors.append('Event API outside explicit runtime adapter: ' + relative)
        if re.search(r'\bModData\s*[.:\[]', code) and relative not in {'src/native/B47Dog/NativeCheckpoint.lua','src/native/B47Dog/NativeProvision.lua'}:
            errors.append('Native anchor API outside checkpoint adapter: ' + relative)
        if relative in DOMAIN and re.search(r'\b(?:IsoAnimal)\s*[.:\[]|'
                     r'\b(?:getFileWriter|getFileReader|getCurrentSaveName|getRandomUUID|instanceof|isServer|isClient)\b', code):
            errors.append('Engine/storage/dynamic execution outside approved domain: ' + relative)
        if relative in NATIVE:
            allowed_api = {'isServer', 'isClient', 'getCurrentSaveName', 'getFileReader', 'getFileWriter',
                           'instanceof', 'getRandomUUID', 'Events', 'ModData', 'getCell',
                           'B47DogSinglePlayer','cacheFileExists','AnimalDefinitions','addAnimal',
                           'SandboxVars','Capability','getTimestampMs'}
            if not set(re.findall(r'\bapi\.([A-Za-z_][A-Za-z0-9_]*)', code)) <= allowed_api:
                errors.append('Unreviewed native API reference: ' + relative)
        if relative == 'src/native/B47Dog/NativeRuntime.lua':
            events = set(re.findall(r'api\.Events\.([A-Za-z_][A-Za-z0-9_]*)\.Add\(', code))
            if events != {'OnInitGlobalModData', 'OnServerStarted', 'OnGameStart', 'OnCharacterDeath'}:
                errors.append('Native adapter event registrations changed')
        if relative == 'src/native/B47Dog/NativeCheckpoint.lua':
            if set(re.findall(r'api\.ModData\.([A-Za-z_][A-Za-z0-9_]*)', code)) != {'get'}:
                errors.append('Unreviewed anchor creation/import API')
        if relative == 'src/native/B47Dog/NativeProvision.lua':
            if set(re.findall(r'api\.ModData\.([A-Za-z_][A-Za-z0-9_]*)', code)) != {'get','create'}:
                errors.append('Unreviewed initializer anchor API')
        if relative in DOMAIN and re.search(r'\b(?:Events|ModData|SandboxVars|addAnimal|sendServerCommand|sendClientCommand)\b', code):
            errors.append('Native mutation/network API in pure domain')
    metadata=(ROOT/'src/metadata/mod.info').read_text(encoding='utf-8')
    if re.findall(r'^id=(.*)$',metadata,re.M)!=['B47ANCEDDogmeat'] or 'versionMin=42.21' not in metadata:
        errors.append('Loadable metadata differs from approved identity/baseline')
    option=read(ROOT/'src/metadata/runtime-options.json')['settings']
    if len(option)!=1 or option[0]['id']!='B47ANCEDDogmeat.PersistenceTestMode' or option[0]['default'] is not False or option[0]['server_authority'] is not True:
        errors.append('Runtime sandbox option contract differs')
    sandbox=(ROOT/'src/metadata/sandbox-options.txt').read_text(encoding='utf-8')
    if re.findall(r'option\s+([\w.]+)',sandbox)!=['B47ANCEDDogmeat.PersistenceTestMode','B47ANCEDDogmeat.TailHealthIndicator'] or 'default = false' not in sandbox:
        errors.append('Native sandbox source differs')
    with tempfile.TemporaryDirectory(prefix='b47dog-validate-') as temp:
        assemble(Path(temp)/'B47ANCEDDogmeat')
    for forbidden in ('dist', 'Contents', 'media', 'mod.info'):
        if (ROOT / forbidden).exists():
            errors.append('Unexpected runtime/distribution root: ' + forbidden)
    return errors


def check_native(game_root):
    errors, checked = [], 0
    inputs = []
    for name in ('native-persistence-evidence.json', 'native-pairing-evidence.json','native-bootstrap-evidence.json',
                 'native-identity-evidence.json','native-admission-evidence.json',
                 'native-continuity-evidence.json', 'native-save-load-evidence.json',
                 'native-database-redesign-evidence.json'):
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
            if category not in ('UI', 'Sandbox', 'IGUI') or len(set(keys)) != len(keys):
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
              'bootstrap_files':len(BOOTSTRAP),'loadable_source_parity':'PASS' if not errors else 'FAIL',
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
