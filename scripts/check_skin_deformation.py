"""Recompute skin deformation from shipped GLB and serialized X clips, offline.

This is a regression screen, not visual or PZ acceptance. Uses NumPy; does not
import Blender, the authoring pose function, a game class or any native motion.
"""
import hashlib,json,struct,contextlib,io
from pathlib import Path
from types import SimpleNamespace
import numpy as np
from check_tail_blends import read_clip,read_bind,quat,matrix
ROOT=Path(__file__).resolve().parents[1]
ASSET=ROOT/'art/german_shepherd_motion_v3'

def read_model(path):
    raw=path.read_bytes();size=struct.unpack_from('<I',raw,12)[0];doc=json.loads(raw[20:20+size]);binary=raw[28+size:]
    def accessor(index):
        a=doc['accessors'][index];v=doc['bufferViews'][a['bufferView']]
        dtype={5121:'u1',5123:'<u2',5125:'<u4',5126:'<f4'}[a['componentType']]
        width={'SCALAR':1,'VEC2':2,'VEC3':3,'VEC4':4,'MAT4':16}[a['type']];item=np.dtype(dtype).itemsize
        values=np.ndarray((a['count'],width),dtype=dtype,buffer=binary,offset=v.get('byteOffset',0)+a.get('byteOffset',0),strides=(v.get('byteStride',width*item),item))
        return values
    primitive=doc['meshes'][0]['primitives'][0];attributes=primitive['attributes']
    return raw,doc,accessor(attributes['POSITION']),accessor(attributes['JOINTS_0']),accessor(attributes['WEIGHTS_0']),accessor(primitive['indices']).reshape(-1,3)

def audit():
    # CI hydrates only current runtime assets. Compare against the independently
    # verified v2 digests, then exercise all ten actual Look clips and half frames.
    from check_head_deformation import main as audit_head
    with contextlib.redirect_stdout(io.StringIO()):
        head_proof=audit_head(SimpleNamespace(candidate='art/german_shepherd_motion_v3',
            baseline='art/german_shepherd_motion_v2',skip_previous=True,models_only=False,
            reference='art/german_shepherd_motion_v3/validation/head-deformation.json',output=None))
    path=ASSET/'models/B47Dogmeat_GSD_Coat2.glb';raw,doc,positions,joints,weights,faces=read_model(path)
    report=json.loads((ASSET/'validation/native-bind.json').read_text());coordinate=np.array(report['native_to_authoring']);inverse=np.linalg.inv(coordinate)
    transform=coordinate@np.diag([1,1,-1,1]);co=positions@transform[:3,:3].T+transform[:3,3]
    names=[doc['nodes'][i]['name'] for i in doc['skins'][0]['joints']]
    assert np.isfinite(co).all() and np.isfinite(weights).all() and weights.min()>=0
    assert int(joints.max())<25 and np.max(np.abs(weights.sum(axis=1)-1))<2e-7
    combined=np.zeros((len(co),25),np.float32)
    for column in range(4):np.add.at(combined,(np.arange(len(co)),joints[:,column]),weights[:,column])
    assert (combined>0).sum(axis=1).max()<=4
    # A face split between Head and Neck used to squeeze the muzzle during
    # independent turns. These source-space masks cover the actual supplied
    # muzzle, upper face, ears, and mouth; no authoring weight function imported.
    x,y,z=co.T;head=combined[:,names.index('Bip01_Head')]
    facial_masks={'muzzle':(y<-.4)&(z>.25)&(z<.52),
        'upper_face':(z>.48)&(z<.63)&(x<-.45),'ears':z>.65,
        'mouth':(y<-.32)&(z>.17)&(z<.4)}
    landmarks=[];head_regions={}
    for label,mask in facial_masks.items():
        selected=np.flatnonzero(mask);assert len(selected)>1000
        assert np.all(head[selected]==1),(label,'face must follow Head rigidly')
        head_regions[label]={'vertices':len(selected),'head_weight':1}
        landmarks.extend(selected[np.argmin(co[selected],axis=0)])
        landmarks.extend(selected[np.argmax(co[selected],axis=0)])
    landmarks=np.unique(landmarks);face=co[landmarks]
    facial_distances=np.linalg.norm(face[:,None]-face[None,:],axis=2)
    tail_columns=np.array(['Tail' in n for n in names]);tail_weight=combined[:,tail_columns].sum(axis=1)
    # Distal tail and the four distinct paw clouds caught the original cross-
    # limb errors. Full source-topology fields have a separate authoring audit.
    distal=(co[:,0]>.80)&(co[:,1]>.35)&(co[:,2]<-.45)
    assert distal.sum()>1000 and np.min(tail_weight[distal])>.99999
    centers=np.array([[-.686,.226],[-.494,-.178],[.309,.514],[.590,.077]])
    index=np.flatnonzero(co[:,2]<-.76);labels=((co[index,None,:2]-centers[None,:,:])**2).sum(axis=2).argmin(axis=1)
    paws={}
    for k,(side,parts) in enumerate([('R',('Clavicle','UpperArm','Forearm','Hand','Finger')),('L',('Clavicle','UpperArm','Forearm','Hand','Finger')),('R',('Thigh','Calf','Foot','Toe')),('L',('Thigh','Calf','Foot','Toe'))]):
        selected=index[labels==k];own=np.array([n.startswith('Bip01_'+side+'_') and any(part in n for part in parts) for n in names])
        opposite=np.array([('_L_' if side=='R' else '_R_') in n for n in names])
        minimum=float(combined[selected][:,own].sum(axis=1).min());other=float(combined[selected][:,opposite].sum(axis=1).max())
        assert minimum>.99999 and other==0 and tail_weight[selected].max()==0
        paws[str(k)]={'vertices':len(selected),'minimum_correct_limb':minimum,'maximum_opposite_limb':other}
    regions=[(name,np.flatnonzero(combined[:,i]),i) for i,name in enumerate(names)]
    edges=np.concatenate([faces[:,[0,1]],faces[:,[1,2]],faces[:,[2,0]]]);edges.sort(axis=1);edges=np.unique(edges,axis=0)
    rest_lengths=np.linalg.norm(co[edges[:,0]]-co[edges[:,1]],axis=1)
    parents,rest=read_bind(ASSET/'anims/B47Dogmeat_Idle_Neutral.x');inverse_rest={n:np.linalg.inv(v) for n,v in rest.items()}
    cases=[('Idle','High',0),('Eat','Neutral',.5),('Lie','Neutral',0),('Dead','Neutral',0)]
    cases += [(kind,'High' if kind=='Run' else 'Neutral',i/8) for kind in ('Walk','Run') for i in range(8)]
    # Every serialized rest-transition frame, including the deepest fold.
    cases += [(kind,'Neutral',i/39) for kind in ('LieDown','GetUp') for i in range(40)]
    cases += [('Look','Neutral',i/8) for i in range(8)]
    cases += [('Death','Neutral',t) for t in (.25,.5,.75,1)]
    cache={};results=[]
    for kind,suffix,t in cases:
        clip='B47Dogmeat_'+kind+'_'+suffix
        if clip not in cache:cache[clip]=read_clip(ASSET/'anims'/(clip+'.x'))[2]
        tracks=cache[clip];frame=round(t*(len(tracks['Bip01_Head'][0])-1));global_pose={}
        for name,parent in parents.items():
            local=matrix(quat(tracks[name][0][frame][1]),tracks[name][2][frame][1])
            global_pose[name]=global_pose[parent]@local if parent else local
        posed=np.zeros_like(co);skin_matrices={}
        for name,ix,column in regions:
            skin=coordinate@global_pose[name]@inverse_rest[name]@inverse
            skin_matrices[name]=skin
            posed[ix]+=(co[ix]@skin[:3,:3].T+skin[:3,3])*combined[ix,column,None]
        minimum=float(posed[:,2].min());assert np.isfinite(posed).all()
        floor_limit=-.836 if kind in ('Walk','Run') else -.8321
        assert minimum>=floor_limit,(kind,t,'floor',minimum)
        item={'clip':clip,'frame':frame,'phase_requested':t,'minimum_z':minimum}
        if kind in ('Lie','LieDown','GetUp','Dead'):
            # Independently recorded source landmarks. The old 50-degree tuck
            # collapsed the thigh/calf blend; these angles measure the emitted
            # transforms rather than trusting the IK author's claimed limits.
            rear_landmarks={'L':[(.49,.17,.10),(.451202,.136585,-.24),(.625738,.202348,-.56)],
                'R':[(.39,.415,.10),(.339772,.454671,-.24),(.478176,.490376,-.56)]}
            angles={}
            for side,points in rear_landmarks.items():
                bones=('Bip01_Pelvis','Bip01_'+side+'_Thigh','Bip01_'+side+'_Calf')
                hip,knee,hock=[(skin_matrices[bone]@np.r_[p,1])[:3] for bone,p in zip(bones,points)]
                a=hip-knee;b=hock-knee
                angle=float(np.degrees(np.arccos(np.clip(a@b/np.linalg.norm(a)/np.linalg.norm(b),-1,1))))
                assert angle>=(140 if kind=='Dead' else 85),(kind,frame,side,'acute rear knee',angle)
                angles[side]=angle
            item['rear_knee_degrees']=angles
        if kind=='Look':
            face=posed[landmarks];error=float(np.max(np.abs(np.linalg.norm(face[:,None]-face[None,:],axis=2)-facial_distances)))
            assert error<2e-5,('rigid face',t,error)
            item['facial_pair_distance_error']=error
        if kind in ('Idle','Eat','Lie','Walk','Run','LieDown','GetUp','Look'):
            extension=np.linalg.norm(posed[edges[:,0]]-posed[edges[:,1]],axis=1)-rest_lengths
            maximum=float(extension.max());assert maximum<.06,(kind,t,'edge extension',maximum)
            item.update(maximum_edge_extension=maximum,edges_above_004_extension=int((extension>.04).sum()))
        results.append(item)
    return {'project_version':(ROOT/'VERSION').read_text().strip(),'status':'OFFLINE REGRESSION PASS',
        'method':'Actual current GLB skin and serialized X hierarchy/local transforms; full surface, sampled authored frames',
        'model_sha256':hashlib.sha256(raw).hexdigest(),
        'audit_source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'clip_sha256':{clip:hashlib.sha256((ASSET/'anims'/(clip+'.x')).read_bytes()).hexdigest() for clip in cache},
        'vertices':len(co),'edges':len(edges),'paws':paws,'head_regions':head_regions,
        'independent_head_audit':{'status':head_proof['status'],'models':len(head_proof['models']),
            'look_samples':sum(v['samples_with_half_frames'] for v in head_proof['clips'].values())},'samples':results,
        'limits':'Numerical regression bounds do not certify anatomy or visual quality; no between-frame/state blends or PZ execution.'}

if __name__=='__main__':print(json.dumps(audit(),indent=2))
