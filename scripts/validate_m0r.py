"""Read-only M0R documentation/design checks; never execute PZ or write evidence."""
from pathlib import Path
import argparse
import hashlib
import json
import math
import platform
import re
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[1]
REQUIRED = [
    'STANDALONE_CANINE_FEASIBILITY.md', 'NATIVE_STATE_OWNERSHIP_MATRIX.md',
    'CANINE_IDENTITY_CONTRACT.md', 'PRIVATE_PERSISTENCE_RECOVERY_CONTRACT.md',
    'TASK_ARBITRATION_CONTRACT.md', 'MILESTONE_DEPENDENCY_GRAPH.md',
    'SANDBOX_SETTINGS_REGISTRY.md', 'LOCALIZATION_CONTRACT.md',
    'CANINE_BIOLOGY_TIME_MODEL.md', 'MINIMUM_PLAYABLE_RELEASE.md',
    'MULTIPLAYER_ACCEPTANCE_MATRIX.md', 'FEATURE_TRACEABILITY_MATRIX.md',
    'M0R_VALIDATION.md',
]
LANGUAGES = 'AR CA CH CN CS DA DE EN ES ES_CL ES_MX FI FR HU ID IT JP KO NL NO PL PT PTBR RO RU STREW TH TR UA'.split()


def pairs_no_duplicates(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError('Duplicate JSON key: ' + key)
        result[key] = value
    return result


def read_json(path):
    return json.loads(path.read_text(encoding='utf-8'), object_pairs_hook=pairs_no_duplicates)


def sha(path):
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(block)
    return digest.hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--native', action='store_true', help='Recheck declared installed native input hashes; still source evidence only')
    parser.add_argument('--game-root', type=Path)
    parser.add_argument('--baseline', action='store_true', help='Verify optional local pre-edit hash baseline without publishing it')
    args = parser.parse_args()
    errors, notes = [], []
    version = (ROOT / 'VERSION').read_text(encoding='utf-8').strip()
    contracts = ROOT / 'docs/contracts'
    history = read_json(contracts / 'historical_inventory.json')['records']
    historical_paths = {record['path'] for record in history}
    current_paths = ['README.md', 'docs/IMPLEMENTATION_PLAN.md', 'docs/VERSIONING.md', 'docs/M0R_SOURCE_EVIDENCE.md', 'docs/HISTORICAL_RESEARCH_INDEX.md'] + ['docs/' + p for p in REQUIRED]
    for relative in current_paths:
        path = ROOT / relative
        if not path.is_file() or path.stat().st_size < 200:
            errors.append('Missing/empty current document: ' + relative)
            continue
        content = path.read_text(encoding='utf-8')
        if re.findall(r'^Project Version: (\S+)$', content, re.M) != [version]:
            errors.append('Current version header mismatch: ' + relative)
        for target in re.findall(r'\]\(([^)]+)\)', content):
            target = target.split('#')[0].strip('<>')
            if not target or '://' in target:
                continue
            if not (path.parent / target).exists():
                errors.append('Broken local link: ' + relative + ' -> ' + target)
        if relative not in ('README.md', 'docs/VERSIONING.md', 'docs/HISTORICAL_RESEARCH_INDEX.md'):
            if re.search(r'G[67]\s+PASS', content) and not any(text in content for text in ('requires', 'Require', 'before', 'mandatory', 'need')):
                errors.append('Review possible runtime PASS claim: ' + relative)
    for path in contracts.glob('*.json'):
        data = read_json(path)
        if data.get('project_version') != version:
            errors.append('Contract version mismatch: ' + path.name)
    features = read_json(contracts / 'feature_traceability.json')['features']
    ids = [f['id'] for f in features]
    expected = [f'F{n:02d}' for n in range(1, 133)]
    if sorted(ids) != sorted(expected) or len(set(ids)) != len(ids):
        errors.append('Expected exactly original F01-F101 plus F102-F132, no duplicates')
    old = (ROOT / 'docs/FEATURE_FEASIBILITY_MATRIX.md').read_text(encoding='utf-8')
    old_names = {line.split('|')[1].strip(): line.split('|')[3].strip() for line in old.splitlines() if re.match(r'^\| F\d+', line)}
    mp = (ROOT / 'docs/MULTIPLAYER_ACCEPTANCE_MATRIX.md').read_text(encoding='utf-8')
    test_ids = set(re.findall(r'^\| (T-[A-Z]+) \|', mp, re.M))
    blocker_ids = set(re.findall(r'^\| (B-[A-Z]+) \|', mp, re.M))
    evidence = (ROOT / 'docs/M0R_SOURCE_EVIDENCE.md').read_text(encoding='utf-8')
    evidence_ids = set(re.findall(r'^\| (E-[A-Z]+) \|', evidence, re.M))
    table = (ROOT / 'docs/FEATURE_TRACEABILITY_MATRIX.md').read_text(encoding='utf-8')
    for f in features:
        if f['id'] in old_names and f['requirement'] != old_names[f['id']]:
            errors.append('Original feature meaning changed: ' + f['id'])
        for field in ('requirement','technical_dependency','milestone','classification','acceptance_tests','acceptance','evidence','authority','implementation_status','runtime_status','provenance'):
            if not f.get(field):
                errors.append('Incomplete feature ' + f['id'] + ': ' + field)
        if f['classification'] not in ('VERIFIED','FEASIBLE','EXPERIMENTAL','BLOCKED') or f['runtime_status'] != 'NOT TESTED':
            errors.append('Invalid evidence/runtime classification: ' + f['id'])
        if not set(f['acceptance_tests']) <= test_ids or not set(f['technical_dependency']) <= blocker_ids or not set(f['evidence']) <= evidence_ids:
            errors.append('Undefined test/blocker/evidence: ' + f['id'])
        if table.count('| ' + f['id'] + ' |') != 1 or f['acceptance'] not in table or f['requirement'] not in table:
            errors.append('Feature JSON/Markdown mismatch: ' + f['id'])
    settings = read_json(contracts / 'sandbox_settings.json')['settings']
    setting_ids = {s['id'] for s in settings}
    if len(setting_ids) != len(settings):
        errors.append('Duplicate sandbox setting ID')
    loc = read_json(contracts / 'localization_keys.json')
    keys = loc['english_fallback']
    if loc['languages'] != LANGUAGES:
        errors.append('Required 29-language policy differs')
    registry = (ROOT / 'docs/SANDBOX_SETTINGS_REGISTRY.md').read_text(encoding='utf-8')
    for s in settings:
        for field in ('id','group','name','description','type','default','minimum','maximum','step','allowed_values','server_authority','existing_save_policy','dependencies','conflicts','classification','name_key','tooltip_key','parent_settings','schema_status','capability_status','capability_blockers','runtime_status','existing_obligations'):
            if field not in s:
                errors.append('Missing setting field: ' + s['id'] + ':' + field)
        if s['server_authority'] is not True or not s['id'].startswith('B47ANCEDDogTraining.'):
            errors.append('Wrong authority/namespace: ' + s['id'])
        if not set(s['parent_settings']) <= setting_ids:
            errors.append('Undefined setting parent: ' + s['id'])
        if s['schema_status']!='FEASIBLE DESIGN ONLY' or s['capability_status'] not in ('EXPERIMENTAL','BLOCKED') or s['runtime_status']!='NOT TESTED' or not set(s['capability_blockers']) <= blocker_ids:
            errors.append('Setting capability/status overclaim: '+s['id'])
        if s['type'] in ('double','integer'):
            if not all(isinstance(s[x], (int,float)) and not isinstance(s[x],bool) and math.isfinite(s[x]) for x in ('default','minimum','maximum','step')):
                errors.append('Non-finite numeric setting: ' + s['id'])
            elif not s['minimum'] <= s['default'] <= s['maximum'] or s['step'] <= 0:
                errors.append('Invalid setting bounds/default: ' + s['id'])
            elif abs((s['default']-s['minimum'])/s['step']-round((s['default']-s['minimum'])/s['step'])) > 1e-8:
                errors.append('Default not on documented step: ' + s['id'])
        elif s['type']=='boolean' and not isinstance(s['default'],bool):
            errors.append('Invalid boolean setting: ' + s['id'])
        elif s['type']=='enum' and (s['default'] not in s['allowed_values'] or len(set(s['allowed_values'])) != len(s['allowed_values'])):
            errors.append('Invalid enum setting: ' + s['id'])
        if keys.get(s['name_key']) != s['name'] or keys.get(s['tooltip_key']) != s['description']:
            errors.append('Missing/mismatched setting text: ' + s['id'])
        for index in range(1,len(s['allowed_values'])+1):
            if not keys.get(s['name_key']+'_option'+str(index)):
                errors.append('Missing enum label: ' + s['id'])
        if registry.count('| '+s['id']+' |')!=1 or s['description'] not in registry:
            errors.append('Setting JSON/Markdown mismatch: ' + s['id'])
        row=next((line.split('|') for line in registry.splitlines() if line.startswith('| '+s['id']+' |')),None)
        expected_default=str(s['default']).lower() if s['type']=='boolean' else str(s['default'])
        if row is not None and row[4].strip()!=expected_default:
            errors.append('Setting Markdown default differs: '+s['id'])
    for k,v in keys.items():
        if not isinstance(v,str) or not v.strip() or not k.startswith(('Sandbox_B47ANCEDDogTraining','UI_B47ANCEDDogTraining',
                'Sandbox_B47ANCEDDogmeat','UI_B47ANCEDDogmeat','IGUI_AnimalType_b47dogtest')):
            errors.append('Invalid localization catalog entry: '+k)
    checked_history = 0
    for record in history:
        path = ROOT / record['path']
        if not path.exists() and record.get('local_only'):
            notes.append('Local-only historical input unavailable: '+record['path'])
            continue
        if not path.is_file() or sha(path)!=record['sha256']:
            errors.append('Historical report changed/missing: '+record['path'])
        checked_history += 1
    if args.baseline:
        baseline = read_json(ROOT / '.m0r-local/baseline.json')
        permitted = {'README.md','docs/IMPLEMENTATION_PLAN.md','docs/VERSIONING.md','version-inventory.json','CHANGELOG.md'}
        for relative,digest in baseline.items():
            if relative not in permitted and (not (ROOT/relative).is_file() or sha(ROOT/relative)!=digest):
                if relative.startswith('.agents/'):
                    notes.append('Managed local guidance changed concurrently and was preserved: '+relative)
                else:
                    errors.append('Unexpected baseline mutation: '+relative)
    native_checked=0
    if args.native:
        if not args.game_root:
            errors.append('--native requires --game-root')
        else:
            manifest = read_json(contracts / 'native_evidence.json')['sources']
            with zipfile.ZipFile(args.game_root/'projectzomboid.jar') as jar:
                for record in manifest:
                    digest = hashlib.sha256(jar.read(record['path'])).hexdigest() if record['kind']=='jar_entry' else sha(args.game_root/record['path'])
                    if digest != record['sha256']:
                        errors.append('Native input changed: '+record['path'])
                    native_checked += 1
            languages = sorted(p.name for p in (args.game_root/'media/lua/shared/Translate').iterdir() if p.is_dir())
            if languages != sorted(LANGUAGES):
                errors.append('Installed translation language set differs; compatibility review required')
    # Feature development is now authorized; retain a bounded no-integration guard.
    from validate_foundation import check_source
    errors.extend(check_source())
    result = {'status':'STATIC PASS' if not errors else 'FAIL','project_version':version,'required_deliverables':len(REQUIRED),
              'feature_rows':len(features),'sandbox_settings':len(settings),'localization_keys':len(keys),'required_languages':len(LANGUAGES),
              'acceptance_scenarios':len(test_ids),'historical_hashes_checked':checked_history,'native_inputs_rehashed':native_checked,
              'environment':platform.system()+' offline documentation/source checks; no gameplay executed','errors':errors,'notes':notes,
              'G6':'NOT TESTED','G7':'BLOCKED / NOT TESTED','G8':'BLOCKED'}
    print(json.dumps(result,indent=2))
    return bool(errors)


if __name__ == '__main__':
    try:
        sys.exit(main())
    except (OSError,ValueError,KeyError,zipfile.BadZipFile) as exc:
        print('FAIL: '+str(exc))
        sys.exit(1)
