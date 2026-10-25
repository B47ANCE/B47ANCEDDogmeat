"""Original dog-pivot animation; immutable model meshes and native bone names.

Run with Blender --background --factory-startup --python this.py -- [--preview].
No installed animation is read. The existing approved bind is read from our BLEND.
"""
import argparse, hashlib, json, math, sys
from pathlib import Path
import bpy
from mathutils import Matrix, Quaternion, Vector

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / 'art/german_shepherd_motion'
MODEL = ROOT / 'art/german_shepherd_native'
sys.path.insert(0, str(MODEL / 'source'))
from build_native import C, H, mesh_hash

FPS = 30
HEALTH_POSES=[('Low',0),('H25',.25),('H50',.5),('H75',.75),('High',1)]
IDENTITY = Matrix.Identity(4)
TAIL = ['Bip01_Tail', 'Bip01_Tail1', 'Bip01_Tail2', 'Bip01_TailNub']
TAIL_POINTS = [Vector(p) for p in [( .64,0,.02),(.76,0,-.25),(.91,0,-.48),(.96,0,-.58)]]
LIMBS = {}
for side, sign in [('L',-1),('R',1)]:
    for kind, points in [('front',[(-.4,.17,-.10),(-.34,.18,-.34),(-.49,.19,-.73),(-.57,.19,-.79)]),
                         ('rear',[(.49,.17,.02),(.55,.18,-.28),(.67,.19,-.6),(.56,.2,-.77)])]:
        LIMBS[(side,kind)] = [Vector((x,sign*y,z)) for x,y,z in points]

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

def pose(kind,t,health=None):
    phase=0 if kind=='Dead' else 2*math.pi*t
    lie=smooth(t) if kind=='LieDown' else 1-smooth(t) if kind=='GetUp' else 1 if kind=='Lie' else 0
    death=smooth(t) if kind=='Death' else 1 if kind=='Dead' else 0
    gait=kind in ('Walk','Run')
    drop=(-.028 if kind=='Walk' else -.055 if kind=='Run' else 0)
    if lie:
        # Relaxed sphinx/sploot rest: extend limbs along the ground instead of
        # forcing extreme IK folds into an immutable, straight-legged mesh.
        minimum=min((around(a,math.radians(65 if part=='front' else -57)*lie)@c).z+(foot-c).z
                    for (side,part),(a,b,c,foot) in LIMBS.items())
        drop=-.79-minimum
    bob=(.004 if kind=='Walk' else .008 if kind=='Run' else .002)*(math.cos(2*phase)-1)
    body=Matrix.Translation((0,0,drop+bob))
    transforms={}
    # Only native locomotion advances the animal. No authored root displacement.
    for name in BONE_NAMES:transforms[name]=body.copy()
    transforms['Dummy01']=IDENTITY.copy();transforms['Translation_Data']=IDENTITY.copy()
    head_angle=.018*math.sin(phase)
    if kind=='Look':head_angle=.075*math.sin(phase)
    if kind=='Eat':head_angle=-.38*(.5-.5*math.cos(phase))
    head=body@around(Vector((-.4,0,.22)),head_angle)
    transforms['Bip01_Neck']=head;transforms['Bip01_Head']=head;transforms['Bip01_HeadNub']=head
    contacts=[];length_errors=[]
    for (side,part),(a,b,c,foot) in LIMBS.items():
        shift=Vector((0,0,0));lift=0;stance=True
        if gait:
            offsets = {('L','rear'):0,('L','front'):.25,('R','rear'):.5,('R','front'):.75} if kind=='Walk' else {('L','front'):0,('R','rear'):0,('R','front'):.5,('L','rear'):.5}
            p=(t+offsets[(side,part)])%1;duty=.68 if kind=='Walk' else .55
            stride=.085 if kind=='Walk' else .14
            if p<duty:shift.x=-stride+2*stride*p/duty
            else:
                u=(p-duty)/(1-duty);shift.x=stride-2*stride*smooth(u)
                lift=(.065 if kind=='Walk' else .12)*math.sin(math.pi*u)**2;stance=False
            shift.z=lift
        target=c+shift;p=body@a;joint,ankle=ik(a,b,c,p,target)
        upper=segment(a,b,p,joint);lower=segment(b,c,joint,ankle)
        foot_transform=Matrix.Translation(ankle-c)
        if part=='front':
            transforms['Bip01_'+side+'_Clavicle']=body
            transforms['Bip01_'+side+'_UpperArm']=upper
            transforms['Bip01_'+side+'_Forearm']=lower
            for name in ('Hand','Finger0','Finger0Nub'):transforms['Bip01_'+side+'_'+name]=foot_transform
        else:
            transforms['Bip01_'+side+'_Thigh']=upper;transforms['Bip01_'+side+'_Calf']=lower
            for name in ('Foot','Toe0','Toe0Nub'):transforms['Bip01_'+side+'_'+name]=foot_transform
        if lie:
            resting=body@around(a,math.radians(65 if part=='front' else -57)*lie)
            parts=('UpperArm','Forearm','Hand','Finger0','Finger0Nub') if part=='front' else ('Thigh','Calf','Foot','Toe0','Toe0Nub')
            for name in parts:transforms['Bip01_'+side+'_'+name]=resting
            # Keep paws facing down while the upper leg extends into rest.
            paw=Matrix.Translation(resting@c-c)
            for name in (('Hand','Finger0','Finger0Nub') if part=='front' else ('Foot','Toe0','Toe0Nub')):
                transforms['Bip01_'+side+'_'+name]=paw
        contacts.append({'side':side,'part':part,'stance':stance,'foot':list(foot_transform@foot),
                         'target_error':(ankle-target).length})
        length_errors.extend([abs((joint-p).length-(b-a).length),abs((ankle-joint).length-(c-b).length)])
    tail_angle=math.radians(-50)*lie if health is None else math.radians(8-65*health)
    # The health signal is elevation, with only a small lateral natural motion.
    tail=body@around(TAIL_POINTS[0],tail_angle)@around(TAIL_POINTS[0],.018*math.sin(phase),'Z')
    for i,name in enumerate(TAIL):
        if i>0:tail=tail@around(TAIL_POINTS[min(i,2)],.015*math.sin(phase-i*.5),'Z')
        transforms[name]=tail.copy()
    if death:
        collapse=Matrix.Translation((0,0,-.30*death))@around(Vector((.1,0,-.4)),math.radians(82)*death,'X')
        for name in transforms:
            if name not in ('Dummy01','Translation_Data'):transforms[name]=collapse@transforms[name]
    if kind=='Hit':
        recoil=Matrix.Translation((.035*math.sin(math.pi*t),0,-.025*math.sin(math.pi*t)))
        for name in transforms:
            if name not in ('Dummy01','Translation_Data'):transforms[name]=recoil@transforms[name]
    return transforms,contacts,max(length_errors)

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
    index=min(3,int(health*4));fraction=health*4-index
    low=native_locals(pose(kind,t,index/4)[0]);high=native_locals(pose(kind,t,(index+1)/4)[0]);globals_={}
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
    global REST,PARENTS,BONE_NAMES,PLACEMENT,AXIS
    parser=argparse.ArgumentParser();parser.add_argument('--preview',action='store_true');parser.add_argument('--only-preview',action='store_true');parser.add_argument('--preview-filter',default='');args=parser.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
    bpy.ops.wm.open_mainfile(filepath=str(MODEL/'source/shepherd_native.blend'))
    rig=next(o for o in bpy.data.objects if o.type=='ARMATURE');objects=[o for o in bpy.data.objects if o.type=='MESH']
    for bone in rig.pose.bones:bone.rotation_mode='QUATERNION'
    REST={b.name:b.matrix_local.copy() for b in rig.data.bones};PARENTS={b.name:b.parent.name if b.parent else None for b in rig.data.bones};BONE_NAMES=list(REST)
    PLACEMENT=objects[0].matrix_world.copy();AXIS=C@H
    for folder in ['anims','previews','validation']:(OUT/folder).mkdir(parents=True,exist_ok=True)
    specifications={'Idle':2,'Look':3,'Walk':1.2,'Run':.7,'LieDown':1.3,'Lie':2,'GetUp':1.3,'Eat':2,'Hit':.5,'Death':1.1,'Dead':1}
    report={'project_version':(ROOT/'VERSION').read_text().strip(),'asset_revision':'gsd-motion-v001','environment':'Blender '+bpy.app.version_string+' offline','runtime':'NOT TESTED','mesh_geometry_uv_untouched':{},'clips':{},'max_bone_length_error':0,'max_stance_target_error':0,'bone_count':len(BONE_NAMES),'native_motion_tracks_read':False,'gait':'Original planted-foot walk and diagonal trot; same native hierarchy'}
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
        motion_scene['model_checkpoint']='art/german_shepherd_native/source/shepherd_native.blend'
        motion_scene['scope']='Editable original motion; supplied meshes remain in the unchanged model checkpoint.'
        bpy.data.libraries.write(str(OUT/'source/shepherd_motion.blend'),set([motion_scene]+list(bpy.data.actions)),fake_user=True,compress=True)
        print('MOTION_EXPORT',json.dumps(report),flush=True)
    if args.preview or args.only_preview:
        scene=bpy.context.scene;scene.render.resolution_x=640;scene.render.resolution_y=640;scene.cycles.samples=8
        bpy.ops.mesh.primitive_plane_add(size=200)
        floor=bpy.context.object;floor.name='ReviewOnlyFloor';floor.matrix_world=PLACEMENT@Matrix.Translation((0,0,-.8312))
        floor_material=bpy.data.materials.new('ReviewOnlyFloor');floor_material.diffuse_color=(.12,.12,.12,1);floor.data.materials.append(floor_material)
        # A fixed three-quarter view makes both front and rear leg motion visible.
        center=PLACEMENT@Vector((0,0,-.08));cam=scene.camera;cam.location=PLACEMENT@Vector((-4,-7,2.2));cam.rotation_euler=(center-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=3.1/4.3212890625
        cases=[('Walk',i/8,None) for i in range(8)]+[('Run',i/8,None) for i in range(8)]+[('Idle',0,h) for h in (0,.25,.5,.75,1)]+[('LieDown',.5,None),('Lie',0,None),('GetUp',.5,None),('Death',.5,None),('Dead',0,None)]+[('Idle',0,h) for h in (.125,.375,.625,.875)]
        for obj in objects:
            if obj.name.endswith('Original'):continue
            for other in objects:other.hide_render=other!=obj
            for idx,(kind,phase,health) in enumerate(cases):
                if args.preview_filter and kind not in args.preview_filter.split(','):continue
                if health is None:apply_pose(rig,pose(kind,phase)[0])
                else:apply_health_blend(rig,kind,phase,health)
                scene.render.filepath=str(OUT/'previews'/(obj.name+'_'+str(idx).zfill(2)+'_'+kind+'.png'))
                bpy.ops.render.render(write_still=True)
                print('PREVIEW',obj.name,idx,kind,phase,health,flush=True)
    print('COMPLETE: original models, UVs, weights and bind files were not saved or changed',flush=True)

if __name__=='__main__':main()
