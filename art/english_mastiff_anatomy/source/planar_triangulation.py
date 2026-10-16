"""Pure-Python planar polygon triangulation preserving every boundary vertex.

Tested on the actual em-v004 dense mouth XY and rear wall XZ boundaries.
Does not remove, round, reorder, weld, or introduce any vertices. Exact
coincident boundary vertices are an explicit error: keeping a zero-length
boundary edge is incompatible with a nondegenerate triangle mesh.
"""
import math
from collections import Counter


def signed_area(points):
    return .5 * sum(a[0]*b[1]-a[1]*b[0]
                    for a,b in zip(points,points[1:]+points[:1]))


def cross2(a,b,p):
    return (b[0]-a[0])*(p[1]-a[1])-(b[1]-a[1])*(p[0]-a[0])


def triangulate_simple_polygon(points, cross_epsilon=1e-15):
    """Return triples of original indices for a simple ordered 2D boundary.

    Suitable for the measured source-unit scale. Caller supplies XY or XZ;
    three-dimensional planarity/projection validity is the caller's contract.
    Input winding is retained. Concave polygons and retained collinear edge
    vertices work; holes and self-intersecting boundaries are unsupported.
    """
    ps=[(float(p[0]),float(p[1])) for p in points]
    if len(ps)<3 or any(not math.isfinite(x) for p in ps for x in p):
        raise ValueError('Invalid polygon coordinates')
    if any(a==b for a,b in zip(ps,ps[1:]+ps[:1])):
        raise ValueError('Exact coincident boundary vertices require explicit source-boundary repair')
    poly_area=signed_area(ps)
    if abs(poly_area)<=cross_epsilon:
        raise ValueError('Polygon has zero projected area')
    sign=1 if poly_area>0 else -1
    ids=list(range(len(ps)));triangles=[]
    while len(ids)>3:
        ears=[]
        for i,b in enumerate(ids):
            a=ids[i-1];c=ids[(i+1)%len(ids)]
            cr=cross2(ps[a],ps[b],ps[c])*sign
            if cr<=cross_epsilon:
                continue
            # Inclusive blocking preserves every retained collinear edge node:
            # a diagonal cannot skip a node that lies along the proposed ear.
            if any(min(cross2(ps[a],ps[b],ps[k])*sign,
                       cross2(ps[b],ps[c],ps[k])*sign,
                       cross2(ps[c],ps[a],ps[k])*sign)>=-cross_epsilon
                   for k in ids if k not in (a,b,c)):
                continue
            perimeter_sq=sum(math.dist(ps[u],ps[v])**2
                             for u,v in ((a,b),(b,c),(c,a)))
            ears.append((cr/max(perimeter_sq,1e-30),i,(a,b,c)))
        if not ears:
            raise ValueError('No valid ear; check boundary crossings/coincident vertices')
        _,i,t=max(ears)
        triangles.append(t);ids.pop(i)
    triangles.append(tuple(ids))
    if any(cross2(ps[a],ps[b],ps[c])*sign<=cross_epsilon
           for a,b,c in triangles):
        raise ValueError('Degenerate or inverted triangulation')
    counts=Counter(tuple(sorted((a,b))) for tri in triangles
                   for a,b in zip(tri,tri[1:]+tri[:1]))
    boundary={tuple(sorted((i,(i+1)%len(ps)))) for i in range(len(ps))}
    if any(counts.get(e)!=1 for e in boundary) or any(
            count!=(1 if e in boundary else 2) for e,count in counts.items()):
        raise ValueError('Triangulation boundary/incidence mismatch')
    tri_area=sum(abs(cross2(ps[a],ps[b],ps[c]))*.5 for a,b,c in triangles)
    if abs(tri_area-abs(poly_area))>max(1e-12,abs(poly_area)*1e-10):
        raise ValueError('Triangulation area mismatch')
    return triangles
