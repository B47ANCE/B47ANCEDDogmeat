"""Original spatial coat painting, tangent-space maps and anchored mesh groom."""
import math
import bpy
import numpy as np
from PIL import Image
from mathutils import Vector
from pathlib import Path

SIZE=2048
DETAIL=np.asarray(Image.open(Path(__file__).resolve().parents[1]/'textures'/'fur_detail_source.png').convert('L'),dtype=np.float32)/255


def smooth(a,b,x):
    t=np.clip((x-a)/(b-a),0,1);return t*t*(3-2*t)


def colors(p):
    x,y,z=p.T;ay=np.abs(y)
    grain=np.sin(x*91+y*67+z*113)*np.sin(x*137-y*101+z*59)
    wave=.012*np.sin(x*38+z*23)+.007*np.sin(x*91-z*49)+.005*grain
    tan=np.tile([.58,.395,.243],(len(p),1))
    tan+=np.clip((.37-z)/.26,0,1)[:,None]*[.10,.105,.09]
    # Warm buff throat, chest and inner hindlegs.
    bib=np.exp(-((x-.26)/.16)**2-((z-.43)/.18)**2)*smooth(.13,.05,ay)
    tan+=bib[:,None]*[.12,.12,.10]
    flank=np.exp(-((x+.15)/.22)**2-((z-.37)/.10)**2)
    tan+=flank[:,None]*[.03,.026,.02]
    saddle=smooth(.443+wave,.489+wave,z)*smooth(.31,.17,x)*smooth(-.42,-.31,x)
    # Back of neck is sable; tan cheeks and forehead remain visible.
    nape=smooth(.68+.85*(x-.31),.73+.85*(x-.31),z)*smooth(.20,.32,x)*smooth(.455,.37,x)
    mask=smooth(.405,.495,x)*smooth(.60,.64,z)*smooth(.785,.735,z)
    eye=.90*np.exp(-((x-.480)/.045)**2-((z-.746)/.027)**2)*smooth(.035,.065,ay)
    brow=np.exp(-((x-.469)/.025)**2-((z-.775)/.011)**2)*smooth(.025,.060,ay)
    forehead=.65*np.exp(-((x-.397)/.075)**2-((z-.807)/.03)**2)
    ear=smooth(.80,.86,z)*smooth(.45,.415,x)
    tail=smooth(-.38,-.46,x)*smooth(.16,.28,z)
    black=np.maximum.reduce([saddle,nape,mask,eye,forehead,ear,tail])*(1-.82*brow)
    charcoal=np.tile([.105,.101,.096],(len(p),1))
    charcoal+=np.clip((z-.45)/.4,0,1)[:,None]*[.018,.018,.02]
    c=tan*(1-black[:,None])+charcoal*black[:,None]
    mott=.04*np.sin(x*57+z*73)*np.sin(y*103-z*31)+.025*grain
    c*=1+mott[:,None]
    return np.clip(c,0,1)


def flow(p):
    x,y,z=p.T
    d=np.tile([-1.,0.,-.15],(len(p),1))
    neck=(x>.22)&(z>.46)&(x<.50)
    d[neck]=[-.65,0,-1]
    legs=(z<.36)&(x>-.38)
    d[legs]=[.10,0,-1]
    head=(x>.43)&(z>.69)
    d[head]=[-1,0,.14]
    ears=(z>.86)
    d[ears]=[0,0,1]
    tail=x<-.39
    d[tail]=[-1,0,-.42]
    d[:,1]=.22*np.sign(y)
    return d/np.maximum(np.linalg.norm(d,axis=1)[:,None],1e-8)


def hairfield(p):
    # Sample original generated short-fur detail in region-oriented material space.
    d=flow(p);x,y,z=p.T
    along=(p*d).sum(axis=1)
    across=z*d[:,0]-x*d[:,2]+y*.67
    size=np.where((x>.40)&(z>.65),.20,.40)
    u=np.mod(across/size,1)*(DETAIL.shape[1]-1)
    v=np.mod(-along/size,1)*(DETAIL.shape[0]-1)
    ui,vi=u.astype(int),v.astype(int);a,b=u-ui,v-vi
    sample=(DETAIL[vi,ui]*(1-a)*(1-b)+DETAIL[vi,(ui+1)%DETAIL.shape[1]]*a*(1-b)
            +DETAIL[(vi+1)%DETAIL.shape[0],ui]*(1-a)*b
            +DETAIL[(vi+1)%DETAIL.shape[0],(ui+1)%DETAIL.shape[1]]*a*b)
    return np.clip(.5+(sample-float(DETAIL.mean()))*1.5,0,1)


def texture(g,dog):
    g.select([dog]);bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.uv.smart_project(angle_limit=math.radians(65),island_margin=.008)
    bpy.ops.object.mode_set(mode='OBJECT')
    pos=np.zeros((SIZE,SIZE,3),np.float32);mask=np.zeros((SIZE,SIZE),bool)
    uvdata=dog.data.uv_layers.active.data
    for face in dog.data.polygons:
        uv=np.array([tuple(uvdata[i].uv)for i in face.loop_indices])*(SIZE-1)
        xyz=np.array([tuple(dog.data.vertices[i].co)for i in face.vertices])
        lo=np.floor(uv.min(axis=0)).astype(int).clip(0,SIZE-1);hi=np.ceil(uv.max(axis=0)).astype(int).clip(0,SIZE-1)
        xx,yy=np.meshgrid(np.arange(lo[0],hi[0]+1),np.arange(lo[1],hi[1]+1))
        q=np.stack([xx.ravel(),yy.ravel()],axis=1)+.5;a,b,c=uv
        det=(b[1]-c[1])*(a[0]-c[0])+(c[0]-b[0])*(a[1]-c[1])
        if abs(det)<1e-10:continue
        wa=((b[1]-c[1])*(q[:,0]-c[0])+(c[0]-b[0])*(q[:,1]-c[1]))/det
        wb=((c[1]-a[1])*(q[:,0]-c[0])+(a[0]-c[0])*(q[:,1]-c[1]))/det
        weights=np.stack([wa,wb,1-wa-wb],axis=1);inside=np.all(weights>=-1e-5,axis=1)
        rr,cc=yy.ravel()[inside],xx.ravel()[inside]
        pos[rr,cc]=weights[inside]@xyz;mask[rr,cc]=True
    coverage=float(mask.mean())
    # Dilate world-position field before evaluation, giving consistent atlas padding.
    for _ in range(12):
        old=mask.copy()
        for ax,step in [(0,1),(0,-1),(1,1),(1,-1)]:
            take=(~mask)&np.roll(old,step,axis=ax)
            pos[take]=np.roll(pos,step,axis=ax)[take];mask[take]=True
    p=pos[mask];h=hairfield(p)
    col=colors(p)*(1+.95*(h-.5)[:,None])
    rgb=np.full((SIZE,SIZE,3),.3,np.float32);rgb[mask]=col
    height=np.full((SIZE,SIZE),.5,np.float32);height[mask]=h
    # Tangent-space hair relief derived from the packed UV height map.
    dx=np.roll(height,-1,axis=1)-np.roll(height,1,axis=1)
    dy=np.roll(height,-1,axis=0)-np.roll(height,1,axis=0)
    normal=np.stack([-dx*1.45,-dy*1.45,np.ones_like(dx)],axis=2)
    normal/=np.linalg.norm(normal,axis=2)[:,:,None];normal=normal*.5+.5
    rough=np.full((SIZE,SIZE,3),.79,np.float32);rough[mask]=(.78+(h-.5)*.13)[:,None]
    mat=g.material('GSD_Coat',(.5,.3,.2),.79);nodes=mat.node_tree.nodes;links=mat.node_tree.links
    bs=nodes.get('Principled BSDF')
    maps={}
    for role,data in [('albedo',rgb),('normal',normal),('roughness',rough)]:
        path=g.ROOT/'textures'/('coat_'+role+'.png')
        Image.fromarray(np.flipud(np.round(np.clip(data,0,1)*255).astype(np.uint8))).save(path)
        im=bpy.data.images.load(str(path),check_existing=False);im.name='GSD_Coat_'+role+'_2048'
        if role!='albedo':im.colorspace_settings.name='Non-Color'
        im.pack();im.filepath='//../textures/'+path.name
        n=nodes.new('ShaderNodeTexImage');n.image=im;n.label=role;maps[role]=n
    links.new(maps['albedo'].outputs['Color'],bs.inputs['Base Color'])
    links.new(maps['roughness'].outputs['Color'],bs.inputs['Roughness'])
    nm=nodes.new('ShaderNodeNormalMap');nm.inputs['Strength'].default_value=.06
    links.new(maps['normal'].outputs['Color'],nm.inputs['Color']);links.new(nm.outputs['Normal'],bs.inputs['Normal'])
    dog.data.materials.clear();dog.data.materials.append(mat)
    return coverage


def groom(g,dog,rig,count=65000):
    """Narrow tapered mesh ribbons. Every ribbon inherits its skin root weights."""
    rng=np.random.default_rng(47002)
    verts=np.array([tuple(v.co)for v in dog.data.vertices]);norms=np.array([tuple(v.normal)for v in dog.data.vertices])
    faces=np.array([tuple(p.vertices)for p in dog.data.polygons]);areas=np.array([p.area for p in dog.data.polygons])
    ids=rng.choice(len(faces),count,p=areas/areas.sum());tri=faces[ids]
    # Exact surface-vertex roots avoid LBS covariance drift: interpolating
    # weights and position independently does not equal a deformed triangle.
    corners=rng.integers(0,3,count)
    w=np.eye(3)[corners]
    p=(verts[tri]*w[:,:,None]).sum(axis=1);n=(norms[tri]*w[:,:,None]).sum(axis=1);n/=np.linalg.norm(n,axis=1)[:,None]
    x,y,z=p.T
    # Keep ear interiors and detailed eyes/nostrils clean. Short face whisker coat.
    ok=~((z>.80)&(n[:,0]>.35))
    # Read refined geometry so proportional edits cannot stale the groom masks.
    for side in ['L','R']:
        eye=bpy.data.objects['GSD_Eye_'+side]
        ep=np.array([tuple(v.co)for v in eye.data.vertices]);lo,hi=ep.min(axis=0)-.005,ep.max(axis=0)+.005
        ok &= ~np.all((p>=lo)&(p<=hi),axis=1)
    p,n,tri,w=p[ok],n[ok],tri[ok],w[ok];count=len(p);x,y,z=p.T
    d=flow(p);d-=n*(d*n).sum(axis=1)[:,None]
    d+=rng.normal(0,.12,d.shape);d-=n*(d*n).sum(axis=1)[:,None]
    d/=np.maximum(np.linalg.norm(d,axis=1)[:,None],1e-8)
    side=np.cross(n,d);side/=np.maximum(np.linalg.norm(side,axis=1)[:,None],1e-8)
    ruff=smooth(.10,.24,x)*smooth(.46,.34,x)*smooth(.28,.42,z)*smooth(.78,.67,z)
    length=.007+.005*ruff
    length=length*(1-smooth(-.38,-.48,x))+.022*smooth(-.38,-.48,x)
    short=np.maximum(smooth(.38,.28,z),smooth(.38,.46,x)*smooth(.60,.69,z))
    length=length*(1-short)+.0025*short
    ears=smooth(.80,.86,z);length=length*(1-ears)+.003*ears
    length*=rng.uniform(.55,1.30,count)
    width=np.clip(length*.041,.00015,.00075)*rng.uniform(.7,1.2,count)
    points=np.zeros((count,5,3))
    lift=.23+.22*smooth(-.35,-.49,x)+.08*ruff
    base=p-n*.0002;middle=p+d*length[:,None]*.56+n*(length*lift)[:,None]
    tip=p+d*length[:,None]+n*(length*lift)[:,None]
    points[:,0]=base-side*width[:,None];points[:,1]=base+side*width[:,None]
    points[:,2]=middle-side*width[:,None]*.55;points[:,3]=middle+side*width[:,None]*.55;points[:,4]=tip
    ff=[]
    for i in range(count):
        a=i*5;ff.extend([(a,a+1,a+3,a+2),(a+2,a+3,a+4)])
    obj=g.mesh_obj('GSD_GuardFur',points.reshape(-1,3).tolist(),ff)
    basecolor=colors(p)*(1+.7*(hairfield(p)-.5)[:,None])*rng.uniform(.79,1.26,(count,1));basecolor=np.clip(basecolor,0,1)
    rgba=np.ones((count,5,4),np.float32)
    for j,factor in enumerate([.82,.82,1.03,1.03,1.15]):
        srgb=np.clip(basecolor*factor,0,1)
        rgba[:,j,:3]=np.where(srgb<=.04045,srgb/12.92,((srgb+.055)/1.055)**2.4)
    attr=obj.data.color_attributes.new(name='CoatColor',type='FLOAT_COLOR',domain='POINT')
    attr.data.foreach_set('color',rgba.reshape(-1))
    mat=g.material('GSD_GuardHair',(.4,.3,.2),.78);nodes=mat.node_tree.nodes
    c=nodes.new('ShaderNodeVertexColor');c.layer_name='CoatColor'
    mat.node_tree.links.new(c.outputs['Color'],nodes.get('Principled BSDF').inputs['Base Color']);obj.data.materials.append(mat)
    groups={vg.index:obj.vertex_groups.new(name=vg.name)for vg in dog.vertex_groups}
    root_records=[]
    for i,(indices,weights)in enumerate(zip(tri,w)):
        sums={}
        for idx,bary in zip(indices,weights):
            for item in dog.data.vertices[int(idx)].groups:sums[item.group]=sums.get(item.group,0)+item.weight*bary
        chosen=sorted(sums.items(),key=lambda a:a[1],reverse=True)[:4];total=sum(v for _,v in chosen)
        for grp,weight in chosen:groups[grp].add(list(range(i*5,i*5+5)),float(weight/total),'REPLACE')
        if i%1000==0:root_records.append({'vertex':i*5,'body_vertices':indices.tolist(),'barycentric':weights.tolist(),'rest_distance_m':float(np.linalg.norm(points[i,0]-p[i]))})
    mod=obj.modifiers.new('GSD_Skin','ARMATURE');mod.object=rig;obj.parent=rig
    obj['groom_method']='Original mesh ribbons; exact skin-vertex roots inherit identical weights. No Blender particle dependency.'
    g.MODEL.append(obj)
    return {'strand_count':count,'triangles':count*3,'root_probes':root_records}
