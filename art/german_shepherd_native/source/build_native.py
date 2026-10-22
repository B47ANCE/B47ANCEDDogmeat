"""Bind unchanged supplied Shepherd meshes to the native deforming-bone contract.

Reads installed skeleton technical data; never imports native meshes or skin weights.
Native clips are read only by the separate local preview tool and are never exported.
"""
import argparse,hashlib,json,math,re,struct,sys
from pathlib import Path
import bpy
import numpy as np
from mathutils import Matrix,Vector

ROOT=Path(__file__).resolve().parents[3]
OUT=ROOT/'art/german_shepherd_native'
INPUT=ROOT/'art/german_shepherd_selected'
sys.path.insert(0,str(Path(__file__).resolve().parent))
C=Matrix(((1,0,0,0),(0,0,-1,0),(0,1,0,0),(0,0,0,1)))
H=Matrix.Diagonal((1,1,-1,1))

def array(collection,prop,width,dtype):
    data=np.empty(len(collection)*width,dtype=dtype)
    collection.foreach_get(prop,data)
    return data.reshape(-1,width)

def mesh_hash(mesh):
    digest=hashlib.sha256()
    for collection,prop,width,dtype in [(mesh.vertices,'co',3,np.float32),(mesh.loops,'vertex_index',1,np.int32),(mesh.polygons,'loop_total',1,np.int32)]:
        digest.update(array(collection,prop,width,dtype).tobytes())
    for layer in mesh.uv_layers:digest.update(array(layer.data,'uv',2,np.float32).tobytes())
    return digest.hexdigest()

def native_contract(game):
    path=game/'media/models_X/Skinned/Raccoon_Body.x';raw=path.read_bytes();text=raw.decode('utf-8-sig')
    bones=[];stack=[];depth=0
    for match in re.finditer(r'\bFrame\s+(\w+)\s*\{|\bFrameTransformMatrix\s*\{([^}]+)\}|[{}]',text):
        token=match.group()
        if token.startswith('Frame '):
            name=match[1];parent=stack[-1][0] if stack else None
            stack.append((name,depth));depth+=1
            if name!='Raccoon':bones.append({'name':name,'parent':parent if parent!='Raccoon' else None})
        elif token.startswith('FrameTransformMatrix'):
            if stack and stack[-1][0]!='Raccoon':
                values=[float(x) for x in re.findall(r'[-+]?\d*\.?\d+(?:[eE][-+]?\d+)?',match[2])]
                assert len(values)==16
                bones[-1]['frame']=Matrix(np.array(values).reshape(4,4).T.tolist())
        elif token=='{':depth+=1
        else:
            depth-=1
            while stack and stack[-1][1]==depth:stack.pop()
    offsets={}
    for match in re.finditer(r'SkinWeights\s*\{\s*"([^"]+)"\s*;(.*?)\}',text,re.S):
        # Only the final transform; native mesh indices/weights are not retained.
        values=[float(x) for x in re.findall(r'[-+]?\d*\.?\d+(?:[eE][-+]?\d+)?',match[2])][-16:]
        offsets[match[1]]=Matrix(np.array(values).reshape(4,4).T.tolist())
    frames={};bind={}
    for bone in bones:
        name,parent=bone['name'],bone['parent']
        frames[name]=frames[parent]@bone['frame'] if parent else bone['frame']
        if name in offsets:bind[name]=offsets[name].inverted()
        elif name.endswith('Nub'):bind[name]=bind[parent]@bone['frame']
        else:bind[name]=frames[name]
    assert len(bones)==34 and len(offsets)==25
    return bones,bind,offsets,hashlib.sha256(raw).hexdigest()

def playback_contract(game):
    from native_clip_reader import tracks,sample
    bones,native_bind,native_offsets,native_hash=native_contract(game)
    path=game/'media/anims_X/Raccoon/Rac_Idle01.x';data=tracks(path);bind={}
    for bone in bones:
        name,parent=bone['name'],bone['parent'];channels=data[name]
        local=Matrix.LocRotScale(sample(channels[2],0),sample(channels[0],0,True),sample(channels[1],0))
        bind[name]=bind[parent]@local if parent else local
    offsets={name:bind[name].inverted() for name in native_offsets}
    return bones,bind,offsets,native_hash,hashlib.sha256(path.read_bytes()).hexdigest()


def source_weights():
    bpy.ops.wm.open_mainfile(filepath=str(INPUT/'source/selected_shepherd_rigged.blend'))
    mesh=next(o for o in bpy.data.objects if o.type=='MESH')
    arm=next(o for o in bpy.data.objects if o.type=='ARMATURE')
    co=array(mesh.data.vertices,'co',3,np.float32);co[co==0]=0
    groups=[g.name for g in mesh.vertex_groups]
    weights=np.zeros((len(co),len(groups)),np.float32)
    for v in mesh.data.vertices:
        for g in v.groups:weights[v.index,g.group]=g.weight
    keys=co.view('V12').ravel();order=np.argsort(keys);keys=keys[order]
    duplicate=keys[1:]==keys[:-1]
    assert np.array_equal(weights[order[1:][duplicate]],weights[order[:-1][duplicate]])
    # Existing authoring left/right groups were assigned by +Y/-Y. Align them to
    # the native handedness: a dog facing -X has its left side at negative Y.
    rename=lambda n:n.replace('_L_','_TEMP_').replace('_R_','_L_').replace('_TEMP_','_R_')
    target={rename(b.name):b.head_local.copy() for b in arm.data.bones}
    from author_weights import weights as authored_weights
    names=[rename(n) for n in groups]
    return keys,authored_weights(co,names)[order],names,target,float(co[:,2].min())

def material(name):
    material=bpy.data.materials.new(name);material.use_nodes=True
    nodes=material.node_tree.nodes;links=material.node_tree.links
    shader=next(n for n in nodes if n.type=='BSDF_PRINCIPLED')
    for role,socket in [('base_color','Base Color'),('roughness','Roughness'),('metallic','Metallic'),('normal','Normal')]:
        tex=nodes.new('ShaderNodeTexImage');tex.image=bpy.data.images.load(str(INPUT/'coats'/name/(role+'.png')),check_existing=False)
        if role!='base_color':tex.image.colorspace_settings.name='Non-Color'
        output=tex.outputs['Color']
        if role=='normal':
            normal=nodes.new('ShaderNodeNormalMap');links.new(output,normal.inputs['Color']);output=normal.outputs['Normal']
        links.new(output,shader.inputs[socket]);tex.image.pack()
    return material

def restrict_skin(path,deforming):
    raw=path.read_bytes();length=struct.unpack_from('<I',raw,12)[0]
    doc=json.loads(raw[20:20+length]);binary=bytearray(raw[28+length:])
    skin=doc['skins'][0];old=skin['joints'];keep=[i for i,n in enumerate(old) if doc['nodes'][n]['name'] in deforming]
    assert len(keep)==25
    mapping=np.zeros(len(old),np.uint16)
    for index,previous in enumerate(keep):mapping[previous]=index
    processed=set()
    for mesh in doc['meshes']:
        for primitive in mesh['primitives']:
            aid=primitive['attributes']['JOINTS_0']
            if aid in processed:continue
            processed.add(aid);a=doc['accessors'][aid];v=doc['bufferViews'][a['bufferView']]
            assert 'byteStride' not in v
            dtype={5121:np.uint8,5123:np.uint16}[a['componentType']]
            values=np.frombuffer(binary,dtype=dtype,count=a['count']*4,offset=v.get('byteOffset',0)+a.get('byteOffset',0))
            values[:]=mapping[values]
            a.pop('min',None);a.pop('max',None)
    a=doc['accessors'][skin['inverseBindMatrices']];v=doc['bufferViews'][a['bufferView']]
    matrices=np.frombuffer(binary,dtype='<f4',count=a['count']*16,offset=v.get('byteOffset',0)+a.get('byteOffset',0)).reshape(-1,16)[keep].copy()
    # Detach from temporary numpy views before extending the packed buffer.
    binary=bytearray(binary)
    while len(binary)%4:binary.append(0)
    offset=len(binary);binary.extend(matrices.tobytes())
    doc['bufferViews'].append({'buffer':0,'byteOffset':offset,'byteLength':matrices.nbytes})
    a['bufferView']=len(doc['bufferViews'])-1;a['byteOffset']=0;a['count']=25
    skin['joints']=[old[i] for i in keep];doc['buffers'][0]['byteLength']=len(binary)
    encoded=json.dumps(doc,separators=(',',':')).encode();encoded+=b' '*((-len(encoded))%4)
    binary+=b'\0'*((-len(binary))%4)
    total=12+8+len(encoded)+8+len(binary)
    path.write_bytes(struct.pack('<III',0x46546c67,2,total)+struct.pack('<II',len(encoded),0x4e4f534a)+encoded+struct.pack('<II',len(binary),0x004e4942)+binary)

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--game-root',type=Path,required=True)
    args=parser.parse_args(sys.argv[sys.argv.index('--')+1:])
    target=OUT/'source/shepherd_native.blend';assert not target.exists(),'Protect existing checkpoint; use a new revision'
    bones,bind,offsets,native_hash,idle_hash=playback_contract(args.game_root)
    keys,weights,groups,landmarks,ground=source_weights();assert set(groups)==set(offsets)
    Q=Matrix.Rotation(-math.pi/2,4,'Z')@C@H
    _,alignment_bind,_,_=native_contract(args.game_root)
    n=np.array([list((Q@alignment_bind[g]).translation) for g in groups]);t=np.array([list(landmarks[g]) for g in groups])
    nc=n-n.mean(axis=0);tc=t-t.mean(axis=0)
    scale=float(np.sum(nc*tc)/np.sum(nc*nc));shift=t.mean(axis=0)-scale*n.mean(axis=0);shift[2]=ground
    P=Matrix.Translation(Vector(shift.tolist()))@Matrix.Scale(scale,4)@Q
    placement=C@H@P.inverted();assert placement.determinant()>0
    bpy.ops.wm.read_factory_settings(use_empty=True)
    data=bpy.data.armatures.new('B47Dogmeat_NativeRaccoonRig');rig=bpy.data.objects.new(data.name,data);bpy.context.collection.objects.link(rig)
    bpy.context.view_layer.objects.active=rig;rig.select_set(True);bpy.ops.object.mode_set(mode='EDIT')
    for bone in bones:
        name,parent=bone['name'],bone['parent'];eb=data.edit_bones.new(name);eb.length=.007;eb.matrix=C@H@bind[name]@H
        children=[b['name'] for b in bones if b['parent']==name]
        eb.length=max(((C@H@bind[children[0]]@H).translation-eb.head).length,.007) if children else .007
        if parent:eb.parent=data.edit_bones[parent]
        eb.use_connect=False;eb.use_deform=name in offsets
    bpy.ops.object.mode_set(mode='OBJECT')
    report={'asset_revision':'gsd-native-rig-v001','project_version':(ROOT/'VERSION').read_text().strip(),
            'environment':'Blender '+bpy.app.version_string+' offline','native_source_sha256':native_hash,'idle_bind_source_sha256':idle_hash,'bind_reference':'Rac_Idle01 frame zero',
            'bones':34,'deforming_bones':25,'helper_bones':'Nine zero-weight hierarchy helpers; no native anatomical bind claim',
            'alignment_scale':scale,'native_to_authoring':[list(row) for row in P],
            'mesh_object_transform':[list(row) for row in placement],'variants':{},'runtime':'NOT TESTED'}
    objects=[]
    specs=[('original','Original'),('variation_1','Coat1'),('variation_2','Coat2')]
    for name,suffix in specs:
        if name=='original':bpy.ops.import_scene.gltf(filepath=str(INPUT/'original/selected_shepherd.glb'))
        else:bpy.ops.import_scene.fbx(filepath=str(INPUT/'coats'/name/'supplied.fbx'))
        obj=next(o for o in bpy.data.objects if o.type=='MESH' and o not in objects)
        obj.name='B47Dogmeat_GSD_'+suffix;before=mesh_hash(obj.data)
        co=array(obj.data.vertices,'co',3,np.float32);co[co==0]=0;k=co.view('V12').ravel();indices=np.searchsorted(keys,k)
        assert np.all(indices<len(keys)) and np.array_equal(keys[indices],k),'Require exact position matches'
        mapped=weights[indices]
        for i,group in enumerate(groups):
            vg=obj.vertex_groups.new(name=group)
            for value in np.unique(mapped[:,i]):
                if value>0:vg.add(np.flatnonzero(mapped[:,i]==value).tolist(),float(value),'REPLACE')
        obj.parent=rig;obj.matrix_world=placement
        modifier=obj.modifiers.new('NativeRaccoonSkin','ARMATURE');modifier.object=rig
        if name!='original':obj.data.materials.clear();obj.data.materials.append(material(name))
        for image in bpy.data.images:
            if image.has_data and not image.packed_file:image.pack()
        assert mesh_hash(obj.data)==before
        objects.append(obj)
        report['variants'][name]={'vertices':len(obj.data.vertices),'triangles':len(obj.data.polygons),
             'geometry_uv_before':before,'geometry_uv_after':mesh_hash(obj.data),'exact_position_matches':len(co),
             'max_influences':int((mapped>0).sum(axis=1).max()),'unweighted_vertices':int(np.count_nonzero(mapped.sum(axis=1)==0)),
             'max_weight_sum_error':float(abs(mapped.sum(axis=1)-1).max()),'model':obj.name}
    scene=bpy.context.scene;scene.world=bpy.data.worlds.new('ReviewWorld');scene.world.use_nodes=True
    next(n for n in scene.world.node_tree.nodes if n.type=='BACKGROUND').inputs['Color'].default_value=(.14,.14,.14,1)
    center=placement@Vector((0,0,0))
    for i,(pos,energy) in enumerate([((3,-4,5),1200),((-3,-2,3),800),((2,4,3),1000)]):
        light=bpy.data.lights.new('ReviewLight'+str(i),'AREA');light.energy=energy/scale**2;light.size=5/scale
        obj=bpy.data.objects.new(light.name,light);scene.collection.objects.link(obj);obj.location=placement@Vector(pos);obj.rotation_euler=(center-obj.location).to_track_quat('-Z','Y').to_euler()
    cam=bpy.data.cameras.new('ReviewCamera');obj=bpy.data.objects.new(cam.name,cam);scene.collection.objects.link(obj);obj.location=placement@Vector((5,-8,3.2));obj.rotation_euler=(center-obj.location).to_track_quat('-Z','Y').to_euler();cam.type='ORTHO';cam.ortho_scale=2.65/scale;scene.camera=obj
    scene.render.engine='CYCLES';scene.cycles.samples=12;scene.render.resolution_x=900;scene.render.resolution_y=900;scene.render.resolution_percentage=100
    for folder in ['models','previews','validation']:(OUT/folder).mkdir(parents=True,exist_ok=True)
    for i,obj in enumerate(objects):obj.hide_render=i!=0
    bpy.ops.wm.save_as_mainfile(filepath=str(target),compress=True)
    for (name,suffix),obj in zip(specs,objects):
        for other in bpy.data.objects:other.select_set(False)
        obj.select_set(True);rig.select_set(True);bpy.context.view_layer.objects.active=rig
        path=OUT/'models'/(obj.name+'.glb');assert not path.exists()
        bpy.ops.export_scene.gltf(filepath=str(path),export_format='GLB',use_selection=True,export_animations=False,export_skins=True,export_rest_position_armature=True,export_def_bones=False,export_materials='EXPORT',export_image_format='AUTO',export_apply=False)
        restrict_skin(path,set(offsets))
        for other in objects:other.hide_render=other!=obj
        scene.render.filepath=str(OUT/'previews'/(name+'_neutral.png'));bpy.ops.render.render(write_still=True)
        report['variants'][name]['glb_sha256']=hashlib.sha256(path.read_bytes()).hexdigest()
    (OUT/'validation/build.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8',newline='\n')
    print('NATIVE_BIND_BUILD',json.dumps(report))

if __name__=='__main__':main()
