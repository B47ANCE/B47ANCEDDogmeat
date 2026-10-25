"""Independent exported-asset audit. NumPy only; no authoring imports.

Known fitted anatomical landmarks are data, copied from frozen v2/v3 records.
The existing X decoder is reused; no pose, gait, IK or Blender function is read.
Contact is measured from the skinned GLB sole surface, not authored state flags.
This is an offline regression screen, not anatomy or in-game acceptance.
"""
import argparse
import hashlib
import json
import math
from pathlib import Path
import struct
import sys

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from check_tail_blends import read_bind, read_clip, quat, matrix

BACK = np.array((.96748, .25296, 0.)); BACK /= np.linalg.norm(BACK)
SIDE = np.array((-BACK[1], BACK[0], 0.))
HEAD_FORWARD = np.array((-.09234968807098541, -.9957266367398191, 0.))
LIMBS = {
    'LF': np.array([(-.55,-.06,.04),(-.463863,-.092709,-.24),(-.429093,-.101119,-.69),(-.474205,-.154267,-.79)]),
    'RF': np.array([(-.65,.20,.04),(-.582209,.187946,-.24),(-.589781,.205677,-.69),(-.662712,.219141,-.79)]),
    'LH': np.array([(.49,.17,.10),(.451202,.136585,-.24),(.625738,.202348,-.56),(.600565,.096232,-.79)]),
    'RH': np.array([(.39,.415,.10),(.339772,.454671,-.24),(.478176,.490376,-.56),(.333397,.515298,-.79)]),
}
for limb in ('LH','RH'):
    LIMBS[limb][1:3]-=BACK*.04
TAIL = np.array([(.59,.37,.08),(.640226,.378946,-.24),(.760287,.425082,-.48),(.929105,.491706,-.64)])
FLOOR = -.831


def sha(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def point(transform, p):
    return transform[:3, :3] @ p + transform[:3, 3]


def angle(a, b):
    return float(np.degrees(np.arccos(np.clip(a @ b / np.linalg.norm(a) / np.linalg.norm(b), -1, 1))))


def yaw(a, b):
    return float(np.degrees(np.arctan2(np.cross(a, b)[2], a[:2] @ b[:2])))


def bones_for(limb):
    side = limb[0]
    if limb[1] == 'F':
        return ['Bip01_Spine'] + ['Bip01_'+side+'_'+p for p in ('UpperArm','Forearm','Hand','Finger0')]
    return ['Bip01_Pelvis'] + ['Bip01_'+side+'_'+p for p in ('Thigh','Calf','Foot','Toe0')]


def load_paws(path, coordinate):
    """Read actual GLB accessors; retain each limb's low sole surface and skin."""
    raw = path.read_bytes()
    magic, version, length = struct.unpack_from('<III', raw)
    assert magic == 0x46546C67 and version == 2 and length == len(raw)
    size, kind = struct.unpack_from('<II', raw, 12); assert kind == 0x4E4F534A
    doc = json.loads(raw[20:20+size]); binary = memoryview(raw)[28+size:]
    def values(index):
        a=doc['accessors'][index]; view=doc['bufferViews'][a['bufferView']]
        dtype={5121:'u1',5123:'<u2',5125:'<u4',5126:'<f4'}[a['componentType']]
        width={'SCALAR':1,'VEC2':2,'VEC3':3,'VEC4':4,'MAT4':16}[a['type']]
        item=np.dtype(dtype).itemsize
        return np.ndarray((a['count'],width), dtype=dtype, buffer=binary,
            offset=view.get('byteOffset',0)+a.get('byteOffset',0),
            strides=(view.get('byteStride',width*item),item))
    attrs=doc['meshes'][0]['primitives'][0]['attributes']
    transform=coordinate@np.diag([1,1,-1,1])
    source=values(attrs['POSITION']); co=source@transform[:3,:3].T+transform[:3,3]
    joints=values(attrs['JOINTS_0']); weights=values(attrs['WEIGHTS_0'])
    names=[doc['nodes'][i]['name'] for i in doc['skins'][0]['joints']]
    clouds={}
    for limb in LIMBS:
        columns=[names.index(n) for n in bones_for(limb)[1:]]
        own=np.where(np.isin(joints, columns), weights, 0).sum(axis=1)
        mask=(co[:,2]<-.76)&(own>.99999)
        assert mask.sum()>1000, (limb, 'missing sole cloud')
        clouds[limb]={'positions':co[mask].copy(), 'joints':joints[mask].copy(),
                      'weights':weights[mask].copy()}
    return clouds, names


class ExportedClip:
    def __init__(self, path, coordinate, reference_parents, reference_rest):
        self.path=path; self.name,self.fps,self.tracks=read_clip(path)
        self.parents,self.rest=read_bind(path); self.coordinate=coordinate
        assert self.parents==reference_parents, (path.name,'hierarchy drift')
        self.bind_error=max(float(np.abs(self.rest[n]-reference_rest[n]).max()) for n in self.rest)
        assert self.bind_error<2e-6, (path.name,'rest header drift',self.bind_error)
        self.count=len(self.tracks['Bip01_Head'][0]); assert self.count>2
        assert set(self.tracks)==set(self.parents)
        for bone,tracks in self.tracks.items():
            assert set(tracks)=={0,1,2}
            for channel,rows in tracks.items():
                assert len(rows)==self.count and [r[0] for r in rows]==list(range(self.count))
                assert np.isfinite([r[1] for r in rows]).all()
                if channel==1: assert np.max(np.abs(np.array([r[1] for r in rows])-1))<1e-8
        self.inverse_rest={n:np.linalg.inv(m) for n,m in self.rest.items()}
        self.inverse_coordinate=np.linalg.inv(coordinate)

    def skins(self, frame):
        globals_={}; result={}
        for name,parent in self.parents.items():
            t=self.tracks[name]
            local=matrix(quat(t[0][frame][1]),t[2][frame][1])
            globals_[name]=globals_[parent]@local if parent else local
            result[name]=self.coordinate@globals_[name]@self.inverse_rest[name]@self.inverse_coordinate
        return result


def skin_cloud(cloud, names, skins):
    output=np.zeros_like(cloud['positions'])
    for column in range(4):
        for index in np.unique(cloud['joints'][:,column]):
            mask=cloud['joints'][:,column]==index; transform=skins[names[int(index)]]
            moved=cloud['positions'][mask]@transform[:3,:3].T+transform[:3,3]
            output[mask]+=moved*cloud['weights'][mask,column,None]
    return output


def contact_events(heights, epsilon=.001):
    # Final frame duplicates phase zero. Circular transitions preserve a landing
    # at phase zero and are invariant under where the author starts the cycle.
    contact=np.array(heights[:-1])<=FLOOR+epsilon
    starts=np.flatnonzero(contact&~np.roll(contact,1)).tolist()
    ends=np.flatnonzero(~contact&np.roll(contact,1)).tolist()
    return {'contact':contact.tolist(), 'touchdown_frames':starts, 'liftoff_frames':ends,
            'touchdown_phases':[i/len(contact) for i in starts],
            'support_fraction':float(contact.mean())}


def sequence_is_lateral(order):
    if len(order)!=4 or set(order)!=set(LIMBS): return False
    start=order.index('LH'); rotated=order[start:]+order[:start]
    return rotated==['LH','LF','RH','RF']


def circular_distance(a,b):
    difference=abs(a-b)%1
    return min(difference,1-difference)


def audit(model, motion, output):
    bind_path=model/'validation/native-bind.json'; bind=json.loads(bind_path.read_text())
    motion_report_path=motion/'validation/motion.json'; motion_report=json.loads(motion_report_path.read_text())
    coordinate=np.array(bind['native_to_authoring'])
    reference_parents,reference_rest=read_bind(model/'anims/B47Dogmeat_Idle_Neutral.x')
    immutable={}
    for variant in bind['variants'].values():
        path=model/'models'/(variant['model']+'.glb'); actual=sha(path)
        assert actual==variant['glb_sha256'], (path,'model changed')
        immutable[path.name]=actual
    clouds,names=load_paws(model/'models/B47Dogmeat_GSD_Coat2.glb',coordinate)
    errors=[]
    def require(condition,message):
        if not condition: errors.append(message)
    result={'model_checkpoint':model.relative_to(ROOT).as_posix(), 'motion_checkpoint':motion.relative_to(ROOT).as_posix(),
        'model_recorded_project_version':bind['project_version'], 'current_project_version':(ROOT/'VERSION').read_text().strip(),
        'motion_recorded_project_version':motion_report['project_version'],'motion_report_sha256':sha(motion_report_path),
        'audit_source_sha256':sha(Path(__file__)), 'immutable_model_sha256':immutable,
        'reference_bind_sha256':sha(bind_path),'decoder_sha256':sha(ROOT/'scripts/check_tail_blends.py'),
        'landmark_sources':{p:sha(ROOT/p) for p in ['art/german_shepherd_motion_v2/source/anatomy.py','art/german_shepherd_motion_v3/source/head_rig.py']},
        'floor':FLOOR,'contact_epsilon':.001,'sole_vertex_counts':{k:len(v['positions']) for k,v in clouds.items()},'clips':{}}
    paths=sorted((motion/'anims').glob('*.x')); assert len(paths)==47,('expected 47 exported clips',len(paths))
    for path in paths:
        clip=ExportedClip(path,coordinate,reference_parents,reference_rest)
        assert sha(path)==motion_report['clips'][clip.name]['sha256'],(path.name,'motion report SHA mismatch')
        assert clip.count==motion_report['clips'][clip.name]['frames'],(path.name,'motion report frame mismatch')
        kind,suffix=clip.name.removeprefix('B47Dogmeat_').rsplit('_',1)
        head_yaws=[]; head_pitches=[]; tail_side=[]; tail_gap=0.; tail_length_error=0.
        gait=kind in ('Walk','Run'); joint_gap=0.; joint_detail={}; knee_angles={k:[] for k in LIMBS}
        distal_angles={k:[] for k in LIMBS}; length_errors={k:0. for k in LIMBS}
        pawn={k:{'sole_min_z':[],'center':[],'pelvis_local_center':[]} for k in LIMBS}
        for frame in range(clip.count):
            skins=clip.skins(frame)
            head=np.linalg.inv(skins['Bip01_Spine'])@skins['Bip01_Head']
            direction=head[:3,:3]@HEAD_FORWARD
            head_yaws.append(yaw(-BACK,direction)); head_pitches.append(float(np.degrees(np.arctan2(direction[2],np.linalg.norm(direction[:2])))))
            pelvis_inverse=np.linalg.inv(skins['Bip01_Pelvis'])
            tip=point(pelvis_inverse,point(skins['Bip01_Tail2'],TAIL[-1])); tail_side.append(float(tip@SIDE))
            chain=['Bip01_Pelvis','Bip01_Tail','Bip01_Tail1','Bip01_Tail2']
            for i in range(3):
                tail_gap=max(tail_gap,float(np.linalg.norm(point(skins[chain[i]],TAIL[i])-point(skins[chain[i+1]],TAIL[i]))))
                length=np.linalg.norm(point(skins[chain[i+1]],TAIL[i+1])-point(skins[chain[i+1]],TAIL[i]))
                tail_length_error=max(tail_length_error,float(abs(length-np.linalg.norm(TAIL[i+1]-TAIL[i]))))
            if not gait: continue
            for limb,points in LIMBS.items():
                bones=bones_for(limb)
                for i,source in enumerate(points):
                    gap=float(np.linalg.norm(point(skins[bones[i]],source)-point(skins[bones[i+1]],source)))
                    if gap>joint_gap: joint_gap=gap; joint_detail={'limb':limb,'joint':i,'frame':frame}
                hip=point(skins[bones[0]],points[0]); knee=point(skins[bones[1]],points[1]); ankle=point(skins[bones[2]],points[2]); paw=point(skins[bones[3]],points[3])
                knee_angles[limb].append(angle(hip-knee,ankle-knee))
                distal_angles[limb].append(angle(knee-ankle,paw-ankle))
                posed_points=np.array([hip,knee,ankle,paw])
                length_errors[limb]=max(length_errors[limb],float(np.abs(np.linalg.norm(np.diff(posed_points,axis=0),axis=1)-np.linalg.norm(np.diff(points,axis=0),axis=1)).max()))
                surface=skin_cloud(clouds[limb],names,skins); center=surface.mean(axis=0)
                pawn[limb]['sole_min_z'].append(float(surface[:,2].min()))
                pawn[limb]['center'].append(center.tolist()); pawn[limb]['pelvis_local_center'].append(point(pelvis_inverse,center).tolist())
        info={'sha256':sha(path),'frames':clip.count,'fps':clip.fps,'bind_header_error':clip.bind_error,
            'head_torso_relative_yaw_degrees_range':[min(head_yaws),max(head_yaws)],
            'head_pitch_degrees_range':[min(head_pitches),max(head_pitches)],
            'head_endpoint_yaw_degrees':[head_yaws[0],head_yaws[-1]],
            'tail_pelvis_local_lateral_tip_range':float(np.ptp(tail_side)),
            'tail_attachment_max_gap':tail_gap,'tail_segment_length_max_error':tail_length_error}
        require(tail_gap<2e-5 and tail_length_error<2e-5,clip.name+': tail disconnected or scaled')
        if kind in ('Idle','Look','Walk','Run'):
            require(max(abs(head_yaws[i]) for i in (0,-1))<3,clip.name+': neutral head does not face torso-forward')
            require(np.ptp(tail_side)>.025,clip.name+': lateral tail sway is absent or too small')
        if kind in ('Idle','Walk','Run'):
            require(max(map(abs,head_yaws))<3,clip.name+': neutral head leaves torso-forward cone')
        if kind=='Look':
            require(min(head_yaws)<-20 and max(head_yaws)>20 and max(map(abs,head_yaws))<31,clip.name+': Look must straddle forward neutral')
        if kind=='Dead': require(np.ptp(tail_side)<2e-6,clip.name+': Dead tail moves')
        if gait:
            require(joint_gap<2e-5,clip.name+': disconnected anatomical joint '+str(joint_detail))
            events=[]; phases={}; paws={}
            for limb,data in pawn.items():
                contact=contact_events(data['sole_min_z']); center=np.array(data['center']); local=np.array(data['pelvis_local_center'])
                require(len(contact['touchdown_frames'])==1 and len(contact['liftoff_frames'])==1,clip.name+': '+limb+' needs one swing/contact interval')
                require(length_errors[limb]<2e-5,clip.name+': '+limb+' fitted limb length changed')
                require(min(data['sole_min_z'])>=FLOOR-.005,clip.name+': '+limb+' sole penetrates floor')
                require(max(data['sole_min_z'])-FLOOR>.035,clip.name+': '+limb+' insufficient swing clearance')
                if len(contact['touchdown_phases'])==1:
                    phases[limb]=contact['touchdown_phases'][0]; events.append((phases[limb],limb))
                foreaft=center@BACK; velocity=np.diff(foreaft)*clip.fps
                support=np.array(contact['contact']); support_pairs=support&np.roll(support,-1)
                # Last→first is the loop interval; duplicate end supplies its velocity.
                support_velocity=velocity[support_pairs]
                require(len(support_velocity)>0 and support_velocity.min()>-.005,clip.name+': '+limb+' supported paw reverses forward')
                paws[limb]={**data,**contact,'foreaft_travel':float(np.ptp(foreaft)),
                    'pelvis_local_lateral_travel':float(np.ptp(local@SIDE)),
                    'support_back_velocity_range':[float(support_velocity.min()),float(support_velocity.max())] if len(support_velocity) else [],
                    'knee_degrees_range':[min(knee_angles[limb]),max(knee_angles[limb])],
                    'wrist_or_hock_degrees_range':[min(distal_angles[limb]),max(distal_angles[limb])],
                    'segment_length_max_error':length_errors[limb]}
            order=[limb for _,limb in sorted(events)]
            if kind=='Walk': require(sequence_is_lateral(order),clip.name+': observed touchdown order '+str(order)+' is not lateral sequence')
            if kind=='Run' and len(phases)==4:
                tolerance=1.1/(clip.count-1)
                diagonal=max(circular_distance(phases['LF'],phases['RH']),circular_distance(phases['RF'],phases['LH']))
                opposing=circular_distance(phases['LF'],phases['RF'])
                require(diagonal<=tolerance and abs(opposing-.5)<=tolerance,clip.name+': exported contact is not diagonal trot')
                info['diagonal_pair_phase_error']=diagonal;info['opposing_pair_phase_separation']=opposing
            info.update(joint_endpoint_max_gap=joint_gap,joint_endpoint_worst=joint_detail,paws=paws,touchdown_order=order)
        result['clips'][clip.name]=info
    result.update(status='OFFLINE REGRESSION PASS' if not errors else 'OFFLINE REGRESSION FAIL',failures=errors,
        limitations=['Only authored frames; no temporal/state blends or PZ playback.',
            'Joint/paw/tail landmarks do not detect full-surface edge extension; retain the independent full-mesh 0.06 bound.',
            'Contact threshold and tail visibility bounds are explicit regression acceptance criteria; numerics do not certify visual anatomy.'])
    output.parent.mkdir(parents=True,exist_ok=True); output.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps({'status':result['status'],'report':str(output),'clips':len(paths),'failures':errors},indent=2))
    return 1 if errors else 0


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--model',default='art/german_shepherd_motion_v3')
    parser.add_argument('--motion',default='art/german_shepherd_motion_v4')
    parser.add_argument('--output',default='art/german_shepherd_motion_v4/validation/canine-movement.json')
    args=parser.parse_args();sys.exit(audit(ROOT/args.model,ROOT/args.motion,ROOT/args.output))
