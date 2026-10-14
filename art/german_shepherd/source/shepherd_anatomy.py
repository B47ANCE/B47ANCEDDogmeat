"""Original v002 canine proportions, facial construction and ear shells.

All dimensions are original authoring choices in metres; no imported geometry.
"""
import math
import numpy as np
import bpy
from mathutils import Vector


def build(g):
    t, e = g.tube, g.ellipsoid
    # Thorax: broad deep front rib cage, narrowing and lifting toward the flank.
    t('Thorax', [((-.395,0,.475),.012,.023),((-.35,0,.475),.086,.106),
      ((-.27,0,.475),.106,.120),((-.16,0,.481),.102,.116),
      ((-.045,0,.472),.123,.153),((.08,0,.465),.145,.174),
      ((.19,0,.473),.138,.184),((.27,0,.478),.117,.178),
      ((.32,0,.470),.078,.134),((.35,0,.46),.015,.042)],32)
    t('Ruff', [((.18,0,.478),.133,.171),((.235,0,.565),.124,.148),
      ((.29,0,.635),.113,.129),((.34,0,.699),.099,.116),
      ((.39,0,.754),.085,.098),((.432,0,.79),.070,.063)],32)
    # Cranium and cheek arc are deliberately taller/broader than the v001 loft.
    t('Cranium', [((.345,0,.780),.045,.065),((.39,0,.797),.082,.087),
      ((.445,0,.801),.095,.087),((.493,0,.792),.082,.075),
      ((.53,0,.768),.061,.052),((.56,0,.751),.050,.035)],32)
    t('MuzzleBridge', [((.502,0,.756),.066,.049),((.546,0,.756),.061,.045),
      ((.586,0,.750),.054,.040),((.625,0,.743),.048,.034),
      ((.663,0,.736),.041,.029),((.681,0,.734),.029,.021)],28)
    for side,sgn in [('L',1),('R',-1)]:
        e('Cheek_'+side,(.453,sgn*.054,.766),(.056,.027,.041),part=True,segments=24,rings=16)
        e('Brow_'+side,(.498,sgn*.058,.821),(.037,.022,.014),part=True,segments=24,rings=12)
        # Scapula sits within the chest volume, not an isolated shoulder sphere.
        t('Scapula_'+side,[((.19,sgn*.083,.610),.043,.055),
          ((.23,sgn*.106,.515),.047,.072),((.20,sgn*.113,.412),.044,.060)],24)
        y=sgn*.112
        t('Foreleg_'+side,[((.237,y,.476),.045,.054),((.20,y,.370),.035,.041),
          ((.205,y,.322),.033,.037),((.222,y,.235),.028,.031),
          ((.235,y,.144),.024,.027),((.235,y,.095),.026,.030),
          ((.245,y,.062),.021,.025),((.264,y,.038),.029,.031)],24)
        e('FrontPad_'+side,(.275,y,.036),(.048,.036,.031),part=True,segments=24,rings=16)
        for toe in range(4):
            dy=(toe-1.5)*.019
            forward=.009 if toe in (1,2) else 0
            e('FrontToe_'+side+str(toe),(.309+forward,y+dy,.026),(.026,.012,.022),part=True,segments=16,rings=12)
        y=sgn*.108
        e('Haunch_'+side,(-.285,sgn*.065,.459),(.083,.050,.113),part=True,segments=24,rings=16)
        t('Hindleg_'+side,[((-.31,y,.487),.043,.067),((-.284,y,.407),.054,.074),
          ((-.237,y,.337),.047,.057),((-.214,y,.295),.035,.038),
          ((-.265,y,.237),.029,.034),((-.325,y,.171),.025,.027),
          ((-.342,y,.134),.025,.024),((-.332,y,.072),.019,.021),
          ((-.318,y,.037),.029,.028)],24)
        e('RearPad_'+side,(-.295,y,.033),(.048,.034,.029),part=True,segments=24,rings=16)
        for toe in range(4):
            dy=(toe-1.5)*.018
            forward=.008 if toe in (1,2) else 0
            e('RearToe_'+side+str(toe),(-.263+forward,y+dy,.024),(.025,.0115,.021),part=True,segments=16,rings=12)
    # Bushy tail falls smoothly from the croup; no sharp hook.
    t('Tail',[((-.363,0,.498),.033,.039),((-.433,.008,.451),.041,.046),
      ((-.502,.018,.377),.044,.052),((-.579,.031,.300),.043,.053),
      ((-.652,.041,.254),.037,.047),((-.719,.049,.245),.026,.033),
      ((-.764,.053,.259),.013,.018),((-.788,.055,.276),.002,.003)],28)
    for side,sgn in [('L',1),('R',-1)]:
        # Closed, curved ear shell with a recessed front bowl and broad base.
        rows,cols=18,16
        verts=[]
        for back in (False,True):
            for j in range(rows):
                u=j/(rows-1)
                width=(.053*(1-u)**.72+.003)*(.88+.12*math.sin(math.pi*u))
                for k in range(cols):
                    v=-1+2*k/(cols-1)
                    cy=sgn*(.063+.026*u)
                    x=.444-.035*u + .021*v*v*(1-u)-.010*math.sin(math.pi*u)
                    if back: x-=.010+.012*(1-v*v)*(1-u)
                    z=.839+.188*u+.005*(1-v*v)*math.sin(math.pi*u)
                    verts.append((x,cy+width*v,z))
        faces=[];n=rows*cols
        for j in range(rows-1):
            for k in range(cols-1):
                a=j*cols+k
                faces.extend([(a,a+1,a+1+cols,a+cols),(n+a+cols,n+a+cols+1,n+a+1,n+a)])
        for j in range(rows-1):
            a=j*cols; b=j*cols+cols-1
            faces.extend([(a,a+cols,n+a+cols,n+a),(b,n+b,n+b+cols,b+cols)])
        for k in range(cols-1):
            a=k;b=(rows-1)*cols+k
            faces.extend([(a,n+a,n+a+1,a+1),(b,b+1,n+b+1,n+b)])
        g.mesh_obj('Ear_'+side,verts,faces,part=True)
    g.select(g.PARTS);bpy.ops.object.join();dog=bpy.context.object;dog.name='GSD_CoatBody'
    bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.normals_make_consistent(inside=False);bpy.ops.object.mode_set(mode='OBJECT')
    dog.data.remesh_voxel_size=.0022;bpy.ops.object.voxel_remesh()
    m=dog.modifiers.new('AnatomyRelax','SMOOTH');m.factor=.72;m.iterations=14;g.apply(dog,m)
    tri=sum(len(p.vertices)-2 for p in dog.data.polygons)
    m=dog.modifiers.new('AuthoringSurface','DECIMATE');m.ratio=min(1,24000/tri);g.apply(dog,m)
    m=dog.modifiers.new('Triangles','TRIANGULATE');g.apply(dog,m)
    for p in dog.data.polygons:p.use_smooth=True
    dog['asset_revision']=g.REVISION;g.MODEL.append(dog)
    return dog


def details(g):
    dark=g.material('GSD_Lips',(.065,.052,.049),.57)
    nose=g.material('GSD_NoseLeather',(.020,.022,.024),.72)
    inner=g.material('GSD_EarSkin',(.31,.205,.172),.87)
    mouth=g.material('GSD_OralCavity',(.095,.027,.032),.72)
    gum=g.material('GSD_Gum',(.26,.113,.115),.55)
    tongue=g.material('GSD_Tongue',(.64,.29,.34),.46)
    enamel=g.material('GSD_Teeth',(.83,.79,.66),.38)
    amber=g.material('GSD_Iris',(.30,.16,.050),.23)
    black=g.material('GSD_Pupil',(.008,.009,.009),.13)
    claw=g.material('GSD_Claw',(.16,.135,.113),.49)
    jawcoat=g.material('GSD_JawCoat',(.17,.14,.12),.86)
    # Portable standard material; no unexported procedural nose shader.
    def ell(name,center,radius,mat,domain='head',seg=24,rings=16):
        o=g.ellipsoid('GSD_'+name,center,radius,mat,segments=seg,rings=rings)
        o['rig_domain']=domain;g.MODEL.append(o);return o
    def line(name,pts,r,mat,domain='head'):
        o=g.curve_mesh('GSD_'+name,pts,r,mat);o['rig_domain']=domain;g.MODEL.append(o);return o
    jaw=g.tube('GSD_LowerJaw',[((.477,0,.721),.041,.024),((.528,0,.694),.038,.012),
      ((.581,0,.687),.032,.010),((.634,0,.692),.026,.009),((.659,0,.700),.021,.008)],24,False)
    jaw.data.materials.append(jawcoat);jaw['rig_domain']='jaw';g.MODEL.append(jaw)
    ell('MouthInterior',(.559,0,.715),(.077,.028,.016),mouth)
    tong=g.tube('GSD_TongueTip',[((.567,0,.703),.010,.003),((.605,0,.702),.018,.004),
      ((.639,0,.704),.020,.004),((.659,0,.702),.020,.004),((.675,0,.691),.018,.005),
      ((.682,0,.683),.012,.004),((.682,0,.680),.003,.002)],24,False)
    tong.data.materials.append(tongue);tong['rig_domain']='jaw';g.MODEL.append(tong)
    # Nose is a beveled broad triangular pad, not a sphere.
    outline=[(-.033,.012),(-.025,.023),(.025,.023),(.033,.012),(.027,-.008),(0,-.018),(-.027,-.008)]
    verts=[(x,y,.738+z) for x in (.670,.695) for y,z in outline]
    n=len(outline);faces=[tuple(reversed(range(n))),tuple(range(n,2*n))]
    faces += [(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
    o=g.mesh_obj('GSD_Nose',verts,faces);o.data.materials.append(nose)
    m=o.modifiers.new('NoseSoftEdges','BEVEL');m.width=.006;m.segments=3;g.apply(o,m)
    o['rig_domain']='head';g.MODEL.append(o)
    line('Philtrum',[(.698,0,.735),(.699,0,.725),(.688,0,.718)],.0011,black)
    for side,sgn in [('L',1),('R',-1)]:
        ell('Nostril_'+side,(.692,sgn*.024,.745),(.008,.007,.0045),black)
        line('NostrilWing_'+side,[(.694,sgn*.031,.739),(.698,sgn*.030,.749),(.691,sgn*.021,.752)],.0007,nose)
        # Iris and pupil seated in a curved dark globe, with anatomical lid rims.
        center=Vector((.518,sgn*.060,.801));normal=Vector((.43,sgn*.90,.02)).normalized()
        globe=ell('Eye_'+side,tuple(center),(.014,.011,.010),black)
        ir=ell('Iris_'+side,tuple(center+normal*.009),(.007,.0025,.007),amber)
        pu=ell('Pupil_'+side,tuple(center+normal*.0108),(.0035,.0015,.0045),black)
        for o in (ir,pu):
            # Ellipsoids currently identity; rotate local vertices around center.
            angle=-sgn*.43; c=Vector(center+normal*(.009 if o is ir else .0108))
            from mathutils import Matrix
            rot=Matrix.Rotation(angle,3,'Z')
            for v in o.data.vertices:v.co=c+rot@(v.co-c)
        upper=[(.502,sgn*.065,.800),(.512,sgn*.071,.810),(.524,sgn*.071,.809),(.535,sgn*.064,.803)]
        lower=[(.502,sgn*.065,.800),(.513,sgn*.071,.795),(.526,sgn*.068,.796),(.535,sgn*.064,.803)]
        line('UpperLid_'+side,upper,.0010,dark);line('LowerLid_'+side,lower,.0007,dark)
        line('UpperLip_'+side,[(.677,sgn*.030,.716),(.636,sgn*.043,.711),(.586,sgn*.051,.714),(.536,sgn*.054,.730),(.502,sgn*.048,.744)],.0028,dark)
        line('LowerLip_'+side,[(.659,sgn*.021,.706),(.621,sgn*.029,.703),(.568,sgn*.037,.701),(.520,sgn*.039,.713)],.0018,dark,'jaw')
        line('UpperGum_'+side,[(.646,sgn*.030,.711),(.607,sgn*.039,.711),(.558,sgn*.045,.719)],.0035,gum)
        for j,x in enumerate([.636,.622,.604,.579,.563]):
            y=sgn*(.033+(.64-x)*.15)
            length=.012 if j==2 else .005
            # Tapered teeth grow downward from upper gum; lower teeth upward.
            tooth=g.tube('GSD_UpperTooth_'+side+str(j),[((x,y,.716),.0035,.004),((x+.002,y,.714-length*.65),.0025,.0028),((x+.003,y,.714-length),.0005,.0005)],10,False)
            tooth.data.materials.append(enamel);tooth['rig_domain']='head';g.MODEL.append(tooth)
            if j!=2:ell('LowerTooth_'+side+str(j),(x-.005,y*.85,.704),(.0025,.002,.003),enamel,'jaw',12,8)
        # Inset follows the cupped shell. It stays inside the dark outer rim.
        verts=[];faces=[];rows,cols=13,12
        for j in range(rows):
            u=.12+.75*j/(rows-1);w=.040*(1-u)**.72
            for k in range(cols):
                v=-1+2*k/(cols-1)
                x=.445-.035*u+.021*(v*.82)**2*(1-u)-.010*math.sin(math.pi*u)+.0018
                verts.append((x,sgn*(.063+.026*u)+w*v,.839+.188*u+.005*(1-(v*.82)**2)*math.sin(math.pi*u)))
        for j in range(rows-1):
            for k in range(cols-1):
                a=j*cols+k;faces.append((a,a+1,a+1+cols,a+cols))
        o=g.mesh_obj('GSD_EarInset_'+side,verts,faces);o.data.materials.append(inner)
        o['rig_domain']='ear_'+side;g.MODEL.append(o)
        for front,x,y in [(True,.309,sgn*.112),(False,-.263,sgn*.108)]:
            domain=('front_foot_' if front else 'rear_foot_')+side
            for toe in range(4):
                yy=y+(toe-1.5)*(.019 if front else .018)
                xx=x+(.009 if toe in(1,2)else 0)
                line('Claw_'+domain+str(toe),[(xx+.018,yy,.027),(xx+.025,yy,.019),(xx+.028,yy,.011)],.0032,claw,domain)
    return jaw


def refine_proportions(g,rig):
    """Shorter neck, wider skull, softer pelvis, matched rest skeleton.

    Applied to mesh and rest bones after binding; no undeclared object scaling.
    """
    def warp(p):
        x,y,z=p
        high=max(0,min(1,(z-.60)/.15))
        head=max(0,min(1,(x-.33)/.12))*max(0,min(1,(z-.65)/.1))
        # Bring skull back and down while keeping four planted paws fixed.
        xx=x-.040*high
        zz=z-.057*high
        yy=y*(1+.24*head)
        # A larger cranial wedge and a shorter, deeper muzzle avoid the pin head.
        xx=.455+(xx-.455)*(1+.25*head)
        zz=.728+(zz-.728)*(1+.25*head)
        if xx>.535:xx=.535+(xx-.535)*.72
        if zz>.86:zz=.86+(zz-.86)*.85
        # Withers connect the high neck to the thoracic wedge.
        zz+=.026*math.exp(-((x-.13)/.18)**2-((z-.64)/.075)**2)
        # Lift abdominal tuck and blend the rear ball into the pelvis.
        zz+=.065*math.exp(-((x+.15)/.16)**2-((z-.35)/.08)**2)
        return (xx,yy,zz)
    for obj in g.MODEL:
        for v in obj.data.vertices:v.co=warp(v.co)
        obj.data.update()
    g.select([rig]);bpy.ops.object.mode_set(mode='EDIT')
    for bone in rig.data.edit_bones:
        bone.head=warp(bone.head);bone.tail=warp(bone.tail)
    bpy.ops.object.mode_set(mode='OBJECT')
