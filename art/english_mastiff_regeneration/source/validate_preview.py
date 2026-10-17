"""Read-only inventory/evidence validation for a deliberately unapproved preview."""
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
    assert {entry['path'] for entry in manifest['files']} == set(actual)
    assert len(manifest['files']) == len(actual)
    for entry in manifest['files']:
        path = (ROOT / entry['path']).resolve()
        assert path.is_relative_to(ROOT) and path.stat().st_size == entry['bytes']
        assert sha(path) == entry['sha256'], entry['path']
    reports = []
    for label in ('geometry_preview', 'geometry_fbx'):
        report = json.loads((ROOT / 'validation' / (label+'.json')).read_text())
        assert report['asset_revision'] == 'em-v002-preview'
        assert sha(ROOT / report['source']) == report['sha256']
        assert report['armatures'] == report['animations'] == 0
        assert report['triangles'] == 15601 and len(report['meshes']) == 1
        mesh = report['meshes'][0]
        assert mesh['uv_layers'] == 1 and mesh['nonfinite_coordinates'] == mesh['zero_area_triangles'] == 0
        assert mesh['welded_boundary_edges'] == 18 and mesh['welded_nonmanifold_edges'] == 28
        assert mesh['welded_components_vertices'] == [7799]
        reports.append(report)
    assert max(abs(a-b) for a, b in zip(reports[0]['dimensions_blender_units'],
                                      reports[1]['dimensions_blender_units'])) < 1e-6
    for render in reports[0]['renders']:
        assert sha(ROOT / render['path']) == render['sha256']
    assert len(list((ROOT / 'previews/mouth').glob('*.png'))) == 5
    generation = json.loads((ROOT / 'generation.json').read_text())
    assert generation['consumed_credits'] == 20 and generation['additional_paid_jobs'] == 0
    print(json.dumps({'artifact_integrity': 'PASS', 'files': len(actual),
                      'geometry_acceptance': 'HOLD / NOT APPROVED',
                      'reason': 'Mouth anatomy/articulation not established; 18 boundary and 28 non-manifold edges',
                      'environment': 'offline file + pinned Blender evidence; not PZ',
                      'new_credits': 20, 'native': 'NOT TESTED',
                      'G7': 'BLOCKED / NOT TESTED', 'G8': 'BLOCKED'}, indent=2))


if __name__ == '__main__':
    main()
