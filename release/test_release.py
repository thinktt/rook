"""Fail-closed package and draft-publication controls; no network or engine runs."""
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('package', ROOT/'release/package.py')
package = importlib.util.module_from_spec(spec)
spec.loader.exec_module(package)


class ReleaseControls(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.build = self.root/'build'
        recipe = json.loads((ROOT/'build/release.json').read_text())
        graph = recipe['sourceGraphSha256']
        self.manifest = dict(schema='rook-artifact-qualification-v1', status='qualified-locally',
                             sourceGraphSha256=graph, artifacts=[])
        for variant in recipe['variants']:
            out = self.build/variant
            out.mkdir(parents=True)
            entries = {}
            for name in ['rook', 'rook-diag']:
                data = (variant+'/'+name).encode()
                (out/name).write_bytes(data)
                h = hashlib.sha256(data).hexdigest()
                entries[name] = dict(sha256=h, debugInformationRetained=True)
                self.manifest['artifacts'].append(dict(path=variant+'/'+name, sha256=h,
                    bytes=len(data), releaseName=name+'-{version}-'+variant))
            (out/'build.json').write_text(json.dumps(dict(mode='release', sourceGraphSha256=graph, artifacts=entries)))
        self.path = self.root/'qualification.json'
        self.save()

    def tearDown(self):
        self.temp.cleanup()

    def save(self):
        self.path.write_text(json.dumps(self.manifest))

    def prepare(self):
        self.assets = self.root/'assets'
        return package.prepare(self.build, self.path, 'v1.0.0', self.assets)

    def test_assets_preserve_the_qualified_bytes(self):
        names = self.prepare()
        self.assertEqual(len(names), 6)
        for item in self.manifest['artifacts']:
            name = item['releaseName'].format(version='1.0.0')
            self.assertEqual((self.assets/name).read_bytes(), (self.build/item['path']).read_bytes())
        subprocess.run(['sha256sum', '--check', 'SHA256SUMS'], cwd=self.assets, check=True, capture_output=True)

    def test_changed_binary_rejected_before_packaging(self):
        (self.build/'glibc/rook').write_bytes(b'changed')
        with self.assertRaisesRegex(ValueError, 'qualified artifact mismatch'):
            self.prepare()
        self.assertFalse(self.assets.exists())

    def test_missing_static_companion_rejected(self):
        self.manifest['artifacts'].pop()
        self.save()
        with self.assertRaisesRegex(ValueError, 'complete build'):
            self.prepare()

    def test_unqualified_manifest_rejected(self):
        self.manifest['status'] = 'preparing'
        self.save()
        with self.assertRaisesRegex(ValueError, 'not locally qualified'):
            self.prepare()

    def test_non_pgo_receipt_cannot_be_released(self):
        path = self.build/'glibc/build.json'
        record = json.loads(path.read_text())
        record['mode'] = 'plain'
        path.write_text(json.dumps(record))
        with self.assertRaisesRegex(ValueError, 'provenance'):
            self.prepare()

    def test_wrong_source_graph_cannot_be_released(self):
        self.manifest['sourceGraphSha256'] = '0'*64
        self.save()
        with self.assertRaisesRegex(ValueError, 'provenance'):
            self.prepare()

    def publish(self, state, fail_upload=False):
        self.prepare()
        bin_dir = self.root/'bin'
        bin_dir.mkdir()
        fake = bin_dir/'gh'
        fake.write_text('''#!/usr/bin/python3
import json,os,sys
from pathlib import Path
p=Path(os.environ['CALL_LOG'])
with p.open('a') as f:f.write(json.dumps(sys.argv[1:])+'\\n')
command=sys.argv[2]
if command=='view':
 state=os.environ['RELEASE_STATE']
 if state=='absent':raise SystemExit(1)
 print('true' if state=='draft' else 'false')
if command=='upload' and os.environ['FAIL_UPLOAD']=='1':raise SystemExit(1)
''')
        fake.chmod(0o755)
        log = self.root/'calls'
        env = dict(os.environ, PATH=str(bin_dir)+':'+os.environ['PATH'], CALL_LOG=str(log),
                   RELEASE_STATE=state, FAIL_UPLOAD=str(int(fail_upload)))
        result = subprocess.run(['bash', str(ROOT/'release/publish.sh'), 'v1.0.0', str(self.assets)],
                                env=env, capture_output=True)
        return result, [json.loads(s)[1] for s in log.read_text().splitlines()]

    def test_new_release_stays_draft_until_upload_succeeds(self):
        result, commands = self.publish('absent')
        self.assertEqual(result.returncode, 0)
        self.assertEqual(commands, ['view', 'create', 'upload', 'edit'])

    def test_failed_upload_does_not_publish(self):
        result, commands = self.publish('absent', fail_upload=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertNotIn('edit', commands)

    def test_draft_can_be_completed_by_rerun(self):
        result, commands = self.publish('draft')
        self.assertEqual(result.returncode, 0)
        self.assertEqual(commands, ['view', 'upload', 'edit'])

    def test_published_assets_cannot_be_replaced(self):
        result, commands = self.publish('published')
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(commands, ['view'])


if __name__ == '__main__':
    unittest.main()
