"""Read-only JVM class-file inventory; does not load/execute game classes.

Lists public method/field descriptors and selected string constants. Presence is
not proof of Lua exposure, runtime safety, or network authority.
"""
import argparse
import hashlib
import json
import re
import struct
from pathlib import Path
import zipfile

def inspect(data):
    offset = 0
    def read(fmt):
        nonlocal offset
        size = struct.calcsize(fmt)
        value = struct.unpack_from(fmt, data, offset)
        offset += size
        return value[0] if len(value) == 1 else value
    if read('>I') != 0xCAFEBABE:
        raise ValueError('Not a JVM class file')
    minor, major = read('>HH')
    count = read('>H')
    pool = [None] * count
    i = 1
    while i < count:
        tag = read('>B')
        if tag == 1:
            size = read('>H')
            pool[i] = data[offset:offset + size].decode('utf-8', errors='replace')
            offset += size
        elif tag == 3:
            pool[i] = read('>i')
        elif tag == 4:
            pool[i] = read('>f')
        elif tag in (5, 6):
            pool[i] = read('>q' if tag == 5 else '>d')
            i += 1
        elif tag in (7, 8, 16, 19, 20):
            pool[i] = ('reference', read('>H'))
        elif tag in (9, 10, 11, 12, 17, 18):
            offset += 4
        elif tag == 15:
            offset += 3
        else:
            raise ValueError(f'Unsupported constant tag {tag}')
        i += 1
    read('>HHH')
    interfaces = read('>H')
    offset += interfaces * 2
    def members():
        nonlocal offset
        result = []
        for _ in range(read('>H')):
            access, name, descriptor = read('>HHH')
            attributes = []
            for _ in range(read('>H')):
                attr_name, size = read('>HI')
                raw = data[offset:offset + size]
                offset += size
                if pool[attr_name] == 'ConstantValue' and len(raw) == 2:
                    value = pool[struct.unpack('>H', raw)[0]]
                    if isinstance(value, tuple):
                        value = pool[value[1]]
                    attributes.append(value)
            if access & 1:
                result.append({'name': pool[name], 'descriptor': pool[descriptor], 'access': access,
                               'constant_values': attributes})
        return result
    fields = members()
    methods = members()
    strings = [v for v in pool if isinstance(v, str)]
    return {'class_major': major, 'class_minor': minor, 'public_fields': fields,
            'public_methods': methods,
            'version_strings': [v for v in strings if re.fullmatch(r'42\.\d+(?:\.\d+)?(?:[ -].*)?', v)]}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--game-root', required=True)
    parser.add_argument('--output', required=True)
    parser.add_argument('--prefer-jar', action='store_true', help='Inspect packaged classes instead of loose overrides')
    parser.add_argument('classes', nargs='+')
    args = parser.parse_args()
    root = Path(args.game_root)
    results = []
    with zipfile.ZipFile(root / 'projectzomboid.jar') as jar:
        for name in args.classes:
            relative = name.replace('.', '/') + '.class'
            loose = root / relative
            if loose.exists() and not args.prefer_jar:
                data = loose.read_bytes()
                source = str(loose)
            else:
                data = jar.read(relative)
                source = str(root / 'projectzomboid.jar') + '!' + relative
            record = inspect(data)
            record.update({'class': name, 'source': source, 'sha256': hashlib.sha256(data).hexdigest()})
            results.append(record)
    Path(args.output).write_text(json.dumps(results, indent=2), encoding='utf-8')
    print(f'Inspected {len(results)} class files; game code was not executed.')

if __name__ == '__main__':
    main()
