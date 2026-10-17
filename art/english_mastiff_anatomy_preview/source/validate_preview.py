"""Read-only inventory and pinned import-evidence checks, not anatomy acceptance."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    manifest = json.loads((ROOT / 'validation/artifact_manifest.json').read_text())
    actual = {p.relative_to(ROOT).as_posix(): p for p in ROOT.rglob('*') if p.is_file()
              and p.name != 'artifact_manifest.json' and p.suffix not in ('.blend1', '.pyc')
              and '__pycache__' not in p.parts}
    assert {e['path'] for e in manifest['files']} == set(actual) and len(manifest['files']) == len(actual)
    for entry in manifest['files']:
        path = (ROOT / entry['path']).resolve()
        assert path.is_relative_to(ROOT) and path.stat().st_size == entry['bytes']
        assert sha(path) == entry['sha256'], entry['path']
    reports = []
    for label in ('geometry_preview', 'geometry_fbx'):
        report = json.loads((ROOT / 'validation' / (label+'.json')).read_text())
        assert report['asset_revision'] == 'em-v003-preview'
        assert sha(ROOT / report['source']) == report['sha256']
        assert report['triangles'] == 23865
        assert report['armatures'] == report['animations'] == 0 and not report['textures']
        assert len(report['meshes']) == 1
        mesh = report['meshes'][0]
        assert mesh['uv_layers'] == 1 and mesh['nonfinite_coordinates'] == mesh['zero_area_triangles'] == 0
        assert mesh['welded_boundary_edges'] == 52 and mesh['welded_nonmanifold_edges'] == 80
        assert mesh['welded_components_vertices'] == [11942]
        reports.append(report)
    assert max(abs(a-b) for a, b in zip(reports[0]['dimensions_blender_units'],
                                      reports[1]['dimensions_blender_units'])) < 1e-6
    for render in reports[0]['renders']:
        assert sha(ROOT / render['path']) == render['sha256']
    mouth = json.loads((ROOT / 'validation/mouth_views.json').read_text())
    assert mouth['source_model_sha256'] == reports[0]['sha256'] and len(mouth['renders']) == 5
    for render in mouth['renders']:
        assert sha(ROOT / render['path']) == render['sha256']
    scene = reports[0]['editable_source']
    assert sha(ROOT / scene['path']) == scene['sha256']
    generation = json.loads((ROOT / 'generation.json').read_text())
    assert generation['status'] == 'SUCCEEDED' and generation['actual_consumed_credits'] == 20
    assert generation['additional_paid_jobs'] == 0
    assert len(json.loads((ROOT / 'preview-parameters.json').read_text())['prompt']) <= 800
    print(json.dumps({'artifact_integrity': 'PASS', 'files': len(actual),
                      'geometry_acceptance': 'INCOMPLETE / HOLD', 'triangles': 23865,
                      'boundary_edges': 52, 'nonmanifold_edges': 80,
                      'environment': 'Offline files and pinned Blender evidence; not PZ',
                      'credits_this_job': 20, 'native': 'NOT TESTED',
                      'G7': 'BLOCKED / NOT TESTED', 'G8': 'BLOCKED'}, indent=2))


if __name__ == '__main__':
    main()
