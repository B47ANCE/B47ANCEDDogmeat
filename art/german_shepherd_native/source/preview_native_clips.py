"""Local read-only native clip samples on our dog; no clip data is saved/exported."""
import argparse,hashlib,importlib.util,json,re,sys
from pathlib import Path
import bpy
from mathutils import Matrix,Quaternion,Vector
HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('builder',HERE/'build_native.py');b=importlib.util.module_from_spec(spec);spec.loader.exec_module(b)
parser=argparse.ArgumentParser();parser.add_argument('--game-root',type=Path,required=True);args=parser.parse_args(sys.argv[sys.argv.index('--')+1:])
bones,bind,offsets,_,_=b.playback_contract(args.game_root)
bpy.ops.wm.open_mainfile(filepath=str(HERE/'shepherd_native.blend'))
rig=next(o for o in bpy.data.objects if o.type=='ARMATURE')
for obj in bpy.data.objects:
 if obj.type=='MESH':obj.hide_render=obj.name!='B47Dogmeat_GSD_Coat2'

from native_clip_reader import tracks,sample

report={'environment':'Local Blender samples of installed clips; NOT PZ playback','clips':[],'native_clips_exported':False}
for name,fraction in [('Rac_Idle01',0),('Rac_Walk',.25),('Rac_Run',.25),('Rac_Death',1)]:
 path=args.game_root/'media/anims_X/Raccoon'/(name+'.x');data=tracks(path);end=max(k[0] for channels in data.values() for keys in channels.values() for k in keys);time=end*fraction
 globals={}
 for bone in bones:
  n=bone['name'];channels=data[n];local=Matrix.LocRotScale(sample(channels[2],time),sample(channels[0],time,True),sample(channels[1],time))
  globals[n]=globals[bone['parent']]@local if bone['parent'] else local
  desired=b.C@b.H@globals[n]@b.H;rest=rig.data.bones[n].matrix_local
  if bone['parent']:
   parent=bone['parent'];local_rest=rig.data.bones[parent].matrix_local.inverted()@rest
   local_pose=(b.C@b.H@globals[parent]@b.H).inverted()@desired
  else:local_rest=rest;local_pose=desired
  rig.pose.bones[n].matrix_basis=local_rest.inverted()@local_pose
 bpy.context.scene.render.filepath=str(b.OUT/'previews'/(name+'.png'));bpy.ops.render.render(write_still=True)
 report['clips'].append({'name':name,'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'fraction':fraction,'bone_tracks':len(data),'render':name+'.png'})
(b.OUT/'validation/clip-samples.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8',newline='\n')
print('LOCAL CLIP SAMPLES COMPLETE; BLEND and all exports unchanged')
