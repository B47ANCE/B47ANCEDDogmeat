"""Independent stdlib artifact/GLB checks; never execute Blender, Meshy or PZ."""
from collections import Counter
import hashlib
import json
import math
from pathlib import Path
import struct

ROOT = Path(__file__).resolve().parents[1]


def digest(data):
    return hashlib.sha256(data).hexdigest()


def image_size(blob):
    if blob[:8] == b'\x89PNG\r\n\x1a\n':
        return struct.unpack_from('>II', blob, 16)
    assert blob[:2] == b'\xff\xd8', 'Expected embedded PNG or JPEG'
    offset = 2
    while offset < len(blob):
        assert blob[offset] == 255, 'Invalid JPEG marker'
        while blob[offset] == 255:
            offset += 1
        marker = blob[offset]
        offset += 1
        size = struct.unpack_from('>H', blob, offset)[0]
        assert size >= 2 and offset+size <= len(blob)
        if marker in (0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC6, 0xC7, 0xC9, 0xCA, 0xCB, 0xCD, 0xCE, 0xCF):
            height, width = struct.unpack_from('>HH', blob, offset+3)
            return width, height
        offset += size
    raise ValueError('JPEG size not found')


def glb(path):
    raw = path.read_bytes()
    magic, version, length = struct.unpack_from('<4sII', raw)
    assert magic == b'glTF' and version == 2 and length == len(raw), 'Invalid GLB header/length'
    offset = 12
    chunks = {}
    while offset < len(raw):
        length, kind = struct.unpack_from('<II', raw, offset)
        offset += 8
        assert kind not in chunks and offset+length <= len(raw), 'Invalid GLB chunk'
        chunks[kind] = raw[offset:offset+length]
        offset += length
    data = json.loads(chunks[0x4E4F534A])
    binary = chunks[0x004E4942]
    assert len(data['meshes']) == 1 and len(data['meshes'][0]['primitives']) == 1
    assert not data.get('skins') and not data.get('animations'), 'Unexpected rig/animation'
    assert all('uri' not in b for b in data['buffers']), 'External buffer'

    def accessor(index):
        a = data['accessors'][index]
        assert 'sparse' not in a
        v = data['bufferViews'][a['bufferView']]
        code = {5121: 'B', 5123: 'H', 5125: 'I', 5126: 'f'}[a['componentType']]
        width = {'SCALAR': 1, 'VEC2': 2, 'VEC3': 3, 'VEC4': 4}[a['type']]
        fmt = '<'+code*width
        size = struct.calcsize(fmt)
        start = v.get('byteOffset', 0)+a.get('byteOffset', 0)
        stride = v.get('byteStride', size)
        assert start+(a['count']-1)*stride+size <= v.get('byteOffset', 0)+v['byteLength']
        values = [struct.unpack_from(fmt, binary, start+i*stride) for i in range(a['count'])]
        assert all(all(math.isfinite(x) for x in value) for value in values)
        return values

    primitive = data['meshes'][0]['primitives'][0]
    assert primitive.get('mode', 4) == 4
    positions = accessor(primitive['attributes']['POSITION'])
    uv = accessor(primitive['attributes']['TEXCOORD_0'])
    indices = [v[0] for v in accessor(primitive['indices'])]
    assert len(positions) == len(uv) and len(indices) % 3 == 0
    assert max(indices) < len(positions)
    triangles = Counter(tuple(sorted(tuple(round(x, 6) for x in positions[i]+uv[i])
                                      for i in indices[j:j+3])) for j in range(0, len(indices), 3))
    images = []
    for im in data['images']:
        v = data['bufferViews'][im['bufferView']]
        start = v.get('byteOffset', 0)
        blob = binary[start:start+v['byteLength']]
        assert image_size(blob) == (2048, 2048)
        images.append(digest(blob))
    material = data['materials'][primitive['material']]
    pbr = material['pbrMetallicRoughness']
    roles = {key: images[data['textures'][value['index']]['source']] for key, value in {
        'base_color': pbr['baseColorTexture'], 'metallic_roughness': pbr['metallicRoughnessTexture'],
        'normal': material['normalTexture']}.items()}
    return triangles, roles


def check():
    original, original_images = glb(ROOT / 'source/meshy_textured.glb')
    cleaned, cleaned_images = glb(ROOT / 'interchange/english_mastiff.glb')
    assert sum(cleaned.values()) == 12476 and sum(original.values()) == 12479
    assert not (cleaned-original), 'Unexpected new position/UV triangles'
    assert sum((original-cleaned).values()) == 3, 'Unexpected source geometry change'
    assert original_images == cleaned_images, 'Embedded PBR image/role changed'
    report = json.loads((ROOT / 'validation/processed.json').read_text())
    assert report['sha256'] == digest((ROOT / report['source']).read_bytes())
    assert report['meshes'][0]['welded_nonmanifold_edges'] == 0 and report['armatures'] == 0
    assert len(report['meshes'][0]['welded_components_vertices']) == 1
    fbx = json.loads((ROOT / 'validation/processed_fbx.json').read_text())
    assert fbx['sha256'] == digest((ROOT / fbx['source']).read_bytes())
    assert fbx['triangles'] == 12476 and fbx['meshes'][0]['welded_nonmanifold_edges'] == 0
    assert len(fbx['textures']) == 4 and all(im['size'] == [2048, 2048] for im in fbx['textures'])
    for a, b in zip(report['dimensions_blender_units'], fbx['dimensions_blender_units']):
        assert abs(a-b) < 1e-6, 'FBX dimension drift'
    for stage in ('geometry_preview', 'textured_service', 'processed'):
        record = json.loads((ROOT / 'validation' / (stage+'.json')).read_text())
        assert len(record['renders']) == 5
        for image in record['renders']:
            assert digest((ROOT / image['path']).read_bytes()) == image['sha256']
        editable = record['editable_source']
        assert digest((ROOT / editable['path']).read_bytes()) == editable['sha256']
    manifest = ROOT / 'validation/artifact_manifest.json'
    if manifest.exists():
        entries = json.loads(manifest.read_text())['files']
        actual = {p.relative_to(ROOT).as_posix() for p in ROOT.rglob('*') if p.is_file()
                  and p != manifest and '__pycache__' not in p.parts and p.suffix not in ('.blend1', '.pyc')}
        assert len(entries) == len({entry['path'] for entry in entries}), 'Duplicate artifact record'
        assert {entry['path'] for entry in entries} == actual, 'Artifact inventory coverage differs'
        for entry in entries:
            target = (ROOT / entry['path']).resolve()
            assert target.is_relative_to(ROOT), 'Unsafe artifact manifest path'
            assert target.stat().st_size == entry['bytes'] and digest(target.read_bytes()) == entry['sha256'], entry['path']
    return {'status': 'PASS', 'environment': 'Offline stdlib artifact inspection; not PZ',
            'triangles': 12476, 'removed_triangles': 3, 'position_uv_triangle_subset': 'PASS at 1e-6 rounding',
            'embedded_pbr_bytes_and_roles_preserved': True, 'fbx_reimport_evidence': 'PASS within recorded scope',
            'rigging': 'NOT TESTED', 'PZ': 'NOT TESTED', 'G7': 'BLOCKED / NOT TESTED', 'G8': 'BLOCKED'}


if __name__ == '__main__':
    print(json.dumps(check(), indent=2))
