"""Continuous anatomical skin fields; edits only weights, never mesh/UV data."""
import numpy as np

def smooth(a,b,x):
 t=np.clip((x-a)/(b-a),0,1);return t*t*(3-2*t)

def weights(co,names):
 x,y,z=co.T;result=np.zeros((len(co),len(names)),np.float32)
 def chain(axis,centers,bones,mask):
  # Partition of unity, at most two adjacent bones before anatomical blending.
  for i,name in enumerate(bones):
   left=np.ones(len(co),np.float32) if i==0 else smooth(centers[i-1],centers[i],axis)
   right=np.ones(len(co),np.float32) if i==len(bones)-1 else 1-smooth(centers[i],centers[i+1],axis)
   result[:,names.index(name)]+=left*right*mask
 tail=smooth(.66,.88,x)*(1-smooth(-.12,.08,z))
 limb=(1-smooth(-.35,.10,z))*(1-tail)
 front=1-smooth(-.10,.22,x)
 chain(x-.35*np.maximum(z-.2,0),[-.72,-.34,.08,.55],
       ['Bip01_Head','Bip01_Neck','Bip01_Spine','Bip01_Pelvis'],(1-tail)*(1-limb))
 chain(x,[.68,.81,.96],['Bip01_Tail','Bip01_Tail1','Bip01_Tail2'],tail)
 for side,side_mask in [('L',y<0),('R',y>=0)]:
  sign=-1 if side=='L' else 1
  for parts,points,mask in [
   (['Clavicle','UpperArm','Forearm','Hand','Finger0'],[(-.35,.15,.16),(-.4,.17,-.13),(-.45,.18,-.44),(-.49,.19,-.73),(-.57,.19,-.79),(-.66,.19,-.79)],limb*front*side_mask),
   (['Thigh','Calf','Foot','Toe0'],[(.49,.15,.02),(.55,.18,-.28),(.67,.19,-.6),(.56,.2,-.77),(.43,.2,-.77)],limb*(1-front)*side_mask)]:
   distances=[]
   for first,last in zip(points,points[1:]):
    a=np.array(first,np.float32);a[1]*=sign;b=np.array(last,np.float32);b[1]*=sign;delta=b-a
    t=np.clip((co-a)@delta/(delta@delta),0,1)
    distances.append(np.sum((co-a-t[:,None]*delta)**2,axis=1))
   distances=np.stack(distances,axis=1);w=np.exp(-(distances-distances.min(axis=1,keepdims=True))/.012);w/=w.sum(axis=1,keepdims=True)
   for i,part in enumerate(parts):result[:,names.index('Bip01_'+side+'_'+part)]+=w[:,i]*mask
 # Engine shader permits four influences; normalize only after retaining them.
 keep=np.argpartition(result,-4,axis=1)[:,-4:];out=np.zeros_like(result)
 np.put_along_axis(out,keep,np.take_along_axis(result,keep,axis=1),axis=1)
 out/=out.sum(axis=1,keepdims=True)
 quant=np.rint(out*255).astype(np.int16);best=np.argmax(out,axis=1)
 quant[np.arange(len(co)),best]+=255-quant.sum(axis=1)
 assert np.all(quant>=0) and np.all(quant.sum(axis=1)==255)
 return quant.astype(np.float32)/255
