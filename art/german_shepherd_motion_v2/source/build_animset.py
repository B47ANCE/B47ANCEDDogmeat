"""Write our own Shepherd graph against observed native state/event contracts."""
from pathlib import Path
import xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parents[3]
OUT=ROOT/'src/assets/AnimSets/b47germanshepherd'

def field(parent,name,value):
    return ET.SubElement(parent,name).__setattr__('text',str(value))

def node(state,name,clip,conditions=(),health=False,loop=True,transitions=(),events=()):
    root=ET.Element('animNode');field(root,'m_Name',name)
    field(root,'m_AnimName','B47Dogmeat_'+clip+'_Neutral')
    field(root,'m_BlendTime',.2);field(root,'m_SpeedScale',1)
    field(root,'m_Looped',str(loop).lower());field(root,'m_SyncTrackingEnabled','true')
    # Constant Translation_Data leaves native animal navigation in control.
    field(root,'m_useDeferredMovement','false')
    if health:
        field(root,'m_Scalar','B47DogmeatHealth')
        for index,(suffix,x,y) in enumerate([('Neutral',0,0),('Low',1,0),('H125',1.125,0),('H25',1.25,0),('H375',1.375,0),('H50',1.5,0),('H625',1.625,0),('H75',1.75,0),('H875',1.875,0),('High',2,0),('Neutral',1.5,1)],1):
            blend=ET.SubElement(root,'m_2DBlends',referenceID=str(index))
            field(blend,'m_AnimName','B47Dogmeat_'+clip+'_'+suffix);field(blend,'m_XPos',x);field(blend,'m_YPos',y);field(blend,'m_SpeedScale',1)
        for a,b,c in [(i,i+1,11) for i in range(1,10)]:
            tri=ET.SubElement(root,'m_2DBlendTri')
            for key,value in [('node1',a),('node2',b),('node3',c)]:field(tri,key,value)
    for variable,kind,value in conditions:
        condition=ET.SubElement(root,'m_Conditions')
        for key,val in [('m_Name',variable),('m_Type',kind),('m_Value',value)]:field(condition,key,val)
    for target,transition in transitions:
        entry=ET.SubElement(root,'m_Transitions');field(entry,'m_Target',target);field(entry,'m_AnimName','B47Dogmeat_'+transition+'_Neutral')
        field(entry,'m_blendInTime',.15);field(entry,'m_blendOutTime',.15)
    for event,time,parameter in events:
        entry=ET.SubElement(root,'m_Events');field(entry,'m_EventName',event)
        field(entry,'m_TimePc' if isinstance(time,float) else 'm_Time',time);field(entry,'m_ParameterValue',parameter)
    ET.indent(root,space='  ');folder=OUT/state;folder.mkdir(parents=True,exist_ok=True)
    (folder/(name+'.xml')).write_bytes(ET.tostring(root,encoding='utf-8',xml_declaration=True)+b'\n')

def build():
    sit=[('idleSit','LieDown')]
    node('idle','idle','Idle',health=True,transitions=sit)
    node('idle','idle2','Look',[('idleAction','STRING','idle1')],health=True,transitions=sit)
    node('idle','idle3','Look',[('idleAction','STRING','idle2')],health=True,transitions=sit)
    node('idle','idleSit','Lie',[('idleAction','STRING','sit')],transitions=[('idle','GetUp'),('idle2','GetUp'),('idle3','GetUp')])
    footsteps=[('PlayBreedSound',.25,'walkFront'),('PlayBreedSound',.75,'walkBack')]
    for state in ('walk','followwall'):
        moving=[('bMoving','BOOL','true')] if state=='followwall' else []
        node(state,'defaultWalk','Walk',moving,health=True,events=footsteps)
        node(state,'run','Run',moving+[('animalRunning','BOOL','true')],health=True)
    node('pathfind','defaultPathfind','Walk',[('bMoving','BOOL','true')],health=True,events=footsteps)
    node('pathfind','runPathfind','Run',[('bMoving','BOOL','true'),('animalRunning','BOOL','true')],health=True)
    node('pathfind','pathfindWait','Idle',[('bMoving','BOOL','false')],health=True)
    node('eating','eating','Eat',[('idleAction','STRING','eat')],loop=False,events=[('idleActionEnd','End','')])
    node('hitreaction','hitreaction1','Hit',loop=False,events=[('PlayBreedSound','Start','pain')])
    node('death','death','Death',loop=False)
    node('falldown','falldown','Death',loop=False,events=[('PlayDeathSound','Start',''),('PlayBreedSound',.35,'fallover')])
    node('deadbody','deadbody','Dead')
    node('onground','onground','Dead')
    print('Wrote 17 original Shepherd animation nodes; native raccoon files untouched')
    build_actiongroup()

def build_actiongroup():
    """Independent graph retaining observed native raccoon state/event contracts.

    No state controller, task authority, or vanilla group file is replaced.
    """
    folder=ROOT/'src/assets/actiongroups/b47germanshepherd';folder.mkdir(parents=True,exist_ok=True)
    group=ET.Element('actiongroup');field(group,'initial','idle')
    (folder/'actionGroup.xml').write_bytes(ET.tostring(group,encoding='utf-8',xml_declaration=True)+b'\n')
    common=[('hitreaction',[('isTrue','hashitreaction')]),
            ('falldown',[('isTrue','bDead'),('isFalse','bOnFloor')]),
            ('onground',[('isTrue','bDead'),('isTrue','bOnFloor')]),
            ('eating',[('isTrue','isAnimalEating')]),
            ('walk',[('isTrue','bMoving'),('isFalse','bPathfind')]),
            ('pathfind',[('isTrue','bPathfind')])]
    states={state:list(common) for state in ('idle','walk','pathfind','eating','hitreaction')}
    states['walk'].append(('idle',[('isFalse','bMoving')]))
    states['pathfind'] += [('idle',[('isFalse','bPathfind')]),('followwall',[('isTrue','shouldFollowWall')])]
    states['eating'].append(('idle',[('isFalse','isAnimalEating')]))
    states['hitreaction'].append(('idle',[('eventOccurred','ActiveAnimFinishing')]))
    states['followwall']=[('idle',[('isFalse','bMoving')]),('idle',[('isFalse','shouldFollowWall')]),
                         common[0],common[1]]
    states['falldown']=[('onground',[('eventOccurred','ActiveAnimFinishing')])]
    states['onground']=[];states['death']=[];states['deadbody']=[]
    for state,transitions in states.items():
        path=folder/state;path.mkdir(parents=True,exist_ok=True)
        (path/'state.xml').write_bytes(b'<ActionState />\n')
        root=ET.Element('transitions')
        # Native files are read by destination name before stable specificity
        # sorting. Preserve that precedence for equally specific conditions.
        for target,conditions in sorted(transitions,key=lambda row:row[0]):
            if target==state:continue
            transition=ET.SubElement(root,'transition');field(transition,'transitionTo',target)
            condition_root=ET.SubElement(transition,'conditions')
            for name,value in conditions:field(condition_root,name,value)
        ET.indent(root,space='  ')
        (path/'transitions.xml').write_bytes(ET.tostring(root,encoding='utf-8',xml_declaration=True)+b'\n')
    print('Wrote own actiongroup; climbing omitted and disabled in own animal definitions')

if __name__=='__main__':build()
