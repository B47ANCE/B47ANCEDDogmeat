"""Offline publication regressions: drift rejection and hostile archive/content cases."""
from pathlib import Path
import io, json, sys, tempfile, unittest, zipfile
from unittest.mock import patch
from audit_publication_target import review_input, sha
from prepare_workshop import verify_archive, payload, configuration, build, PREFIX


class EvidenceTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name);self.path='zombie/Test.class'
        (self.root/'zombie').mkdir();(self.root/self.path).write_bytes(b'known override')
        data=io.BytesIO()
        with zipfile.ZipFile(data,'w') as archive: archive.writestr(self.path,b'vanilla')
        self.archive=zipfile.ZipFile(io.BytesIO(data.getvalue()));self.addCleanup(self.archive.close)
        self.observed={self.path:{'current_loose_sha256':sha(b'known override'),'packaged_sha256':sha(b'vanilla')}}
        self.item={'path':self.path,'container':'game-root','sha256':sha(b'old historical override')}

    def test_historical_drift_is_environment_only(self):
        self.assertEqual(review_input(self.item,self.archive,self.root,self.observed),'known_modified_environment')

    def test_unrecorded_override_refused(self):
        with self.assertRaisesRegex(ValueError,'Unreviewed'): review_input(self.item,self.archive,self.root,{})

    def test_new_override_change_refused(self):
        (self.root/self.path).write_bytes(b'new drift')
        with self.assertRaisesRegex(ValueError,'Unreviewed'): review_input(self.item,self.archive,self.root,self.observed)

    def test_changed_packaged_counterpart_refused(self):
        self.observed[self.path]['packaged_sha256']=sha(b'different vanilla')
        with self.assertRaisesRegex(ValueError,'counterpart'): review_input(self.item,self.archive,self.root,self.observed)

    def test_changed_vanilla_source_refused(self):
        self.item.update(path='vanilla.lua',sha256=sha(b'old'))
        (self.root/'vanilla.lua').write_bytes(b'changed')
        with self.assertRaisesRegex(ValueError,'Vanilla loose input changed'):
            review_input(self.item,self.archive,self.root,self.observed)

    def test_packaged_evidence_never_uses_override(self):
        self.item.update(container='projectzomboid.jar',sha256=sha(b'vanilla'))
        self.assertEqual(review_input(self.item,self.archive,self.root,{}),'packaged')
        self.item['sha256']=sha(b'known override')
        with self.assertRaisesRegex(ValueError,'Vanilla packaged'): review_input(self.item,self.archive,self.root,self.observed)

    def test_evidence_traversal_refused(self):
        self.item['path']='../private.txt'
        with self.assertRaisesRegex(ValueError,'Unsafe'): review_input(self.item,self.archive,self.root,self.observed)


class ArtifactTests(unittest.TestCase):
    def check_invalid(self,names,expected):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/'test.zip'
            with zipfile.ZipFile(path,'w') as archive:
                for name,raw in names: archive.writestr(name,raw)
            with self.assertRaises(ValueError): verify_archive(path,expected)

    def test_extra_native_or_private_file_refused(self):
        name=PREFIX+'42/mod.info'
        for extra in (PREFIX+'bridge.jar',PREFIX+'server-console.txt'):
            with self.subTest(extra=extra): self.check_invalid([(name,b'ok'),(extra,b'bad')],{name:b'ok'})

    def test_path_traversal_refused(self):
        name=PREFIX+'../escape.lua';self.check_invalid([(name,b'bad')],{name:b'bad'})

    def test_case_collision_refused(self):
        a=PREFIX+'42/a.lua';b=PREFIX+'42/A.lua'
        self.check_invalid([(a,b'a'),(b,b'b')],{a:b'a',b:b'b'})

    def test_content_tampering_refused(self):
        name=PREFIX+'42/mod.info';self.check_invalid([(name,b'wrong')],{name:b'expected'})

    def test_complete_package_and_preserved_output(self):
        with tempfile.TemporaryDirectory() as tmp:
            target=Path(tmp)/'new'
            result=build(target)
            self.assertEqual(verify_archive(target/result['package'],payload()),112)
            from publish_workshop import read_vdf
            values=read_vdf(target/'upload.vdf')
            self.assertEqual(values['publishedfileid'],configuration()['publishedfileid'] or '0')
            self.assertIn('\n',values['description'])
            second=build(Path(tmp)/'second')
            self.assertEqual(result['package_sha256'],second['package_sha256'])
            with self.assertRaisesRegex(ValueError,'Output exists'): build(target)

    def test_wrong_workshop_identity_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);(root/'VERSION').write_text('0.2.0-dev.7')
            (root/'source-inventory.json').write_text(json.dumps({'workshop_id':None}))
            data=configuration();data['appid']='480'
            (root/'workshop.json').write_text(json.dumps(data))
            with self.assertRaisesRegex(ValueError,'identity'): configuration(root)


if __name__=='__main__': unittest.main(verbosity=2)
