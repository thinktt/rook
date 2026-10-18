"""Controls for direct wait4 accounting and transparent native stream ownership."""
import json
from pathlib import Path
import selectors
import signal
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
CONTROL = ROOT / 'evidence/runner-controls/runner-control'
LAUNCHER = ROOT / 'tools/account_native.py'


class AccountingControls(unittest.TestCase):
    def command(self, receipt, mode):
        return [sys.executable, str(LAUNCHER), '--engine', str(CONTROL),
                '--record', str(receipt), '--known-single-process', mode]

    def test_normal_native_cpu_and_streams_exclude_supervisor_output(self):
        with tempfile.TemporaryDirectory() as directory:
            receipt = Path(directory) / 'native.json'
            result = subprocess.run(self.command(receipt, 'normal'),
                                    capture_output=True, text=True, timeout=5)
            self.assertEqual(result.returncode, 0, result.stderr)
            r = json.loads(receipt.read_text())
            self.assertIsNone(r['failure'])
            self.assertEqual(r['native_exit_code'], 0)
            self.assertEqual(r['native_post_exec']['affinity'], [14])
            self.assertGreaterEqual(r['total_cpu_s'], 0.029)
            self.assertEqual(r['total_cpu_s'], r['user_cpu_s'] + r['system_cpu_s'])
            self.assertGreater(r['wall_ns'], 0)
            self.assertEqual(r['engine_sha256_before'], r['engine_sha256_after'])
            first, second = result.stdout.splitlines()
            first = json.loads(first)
            self.assertEqual(first['pid'], r['native_pid'])
            self.assertEqual(first['affinity'], [14])
            self.assertTrue(second.startswith('cpu-work-completed:'))
            self.assertEqual(result.stderr, 'synthetic-stderr:normal\n')

    def test_nonzero_native_exit_is_mirrored_and_retained_as_invalid(self):
        with tempfile.TemporaryDirectory() as directory:
            receipt = Path(directory) / 'native.json'
            result = subprocess.run(self.command(receipt, 'nonzero'),
                                    capture_output=True, text=True, timeout=5)
            self.assertEqual(result.returncode, 7)
            r = json.loads(receipt.read_text())
            self.assertEqual(r['native_exit_code'], 7)
            self.assertIsNotNone(r['failure'])
            self.assertEqual(result.stderr, 'synthetic-stderr:nonzero\n')
            self.assertEqual(json.loads(result.stdout)['mode'], 'nonzero')

    def test_existing_receipt_prevents_launch_and_preserves_bytes(self):
        with tempfile.TemporaryDirectory() as directory:
            receipt = Path(directory) / 'native.json'
            receipt.write_bytes(b'previous attempt\n')
            result = subprocess.run(self.command(receipt, 'normal'),
                                    capture_output=True, text=True, timeout=5)
            self.assertEqual(result.returncode, 2)
            self.assertEqual(result.stdout, '')
            self.assertEqual(receipt.read_bytes(), b'previous attempt\n')

    def test_supervisor_signal_reaps_native_and_preserves_native_signal_exit(self):
        with tempfile.TemporaryDirectory() as directory:
            receipt = Path(directory) / 'native.json'
            process = subprocess.Popen(self.command(receipt, 'timeout'),
                                       stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            try:
                with selectors.DefaultSelector() as ready:
                    ready.register(process.stdout, selectors.EVENT_READ)
                    self.assertTrue(ready.select(3), 'native control did not start')
                first = json.loads(process.stdout.readline())
                process.send_signal(signal.SIGTERM)
                _, stderr = process.communicate(timeout=5)
                self.assertEqual(process.returncode, -signal.SIGTERM, stderr)
                r = json.loads(receipt.read_text())
                self.assertEqual(r['native_exit_code'], -signal.SIGTERM)
                self.assertEqual(r['supervisor_signals'], [signal.SIGTERM])
                self.assertIsNotNone(r['failure'])
                self.assertFalse(Path(f"/proc/{first['pid']}").exists(), 'native child not reaped')
            finally:
                if process.poll() is None:
                    process.terminate()
                    process.communicate(timeout=5)


if __name__ == '__main__':
    unittest.main()
