"""Author em-v004 mouth anatomy in a fresh standalone Blender process.

Original em-v001 is read-only. This is an editable art checkpoint, not a PZ
registration, approved final likeness, production animation rig or paid job.
"""
import argparse
from collections import Counter
import hashlib
import json
import math
from pathlib import Path

import bpy
import bmesh
from mathutils import Vector
from mathutils.bvhtree import BVHTree

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parents[1]
BASE = REPO / 'art/english_mastiff/interchange/english_mastiff.glb'
BASE_SHA = '37c8e1cc6e47f9ffde22aa93346e8d91f15fb4c3d90843e4cb278e2aab07bd31'
LIFT = 0.6689440608
YAW = math.radians(30)
FRAME_ORIGIN = Vector((0, -.8, 0))
WORLD_ORIGIN = Vector((.05, -.8, 0))


def world_point(co):
    x,y,z=Vector(co)-FRAME_ORIGIN
    return Vector((x*math.cos(YAW)-y*math.sin(YAW),x*math.sin(YAW)+y*math.cos(YAW),z))+WORLD_ORIGIN


def mouth_point(co):
    x,y,z=Vector(co)-WORLD_ORIGIN
    return Vector((x*math.cos(YAW)+y*math.sin(YAW),-x*math.sin(YAW)+y*math.cos(YAW),z))+FRAME_ORIGIN


HINGE = world_point((0, -.704, 1.075))
BACK = -.705
SOURCE_SURFACE = None


def write_json(path, data):
    path.write_text(json.dumps(data, indent=2) + '\n', encoding='utf-8', newline='\n')


def smooth(a, b, x):
    t = max(0, min(1, (x-a)/(b-a)))
    return t*t*(3-2*t)


def lip_z(x, y):
    # Front split follows the dropped upper jowls rather than a flat grin.
    return .986 - .060*math.exp(-((abs(x)-.112)/.065)**2) + .065*smooth(-.87, BACK, y)


def jaw_weight(co):
    p=mouth_point(co)
    width=.145+.75*max(0,1.027-p.z)
    return 1-smooth(BACK-width,BACK,p.y)


def neck_weight(co):
    p=mouth_point(co)
    return smooth(BACK-.020,BACK,p.y)*(1-smooth(BACK,BACK+.11,p.y))*(1-smooth(1.06,1.12,p.z))


def rear_offset(depth):
    # A planar posterior cheek attachment avoids folding the inner transition
    # around the underside of the loose jowls. It remains fixed to the head.
    return 0.0


def material(name, color, roughness=.45):
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*color, 1)
    m.use_nodes = True
    p = m.node_tree.nodes.get('Principled BSDF')
    p.inputs['Base Color'].default_value = (*color, 1)
    p.inputs['Roughness'].default_value = roughness
    return m


def mesh_object(name, verts, faces, mat, smooth_faces=True):
    m = bpy.data.meshes.new(name)
    m.from_pydata(verts, [], faces)
    m.update()
    o = bpy.data.objects.new(name, m)
    bpy.context.scene.collection.objects.link(o)
    if mat: m.materials.append(mat)
    uv = m.uv_layers.new(name='AnatomyUV')
    lo = [min(v[i] for v in verts) for i in range(3)]
    hi = [max(v[i] for v in verts) for i in range(3)]
    for p in m.polygons:
        p.use_smooth = smooth_faces
        for li in p.loop_indices:
            co = m.vertices[m.loops[li].vertex_index].co
            uv.data[li].uv = ((co.x-lo[0])/max(hi[0]-lo[0], 1e-8),
                              (co.y-lo[1])/max(hi[1]-lo[1], 1e-8))
    bm = bmesh.new(); bm.from_mesh(m)
    bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
    bm.to_mesh(m); bm.free()
    return o


def boundary_loop(bm):
    edges = [e for e in bm.edges if e.is_boundary]
    if not edges: raise ValueError('Expected an open surgery boundary')
    adjacent = {}
    for e in edges:
        for v in e.verts: adjacent.setdefault(v, []).append(e.other_vert(v))
    if any(len(a) != 2 for a in adjacent.values()):
        raise ValueError('Surgery boundary branches')
    start = min(adjacent, key=lambda v: (v.co.y, abs(v.co.x)))
    loop = [start]; previous = None; current = start
    while True:
        nxt = next(v for v in adjacent[current] if v != previous)
        if nxt == start: break
        loop.append(nxt); previous, current = current, nxt
        if len(loop) > len(adjacent): raise ValueError('Invalid cut loop')
    if len(loop) != len(adjacent): raise ValueError('Unexpected second cut boundary')
    return loop


def oral_footprint(ring):
    """Map the lip U and posterior chin arc separately to a convex oral rim.

    The 3D incision is not star-shaped in XY. Projecting it to a center fan
    folds the palate/floor. Semantic arc correspondence keeps the back behind
    the dental arch while the lip remains at the front.
    """
    n=len(ring)
    lip=[abs(v.co.z-lip_z(v.co.x,v.co.y))<2e-5 for v in ring]
    if all(lip):
        distances=[0.0]
        for a,b in zip(ring,ring[1:]):distances.append(distances[-1]+(a.co-b.co).length)
        sign=-1 if ring[0].co.x<ring[-1].co.x else 1
        return [Vector((sign*.110*math.cos(math.pi*d/distances[-1]),-.728-.182*math.sin(math.pi*d/distances[-1]),0)) for d in distances]
    starts=[i for i in range(n) if lip[i] and not lip[(i-1)%n]]
    if len(starts)!=1:raise ValueError(f'Expected one contiguous lip arc, got {len(starts)}')
    start=starts[0];front=[];i=start
    while lip[i]:
        front.append(i);i=(i+1)%n
        if i==start:raise ValueError('No posterior arc')
    end=front[-1]
    back=[end];i=(end+1)%n
    while i!=start:back.append(i);i=(i+1)%n
    back.append(start)
    targets=[None]*n
    def params(indices):
        d=[0.0]
        for a,b in zip(indices,indices[1:]):d.append(d[-1]+(ring[a].co-ring[b].co).length)
        return [x/d[-1] for x in d]
    sign=-1 if ring[start].co.x<ring[end].co.x else 1
    for idx,t in zip(front,params(front)):
        targets[idx]=Vector((sign*.110*math.cos(math.pi*t),-.728-.182*math.sin(math.pi*t),0))
    for idx,t in zip(back,params(back)):
        targets[idx]=Vector((-sign*.110*(1-2*t),-.728+.008*math.sin(math.pi*t),0))
    return targets


def earclip(points):
    # Double-precision inclusive tests retain dense/collinear boundary nodes.
    def cross(a,b,c):return (b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0])
    area=sum(a[0]*b[1]-a[1]*b[0] for a,b in zip(points,points[1:]+points[:1]))*.5
    sign=1 if area>0 else -1;ids=list(range(len(points)));tris=[]
    while len(ids)>3:
        ears=[]
        for i,b in enumerate(ids):
            a=ids[i-1];c=ids[(i+1)%len(ids)];cr=cross(points[a],points[b],points[c])*sign
            if cr<=1e-15:continue
            if any(min(cross(points[a],points[b],points[k])*sign,cross(points[b],points[c],points[k])*sign,
                       cross(points[c],points[a],points[k])*sign)>=-1e-15 for k in ids if k not in (a,b,c)):continue
            per=sum(math.dist(points[u],points[v])**2 for u,v in [(a,b),(b,c),(c,a)])
            ears.append((cr/max(per,1e-30),i,(a,b,c)))
        if not ears:raise ValueError('No valid planar ear; stop rather than emit folded cap')
        _,i,t=max(ears);tris.append(t);ids.pop(i)
    tris.append(tuple(ids));return tris


def posterior_jaw_patch(bm,ring):
    n=len(ring);lip=[abs(v.co.z-lip_z(v.co.x,v.co.y))<2e-5 for v in ring]
    start=next(i for i in range(n) if lip[i] and not lip[(i-1)%n])
    front=[];i=start
    while lip[i]:front.append(ring[i]);i=(i+1)%n
    back=[front[-1]]
    while i!=start:back.append(ring[i]);i=(i+1)%n
    back.append(front[0])
    # Rear chin cross-section is planar and concave, so triangulate it as a
    # polygon instead of forcing its low U into the horizontal oral floor.
    for tri in earclip([(float(v.co.x),float(v.co.z)) for v in back]):
        f=bm.faces.new([back[i] for i in tri]);f.material_index=1
    return front


def profile_lining(bm,ring,upper,inset):
    """A nonoverlapping planar triangulation, profiled vertically into the mouth.

    The source jowl rim doubles back locally. A radial loft folds it; retain its
    exact boundary with a constrained triangulation and refine inside only.
    """
    points=[(float(v.co.x),float(v.co.y)) for v in ring]
    faces=[]
    for tri in earclip(points):
        f=bm.faces.new([ring[i] for i in tri]);f.material_index=3;faces.append(f)
    for _ in range(2):
        mids={};created=[]
        for f in faces:
            sequence=[]
            for loop in f.loops:
                sequence.append(loop.vert);e=loop.edge
                if len(e.link_faces)==2 and all(x.material_index==3 for x in e.link_faces):
                    if e not in mids:mids[e]=bm.verts.new((e.verts[0].co+e.verts[1].co)*.5)
                    sequence.append(mids[e])
            c=bm.verts.new(sum((v.co for v in f.verts),Vector())/len(f.verts))
            for i in range(len(sequence)):
                nf=bm.faces.new((sequence[i],sequence[(i+1)%len(sequence)],c));nf.material_index=3;created.append(nf)
        bmesh.ops.delete(bm,geom=faces,context='FACES_ONLY')
        loose=[e for e in bm.edges if not e.link_faces]
        if loose:bmesh.ops.delete(bm,geom=loose,context='EDGES')
        faces=created
    def distance(p):
        best=10
        for a,b in zip(points,points[1:]+points[:1]):
            x,y=b[0]-a[0],b[1]-a[1]
            t=max(0,min(1,((p.x-a[0])*x+(p.y-a[1])*y)/max(x*x+y*y,1e-30)))
            best=min(best,math.hypot(p.x-a[0]-t*x,p.y-a[1]-t*y))
        return best
    boundary=set(ring)
    # Constrain a narrow rim strip. Midpoint subdivision alone leaves long ramps
    # from a boundary vertex through the teeth to the distant roof/floor plateau.
    split={};newfaces=[]
    def rim_point(a,b):
        key=frozenset((a,b))
        if key not in split:
            lo=0;hi=1
            for _ in range(32):
                t=(lo+hi)*.5
                if distance(a.co.lerp(b.co,t))<.0015:lo=t
                else:hi=t
            split[key]=bm.verts.new(a.co.lerp(b.co,(lo+hi)*.5))
        return split[key]
    for f in faces:
        vs=list(f.verts);bs=[v for v in vs if v in boundary]
        if len(bs)==1:
            a=bs[0];idx=vs.index(a);b=vs[(idx+1)%3];c=vs[(idx+2)%3]
            p=rim_point(a,b);q=rim_point(a,c)
            polys=[(a,p,q),(p,b,c),(p,c,q)]
        elif len(bs)==2:
            c=next(v for v in vs if v not in boundary);idx=vs.index(c)
            a=vs[(idx+1)%3];b=vs[(idx+2)%3]
            p=rim_point(a,c);q=rim_point(b,c)
            polys=[(a,b,q),(a,q,p),(p,q,c)]
        else:polys=[tuple(vs)]
        if len(polys)==1:newfaces.append(f);continue
        for poly in polys:
            nf=bm.faces.new(poly);nf.material_index=3;newfaces.append(nf)
        bmesh.ops.delete(bm,geom=[f],context='FACES_ONLY')
    loose=[e for e in bm.edges if not e.link_faces]
    if loose:bmesh.ops.delete(bm,geom=loose,context='EDGES')
    faces=newfaces
    for v in {v for f in faces for v in f.verts}:
        d=0 if v in boundary else distance(v.co)
        w=smooth(0,.0015,d)
        v.co.z=v.co.z*(1-w)+(1.075 if upper else .934)*w
        if v not in boundary:
            # Interior linings must fit the retained head, not protrude through
            # the nose/jowls when the global roof/floor height exceeds the coat.
            def column(p):
                hi=SOURCE_SURFACE.ray_cast(Vector((p.x,p.y,2)),Vector((0,0,-1)))[0]
                lo=SOURCE_SURFACE.ray_cast(Vector((p.x,p.y,.5)),Vector((0,0,1)))[0]
                return hi,lo
            hi,lo=column(v.co)
            if hi is None or lo is None:
                direction=Vector((0,-.82,0))-Vector((v.co.x,v.co.y,0))
                direction.normalize()
                for amount in (.00001,.00005,.0002,.001,.003):
                    trial=v.co+direction*amount;hi,lo=column(trial)
                    if hi is not None and lo is not None:v.co.x=trial.x;v.co.y=trial.y;break
            if hi is None or lo is None or hi.z<lo.z:raise ValueError('No bounded source-head column at lining node')
            pad=min(.005,(hi.z-lo.z)*.20)
            v.co.z=max(lo.z+pad,min(hi.z-pad,v.co.z))
        v[inset]=min(1,d/.020)
    uv=bm.loops.layers.uv.active
    for f in faces:
        f.material_index=2 if distance(f.calc_center_median())<.004 else 1
        for l in f.loops:l[uv].uv=((l.vert.co.x+.2)/.4,(l.vert.co.y+1)/.4)
    # The source contains very narrow jowl ears. Their inset can terminate at
    # an existing interior node; weld only new lining nodes, never coat/rim UVs.
    created=[v for v in bm.verts if v not in boundary and any(f.material_index in (1,2) for f in v.link_faces)]
    bmesh.ops.remove_doubles(bm,verts=created,dist=2e-6)


def cut_mandible(obj, lining, lip):
    """Curved lip incision and posterior cheek cut, preserving loop UVs."""
    bm = bmesh.new(); bm.from_mesh(obj.data)
    bmesh.ops.remove_doubles(bm, verts=list(bm.verts), dist=1e-6)
    uv = bm.loops.layers.uv.active
    original = bm.verts.layers.int.new('base_vertex')
    bm.verts.index_update()
    for v in bm.verts: v[original] = v.index+1
    before = [{'co': list(v.co), 'index': v.index} for v in bm.verts]
    # Flatten a smooth curved cutting surface temporarily; bisect interpolates UVs.
    for v in bm.verts: v.co.z -= lip_z(v.co.x, v.co.y)
    fs = [f for f in bm.faces if all(v.co.y < BACK+.04 for v in f.verts)
          and all(v.co.z > -.28 for v in f.verts)]
    geo = set(fs)
    for f in fs: geo.update(f.edges); geo.update(f.verts)
    bmesh.ops.bisect_plane(bm, geom=list(geo), dist=1e-8,
                          plane_co=(0, 0, 0), plane_no=(0, 0, 1))
    for v in bm.verts:v.co.y+=rear_offset(v.co.z)
    fs = [f for f in bm.faces if all(v.co.z < 1e-7 for v in f.verts)
          and any(v.co.y < BACK for v in f.verts)
          and all(v.co.y < BACK+.045 and v.co.z > -.28 for v in f.verts)]
    geo = set(fs)
    for f in fs: geo.update(f.edges); geo.update(f.verts)
    bmesh.ops.bisect_plane(bm, geom=list(geo), dist=1e-8,
                          plane_co=(0, BACK, 0), plane_no=(0, 1, 0))
    lower = [f for f in bm.faces if all(v.co.y <= BACK+1e-7 and -.27 < v.co.z <= 1e-7 for v in f.verts)]
    if not 50 < len(lower) < 2000: raise ValueError(f'Unexpected jaw cut: {len(lower)} faces')
    for v in bm.verts:
        v.co.y-=rear_offset(v.co.z)
        v.co.z += lip_z(v.co.x, v.co.y)
    vs = sorted({v for f in lower for v in f.verts}, key=lambda v:v.index)
    ids = {v:i for i,v in enumerate(vs)}
    jaw = mesh_object('DM_Mandible', [tuple(v.co) for v in vs],
                      [[ids[v] for v in f.verts] for f in lower], obj.data.materials[0])
    outuv = jaw.data.uv_layers.active
    for old, new in zip(lower, jaw.data.polygons):
        for loop, li in zip(old.loops, new.loop_indices): outuv.data[li].uv = loop[uv].uv
    bmesh.ops.delete(bm, geom=lower, context='FACES')
    loose = [v for v in bm.verts if not v.link_faces]
    if loose: bmesh.ops.delete(bm, geom=loose, context='VERTS')
    bm.to_mesh(obj.data); bm.free(); obj.data.update()
    # The original cap has been removed. Each exterior is closed with an inset
    # lining, producing opposing roof/floor surfaces rather than a hollow skull.
    surgery = {'cut_faces':len(lower), 'cut_method':'curved lip incision and posterior cheek boundary',
               'hinge_source_units':list(HINGE), 'posterior_boundary_y':BACK}
    for part, upper in [(obj, True), (jaw, False)]:
        part.data.materials.append(lining)
        part.data.materials.append(lip)
        bm = bmesh.new(); bm.from_mesh(part.data)
        inset=bm.verts.layers.float.new('oral_inset')
        ring = boundary_loop(bm)
        surgery[part.name+'_boundary_vertices'] = len(ring)
        surgery[part.name+'_lip_boundary'] = [list(v.co) for v in ring]
        ring=posterior_jaw_patch(bm,ring)
        profile_lining(bm,ring,upper,inset)
        bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
        bm.to_mesh(part.data);bm.free();part.data.update()
        for p in part.data.polygons:p.use_smooth=True
    return jaw, surgery, before


def preserve_coat_normals(parts,reference):
    from mathutils.bvhtree import BVHTree
    from mathutils.geometry import barycentric_transform
    reference.calc_loop_triangles()
    verts=[v.co.copy() for v in reference.vertices]
    tris=[tuple(t.vertices) for t in reference.loop_triangles]
    normals=[v.normal.copy() for v in reference.vertices]
    tree=BVHTree.FromPolygons(verts,tris,all_triangles=True)
    for obj in parts:
        mesh=obj.data;mesh.update()
        values=[n.vector.copy() for n in mesh.corner_normals]
        for p in mesh.polygons:
            if p.material_index!=0:continue
            for li in p.loop_indices:
                pos=mesh.vertices[mesh.loops[li].vertex_index].co
                near,_,idx,_=tree.find_nearest(pos)
                ids=tris[idx]
                n=barycentric_transform(near,*[verts[i] for i in ids],*[normals[i] for i in ids]).normalized()
                values[li]=n
        mesh.normals_split_custom_set(values)


def arch_path(upper, side):
    if upper:
        return [(0,-.931,1.044),(.026,-.929,1.044),(.052,-.918,1.044),
                (.078,-.896,1.044),(.090,-.863,1.044),(.096,-.820,1.044),
                (.097,-.777,1.044),(.089,-.730,1.044),(.080,-.713,1.044)]
    return [(0,-.935,.944),(.024,-.932,.944),(.047,-.919,.944),
            (.061,-.899,.944),(.072,-.862,.944),(.080,-.820,.944),
            (.082,-.778,.944),(.075,-.731,.944),(.065,-.711,.944)]


def tube(name, points, radii, mat, sides=12):
    verts=[]; faces=[]
    points=[Vector(p) for p in points]
    for i,p in enumerate(points):
        tangent=(points[min(i+1,len(points)-1)]-points[max(0,i-1)]).normalized()
        normal=tangent.cross(Vector((0,0,1))).normalized()
        binormal=tangent.cross(normal).normalized()
        for j in range(sides):
            a=2*math.pi*j/sides
            verts.append(tuple(p+normal*(radii[i][0]*math.cos(a))+binormal*(radii[i][1]*math.sin(a))))
    for i in range(len(points)-1):
        for j in range(sides):
            a=i*sides+j;b=i*sides+(j+1)%sides
            faces.append((a,b,b+sides,a+sides))
    faces.append(tuple(reversed(range(sides))))
    faces.append(tuple((len(points)-1)*sides+j for j in range(sides)))
    return mesh_object(name,verts,faces,mat)


def gums(upper,mat):
    half=arch_path(upper,1)
    points=[(-x,y,z) for x,y,z in reversed(half[1:])]+half
    if not upper:points=[(x,y,z+.001) for x,y,z in points]
    obj=tube('DM_Gums_Upper' if upper else 'DM_Gums_Lower',points,[(.010,.010)]*len(points),mat)
    if not upper:
        # Raised cervical crest, with a deeper basal ridge joining the floor.
        # Do not lift crowns out of the gums or leave a floating dental arch.
        for v in obj.data.vertices:
            delta=v.co.z-.945
            v.co.z=.975+(delta if delta>=0 else delta*4)
        obj.data.update()
    return obj


def tooth(name, pos, rx, ry, height, upper, kind, mat):
    # Crown meshes have collars, embedded roots and distinct cutting/cusp forms.
    n=12; verts=[]; faces=[]; sign=-1 if upper else 1
    if kind=='C': levels=[(-.010,.66),(0,1),(.26,.88),(.62,.51),(.88,.21),(1,.045)]
    elif kind=='I':levels=[(-.008,.63),(0,.72),(.55,.98),(.88,1),(1,.80)]
    else:levels=[(-.009,.70),(0,.92),(.38,1),(.70,.88),(.91,.54),(1,.12)]
    for t,s in levels:
        for j in range(n):
            a=2*math.pi*j/n
            cusp=0
            if kind in ('P','M') and t>.55:
                cusp=(.20 if kind=='M' else .31)*(t-.55)*math.cos(a*(4 if kind=='M' else 2))
            x=rx*s*math.cos(a)
            y=ry*s*math.sin(a)+(.004*t*t if kind=='C' else 0)
            verts.append((pos[0]+x,pos[1]+y,pos[2]+sign*(height*t+height*cusp)))
    for i in range(len(levels)-1):
        for j in range(n):
            a=i*n+j;b=i*n+(j+1)%n;faces.append((a,b,b+n,a+n))
    faces.append(tuple(reversed(range(n))))
    faces.append(tuple((len(levels)-1)*n+j for j in range(n)))
    o=mesh_object(name,verts,faces,mat)
    o['tooth_class']=kind;o['arch']='upper' if upper else 'lower'
    return o


def dentition(mat):
    output=[]; inventory=[]
    for upper in (True,False):
        for side,sgn in [('L',1),('R',-1)]:
            teeth=[]
            for i in range(3):
                x=(.010+.017*i) if upper else (.009+.014*i)
                y=(-.924+.003*i) if upper else (-.930+.003*i)
                teeth.append(('I',i+1,x,y,.0065,.005,.021 if upper else .020))
            teeth.append(('C',1,.076 if upper else .059,-.893 if upper else -.912,.0085,.009,.058 if upper else .047))
            ys=[-.863,-.836,-.809,-.780] if upper else [-.880,-.854,-.827,-.799]
            xs=[.089,.094,.097,.097] if upper else [.071,.076,.080,.082]
            for i,(x,y) in enumerate(zip(xs,ys)):
                teeth.append(('P',i+1,x,y,.0065+.0007*i,.008+.001*i,.018+.003*i))
            ys=[-.747,-.722] if upper else [-.766,-.740,-.717]
            xs=[.092,.082] if upper else [.081,.077,.067]
            for i,(x,y) in enumerate(zip(xs,ys)):
                teeth.append(('M',i+1,x,y,.009,.010 if i==0 else .0085,.022-.002*i))
            for kind,i,x,y,rx,ry,h in teeth:
                if upper and side=='R' and kind=='P' and i==4:x-=.003
                name=f'DM_Tooth_{"U" if upper else "L"}_{side}_{kind}{i}'
                o=tooth(name,(sgn*x,y,1.043 if upper else .985),rx,ry,h,upper,kind,mat)
                output.append(o)
                inventory.append({'object':name,'arch':o['arch'],'side':side,'class':kind,'number':i,
                                  'bone':'DM_Head' if upper else 'DM_Jaw'})
    return output,inventory


def tongue(mat):
    # Closed, independent elliptical cross sections with root/middle/tip loops.
    verts=[];faces=[];n=16;rows=25
    for i in range(rows):
        t=i/(rows-1);y=-.718-.192*t
        width=.036+.009*math.sin(math.pi*t)-.017*t**4
        thickness=.0085-.003*t
        for j in range(n):
            a=2*math.pi*j/n
            z=.963+thickness*math.sin(a)
            if math.sin(a)>0:z-=.0025*math.exp(-(math.cos(a)/.18)**2)*math.sin(math.pi*t)
            verts.append((width*math.cos(a),y,z))
    for i in range(rows-1):
        for j in range(n):
            a=i*n+j;b=i*n+(j+1)%n;faces.append((a,b,b+n,a+n))
    faces.append(tuple(reversed(range(n))))
    # Rounded cap avoids a permanently flat or pointed tongue tip.
    end=len(verts);verts.append((0,-.918,.963))
    for j in range(n):faces.append(((rows-1)*n+j,(rows-1)*n+(j+1)%n,end))
    o=mesh_object('DM_Tongue',verts,faces,mat)
    o['longitudinal_rows']=rows;o['cross_section_vertices']=n
    return o


def palate(mat):
    # Low transverse palatal ridges, separate from the smooth roof lining.
    parts=[]
    for i in range(7):
        y=-.89+i*.022
        pts=[]
        for j in range(13):
            x=-.058+.116*j/12
            pts.append((x,y+.003*math.cos(math.pi*x/.116),1.057+.007*(x/.065)**2))
        parts.append(tube(f'DM_PalatalRidge_{i+1:02d}',pts,[(.0022,.0022)]*len(pts),mat,8))
    return parts


def build_eyes(body, rim_material):
    """Replace painted eye centers locally; retain original surrounding coat UVs.

    Landmarks come from the original texture projected onto original geometry,
    in world/source coordinates. Socket cap, eyeball and blinking lid are distinct.
    """
    eye_mats=[material('DM_Eye_Sclera',(.035,.025,.020),.26),
              material('DM_Eye_IrisDark',(.055,.025,.010),.26),
              material('DM_Eye_IrisAmber',(.085,.040,.015),.26),
              material('DM_Eye_Pupil',(.002,.002,.001),.20)]
    for m in eye_mats:m.node_tree.nodes.get('Principled BSDF').inputs['Specular IOR Level'].default_value=.08
    parts=[];landmarks=[]
    for side,cx in [('R',-.023),('L',.141)]:
        cz=1.162;rx=.021;rz=.015
        body.data.update()
        hit,point,_,_=body.ray_cast(Vector((cx,-2,cz)),Vector((0,1,0)))
        if not hit:raise ValueError('Missing original eye surface')
        cy=point.y
        bm=bmesh.new();bm.from_mesh(body.data)
        def distance(p):return ((p.x-cx)/rx)**2+((p.z-cz)/rz)**2
        patch=[f for f in bm.faces if distance(f.calc_center_median())<4
               and abs(f.calc_center_median().y-cy)<.055]
        edges=list({e for f in patch for e in f.edges})
        bmesh.ops.subdivide_edges(bm,edges=edges,cuts=2,use_grid_fill=True)
        ngons=[f for f in bm.faces if f.material_index==0 and len(f.verts)>3]
        if ngons:bmesh.ops.triangulate(bm,faces=ngons,quad_method='BEAUTY',ngon_method='BEAUTY')
        tiny=[f for f in bm.faces if f.calc_area()<1e-12]
        if tiny:bmesh.ops.dissolve_degenerate(bm,dist=1e-7,edges=list({e for f in tiny for e in f.edges}))
        removed=[f for f in bm.faces if distance(f.calc_center_median())<1
                 and abs(f.calc_center_median().y-cy)<.030]
        if not removed:raise ValueError('No eye aperture cut')
        bmesh.ops.delete(bm,geom=removed,context='FACES')
        loose=[v for v in bm.verts if not v.link_faces]
        if loose:bmesh.ops.delete(bm,geom=loose,context='VERTS')
        ring=boundary_loop(bm)
        angles=[math.atan2((v.co.z-cz)/rz,(v.co.x-cx)/rx) for v in ring]
        outer=[v.co.copy() for v in ring]
        # Recessed socket closes the original shell behind the independent eye.
        new=[]
        for a in angles:new.append(bm.verts.new((cx+rx*.78*math.cos(a),cy+.027,cz+rz*.78*math.sin(a))))
        idx=len(body.data.materials)
        body.data.materials.append(rim_material)
        uv=bm.loops.layers.uv.active
        for i in range(len(ring)):
            f=bm.faces.new((ring[i],ring[(i+1)%len(ring)],new[(i+1)%len(ring)],new[i]));f.material_index=idx
            for l in f.loops:l[uv].uv=((l.vert.co.x-cx)/rx*.5+.5,(l.vert.co.z-cz)/rz*.5+.5)
        center=bm.verts.new((cx,cy+.031,cz))
        for i in range(len(new)):
            f=bm.faces.new((new[i],new[(i+1)%len(new)],center));f.material_index=idx
        bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
        bm.to_mesh(body.data);bm.free();body.data.update()
        # Annular closed lid, with a real blink morph and fixed outer attachments.
        verts=[];faces=[];n=len(outer)
        for back in (False,True):
            for inner in (False,True):
                for p,a in zip(outer,angles):
                    if inner:p=Vector((cx+.018*math.cos(a),cy-.006,cz+.012*math.sin(a)))
                    else:p=p+Vector((0,-.001,0))
                    if back:p=p+Vector((0,.001,0))
                    verts.append(tuple(p))
        for i in range(n):
            j=(i+1)%n
            faces.extend([(i,j,n+j,n+i),(2*n+i,3*n+i,3*n+j,2*n+j),
                          (i,2*n+i,2*n+j,j),(n+i,n+j,3*n+j,3*n+i)])
        lid=mesh_object('DM_Eyelid.'+side,verts,faces,rim_material)
        lid.shape_key_add(name='Basis')
        blink=lid.shape_key_add(name='Blink')
        blink.value=0
        for back in (0,1):
            for i,a in enumerate(angles):
                p=blink.data[back*2*n+n+i].co
                p.z=cz+.00045*math.sin(a);p.y=cy-.014+back*.001
        lid['control']='Blink shape key 0..1; native morph support UNKNOWN'
        # Polar topology around -Y makes pupil and iris actual independent geometry.
        verts=[(cx,cy-.005,cz)];faces=[];face_mats=[];count=40
        rings=[.12,.24,.40,.58,.72,1.0,1.3,1.6,1.9,2.2,2.5,2.8,3.02]
        ec=Vector((cx,cy+.009,cz))
        for a in rings:
            for j in range(count):
                t=2*math.pi*j/count
                verts.append((cx+.020*math.sin(a)*math.cos(t),ec.y-.014*math.cos(a),cz+.017*math.sin(a)*math.sin(t)))
        for j in range(count):faces.append((0,1+j,1+(j+1)%count));face_mats.append(3)
        for k in range(len(rings)-1):
            a=(rings[k]+rings[k+1])*.5
            for j in range(count):
                v=1+k*count+j;w=1+k*count+(j+1)%count
                faces.append((v,w,w+count,v+count))
                face_mats.append(3 if a<.24 else (1+(j%3!=0) if a<.72 else 0))
        last=len(verts);verts.append((cx,ec.y+.014,cz))
        for j in range(count):faces.append((last,1+(len(rings)-1)*count+(j+1)%count,1+(len(rings)-1)*count+j));face_mats.append(0)
        eye=mesh_object('DM_Eye.'+side,verts,faces,eye_mats[0])
        for m in eye_mats[1:]:eye.data.materials.append(m)
        for p,mi in zip(eye.data.polygons,face_mats):p.material_index=mi
        eye['center']=list(ec)
        landmarks.append({'side':side,'center':list(ec),'original_surface_y':cy,'aperture_rx':rx,'aperture_rz':rz})
        parts.extend([eye,lid])
    return parts,landmarks


def make_rig(objects, jaw, tongue_obj):
    data=bpy.data.armatures.new('DM_AnatomyTestRig')
    rig=bpy.data.objects.new('DM_AnatomyTestRig',data);bpy.context.scene.collection.objects.link(rig)
    bpy.context.view_layer.objects.active=rig;rig.select_set(True)
    bpy.ops.object.mode_set(mode='EDIT')
    def bone(name,head,tail,parent=None):
        b=data.edit_bones.new(name);b.head=head;b.tail=tail
        if parent:b.parent=data.edit_bones[parent]
        return b
    bone('DM_Head',world_point((0,-.64,1.16)),world_point((0,-.83,1.16)))
    bone('DM_Jaw',HINGE,world_point((0,-.88,.982)),'DM_Head')
    bone('DM_TongueRoot',world_point((0,-.718,.963)),world_point((0,-.786,.963)),'DM_Head')
    bone('DM_TongueMiddle',world_point((0,-.786,.963)),world_point((0,-.854,.963)),'DM_TongueRoot')
    bone('DM_TongueTip',world_point((0,-.854,.963)),world_point((0,-.918,.963)),'DM_TongueMiddle')
    for o in objects:
        if o.name.startswith('DM_Eye.'):
            center=Vector(o['center']);bone(o.name,center,center+Vector((0,-.03,0)),'DM_Head')
    bpy.ops.object.mode_set(mode='OBJECT');rig.show_in_front=True
    for o in objects:
        if o==tongue_obj:
            groups={n:o.vertex_groups.new(name=n) for n in ('DM_TongueRoot','DM_TongueMiddle','DM_TongueTip')}
            for v in o.data.vertices:
                t=max(0,min(1,(-mouth_point(v.co).y-.752)/.136))
                if t<.5:w=[1-2*t,2*t,0]
                else:w=[0,2-2*t,2*t-1]
                for n,x in zip(groups,w):
                    if x>1e-8:groups[n].add([v.index],x,'REPLACE')
        elif o==jaw:
            o.vertex_groups.new(name='DM_Jaw').add(list(range(len(o.data.vertices))),1,'REPLACE')
        elif o.name=='DM_CoatAndUpperHead':
            h=o.vertex_groups.new(name='DM_Head');j=o.vertex_groups.new(name='DM_Jaw')
            coat={vi for p in o.data.polygons if p.material_index==0 for vi in p.vertices}
            oral={vi for p in o.data.polygons if p.material_index in (1,2) for vi in p.vertices}
            for v in o.data.vertices:
                if v.index in coat:w=neck_weight(v.co)
                elif v.index in oral:w=0
                else:w=0
                if w<1:h.add([v.index],1-w,'REPLACE')
                if w>0:j.add([v.index],w,'REPLACE')
        else:
            name='DM_Jaw' if o.name=='DM_Gums_Lower' or o.name.startswith('DM_Tooth_L_') else 'DM_Head'
            if o.name.startswith('DM_Eye.'):name=o.name
            o.vertex_groups.new(name=name).add(list(range(len(o.data.vertices))),1,'REPLACE')
        mod=o.modifiers.new('Anatomy test skin','ARMATURE');mod.object=rig
        o.parent=rig
    rig['scope']='Source-only jaw/tongue geometry acceptance; not full-body or native rig'
    return rig


def set_pose(rig,angle=0,tongue_mode='rest'):
    for p in rig.pose.bones:
        p.rotation_mode='XYZ';p.rotation_euler=(0,0,0);p.location=(0,0,0);p.scale=(1,1,1)
    # World +X rotation lowers the forward (-Y) mandible.
    b=rig.pose.bones['DM_Jaw'];q=b.bone.matrix_local.to_quaternion()
    from mathutils import Quaternion
    b.rotation_mode='QUATERNION'
    b.rotation_quaternion=q.inverted() @ Quaternion((math.cos(YAW),math.sin(YAW),0),math.radians(angle)) @ q
    # The tongue root stays at the throat; its chain progressively follows the
    # lower floor instead of swinging the whole root through the posterior wall.
    for name,fraction in [('DM_TongueRoot',.20),('DM_TongueMiddle',.45),('DM_TongueTip',.35)]:
        rig.pose.bones[name].rotation_euler.x=-math.radians(angle*fraction)
    tuck=math.sin(math.pi*angle/30) if 0<angle<30 else 0
    rig.pose.bones['DM_TongueMiddle'].location.y=-.010*tuck
    rig.pose.bones['DM_TongueTip'].location.y=-.015*tuck
    if tongue_mode=='extend':
        rig.pose.bones['DM_TongueRoot'].location.y=.025
        rig.pose.bones['DM_TongueRoot'].location.z=.027
        rig.pose.bones['DM_TongueMiddle'].location.y=.018
        rig.pose.bones['DM_TongueTip'].rotation_euler.x+=math.radians(14)
    elif tongue_mode=='curl':
        rig.pose.bones['DM_TongueMiddle'].rotation_euler.x+=math.radians(20)
        rig.pose.bones['DM_TongueTip'].rotation_euler.x+=math.radians(38)
    elif tongue_mode=='retract':
        rig.pose.bones['DM_TongueRoot'].location.y=-.006
        rig.pose.bones['DM_TongueMiddle'].rotation_euler.x+=math.radians(10)
    bpy.context.view_layer.update()


def make_actions(rig):
    cases=[(f'Jaw_{a:02d}',a,'rest') for a in (0,5,15,30,45)]
    cases += [('Tongue_Extend',30,'extend'),('Tongue_Curl',30,'curl'),('Tongue_Retract',15,'retract')]
    for name,a,t in cases:
        rig.animation_data_create();rig.animation_data.action=bpy.data.actions.new(name)
        set_pose(rig,a,t)
        for p in rig.pose.bones:
            p.keyframe_insert('location',frame=1)
            p.keyframe_insert('rotation_quaternion' if p.rotation_mode=='QUATERNION' else 'rotation_euler',frame=1)
        rig.animation_data.action.use_fake_user=True
    rig.animation_data.action=None
    set_pose(rig)


def setup_render():
    scene=bpy.context.scene
    scene.render.engine='CYCLES';scene.cycles.samples=24;scene.cycles.use_denoising=True
    scene.render.resolution_x=1000;scene.render.resolution_y=1000;scene.render.resolution_percentage=100
    scene.render.image_settings.file_format='PNG'
    scene.world=bpy.data.worlds.new('AnatomyReviewWorld');scene.world.use_nodes=True
    scene.world.node_tree.nodes['Background'].inputs['Color'].default_value=(.10,.11,.13,1)
    scene.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.4
    scene.view_settings.view_transform='AgX'
    target=Vector((0,-.8,1.0))
    for name,pos,power,size in [('Key',(1,-2,3),250,2),('Fill',(-1,-2,1.3),150,1.8),('Rim',(0,1,2),200,2)]:
        d=bpy.data.lights.new(name,'AREA');d.energy=power;d.size=size
        o=bpy.data.objects.new(name,d);scene.collection.objects.link(o);o.location=pos
        o.rotation_euler=(target-o.location).to_track_quat('-Z','Y').to_euler()
    d=bpy.data.cameras.new('AnatomyReviewCamera');d.type='ORTHO'
    o=bpy.data.objects.new(d.name,d);scene.collection.objects.link(o);scene.camera=o
    return o


def render(camera,name,location,target,scale):
    camera.location=location;camera.data.ortho_scale=scale
    camera.rotation_euler=(Vector(target)-camera.location).to_track_quat('-Z','Y').to_euler()
    bpy.context.scene.render.filepath=str(ROOT/'previews'/(name+'.png'))
    bpy.ops.render.render(write_still=True)


def select_model(objects,rig=None):
    bpy.ops.object.select_all(action='DESELECT')
    for o in objects:o.select_set(True)
    if rig:rig.select_set(True)
    bpy.context.view_layer.objects.active=rig or objects[0]


def export_fbx(path,objects,rig=None):
    # FBX does not translate glTF's packed metal/rough channel graph. Feed the
    # provider's original separate scalar maps directly, then restore GLB graph.
    coat=bpy.data.objects['DM_CoatAndUpperHead'].data.materials[0]
    fbxmat=coat.copy();fbxmat.name='DM_Coat_FBX_PBR'
    shader=next(n for n in fbxmat.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
    images=[]
    for socket,filename in [('Roughness','roughness.png'),('Metallic','metallic.png')]:
        im=bpy.data.images.load(str(REPO/'art/english_mastiff/source/meshy_textured_textures'/filename))
        im.colorspace_settings.name='Non-Color';im.pack();images.append(im)
        node=fbxmat.node_tree.nodes.new('ShaderNodeTexImage');node.image=im
        fbxmat.node_tree.links.new(node.outputs['Color'],shader.inputs[socket])
    parts=[bpy.data.objects['DM_CoatAndUpperHead'],bpy.data.objects['DM_Mandible']]
    for o in parts:o.data.materials[0]=fbxmat
    try:
        select_model(objects,rig)
        bpy.ops.export_scene.fbx(filepath=str(path),use_selection=True,object_types={'MESH','ARMATURE'} if rig else {'MESH'},
                                 add_leaf_bones=False,bake_anim=False,path_mode='COPY',embed_textures=True)
    finally:
        for o in parts:o.data.materials[0]=coat
        bpy.data.materials.remove(fbxmat)
        for im in images:
            if im.users==0:bpy.data.images.remove(im)


def render_section(camera,objects):
    deps=bpy.context.evaluated_depsgraph_get();copies=[]
    for obj in objects:
        ev=obj.evaluated_get(deps);mesh=bpy.data.meshes.new_from_object(ev,depsgraph=deps)
        copy=bpy.data.objects.new('SECTION_'+obj.name,mesh);bpy.context.scene.collection.objects.link(copy)
        copy.matrix_world=obj.matrix_world.copy();copies.append(copy);obj.hide_render=True
        bm=bmesh.new();bm.from_mesh(mesh)
        bmesh.ops.bisect_plane(bm,geom=list(bm.verts)+list(bm.edges)+list(bm.faces),
                              plane_co=WORLD_ORIGIN,plane_no=(math.cos(YAW),math.sin(YAW),0),
                              dist=1e-7,clear_outer=True)
        bm.to_mesh(mesh);bm.free()
    render(camera,'mouth_section',world_point((2,-.8,1.10)),world_point((0,-.81,1.0)),.51)
    for obj in objects:obj.hide_render=False
    for obj in copies:
        mesh=obj.data;bpy.data.objects.remove(obj,do_unlink=True);bpy.data.meshes.remove(mesh)


def main():
    global SOURCE_SURFACE
    parser=argparse.ArgumentParser();parser.add_argument('--render',action='store_true');args=parser.parse_args()
    for name in ('source','interchange','metadata','validation','previews'):(ROOT/name).mkdir(parents=True,exist_ok=True)
    if hashlib.sha256(BASE.read_bytes()).hexdigest()!=BASE_SHA:raise ValueError('Frozen base changed')
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=str(BASE))
    body=next(o for o in bpy.context.scene.objects if o.type=='MESH');body.name='DM_CoatAndUpperHead'
    bpy.context.view_layer.objects.active=body;body.select_set(True)
    bpy.ops.object.transform_apply(location=True,rotation=True,scale=True)
    for v in body.data.vertices:v.co.z+=LIFT
    coat_reference=body.data.copy()
    for v in body.data.vertices:v.co=mouth_point(v.co)
    body.data.update();body.data.calc_loop_triangles()
    SOURCE_SURFACE=BVHTree.FromPolygons([v.co.copy() for v in body.data.vertices],
        [tuple(t.vertices) for t in body.data.loop_triangles],all_triangles=True)
    lining=material('DM_OralLining',(.18,.046,.052),.43)
    gum=material('DM_Gingiva',(.27,.07,.078),.36)
    enamel=material('DM_Enamel',(.78,.72,.58),.28)
    lingual=material('DM_TongueSurface',(.45,.13,.16),.43)
    palate_mat=material('DM_HardPalate',(.20,.055,.065),.48)
    lip=material('DM_LipRim',(.018,.015,.016),.48)
    jaw,surgery,before=cut_mandible(body,lining,lip)
    upper_gum=gums(True,gum);lower_gum=gums(False,gum)
    teeth,inventory=dentition(enamel)
    ling=tongue(lingual);ridges=palate(palate_mat)
    objects=[body,jaw,upper_gum,lower_gum,*teeth,ling,*ridges]
    for o in [upper_gum,lower_gum,*teeth,ling,*ridges]:
        for v in o.data.vertices:
            v.co.x*=.90
            v.co.y=-.8+(v.co.y+.8)*.88+.010
    for o in objects:
        for v in o.data.vertices:v.co=world_point(v.co)
        o.data.update()
    eye_parts,eye_landmarks=build_eyes(body,lip)
    objects.extend(eye_parts)
    preserve_coat_normals([body,jaw],coat_reference)
    for o in objects:
        o['asset_revision']='em-v004';o['source_only']=True
    for im in bpy.data.images:
        if im.type=='IMAGE' and im.has_data:im.pack()
    # A rig-free source/interchange checkpoint is kept separately from test skin.
    select_model(objects)
    bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'source/english_mastiff_anatomy.blend'))
    bpy.ops.export_scene.gltf(filepath=str(ROOT/'interchange/english_mastiff_anatomy.glb'),export_format='GLB',use_selection=True,export_animations=False)
    export_fbx(ROOT/'interchange/english_mastiff_anatomy.fbx',objects)
    rig=make_rig(objects,jaw,ling);make_actions(rig)
    select_model(objects,rig)
    bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'source/english_mastiff_anatomy_tests.blend'))
    bpy.ops.export_scene.gltf(filepath=str(ROOT/'interchange/english_mastiff_anatomy_tests.glb'),export_format='GLB',use_selection=True,export_animations=False)
    export_fbx(ROOT/'interchange/english_mastiff_anatomy_tests.fbx',objects,rig)
    write_json(ROOT/'metadata/dentition.json',{'asset_revision':'em-v004','target':'adult canine reference formula; not a clinical simulation','teeth':inventory})
    write_json(ROOT/'metadata/construction.json',{'asset_revision':'em-v004','project_version':(REPO/'VERSION').read_text(encoding='utf-8').strip(),
        'base':BASE.relative_to(REPO).as_posix(),'base_sha256':BASE_SHA,'environment':bpy.app.version_string,
        'ground_translation_z':LIFT,'physical_scale':'NOT CALIBRATED','surgery':surgery,
        'mouth_frame':{'yaw_degrees':math.degrees(YAW),'local_origin':list(FRAME_ORIGIN),'world_origin':list(WORLD_ORIGIN),'reason':'Measured fit to existing asymmetric source head; exterior transformed back to original coordinates'},
        'preserved_body_vertex_reference':before,'meshy_credits_consumed':0,
        'scope':'Original local Blender mouth reconstruction; source-only temporary jaw/tongue test rig',
        'eyes':eye_landmarks,
        'native_compatibility':'NOT TESTED','production_animations':'NOT CREATED'})
    if args.render:
        camera=setup_render()
        render(camera,'neutral_whole',(2.8,-4.3,2.0),(0,0,.68),2.2)
        render(camera,'neutral_head',(.9,-2,1.2),(0,-.77,1.08),.54)
        render(camera,'neutral_front',(0,-2,1.04),(.04,-.8,1.04),.58)
        for o in eye_parts:
            if o.name.startswith('DM_Eyelid.'):o.data.shape_keys.key_blocks['Blink'].value=1
        render(camera,'eyes_blink',(.9,-2,1.2),(.04,-.77,1.12),.43)
        for o in eye_parts:
            if o.name.startswith('DM_Eyelid.'):o.data.shape_keys.key_blocks['Blink'].value=0
        for name in ('DM_Eye.L','DM_Eye.R'):rig.pose.bones[name].rotation_euler.z=math.radians(8)
        bpy.context.view_layer.update()
        render(camera,'eyes_gaze',(.9,-2,1.2),(.04,-.77,1.12),.43)
        set_pose(rig)
        for a in (5,15,30,45):
            set_pose(rig,a)
            render(camera,f'jaw_{a:02d}',(.85,-2,1.12),(0,-.79,1.02),.57)
        set_pose(rig,30,'extend')
        render(camera,'tongue_extend',(.7,-2,1.05),(0,-.80,.99),.5)
        set_pose(rig,30,'curl')
        render(camera,'tongue_curl',(.7,-2,1.05),(0,-.80,.99),.5)
        set_pose(rig,15,'retract')
        render(camera,'tongue_retract',(.7,-2,1.05),(0,-.80,1.01),.5)
        set_pose(rig,30)
        # X-ray dental/lining view hides only coat/jaw exteriors, not new anatomy.
        body.hide_render=True;jaw.hide_render=True
        render(camera,'oral_components',(.65,-1.7,1.18),(0,-.82,.985),.40)
        body.hide_render=False;jaw.hide_render=False
        render_section(camera,objects)
        set_pose(rig)
    print(json.dumps({'asset_revision':'em-v004','meshes':len(objects),'teeth':len(teeth),'cut_faces':surgery['cut_faces'],'source':str(ROOT/'source/english_mastiff_anatomy_tests.blend')}))


if __name__=='__main__':main()
