"""Read-only direct IsoAnimal NEW inventory; metadata only, not a call-graph proof."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
import zipfile


def collect(game_root, javap):
    jar_path = game_root / 'projectzomboid.jar'
    candidates, inputs, sites = [], [], []
    with zipfile.ZipFile(jar_path) as jar:
        for name in sorted(jar.namelist()):
            if not name.endswith('.class'):
                continue
            data = jar.read(name)
            if b'zombie/characters/animals/IsoAnimal' not in data or b'<init>' not in data:
                continue
            candidates.append(name)
            inputs.append({'container': 'projectzomboid.jar', 'path': name,
                           'sha256': hashlib.sha256(data).hexdigest(), 'bytes': len(data)})
    for name in candidates:
        class_name = name[:-6].replace('/', '.')
        result = subprocess.run([str(javap), '-c', '-p', '-classpath', str(jar_path), class_name],
                                capture_output=True, text=True, encoding='utf-8', check=True)
        method = None
        for line in result.stdout.splitlines():
            if re.match(r'^  \S.*\(.*\).*;$', line):
                method = line.strip()
            match = re.match(r'^\s*(\d+): new\s+#[0-9]+\s+// class zombie/characters/animals/IsoAnimal\s*$', line)
            if match:
                if method is None:
                    raise ValueError('Constructor instruction without method: ' + class_name)
                sites.append({'class': class_name, 'method': method, 'new_offset': int(match.group(1))})
    return {'candidate_classes': len(candidates), 'direct_constructor_sites': sites}, inputs


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--game-root', required=True, type=Path)
    parser.add_argument('--javap', required=True, type=Path)
    parser.add_argument('--check', required=True, type=Path, help='Compare to recorded metadata; never write it')
    args = parser.parse_args()
    actual, inputs = collect(args.game_root, args.javap)
    expected = json.loads(args.check.read_text(encoding='utf-8'))
    errors = []
    for key in ('candidate_classes', 'direct_constructor_sites'):
        if actual[key] != expected[key]:
            errors.append('Constructor metadata differs: ' + key)
    # Check candidate hashes independently of the broader native evidence verifier.
    manifest = json.loads((args.check.parent / 'native-continuity-evidence.json').read_text(encoding='utf-8'))
    indexed = {(item['container'], item['path']): item for item in manifest['inputs']}
    for item in inputs:
        if indexed.get((item['container'], item['path'])) != item:
            errors.append('Candidate evidence differs: ' + item['path'])
    print(json.dumps({'status': 'STATIC PASS' if not errors else 'FAIL',
                      'candidate_classes': actual['candidate_classes'],
                      'direct_constructor_sites': len(actual['direct_constructor_sites']),
                      'scope': 'Direct NEW only; no engine execution or graph-closure claim',
                      'errors': errors}, indent=2))
    return bool(errors)


if __name__ == '__main__':
    sys.exit(main())
