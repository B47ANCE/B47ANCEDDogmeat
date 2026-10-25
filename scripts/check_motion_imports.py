"""Independent Assimp X syntax/hierarchy check; does not execute PZ."""
import argparse,hashlib,json,sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]

def check(module_directory=None):
    if module_directory:sys.path.insert(0,str(module_directory))
    import assimp_py
    flags=assimp_py.Process_MakeLeftHanded | assimp_py.Process_RemoveRedundantMaterials
    results=[]
    for path in sorted((ROOT/'art/german_shepherd_motion_v4/anims').glob('*.x')):
        scene=assimp_py.import_file(str(path),flags)
        def nodes(node):return [node.name]+[name for child in node.children for name in nodes(child)]
        hierarchy=nodes(scene.root_node)
        assert len(scene.meshes)==0 and len(hierarchy)==35,(path,len(hierarchy))
        assert len(set(hierarchy))==35 and 'Dummy01' in hierarchy and 'Translation_Data' in hierarchy
        results.append({'file':path.name,'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'nodes':35,'meshes':0})
    assert len(results)==47
    print(json.dumps({'status':'OFFLINE ASSIMP PARSE PASS','parser':'assimp_py 1.1.0','clips':results,
        'limit':'Binding exposes no animation metadata; channel/timing/matrix checks are separate. Not the bundled PZ importer or runtime.'},indent=2))

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--module-directory',type=Path)
    check(parser.parse_args().module_directory)
