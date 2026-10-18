"""Real byte/exit/CPU-boundary controls for the controller-side wire tap."""
import hashlib
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
TAP = ROOT/'tools/tap_wire.mjs'
ACCOUNT = ROOT/'tools/account_native.py'

NATIVE = """import sys,time
print('READY',flush=True)
for line in sys.stdin.buffer:
    if line == b'go\\n':
        until=time.process_time()+0.03
        value=0
        while time.process_time()<until: value=(value+17)%65521
        sys.stdout.buffer.write(b'move a1'); sys.stdout.buffer.flush()
        time.sleep(0.01)
        sys.stdout.buffer.write(b'b2\\n'); sys.stdout.buffer.flush()
        sys.stderr.buffer.write(b'synthetic-stderr\\n'); sys.stderr.buffer.flush()
    elif line == b'quit\\n':
        time.sleep(0.03)
        raise SystemExit(int(sys.argv[1]))
"""


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


class WireTapControls(unittest.TestCase):
    def setUp(self):
        parent=os.environ.get('ROOK2_TAP_TEST_OUTPUT')
        if parent:
            self.directory=Path(parent).resolve()/self._testMethodName
            self.directory.mkdir()
            self.temporary=None
        else:
            self.temporary=tempfile.TemporaryDirectory(prefix='rook2-tap-control-')
            self.directory=Path(self.temporary.name)

    def tearDown(self):
        if self.temporary:
            self.temporary.cleanup()

    def run_control(self, exit_code=0, cap=1048576, mismatch=False):
        directory=self.directory
        native=directory/'native-control.py'; native.write_text(NATIVE)
        receipt=directory/'native.json'
        command=[sys.executable,str(ACCOUNT),'--engine',str(Path(sys.executable).resolve()),
                 '--record',str(receipt),'--known-single-process',str(native),str(exit_code)]
        expected=['/bin/false'] if mismatch else command
        config=dict(version=1,expectedArgv=expected,directory=str(directory/'wire'),
                    nativeExecutable=str(Path(sys.executable).resolve()),
                    maxRawBytes=cap,tickHz=os.sysconf('SC_CLK_TCK'))
        config_path=directory/'tap-config.json'; config_path.write_text(json.dumps(config)+'\n')
        driver=directory/'driver.mjs'
        driver.write_text("import {spawn} from 'node:child_process';\nconst argv="+json.dumps(command)+";\n"+r"""
const child=spawn(argv[0],argv.slice(1),{stdio:['pipe','pipe','pipe']});
let out='',sent=false,quit=false;
child.stdin.on('error',()=>{});
child.stdout.on('data',chunk=>{
  process.stdout.write(chunk);
  out+=chunk.toString('utf8');
  if (!sent && out.includes('READY\n')) {
    sent=true; child.stdin.write(Buffer.from('g'));
    setImmediate(()=>child.stdin.write('o\n'));
  }
  if (!quit && out.includes('move a1b2\n')) {
    quit=true; child.stdin.write('quit\n');
  }
});
child.stderr.on('data',chunk=>process.stderr.write(chunk));
child.on('error',()=>{process.exitCode=1;});
child.on('close',(code,signal)=>{process.exitCode=code ?? 1;});
""")
        argv=['/usr/bin/node','--import',str(TAP),str(driver)]
        env=dict(os.environ,ROOK2_WIRE_TAP_CONFIG=str(config_path))
        before={str(path):sha(path) for path in [TAP,ACCOUNT,native,driver,config_path]}
        process=subprocess.Popen(argv,env=env,stdout=subprocess.PIPE,stderr=subprocess.PIPE,start_new_session=True)
        timed_out=False
        try:
            stdout,stderr=process.communicate(timeout=5)
        except subprocess.TimeoutExpired:
            timed_out=True
            os.killpg(process.pid,signal.SIGKILL)
            stdout,stderr=process.communicate(timeout=5)
        (directory/'controller.stdout').write_bytes(stdout)
        (directory/'controller.stderr').write_bytes(stderr)
        after={path:sha(Path(path)) for path in before}
        (directory/'control.json').write_text(json.dumps(dict(command=argv,exit=process.returncode,
            timed_out=timed_out,input_sha256_before=before,input_sha256_after=after,
            helper_affinity=sorted(os.sched_getaffinity(0))),indent=2)+'\n')
        self.assertFalse(timed_out,'control exceeded deadline')
        self.assertEqual(before,after)
        return process.returncode,stdout,stderr

    def test_exact_bytes_split_records_and_native_tick_boundaries(self):
        code,stdout,stderr=self.run_control()
        self.assertEqual(code,0,stderr)
        self.assertEqual(stdout,b'READY\nmove a1b2\n')
        self.assertEqual(stderr,b'synthetic-stderr\n')
        wire=self.directory/'wire'
        self.assertEqual((wire/'stdin.raw').read_bytes(),b'go\nquit\n')
        self.assertEqual((wire/'stdout.raw').read_bytes(),stdout)
        self.assertEqual((wire/'stderr.raw').read_bytes(),stderr)
        tap=json.loads((wire/'receipt.json').read_text())
        native=json.loads((self.directory/'native.json').read_text())
        self.assertIsNone(tap['failure'])
        self.assertIsNone(native['failure'])
        self.assertIsNone(tap['pending'])
        self.assertEqual(len(tap['searches']),1)
        search=tap['searches'][0]
        self.assertEqual(search['beforeWrite']['pid'],native['native_pid'])
        self.assertEqual(search['afterData']['pid'],native['native_pid'])
        self.assertGreater(search['wallNs'],0)
        self.assertGreaterEqual(search['cpuTicks'],1)
        self.assertEqual(search['cpuSeconds'],search['cpuTicks']/tap['tickHz'])
        for stream,row in tap['raw'].items():
            self.assertEqual(row['sha256'],sha(wire/(stream+'.raw')))
            self.assertEqual(row['discardedObservedBytes'],0)

    def test_nonzero_exit_is_retained_without_stream_mutation(self):
        code,stdout,stderr=self.run_control(exit_code=7)
        self.assertEqual(code,7)
        self.assertEqual(stdout,b'READY\nmove a1b2\n')
        self.assertEqual(stderr,b'synthetic-stderr\n')
        tap=json.loads((self.directory/'wire/receipt.json').read_text())
        self.assertEqual(tap['launcherExit'],dict(code=7,signal=None))
        native=json.loads((self.directory/'native.json').read_text())
        self.assertEqual(native['native_exit_code'],7)
        self.assertIsNotNone(native['failure'])

    def test_raw_cap_retains_prefix_and_marks_discarded_bytes(self):
        code,_,_=self.run_control(cap=12)
        self.assertNotEqual(code,0)
        wire=self.directory/'wire'
        tap=json.loads((wire/'receipt.json').read_text())
        self.assertEqual(tap['failure'],'native-raw-byte-cap')
        self.assertLessEqual(sum(v['bytes'] for v in tap['raw'].values()),12)
        self.assertGreater(sum(v['discardedObservedBytes'] for v in tap['raw'].values()),0)
        self.assertTrue((wire/'failure.json').is_file())
        native=json.loads((self.directory/'native.json').read_text())
        self.assertIsNotNone(native['failure'])
        self.assertFalse(Path(f"/proc/{native['native_pid']}").exists())

    def test_undeclared_spawn_is_rejected_before_launch(self):
        code,_,stderr=self.run_control(mismatch=True)
        self.assertNotEqual(code,0)
        self.assertIn(b'undeclared spawn',stderr)
        self.assertFalse((self.directory/'native.json').exists())
        self.assertFalse((self.directory/'wire').exists())


if __name__ == '__main__':
    unittest.main()
