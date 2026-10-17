"""Read-only, bounded native proof inventory. Never execute or modify game classes.

Raw javap output stays in the caller's ignored scratch directory. Public output
contains fingerprints/method names only, never game bytecode or private logs.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import zipfile

ROOT = Path(__file__).resolve().parents[1]
CLASSES = [
    'zombie.core.Core', 'zombie.GameWindow', 'zombie.iso.IsoWorld',
    'zombie.Lua.LuaEventManager', 'zombie.gameStates.GameLoadingState',
    'zombie.Lua.LuaManager$GlobalObject', 'zombie.Lua.LuaManager$Exposer',
    'zombie.Lua.LuaManager$GlobalObject$LuaFileWriter',
    'zombie.Lua.KahluaNumberConverter',
    'zombie.Lua.KahluaNumberConverter$NumberToLuaConverter',
    'zombie.network.GameServer', 'zombie.core.raknet.UdpConnection',
    'zombie.characters.IsoPlayer', 'zombie.core.znet.SteamUtils',
    'zombie.characters.animals.IsoAnimal', 'zombie.characters.animals.VirtualAnimal',
    'zombie.characters.animals.AnimalManagerMain', 'zombie.characters.animals.AnimalManagerWorker',
    'zombie.characters.animals.behavior.BaseAnimalBehavior',
    'zombie.characters.animals.datas.AnimalData', 'zombie.iso.IsoObject',
]
LUA = [
    'media/lua/shared/TimedActions/Animals/ISFeedAnimalFromHand.lua',
    'media/lua/shared/TimedActions/Animals/ISPetAnimal.lua',
    'media/lua/shared/TimedActions/Animals/ISAttachAnimalToPlayer.lua',
]


def digest(data):
    return hashlib.sha256(data).hexdigest()


def methods(output):
    # Compare normalized instructions, ignoring constant-pool indexes. This is
    # not semantic equivalence: pool/debug/compiler changes can still matter.
    result, signature, lines = {}, None, []
    for line in output.splitlines():
        if re.match(r'^  \S.*(?:\);|\{\};)$', line) or line == '  static {};':
            if signature:
                result[signature] = digest('\n'.join(lines).encode())
            signature, lines = line.strip(), []
        elif signature:
            lines.append(re.sub(r'#\d+', '#POOL', line))
    if signature:
        result[signature] = digest('\n'.join(lines).encode())
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--game-root', required=True, type=Path)
    parser.add_argument('--javap', required=True, type=Path)
    parser.add_argument('--scratch', required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    game = args.game_root.resolve()
    scratch = args.scratch.resolve()
    # Only raw output beneath the repository's explicitly ignored scratch root.
    if not scratch.is_relative_to(ROOT / '.m0r-local'):
        parser.error('scratch must be beneath repository .m0r-local')
    scratch.mkdir(parents=True, exist_ok=True)
    jar = game / 'projectzomboid.jar'
    prior = json.loads((ROOT / 'docs/native-database-redesign-evidence.json').read_text(encoding='utf-8'))
    prior_drift = {r['path']: r for r in prior['native_baseline_validation']['drift_inputs']}
    inputs, drift = [], []

    def inspect(name, classpath, label):
        value = subprocess.check_output([str(args.javap), '-c', '-p', '-classpath', str(classpath), name])
        output = value.decode('cp1252')
        (scratch / (label + '-' + name + '.txt')).write_text(output, encoding='utf-8', newline='\n')
        return output

    with zipfile.ZipFile(jar) as archive:
        for name in CLASSES:
            path = name.replace('.', '/') + '.class'
            packaged = archive.read(path)
            inputs.append({'container': 'projectzomboid.jar', 'path': path,
                           'sha256': digest(packaged), 'bytes': len(packaged)})
            packaged_output = inspect(name, jar, 'packaged')
            loose_path = game / path
            if loose_path.exists():
                loose = loose_path.read_bytes()
                inputs.append({'container': 'loose', 'path': path, 'sha256': digest(loose), 'bytes': len(loose)})
                if loose != packaged:
                    old = prior_drift.get(path, {})
                    a, b = methods(packaged_output), methods(inspect(name, game, 'loose'))
                    changed = sorted(k for k in a.keys() & b.keys() if a[k] != b[k])
                    pzopt_refs = sorted(set(re.findall(r'// (?:Method|class|Field) (pzopt/[A-Za-z0-9_$]+)',
                                                       (scratch / ('loose-' + name + '.txt')).read_text(encoding='utf-8'))))
                    drift.append({'path': path, 'current_loose_sha256': digest(loose),
                                  'packaged_sha256': digest(packaged),
                                  'previous_observation': old,
                                  'added_methods': sorted(set(b) - set(a)),
                                  'removed_methods': sorted(set(a) - set(b)),
                                  'changed_normalized_method_count': len(changed),
                                  'selected_changed_methods': [m for m in changed if any(s in m for s in
                                      (' save(', ' load(', ' init(', ' update(', ' exit(', ' triggerEvent(', ' getSteamID(', ' Serialize('))],
                                  'observed_external_namespace_references': pzopt_refs,
                                  'runtime_effect': 'UNKNOWN; source differences are not an execution test'})
        for path in LUA:
            value = (game / path).read_bytes()
            inputs.append({'container': 'loose', 'path': path, 'sha256': digest(value), 'bytes': len(value)})
    manifest = (game.parent.parent / 'appmanifest_108600.acf').read_text(encoding='utf-8')
    build = re.search(r'"buildid"\s+"(\d+)"', manifest).group(1)
    sources = {p: digest((ROOT / p).read_bytes().replace(b'\r\n', b'\n')) for p in
               json.loads((ROOT / 'source-inventory.json').read_text(encoding='utf-8'))['authoritative_lua']}
    result = {'format_revision': 1, 'project_version': (ROOT / 'VERSION').read_text().strip(),
              'source_baseline_commit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
              'steam_build': build, 'jar_sha256': digest(jar.read_bytes()),
              'inputs': inputs, 'drift': drift, 'production_sources': sources,
              'production_source_hash_normalization': 'CRLF_TO_LF',
              'environment': 'READ_ONLY_SOURCE_INSPECTION; no game/server execution',
              'effective_runtime': 'UNKNOWN / BASELINE_DRIFT', 'native_no_go_retained': True}
    args.output.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8', newline='\n')
    print(json.dumps({'inputs': len(inputs), 'loose_overrides_differing_from_package': len(drift),
                      'production_sources': len(sources), 'steam_build': build}))


if __name__ == '__main__':
    main()
