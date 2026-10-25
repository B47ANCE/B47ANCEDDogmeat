"""Source-fitted atlas control and a continuous, quantized head/neck split.

The supplied head faces nearly -Y, independently of the torso direction. These
are rig-fitting landmarks, not gameplay settings. Only Head/Neck weights change.
"""
import hashlib
import numpy as np

ATLAS=(-.745,.015,.435)
NECK_BASE=(-.49,.035,.19)
HEAD_FORWARD=(-.09234968807098541,-.9957266367398191,0)
HEAD_PITCH=(.9957266367398191,-.09234968807098541,0)

def smoothstep(low,high,value):
    t=np.clip((value-low)/(high-low),0,1)
    return t*t*(3-2*t)

def reweight_head(co,names,previous):
    normal=.6*np.array(HEAD_FORWARD)+np.array((0,0,.8))
    back=np.array((.96748,.25296,0));back/=np.linalg.norm(back)
    relative=co-np.array(ATLAS)
    fraction=smoothstep(-.14,-.025,relative@normal)
    fraction*=1-smoothstep(.20,.32,relative@back)
    h=names.index('Bip01_Head');n=names.index('Bip01_Neck')
    total=np.rint((previous[:,h]+previous[:,n])*255).astype(np.int16)
    head=np.rint(total*fraction).astype(np.int16)
    result=previous.copy();result[:,h]=head/255;result[:,n]=(total-head)/255
    other=[i for i in range(len(names)) if i not in (h,n)]
    assert np.array_equal(result[:,other],previous[:,other])
    assert np.max(np.abs(result.sum(axis=1)-1))<2e-7
    assert (result>0).sum(axis=1).max()<=4
    assert np.array_equal(np.rint((result[:,h]+result[:,n])*255),total)
    return result,{'atlas':ATLAS,'neck_base':NECK_BASE,'head_forward':HEAD_FORWARD,
        'head_pitch_axis':HEAD_PITCH,'transition_signed_distance':[-.14,-.025],
        'posterior_cap_along_BACK':[.20,.32],'changed_bones':['Bip01_Head','Bip01_Neck'],
        'all_other_bones_exact':True,'max_influences':int((result>0).sum(axis=1).max()),
        'changed_vertices':int(np.any(result!=previous,axis=1).sum()),
        'head_core_full_weight_vertices':int((result[:,h]==1).sum()),
        'field_sha256':hashlib.sha256(fraction.astype('<f4').tobytes()).hexdigest()}
