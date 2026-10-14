"""Reopen editable source and independently import GLB in a fresh bpy process.

Offline authoring checks only. This does not test Project Zomboid's importer,
native rigs, animation states, species registration, gameplay or multiplayer.
"""
from pathlib import Path
import hashlib
import json
import struct

import bpy
import bmesh
import numpy as np
from mathutils import Quaternion, Vector
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
PROJECT = ROOT.parents[1]
SOURCE_FUR = None


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def points(obj):
    bpy.context.view_layer.update()
    evaluated = obj.evaluated_get(bpy.context.evaluated_depsgraph_get())
    mesh = evaluated.to_mesh()
    result = np.array([tuple(evaluated.matrix_world @ v.co) for v in mesh.vertices])
    evaluated.to_mesh_clear()
    return result


def inventory(source):
    global SOURCE_FUR
    meshes = sorted([o for o in bpy.context.scene.objects if o.type == 'MESH' and o.name.startswith('GSD_')], key=lambda o: o.name)
    rigs = [o for o in bpy.context.scene.objects if o.type == 'ARMATURE']
    require(len(rigs) == 1, 'Exactly one original rig required')
    rig = rigs[0]
    require(len(rig.data.bones) == 29, 'Original deformation skeleton inventory changed')
    required={'GSD_CoatBody','GSD_GuardFur','GSD_LowerJaw','GSD_TongueTip',
              'GSD_Iris_L','GSD_Iris_R','GSD_EarInset_L','GSD_EarInset_R','GSD_Nose'}
    require(required.issubset({o.name for o in meshes}), 'Required anatomical objects missing')
    body = bpy.data.objects['GSD_CoatBody']
    bm = bmesh.new()
    bm.from_mesh(body.data)
    if not source:
        # glTF stores separate vertices at UV seams. Weld only this disposable
        # topology-check copy; preserve the actual imported/exported mesh.
        bmesh.ops.remove_doubles(bm, verts=list(bm.verts), dist=1e-6)
    require(all(e.is_manifold for e in bm.edges), 'Body has a nonmanifold edge')
    require(all(f.calc_area() > 1e-10 for f in bm.faces), 'Body has degenerate faces')
    seen = set()
    components = 0
    for v in bm.verts:
        if v in seen:
            continue
        components += 1
        queue = [v]
        seen.add(v)
        while queue:
            current = queue.pop()
            for edge in current.link_edges:
                nxt = edge.other_vert(current)
                if nxt not in seen:
                    seen.add(nxt)
                    queue.append(nxt)
    bm.free()
    require(components == 1, 'Coat body must be a single connected outer surface')
    unweighted = badsum = excessive = 0
    for obj in meshes:
        require(obj.parent is rig, 'Mesh is not parented to original rig: ' + obj.name)
        require(any(m.type == 'ARMATURE' and m.object is rig for m in obj.modifiers), 'Skin modifier missing')
        require(all(np.isfinite(tuple(v.co)).all() for v in obj.data.vertices), 'Nonfinite mesh')
        for v in obj.data.vertices:
            weights = [g.weight for g in v.groups if g.weight > 0]
            unweighted += len(weights) == 0
            badsum += abs(sum(weights) - 1) > 1e-5
            excessive += len(weights) > 4
        if source:
            require(obj.get('project_version') == (PROJECT / 'VERSION').read_text().strip(), 'Stale binary version property')
            require(obj.get('asset_revision') == 'gsd-v002', 'Wrong asset revision')
            require(np.allclose(obj.matrix_world, np.eye(4), atol=1e-7), 'Nonidentity source mesh transform')
    require(unweighted == badsum == excessive == 0, 'Invalid skin weights')
    require(body.data.uv_layers.active is not None, 'No UVs')
    uvs = np.array([tuple(u.uv) for u in body.data.uv_layers.active.data])
    require(np.isfinite(uvs).all() and uvs.min() >= -1e-6 and uvs.max() <= 1 + 1e-6, 'Invalid UV coordinates')
    texture = [n.image for mat in body.data.materials if mat.use_nodes
               for n in mat.node_tree.nodes if n.type == 'TEX_IMAGE' and n.image]
    require(len(texture) == 3 and all(tuple(im.size)==(2048,2048) for im in texture), 'Missing 2048 coat maps')
    mat=body.data.materials[0]
    shader=next(n for n in mat.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
    def images_upstream(socket,seen=None):
        seen=set() if seen is None else seen
        found=set()
        for link in socket.links:
            node=link.from_node
            if node in seen:continue
            seen.add(node)
            if node.type=='TEX_IMAGE' and node.image:found.add(node.image.name)
            for inp in node.inputs:found.update(images_upstream(inp,seen))
        return found
    roles={role:sorted(images_upstream(shader.inputs[socket])) for role,socket in
           [('albedo','Base Color'),('normal','Normal'),('roughness','Roughness')]}
    require(all(len(images)==1 for images in roles.values()),'Coat map is not connected to its material input')
    require(len({im for images in roles.values() for im in images})==3,'Three distinct coat roles required')
    if source:
        require(all(im.packed_file is not None for im in texture), 'Editable source needs packed coat maps')
        require(all(im.filepath.startswith('//') for im in texture), 'Texture paths must be portable')
        require(rig.get('project_version') == (PROJECT / 'VERSION').read_text().strip(), 'Stale rig version property')
        require(np.allclose(rig.matrix_world, np.eye(4), atol=1e-7), 'Nonidentity source rig transform')
    require(not bpy.data.actions, 'Unexpected authored/imported animation clips')
    allpoints = np.concatenate([points(o) for o in meshes])
    neutral = points(body)
    motions = {}
    build=json.loads((ROOT/'validation'/'asset_validation.json').read_text())
    roots=build['fur']['root_probes']
    fur=bpy.data.objects['GSD_GuardFur']
    neutral_fur=points(fur)
    if source:
        sample_ids=[a['vertex'] for a in roots[::4]]
    else:
        from mathutils.kdtree import KDTree
        kd=KDTree(len(neutral_fur))
        for i,p in enumerate(neutral_fur):kd.insert(p,i)
        kd.balance();sample_ids=[]
        for p in SOURCE_FUR['neutral']:
            _,idx,distance=kd.find(p);require(distance<2e-5,'Imported fur sample not found');sample_ids.append(idx)
    attr=fur.data.color_attributes.active_color
    require(attr is not None and attr.domain in {'POINT','CORNER'},'Fur colors missing')
    if attr.domain=='POINT':
        sample_colors=[list(attr.data[i].color) for i in sample_ids]
    else:
        # Blender's glTF importer stores triangle colors on corners. Check all
        # corners of sampled vertices agree before comparing linear RGBA.
        wanted=set(sample_ids);corner_colors={i:[] for i in sample_ids}
        for loop in fur.data.loops:
            if loop.vertex_index in wanted:corner_colors[loop.vertex_index].append(list(attr.data[loop.index].color))
        require(all(v and np.allclose(v,v[0],atol=.005) for v in corner_colors.values()),'Imported corner colors disagree')
        sample_colors=[corner_colors[i][0] for i in sample_ids]
    sample_weights=[{fur.vertex_groups[w.group].name:round(w.weight,7) for w in fur.data.vertices[i].groups if w.weight>0} for i in sample_ids]
    fur_report={'neutral':neutral_fur[sample_ids].round(7).tolist(),'colors':sample_colors,'weights':sample_weights,'poses':{}}
    if not source:
        require(np.allclose(sample_colors,SOURCE_FUR['colors'],atol=.005),'Fur colors changed in GLB')
        for a,b in zip(sample_weights,SOURCE_FUR['weights']):
            # Blender 5.2's glTF primitive_extract.py uses min_influence=.0001.
            # Compare its defined normalized result, not a relaxed arbitrary
            # tolerance. Posed positions still retain the strict 20um limit.
            kept={k:v for k,v in b.items() if v>.0001};total=sum(kept.values())
            expected={k:v/total for k,v in kept.items()}
            error=max(abs(a.get(k,0)-expected.get(k,0)) for k in a.keys()|expected.keys())
            require(error<2e-5,'Fur skin weights changed: '+str((error,a,b)))
    max_root_error=0
    for name, angle, axis in [('head', .35, (0, 0, 1)), ('front_lower_L', .50, (0, 1, 0)),
                             ('rear_lower_R', -.45, (0, 1, 0)), ('tail_2', .5, (0, 0, 1))]:
        bone = rig.pose.bones[name]
        bone.rotation_mode = 'QUATERNION'
        # Both source and import may have different object-axis conventions.
        world_basis = rig.matrix_world.to_3x3() @ bone.bone.matrix_local.to_3x3()
        bone.rotation_quaternion = Quaternion((world_basis.inverted() @ Vector(axis)).normalized(), angle)
        posed = points(body)
        delta = np.linalg.norm(posed - neutral, axis=1)
        require(np.isfinite(posed).all() and (delta > .001).sum() > 10 and .005 < delta.max() < .25,
                'Pose failed: ' + name)
        if source:
            hairpoints=points(fur)
            for anchor in roots:
                skin=np.array(anchor['barycentric'])@posed[anchor['body_vertices']]
                error=float(np.linalg.norm(hairpoints[anchor['vertex']]-skin))
                max_root_error=max(max_root_error,error)
                require(error < .003,'Fur root detached from posed skin: '+name)
        else:
            hairpoints=points(fur)
        fur_report['poses'][name]=hairpoints[sample_ids].round(7).tolist()
        if not source:
            require(np.allclose(fur_report['poses'][name],SOURCE_FUR['poses'][name],atol=2e-5),'Imported fur deformation changed: '+name)
        motions[name] = round(float(delta.max()), 6)
        bone.rotation_quaternion = (1, 0, 0, 0)
        bpy.context.view_layer.update()
    # Facial ownership checks: jaw movement must carry lower teeth/tongue,
    # while upper teeth remain attached to head. Ear interiors must move too.
    detail_motions={}
    for bone_name,obj_name,angle in [('jaw','GSD_TongueTip',.18),('jaw','GSD_LowerJaw',.18),('jaw','GSD_LowerTooth_L0',.18),
            ('ear_L','GSD_EarInset_L',.20),('ear_R','GSD_EarInset_R',-.20)]:
        obj=bpy.data.objects[obj_name];before=points(obj)
        upper=bpy.data.objects['GSD_UpperTooth_L0'];upper_before=points(upper)
        b=rig.pose.bones[bone_name];b.rotation_mode='QUATERNION'
        basis=rig.matrix_world.to_3x3()@b.bone.matrix_local.to_3x3()
        b.rotation_quaternion=Quaternion((basis.inverted()@Vector((0,1,0))).normalized(),angle)
        after=points(obj);change=float(np.linalg.norm(after-before,axis=1).max())
        require(np.isfinite(after).all() and .003<change<.1,'Facial ownership/deformation failed: '+obj_name)
        detail_motions[obj_name]=round(change,6)
        if bone_name=='jaw':require(np.allclose(points(upper),upper_before,atol=1e-7),'Upper tooth incorrectly follows jaw')
        b.rotation_quaternion=(1,0,0,0);bpy.context.view_layer.update()
    if source:SOURCE_FUR=fur_report
    return {
        'mesh_names':sorted(o.name for o in meshes),
        'mesh_objects': len(meshes), 'total_triangles': sum(sum(len(p.vertices) - 2 for p in o.data.polygons) for o in meshes),
        'bones': sorted(b.name for b in rig.data.bones),
        'bone_parent_map': {b.name: b.parent.name if b.parent else None for b in rig.data.bones},
        'body_components': components, 'topology_check_weld_tolerance_m': 0 if source else 1e-6,
        'bounds_min_m': allpoints.min(axis=0).round(6).tolist(),
        'bounds_max_m': allpoints.max(axis=0).round(6).tolist(),
        'pose_max_displacement_m': motions, 'detail_pose_displacement_m':detail_motions,
        'fur_root_probe_max_error_m':round(max_root_error,6) if source else 'Compared matched imported samples with source poses',
        'fur_roundtrip_samples':fur_report,
        'gltf_exporter_min_influence':.0001,
        'coat_material_roles':sorted(roles),'skin_weight_check': 'PASS', 'uv_texture_check': 'PASS',
    }


def inspect_glb(path):
    data = path.read_bytes()
    magic, version, length = struct.unpack_from('<4sII', data, 0)
    require(magic == b'glTF' and version == 2 and length == len(data), 'Invalid GLB header')
    jsonlen, jsontype = struct.unpack_from('<I4s', data, 12)
    require(jsontype == b'JSON', 'Missing glTF JSON')
    doc = json.loads(data[20:20 + jsonlen])
    require(len(doc.get('skins', [])) == 1 and len(doc['skins'][0]['joints']) == 29, 'GLB skin inventory')
    require(len(doc.get('images', [])) == 3 and all('bufferView' in im for im in doc['images']), 'Three maps must be embedded')
    require(not doc.get('animations') and not doc.get('cameras'), 'Unexpected animations/cameras')
    require(not doc.get('extensions', {}).get('KHR_lights_punctual'), 'Studio lights leaked into GLB')
    require(not any('uri' in b for b in doc.get('buffers', [])), 'External GLB buffer')
    require(all('extras' not in n for n in doc['nodes']), 'Unexpected private metadata in GLB')
    for mesh in doc['meshes']:
        for primitive in mesh['primitives']:
            require(primitive.get('mode', 4) == 4, 'Interchange mesh must be triangulated')
            require('JOINTS_0' in primitive['attributes'] and 'WEIGHTS_0' in primitive['attributes'], 'Missing skin data')
            if 'GuardFur' in mesh.get('name',''):
                require('COLOR_0' in primitive['attributes'],'Fur vertex colors missing from GLB')
    return {'embedded_textures': len(doc['images']), 'skins': len(doc['skins']), 'joint_count': 29,
            'external_resources': 0, 'studio_objects_exported': 0, 'clips_exported': 0}


def main():
    build = json.loads((ROOT / 'validation' / 'asset_validation.json').read_text())
    require(build.get('preview_status') == 'RENDERED_THIS_BUILD',
            'Complete asset validation requires previews rendered in this build; run builder without --no-render')
    require(build['project_version'] == (PROJECT / 'VERSION').read_text().strip(), 'Stale build report')
    require(build['asset_revision']=='gsd-v002','Wrong current asset revision')
    expected={'german_shepherd','side','front','rear','clay','deformation_check','deformation_side',
              'silhouette_160','head_closeup','paws_closeup','coat_closeup'}
    require({Path(p).stem for p in build['rendered_views']}==expected,'Incomplete current-build view set')
    for relative, record in build['files'].items():
        p = ROOT / relative
        require(hashlib.sha256(p.read_bytes()).hexdigest() == record['sha256'], 'Stale provenance hash: ' + relative)
    for p in (ROOT / 'previews').glob('*.png'):
        with Image.open(p) as im:
            im.verify()
    bpy.ops.wm.open_mainfile(filepath=str(ROOT / 'source' / 'german_shepherd.blend'))
    source = inventory(True)
    envelope = inspect_glb(ROOT / 'interchange' / 'german_shepherd.glb')
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=str(ROOT / 'interchange' / 'german_shepherd.glb'))
    imported = inventory(False)
    require(source['bones'] == imported['bones'], 'Bone names lost')
    require(source['mesh_names']==imported['mesh_names'],'Mesh names/inventory changed')
    require(source['coat_material_roles']==imported['coat_material_roles'],'Material roles changed')
    require(source['bone_parent_map'] == imported['bone_parent_map'], 'Bone hierarchy changed')
    require(source['total_triangles'] == imported['total_triangles'], 'Triangle count changed')
    for key in ['bounds_min_m', 'bounds_max_m']:
        require(np.allclose(source[key], imported[key], atol=2e-5), 'Bounds changed: ' + key)
    for bone, displacement in source['pose_max_displacement_m'].items():
        require(abs(displacement - imported['pose_max_displacement_m'][bone]) < 2e-5,
                'Roundtrip deformation changed: ' + bone)
    for name,displacement in source['detail_pose_displacement_m'].items():
        require(abs(displacement-imported['detail_pose_displacement_m'][name])<2e-5,'Facial roundtrip changed: '+name)
    # Render the imported GLB with the source studio, without its source meshes.
    with bpy.data.libraries.load(str(ROOT/'source'/'german_shepherd.blend'),link=False) as (available,loaded):
        loaded.objects=[n for n in available.objects if n.startswith('Studio_')]
        loaded.worlds=['Studio_World']
    for obj in loaded.objects:
        if obj is not None:bpy.context.scene.collection.objects.link(obj)
    scene=bpy.context.scene;scene.world=loaded.worlds[0]
    scene.camera=bpy.data.objects['Studio_Camera'];scene.render.engine='CYCLES'
    scene.cycles.samples=32;scene.cycles.use_denoising=True
    scene.render.threads_mode='FIXED';scene.render.threads=12
    scene.view_settings.view_transform='AgX';scene.view_settings.look='AgX - Medium High Contrast'
    scene.render.resolution_x=1500;scene.render.resolution_y=1200;scene.render.resolution_percentage=100
    scene.render.image_settings.file_format='PNG'
    preview=ROOT/'previews'/'imported_glb.png';scene.render.filepath=str(preview)
    bpy.ops.render.render(write_still=True)
    report = {
        'project_version': (PROJECT / 'VERSION').read_text().strip(), 'asset_revision': build['asset_revision'],
        'environment': 'Offline Blender Python ' + bpy.app.version_string,
        'blend_reopen': 'PASS', 'glb_import_roundtrip': 'PASS', 'provenance_hash_check': 'PASS',
        'preview_provenance': 'RENDERED_THIS_BUILD',
        'source': source, 'glb_envelope': envelope, 'imported': imported,
        'G6': 'NOT TESTED', 'G7': 'BLOCKED / NOT TESTED', 'G8': 'BLOCKED',
        'scope': 'Blender authoring and review interchange only; no native PZ importer/state validation.',
        'validator_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'imported_preview':{'path':'previews/imported_glb.png','sha256':hashlib.sha256(preview.read_bytes()).hexdigest()},
    }
    (ROOT / 'validation' / 'roundtrip_validation.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print('PASS: editable source, packed texture, original hierarchy, normalized skins, bounds and four deformation probes survived GLB roundtrip.', flush=True)


if __name__ == '__main__':
    main()
