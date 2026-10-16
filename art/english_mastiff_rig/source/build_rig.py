"""Original large-mastiff intermediate rig and contact-aware motion authoring.

Run only in a fresh standalone Blender-Python process. No game writes, remote
operations, installs, native rig copying, or changes to the em-v001 checkpoint.
"""
import hashlib
import json
import math
from pathlib import Path
import sys

import bpy
import bmesh
from mathutils import Matrix, Quaternion, Vector

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT.parent / 'english_mastiff'
FPS = 24
REVISION = 'em-rig-v001'
TAU = math.tau
DEFS = {}
LEGS = {}


def write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + '\n', encoding='utf-8', newline='\n')


def smooth(t):
    t = max(0.0, min(1.0, t))
    return t * t * (3 - 2 * t)


def add(name, head, tail, parent=None, deform=True):
    DEFS[name] = {'head': Vector(head), 'tail': Vector(tail), 'parent': parent, 'deform': deform}


def skeleton():
    add('DM_Root', (0, 0, 0), (0, 0, .15), deform=False)
    chain = [('Pelvis', (0, .43, .88)), ('Spine01', (0, .30, .87)),
             ('Spine02', (0, .10, .88)), ('Spine03', (0, -.13, .91)),
             ('Chest', (0, -.30, .96)), ('Neck01', (0, -.43, 1.04)),
             ('Neck02', (0, -.57, 1.16)), ('Head', (0, -.67, 1.19)),
             ('HeadEnd', (0, -.89, 1.12))]
    for i, (name, point) in enumerate(chain[:-1]):
        add('DM_' + name, point, chain[i + 1][1], 'DM_' + chain[i-1][0] if i else 'DM_Root')
    add('DM_Jaw', (0, -.70, 1.03), (0, -.89, .94), 'DM_Head', False)
    for side, sign in [('L', 1), ('R', -1)]:
        add('DM_Ear.' + side, (sign*.18, -.66, 1.24), (sign*.22, -.61, 1.04), 'DM_Head')
        add('DM_Jowl.' + side, (sign*.12, -.79, 1.02), (sign*.12, -.81, .89), 'DM_Head')
    tail = [(0, .70, .96), (0, .77, .77), (.015, .80, .59), (.03, .86, .43), (.03, .94, .34)]
    for i in range(4):
        add('DM_Tail%02d' % (i+1), tail[i], tail[i+1], 'DM_Pelvis' if i == 0 else 'DM_Tail%02d' % i)
    for side, sign in [('L', 1), ('R', -1)]:
        front = [(sign*.15, -.33, .99), (sign*.23, -.39, .84), (sign*.23, -.29, .48),
                 (sign*.21, -.43, .14), (sign*.21, -.46, .075),
                 (sign*.21, -.57, .055), (sign*.21, -.63, .05)]
        rear = [(sign*.15, .43, .90), (sign*.22, .48, .82), (sign*.24, .37, .53),
                (sign*.22, .65, .26), (sign*.22, .61, .075),
                (sign*.22, .49, .055), (sign*.22, .44, .05)]
        for key, points, names, parent in [
                ('F'+side, front, ['Scapula', 'UpperFore', 'Forearm', 'Carpus', 'FrontPaw', 'FrontToe'], 'DM_Chest'),
                ('R'+side, rear, ['Hip', 'Thigh', 'Shin', 'Hock', 'RearPaw', 'RearToe'], 'DM_Pelvis')]:
            bones = []
            for i, name in enumerate(names):
                bone = 'DM_' + name + '.' + side
                add(bone, points[i], points[i+1], parent if i == 0 else bones[-1])
                bones.append(bone)
            LEGS[key] = {'points': [Vector(p) for p in points], 'bones': bones, 'front': key[0] == 'F'}


def bind(mesh, armature):
    """Blender bone-heat solve, normalized and capped to the inspected four lanes."""
    bpy.ops.object.select_all(action='DESELECT')
    mesh.select_set(True)
    armature.select_set(True)
    bpy.context.view_layer.objects.active = armature
    bpy.ops.object.parent_set(type='ARMATURE_AUTO')
    counts = {}
    def capsule_weights(point, names):
        values = {}
        for name in names:
            start, end = DEFS[name]['head'], DEFS[name]['tail']
            edge = end-start
            factor = max(0, min(1, (point-start).dot(edge)/edge.length_squared))
            distance = (point-start-edge*factor).length
            values[name] = 1/(distance*distance+.035**2)**2
        total = sum(values.values())
        return {name: value/total for name, value in values.items()}
    def mix(weights, target, factor):
        return {name: (1-factor)*weights.get(name, 0)+factor*target.get(name, 0)
                for name in weights.keys() | target.keys()}
    for vertex in mesh.data.vertices:
        point = vertex.co
        weights = {mesh.vertex_groups[g.group].name: g.weight for g in vertex.groups if g.weight > 1e-8}
        # Bone heat bleeds between the close rear legs, underside and hanging tail.
        # Smooth, inspected anatomical masks keep these distinct without a remesh.
        central = 1-smooth((abs(point.x)-.07)/.12)
        belly = central*smooth((point.z-.25)/.12)*(1-smooth((point.z-.78)/.18))
        belly *= smooth((point.y+.22)/.16)*(1-smooth((point.y-.72)/.12))
        body = capsule_weights(point, ['DM_Pelvis', 'DM_Spine01', 'DM_Spine02', 'DM_Spine03'])
        weights = mix(weights, body, belly)
        tail_mask = central*smooth((point.y-.75)/.07)*(1-smooth((point.z-.90)/.08))
        weights = mix(weights, capsule_weights(point, ['DM_Tail%02d' % i for i in range(1, 5)]), tail_mask)
        side = 'L' if point.x >= 0 else 'R'
        key = ('F' if point.y < .10 else 'R')+side
        plantar = 1-smooth((point.z-.10)/.13)
        weights = mix(weights, {LEGS[key]['bones'][4]: 1.0}, plantar)
        weights = sorted(((w, name) for name, w in weights.items() if w > 1e-8), reverse=True)[:4]
        if not weights:
            raise ValueError('Bone heat left an unbound vertex; manual repair required')
        total = sum(w for w, _ in weights)
        for group in mesh.vertex_groups:
            group.remove([vertex.index])
        for weight, name in weights:
            mesh.vertex_groups[name].add([vertex.index], weight/total, 'REPLACE')
            counts[name] = counts.get(name, 0)+1
    modifier = next(m for m in mesh.modifiers if m.type == 'ARMATURE')
    modifier.use_deform_preserve_volume = False
    return counts


def aim_matrix(name, start, end, twist=0.0):
    definition = DEFS[name]
    rest_dir = (definition['tail']-definition['head']).normalized()
    new_dir = (end-start).normalized()
    rotation = rest_dir.rotation_difference(new_dir)
    if twist:
        rotation = Quaternion(new_dir, twist) @ rotation
    return Matrix.Translation(start) @ rotation.to_matrix().to_4x4() @ REST[name].to_quaternion().to_matrix().to_4x4()


def ik_joint(start, end, length_a, length_b, pole):
    vector = end-start
    distance = vector.length
    if distance >= length_a+length_b:
        # Return a measured unreachable result; do not silently stretch bones.
        end = start + vector.normalized() * (length_a+length_b-1e-6)
        vector, distance = end-start, length_a+length_b-1e-6
    distance = max(distance, abs(length_a-length_b)+1e-6)
    direction = vector.normalized()
    perpendicular = pole-direction*pole.dot(direction)
    if perpendicular.length < 1e-6:
        perpendicular = Vector((1, 0, 0))
    perpendicular.normalize()
    along = (length_a*length_a-length_b*length_b+distance*distance)/(2*distance)
    height = math.sqrt(max(0, length_a*length_a-along*along))
    return start + direction*along + perpendicular*height, end


def clips():
    output = []
    def clip(name, seconds, loop=True, **options):
        output.append(dict(name='DM_EM_'+name, seconds=seconds, frames=round(seconds*FPS)+1,
                           loop=loop, kind=name, **options))
    clip('IdleNeutral', 2)
    clip('IdleBreathing', 4)
    for name, sec, excursion, duty, lift, phases in [
            ('Walk', 1.5, .34, .70, .065, [0, .25, .5, .75]),
            ('Trot', 1, .42, .58, .09, [0, .5, .5, 0]),
            ('Run', .875, .45, .49, .12, [.48, 0, .60, .12]),
            ('Gallop', .75, .47, .42, .14, [.48, 0, .60, .12])]:
        clip(name, sec, gait=True, excursion=excursion, duty=duty, lift=lift, phases=phases)
    for name, turn in [('TurnLeft', .65), ('TurnRight', -.65)]:
        clip(name, 2, False, turn=turn)
    clip('StartMoving', 1.5, False)
    clip('StopMoving', 1.5, False)
    for name, sec, loop in [('Sit', 2.5, False), ('SitIdle', 3, True), ('StandUp', 2.5, False),
                             ('LieDown', 3, False), ('LieIdle', 4, True), ('GetUp', 3, False), ('Sleep', 4, True)]:
        clip(name, sec, loop)
    for name, sec, loop in [('HeadTilt', 2.5, False), ('LookAround', 4, True), ('TailWag', 2, True),
                             ('EarsAlert', 2, False), ('EarsRelaxed', 2, False),
                             ('SniffAir', 3, True), ('SniffObject', 3, True),
                             ('SniffGround', 3, True), ('PettingReaction', 3, False),
                             ('PlayBow', 3, False), ('InjuredIdle', 3, True),
                             ('ExhaustedIdle', 4, True), ('Tremble', 2, True),
                             ('HeadShake', 2, False), ('PainReaction', 2, False)]:
        clip(name, sec, loop)
    for key in LEGS:
        clip('Limp'+key, 1.75, gait=True, excursion=.18, duty=.78, lift=.04,
             phases=[0, .25, .5, .75], affected_limb=key)
    clip('CautiousWalk', 2, gait=True, excursion=.20, duty=.80, lift=.035, phases=[0, .25, .5, .75])
    return output


def motion(spec, frame):
    n = spec['frames']-1
    u = frame/n
    kind = spec['kind']
    t = u*spec['seconds']
    ease = smooth(u)
    pulse = math.sin(math.pi*u)**2
    sit = ease if kind == 'Sit' else 1-ease if kind == 'StandUp' else 1 if kind == 'SitIdle' else 0
    lie = ease if kind == 'LieDown' else 1-ease if kind == 'GetUp' else 1 if kind in ('LieIdle', 'Sleep') else 0
    bow = pulse if kind == 'PlayBow' else 0
    breath = math.sin(TAU*u) * (.003 if kind == 'IdleNeutral' else .006)
    if kind in ('Sit', 'StandUp', 'LieDown', 'GetUp', 'StartMoving', 'StopMoving'):
        breath *= pulse
    yaw = spec.get('turn', 0)*ease
    hip = Vector((0, .43, .88))
    translation = Vector((.004*math.sin(TAU*u), 0, breath))
    if kind in ('Sit', 'StandUp', 'SitIdle'):
        translation += Vector((0, 0, -.47*sit))
    translation.z -= .33*lie
    angle = -.62*sit + .08*lie + .17*bow
    translation.z -= .02*bow
    if spec.get('gait'):
        translation.z -= .012 if kind in ('Walk', 'CautiousWalk') or 'Limp' in kind else .04
        translation.z += (.012 if kind == 'Walk' or 'Limp' in kind or kind == 'CautiousWalk' else .025)*math.sin(2*TAU*u)
        translation.x = .008*math.sin(TAU*u)
    if kind == 'Tremble':
        translation.x += .002*math.sin(8*TAU*u)
    if kind == 'SniffGround':
        angle += .45
        translation.z -= .03
    if kind in ('IdleNeutral', 'IdleBreathing'):
        translation.x = 0
    body = Matrix.Translation(translation) @ Matrix.Rotation(yaw, 4, 'Z') @ Matrix.Translation(hip) @ Matrix.Rotation(angle, 4, 'X') @ Matrix.Translation(-hip)
    poses = {}
    for name, d in DEFS.items():
        if name == 'DM_Root':
            poses[name] = Matrix.Rotation(yaw, 4, 'Z') @ REST[name]
        else:
            poses[name] = body @ REST[name]
    # Stable head/neck, small heavy-body follow-through; no open-jaw fiction.
    pitch = -.22*lie - .04*sit
    head_yaw, roll = 0.0, 0.0
    if kind == 'HeadTilt':
        roll = .16*pulse
    if kind == 'LookAround':
        head_yaw = .20*math.sin(TAU*u)
    if kind == 'HeadShake':
        head_yaw = .24*math.sin(6*math.pi*u)*pulse
    if kind == 'PainReaction':
        pitch -= .13*pulse
        head_yaw = .12*pulse
    if kind in ('SniffAir', 'SniffObject', 'SniffGround'):
        pitch += {'SniffAir': -.13, 'SniffObject': .22, 'SniffGround': .73}[kind]
        pitch += .018*math.sin(6*math.pi*u)
    if kind in ('InjuredIdle', 'ExhaustedIdle'):
        pitch += .13 + .012*math.sin(2*TAU*u)
    if kind == 'PettingReaction':
        roll = -.10*pulse
        pitch -= .08*pulse
    pivot = body @ DEFS['DM_Neck01']['head']
    head_tf = Matrix.Translation(pivot) @ Matrix.Rotation(head_yaw, 4, 'Z') @ Matrix.Rotation(pitch, 4, 'X') @ Matrix.Rotation(roll, 4, 'Y') @ Matrix.Translation(-pivot) @ body
    neck_end = head_tf @ DEFS['DM_Neck01']['tail']
    poses['DM_Neck01'] = aim_matrix('DM_Neck01', body @ DEFS['DM_Neck01']['head'], neck_end)
    for name in ['DM_Neck02', 'DM_Head', 'DM_Jaw', 'DM_Ear.L', 'DM_Ear.R', 'DM_Jowl.L', 'DM_Jowl.R']:
        poses[name] = head_tf @ REST[name]
    for side, sign in [('L', 1), ('R', -1)]:
        for part in ['Ear', 'Jowl']:
            name = 'DM_'+part+'.'+side
            wiggle = .018*math.sin(TAU*u-.35)*pulse
            if part == 'Ear':
                wiggle += sign*(.10*pulse if kind == 'EarsAlert' else -.05*pulse if kind == 'EarsRelaxed' else .012*math.sin(TAU*u))
            p = head_tf @ DEFS[name]['head']
            poses[name] = Matrix.Translation(p) @ Matrix.Rotation(wiggle, 4, 'Y') @ Matrix.Translation(-p) @ poses[name]
    tail_start = body @ DEFS['DM_Tail01']['head']
    for i in range(1, 5):
        name = 'DM_Tail%02d' % i
        amplitude = .20 if kind in ('TailWag', 'PettingReaction') else .025
        wave = amplitude*math.sin((2 if kind == 'TailWag' else 1)*TAU*u-i*.22)
        rest_vector = DEFS[name]['tail']-DEFS[name]['head']
        length = rest_vector.length
        direction = (body.to_3x3() @ rest_vector).normalized()
        direction = direction.lerp(Vector((.20, .95, -.37+.08*i)).normalized(), sit).normalized()
        direction.x += wave
        direction.normalize()
        # Tail joints remain above the review floor; no simulated collision claim.
        minimum_dz = max(-.98, min(.98, (.085-tail_start.z)/length))
        dz = max(direction.z, minimum_dz)
        horizontal = Vector((direction.x, direction.y, 0)).normalized()*math.sqrt(1-dz*dz)
        direction = Vector((horizontal.x, horizontal.y, dz))
        tail_end = tail_start+direction*length
        poses[name] = aim_matrix(name, tail_start, tail_end)
        tail_start = tail_end
    contacts, reach_errors = {}, {}
    for index, (key, leg) in enumerate(LEGS.items()):
        points, bones = leg['points'], leg['bones']
        start = body @ points[0]
        shoulder = body @ points[1]
        foot = points[4].copy()
        foot.y -= .18*lie*(1 if leg['front'] else 0)
        foot.x *= 1 + .15*lie
        if not leg['front']:
            foot.x *= 1+.30*sit
            foot.y -= .24*sit+.10*lie
        z_lift = 0.0
        stance = True
        virtual_speed = 0.0
        if spec.get('gait'):
            duty = spec['duty']
            phase = (u+spec['phases'][index]) % 1
            excursion = spec['excursion']
            virtual_speed = excursion/(duty*spec['seconds'])
            if phase < duty:
                foot.y += excursion*(phase/duty-.5)
            else:
                swing = (phase-duty)/(1-duty)
                foot.y += excursion*(.5-smooth(swing))
                z_lift = spec['lift']*math.sin(math.pi*swing)**2
                stance = False
            if spec.get('affected_limb') == key:
                # Foundation: this exact limb is held clear, never a hidden gameplay restriction.
                z_lift += .035
                stance = False
        elif 'turn' in spec:
            # Slow pivot: each paw alternates a world-pinned stance and an arc step.
            phase = (u*2+[0, .5, .75, .25][index]) % 1
            duty = .65
            touchdown_u = max(0, u-phase/2)
            if phase < duty:
                step_yaw = spec['turn']*smooth(touchdown_u)
            else:
                a = smooth((phase-duty)/(1-duty))
                step_yaw = spec['turn']*((1-a)*smooth(touchdown_u)+a*smooth(min(1, touchdown_u+.5)))
                z_lift = .065*math.sin(math.pi*(phase-duty)/(1-duty))**2
                stance = False
            foot = Matrix.Rotation(step_yaw, 3, 'Z') @ foot
        elif kind in ('StartMoving', 'StopMoving'):
            ramp = ease if kind == 'StartMoving' else 1-ease
            phase = (u+[0, .5, .75, .25][index]) % 1
            foot.y += .12*ramp*math.sin(TAU*phase)
            z_lift = .055*ramp*max(0, math.sin(TAU*phase))
            stance = z_lift < 1e-5
        foot.z += z_lift
        offset = points[3]-points[4]
        if not leg['front']:
            # Fold hocks horizontally alongside the body for seated/resting poses.
            offset = offset.lerp(Vector((0, .17, .08)).normalized()*offset.length, sit)
            offset = offset.lerp(Vector((0, .185, .04)).normalized()*offset.length, lie)
            offset.normalize()
            offset *= (points[3]-points[4]).length
        target = foot+offset
        length_a = (points[2]-points[1]).length
        length_b = (points[3]-points[2]).length
        pole = Vector((0, 1 if leg['front'] else -1, 0))
        pole = Matrix.Rotation(yaw, 3, 'Z') @ pole
        knee, actual_target = ik_joint(shoulder, target, length_a, length_b, pole)
        reach_errors[key] = (actual_target-target).length
        # Refuse stretching. Any unreachable paw is reported by validation.
        foot += actual_target-target
        positions = [start, shoulder, knee, actual_target, foot,
                     foot+Vector((0, -.11 if leg['front'] else -.12, -.02)),
                     foot+Vector((0, -.17, -.025))]
        for i, name in enumerate(bones):
            poses[name] = aim_matrix(name, positions[i], positions[i+1])
        contacts[key] = {'stance': stance, 'paw': list(foot), 'virtual_speed': virtual_speed,
                         'virtual_world_paw': [foot.x, foot.y-virtual_speed*t, foot.z]}
    return poses, contacts, reach_errors


def apply_pose(armature, matrices, frame=None):
    for name, desired in matrices.items():
        parent = DEFS[name]['parent']
        if parent:
            relative_rest = REST[parent].inverted() @ REST[name]
            basis = relative_rest.inverted() @ matrices[parent].inverted() @ desired
        else:
            basis = REST[name].inverted() @ desired
        pb = armature.pose.bones[name]
        loc, rot, scale = basis.decompose()
        pb.location, pb.rotation_quaternion, pb.scale = loc, rot, scale
        if frame is not None:
            pb.keyframe_insert('location', frame=frame, group=name)
            pb.keyframe_insert('rotation_quaternion', frame=frame, group=name)
            pb.keyframe_insert('scale', frame=frame, group=name)


def sockets(armature):
    specs = [
        ('collar', 'Neck01', (0, -.49, 1.08)), ('lead', 'Neck01', (0, -.46, 1.18)),
        ('harness', 'Chest', (0, -.23, 1.07)), ('backpack', 'Spine02', (0, .05, 1.09)),
        ('k9_armor', 'Chest', (0, -.12, 1.07)), ('recovery_harness', 'Spine01', (0, .18, 1.08)),
        ('cone', 'Neck02', (0, -.63, 1.15)), ('head_bandage', 'Head', (0, -.70, 1.28)),
        ('neck_bandage', 'Neck01', (0, -.49, 1.05)), ('torso_dressing', 'Spine02', (0, .05, .91)),
        ('mouth_carry', 'Head', (0, -.94, 1.02))]
    for side, sign in [('L', 1), ('R', -1)]:
        for limb, prefix, y in [('front', 'Forearm', -.37), ('rear', 'Shin', .51)]:
            specs.append((limb+'_wrap.'+side, prefix+'.'+side, (sign*.22, y, .34)))
            specs.append((limb+'_boot.'+side, ('FrontPaw' if limb == 'front' else 'RearPaw')+'.'+side,
                          (sign*.21, -.5 if limb == 'front' else .55, .08)))
    output = []
    for name, bone, position in specs:
        bone = 'DM_'+bone
        local = REST[bone].inverted() @ Vector(position)
        # Explicit constraint to the full bone transform avoids tail-offset parenting.
        empty = bpy.data.objects.new('SOCKET_'+name, None)
        bpy.context.scene.collection.objects.link(empty)
        empty.empty_display_size = .035
        empty.empty_display_type = 'ARROWS'
        empty.matrix_world = Matrix.Translation(position)
        constraint = empty.constraints.new('CHILD_OF')
        constraint.target, constraint.subtarget = armature, bone
        constraint.inverse_matrix = REST[bone].inverted()
        output.append({'name': name, 'bone': bone, 'bone_local_position': list(local),
                       'rest_position': list(position), 'orientation': 'bone frame; equipment fit/clearance must be reviewed',
                       'native_binding': 'NOT IMPLEMENTED',
                       'uses': ['splint', 'cast'] if 'wrap' in name else [name.split('.')[0]]})
    return output


def main():
    skeleton()
    bpy.ops.wm.read_factory_settings(use_empty=True)
    source = SOURCE / 'interchange/english_mastiff.glb'
    if hashlib.sha256(source.read_bytes()).hexdigest() != '37c8e1cc6e47f9ffde22aa93346e8d91f15fb4c3d90843e4cb278e2aab07bd31':
        raise ValueError('Inspected source changed')
    bpy.ops.import_scene.gltf(filepath=str(source))
    mesh = next(o for o in bpy.context.scene.objects if o.type == 'MESH')
    mesh.name = 'EnglishMastiff'
    # Preserve UVs and positions; source GLB has duplicated seam vertices.
    bm = bmesh.new()
    bm.from_mesh(mesh.data)
    bmesh.ops.remove_doubles(bm, verts=list(bm.verts), dist=1e-6)
    bm.to_mesh(mesh.data)
    bm.free()
    floor = min(v.co.z for v in mesh.data.vertices)
    for vertex in mesh.data.vertices:
        vertex.co.z -= floor
    for polygon in mesh.data.polygons:
        polygon.use_smooth = True
    arm_data = bpy.data.armatures.new('DM_LargeMastiff')
    armature = bpy.data.objects.new('DM_LargeMastiff', arm_data)
    bpy.context.scene.collection.objects.link(armature)
    bpy.context.view_layer.objects.active = armature
    armature.select_set(True)
    bpy.ops.object.mode_set(mode='EDIT')
    for name, definition in DEFS.items():
        bone = arm_data.edit_bones.new(name)
        bone.head, bone.tail = definition['head'], definition['tail']
        bone.use_deform = definition['deform']
        if definition['parent']:
            bone.parent = arm_data.edit_bones[definition['parent']]
    bpy.ops.object.mode_set(mode='OBJECT')
    armature.show_in_front = True
    global REST
    REST = {b.name: b.matrix_local.copy() for b in arm_data.bones}
    for pb in armature.pose.bones:
        pb.rotation_mode = 'QUATERNION'
    counts = bind(mesh, armature)
    socket_specs = sockets(armature)
    scene = bpy.context.scene
    scene.render.fps = FPS
    scene.unit_settings.system = 'NONE'
    scene['asset_revision'] = REVISION
    scene['native_compatibility'] = 'INTERMEDIATE; NOT TESTED IN PROJECT ZOMBOID'
    catalog = clips()
    trace = {}
    for spec in catalog:
        armature.animation_data_create()
        action = bpy.data.actions.new(spec['name'])
        armature.animation_data.action = action
        action.use_fake_user = True
        action['loop'] = spec['loop']
        trace[spec['name']] = []
        for frame in range(spec['frames']):
            matrices, contacts, reach = motion(spec, frame)
            apply_pose(armature, matrices, frame+1)
            trace[spec['name']].append({'frame': frame+1, 'feet': contacts, 'reach_error': reach})
        # New action-layer API, no dependence on removed Action.fcurves.
        for layer in action.layers:
            for strip in layer.strips:
                for channelbag in strip.channelbags:
                    for curve in channelbag.fcurves:
                        for key in curve.keyframe_points:
                            key.interpolation = 'LINEAR'
        spec['nominal_virtual_speed_source_units_s'] = spec.get('excursion', 0)/(spec.get('duty', 1)*spec['seconds'])
        spec['root_motion'] = 'in-place translation; yaw only in turn clips; no native speed/stat changes'
        spec['quality'] = 'procedural authoring foundation; deformation/foot contact review required'
        print('Authored', spec['name'], flush=True)
    armature.animation_data.action = bpy.data.actions['DM_EM_IdleBreathing']
    scene.frame_start, scene.frame_end = 1, 97
    scene.frame_set(1)
    for image in bpy.data.images:
        if image.type == 'IMAGE' and image.has_data:
            image.pack()
    (ROOT / 'interchange').mkdir(exist_ok=True)
    (ROOT / 'animations').mkdir(exist_ok=True)
    for obj in scene.objects:
        obj.select_set(obj in (mesh, armature))
    bpy.context.view_layer.objects.active = armature
    blend = ROOT / 'source/english_mastiff_rig.blend'
    bpy.ops.wm.save_as_mainfile(filepath=str(blend))
    bpy.ops.export_scene.gltf(filepath=str(ROOT / 'interchange/english_mastiff_rig.glb'),
                             export_format='GLB', use_selection=True, export_animations=True,
                             export_animation_mode='ACTIONS', export_force_sampling=True,
                             export_frame_range=False, export_def_bones=False)
    # Separate maps for FBX's Principled wrapper; preserve the source GLB material.
    mat = mesh.data.materials[0].copy()
    mesh.data.materials[0] = mat
    shader = next(n for n in mat.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
    for socket, filename in [('Roughness', 'roughness.png'), ('Metallic', 'metallic.png')]:
        image = bpy.data.images.load(str(SOURCE / 'source/meshy_textured_textures' / filename))
        image.colorspace_settings.name = 'Non-Color'
        node = mat.node_tree.nodes.new('ShaderNodeTexImage')
        node.image = image
        mat.node_tree.links.new(node.outputs['Color'], shader.inputs[socket])
    bpy.ops.export_scene.fbx(filepath=str(ROOT / 'interchange/english_mastiff_rig.fbx'),
                            use_selection=True, object_types={'MESH', 'ARMATURE'},
                            add_leaf_bones=False, use_armature_deform_only=False,
                            bake_anim=True, bake_anim_use_all_actions=True, bake_anim_use_nla_strips=False,
                            bake_anim_simplify_factor=0, path_mode='COPY', embed_textures=True)
    for spec in catalog:
        armature.animation_data.action = bpy.data.actions[spec['name']]
        scene.name = spec['name']  # Single-take FBX names its take after the scene.
        scene.frame_start, scene.frame_end = 1, spec['frames']
        mesh.select_set(False)
        bpy.ops.export_scene.fbx(filepath=str(ROOT / 'animations' / (spec['name']+'.fbx')),
                                use_selection=True, object_types={'ARMATURE'}, add_leaf_bones=False,
                                bake_anim=True, bake_anim_use_all_actions=False,
                                bake_anim_use_nla_strips=False, bake_anim_simplify_factor=0)
    write_json(ROOT / 'metadata/rig.json', {
        'asset_revision': REVISION, 'tested_project_version': '0.2.0-dev.7',
        'toolchain': 'Windows standalone Blender-Python '+bpy.app.version_string,
        'additional_credits': 0, 'source': '../english_mastiff/interchange/english_mastiff.glb',
        'source_sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
        'coordinate_system': '+X animal-left; -Y forward; +Z up; original units, not calibrated metres',
        'source_translation_z': -floor, 'scale_factor': 1,
        'bone_count': len(DEFS), 'weighted_bones': counts, 'max_influences': 4,
        'skin_method': 'Blender bone-heat weights with smooth underside/tail isolation and plantar rigidity corrections; top-four normalized, linear skinning; editable starting weights requiring deformation review',
        'jaw': 'reserved non-deforming bone; source closed mouth has no oral cavity/tongue/teeth. Bark/pant/eating must wait for approved topology work.',
        'bones': [{'name': n, **{k: list(v) if k in ('head', 'tail') else v for k, v in d.items()}}
                  for n, d in DEFS.items()],
        'native': 'INTERMEDIATE; hierarchy/bind pose not native-compatible proof; not registered',
    })
    write_json(ROOT / 'metadata/clips.json', {'fps': FPS, 'clips': catalog})
    write_json(ROOT / 'metadata/attachments.json', {'sockets': socket_specs, 'export_policy': 'Authoring empties live in BLEND; portable definitions are this JSON, no native API assumed.'})
    write_json(ROOT / 'validation/contact_reference.json', trace)
    print(json.dumps({'bones': len(DEFS), 'clips': len(catalog), 'vertices': len(mesh.data.vertices),
                      'source_translation_z': -floor, 'additional_credits': 0}), flush=True)


if __name__ == '__main__':
    main()
