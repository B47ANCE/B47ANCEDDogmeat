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
REVISION = "gsd-v001"
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


def anatomy():
    tube('Trunk', [((-.432, 0, .48), .009, .016), ((-.405, 0, .475), .055, .074), ((-.34, 0, .47), .10, .117),
                  ((-.24, 0, .467), .104, .132), ((-.12, 0, .468), .10, .118),
                  ((.03, 0, .466), .12, .145), ((.16, 0, .47), .125, .15),
                  ((.265, 0, .477), .112, .144), ((.33, 0, .472), .088, .12),
                  ((.355, 0, .463), .035, .077), ((.382, 0, .466), .009, .025)], 28)
    # Ruff and shoulder blend into the chest. Back is firm, not a show-stack dip.
    tube('NeckRuff', [((.205, 0, .481), .104, .133), ((.302, 0, .542), .106, .124),
                     ((.372, 0, .610), .090, .10), ((.436, 0, .665), .073, .083),
                     ((.481, 0, .70), .066, .070), ((.518, 0, .710), .048, .047)], 28)
    tube('Skull', [((.426, 0, .704), .055, .065), ((.48, 0, .713), .079, .071),
                  ((.527, 0, .713), .083, .069), ((.575, 0, .701), .071, .059),
                  ((.618, 0, .682), .052, .04)], 28)
    tube('Muzzle', [((.574, 0, .671), .059, .045), ((.62, 0, .665), .05, .039),
                   ((.668, 0, .664), .042, .032), ((.719, 0, .663), .034, .025),
                   ((.754, 0, .665), .03, .022)], 24)
    tube('LowerJaw', [((.57, 0, .646), .048, .024), ((.626, 0, .637), .043, .018),
                     ((.69, 0, .638), .032, .013), ((.741, 0, .647), .026, .012)], 20)
    for side, sign in [('L', 1), ('R', -1)]:
        y = .088 * sign
        ellipsoid('Shoulder_' + side, (.247, .073 * sign, .45), (.072, .044, .103), part=True)
        tube('Foreleg_' + side, [((.248, .067 * sign, .535), .025, .031),
                                 ((.242, y, .46), .041, .052), ((.218, y, .367), .032, .038),
                                 ((.228, y, .308), .025, .029), ((.231, y, .265), .022, .024),
                                 ((.246, y, .166), .018, .021), ((.25, y, .11), .017, .020),
                                 ((.251, y, .071), .02, .023), ((.27, y, .038), .028, .027)], 16)
        ellipsoid('ForePaw_' + side, (.284, y, .032), (.058, .036, .03), part=True)
        y = .09 * sign
        ellipsoid('Haunch_' + side, (-.311, .067 * sign, .44), (.078, .057, .113), part=True)
        tube('Hindleg_' + side, [((-.322, .059 * sign, .502), .028, .034),
                                 ((-.316, y, .435), .045, .057), ((-.255, y, .352), .043, .053),
                                 ((-.216, y, .286), .034, .039), ((-.279, y, .22), .025, .03),
                                 ((-.36, y, .134), .023, .025), ((-.352, y, .071), .018, .021),
                                 ((-.333, y, .039), .026, .023)], 16)
        ellipsoid('HindPaw_' + side, (-.311, y, .03), (.052, .034, .028), part=True)
        # Closed, cupped triangular ears, broad roots fused into the skull.
        ey = sign * .06
        verts = [(.548, ey - .036, .740), (.548, ey + .036, .740),
                 (.513, ey + sign * .027, .900), (.535, ey + sign * .009, .801),
                 (.482, ey - .036, .740), (.482, ey + .036, .740),
                 (.495, ey + sign * .027, .897)]
        # Watertight triangular prism with an inset front center for the cup.
        mesh_obj('Ear_' + side, verts, [(0, 1, 3), (1, 2, 3), (2, 0, 3),
                                        (4, 6, 5), (0, 4, 5, 1), (1, 5, 6, 2),
                                        (2, 6, 4, 0)], part=True)
    tube('Tail', [((-.393, 0, .475), .034, .038), ((-.473, 0, .42), .036, .043),
                 ((-.539, .012, .351), .04, .047), ((-.605, .022, .269), .041, .048),
                 ((-.677, .033, .192), .037, .043), ((-.749, .043, .16), .027, .032),
                 ((-.795, .048, .17), .011, .016), ((-.816, .05, .183), .003, .004)], 24)
    select(PARTS)
    bpy.ops.object.join()
    dog = bpy.context.object
    dog.name = 'GSD_CoatBody'
    # Fix primitive winding before union; the final outer surface is one mesh.
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.normals_make_consistent(inside=False)
    bpy.ops.object.mode_set(mode='OBJECT')
    dog.data.remesh_voxel_size = .0035
    bpy.ops.object.voxel_remesh()
    smooth = dog.modifiers.new('SurfaceRelax', 'SMOOTH')
    smooth.factor = .7
    smooth.iterations = 3
    apply(dog, smooth)
    triangles = sum(len(p.vertices) - 2 for p in dog.data.polygons)
    dec = dog.modifiers.new('AuthoringBudget', 'DECIMATE')
    dec.ratio = min(1, 10500 / triangles)
    apply(dog, dec)
    tri = dog.modifiers.new('StableTriangles', 'TRIANGULATE')
    apply(dog, tri)
    for face in dog.data.polygons:
        face.use_smooth = True
    dog['asset_revision'] = REVISION
    dog['provenance'] = 'Original independently authored geometry; no imported mesh or rig.'
    MODEL.append(dog)
    return dog


def coat_color(points):
    """Original spatial black/tan pattern, evaluated at texture-pixel positions."""
    x, y, z = points.T
    ay = np.abs(y)
    wave = .008 * np.sin(x * 53 + z * 27) + .003 * np.sin(x * 137 - z * 89)
    tan = np.tile(np.array([.57, .345, .158]), (len(points), 1))
    warm = np.clip((z - .06) / .45, 0, 1)
    tan += warm[:, None] * np.array([.08, .038, .014])
    # Ventral feathering / throat are warm buff, keeping paws darker than chest.
    cream = np.clip((.38 - z) / .10, 0, 1) * np.clip((x + .03) / .25, 0, 1)
    cream *= np.clip((.09 - ay) / .045, 0, 1)
    tan += cream[:, None] * np.array([.16, .15, .105])
    saddle_edge = .445 + .05 * np.clip((x + .10) / .4, 0, 1) + wave
    saddle = np.clip((z - saddle_edge) / .035, 0, 1)
    saddle *= np.clip((.335 - x) / .095, 0, 1) * np.clip((x + .44) / .09, 0, 1)
    # Neck's outer ruff, forehead, muzzle and ear backs.
    nape = np.clip((z - (.585 + .45 * (x - .34))) / .045, 0, 1)
    nape *= np.clip((x - .28) / .07, 0, 1) * np.clip((.54 - x) / .07, 0, 1)
    mask = np.clip((x - .605) / .035, 0, 1) * np.clip((z - .61) / .04, 0, 1)
    forehead = np.clip((z - .734) / .016, 0, 1) * np.clip((x - .44) / .06, 0, 1)
    forehead *= np.clip((.625 - x) / .03, 0, 1)
    tail = np.clip((-x - .405) / .055, 0, 1)
    eye_mask = .94 * np.exp(-((x - .600) / .063) ** 2 - ((z - .713) / .033) ** 2)
    eye_mask *= np.clip((x - .537) / .028, 0, 1)
    dark = np.maximum.reduce([saddle, nape, mask, forehead, tail, eye_mask])
    # Small tan eyebrow marks leave the long black mask legible.
    brow = np.exp(-((x - .585) / .026) ** 2 - ((ay - .047) / .031) ** 2 - ((z - .729) / .010) ** 2)
    cheek = np.exp(-((x - .588) / .034) ** 2 - ((ay - .06) / .022) ** 2 - ((z - .665) / .025) ** 2)
    dark *= 1 - .83 * brow
    dark *= 1 - .7 * cheek
    charcoal = np.tile(np.array([.042, .048, .055]), (len(points), 1))
    charcoal += np.clip((z - .35) / .5, 0, 1)[:, None] * np.array([.023, .019, .015])
    color = tan * (1 - dark[:, None]) + charcoal * dark[:, None]
    # Deterministic fine coat grain, no external photographic input.
    grain = (np.sin(x * 1801 + y * 823 + z * 937) * np.sin(x * 137 - y * 1481 + z * 571))
    strand = np.sin(x * 310 + y * 1430 + z * 715)
    color *= (1 + .020 * grain + .012 * strand)[:, None]
    return np.clip(color, 0, 1)


def texture(dog):
    select([dog])
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.uv.smart_project(angle_limit=math.radians(66), island_margin=.013)
    bpy.ops.object.mode_set(mode='OBJECT')
    size = 1024
    pixels = np.zeros((size, size, 3), dtype=np.uint8)
    filled = np.zeros((size, size), dtype=bool)
    uvdata = dog.data.uv_layers.active.data
    for face in dog.data.polygons:
        uv = np.array([tuple(uvdata[i].uv) for i in face.loop_indices]) * (size - 1)
        xyz = np.array([tuple(dog.data.vertices[i].co) for i in face.vertices])
        lo = np.floor(uv.min(axis=0)).astype(int).clip(0, size - 1)
        hi = np.ceil(uv.max(axis=0)).astype(int).clip(0, size - 1)
        if np.any(hi < lo):
            continue
        xx, yy = np.meshgrid(np.arange(lo[0], hi[0] + 1), np.arange(lo[1], hi[1] + 1))
        q = np.stack([xx.ravel(), yy.ravel()], axis=1) + .5
        a, b, c = uv
        determinant = (b[1] - c[1]) * (a[0] - c[0]) + (c[0] - b[0]) * (a[1] - c[1])
        if abs(determinant) < 1e-8:
            continue
        wa = ((b[1] - c[1]) * (q[:, 0] - c[0]) + (c[0] - b[0]) * (q[:, 1] - c[1])) / determinant
        wb = ((c[1] - a[1]) * (q[:, 0] - c[0]) + (a[0] - c[0]) * (q[:, 1] - c[1])) / determinant
        weights = np.stack([wa, wb, 1 - wa - wb], axis=1)
        inside = np.all(weights >= -1e-5, axis=1)
        rows = yy.ravel()[inside]
        cols = xx.ravel()[inside]
        pixels[rows, cols] = np.round(coat_color(weights[inside] @ xyz) * 255).astype(np.uint8)
        filled[rows, cols] = True
    # Eight-pixel padding prevents dark UV seams in filtered/mipped views.
    coverage = float(filled.mean())
    for _ in range(8):
        old = filled.copy()
        for axis, direction in [(0, 1), (0, -1), (1, 1), (1, -1)]:
            neighbor = np.roll(old, direction, axis=axis)
            take = (~filled) & neighbor
            pixels[take] = np.roll(pixels, direction, axis=axis)[take]
            filled[take] = True
    pixels[~filled] = [104, 67, 36]
    path = ROOT / 'textures' / 'coat_albedo.png'
    Image.fromarray(np.flipud(pixels)).save(path)
    image = bpy.data.images.load(str(path), check_existing=True)
    image.name = 'GSD_OriginalCoat_1024'
    image.pack()
    image.filepath = '//../textures/coat_albedo.png'
    mat = material('GSD_Coat', (.5, .3, .15), .84)
    nodes = mat.node_tree.nodes
    shader = next(n for n in nodes if n.type == 'BSDF_PRINCIPLED')
    tex = nodes.new('ShaderNodeTexImage')
    tex.image = image
    mat.node_tree.links.new(tex.outputs['Color'], shader.inputs['Base Color'])
    dog.data.materials.clear()
    dog.data.materials.append(mat)
    return coverage


def features():
    dark = material('GSD_LipEyelid', (.052, .046, .04), .68)
    nosemat = material('GSD_Nose', (.035, .039, .043), .48)
    eyemat = material('GSD_DarkAmberEye', (.115, .057, .022), .16)
    pupilmat = material('GSD_Pupil', (.007, .008, .009), .11)
    inner = material('GSD_EarInterior', (.30, .215, .165), .9)
    nailmat = material('GSD_Claw', (.13, .115, .10), .57)
    nose = ellipsoid('GSD_Nose', (.755, 0, .669), (.02, .032, .021), nosemat)
    MODEL.append(nose)
    for side, sign in [('L', 1), ('R', -1)]:
        ey = sign * .06
        verts = [(.543, ey - .020, .774), (.543, ey + .022, .774),
                 (.520, ey + sign * .021, .86), (.538, ey + sign * .008, .800)]
        inset = mesh_obj('GSD_EarInset_' + side, verts, [(0, 1, 3), (1, 2, 3), (2, 0, 3)])
        solid = inset.modifiers.new('EarInsetThickness', 'SOLIDIFY')
        solid.thickness = .002
        apply(inset, solid)
        inset.data.materials.append(inner)
        inset['rig_domain'] = 'ear_' + side
        MODEL.append(inset)
        rim = ellipsoid('GSD_EyeLid_' + side, (.588, sign * .061, .711), (.020, .006, .009), dark)
        eye = ellipsoid('GSD_Eye_' + side, (.591, sign * .065, .712), (.0145, .0032, .0063), eyemat)
        pupil = ellipsoid('GSD_Pupil_' + side, (.595, sign * .0675, .712), (.0045, .001, .0045), pupilmat, segments=16, rings=10)
        MODEL.extend([rim, eye, pupil])
        nostril = ellipsoid('GSD_Nostril_' + side, (.765, sign * .023, .673), (.007, .003, .004), pupilmat, segments=16, rings=10)
        MODEL.append(nostril)
        lip = curve_mesh('GSD_MouthLine_' + side,
                         [(.747, sign * .028, .650), (.713, sign * .035, .645),
                          (.667, sign * .044, .642), (.619, sign * .051, .640)], .0010, dark)
        MODEL.append(lip)
        for front, centerx, centery in [(True, .284, .088 * sign), (False, -.311, .09 * sign)]:
            domain = ('front_foot_' if front else 'rear_foot_') + side
            for t in [-1.5, -.5, .5, 1.5]:
                # Tiny arched toe grooves and claws; four paws stay grounded.
                nail = ellipsoid('GSD_Claw_' + domain + '_' + str(t),
                                 (centerx + (.049 if front else .045), centery + t * .015, .019),
                                 (.010, .004, .0045), nailmat, segments=12, rings=8)
                nail['rig_domain'] = domain
                MODEL.append(nail)
            for t in [-1, 0, 1]:
                groove = curve_mesh('GSD_Toe_' + domain + '_' + str(t),
                                    [(centerx + .045, centery + t * .015, .027),
                                     (centerx + .028, centery + t * .015, .05)], .0007, dark)
                groove['rig_domain'] = domain
                MODEL.append(groove)


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
    bone('pelvis', (-.30, 0, .455), (-.15, 0, .47), 'root')
    bone('spine', (-.15, 0, .47), (.07, 0, .48), 'pelvis')
    bone('chest', (.07, 0, .48), (.26, 0, .50), 'spine')
    bone('neck', (.26, 0, .50), (.475, 0, .705), 'chest')
    bone('head', (.475, 0, .705), (.741, 0, .665), 'neck')
    bone('jaw', (.577, 0, .642), (.741, 0, .645), 'head')
    for side, sign in [('L', 1), ('R', -1)]:
        bone('ear_' + side, (.51, sign * .06, .75), (.50, sign * .087, .898), 'head')
        fy, ry = sign * .088, sign * .09
        bone('front_upper_' + side, (.24, fy, .46), (.22, fy, .36), 'chest')
        bone('front_lower_' + side, (.22, fy, .36), (.251, fy, .071), 'front_upper_' + side)
        bone('front_pastern_' + side, (.251, fy, .071), (.267, fy, .033), 'front_lower_' + side)
        bone('front_foot_' + side, (.267, fy, .033), (.326, fy, .025), 'front_pastern_' + side)
        bone('rear_upper_' + side, (-.316, ry, .435), (-.216, ry, .286), 'pelvis')
        bone('rear_lower_' + side, (-.216, ry, .286), (-.36, ry, .134), 'rear_upper_' + side)
        bone('rear_pastern_' + side, (-.36, ry, .134), (-.333, ry, .039), 'rear_lower_' + side)
        bone('rear_foot_' + side, (-.333, ry, .039), (-.268, ry, .023), 'rear_pastern_' + side)
    tailpoints = [(-.39, 0, .475), (-.50, .006, .39), (-.605, .022, .269),
                  (-.725, .04, .164), (-.825, .05, .197)]
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
            elif z > .750 and x > .44:
                candidates = ['ear_' + side, 'head']
            elif x > .455 and z > .596:
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
        'body_vertices': len(dog.data.vertices), 'body_triangles': len(dog.data.polygons),
        'total_triangles': sum(sum(len(p.vertices) - 2 for p in obj.data.polygons) for obj in MODEL),
        'mesh_objects': len(MODEL), 'bones': len(rig.data.bones), 'body_nonmanifold_edges': nonmanifold,
        'body_degenerate_faces': degenerate, 'unweighted_vertices': unweighted,
        'invalid_weight_sums': badsum, 'vertices_over_four_influences': overfour,
        'texture_size': [1024, 1024], 'uv_occupied_fraction_before_padding': round(coverage, 4),
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
    scene.world.color = (.16, .16, .16)
    world = scene.world
    world.use_nodes = True
    background = next(n for n in world.node_tree.nodes if n.type == 'BACKGROUND')
    background.inputs['Color'].default_value = (.19, .23, .29, 1)
    background.inputs['Strength'].default_value = .32
    scene.view_settings.view_transform = 'AgX'
    bpy.ops.mesh.primitive_plane_add(size=200, location=(0, 0, -.002))
    ground = bpy.context.object
    ground.name = 'Studio_Ground'
    ground.data.materials.append(material('Studio_Slate', (.22, .255, .29), .9))
    for name, location, power, size, color in [
        ('Studio_Key', (1.6, -2.3, 3.3), 260, 2.5, (1, .88, .75)),
        ('Studio_Fill', (1, 2.2, 1.5), 125, 2, (.75, .86, 1)),
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
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--no-render', action='store_true')
    args = parser.parse_args()
    started = time.time()
    for folder in ['textures', 'interchange', 'previews', 'validation']:
        (ROOT / folder).mkdir(parents=True, exist_ok=True)
    # Factory state belongs exclusively to this standalone authoring process.
    bpy.ops.wm.read_factory_settings(use_empty=True)
    log('Build original anatomy')
    dog = anatomy()
    log('UV and original coat texture')
    coverage = texture(dog)
    features()
    rig = skeleton()
    for obj in MODEL + [rig]:
        obj['project_version'] = (PROJECT / 'VERSION').read_text().strip()
    report = validate(dog, rig, coverage)
    report['preview_status'] = ('RENDERED_THIS_BUILD' if not args.no_render
                                else 'NOT RENDERED; cached previews excluded from provenance')
    log(json.dumps(report, indent=2))
    export_glb(rig)
    camera = studio()
    bpy.ops.wm.save_as_mainfile(filepath=str(ROOT / 'source' / 'german_shepherd.blend'), compress=True)
    if not args.no_render:
        render(camera, 'german_shepherd', (2.2, -3.7, 1.64), target=(.015, 0, .448), scale=1.86)
        bpy.data.objects['Studio_Ground'].hide_render = True
        render(camera, 'side', (0, -4, .44), scale=1.86)
        render(camera, 'front', (4, 0, .46), scale=1.12, size=(1000, 1000))
        render(camera, 'rear', (-4, 0, .46), scale=1.12, size=(1000, 1000))
        bpy.data.objects['Studio_Ground'].hide_render = False
        clay = material('Studio_Clay', (.49, .56, .61), .9)
        bpy.context.scene.view_layers[0].material_override = clay
        render(camera, 'clay', (2.2, -3.7, 1.64), target=(.015, 0, .448), scale=1.86)
        bpy.context.scene.view_layers[0].material_override = None
        pose_bone(rig, 'head', -.35, (0, 0, 1))
        pose_bone(rig, 'tail_2', .5, (0, 0, 1))
        pose_bone(rig, 'front_lower_L', .5, (0, 1, 0))
        pose_bone(rig, 'rear_lower_R', -.45, (0, 1, 0))
        render(camera, 'deformation_check', (2.2, -3.7, 1.64), target=(.015, 0, .448), scale=1.86)
        reset_pose(rig)
        bpy.data.objects['Studio_Ground'].hide_render = True
        render(camera, 'silhouette_160', (0, -4, .44), scale=1.86, size=(160, 120))
        bpy.data.objects['Studio_Ground'].hide_render = False
        # Restore the initial review framing in the editable source.
        camera.location = (2.2, -3.7, 1.64)
        camera.rotation_euler = (Vector((.015, 0, .448)) - camera.location).to_track_quat('-Z', 'Y').to_euler()
        camera.data.ortho_scale = 1.86
        bpy.context.scene.render.resolution_x, bpy.context.scene.render.resolution_y = 1400, 1050
    bpy.context.scene.render.filepath = '//../previews/german_shepherd.png'
    # Packed image keeps the canonical source editable and self-contained.
    select([rig])
    bpy.ops.wm.save_as_mainfile(filepath=str(ROOT / 'source' / 'german_shepherd.blend'))
    report['build_seconds'] = round(time.time() - started, 2)
    folders = ['source', 'textures', 'interchange'] + ([] if args.no_render else ['previews'])
    report['files'] = {str(p.relative_to(ROOT)).replace('\\', '/'): {
        'bytes': p.stat().st_size, 'sha256': hashlib.sha256(p.read_bytes()).hexdigest()}
        for folder in folders
        for p in sorted((ROOT / folder).iterdir()) if p.is_file() and p.suffix != '.blend1'}
    (ROOT / 'validation' / 'asset_validation.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    log('DONE in ' + str(report['build_seconds']) + ' seconds')


if __name__ == '__main__':
    main()
