"""Portable, deterministic tail-region authoring from mesh positions and edges.

Development-time Python/NumPy only. Does not alter mesh data and uses no game
assets. Call generate_tail_field(co, edges) directly from Blender, or provide an
NPZ containing positions Nx3 and edges Mx2. The reviewed landmarks intentionally
refer to this supplied Shepherd stance; this is not a generic animal classifier.
"""
from pathlib import Path
import argparse,hashlib,heapq,json
import numpy as np

def generate_tail_field(source_positions,source_edges,*,cut_z=0.,blend_top=.16,
                        fade_start=.27,reach=.35,body_reach=1.):
    if not cut_z<blend_top or not 0<=fade_start<reach:raise ValueError('Invalid field bounds')
    source=np.asarray(source_positions,dtype=np.float32)
    source_edges=np.asarray(source_edges,dtype=np.int64)
    if source.ndim!=2 or source.shape[1]!=3 or source_edges.ndim!=2 or source_edges.shape[1]!=2:
        raise ValueError('Expected positions Nx3 and edges Mx2')
    if not np.isfinite(source).all() or source_edges.min()<0 or source_edges.max()>=len(source):
        raise ValueError('Invalid positions or edge indices')
    # Exact-position analysis weld only; the supplied source arrays stay intact.
    unique,weld=np.unique(source,axis=0,return_inverse=True);co=unique.astype(np.float64)
    edges=weld[source_edges];edges.sort(axis=1);edges=np.unique(edges,axis=0)
    edges=edges[edges[:,0]!=edges[:,1]]
    below=co[:,2]<cut_z;parent=np.arange(len(co));size=np.ones(len(co),np.int32)
    def find(i):
        while parent[i]!=i:parent[i]=parent[parent[i]];i=parent[i]
        return i
    for a,b in edges[below[edges].all(axis=1)]:
        a=find(a);b=find(b)
        if a==b:continue
        if size[a]<size[b]:a,b=b,a
        parent[b]=a;size[a]+=size[b]
    labels=np.full(len(co),-1,np.int64)
    for i in np.flatnonzero(below):labels[i]=find(i)
    seeds=below&(co[:,0]>.85)&(co[:,1]>.4)&(co[:,2]<-.5)
    seed_labels=np.unique(labels[seeds])
    if len(seed_labels)!=1:raise ValueError('Expected one connected distal-tail seed component')
    tail=labels==seed_labels[0]
    if co[tail,2].min()<-.74 or co[tail,0].min()<.50 or co[tail,1].min()<.25:
        raise ValueError('Tail component reaches reviewed body/paw exclusion region')
    inside=(co[:,2]>=cut_z)&(co[:,2]<blend_top)
    patch_edges=edges[inside[edges].any(axis=1)];active=np.unique(patch_edges)
    local=np.full(len(co),-1,np.int64);local[active]=np.arange(len(active));patch_edges=local[patch_edges]
    positions=co[active];interior=inside[active]
    tail_boundary=tail[active]&~interior;body_boundary=~interior&~tail_boundary
    arcs=np.concatenate([patch_edges,patch_edges[:,::-1]])
    arcs=arcs[np.lexsort((arcs[:,1],arcs[:,0]))]
    costs=np.linalg.norm(positions[arcs[:,0]]-positions[arcs[:,1]],axis=1)
    ptr=np.r_[0,np.cumsum(np.bincount(arcs[:,0],minlength=len(active)))];neighbors=arcs[:,1]
    def distances(seed,limit):
        distance=np.full(len(active),np.inf);initial=np.flatnonzero(seed);distance[initial]=0
        pending=[(0.,int(i)) for i in initial];heapq.heapify(pending)
        while pending:
            value,i=heapq.heappop(pending)
            if value!=distance[i] or value>limit:continue
            for k in range(ptr[i],ptr[i+1]):
                j=neighbors[k]
                if not interior[j]:continue
                candidate=value+costs[k]
                if candidate<distance[j] and candidate<=limit:
                    distance[j]=candidate;heapq.heappush(pending,(candidate,int(j)))
        return distance
    dt=distances(tail_boundary,reach);db=distances(body_boundary,body_reach)
    eligible=interior&np.isfinite(dt)&np.isfinite(db)
    phase=np.clip((dt[eligible]-fade_start)/(reach-fade_start),0,1)
    fade=1-phase*phase*(3-2*phase)
    field=tail.astype(np.float32)
    field[active[eligible]]=db[eligible]/(dt[eligible]+db[eligible])*fade
    result=field[weld];source_tail=tail[weld]
    assert np.all(result[source_tail]==1)
    assert np.all(result[(source[:,2]<cut_z)&~source_tail]==0)
    report={'method':'Exact-position welded mesh edge graph, cut-plane component, two-source surface geodesic root blend, smooth finite-reach decay',
        'source_vertices':len(source),'welded_vertices':len(co),'tail_vertices':int(source_tail.sum()),
        'mixed_root_vertices':int(((result>0)&(result<1)).sum()),
        'parameters':{'cut_z':cut_z,'blend_top':blend_top,'fade_start':fade_start,'reach':reach,'body_reach':body_reach},
        'positions_sha256':hashlib.sha256(source.astype('<f4',copy=False).tobytes()).hexdigest(),
        'welded_edges_sha256':hashlib.sha256(edges.astype('<i8',copy=False).tobytes()).hexdigest(),
        'field_sha256':hashlib.sha256(result.astype('<f4',copy=False).tobytes()).hexdigest()}
    return result,source_tail,report

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input',type=Path);parser.add_argument('output',type=Path)
    args=parser.parse_args();bundle=np.load(args.input,allow_pickle=False)
    field,tail,report=generate_tail_field(bundle['positions'],bundle['edges'])
    np.savez_compressed(args.output,positions=bundle['positions'],tail_mask=field,tail_mask_z0=tail)
    args.output.with_suffix('.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report))

if __name__=='__main__':main()
