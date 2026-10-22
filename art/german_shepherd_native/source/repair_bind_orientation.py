"""Bind the authoring checkpoint to native idle globals; retain immutable geometry."""
import argparse,sys
from pathlib import Path
import bpy
sys.path.insert(0,str(Path(__file__).resolve().parent))
import build_native as b
parser=argparse.ArgumentParser();parser.add_argument('--game-root',type=Path,required=True)
args=parser.parse_args(sys.argv[sys.argv.index('--')+1:])
bones,bind,offsets,_,_=b.playback_contract(args.game_root)
bpy.ops.wm.open_mainfile(filepath=str(b.OUT/'source/shepherd_native.blend'))
rig=next(o for o in bpy.data.objects if o.type=='ARMATURE')
hashes={o.name:b.mesh_hash(o.data) for o in bpy.data.objects if o.type=='MESH'}
bpy.context.view_layer.objects.active=rig;bpy.ops.object.mode_set(mode='EDIT')
for bone in bones:
 eb=rig.data.edit_bones[bone['name']];eb.matrix=b.C@b.H@bind[bone['name']]@b.H
bpy.ops.object.mode_set(mode='OBJECT')
for bone in bones:
 actual=rig.data.bones[bone['name']].matrix_local;expected=b.C@b.H@bind[bone['name']]@b.H
 assert max(abs(actual[i][j]-expected[i][j]) for i in range(4) for j in range(4))<3e-5
assert hashes=={o.name:b.mesh_hash(o.data) for o in bpy.data.objects if o.type=='MESH'}
bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(b.OUT/'source/shepherd_native.blend'),compress=True)
print('BIND ORIENTATION REPAIRED; geometry and UV hashes unchanged')
