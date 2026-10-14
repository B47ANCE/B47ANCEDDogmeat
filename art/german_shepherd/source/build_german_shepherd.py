"""Original German Shepherd authoring asset. Run in a fresh standalone bpy process.

Requires Blender Python (tested with bpy 5.2.2), NumPy and Pillow. These are
authoring tools, never Project Zomboid dependencies. Rebuilds only this asset's
owned outputs; do not run inside a Blender session containing unsaved work.
"""
from pathlib import Path
import argparse
import hashlib
import json
import math
import time

import bpy
import numpy as np
from mathutils import Quaternion, Vector
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
PROJECT = ROOT.parents[1]
REVISION = "gsd-v002"
MODEL = []
PARTS = []


def log(message):
    print(message, flush=True)


def select(objects):
    bpy.ops.object.select_all(action='DESELECT')
    for obj in objects:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = objects[0]


def apply(obj, modifier):
    select([obj])
    bpy.ops.object.modifier_apply(modifier=modifier.name)


def linear(c):
    return tuple(v / 12.92 if v <= .04045 else ((v + .055) / 1.055) ** 2.4 for v in c)


def material(name, color, roughness=.6, metallic=0):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    shader = next(n for n in mat.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
    shader.inputs['Base Color'].default_value = (*linear(color), 1)
    shader.inputs['Roughness'].default_value = roughness
    shader.inputs['Specular IOR Level'].default_value = .25
    shader.inputs['Metallic'].default_value = metallic
    mat.diffuse_color = (*linear(color), 1)
    return mat


def mesh_obj(name, vertices, faces, part=False):
    mesh = bpy.data.meshes.new(name + '_Mesh')
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    for p in mesh.polygons:
        p.use_smooth = True
    if part:
        PARTS.append(obj)
    return obj


def tube(name, rings, sides=20, part=True):
    """Loft an elliptical tube: center, lateral radius, sagittal radius."""
    # Interpolated rings avoid straight-sided tube/haunch/tail silhouettes.
    original = np.array([(*c, ry, rz) for c, ry, rz in rings])
    refined = []
    for i in range(len(original) - 1):
        p0, p1 = original[max(0, i - 1)], original[i]
        p2, p3 = original[i + 1], original[min(i + 2, len(original) - 1)]
        for t in np.linspace(0, 1, 5, endpoint=False):
            p = .5 * ((2 * p1) + (-p0 + p2) * t +
                      (2 * p0 - 5 * p1 + 4 * p2 - p3) * t * t +
                      (-p0 + 3 * p1 - 3 * p2 + p3) * t * t * t)
            refined.append((tuple(p[:3]), max(.002, p[3]), max(.002, p[4])))
    refined.append(rings[-1])
    rings = refined
    verts = []
    centers = [Vector(r[0]) for r in rings]
    for i, (center, ry, rz) in enumerate(rings):
        tangent = centers[min(i + 1, len(rings) - 1)] - centers[max(i - 1, 0)]
        tangent.normalize()
        lateral = Vector((0, 1, 0))
        lateral = (lateral - tangent * lateral.dot(tangent)).normalized()
        vertical = tangent.cross(lateral).normalized()
        for j in range(sides):
            angle = j * 2 * math.pi / sides
            point = Vector(center) + lateral * (ry * math.cos(angle)) + vertical * (rz * math.sin(angle))
            verts.append(tuple(point))
    faces = []
    for i in range(len(rings) - 1):
        for j in range(sides):
            a, b = i * sides + j, i * sides + (j + 1) % sides
            faces.append((a, b, b + sides, a + sides))
    faces.append(tuple(reversed(range(sides))))
    faces.append(tuple((len(rings) - 1) * sides + j for j in range(sides)))
    return mesh_obj(name, verts, faces, part)


def ellipsoid(name, center, radius, mat=None, part=False, segments=16, rings=10):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=segments, ring_count=rings, location=center)
    obj = bpy.context.object
    obj.name = name
    obj.data.name = name + '_Mesh'
    obj.scale = radius
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    # Model-space geometry and identity object transforms simplify interchange.
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=False)
    for face in obj.data.polygons:
        face.use_smooth = True
    if mat:
        obj.data.materials.append(mat)
    if part:
        PARTS.append(obj)
    return obj


def curve_mesh(name, points, radius, mat):
    curve = bpy.data.curves.new(name, 'CURVE')
    curve.dimensions = '3D'
    curve.resolution_u = 4
    curve.bevel_depth = radius
    curve.bevel_resolution = 1
    spline = curve.splines.new('BEZIER')
    spline.bezier_points.add(len(points) - 1)
    for bp, point in zip(spline.bezier_points, points):
        bp.co = point
        bp.handle_left_type = 'AUTO'
        bp.handle_right_type = 'AUTO'
    obj = bpy.data.objects.new(name, curve)
    bpy.context.collection.objects.link(obj)
    obj.data.materials.append(mat)
    select([obj])
    bpy.ops.object.convert(target='MESH')
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    return bpy.context.object


def skeleton():
    arm = bpy.data.armatures.new('GSD_OriginalDeformSkeleton')
    rig = bpy.data.objects.new('GSD_Rig', arm)
    bpy.context.collection.objects.link(rig)
    select([rig])
    bpy.ops.object.mode_set(mode='EDIT')
    definitions = {}

    def bone(name, head, tail, parent=None, deform=True):
        b = arm.edit_bones.new(name)
        b.head, b.tail = head, tail
        b.use_deform = deform
        if parent:
            b.parent = arm.edit_bones[parent]
        definitions[name] = (Vector(head), Vector(tail))

    bone('root', (0, 0, .015), (0, 0, .12), deform=False)
    bone('pelvis', (-.285, 0, .475), (-.15, 0, .48), 'root')
    bone('spine', (-.15, 0, .47), (.07, 0, .48), 'pelvis')
    bone('chest', (.07, 0, .48), (.24, 0, .54), 'spine')
    bone('neck', (.24, 0, .54), (.395, 0, .785), 'chest')
    bone('head', (.395, 0, .785), (.673, 0, .735), 'neck')
    bone('jaw', (.48, 0, .722), (.655, 0, .681), 'head')
    for side, sign in [('L', 1), ('R', -1)]:
        bone('ear_' + side, (.435, sign * .063, .84), (.41, sign * .087, 1.025), 'head')
        fy, ry = sign * .112, sign * .108
        bone('front_upper_' + side, (.24, fy, .48), (.20, fy, .37), 'chest')
        bone('front_lower_' + side, (.20, fy, .37), (.235, fy, .095), 'front_upper_' + side)
        bone('front_pastern_' + side, (.235, fy, .095), (.264, fy, .038), 'front_lower_' + side)
        bone('front_foot_' + side, (.264, fy, .038), (.34, fy, .025), 'front_pastern_' + side)
        bone('rear_upper_' + side, (-.285, ry, .459), (-.214, ry, .295), 'pelvis')
        bone('rear_lower_' + side, (-.214, ry, .295), (-.342, ry, .134), 'rear_upper_' + side)
        bone('rear_pastern_' + side, (-.342, ry, .134), (-.318, ry, .037), 'rear_lower_' + side)
        bone('rear_foot_' + side, (-.318, ry, .037), (-.235, ry, .024), 'rear_pastern_' + side)
    tailpoints = [(-.363, 0, .498), (-.50, .018, .377), (-.62, .036, .269),
                  (-.72, .049, .245), (-.79, .055, .276)]
    for i in range(4):
        bone('tail_' + str(i + 1), tailpoints[i], tailpoints[i + 1], 'pelvis' if i == 0 else 'tail_' + str(i))
    bpy.ops.object.mode_set(mode='OBJECT')
    rig.show_in_front = True
    rig['axes'] = 'Authoring convention: metres, Z up, head +X; PZ mapping NOT TESTED.'
    rig['provenance'] = 'Independent original deformation skeleton; no native/third-party rig copied.'
    for obj in MODEL:
        groups = {name: obj.vertex_groups.new(name=name) for name in definitions if name != 'root'}
        for vertex in obj.data.vertices:
            x, y, z = vertex.co
            side = 'L' if y >= 0 else 'R'
            if obj.get('rig_domain'):
                candidates = [obj['rig_domain']]
            elif obj.name != 'GSD_CoatBody':
                candidates = ['head']
            elif x < -.43:
                candidates = ['pelvis', 'tail_1', 'tail_2', 'tail_3', 'tail_4']
            elif z > .855 and .35 < x < .49:
                candidates = ['ear_' + side, 'head']
            elif x > .445 and z > .69:
                candidates = ['head', 'neck']
            elif z < .34 and x > .09:
                candidates = ['front_upper_' + side, 'front_lower_' + side,
                              'front_pastern_' + side, 'front_foot_' + side]
            elif z < .34 and x < -.12:
                candidates = ['rear_upper_' + side, 'rear_lower_' + side,
                              'rear_pastern_' + side, 'rear_foot_' + side]
            elif abs(y) > .075 and x > .10 and z < .48:
                candidates = ['chest', 'front_upper_' + side, 'front_lower_' + side]
            elif abs(y) > .07 and x < -.16 and z < .47:
                candidates = ['pelvis', 'rear_upper_' + side, 'rear_lower_' + side]
            else:
                candidates = ['pelvis', 'spine', 'chest', 'neck', 'head']
            distances = []
            point = vertex.co
            for name in candidates:
                a, b = definitions[name]
                delta = b - a
                t = max(0, min(1, (point - a).dot(delta) / delta.length_squared))
                distances.append(((point - a - delta * t).length, name))
            chosen = sorted(distances)[:4]
            weights = [(1 / (d + .014) ** 4, name) for d, name in chosen]
            total = sum(w for w, _ in weights)
            for w, name in weights:
                groups[name].add([vertex.index], w / total, 'REPLACE')
        modifier = obj.modifiers.new('GSD_Skin', 'ARMATURE')
        modifier.object = rig
        obj.parent = rig
    return rig


def evaluated_points(obj):
    bpy.context.view_layer.update()
    evaluated = obj.evaluated_get(bpy.context.evaluated_depsgraph_get())
    mesh = evaluated.to_mesh()
    result = np.array([tuple(evaluated.matrix_world @ v.co) for v in mesh.vertices])
    evaluated.to_mesh_clear()
    return result


def pose_bone(rig, name, angle, world_axis):
    pb = rig.pose.bones[name]
    pb.rotation_mode = 'QUATERNION'
    local_axis = pb.bone.matrix_local.to_3x3().inverted() @ Vector(world_axis)
    pb.rotation_quaternion = Quaternion(local_axis.normalized(), angle)


def reset_pose(rig):
    for pb in rig.pose.bones:
        pb.rotation_mode = 'QUATERNION'
        pb.rotation_quaternion = (1, 0, 0, 0)
    bpy.context.view_layer.update()


def validate(dog, rig, coverage):
    import bmesh
    bm = bmesh.new()
    bm.from_mesh(dog.data)
    nonmanifold = sum(not e.is_manifold for e in bm.edges)
    degenerate = sum(f.calc_area() < 1e-10 for f in bm.faces)
    bm.free()
    unweighted = badsum = overfour = 0
    for obj in MODEL:
        for v in obj.data.vertices:
            weights = [g.weight for g in v.groups if g.weight > 0]
            unweighted += not bool(weights)
            badsum += abs(sum(weights) - 1) > 1e-5
            overfour += len(weights) > 4
    neutral = evaluated_points(dog)
    pose_tests = {}
    for name, angle, axis in [('head', .35, (0, 0, 1)), ('front_lower_L', .50, (0, 1, 0)),
                              ('rear_lower_R', -.45, (0, 1, 0)), ('tail_2', .5, (0, 0, 1))]:
        pose_bone(rig, name, angle, axis)
        posed = evaluated_points(dog)
        distances = np.linalg.norm(posed - neutral, axis=1)
        pose_tests[name] = {'radians': angle, 'world_axis': axis, 'moved_vertices': int((distances > .001).sum()),
                            'max_displacement_m': round(float(distances.max()), 6),
                            'finite': bool(np.isfinite(posed).all())}
        reset_pose(rig)
    bounds = np.concatenate([evaluated_points(obj) for obj in MODEL])
    result = {
        'project_version': (PROJECT / 'VERSION').read_text().strip(),
        'asset_revision': REVISION, 'environment': 'Offline Blender Python ' + bpy.app.version_string,
        'body_vertices': len(dog.data.vertices), 'body_triangles': sum(len(p.vertices)-2 for p in dog.data.polygons),
        'total_triangles': sum(sum(len(p.vertices) - 2 for p in obj.data.polygons) for obj in MODEL),
        'mesh_objects': len(MODEL), 'bones': len(rig.data.bones), 'body_nonmanifold_edges': nonmanifold,
        'body_degenerate_faces': degenerate, 'unweighted_vertices': unweighted,
        'invalid_weight_sums': badsum, 'vertices_over_four_influences': overfour,
        'texture_size': [2048, 2048], 'uv_occupied_fraction_before_padding': round(coverage, 4),
        'bounds_min_m': bounds.min(axis=0).round(6).tolist(),
        'bounds_max_m': bounds.max(axis=0).round(6).tolist(),
        'dimensions_m': np.ptp(bounds, axis=0).round(6).tolist(),
        'authoring_axes': 'Z up; head +X; metres; identity mesh and armature transforms',
        'pose_tests': pose_tests,
        'animation_clips': 'None: deformation checks only; native state/action set remains unimplemented.',
        'pz_import': 'NOT TESTED', 'G6': 'NOT TESTED', 'G7': 'BLOCKED / NOT TESTED', 'G8': 'BLOCKED',
    }
    assert nonmanifold == 0 and degenerate == 0, (nonmanifold, degenerate)
    assert unweighted == badsum == overfour == 0
    assert all(t['finite'] and t['moved_vertices'] > 10 and .005 < t['max_displacement_m'] < .25 for t in pose_tests.values())
    assert all(np.allclose(obj.matrix_world, np.eye(4)) for obj in MODEL + [rig])
    return result


def studio():
    scene = bpy.context.scene
    scene.unit_settings.system = 'METRIC'
    scene.unit_settings.scale_length = 1
    scene.render.resolution_x = 1400
    scene.render.resolution_y = 1050
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = 'PNG'
    if scene.world is None:
        scene.world = bpy.data.worlds.new('Studio_World')
    scene.world.color = (.6, .6, .6)
    world = scene.world
    world.use_nodes = True
    background = next(n for n in world.node_tree.nodes if n.type == 'BACKGROUND')
    background.inputs['Color'].default_value = (.67, .70, .75, 1)
    background.inputs['Strength'].default_value = .45
    scene.view_settings.view_transform = 'AgX'
    scene.view_settings.look = 'AgX - Medium High Contrast'
    scene.render.engine = 'CYCLES'
    scene.cycles.samples = 32
    scene.cycles.use_denoising = True
    scene.render.threads_mode = 'FIXED'
    scene.render.threads = 12
    bpy.ops.mesh.primitive_plane_add(size=200, location=(0, 0, -.002))
    ground = bpy.context.object
    ground.name = 'Studio_Ground'
    ground.data.materials.append(material('Studio_Slate', (.76, .77, .78), .9))
    for name, location, power, size, color in [
        ('Studio_Key', (1.6, -2.3, 3.3), 260, 2.5, (1, .96, .91)),
        ('Studio_Fill', (1, 2.2, 1.5), 125, 2, (.91, .95, 1)),
        ('Studio_Rim', (-1.8, .7, 2.3), 320, 1.7, (1, .92, .8))]:
        data = bpy.data.lights.new(name, 'AREA')
        data.energy, data.shape, data.size, data.color = power, 'DISK', size, color
        obj = bpy.data.objects.new(name, data)
        scene.collection.objects.link(obj)
        obj.location = location
        obj.rotation_euler = (Vector((0, 0, .45)) - obj.location).to_track_quat('-Z', 'Y').to_euler()
    data = bpy.data.cameras.new('Studio_Camera')
    camera = bpy.data.objects.new('Studio_Camera', data)
    scene.collection.objects.link(camera)
    scene.camera = camera
    return camera


def render(camera, name, position, target=(0, 0, .44), scale=1.83, size=(1400, 1050)):
    scene = bpy.context.scene
    camera.location = position
    camera.rotation_euler = (Vector(target) - camera.location).to_track_quat('-Z', 'Y').to_euler()
    camera.data.type = 'ORTHO'
    camera.data.ortho_scale = scale
    scene.render.resolution_x, scene.render.resolution_y = size
    scene.render.filepath = str(ROOT / 'previews' / (name + '.png'))
    log('Render ' + name + ' using ' + scene.render.engine)
    bpy.ops.render.render(write_still=True)


def export_glb(rig):
    select(MODEL + [rig])
    bpy.ops.export_scene.gltf(filepath=str(ROOT / 'interchange' / 'german_shepherd.glb'),
                              export_format='GLB', use_selection=True, export_animations=False,
                              export_apply=False, export_yup=True, export_skins=True,
                              export_extras=False, export_cameras=False, export_lights=False)


def main():
    import sys
    sys.path.insert(0,str(Path(__file__).resolve().parent))
    import shepherd_anatomy
    import shepherd_coat
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--draft',action='store_true',help='Three quick previews; not complete validation')
    parser.add_argument('--no-render',action='store_true')
    args=parser.parse_args();started=time.time();g=sys.modules[__name__]
    for folder in ['textures','interchange','previews','validation']:(ROOT/folder).mkdir(parents=True,exist_ok=True)
    bpy.ops.wm.read_factory_settings(use_empty=True)
    log('Build v002 anatomy');dog=shepherd_anatomy.build(g)
    log('Build face, ears, mouth and paws');shepherd_anatomy.details(g)
    rig=skeleton()
    shepherd_anatomy.refine_proportions(g,rig)
    log('Paint original 2048 coat maps');coverage=shepherd_coat.texture(g,dog)
    log('Build skin-anchored guard fur');groom=shepherd_coat.groom(g,dog,rig)
    for obj in MODEL+[rig]:
        obj['project_version']=(PROJECT/'VERSION').read_text().strip()
        obj['asset_revision']=REVISION
    log('Validate structure');report=validate(dog,rig,coverage)
    report['fur'] = groom
    report['preview_status']='NOT RENDERED' if args.no_render else ('DRAFT_ONLY' if args.draft else 'RENDERED_THIS_BUILD')
    report['quality_status']='AUTHORING CANDIDATE; visual acceptance reviewed separately, never inferred from tests'
    report['mesh_names']=sorted(o.name for o in MODEL)
    report['texture_roles']=['albedo','normal','roughness']
    log('Export review GLB');export_glb(rig)
    camera=studio();scene=bpy.context.scene
    hero=(2.6,-3.8,1.48);target=(.0,0,.49);scale=1.88
    rendered=[]
    def view(name,position,target=target,scale=scale,size=(1500,1200)):
        if args.draft:size=(900,720)
        render(camera,name,position,target,scale,size);rendered.append('previews/'+name+'.png')
    if args.draft:scene.cycles.samples=16
    if not args.no_render:
        view('german_shepherd',hero)
        view('head_closeup',(2.0,-3.4,1.45),(.49,0,.82),.57,(1200,1200))
        view('side',(0,-4,.53),scale=1.82)
        if not args.draft:
            view('front',(4,0,.53),scale=1.20,size=(1100,1300))
            view('rear',(-4,0,.53),scale=1.20,size=(1100,1300))
            view('paws_closeup',(1.3,-2.6,.7),(.255,0,.11),.40,(1200,1000))
            view('coat_closeup',(.10,-3,.88),(.08,-.02,.55),.55,(1200,1000))
            fur=bpy.data.objects['GSD_GuardFur'];fur.hide_render=True
            clay=material('Studio_Clay',(.47,.49,.51),.86)
            scene.view_layers[0].material_override=clay
            view('clay',hero)
            scene.view_layers[0].material_override=None;fur.hide_render=False
            pose_bone(rig,'head',-.28,(0,0,1));pose_bone(rig,'tail_2',.4,(0,0,1))
            pose_bone(rig,'front_lower_L',.4,(0,1,0));pose_bone(rig,'rear_lower_R',-.35,(0,1,0))
            pose_bone(rig,'jaw',.12,(0,1,0))
            view('deformation_check',hero)
            view('deformation_side',(0,-4,.53),scale=1.82)
            reset_pose(rig)
            view('silhouette_160',(0,-4,.53),scale=1.82,size=(160,120))
    reset_pose(rig)
    camera.location=hero;camera.rotation_euler=(Vector(target)-camera.location).to_track_quat('-Z','Y').to_euler()
    camera.data.ortho_scale=scale;scene.render.resolution_x,scene.render.resolution_y=1500,1200
    scene.render.filepath='//../previews/german_shepherd.png'
    select([rig]);bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'source'/'german_shepherd.blend'),compress=True)
    report['rendered_views']=rendered;report['build_seconds']=round(time.time()-started,2)
    # Validator owns its own hash in the independent report. Editing only a
    # verification tool must not imply that geometry or rendered pixels changed.
    owned=[p for folder in ['source','textures','interchange']for p in sorted((ROOT/folder).iterdir())
           if p.is_file()and p.suffix!='.blend1' and p.name!='validate_german_shepherd.py']
    owned += [ROOT/p for p in rendered]
    report['files']={p.relative_to(ROOT).as_posix():{'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}for p in owned}
    (ROOT/'validation'/'asset_validation.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    log('DONE '+json.dumps({k:report[k]for k in ['body_triangles','total_triangles','mesh_objects','build_seconds','preview_status']}))


if __name__=='__main__':
    main()
