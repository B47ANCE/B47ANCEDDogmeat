"""Check proof scope/fingerprints; a matching drift observation is not runtime PASS."""
import argparse
import hashlib
import json
import re
from pathlib import Path
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[1]
PROOF_BASELINE_VERSION = '0.2.0-dev.7'
SHEPHERD_ADDITION = 'src/bootstrap/shared/B47ShepherdRegistration.lua'
TAIL_ADDITION = 'src/bootstrap/client/B47ShepherdTailHealth.lua'
TAIL_OPTION = b'''option B47ANCEDDogmeat.TailHealthIndicator
{
    type = boolean,
    default = true,
    page = B47ANCEDDogmeat,
    translation = B47ANCEDDogmeat_TailHealthIndicator,
}
'''

def baseline_bytes(relative, raw):
    """Permit only the current edition/version header, never new proof claims.

    Original expected hashes stay tied to source_baseline_commit in the ledger.
    Runtime Lua is never normalized. Other content must still hash identically.
    """
    raw=raw.replace(b'\r\n',b'\n')
    if relative=='src/metadata/sandbox-options.txt':
        # Reviewed presentation-only appended block. Still compare the complete
        # diagnostic prefix against its original immutable proof fingerprint.
        if not raw.endswith(TAIL_OPTION) or raw.count(TAIL_OPTION)!=1:
            raise ValueError('Unexpected tail presentation option block')
        return raw[:-len(TAIL_OPTION)]
    if relative=='src/metadata/mod.info':
        pattern=rb'(?m)^(modversion=)[^\r\n]+$'
    elif relative=='src/metadata/runtime-options.json' or relative.startswith('docs/native-'):
        pattern=rb'(?m)^(  "project_version": ")[^"\r\n]+(",?)$'
    else:return raw
    normalized,count=re.subn(pattern,lambda m:m[1]+PROOF_BASELINE_VERSION.encode()+(m[2] if m.lastindex==2 else b''),raw)
    if count!=1:raise ValueError('Expected exactly one current version header: '+relative)
    return normalized
REPORTS = ('AUTHENTICATED_PRINCIPAL_PROOF', 'NATIVE_MANAGED_LIFECYCLE_PROOF',
           'SERVER_MOVEMENT_INTERACTION_PROOF', 'PRIVATE_DATABASE_DURABILITY_PROOF',
           'NATIVE_OVERRIDE_DRIFT_REPORT', 'DATABASE_AUTHORITY_BLOCKER_MATRIX',
           'DISPOSABLE_RUNTIME_VALIDATION_PLAN', 'DATABASE_AUTHORITY_GO_NO_GO')


def sha(data):
    return hashlib.sha256(data).hexdigest()


def read():
    return json.loads((ROOT / 'docs/database-authority-proof-evidence.json').read_text(encoding='utf-8'))


def check():
    errors = []
    d = read()
    version = (ROOT / 'VERSION').read_text().strip()
    if d['project_version'] != version or d['decision'] != 'NO-GO' or d['native_no_go_retained'] is not True:
        errors.append('Proof disposition/version differs')
    for field in ('runtime_enabled', 'ownership_enabled', 'live_task_control_enabled', 'bond_gameplay_enabled',
                  'handler_gameplay_enabled', 'sqlite_verified'):
        if d.get(field) is not False:
            errors.append('Unsafe proof enablement: ' + field)
    if d.get('fixture_only') is not True or d.get('runtime_status') != 'NOT TESTED':
        errors.append('Offline proof isolation differs')
    gates = {'D1': 'BLOCKED', 'D2': 'BLOCKED', 'D3': 'BLOCKED', 'D4': 'EXPERIMENTAL',
             'D5': 'FEASIBLE', 'D6': 'EXPERIMENTAL', 'D7': 'NOT TESTED', 'D8': 'BLOCKED'}
    if d['gates'] != gates or d['G6'] != 'NOT TESTED' or d['G7'] != 'BLOCKED / NOT TESTED' or d['G8'] != 'BLOCKED':
        errors.append('Unreviewed authority/runtime gate change')
    if d['offline_validation']['combined_pair_rollback_detection'] is not False or d['offline_validation']['durable_native_commit_proven'] is not False:
        errors.append('Unsupported durability claim')
    inventory = json.loads((ROOT / 'source-inventory.json').read_text(encoding='utf-8'))
    if set(d['production_sources']) | {SHEPHERD_ADDITION,TAIL_ADDITION} != set(inventory['authoritative_lua']):
        errors.append('Unreviewed production additions outside Shepherd registration/presentation')
    for group in ('production_sources', 'production_metadata', 'historical_manifests'):
        for relative, expected in d[group].items():
            path = ROOT / relative
            if not path.resolve().is_relative_to(ROOT) or sha(baseline_bytes(relative,path.read_bytes())) != expected:
                errors.append('Proof baseline changed: ' + relative)
    request = d['source_request']
    relative = Path(request['path'])
    if relative.is_absolute() or '..' in relative.parts or not request['path'].startswith('docs/requirements/'):
        errors.append('Unsafe supplied request path')
    elif sha((ROOT / relative).read_bytes()) != request['sha256']:
        errors.append('Supplied request bytes changed')
    for name in REPORTS:
        path = ROOT / 'docs' / (name + '.md')
        if not path.exists() or '\nProject Version: ' + version + '\n' not in path.read_text(encoding='utf-8'):
            errors.append('Missing/version-inconsistent proof deliverable: ' + name)
    expected = {'tests/lua/database_store_fixture.lua', 'tests/lua/database_transaction_spec.lua',
                'tests/lua/database_restart_spec.lua'}
    for relative in expected:
        if not (ROOT / relative).is_file() or relative in inventory['authoritative_lua']:
            errors.append('Fixture missing or included as production: ' + relative)
    for relative in inventory['authoritative_lua']:
        if 'database_store_fixture' in (ROOT / relative).read_text(encoding='utf-8'):
            errors.append('Runtime imports test-only proof fixture')
    return errors


def check_native(game):
    errors, checked = [], 0
    d = read()
    with zipfile.ZipFile(game / 'projectzomboid.jar') as archive:
        for item in d['inputs']:
            path = Path(item['path'])
            if path.is_absolute() or '..' in path.parts:
                errors.append('Unsafe native proof path')
                continue
            if item['container'] == 'projectzomboid.jar':
                data = archive.read(item['path'])
            elif item['container'] == 'loose':
                data = (game / path).read_bytes()
            else:
                errors.append('Unsupported native proof container')
                continue
            checked += 1
            if sha(data) != item['sha256']:
                errors.append('Proof input changed: ' + item['path'])
    # Never promote an observed modified installation to a pristine baseline.
    if d['effective_runtime'] != 'UNKNOWN / BASELINE_DRIFT' or not d['drift']:
        errors.append('Native environment disposition needs explicit review')
    else:
        errors.append('Native baseline BLOCKED: retained historical drift and additional loose/package differences')
    return errors, checked


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--native', action='store_true')
    parser.add_argument('--game-root', type=Path)
    args = parser.parse_args()
    if args.native and not args.game_root:
        parser.error('--native requires --game-root')
    errors, checked = check(), 0
    if args.native:
        native, checked = check_native(args.game_root)
        errors.extend(native)
    d = read()
    print(json.dumps({'status': 'FAIL / BASELINE BLOCKED' if errors else 'STATIC PROOF PASS',
                      'project_version': d['project_version'], 'decision': d['decision'],
                      'native_inputs_rehashed': checked, 'production_sources_unchanged': len(d['production_sources']),
                      'reports': len(REPORTS), 'gates': d['gates'],
                      'environment': 'Offline structural/hash checks; no PZ execution', 'errors': errors,
                      'G6': d['G6'], 'G7': d['G7'], 'G8': d['G8']}, indent=2))
    return bool(errors)


if __name__ == '__main__':
    sys.exit(main())
