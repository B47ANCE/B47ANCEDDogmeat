"""Independent stdlib skin/clip/geometry/evidence checks; no bpy or game execution.

Structural PASS never promotes provisional deformation to artist/native PASS.
"""
from collections import Counter, defaultdict
import hashlib
import itertools
import json
import math
from pathlib import Path
import struct

ROOT = Path(__file__).resolve().parents[1]


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def glb(path):
    blob = path.read_bytes()
    assert struct.unpack_from('<4sII', blob) == (b'glTF', 2, len(blob))
    length = struct.unpack_from('<I', blob, 12)[0]
    data = json.loads(blob[20:20+length])
    binary_start = 20+length+8
    binary = blob[binary_start:]
    assert all('uri' not in b for b in data['buffers'])
    def accessor(index):
        acc = data['accessors'][index]
        view = data['bufferViews'][acc['bufferView']]
        code = {5121: 'B', 5123: 'H', 5125: 'I', 5126: 'f'}[acc['componentType']]
        width = {'SCALAR': 1, 'VEC2': 2, 'VEC3': 3, 'VEC4': 4, 'MAT4': 16}[acc['type']]
        fmt = '<'+code*width
        size = struct.calcsize(fmt)
        stride = view.get('byteStride', size)
        start = view.get('byteOffset', 0)+acc.get('byteOffset', 0)
        assert start+(acc['count']-1)*stride+size <= view.get('byteOffset', 0)+view['byteLength']
        return [struct.unpack_from(fmt, binary, start+i*stride) for i in range(acc['count'])]
    assert len(data['meshes']) == 1 and len(data['meshes'][0]['primitives']) == 1
    primitive = data['meshes'][0]['primitives'][0]
    attrs = {k: accessor(v) for k, v in primitive['attributes'].items()}
    indices = [x[0] for x in accessor(primitive['indices'])]
    assert len(indices) == 12476*3 and max(indices) < len(attrs['POSITION'])
    images = []
    for image in data['images']:
        view = data['bufferViews'][image['bufferView']]
        start = view.get('byteOffset', 0)
        images.append(hashlib.sha256(binary[start:start+view['byteLength']]).hexdigest())
    mat = data['materials'][primitive['material']]
    pbr = mat['pbrMetallicRoughness']
    roles = {k: images[data['textures'][v['index']]['source']] for k, v in {
        'base_color': pbr['baseColorTexture'], 'metallic_roughness': pbr['metallicRoughnessTexture'],
        'normal': mat['normalTexture']}.items()}
    return data, attrs, indices, roles, accessor


def check():
    rig = read(ROOT / 'metadata/rig.json')
    catalog = read(ROOT / 'metadata/clips.json')
    specs = {x['name']: x for x in catalog['clips']}
    source = ROOT.parent / 'english_mastiff/interchange/english_mastiff.glb'
    assert sha(source) == rig['source_sha256']
    original, src, src_indices, src_images, _ = glb(source)
    data, attrs, indices, images, accessor = glb(ROOT / 'interchange/english_mastiff_rig.glb')
    assert images == src_images, 'PBR bytes/roles changed'
    assert len(data['skins']) == 1
    skin = data['skins'][0]
    names = [data['nodes'][i]['name'] for i in skin['joints']]
    assert len(names) == 42 and set(names) == {b['name'] for b in rig['bones']}
    assert len(accessor(skin['inverseBindMatrices'])) == 42
    assert {a['name'] for a in data['animations']} == set(specs) and len(specs) == 37
    for js, ws in zip(attrs['JOINTS_0'], attrs['WEIGHTS_0']):
        assert len(js) == len(ws) == 4
        assert all(0 <= j < len(names) for j in js)
        assert all(math.isfinite(w) and 0 <= w <= 1 for w in ws)
        assert abs(sum(ws)-1) < 1e-5
    assert not any(k.startswith('WEIGHTS_') and k != 'WEIGHTS_0' for k in attrs)
    # Map each exported corner back to the preserved source, tolerance 2e-6.
    grid = defaultdict(list)
    source_corners = list(zip(src['POSITION'], src['TEXCOORD_0']))
    for i, (p, uv) in enumerate(source_corners):
        grid[tuple(round(v*10000) for v in p)].append(i)
    mapping, max_position, max_uv = [], 0.0, 0.0
    canonical = [tuple(p+uv) for p, uv in source_corners]
    for point, uv in zip(attrs['POSITION'], attrs['TEXCOORD_0']):
        p = (point[0], point[1]-rig['source_translation_z'], point[2])
        base = tuple(round(v*10000) for v in p)
        candidates = [i for delta in itertools.product((-1, 0, 1), repeat=3)
                      for i in grid.get(tuple(a+b for a, b in zip(base, delta)), [])]
        candidates = [i for i in candidates
                      if max(abs(a-b) for a, b in zip(source_corners[i][0], p)) < 2e-6
                      and max(abs(a-b) for a, b in zip(source_corners[i][1], uv)) < 1e-6]
        assert candidates, 'Unmatched source position/UV corner'
        i = min(candidates)
        mapping.append(canonical[i])
        max_position = max(max_position, max(abs(a-b) for a, b in zip(source_corners[i][0], p)))
        max_uv = max(max_uv, max(abs(a-b) for a, b in zip(source_corners[i][1], uv)))
    original_triangles = Counter(tuple(sorted(canonical[i] for i in src_indices[j:j+3]))
                                 for j in range(0, len(src_indices), 3))
    exported_triangles = Counter(tuple(sorted(mapping[i] for i in indices[j:j+3]))
                                 for j in range(0, len(indices), 3))
    assert original_triangles == exported_triangles, 'Rest geometry/UV topology changed'
    contacts = read(ROOT / 'validation/contact_reference.json')
    maximum_reach_error = max(v for frames in contacts.values() for f in frames for v in f['reach_error'].values())
    assert maximum_reach_error < 1e-5, 'Unreachable foot trajectory'
    reports = {}
    for label in ('blend', 'glb', 'fbx'):
        report = read(ROOT / 'validation' / (label+'_review.json'))
        assert report['input_sha256'] == sha(ROOT / report['input']), 'Stale '+label+' evidence'
        assert report['triangles'] == 12476 and set(report['bones']) == set(names)
        assert report['unweighted_vertices'] == 0 and report['max_influences'] <= 4
        assert report['max_weight_sum_error'] < 1e-5 and not report['missing_weight_bones']
        assert {c['name'] for c in report['clips']} == set(specs)
        maximum_foot_error = maximum_stance_drift = maximum_loop_seam = 0.0
        for clip in report['clips']:
            spec = specs[clip['name']]
            assert clip['nonfinite_points'] == 0 and clip['fcurves'] > 0
            if spec['loop']:
                maximum_loop_seam = max(maximum_loop_seam, clip['loop_position_seam'])
                assert clip['loop_position_seam'] < 1e-4
            reference = contacts[clip['name']]
            for frame, (feet, ref) in enumerate(zip(clip['feet'], reference)):
                for key, point in feet.items():
                    expected = ref['feet'][key]['paw']
                    error = math.dist(point, expected)
                    maximum_foot_error = max(maximum_foot_error, error)
                    assert error < 2e-4, label+' paw transform disagrees with baked reference'
                    # World contact under the declared virtual in-place travel.
                    if spec.get('gait') and frame and ref['feet'][key]['stance'] and reference[frame-1]['feet'][key]['stance']:
                        speed = ref['feet'][key]['virtual_speed']
                        prev = clip['feet'][frame-1][key]
                        drift = math.dist((point[0], point[1]-speed/catalog['fps'], point[2]), prev)
                        # A modulo wrap begins a new planted interval.
                        phase_index = list(ref['feet']).index(key)
                        phase = (frame/(spec['frames']-1)+spec['phases'][phase_index]) % 1
                        previous_phase = ((frame-1)/(spec['frames']-1)+spec['phases'][phase_index]) % 1
                        if phase >= previous_phase:
                            maximum_stance_drift = max(maximum_stance_drift, drift)
            # Correct injured limb is held clear while other limbs retain contacts.
            if spec.get('affected_limb'):
                key = spec['affected_limb']
                assert all(not f['feet'][key]['stance'] for f in reference)
                assert min(f['feet'][key]['paw'][2] for f in reference) > .10
        assert maximum_stance_drift < 2e-4, 'Planted gait paw sliding exceeds reference tolerance'
        reports[label] = {'maximum_foot_reference_error': maximum_foot_error,
                          'maximum_gait_stance_step_drift': maximum_stance_drift,
                          'maximum_loop_mesh_seam': maximum_loop_seam,
                          'sampled_minimum_mesh_z': min(c['sampled_minimum_mesh_z'] for c in report['clips']),
                          'sampled_maximum_edge_ratio': max(c['sampled_edge_ratio_max'] for c in report['clips'])}
    attachments = read(ROOT / 'metadata/attachments.json')['sockets']
    assert len(attachments) == 19 and all(a['bone'] in names for a in attachments)
    assert len({a['name'] for a in attachments}) == 19
    # Every requested animation has its own real standalone FBX, not just a name.
    for name in specs:
        path = ROOT / 'animations' / (name+'.fbx')
        assert path.read_bytes().startswith(b'Kaydara FBX Binary') and path.stat().st_size > 10000
    manifest_path = ROOT / 'validation/artifact_manifest.json'
    if manifest_path.exists():
        manifest = read(manifest_path)
        files = {p.relative_to(ROOT).as_posix(): p for p in ROOT.rglob('*')
                 if p.is_file() and p != manifest_path and p.suffix not in ('.blend1', '.pyc') and '__pycache__' not in p.parts}
        assert {e['path'] for e in manifest['files']} == set(files)
        for entry in manifest['files']:
            path = files[entry['path']]
            assert path.stat().st_size == entry['bytes'] and sha(path) == entry['sha256'], entry['path']
    return {'structural_status': 'PASS', 'environment': 'offline stdlib + pinned Blender reimport evidence; not PZ',
            'bones': 42, 'clips': 37, 'triangles': 12476, 'sockets': 19, 'additional_credits': 0,
            'source_position_max_error': max_position, 'source_uv_max_error': max_uv,
            'embedded_pbr_bytes_preserved': True, 'maximum_reach_error': maximum_reach_error,
            'roundtrips': reports, 'deformation_quality': 'PROVISIONAL; see visual review/blockers, structural PASS is not animation acceptance',
            'native': 'NOT TESTED', 'dedicated': 'NOT TESTED', 'G7': 'BLOCKED / NOT TESTED', 'G8': 'BLOCKED'}


if __name__ == '__main__':
    print(json.dumps(check(), indent=2))
