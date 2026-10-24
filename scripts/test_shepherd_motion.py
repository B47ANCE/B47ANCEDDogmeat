"""Independent text/graph regressions for exported original clips; not game playback."""
import hashlib,json,math,re,unittest
from pathlib import Path
import xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parents[1]
MOTION=ROOT/'art/german_shepherd_motion'

def read_clip(path):
    text=path.read_text(encoding='utf-8')
    name=re.search(r'AnimationSet\s+(\w+)\s*\{',text)[1]
    fps=int(re.search(r'AnimTicksPerSecond\s*\{\s*(\d+);',text)[1])
    bones={}
    for block in re.split(r'\bAnimation\s*\{\s*\{\s*',text)[1:]:
        bone=block.split('}',1)[0].strip();tracks={}
        for match in re.finditer(r'AnimationKey\s+K\d\s*\{\s*(\d+);\s*(\d+);([^}]+)\}',block):
            keys=[(int(k[1]),tuple(float(v) for v in k[2].split(','))) for k in re.finditer(r'(\d+);\d+;([^;]+);;',match[3])]
            assert len(keys)==int(match[2]);tracks[int(match[1])]=keys
        bones[bone]=tracks
    return name,fps,bones

class Motion(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report=json.loads((MOTION/'validation/motion.json').read_text())
        cls.clips={p.stem:read_clip(p) for p in (MOTION/'anims').glob('*.x')}
        cls.xmls=list((ROOT/'src/assets/AnimSets/b47germanshepherd').rglob('*.xml'))
    def test_complete_original_clips(self):
        self.assertEqual(len(self.clips),31)
        for name,(clip,fps,bones) in self.clips.items():
            self.assertEqual(clip,name);self.assertEqual(fps,30);self.assertEqual(len(bones),34)
            self.assertEqual(hashlib.sha256((MOTION/'anims'/(name+'.x')).read_bytes()).hexdigest(),self.report['clips'][name]['sha256'])
            for bone,tracks in bones.items():
                self.assertEqual(set(tracks),{0,1,2})
                self.assertEqual(len(tracks[0]),self.report['clips'][name]['frames'])
                for key,(time,scale) in enumerate(tracks[1]):self.assertEqual(scale,(1,1,1));self.assertEqual(time,key)
                for _,quat in tracks[0]:self.assertAlmostEqual(sum(x*x for x in quat),1,places=5)
                for keys in tracks.values():self.assertTrue(all(math.isfinite(v) for _,values in keys for v in values))
    def test_health_changes_only_tail(self):
        tail={'Bip01_Tail','Bip01_Tail1','Bip01_Tail2','Bip01_TailNub'}
        for kind in ('Idle','Look','Walk','Run'):
            low=self.clips['B47Dogmeat_'+kind+'_Low'][2];high=self.clips['B47Dogmeat_'+kind+'_High'][2]
            for suffix in ('H25','H50','H75','High'):
                other=self.clips['B47Dogmeat_'+kind+'_'+suffix][2]
                for bone in low:
                    if bone not in tail:self.assertEqual(low[bone],other[bone],(kind,bone,suffix))
            self.assertNotEqual(low['Bip01_Tail'],high['Bip01_Tail'])
    def test_loop_closure_and_constant_motion_root(self):
        loops=('Idle','Look','Walk','Run','Lie','Dead')
        for name,(_,_,bones) in self.clips.items():
            root=bones['Translation_Data']
            for keys in root.values():
                for _,value in keys:self.assertEqual(value,keys[0][1])
            if any(name.startswith('B47Dogmeat_'+kind+'_') for kind in loops):
                for bone,tracks in bones.items():
                    for kind,keys in tracks.items():
                        a,b=keys[0][1],keys[-1][1]
                        if kind==0:self.assertAlmostEqual(abs(sum(x*y for x,y in zip(a,b))),1,places=5)
                        else:self.assertLess(max(abs(x-y) for x,y in zip(a,b)),1e-5,(name,bone))
    def test_immutable_geometry_and_bounded_gait(self):
        baseline=json.loads((ROOT/'art/german_shepherd_native/validation/native-bind.json').read_text())
        for v in baseline['variants'].values():self.assertEqual(self.report['mesh_geometry_uv_untouched'][v['model']],v['geometry_uv_bound_sha256'])
        self.assertLess(self.report['max_bone_length_error'],1e-5)
        self.assertLess(self.report['max_stance_target_error'],1e-5)
        self.assertFalse(self.report['native_motion_tracks_read'])
    def test_graph_uses_only_our_clips_and_expected_states(self):
        self.assertEqual(len(self.xmls),17)
        self.assertEqual({p.parent.name for p in self.xmls},{'idle','walk','followwall','pathfind','eating','hitreaction','death','falldown','deadbody','onground'})
        for p in self.xmls:
            node=ET.parse(p).getroot()
            for clip in node.iter('m_AnimName'):self.assertIn(clip.text,self.clips)
            self.assertEqual(node.findtext('m_useDeferredMovement'),'false')
    def test_neutral_sentinel_and_health_blend_triangles(self):
        for path in self.xmls:
            node=ET.parse(path).getroot();blends=node.findall('m_2DBlends')
            if not blends:continue
            self.assertEqual(node.findtext('m_Scalar'),'B47DogmeatHealth');self.assertIsNone(node.find('m_Scalar2'))
            points={b.attrib['referenceID']:(float(b.findtext('m_XPos')),float(b.findtext('m_YPos'))) for b in blends}
            self.assertEqual(points,{'1':(0,0),'2':(1,0),'3':(1.25,0),'4':(1.5,0),'5':(1.75,0),'6':(2,0),'7':(1.5,1)})
            for tri in node.findall('m_2DBlendTri'):
                a,b,c=[points[tri.findtext(n)] for n in ('node1','node2','node3')]
                self.assertGreater((b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0]),0)
            self.assertEqual(node.findtext('m_SyncTrackingEnabled'),'true')
            self.assertTrue(blends[0].findtext('m_AnimName').endswith('_Neutral'))
    def test_terminal_states_suspend_health(self):
        for path in self.xmls:
            node=ET.parse(path).getroot()
            if path.parent.name in {'death','falldown','deadbody','onground','hitreaction','eating'} or node.findtext('m_Name')=='idleSit':
                self.assertIsNone(node.find('m_Scalar'))
    def test_climbing_is_disabled_for_own_definitions(self):
        source=(ROOT/'src/bootstrap/shared/B47ShepherdRegistration.lua').read_text()
        self.assertIn('definition.canClimbFences=false',source)
        self.assertIn('definition.animset="b47germanshepherd"',source)
    def test_dead_is_static(self):
        bones=self.clips['B47Dogmeat_Dead_Neutral'][2]
        for tracks in bones.values():
            for keys in tracks.values():
                for _,value in keys:self.assertEqual(value,keys[0][1])
    def test_own_actiongroup_resolves_all_transitions(self):
        folder=ROOT/'src/assets/actiongroups/b47germanshepherd'
        states={p.name for p in folder.iterdir() if p.is_dir()}
        self.assertEqual(ET.parse(folder/'actionGroup.xml').getroot().findtext('initial'),'idle')
        self.assertNotIn('climbfence',states)
        self.assertEqual(states,{p.parent.name for p in self.xmls})
        for p in folder.rglob('transitions.xml'):
            targets=[target.text for target in ET.parse(p).getroot().iter('transitionTo')]
            for target in targets:self.assertIn(target,states)
            self.assertEqual(targets,sorted(targets),'Preserve native equal-specificity transition precedence')
        end=ET.parse(folder/'falldown/transitions.xml').getroot()
        self.assertEqual(end.findtext('transition/conditions/eventOccurred'),'ActiveAnimFinishing')
    def test_native_followwall_and_falldown_contracts(self):
        base=ROOT/'src/assets/AnimSets/b47germanshepherd'
        for path in (base/'followwall').glob('*.xml'):
            conditions=ET.parse(path).getroot().findall('m_Conditions')
            self.assertTrue(any(c.findtext('m_Name')=='bMoving' and c.findtext('m_Value')=='true' for c in conditions))
        events=ET.parse(base/'falldown/falldown.xml').getroot().findall('m_Events')
        self.assertEqual([(e.findtext('m_EventName'),e.findtext('m_ParameterValue')) for e in events],[('PlayDeathSound',''),('PlayBreedSound','fallover')])

if __name__=='__main__':unittest.main()
