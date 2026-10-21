"""Tiny offline fixtures: runtime asset inputs and historical proof immutability."""
import hashlib,json,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
import build_loadable as build
from validate_database_authority_proof import baseline_bytes

class ProofHeaders(unittest.TestCase):
    def test_metadata_header_only(self):
        raw=b'name=Dogmeat\r\nmodversion=0.2.0-dev.8\r\n'
        self.assertEqual(baseline_bytes('src/metadata/mod.info',raw),b'name=Dogmeat\nmodversion=0.2.0-dev.7\n')
    def test_json_header_preserves_claims(self):
        raw=b'{\n  "project_version": "0.2.0-dev.8",\n  "observed_project_version": "0.2.0-dev.5",\n  "decision": "NO-GO",\n  "enabled": false\n}\n'
        normalized=baseline_bytes('docs/native-fixture.json',raw)
        self.assertEqual(normalized,raw.replace(b'0.2.0-dev.8',b'0.2.0-dev.7'))
        self.assertNotEqual(normalized,baseline_bytes('docs/native-fixture.json',raw.replace(b'false',b'true')))
    def test_missing_duplicate_headers_rejected(self):
        for raw in [b'name=Dogmeat\n',b'modversion=1\nmodversion=2\n']:
            with self.assertRaises(ValueError):baseline_bytes('src/metadata/mod.info',raw)
        for raw in [b'{}',b'  "project_version": "1",\n  "project_version": "2"\n']:
            with self.assertRaises(ValueError):baseline_bytes('docs/native-fixture.json',raw)
    def test_lua_never_normalized(self):
        raw=b'local observed = "0.2.0-dev.8"\nreturn false\n'
        self.assertEqual(baseline_bytes('src/native/example.lua',raw),raw)

class AssetMapping(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name).resolve()
        self.patch=patch.object(build,'ROOT',self.root);self.patch.start();self.addCleanup(self.patch.stop)
        (self.root/'asset.png').write_bytes(b'fixture image bytes')
        self.entry={'source':'asset.png','target':'42/media/textures/fixture.png','sha256':hashlib.sha256((self.root/'asset.png').read_bytes()).hexdigest()}
    def mapping(self,entries):
        (self.root/'source-inventory.json').write_text(json.dumps({'authoritative_lua':[],'languages':[],'localization_keys':{},'runtime_assets':entries}))
        return build.sources()
    def test_valid_exact_mapping(self):
        self.assertEqual(self.mapping([self.entry])[self.entry['target']].read_bytes(),b'fixture image bytes')
    def test_changed_hash(self):
        with self.assertRaises(ValueError):self.mapping([dict(self.entry,sha256='0'*64)])
    def test_lfs_pointer_rejected_even_with_matching_hash(self):
        raw=b'version https://git-lfs.github.com/spec/v1\noid sha256:fixture\nsize 42\n'
        (self.root/'asset.png').write_bytes(raw)
        with self.assertRaises(ValueError):self.mapping([dict(self.entry,sha256=hashlib.sha256(raw).hexdigest())])
    def test_unsafe_sources(self):
        for source in ['../asset.png',str(self.root/'asset.png'),'C:/private.png','..\\asset.png']:
            with self.subTest(source=source),self.assertRaises(ValueError):self.mapping([dict(self.entry,source=source)])
    def test_unsafe_targets(self):
        for target in ['../x.png','/42/media/x.png','42/media/../x.png','42/media/a:b.png','42\\media\\x.png','media/x.png']:
            with self.subTest(target=target),self.assertRaises(ValueError):self.mapping([dict(self.entry,target=target)])
    def test_duplicate_and_case_collision(self):
        for target in [self.entry['target'],'42/media/textures/FIXTURE.png']:
            with self.subTest(target=target),self.assertRaises(ValueError):self.mapping([self.entry,dict(self.entry,target=target)])
    def test_wrong_formats(self):
        with self.assertRaises(ValueError):self.mapping([dict(self.entry,target='42/media/fixture.glb')])
        with self.assertRaises(ValueError):self.mapping([dict(self.entry,source='asset.exe',target='42/media/asset.exe')])

if __name__=='__main__':unittest.main()
