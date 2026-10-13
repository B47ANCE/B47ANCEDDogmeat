"""Verify documentation/evidence consistency without invoking PZ or its code."""
import csv
import hashlib
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
REQUIRED = ['COMPANION_DOGS_SOURCE_AUDIT.md', 'DOGPACK_COMPATIBILITY_AUDIT.md',
            'DRUGS_OF_93_COMPATIBILITY_AUDIT.md', 'VANILLA_API_AUDIT.md',
            'FEATURE_FEASIBILITY_MATRIX.md', 'SERVER_AUTHORITY_DESIGN.md', 'IMPLEMENTATION_PLAN.md']

def digest(path):
    result = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            result.update(block)
    return result.hexdigest()

def main():
    errors = []
    for name in REQUIRED:
        path = ROOT / 'docs' / name
        if not path.is_file() or path.stat().st_size < 100:
            errors.append('Missing/empty required document: ' + name)
    for path in [ROOT / 'README.md', *(ROOT / 'docs').glob('*.md')]:
        if path.name == 'USER_HANDOFF.md':
            continue
        text = path.read_text(encoding='utf-8')
        for target in re.findall(r'\]\(([^)]+)\)', text):
            target = target.split('#')[0]
            if not target or '://' in target or '<' in target:
                continue
            if not (path.parent / target).exists():
                errors.append(f'Broken local link in {path.name}: {target}')
    matrix = (ROOT / 'docs/FEATURE_FEASIBILITY_MATRIX.md').read_text(encoding='utf-8')
    rows = [line.split('|') for line in matrix.splitlines() if line.startswith('| F')]
    ids = [row[1].strip() for row in rows]
    if len(ids) != 101 or len(set(ids)) != 101:
        errors.append('Feature matrix must contain 101 unique feature identifiers')
    covered = {int(number.split('.')[0]) for row in rows for number in re.findall(r'\d+(?:\.\d+)?', row[2])}
    if covered != set(range(1, 31)):
        errors.append('Handoff section coverage differs from 1 through 30')
    manifest = json.loads((ROOT / 'research/SOURCE_MANIFEST.json').read_text())
    for record in manifest['files']:
        path = Path(record['path'])
        if not path.is_file() or digest(path) != record['sha256']:
            errors.append('Source changed or missing: ' + record['path'])
    metadata = {entry['id']: entry for entry in manifest['dependencies']}
    for mod_id, version in [('CompanionDogs', '0.7.4'), ('CompanionDogsPack', '0.9.3'), ('DrugsOf93', '171')]:
        if metadata.get(mod_id, {}).get('modversion') != version:
            errors.append('Unexpected dependency metadata: ' + mod_id)
    api = json.loads((ROOT / 'research/NATIVE_CLASS_API.json').read_text())
    by_class = {entry['class']: entry for entry in api}
    for class_name, methods in {
        'zombie.characters.animals.datas.AnimalData': ['getAge', 'getWeight', 'setAttachedPlayer'],
        'zombie.characters.skills.CustomPerks': ['init', 'initLua'],
        'zombie.world.moddata.GlobalModData': ['receiveRequest', 'request'],
    }.items():
        names = {method['name'] for method in by_class[class_name]['public_methods']}
        if not set(methods).issubset(names):
            errors.append('Expected native API missing: ' + class_name)
    with (ROOT / 'research/DRUGS_OF_93_ITEM_IDENTIFIERS.csv').open(encoding='utf-8') as stream:
        drug_rows = list(csv.DictReader(stream))
    full_types = {row['FullType'] for row in drug_rows}
    drug_doc = (ROOT / 'docs/DRUGS_OF_93_COMPATIBILITY_AUDIT.md').read_text()
    for full_type in re.findall(r'`(DrugsOf93\.\w+)`', drug_doc):
        if full_type not in full_types:
            errors.append('Unverified item identifier in document: ' + full_type)
    framework = Path('C:/Users/willi/Desktop/Repositories/PZ-AI-Development-Framework/project-template/scripts/check_versions.py')
    if digest(ROOT / 'scripts/check_versions.py') != digest(framework):
        errors.append('Framework version checker was modified')
    if (ROOT / 'src').exists() or (ROOT / 'dist').exists():
        errors.append('Unexpected gameplay source or distribution directory in Milestone 0')
    report = {'status': 'PASS' if not errors else 'FAIL', 'errors': errors,
              'required_documents': len(REQUIRED), 'features': len(rows),
              'handoff_sections': sorted(covered), 'source_hashes_rechecked': len(manifest['files']),
              'native_classes': len(api), 'drug_item_identifiers': len(drug_rows),
              'environment': 'Windows offline documentation/source checks; no mod behavior executed'}
    (ROOT / 'research/DOCUMENTATION_CHECK.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
    print(json.dumps(report, indent=2))
    raise SystemExit(1 if errors else 0)

if __name__ == '__main__':
    main()
