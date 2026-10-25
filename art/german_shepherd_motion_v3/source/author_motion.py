"""Original dog-pivot animation; immutable model meshes and native bone names.

Skin source must first be built with build_skin.py.
Run with Blender --background --factory-startup --python this.py -- [--preview].
No installed animation is read. The existing approved bind is read from our BLEND.
"""
import argparse, hashlib, json, math, sys
from pathlib import Path
import bpy
from mathutils import Matrix, Quaternion, Vector

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / 'art/german_shepherd_motion_v3'
MODEL = OUT
sys.path.insert(0, str(ROOT / 'art/german_shepherd_motion_v2/source'))
sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(ROOT / 'art/german_shepherd_native/source'))
from build_native import C, H, mesh_hash

FPS = 30
HEALTH_POSES=[('Low',0),('H125',.125),('H25',.25),('H375',.375),('H50',.5),('H625',.625),('H75',.75),('H875',.875),('High',1)]
IDENTITY = Matrix.Identity(4)
import numpy as np
import anatomy as fit
from head_rig import ATLAS,NECK_BASE,HEAD_PITCH
SKIN_CACHE=[]
SKIN_SIZE=0
FLOOR_OFFSETS={}
FOOT_POINTS={}

def around(point, angle, axis='Y'):
    return Matrix.Translation(point) @ Matrix.Rotation(angle,4,axis) @ Matrix.Translation(-point)

def smooth(x):
    x=max(0,min(1,x));return x*x*(3-2*x)

def segment(a,b,p,q):
    """Rigid transformation from a rest segment to the posed segment (no scale)."""
    return Matrix.Translation(p) @ (b-a).rotation_difference(q-p).to_matrix().to_4x4() @ Matrix.Translation(-a)

def ik(a,b,c,p,q,fold=0):
    """Two fixed-length bones with the rest bend direction as a stable pole."""
    l1=(b-a).length;l2=(c-b).length;delta=q-p;distance=delta.length
    distance=max(abs(l1-l2)+1e-6,min(distance,l1+l2-1e-6));direction=delta.normalized()
    q=p+direction*distance
    rest_direction=(c-a).normalized();pole=(b-a)-rest_direction*(b-a).dot(rest_direction)
    if fold:pole=pole.normalized().lerp(Vector((0,0,1)),fold).normalized()
    pole=pole-direction*pole.dot(direction)
    if pole.length<1e-7:pole=Vector((1,0,0))-direction*direction.x
    pole.normalize()
    along=(l1*l1-l2*l2+distance*distance)/(2*distance)
    joint=p+direction*along+pole*math.sqrt(max(0,l1*l1-along*along))
    return joint,q

BACK=Vector(fit.BACK);SIDE=Vector(fit.SIDE);UP=Vector((0,0,1))
LIMBS={k:list(map(Vector,v)) for k,v in fit.LIMBS.items()};TAIL=list(map(Vector,fit.TAIL))
def rotation(angle):return Matrix.Rotation(angle,4,SIDE)
def pivot(p,angle):return Matrix.Translation(p)@rotation(angle)@Matrix.Translation(-p)

def paw_transform(side,part,paw,target,roll,lift,gait):
 # Roll about the toe rather than sinking the toe below the floor. The actual
 # supplied sole surface sets contact height; the mesh itself is never edited.
 toe=paw-BACK*.07-UP*.0412
 result=Matrix.Translation(target-paw)@Matrix.Translation(toe)@rotation(roll)@Matrix.Translation(-toe)
 if gait:
  points=FOOT_POINTS[(side,part)];m=np.array(result)
  lowest=float((points@m[:3,:3].T+m[:3,3])[:,2].min())
  result=Matrix.Translation(UP*(-.831+lift-lowest))@result
 return result
def solve(a,b,c,p,q,sign,preference=None):
 l1=(b-a).length;l2=(c-b).length;v=q-p;d=min(l1+l2-1e-5,max(abs(l1-l2)+1e-5,v.length));v.normalize();adjusted=p+v*d
 REACH_ERRORS.append((q-adjusted).length);q=adjusted
 hint=BACK*sign if preference is None else preference
 pole=hint-v*hint.dot(v);pole.normalize();along=(l1*l1-l2*l2+d*d)/(2*d)
 joint=p+v*along+pole*math.sqrt(max(0,l1*l1-along*along))
 LENGTH_ERRORS.extend([abs((joint-p).length-l1),abs((q-joint).length-l2)])
 return joint,q
REACH_ERRORS=[]
LENGTH_ERRORS=[]
def pose(kind,t,health=None):
 REACH_ERRORS.clear()
 LENGTH_ERRORS.clear()
 phase=0 if kind=='Dead' else 2*math.pi*t;gait=kind in ('Walk','Run')
 death=smooth(t) if kind=='Death' else 1 if kind=='Dead' else 0
 rest_time=t if kind=='LieDown' else 1-t if kind=='GetUp' else 1 if kind=='Lie' else 0
 lie=smooth(rest_time)
 body=Matrix.Translation(UP*(-.52*lie+(-.06 if kind=='Walk' else -.10 if kind=='Run' else 0)+(.005*math.cos(2*phase) if gait else 0)))
 D={n:body.copy() for n in BONE_NAMES};D['Dummy01']=Matrix.Identity(4);D['Translation_Data']=Matrix.Identity(4)
 chest=body.copy();pelvis=body.copy()
 if gait:
  chest=body@Matrix.Translation((-.35,.08,.08))@Matrix.Rotation(.018*math.sin(phase),4,BACK)@Matrix.Translation((.35,-.08,-.08))
  pelvis=body@Matrix.Translation((.42,.28,.08))@Matrix.Rotation(.025*math.sin(phase+.7),4,UP)@Matrix.Translation((-.42,-.28,-.08))
 elif lie:
  front_settle=smooth(rest_time/.85);rear_settle=smooth((rest_time-.12)/.88)
  chest=Matrix.Translation(UP*(-.52*front_settle));pelvis=Matrix.Translation(UP*(-.52*rear_settle))
 D['Bip01_Spine']=chest;D['Bip01_Pelvis']=pelvis
 for n in ('Bip01_Neck','Bip01_Head','Bip01_HeadNub','Bip01_L_Clavicle','Bip01_R_Clavicle'):D[n]=chest.copy()
 for (side,part),(a,b,c,paw) in LIMBS.items():
  if not gait and not lie and not death:continue
  lift=0.;roll=0.;shift=Vector((0,0,0))
  if gait:
   offsets={('L','rear'):0,('L','front'):.25,('R','rear'):.5,('R','front'):.75} if kind=='Walk' else {('L','front'):0,('R','rear'):0,('R','front'):.5,('L','rear'):.5}
   phase_=(t+offsets[(side,part)])%1;duty=.64 if kind=='Walk' else .51;stride=.16 if kind=='Walk' else .22
   if phase_<duty:
    u=phase_/duty;shift=BACK*(-stride+2*stride*u);roll=-math.radians(12)*smooth((u-.65)/.35)
   else:
    u=(phase_-duty)/(1-duty);shift=BACK*(stride-2*stride*smooth(u));lift=(.075 if kind=='Walk' else .13)*math.sin(math.pi*u)**1.5;roll=-math.radians(12)*(1-smooth(u))+math.radians(22)*math.sin(math.pi*u)**2
  if lie:
   settle=front_settle if part=='front' else rear_settle
   shift=BACK*((-.30 if part=='front' else .16)*settle)+SIDE*((-.035 if side=='L' else .035)*settle)
  # Individual standing paws have different supplied ground heights.
  ground={('L','front'):0,('R','front'):-.0253,('L','rear'):-.0231,('R','rear'):-.0228}[(side,part)]
  targetpaw=paw+shift+UP*(lift+ground*(1 if gait else lie))
  if death:
   # Relax each leg into the side-resting body's plane before the roll.
   relax=smooth(t) if kind=='Death' else 1
   lateral=.16 if side=='L' else .28
   targetpaw+=relax*(SIDE*(lateral-paw.dot(SIDE))+UP*(.14 if part=='front' else .03)+BACK*(.04 if part=='front' else .10))
  if part=='front':
   foot=paw_transform(side,part,paw,targetpaw,roll,lift,gait);targetpaw=foot@paw
   wrist=foot@c
   if lie:wrist=wrist.lerp(targetpaw+(BACK*(c-paw).length+UP*.08).normalized()*(c-paw).length,front_settle)
   joint,wrist=solve(a,b,c,chest@a,wrist,1)
   D['Bip01_'+side+'_UpperArm']=segment(a,b,chest@a,joint)
   D['Bip01_'+side+'_Forearm']=segment(b,c,joint,wrist)
   D['Bip01_'+side+'_Hand']=segment(c,paw,wrist,targetpaw)
   for n in ('Finger0','Finger0Nub'):D['Bip01_'+side+'_'+n]=foot
  else:
   desired=c-paw
   if lie:
    flat=BACK*desired.length+UP*.135;desired=desired.lerp(flat,rear_settle)
   toe=paw_transform(side,part,paw,targetpaw,roll,lift,gait)
   footrot=(c-paw).rotation_difference(desired).to_matrix().to_4x4()
   foot=toe@Matrix.Translation(paw)@footrot@Matrix.Translation(-paw)
   preference=-BACK+SIDE*((-.5 if side=='L' else .5)*rear_settle) if lie else None
   hock=foot@c;joint,hock=solve(a,b,c,pelvis@a,hock,-1,preference)
   D['Bip01_'+side+'_Thigh']=segment(a,b,pelvis@a,joint)
   D['Bip01_'+side+'_Calf']=segment(b,c,joint,hock)
   D['Bip01_'+side+'_Foot']=foot
   for n in ('Toe0','Toe0Nub'):D['Bip01_'+side+'_'+n]=toe
 # Three distinct rigid tail segments follow one continuous, fixed-length curve.
 amount=0 if health is None else health
 points=[pelvis@TAIL[0]]
 for i,(p,q) in enumerate(zip(TAIL,TAIL[1:])):
  rest=q-p;angle=math.radians([8,-12,-35][i]);target=BACK*math.cos(angle)+UP*math.sin(angle)
  direction=Quaternion().slerp(rest.normalized().rotation_difference(target),amount)@rest.normalized()
  if lie:
   # Rest on the floor behind the haunch instead of pitching through it.
   angle=math.radians([-40,-14,-2][i]);resting=(BACK*math.cos(angle)+UP*math.sin(angle)+SIDE*.18).normalized()
   direction=direction.lerp(resting,lie).normalized()
  direction=(Matrix.Rotation(.015*math.sin(phase-i*.4),4,UP)@direction).normalized()
  points.append(points[-1]+direction*rest.length)
  name='Bip01_Tail'+(str(i) if i else '');D[name]=segment(p,q,points[-2],points[-1])
 D['Bip01_TailNub']=D['Bip01_Tail2'].copy()

 # The supplied skull faces nearly -Y, independently of torso BACK. Rotate
 # the rigid face around its atlas; the neck follows the shoulder separately.
 pitch=math.radians(.7)*math.sin(phase);yaw=0.
 if kind=='Look':
  yaw=math.radians(25)*math.sin(phase)
  pitch=math.radians(12)*math.sin(2*phase)
 neck=chest.copy()
 if kind=='Eat':
  eat=.5-.5*math.cos(phase)
  neck=neck@around(Vector(NECK_BASE),math.radians(12)*eat,Vector(HEAD_PITCH))
  pitch=math.radians(15)*eat
 head=neck@around(Vector(ATLAS),yaw,UP)@around(Vector(ATLAS),pitch,Vector(HEAD_PITCH))
 D['Bip01_Neck']=neck
 for n in ('Bip01_Head','Bip01_HeadNub'):D[n]=head.copy()
 if death:
  roll=smooth((t-.30)/.70) if kind=='Death' else 1
  unturn=Matrix.Translation((-.49,.035,.19))@Matrix.Rotation(-.12*roll,4,BACK)@Matrix.Rotation(-.47*roll,4,UP)@Matrix.Translation((.49,-.035,-.19))
  for n in ('Bip01_Neck','Bip01_Head','Bip01_HeadNub'):D[n]=D[n]@unturn
  center=Vector((.04,.18,.08))
  collapse=Matrix.Translation(center)@Matrix.Rotation(math.radians(-90)*roll,4,BACK)@Matrix.Translation(-center)
  for n in D:
   if n not in ('Dummy01','Translation_Data'):D[n]=collapse@D[n]
  # Actual weighted source surface supplies the collapse-floor correction.
  key=round(t if kind=='Death' else 1,8)
  if key not in FLOOR_OFFSETS:
   surface=np.zeros((SKIN_SIZE,3),np.float64)
   for name,indices,co,weight in SKIN_CACHE:
    matrix=np.array(D[name]);surface[indices]+=(co@matrix[:3,:3].T+matrix[:3,3])*weight[:,None]
   FLOOR_OFFSETS[key]=-.830-float(surface[:,2].min())
  correction=Matrix.Translation(UP*FLOOR_OFFSETS[key])
  for n in D:
   if n not in ('Dummy01','Translation_Data'):D[n]=correction@D[n]
 if kind=='Hit':
  recoil=Matrix.Translation(BACK*(.025*math.sin(math.pi*t)))
  for n in D:
   if n not in ('Dummy01','Translation_Data'):D[n]=recoil@D[n]
 contacts=[{'stance':True,'target_error':error} for error in REACH_ERRORS]
 return D,contacts,max(LENGTH_ERRORS or [0])

def native_locals(transforms):
    globals_={n:AXIS.inverted()@PLACEMENT@transforms[n]@PLACEMENT.inverted()@REST[n]@H for n in BONE_NAMES}
    return {n:globals_[PARENTS[n]].inverted()@globals_[n] if PARENTS[n] else globals_[n] for n in BONE_NAMES}

def f(value):
    # Assimp's X reader requires a decimal float token even for zero/one.
    return format(float(value),'.12f')

def write_x(name,frames):
    lines=['xof 0303txt 0032','AnimTicksPerSecond { 30; }']
    rest=native_locals({n:IDENTITY for n in BONE_NAMES})
    def frame(n,indent=''):
        values=[rest[n][row][col] for col in range(4) for row in range(4)]
        lines.extend([indent+'Frame '+n+' {',indent+' FrameTransformMatrix { '+','.join(map(f,values))+';; }'])
        for child in BONE_NAMES:
            if PARENTS[child]==n:frame(child,indent+' ')
        lines.append(indent+'}')
    for n in BONE_NAMES:
        if PARENTS[n] is None:frame(n)
    lines.append('AnimationSet '+name+' {')
    for n in BONE_NAMES:
        lines.append(' Animation { { '+n+' }')
        decomposed=[frame_[n].decompose() for frame_ in frames]
        for key,width in [(0,4),(1,3),(2,3)]:
            lines.append('  AnimationKey K'+str(key)+' { '+str(key)+'; '+str(len(frames))+';')
            previous=None
            for i,(loc,rot,scale) in enumerate(decomposed):
                if key==0:
                    q=rot.conjugated()
                    if previous is not None and previous.dot(q)<0:q.negate()
                    previous=q.copy();value=q
                elif key==1:value=(1,1,1)
                else:value=loc
                lines.append('   '+str(i)+';'+str(width)+';'+','.join(map(f,value))+';;'+(';' if i==len(frames)-1 else ','))
            lines.append('  }')
        lines.append(' }')
    lines.append('}')
    path=OUT/'anims'/ (name+'.x');path.write_text('\n'.join(lines)+'\n',encoding='utf-8',newline='\n')
    return path

def apply_pose(rig,transforms):
    desired={n:PLACEMENT@transforms[n]@PLACEMENT.inverted()@REST[n] for n in BONE_NAMES}
    for n in BONE_NAMES:
        local_rest=REST[PARENTS[n]].inverted()@REST[n] if PARENTS[n] else REST[n]
        local_pose=desired[PARENTS[n]].inverted()@desired[n] if PARENTS[n] else desired[n]
        rig.pose.bones[n].matrix_basis=local_rest.inverted()@local_pose

def apply_health_blend(rig,kind,t,health):
    """Preview the exported endpoint blend in bone-local space, not a new pose."""
    index=min(7,int(health*8));fraction=health*8-index
    low=native_locals(pose(kind,t,index/8)[0]);high=native_locals(pose(kind,t,(index+1)/8)[0]);globals_={}
    for n in BONE_NAMES:
        a,qa,_=low[n].decompose();b,qb,_=high[n].decompose()
        if qa.dot(qb)<0:qb.negate()
        q=Quaternion(tuple(qa[i]*(1-fraction)+qb[i]*fraction for i in range(4)));q.normalize()
        local=Matrix.LocRotScale(a.lerp(b,fraction),q,Vector((1,1,1)))
        globals_[n]=globals_[PARENTS[n]]@local if PARENTS[n] else local
        desired=AXIS@globals_[n]@H
        local_rest=REST[PARENTS[n]].inverted()@REST[n] if PARENTS[n] else REST[n]
        local_pose=(AXIS@globals_[PARENTS[n]]@H).inverted()@desired if PARENTS[n] else desired
        rig.pose.bones[n].matrix_basis=local_rest.inverted()@local_pose

def main():
    global REST,PARENTS,BONE_NAMES,PLACEMENT,AXIS,SKIN_CACHE,SKIN_SIZE,FOOT_POINTS
    parser=argparse.ArgumentParser();parser.add_argument('--preview',action='store_true');parser.add_argument('--only-preview',action='store_true');parser.add_argument('--preview-filter',default='');args=parser.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
    bpy.ops.wm.open_mainfile(filepath=str(MODEL/'source/shepherd_reweighted.blend'))
    rig=next(o for o in bpy.data.objects if o.type=='ARMATURE');objects=[o for o in bpy.data.objects if o.type=='MESH']
    for bone in rig.pose.bones:bone.rotation_mode='QUATERNION'
    reference=next(o for o in objects if o.name.endswith('Coat2'))
    co=np.empty(len(reference.data.vertices)*3,np.float32);reference.data.vertices.foreach_get('co',co);co=co.reshape(-1,3)
    names=[g.name for g in reference.vertex_groups];skin=np.zeros((len(co),len(names)),np.float32)
    for vertex in reference.data.vertices:
        for group in vertex.groups:skin[vertex.index,group.group]=group.weight
    SKIN_SIZE=len(co);SKIN_CACHE=[]
    for i,name in enumerate(names):
        indices=np.flatnonzero(skin[:,i]);SKIN_CACHE.append((name,indices,co[indices],skin[indices,i]))
    for (side,part) in LIMBS:
        terms=('Clavicle','UpperArm','Forearm','Hand','Finger') if part=='front' else ('Thigh','Calf','Foot','Toe')
        columns=[i for i,n in enumerate(names) if n.startswith('Bip01_'+side+'_') and any(term in n for term in terms)]
        FOOT_POINTS[(side,part)]=co[(co[:,2]<-.76)&(skin[:,columns].sum(axis=1)>.999)]

    REST={b.name:b.matrix_local.copy() for b in rig.data.bones};PARENTS={b.name:b.parent.name if b.parent else None for b in rig.data.bones};BONE_NAMES=list(REST)
    PLACEMENT=objects[0].matrix_world.copy();AXIS=C@H
    for folder in ['anims','previews','validation']:(OUT/folder).mkdir(parents=True,exist_ok=True)
    specifications={'Idle':2,'Look':3,'Walk':1.2,'Run':.7,'LieDown':1.3,'Lie':2,'GetUp':1.3,'Eat':2,'Hit':.5,'Death':1.1,'Dead':1}
    report={'project_version':(ROOT/'VERSION').read_text().strip(),'asset_revision':'gsd-rest-head-v003','environment':'Blender '+bpy.app.version_string+' offline','runtime':'NOT TESTED','mesh_geometry_uv_untouched':{},'clips':{},'max_bone_length_error':0,'max_stance_target_error':0,'bone_count':len(BONE_NAMES),'native_motion_tracks_read':False,'gait':'Fitted four-beat walk and diagonal trot; same native hierarchy','tail_root':list(fit.TAIL[0]),'visual_acceptance':'Candidate; PZ NOT TESTED'}
    for obj in objects:report['mesh_geometry_uv_untouched'][obj.name]=mesh_hash(obj.data)
    if not args.only_preview:
        for kind,duration in specifications.items():
            frames_count=round(duration*FPS)
            for suffix,health in [('Neutral',None)]+(HEALTH_POSES if kind in ('Idle','Look','Walk','Run') else []):
                name='B47Dogmeat_'+kind+'_'+suffix;frames=[]
                for frame_ in range(frames_count+1):
                    transforms,contacts,error=pose(kind,frame_/frames_count,health)
                    report['max_bone_length_error']=max(report['max_bone_length_error'],error)
                    if kind in ('Walk','Run'):
                        report['max_stance_target_error']=max(report['max_stance_target_error'],*(p['target_error'] for p in contacts if p['stance']))
                    frames.append(native_locals(transforms))
                path=write_x(name,frames)
                # Independently decode the emitted X text and compare the complete transforms.
                from native_clip_reader import tracks,sample
                decoded=tracks(path);max_error=0
                for fi,expected in enumerate(frames):
                    for n in BONE_NAMES:
                        channels=decoded[n];actual=Matrix.LocRotScale(sample(channels[2],fi),sample(channels[0],fi,True),sample(channels[1],fi))
                        max_error=max(max_error,max(abs(actual[i][j]-expected[n][i][j]) for i in range(4) for j in range(4)))
                assert max_error<2e-5,(name,max_error)
                report['clips'][name]={'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'frames':len(frames),'duration_seconds':frames_count/FPS,'x_matrix_roundtrip_error':max_error}
        (OUT/'validation/motion.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8',newline='\n')
        # Small editable animation source linked to the unchanged model checkpoint.
        editable=[(name,seconds,suffix,health) for name,seconds in specifications.items()
                  for suffix,health in [('Neutral',None)]+(HEALTH_POSES if name in ('Idle','Look','Walk','Run') else [])]
        for name,seconds,suffix,health in editable:
            action=bpy.data.actions.new('B47Dogmeat_'+name+'_'+suffix);action.use_fake_user=True
            rig.animation_data_create();rig.animation_data.action=action
            count=round(seconds*FPS)
            for fi in range(count+1):
                apply_pose(rig,pose(name,fi/count,health)[0])
                for pb in rig.pose.bones:
                    pb.keyframe_insert('location',frame=fi+1);pb.keyframe_insert('rotation_quaternion',frame=fi+1);pb.keyframe_insert('scale',frame=fi+1)
        rig.animation_data_clear();apply_pose(rig,{n:IDENTITY for n in BONE_NAMES})
        motion_scene=bpy.data.scenes.new('ShepherdMotionSource');motion_scene.collection.objects.link(rig)
        motion_scene.render.fps=FPS;motion_scene.frame_end=90
        motion_scene['model_checkpoint']='art/german_shepherd_motion_v3/source/shepherd_reweighted.blend'
        motion_scene['scope']='Editable original motion; reweighted supplied meshes remain in the separate source checkpoint.'
        bpy.data.libraries.write(str(OUT/'source/shepherd_motion.blend'),set([motion_scene]+list(bpy.data.actions)),fake_user=True,compress=True)
        print('MOTION_EXPORT',json.dumps(report),flush=True)
    if args.preview or args.only_preview:
        scene=bpy.context.scene;scene.render.resolution_x=800;scene.render.resolution_y=600;scene.cycles.samples=4
        bpy.ops.mesh.primitive_plane_add(size=200)
        floor=bpy.context.object;floor.name='ReviewOnlyFloor';floor.matrix_world=PLACEMENT@Matrix.Translation((0,0,-.8312))
        floor_material=bpy.data.materials.new('ReviewOnlyFloor');floor_material.diffuse_color=(.12,.12,.12,1);floor.data.materials.append(floor_material)
        # A fixed three-quarter view makes both front and rear leg motion visible.
        center=PLACEMENT@Vector((.16,.15,-.03));cam=scene.camera
        cam.location=PLACEMENT@(Vector((.16,.15,-.03))-SIDE*7-BACK*2+UP*1.5);cam.rotation_euler=(center-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=3.6/4.3212890625
        cases=[('Walk',i/24,None) for i in range(24)]+[('Run',i/24,1) for i in range(24)]+[('LieDown',i/8,None) for i in range(9)]+[('Idle',0,h) for h in (0,.125,.25,.375,.5,.625,.75,.875,1)]+[('Lie',0,None),('GetUp',.5,None),('Eat',.5,None),('Hit',.5,None),('Death',.5,None),('Dead',0,None)]
        cases += [('Look',i/24,None) for i in range(24)]+[('GetUp',i/8,None) for i in range(9)]
        for obj in objects:
            if obj.name.endswith('Original'):continue
            for other in objects:other.hide_render=other!=obj
            selected=cases if obj.name.endswith('Coat2') else [('Idle',0,0),('Idle',0,1),('Walk',.25,None),('Run',.75,1),('Lie',0,None),('Dead',0,None),('Look',.25,None),('Look',.75,None)]
            for idx,(kind,phase,health) in enumerate(selected):
                if args.preview_filter and kind not in args.preview_filter.split(','):continue
                if health is None:apply_pose(rig,pose(kind,phase)[0])
                else:apply_health_blend(rig,kind,phase,health)
                scene.render.filepath=str(OUT/'previews'/(obj.name+'_'+str(idx).zfill(2)+'_'+kind+'.png'))
                bpy.ops.render.render(write_still=True)
                print('PREVIEW',obj.name,idx,kind,phase,health,flush=True)
    print('COMPLETE: motion exported; geometry, UVs, textures and bind unchanged; revised skin source is separate',flush=True)

if __name__=='__main__':main()
