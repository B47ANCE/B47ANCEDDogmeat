"""Collect a read-only source/hash inventory and public drug item identifiers."""
import argparse
import csv
import hashlib
import json
import re
from pathlib import Path

IDS = ['3740052292','3762296152','3770795385','3779327129','3787202559','3791350747',
       '3791294616','3798112588','3796123931','3807124432','3808688990','3809963228',
       '3784734412','3543229299','3807182783']
NATIVE = [
 'media/lua/shared/TimedActions/Animals/ISAttachAnimalToPlayer.lua',
 'media/lua/shared/TimedActions/Animals/ISPickupAnimal.lua',
 'media/lua/shared/TimedActions/Animals/ISAddAnimalInTrailer.lua',
 'media/lua/shared/TimedActions/Animals/ISRemoveAnimalFromTrailer.lua',
 'media/lua/client/ISUI/Animal/ISAnimalUI.lua',
 'media/lua/client/ISUI/Animal/ISAnimalContextMenu.lua',
 'media/lua/client/ISUI/ISVehicleAnimalUI.lua',
 'media/lua/client/XpSystem/ISUI/ISHealthPanel.lua',
 'media/lua/client/ISUI/ISRadialMenu.lua',
 'media/lua/client/ISUI/ISEmoteRadialMenu.lua',
 'media/lua/client/ISUI/ISContextMenu.lua',
 'media/lua/server/ClientCommands.lua',
 'media/lua/shared/TimedActions/ISBaseTimedAction.lua',
 'media/lua/shared/TimedActions/ISReadABook.lua',
 'media/lua/server/XpSystem/XPSystem_SkillBook.lua',
 'media/lua/shared/RecordedMedia/ISRecordedMedia.lua',
 'media/scripts/generated/characters/character_professions.txt',
 'media/lua/shared/Definitions/animal/AnimalTracksDefinitions.lua',
 'media/lua/client/Foraging/ISAnimalTracksFinder.lua',
 'media/lua/shared/Foraging/ISForageAction.lua',
 'media/lua/shared/Fishing/FishingUtils.lua',
 'media/lua/client/Fishing/FishingManager.lua',
 'projectzomboid.jar', 'ProjectZomboid64.json',
]

def record(path, domain):
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(chunk)
    return {'domain': domain, 'path': str(path), 'bytes': path.stat().st_size, 'sha256': digest.hexdigest()}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--workshop-root', required=True)
    parser.add_argument('--game-root', required=True)
    parser.add_argument('--output-dir', required=True)
    args = parser.parse_args()
    workshop, game, output = map(Path, [args.workshop_root, args.game_root, args.output_dir])
    output.mkdir(parents=True, exist_ok=True)
    records, dependencies = [], []
    for wid in IDS:
        root = workshop / wid
        for path in sorted(root.rglob('*')):
            if not path.is_file() or 'Translate' in path.parts:
                continue
            if path.suffix.lower() not in ('.lua', '.txt', '.xml', '.info', '.md'):
                continue
            if not ('42' in path.parts or path.name == 'mod.info'):
                continue
            records.append(record(path, 'workshop:' + wid))
            if path.name == 'mod.info' and '42' in path.parts:
                text = path.read_text(encoding='utf-8-sig', errors='replace')
                metadata = dict(re.findall(r'^(id|name|require|modversion|versionMin|incompatible)=(.*)$', text, re.M))
                dependencies.append({'workshop_id': wid, 'path': str(path), **metadata})
    missing = []
    for relative in NATIVE:
        path = game / relative
        if path.is_file():
            records.append(record(path, 'native'))
        else:
            missing.append(str(path))
    manifest = {'audit_date': '2026-10-12', 'environment': 'Windows, source inspection only',
                'dependencies': dependencies, 'files': records, 'missing_native_files': missing}
    (output / 'SOURCE_MANIFEST.json').write_text(json.dumps(manifest, indent=2), encoding='utf-8')
    item_path = workshop / '3784734412/mods/DrugsOf93/42/media/scripts/DO93_Items.txt'
    text = item_path.read_text(encoding='utf-8-sig')
    module = re.search(r'^module\s+(\w+)', text, re.M).group(1)
    declarations = list(re.finditer(r'^\s*item\s+(\w+)\s*$', text, re.M))
    items = []
    for i, declaration in enumerate(declarations):
        end = declarations[i + 1].start() if i + 1 < len(declarations) else len(text)
        body = text[declaration.end():end]
        tags = re.search(r'\bTags\s*=\s*([^,\r\n]+)', body)
        items.append({'FullType': module + '.' + declaration.group(1),
                      'Tags': tags.group(1).strip() if tags else '',
                      'SourceLine': text.count('\n', 0, declaration.start(1)) + 1})
    with (output / 'DRUGS_OF_93_ITEM_IDENTIFIERS.csv').open('w', newline='', encoding='utf-8') as stream:
        writer = csv.DictWriter(stream, fieldnames=['FullType', 'Tags', 'SourceLine'])
        writer.writeheader()
        writer.writerows(items)
    print(f'{len(records)} source/hash records; {len(dependencies)} metadata entries; {len(items)} item identifiers.')
    if missing:
        raise SystemExit('Missing native files: ' + ', '.join(missing))

if __name__ == '__main__':
    main()
