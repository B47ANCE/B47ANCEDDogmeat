"""Skin landmarks fitted to the supplied asymmetric stance, without mesh edits."""
import numpy as np
BACK=np.array((.96748,.25296,0));BACK/=np.linalg.norm(BACK)
SIDE=np.array((-BACK[1],BACK[0],0))
LIMBS={
 ('L','front'):[(-.55,-.06,.04),(-.463863,-.092709,-.24),(-.429093,-.101119,-.69),(-.474205,-.154267,-.79)],
 ('R','front'):[(-.65,.20,.04),(-.582209,.187946,-.24),(-.589781,.205677,-.69),(-.662712,.219141,-.79)],
 ('L','rear'):[(.49,.17,.10),(.451202,.136585,-.24),(.625738,.202348,-.56),(.600565,.096232,-.79)],
 ('R','rear'):[(.39,.415,.10),(.339772,.454671,-.24),(.478176,.490376,-.56),(.333397,.515298,-.79)],
}
TAIL=np.array([(.59,.37,.08),(.640226,.378946,-.24),(.760287,.425082,-.48),(.929105,.491706,-.64)])
def smooth(a,b,x):
 t=np.clip((x-a)/(b-a),0,1);return t*t*(3-2*t)
def segment_distance(co,a,b):
 a=np.asarray(a);b=np.asarray(b);v=b-a
 t=np.clip((co-a)@v/(v@v),0,1);return np.linalg.norm(co-a-t[:,None]*v,axis=1)
def weights(co,names,tailmask,limb_fields):
 scores=np.zeros((len(co),len(names)),np.float32)
 def capsule(name,a,b,radius,gain=1):
  d=segment_distance(co,a,b);scores[:,names.index(name)]+=gain*np.exp(-2.5*(d/radius)**2)
 capsule('Bip01_Head',(-.64,-.035,.35),(-.68,-.07,.65),.22)
 capsule('Bip01_Neck',(-.44,.05,.02),(-.61,-.015,.35),.25)
 capsule('Bip01_Spine',(-.24,.13,.04),(.15,.21,.06),.30)
 capsule('Bip01_Pelvis',(.15,.21,.06),(.46,.29,.08),.245)
 for name in ('Head','Neck','Spine','Pelvis'):
  scores[:,names.index('Bip01_'+name)]*=smooth(-.47,-.25,co[:,2])
 legdistance=np.full(len(co),10.)
 for (side,part),points in LIMBS.items():
  a,b,c,d=map(np.array,points)
  if part=='front':
   capsule('Bip01_'+side+'_Clavicle',a+np.array((.10,0,.15)),a,.13,.5)
   fields=[('UpperArm',a,b,.115),('Forearm',b,c,.066),('Hand',c,d,.058),('Finger0',d,d-BACK*.065,.055)]
  else:fields=[('Thigh',a,b,.14),('Calf',b,c,.095),('Foot',c,d,.061),('Toe0',d,d-BACK*.065,.055)]
  for name,p,q,r in fields:
   capsule('Bip01_'+side+'_'+name,p,q,r)
   legdistance=np.minimum(legdistance,segment_distance(co,p,q))
 taildistance=np.full(len(co),10.)
 tailcolumns=[]
 for i,(p,q) in enumerate(zip(TAIL,TAIL[1:])):
  name='Bip01_Tail'+(str(i) if i else '');tailcolumns.append(names.index(name))
  capsule(name,p,q,[.078,.075,.07][i],2)
  taildistance=np.minimum(taildistance,segment_distance(co,p,q))
 # Preserve capsule-based limb membership, but blend across joint tangent planes.
 # Unequal capsule radii previously let upper-arm influence reach far down a
 # narrow forearm, stretching fur when the elbow folded.
 for (side,part),points in LIMBS.items():
  points=np.array(points)
  parts=('UpperArm','Forearm','Hand','Finger0') if part=='front' else ('Thigh','Calf','Foot','Toe0')
  columns=[names.index('Bip01_'+side+'_'+p) for p in parts];total=scores[:,columns].sum(axis=1)
  widths=(.065,.045,.035)
  extended=np.vstack([points,points[-1]-BACK*.065])
  directions=np.diff(extended,axis=0);directions/=np.linalg.norm(directions,axis=1)[:,None]
  transitions=[]
  for i in range(3):
   tangent=directions[i]+directions[i+1];tangent/=np.linalg.norm(tangent)
   transition=smooth(-widths[i],widths[i],(co-points[i+1])@tangent)
   if transitions:transition=np.minimum(transition,transitions[-1])
   transitions.append(transition)
  distribution=np.column_stack((1-transitions[0],transitions[0]-transitions[1],transitions[1]-transitions[2],transitions[2]))
  assert distribution.min()>-1e-7
  scores[:,columns]=total[:,None]*distribution
 # Topology separates tail from nearby hindquarter fur. The geodesic root field
 # follows connected surfaces instead of bridging nearby but unrelated strips.
 other=[i for i in range(len(names)) if i not in tailcolumns]
 scores[:,other]/=np.maximum(scores[:,other].sum(axis=1,keepdims=True),1e-30)
 scores[:,other]*=(1-tailmask[:,None])
 scores[:,tailcolumns]/=np.maximum(scores[:,tailcolumns].sum(axis=1,keepdims=True),1e-30)
 scores[:,tailcolumns]*=tailmask[:,None]
 baseline=scores.copy();total_field=limb_fields.sum(axis=1)
 assert total_field.max()<=1+1e-7
 scores*=1-total_field[:,None]
 for k,(side,part) in enumerate([('R','front'),('L','front'),('R','rear'),('L','rear')]):
  parts=('Clavicle','UpperArm','Forearm','Hand','Finger0') if part=='front' else ('Thigh','Calf','Foot','Toe0')
  columns=[names.index('Bip01_'+side+'_'+p) for p in parts]
  distribution=baseline[:,columns];distribution=distribution/np.maximum(distribution.sum(axis=1,keepdims=True),1e-30)
  scores[:,columns]+=limb_fields[:,k,None]*distribution
 for (side,part),points in LIMBS.items():
  parts=('Clavicle','UpperArm','Forearm','Hand','Finger0') if part=='front' else ('Thigh','Calf','Foot','Toe0')
  columns=[names.index('Bip01_'+side+'_'+p) for p in parts]
  total=scores[:,columns].sum(axis=1);paw=smooth(-.72,-.78,co[:,2])
  scores[:,columns]*=(1-paw[:,None]);scores[:,columns[-1]]+=total*paw
 # Continuous four-influence reduction: an influence approaches zero before
 # leaving the active set, rather than abruptly dropping the fifth weight.
 threshold=np.partition(scores,-5,axis=1)[:,-5]
 out=np.maximum(0,scores-threshold[:,None])
 assert np.all(out.sum(axis=1)>0)
 out/=out.sum(axis=1,keepdims=True)
 q=np.rint(out*255).astype(np.int16);best=np.argmax(out,axis=1);q[np.arange(len(q)),best]+=255-q.sum(axis=1)
 assert np.all(q>=0)
 return q.astype(np.float32)/255
