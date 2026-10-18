"""Recorder controls with a mocked fork/wait4: no executable is launched."""

import contextlib
import importlib.util
import json
from pathlib import Path
import tempfile
import types
import unittest
from unittest import mock


spec = importlib.util.spec_from_file_location("measure", Path(__file__).with_name("measure.py"))
measure = importlib.util.module_from_spec(spec)
spec.loader.exec_module(measure)


class RecorderControls(unittest.TestCase):
    def test_helper_pinned_recorder_can_plan_independent_engine_affinity(self):
        with tempfile.TemporaryDirectory() as temporary:
            args = measure.parser().parse_args([
                "--output", str(Path(temporary) / "fresh-study"),
                "--label", "placement-plan", "--fidelity", "F0",
                "--semantic-description", "synthetic plan only",
                "--known-single-process", "--dry-run", "--", "/bin/true"])
            with mock.patch.object(measure.os, "sched_getaffinity",
                                   return_value=measure.HELPERS):
                plan = measure.make_plan(args)
            self.assertEqual(plan["initial_recorder_affinity"], sorted(measure.HELPERS))
            self.assertEqual(plan["engine_cpu"], 14)

    def run_control(self, *, content=b"actual-output\n", cap=1024,
                    status=0, timeout=False, placement=True):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            binary = root / "fake-never-executed"
            binary.write_bytes(b"not an executable")
            pipes = []
            real_pipe = measure.os.pipe
            killed = []

            def pipe():
                pair = real_pipe()
                pipes.append(pair)
                return pair

            def fake_fork():
                measure.os.write(pipes[0][1], content)
                if placement:
                    measure.os.write(pipes[2][1], json.dumps(
                        {"affinity": [14], "pid": 424242, "pgid": 424242}).encode())
                return 424242

            usage = types.SimpleNamespace(ru_utime=0.1, ru_stime=0.02,
                ru_maxrss=1024, ru_minflt=1, ru_majflt=0, ru_nvcsw=2, ru_nivcsw=3)

            def fake_wait4(pid, options):
                if timeout and not killed:
                    return 0, 0, None
                return pid, status, usage

            args = types.SimpleNamespace(output=root, cwd=root,
                timeout_s=0.03, cleanup_s=0.1, stream_cap_bytes=cap)
            plan = {"command": [str(binary)],
                    "executable_sha256": measure.sha256(binary), "input_sha256": {}}
            with contextlib.ExitStack() as stack:
                stack.enter_context(mock.patch.object(measure.os, "pipe", side_effect=pipe))
                stack.enter_context(mock.patch.object(measure.os, "fork", side_effect=fake_fork))
                stack.enter_context(mock.patch.object(measure.os, "wait4", side_effect=fake_wait4))
                stack.enter_context(mock.patch.object(measure, "kill_owned",
                                                       side_effect=lambda pid: killed.append(pid)))
                record = measure.measure_once(plan, args, 0, False,
                                               measure.time.monotonic() + 1)
            raw = (root / "000-measured/stdout.raw").read_bytes()
            saved = json.loads((root / "000-measured/record.json").read_text())
            self.assertEqual(saved, record)
            return record, raw, killed

    def test_normal_direct_scope_retains_raw_and_separate_cpu(self):
        record, raw, killed = self.run_control()
        self.assertIsNone(record["failure"])
        self.assertEqual(raw, b"actual-output\n")
        self.assertAlmostEqual(record["total_cpu_s"], 0.12)
        self.assertEqual(record["user_cpu_s"], 0.1)
        self.assertIn("not-checked", record["behavior"])
        self.assertIn("not-established", record["owned_descendant_completion"])
        self.assertFalse(killed)

    def test_missing_placement_cannot_be_reported_valid(self):
        record, _, _ = self.run_control(placement=False)
        self.assertEqual(record["failure"], "placement-unverified")

    def test_over_cap_keeps_bounded_bytes_and_invalidates(self):
        record, raw, _ = self.run_control(content=b"abcdefgh", cap=4)
        self.assertEqual(record["failure"], "stream-cap")
        self.assertEqual(raw, b"abcd")
        self.assertEqual(record["streams"]["stdout"]["discarded"], 4)

    def test_nonzero_exit_is_not_behavior_success(self):
        record, _, _ = self.run_control(status=7 << 8)
        self.assertEqual(record["exit_code"], 7)
        self.assertEqual(record["failure"], "nonzero-or-signal-exit")

    def test_timeout_is_invalid_even_with_later_zero_exit(self):
        record, _, killed = self.run_control(timeout=True)
        self.assertEqual(record["failure"], "deadline")
        self.assertEqual(killed, [424242])

    def test_unresolved_zero_cpu_has_no_spread_ratio(self):
        record = {"warmup": False, "failure": None, "total_cpu_s": 0}
        self.assertIsNone(measure.summarize([record], "total_cpu_s")["range_over_median"])


if __name__ == "__main__":
    unittest.main()
