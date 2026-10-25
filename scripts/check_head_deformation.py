"""Independent offline GLB/X head regression; reads frozen assets, never author functions.
Run with bundled Python --candidate art/german_shepherd_motion_v3.
Only the --output JSON is written. Missing outputs/failing assertions are failures.
"""
from pathlib import Path
import argparse,hashlib,json,re,struct,sys
import numpy as np
H=np.diag([1.,1.,-1.,1.])
FORWARD=np.array([-.09234968807098541,-.9957266367398191,0.])
BACK=np.array([.96748,.25296,0.]);BACK/=np.linalg.norm(BACK)
REGION_FORMULAS={
 'muzzle':'y < -0.40 and 0.25 < z < 0.52',
 'upper_face':'0.48 < z < 0.63 and x < -0.45',
 'ears':'z > 0.65',
 'mouth_and_lower_muzzle':'y < -0.32 and 0.17 < z < 0.40',
 'torso_behind_neck':'dot(position,BACK) > -0.25 and -0.22 < z < 0.40',
 'lower_limbs':'z < -0.25 and sum(L/R limb weights) > 0.999'}
def sha(data):return hashlib.sha256(data).hexdigest()
def quat_matrix(q):
 # xyzw normalized quaternion, independent of Blender/mathutils.
 x,y,z,w=q;s=2/float(np.dot(q,q));m=np.eye(4)
 m[:3,:3]=[[1-s*(y*y+z*z),s*(x*y-z*w),s*(x*z+y*w)],
 [s*(x*y+z*w),1-s*(x*x+z*z),s*(y*z-x*w)],
 [s*(x*z-y*w),s*(y*z+x*w),1-s*(x*x+y*y)]]
 return m
class GLB:
 def __init__(self,path):
  self.path=path;self.raw=path.read_bytes();magic,version,total=struct.unpack_from('<III',self.raw,0)
  assert magic==0x46546c67 and version==2 and total==len(self.raw)
  length,kind=struct.unpack_from('<II',self.raw,12);assert kind==0x4e4f534a
  self.doc=json.loads(self.raw[20:20+length]);self.start=28+length;self.binary=self.raw[self.start:]
  self.parents={c:i for i,node in enumerate(self.doc['nodes'])for c in node.get('children',[])}
  self.globals={};self.name_to_node={n['name']:i for i,n in enumerate(self.doc['nodes'])if 'name'in n}
  skin=self.doc['skins'][0];self.joints=skin['joints'];self.names=[self.doc['nodes'][i]['name']for i in self.joints]
  self.ibm=self.read(skin['inverseBindMatrices']).reshape(-1,4,4).transpose(0,2,1)
 def read(self,index):
  a=self.doc['accessors'][index];v=self.doc['bufferViews'][a['bufferView']]
  dtype={5121:'u1',5123:'<u2',5125:'<u4',5126:'<f4'}[a['componentType']]
  width={'SCALAR':1,'VEC2':2,'VEC3':3,'VEC4':4,'MAT4':16}[a['type']];size=np.dtype(dtype).itemsize
  values=np.ndarray((a['count'],width),dtype=dtype,buffer=self.binary,offset=v.get('byteOffset',0)+a.get('byteOffset',0),strides=(v.get('byteStride',width*size),size))
  assert not a.get('normalized'), 'Unexpected normalized attribute; review reader explicitly'
  return values
 def global_node(self,i):
  if i not in self.globals:
   n=self.doc['nodes'][i]
   if 'matrix'in n:local=np.array(n['matrix']).reshape(4,4).T
   else:
    local=quat_matrix(n.get('rotation',[0,0,0,1]));local[:3,:3]*=np.array(n.get('scale',[1,1,1]))[None,:];local[:3,3]=n.get('translation',[0,0,0])
   self.globals[i]=self.global_node(self.parents[i])@local if i in self.parents else local
  return self.globals[i]
 def dense(self,primitive):
  a=primitive['attributes'];j=self.read(a['JOINTS_0']);w=self.read(a['WEIGHTS_0']);result=np.zeros((len(j),len(self.names)),np.float32)
  np.add.at(result,(np.arange(len(j))[:,None],j),w);return result
 def immutable_hash(self):
  binary=bytearray(self.binary)
  for mesh in self.doc['meshes']:
   for primitive in mesh['primitives']:
    for name in ['JOINTS_0','WEIGHTS_0']:
     index=primitive['attributes'][name];a=self.doc['accessors'][index];v=self.doc['bufferViews'][a['bufferView']];array=self.read(index)
     assert v.get('byteStride',array.strides[0])==array.strides[0] and array.flags.c_contiguous
     start=v.get('byteOffset',0)+a.get('byteOffset',0);binary[start:start+array.nbytes]=b'\0'*array.nbytes
  return sha(self.raw[:self.start]+binary)
def closing(text,start):
 depth=1;i=start
 while depth:
  depth+=(text[i]=='{')-(text[i]=='}');i+=1
 return i
def read_x(path):
 text=path.read_text(encoding='utf-8');rest_text=text.split('AnimationSet')[0]
 parents={};rest={};stack=[]
 for m in re.finditer(r'\bFrame\s+(\w+)\s*\{',rest_text):
  while stack and m.start()>stack[-1][1]:stack.pop()
  name=m[1];parents[name]=stack[-1][0]if stack else None
  block=re.search(r'FrameTransformMatrix\s*\{([^}]+)\}',rest_text[m.end():])[1]
  values=[float(v)for v in re.findall(r'[-+]?\d+(?:\.\d+)?(?:[Ee][-+]?\d+)?',block)]
  assert len(values)==16;rest[name]=np.array(values).reshape(4,4).T;stack.append((name,closing(rest_text,m.end())))
 tracks={}
 for m in re.finditer(r'\bAnimation\s*\{\s*\{\s*(\w+)\s*\}',text):
  block=text[m.end():closing(text,text.index('{',m.start())+1)-1];channels={}
  for key in re.finditer(r'AnimationKey\s+\w+\s*\{\s*(\d+);\s*(\d+);([^}]+)\}',block):
   rows=[(int(k[1]),np.array([float(v)for v in k[3].split(',')]))for k in re.finditer(r'(\d+);(\d+);([^;]+);;',key[3])]
   assert len(rows)==int(key[2]);channels[int(key[1])]=rows
  tracks[m[1]]=channels
 assert set(tracks)==set(rest)
 return parents,rest,tracks

def global_matrices(locals_,parents):
 result={}
 def visit(n):
  if n not in result:result[n]=visit(parents[n])@locals_[n]if parents[n] else locals_[n]
  return result[n]
 for n in locals_:visit(n)
 return result

def sample(rows,time,quaternion=False):
 times=[r[0]for r in rows];hi=int(np.searchsorted(times,time));hi=min(hi,len(rows)-1);lo=max(0,hi-1)
 if times[hi]==time:lo=hi
 a=rows[lo][1];b=rows[hi][1];u=(time-times[lo])/(times[hi]-times[lo])if hi!=lo else 0
 if quaternion:
  # X writes wxyz with conjugated vector; read into xyzw, then nlerp.
  a=np.array([-a[1],-a[2],-a[3],a[0]]);b=np.array([-b[1],-b[2],-b[3],b[0]])
  if np.dot(a,b)<0:b=-b
  q=a*(1-u)+b*u;return q/np.linalg.norm(q)
 return a*(1-u)+b*u

def pose_x(tracks,parents,time):
 locals_={}
 for n,c in tracks.items():
  m=quat_matrix(sample(c[0],time,True));m[:3,:3]*=sample(c[1],time)[None,:];m[:3,3]=sample(c[2],time);locals_[n]=m
 return global_matrices(locals_,parents)

def masks(co,weights,names):
 x,y,z=co.T;limb=[i for i,n in enumerate(names)if '_L_'in n or '_R_'in n]
 return {'muzzle':(y<-.4)&(z>.25)&(z<.52),'upper_face':(z>.48)&(z<.63)&(x<-.45),'ears':z>.65,
 'mouth_and_lower_muzzle':(y<-.32)&(z>.17)&(z<.4),'torso_behind_neck':(co@BACK>-.25)&(z>-.22)&(z<.40),
 'lower_limbs':(z<-.25)&(weights[:,limb].sum(1)>.999)}

def main(args):
 root=Path(__file__).resolve().parents[1];candidate=root/args.candidate;baseline=root/args.baseline;motion=root/args.motion
 if args.reference and args.output:assert (root/args.reference).resolve()!=(root/args.output).resolve(),'Do not overwrite the verified reference report'
 reference_proof=json.loads((root/args.reference).read_text(encoding='utf-8')) if args.reference else None
 comparison_mode='previous GLB bytes' if not args.skip_previous else 'verified reference digests' if reference_proof else 'NOT RUN (current-asset checks only)'
 record=json.loads((candidate/'validation/native-bind.json').read_text(encoding='utf-8'));P=np.array(record['native_to_authoring']);A=P@H;invA=np.linalg.inv(A)
 report={'project_version':(root/'VERSION').read_text(encoding='utf-8').strip(),'audit_source_sha256':sha(Path(__file__).read_bytes()),'environment':'Standalone NumPy offline GLB/X decode; no Blender author functions imported','runtime':'NOT TESTED',
 'candidate':str(candidate.relative_to(root)),'baseline':str(baseline.relative_to(root)),'previous_comparison':comparison_mode,'formal_region_masks':REGION_FORMULAS,
 'x_to_glb_coordinate_bridge':'G_glb = H @ G_x @ H, H=diag(1,1,-1,1); checked against emitted rest frames',
 'fractional_sampling':'Quaternion normalized linear interpolation; exact keyframes also all evaluated','models':{},'clips':{}}
 face_labels=['muzzle','upper_face','ears','mouth_and_lower_muzzle'];reference=None
 model_paths=sorted(((candidate if args.skip_previous else baseline)/'models').glob('*.glb'))
 assert {p.stem for p in model_paths}=={v['model'] for v in record['variants'].values()}
 for basepath in model_paths:
  target=candidate/'models'/basepath.name;assert target.exists(),target
  assert sha(target.read_bytes())==next(v['glb_sha256'] for v in record['variants'].values() if v['model']==basepath.stem),'Frozen v3 skin changed'
  base=None if args.skip_previous else GLB(basepath);model=GLB(target)
  immutable=model.immutable_hash()
  if base is not None:
   assert model.doc==base.doc,'GLB metadata/node/bind description changed'
   assert immutable==base.immutable_hash(),'Non-skin GLB bytes changed'
   assert model.names==base.names
  if reference_proof is not None:assert immutable==reference_proof['models'][basepath.name]['immutable_bytes_sha256'],'Reference immutable-byte digest mismatch'
  allowed=[model.names.index(n)for n in ['Bip01_Head','Bip01_Neck']];other=[i for i in range(len(model.names))if i not in allowed]
  permodel={'sha256':sha(model.raw),'baseline_sha256':sha(base.raw) if base is not None else None,'previous_comparison':comparison_mode,'non_skin_bytes_exact':True if base is not None else None,'immutable_bytes_sha256':immutable,'primitives':[]}
  for mi,mesh in enumerate(model.doc['meshes']):
   mesh_nodes=[i for i,node in enumerate(model.doc['nodes'])if node.get('mesh')==mi];assert len(mesh_nodes)==1
   meshG=model.global_node(mesh_nodes[0]);invMesh=np.linalg.inv(meshG)
   for pi,primitive in enumerate(mesh['primitives']):
    w=model.dense(primitive)
    digest=sha(np.ascontiguousarray(w[:,other]).astype('<f4',copy=False).tobytes())
    if base is not None:
     old=base.dense(base.doc['meshes'][mi]['primitives'][pi]);assert np.array_equal(w[:,other],old[:,other])
    if reference_proof is not None:
     expected_primitive=reference_proof['models'][basepath.name]['primitives'][len(permodel['primitives'])]
     assert digest==expected_primitive['non_head_neck_weights_sha256'],'Non-head weight reference digest mismatch'
    assert np.isfinite(w).all() and w.min()>=0 and (w>0).sum(1).max()<=4 and np.allclose(w.sum(1),1,atol=1e-7)
    assert np.all(np.rint(w*255).sum(1)==255)
    pos=model.read(primitive['attributes']['POSITION']).astype(float);co=pos@A[:3,:3].T+A[:3,3];regions=masks(co,w,model.names)
    region_report={};selected=[]
    for label,mask in regions.items():
     ids=np.flatnonzero(mask);assert len(ids)>0
     head=w[ids,allowed[0]];expected=1 if label in face_labels else 0;assert np.all(head==expected),(basepath.name,label,float(head.min()),float(head.max()))
     region_report[label]={'vertices':len(ids),'head_weight_min':float(head.min()),'head_weight_max':float(head.max())}
     if label in face_labels:
      selected.extend(ids[np.argmin(co[ids],axis=0)].tolist());selected.extend(ids[np.argmax(co[ids],axis=0)].tolist())
      center=co[ids].mean(0);selected.append(int(ids[np.linalg.norm(co[ids]-center,axis=1).argmin()]))
    bind_error=max(float(np.abs(invMesh@model.global_node(node)@model.ibm[j]-np.eye(4)).max())for j,node in enumerate(model.joints));assert bind_error<2e-5
    permodel['primitives'].append({'vertices':len(pos),'non_head_neck_weights_exact':True if base is not None else None,'non_head_neck_weights_sha256':digest,'non_head_neck_column_names':[model.names[i]for i in other],'max_influences':int((w>0).sum(1).max()),'regions':region_report,'bind_identity_matrix_error':bind_error})
    if basepath.stem.endswith('Coat2'):
     selected=np.unique(selected);reference={'model':model,'invMesh':invMesh,'positions':pos[selected],'weights':w[selected],
      'source_landmarks':co[selected],'indices':selected,'A':A,'invA':invA}
  report['models'][basepath.name]=permodel
  print('HEAD_MODEL',basepath.name,'current checks verified; previous comparison:',comparison_mode,flush=True)
  if reference is None or model is not reference['model']:del model
  del base
 assert reference is not None
 if args.models_only:
  report['status']='PARTIAL - GLB checks only; exported Look clips not evaluated'
  if args.output:(root/args.output).write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8',newline='\n')
  print('HEAD_MODELS_ONLY',flush=True);return report
 model=reference['model'];head_index=model.names.index('Bip01_Head');head_bind=model.ibm[head_index]
 def pivot_yaw(degrees):
  angle=np.radians(degrees);c,s=np.cos(angle),np.sin(angle);m=np.eye(4);m[:3,:3]=[[c,-s,0],[s,c,0],[0,0,1]]
  atlas=np.array([-.745,.015,.435]);m[:3,3]=atlas-m[:3,:3]@atlas;return m
 neutral_neck=pivot_yaw(-35);neutral_head=pivot_yaw(-70.04851073581948)
 report['motion']=motion.relative_to(root).as_posix();report['neutral_head_torso_forward']=True
 clip_paths=sorted((motion/'anims').glob('*Look*.x'));expected={'B47Dogmeat_Look_'+suffix+'.x'for suffix in ('Neutral','Low','H125','H25','H375','H50','H625','H75','H875','High')};assert expected and {p.name for p in clip_paths}==expected,'Missing or unexpected exported Look clips'
 for path in clip_paths:
  parents,rest,tracks=read_x(path);restG=global_matrices(rest,parents)
  rest_error=max(float(np.abs(H@restG[n]@H-model.global_node(model.name_to_node[n])).max())for n in restG)
  assert rest_error<2e-5,(path.name,'rest coordinate mismatch',rest_error)
  times=sorted({t for rows in tracks['Bip01_Head'].values()for t,_ in rows});samples=sorted(set(times+[(a+b)/2 for a,b in zip(times,times[1:])]))
  maximum={'pairwise_distance_error':0.,'rigid_head_prediction_error':0.,'head_rotation_orthogonality_error':0.,'neck_motion_matrix_error':0.};yaw=[];pitch=[];neutral=[]
  source=reference['source_landmarks'];pairs=np.linalg.norm(source[:,None]-source[None,:],axis=2)
  for time in samples:
   globals_=pose_x(tracks,parents,time);skins=[reference['invMesh']@H@globals_[n]@H@model.ibm[i]for i,n in enumerate(model.names)]
   moved=np.zeros_like(reference['positions'])
   for i,m in enumerate(skins):moved+=(reference['positions']@m[:3,:3].T+m[:3,3])*reference['weights'][:,i,None]
   authored=moved@A[:3,:3].T+A[:3,3];headD=A@skins[head_index]@invA
   predicted=source@headD[:3,:3].T+headD[:3,3];maximum['rigid_head_prediction_error']=max(maximum['rigid_head_prediction_error'],float(np.abs(authored-predicted).max()))
   maximum['pairwise_distance_error']=max(maximum['pairwise_distance_error'],float(np.abs(np.linalg.norm(authored[:,None]-authored[None,:],axis=2)-pairs).max()))
   maximum['head_rotation_orthogonality_error']=max(maximum['head_rotation_orthogonality_error'],float(np.abs(headD[:3,:3].T@headD[:3,:3]-np.eye(3)).max()))
   expected_neck=pivot_yaw(-35+12.5*np.sin(2*np.pi*time/times[-1]))
   neckD=A@skins[model.names.index('Bip01_Neck')]@invA;maximum['neck_motion_matrix_error']=max(maximum['neck_motion_matrix_error'],float(np.abs(neckD-expected_neck).max()))
   if time in times:assert float(np.abs(neckD-expected_neck).max())<2e-5,(path.name,time,'Neck keyframe yaw')
   forward=headD[:3,:3]@FORWARD;yaw.append(float(np.degrees(np.arctan2(np.cross(-BACK,forward)[2],np.dot(-BACK[:2],forward[:2])))));pitch.append(float(np.degrees(np.arctan2(-forward[2],np.linalg.norm(forward[:2])))))
   if time in (times[0],times[-1]):neutral.append(float(np.abs(authored-(source@neutral_head[:3,:3].T+neutral_head[:3,3])).max()))
  # Half-frame PRS interpolation approximates the analytic sinusoid. Keyframes
  # keep the strict bound above; record the separate subframe curve deviation.
  assert maximum['neck_motion_matrix_error']<.00015,(path.name,maximum)
  assert max(v for k,v in maximum.items() if k!='neck_motion_matrix_error')<2e-5,(path.name,maximum)
  assert max(neutral)<2e-5,(path.name,'neutral',neutral)
  assert min(yaw)<-24.9 and max(yaw)>24.9 and max(np.abs(yaw))<25.02,(path.name,'yaw',min(yaw),max(yaw))
  assert min(pitch)<-11.9 and max(pitch)>11.9 and max(np.abs(pitch))<12.02,(path.name,'pitch',min(pitch),max(pitch))
  report['clips'][path.name]={'sha256':sha(path.read_bytes()),'keyframes':len(times),'samples_with_half_frames':len(samples),'rest_global_matrix_error':rest_error,
   'yaw_degrees_range':[min(yaw),max(yaw)],'pitch_degrees_range':[min(pitch),max(pitch)],'endpoint_neutral_max_error':max(neutral),**maximum}
  print('HEAD_CLIP',path.name,json.dumps(report['clips'][path.name]),flush=True)
 report['landmarks']={'reference_model':'B47Dogmeat_GSD_Coat2','vertex_indices':reference['indices'].tolist(),'source_positions':reference['source_landmarks'].tolist()}
 report['status']='PASS - offline asset regression only'
 if args.output:
  output=root/args.output;output.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8',newline='\n')
 print('HEAD_EXPORT_REGRESSION_PASS',flush=True)
 return report
if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('--skip-previous',action='store_true',help='Do not load historical v2 GLBs; comparison is NOT RUN unless --reference is supplied');parser.add_argument('--reference',help='Previously verified report with immutable and non-head weight digests');parser.add_argument('--models-only',action='store_true');parser.add_argument('--candidate',default='art/german_shepherd_motion_v3');parser.add_argument('--motion',default='art/german_shepherd_motion_v4');parser.add_argument('--baseline',default='art/german_shepherd_motion_v2');parser.add_argument('--output',default=None);main(parser.parse_args())
