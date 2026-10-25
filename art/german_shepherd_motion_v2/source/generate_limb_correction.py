"""Continuous lower-limb correction fields; pure positions/edges input.

Apply as a convex blend toward each limb's normalized bone distribution, retaining
the existing distribution with residual 1-sum(fields). This corrects separated
lower-limb fur while leaving the reviewed upper-attachment distribution intact.
"""
from pathlib import Path
import json,heapq,hashlib
import numpy as np

def find_limb_components(co,edges,cut_z=-.25):
    """Reviewed four paw seeds in the supplied source stance; fail if merged."""
    co=np.asarray(co);edges=np.asarray(edges,dtype=np.int64)
    below=co[:,2]<cut_z;parent=np.arange(len(co));size=np.ones(len(co),np.int32)
    def find(i):
        while parent[i]!=i:parent[i]=parent[parent[i]];i=parent[i]
        return i
    for a,b in edges[below[edges].all(axis=1)]:
        a=find(a);b=find(b)
        if a==b:continue
        if size[a]<size[b]:a,b=b,a
        parent[b]=a;size[a]+=size[b]
    roots=np.full(len(co),-1,np.int64)
    for i in np.flatnonzero(below):roots[i]=find(i)
    centers=np.array([[-.686,.226],[-.494,-.178],[.309,.514],[.590,.077]])
    paw=np.flatnonzero(co[:,2]<-.76)
    membership=(((co[paw,None,:2]-centers[None,:,:])**2).sum(axis=2)).argmin(axis=1)
    labels=np.full(len(co),-1,np.int8);selected_roots=[]
    for k in range(4):
        root=np.unique(roots[paw[membership==k]])
        if len(root)!=1 or root[0]<0 or int(root[0]) in selected_roots:
            raise ValueError('Four distinct connected paw components required; check source topology/cut')
        selected_roots.append(int(root[0]));labels[roots==root[0]]=k
    return labels

def generate_limb_correction(co,edges,labels=None,cut_z=-.25,blend_top=-.10,reach=.30,fade_start=.22):
    co=np.asarray(co,dtype=np.float64);edges=np.asarray(edges,dtype=np.int64)
    if labels is None:labels=find_limb_components(co,edges,cut_z)
    inside=(co[:,2]>=cut_z)&(co[:,2]<blend_top)
    patch=edges[inside[edges].any(axis=1)];active=np.unique(patch)
    local=np.full(len(co),-1,np.int64);local[active]=np.arange(len(active));patch=local[patch]
    points=co[active];interior=inside[active]
    arcs=np.concatenate([patch,patch[:,::-1]]);arcs=arcs[np.lexsort((arcs[:,1],arcs[:,0]))]
    cost=np.linalg.norm(points[arcs[:,0]]-points[arcs[:,1]],axis=1)
    ptr=np.r_[0,np.cumsum(np.bincount(arcs[:,0],minlength=len(active)))];adj=arcs[:,1]
    def distances(seeds,limit):
        d=np.full(len(active),np.inf);ix=np.flatnonzero(seeds);d[ix]=0;queue=[(0.,int(i)) for i in ix];heapq.heapify(queue)
        while queue:
            value,i=heapq.heappop(queue)
            if value!=d[i] or value>limit:continue
            for k in range(ptr[i],ptr[i+1]):
                j=adj[k]
                if not interior[j]:continue
                candidate=value+cost[k]
                if candidate<d[j] and candidate<=limit:d[j]=candidate;heapq.heappush(queue,(candidate,int(j)))
        return d
    fields=np.zeros((len(co),4),np.float32)
    for side in range(4):
        target=(labels[active]==side)&~interior
        other=~interior&~target
        dt=distances(target,reach);db=distances(other,1.)
        good=interior&np.isfinite(dt)&np.isfinite(db)
        fade=np.clip((dt[good]-fade_start)/(reach-fade_start),0,1);fade=1-fade*fade*(3-2*fade)
        fields[labels==side,side]=1
        fields[active[good],side]=db[good]/(dt[good]+db[good])*fade
    sums=fields.sum(axis=1);fields/=np.maximum(1,sums[:,None])
    report={'method':'Four separated paw components below cut, surface geodesic correction fading above cut, convex partition; preserves baseline upper attachments',
        'cut_z':cut_z,'blend_top':blend_top,'reach':reach,'fade_start':fade_start,
        'pure_lower_vertices':[int((labels==i).sum()) for i in range(4)],
        'mixed_vertices':int(((fields.sum(axis=1)>0)&(labels<0)).sum()),
        'max_sum':float(fields.sum(axis=1).max()),'min_weight':float(fields.min()),
        'source_positions_sha256':hashlib.sha256(co.astype('<f4').tobytes()).hexdigest(),
        'field_sha256':hashlib.sha256(fields.astype('<f4',copy=False).tobytes()).hexdigest()}
    return fields,report

if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('input',type=Path);parser.add_argument('output',type=Path);args=parser.parse_args()
    graph=np.load(args.input,allow_pickle=False)
    fields,report=generate_limb_correction(graph['positions'],graph['edges'])
    np.savez_compressed(args.output,positions=graph['positions'],limb_fields=fields)
    args.output.with_suffix('.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8',newline='\n');print(json.dumps(report))
