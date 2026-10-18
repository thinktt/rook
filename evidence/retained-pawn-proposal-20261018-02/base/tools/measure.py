#!/usr/bin/env python3
"""Development-only known-single-process CPU/wall measurement. No PMU or oracle."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import selectors
import shutil
import signal
import statistics
import sys
import time


ENGINE_CPU = 14
HELPERS = {0, 1, 2, 3, 4, 5, 8, 9, 10, 11, 12, 13}


def sha256(path: Path) -> str:
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def read_text(path: Path) -> str | None:
    try:
        return path.read_text().strip()
    except OSError:
        return None


def write_json(path: Path, data: dict) -> None:
    temporary = path.with_suffix(".json.tmp")
    with temporary.open("x") as stream:
        json.dump(data, stream, indent=2, allow_nan=False)
        stream.write("\n")
    temporary.replace(path)


def cgroup_snapshot() -> dict:
    """Read the unified local cgroup and ancestors, without changing them."""
    membership = read_text(Path("/proc/self/cgroup"))
    result = {"membership": membership, "visible_ancestors": {}}
    for line in (membership or "").splitlines():
        if not line.startswith("0::/"):
            continue
        relative = line[3:].lstrip("/")
        if ".." in Path(relative).parts:
            continue
        root = Path("/sys/fs/cgroup")
        leaf = root / relative
        for parent in [leaf, *leaf.parents]:
            if parent != root and root not in parent.parents:
                continue
            result["visible_ancestors"][str(parent)] = {
                name: read_text(parent / name)
                for name in ("cpu.max", "cpuset.cpus.effective", "memory.max",
                             "memory.swap.max")
            }
    return result


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--output", required=True, type=Path,
                   help="fresh absent study directory")
    p.add_argument("--label", required=True)
    p.add_argument("--fidelity", required=True, choices=["F0", "F1", "F2", "F3", "F4"])
    p.add_argument("--semantic-description", required=True,
                   help="completed task, reset/stopping/seed policy and omissions")
    p.add_argument("--known-single-process", action="store_true", required=True,
                   help="assert command does not delegate work or spawn children")
    p.add_argument("--cwd", type=Path, default=Path.cwd())
    p.add_argument("--input-file", action="append", type=Path, default=[])
    p.add_argument("--build-record", type=Path,
                   help="optional build metadata file whose exact bytes are bound")
    p.add_argument("--warmups", type=int, default=1)
    p.add_argument("--repeats", type=int, default=3)
    p.add_argument("--timeout-s", type=float, default=300.0)
    p.add_argument("--aggregate-timeout-s", type=float, default=1800.0)
    p.add_argument("--cleanup-s", type=float, default=5.0)
    p.add_argument("--stream-cap-bytes", type=int, default=4 * 1024 * 1024)
    p.add_argument("--dry-run", action="store_true",
                   help="validate and print plan only; no affinity changes or launch")
    p.add_argument("command", nargs=argparse.REMAINDER)
    return p


def make_plan(args: argparse.Namespace) -> dict:
    command = args.command[1:] if args.command[:1] == ["--"] else args.command
    if not command:
        raise ValueError("provide an executable after --")
    if not 0 <= args.warmups <= 10 or not 1 <= args.repeats <= 20:
        raise ValueError("warmups must be 0..10 and repeats 1..20")
    for value in (args.timeout_s, args.aggregate_timeout_s, args.cleanup_s):
        if not math.isfinite(value) or value <= 0:
            raise ValueError("deadlines must be finite positive seconds")
    if not 1 <= args.stream_cap_bytes <= 64 * 1024 * 1024:
        raise ValueError("stream cap must be 1..67108864 bytes")
    args.cwd = args.cwd.resolve(strict=True)
    if not args.cwd.is_dir():
        raise ValueError("cwd must be a directory")
    # Resolve explicit relative paths in the declared command working directory.
    executable = command[0]
    if "/" in executable:
        executable = str((args.cwd / executable).resolve(strict=True))
    else:
        executable = shutil.which(executable)
    if not executable or not os.access(executable, os.X_OK):
        raise ValueError("executable not found or not executable")
    binary = Path(executable).resolve(strict=True)
    if not binary.is_file():
        raise ValueError("command executable must be a regular file")
    command = [str(binary), *command[1:]]
    output = args.output.absolute()
    if output.exists() or output.is_symlink():
        raise ValueError("output must be a fresh absent directory")
    if not output.parent.is_dir():
        raise ValueError("output parent must already exist")
    args.output = output
    allowed = set(os.sched_getaffinity(0))
    if not HELPERS <= allowed:
        raise ValueError("inherited recorder affinity must permit all helper CPUs")
    inputs = {}
    for source in [*args.input_file, *([args.build_record] if args.build_record else [])]:
        source = source.resolve(strict=True)
        inputs[str(source)] = sha256(source)
    return {
        "schema": "rook2-development-cpu-wall-v1",
        "label": args.label,
        "fidelity_claim": args.fidelity,
        "semantic_description": args.semantic_description,
        "behavior": "not-checked-by-this-runner",
        "performance": "reported-only; no qualification comparison",
        "scope": "direct-child wait4 user+system CPU; asserted known single process",
        "descendant_accounting": "not-established; delegated/forked work unsupported",
        "stdin": "DEVNULL; no interactive protocol/oracle adapter",
        "pmu": {"instructions": None, "cycles": None, "ipc": None,
                "reason": "not collected by this runner"},
        "command": command,
        "cwd": str(args.cwd),
        "output": str(output),
        "executable_sha256": sha256(binary),
        "runner_sha256": sha256(Path(__file__).resolve()),
        "python": {"version": sys.version, "executable": sys.executable,
                   "sha256": sha256(Path(sys.executable).resolve())},
        "input_sha256": inputs,
        "build_record": str(args.build_record.resolve()) if args.build_record else None,
        "environment": {key: os.environ.get(key) for key in
                        ("RUSTFLAGS", "CARGO_ENCODED_RUSTFLAGS", "RUSTUP_TOOLCHAIN",
                         "LD_PRELOAD", "LD_LIBRARY_PATH", "LLVM_PROFILE_FILE")},
        "engine_cpu": ENGINE_CPU,
        "idle_sibling": 15,
        "helper_cpus": sorted(HELPERS),
        "initial_recorder_affinity": sorted(allowed),
        "engine_affinity_admission": "child requests CPU14 independently; kernel rejection or mismatched placement invalidates attempt",
        "guest_uname": list(os.uname()),
        "guest_cpu14_siblings": read_text(Path(
            "/sys/devices/system/cpu/cpu14/topology/thread_siblings_list")),
        "cgroups_before": cgroup_snapshot(),
        "clock_ticks_per_second": os.sysconf("SC_CLK_TCK"),
        "cpu_resolution": "kernel wait4 accounting; float seconds, no ns precision claim",
        "wall_scope": "parent monotonic immediately before fork through direct-child reaping",
        "observer_poll_interval_s": 0.02,
        "preexec_scope": "child setsid/affinity/stdio/chdir/exec prelude included",
        "profile_limit": "affinity is pinning, not exclusive isolation or resource caps",
        "schedule": {"warmups": args.warmups, "measured": args.repeats,
                     "order": "serial warmups then measured; one command"},
        "bounds": {"run_timeout_s": args.timeout_s,
                   "aggregate_timeout_s": args.aggregate_timeout_s,
                   "cleanup_s": args.cleanup_s,
                   "per_stream_cap_bytes": args.stream_cap_bytes,
                   "maximum_raw_bytes": (args.warmups + args.repeats)
                   * 2 * args.stream_cap_bytes},
    }


def kill_owned(pid: int) -> None:
    """Kill only our unreaped direct child or the session group it created."""
    try:
        if os.getpgid(pid) == pid:
            os.killpg(pid, signal.SIGKILL)
        else:
            os.kill(pid, signal.SIGKILL)
    except ProcessLookupError:
        pass


def measure_once(plan: dict, args: argparse.Namespace, index: int,
                 warmup: bool, aggregate_deadline: float) -> dict:
    binary = Path(plan["command"][0])
    for file, expected in {str(binary): plan["executable_sha256"],
                           **plan["input_sha256"]}.items():
        if sha256(Path(file)) != expected:
            raise ValueError(f"artifact changed before run: {file}")
    run_id = f"{index:03d}-{'warmup' if warmup else 'measured'}"
    directory = args.output / run_id
    directory.mkdir()
    outputs = {key: (directory / f"{key}.raw").open("xb")
               for key in ("stdout", "stderr")}
    pipes = {key: os.pipe() for key in ("stdout", "stderr", "placement")}
    counts = {key: {"observed": 0, "retained": 0, "discarded": 0}
              for key in outputs}
    start = time.monotonic_ns()
    pid = os.fork()
    if pid == 0:
        try:
            for read_fd, _ in pipes.values():
                os.close(read_fd)
            os.setsid()
            os.sched_setaffinity(0, {ENGINE_CPU})
            os.dup2(pipes["stdout"][1], 1)
            os.dup2(pipes["stderr"][1], 2)
            with open(os.devnull, "rb") as empty:
                os.dup2(empty.fileno(), 0)
            os.chdir(args.cwd)
            placement = json.dumps({"affinity": sorted(os.sched_getaffinity(0)),
                                    "pid": os.getpid(), "pgid": os.getpgrp()})
            os.write(pipes["placement"][1], placement.encode())
            os.execv(plan["command"][0], plan["command"])
        except BaseException as error:
            os.write(2, f"measure child setup/exec error: {type(error).__name__}\n".encode())
            os._exit(127)
    for _, write_fd in pipes.values():
        os.close(write_fd)
    selector = selectors.DefaultSelector()
    for key, (read_fd, _) in pipes.items():
        os.set_blocking(read_fd, False)
        selector.register(read_fd, selectors.EVENT_READ, key)
    failure = None
    status = usage = reaped_ns = None
    placement_bytes = b""
    kill_deadline = None
    deadline = min(start / 1e9 + args.timeout_s, aggregate_deadline)
    try:
        while selector.get_map() or status is None:
            now = time.monotonic()
            if failure is None and now >= deadline:
                failure = "deadline"
            if failure is not None and kill_deadline is None:
                if status is None:
                    kill_owned(pid)
                kill_deadline = now + args.cleanup_s
            if kill_deadline is not None and now >= kill_deadline:
                break
            if reaped_ns is not None and selector.get_map() and now >= reaped_ns / 1e9 + args.cleanup_s:
                failure = failure or "pipe-eof-deadline-after-main-exit"
                break
            for key, _ in selector.select(0.02):
                data = os.read(key.fd, 65536)
                if not data:
                    selector.unregister(key.fd)
                    os.close(key.fd)
                    continue
                if key.data == "placement":
                    if len(placement_bytes) + len(data) > 4096:
                        failure = failure or "invalid-placement-record"
                    else:
                        placement_bytes += data
                    continue
                count = counts[key.data]
                count["observed"] += len(data)
                remaining = args.stream_cap_bytes - count["retained"]
                retained = data[:remaining]
                outputs[key.data].write(retained)
                count["retained"] += len(retained)
                count["discarded"] += len(data) - len(retained)
                if count["discarded"]:
                    failure = failure or "stream-cap"
            if status is None:
                got_pid, new_status, new_usage = os.wait4(pid, os.WNOHANG)
                if got_pid:
                    status, usage = new_status, new_usage
                    reaped_ns = time.monotonic_ns()
    except BaseException as error:
        failure = f"recorder-interrupted:{type(error).__name__}"
        if status is None:
            kill_owned(pid)
        stop = time.monotonic() + args.cleanup_s
        while status is None and time.monotonic() < stop:
            got_pid, new_status, new_usage = os.wait4(pid, os.WNOHANG)
            if got_pid:
                status, usage = new_status, new_usage
                reaped_ns = time.monotonic_ns()
            else:
                time.sleep(0.01)
    finally:
        stream_eof = not selector.get_map()
        for key in list(selector.get_map().values()):
            selector.unregister(key.fd)
            os.close(key.fd)
        selector.close()
        for stream in outputs.values():
            stream.close()
    if status is None:
        failure = failure or "direct-child-exit-unresolved"
    exit_code = os.waitstatus_to_exitcode(status) if status is not None else None
    if exit_code != 0:
        failure = failure or "nonzero-or-signal-exit"
    try:
        placement = json.loads(placement_bytes)
    except (ValueError, UnicodeError):
        placement = None
    if placement != {"affinity": [ENGINE_CPU], "pid": pid, "pgid": pid}:
        failure = failure or "placement-unverified"
    try:
        final_sha = sha256(binary)
    except OSError:
        final_sha = None
    if final_sha != plan["executable_sha256"]:
        failure = failure or "executable-changed"
    input_after = {}
    for file, expected in plan["input_sha256"].items():
        try:
            input_after[file] = sha256(Path(file))
        except OSError:
            input_after[file] = None
        if input_after[file] != expected:
            failure = failure or "input-artifact-changed"
    cpu = usage.ru_utime + usage.ru_stime if usage else None
    record = {
        "id": run_id, "pid": pid, "warmup": warmup,
        "disposition": "valid-for-declared-direct-process-scope" if failure is None else "invalid",
        "failure": failure, "placement_before_exec": placement,
        "affinity_after_exec": "not-continuously-observed; command must not change affinity",
        "start_monotonic_ns": start, "reaped_monotonic_ns": reaped_ns,
        "wall_ns": reaped_ns - start if reaped_ns is not None else None,
        "user_cpu_s": usage.ru_utime if usage else None,
        "system_cpu_s": usage.ru_stime if usage else None,
        "total_cpu_s": cpu,
        "cpu_rate_available": cpu is not None and cpu > 0,
        "maxrss_linux_kib": usage.ru_maxrss if usage else None,
        "minor_faults": usage.ru_minflt if usage else None,
        "major_faults": usage.ru_majflt if usage else None,
        "voluntary_context_switches": usage.ru_nvcsw if usage else None,
        "involuntary_context_switches": usage.ru_nivcsw if usage else None,
        "wait_status": status, "exit_code": exit_code,
        "streams": counts, "stream_eof": stream_eof,
        "executable_sha256_after": final_sha,
        "input_sha256_after": input_after,
        "behavior": "not-checked; raw output retained for separate validation",
        "owned_descendant_completion": "not-established; single-process assertion required",
    }
    write_json(directory / "record.json", record)
    return record


def summarize(records: list[dict], field: str) -> dict | None:
    samples = [record[field] for record in records if not record["warmup"]
               and record["failure"] is None]
    if not samples:
        return None
    median = statistics.median(samples)
    return {"samples": samples, "min": min(samples), "median": median,
            "max": max(samples), "range_over_median":
            (max(samples) - min(samples)) / median if median > 0 else None}


def main() -> int:
    p = parser()
    args = p.parse_args()
    try:
        plan = make_plan(args)
    except (ValueError, OSError) as error:
        p.error(str(error))
    if args.dry_run:
        print(json.dumps(plan, indent=2, allow_nan=False))
        return 0
    args.output.mkdir()
    write_json(args.output / "manifest.json", plan)
    initial_affinity = os.sched_getaffinity(0)
    records = []
    failure = None
    collection_affinity = None
    deadline = time.monotonic() + args.aggregate_timeout_s
    try:
        os.sched_setaffinity(0, HELPERS)
        collection_affinity = sorted(os.sched_getaffinity(0))
        for index in range(args.warmups + args.repeats):
            if time.monotonic() >= deadline:
                failure = "aggregate-deadline-before-next-launch"
                break
            record = measure_once(plan, args, index, index < args.warmups, deadline)
            records.append(record)
            if record["failure"] is not None:
                failure = record["failure"]
                break
    except BaseException as error:
        failure = f"recorder-error:{type(error).__name__}:{error}"
    finally:
        os.sched_setaffinity(0, initial_affinity)
    complete = failure is None and len(records) == args.warmups + args.repeats
    report = {"complete_schedule": complete, "failure": failure,
              "behavior": "not-checked", "performance": "reported-only",
              "measurement_scope": plan["scope"], "records": records,
              "recorder_affinity_during_collection": collection_affinity,
              "summaries": {name: summarize(records, name) if complete else None
                            for name in ("total_cpu_s", "wall_ns")},
              "affinity_restored": sorted(os.sched_getaffinity(0)),
              "cgroups_after": cgroup_snapshot()}
    write_json(args.output / "summary.json", report)
    print(json.dumps({"output": str(args.output), "complete_schedule": complete,
                      "failure": failure, "behavior": "not-checked",
                      "performance": "reported-only"}))
    return 0 if complete else 1


if __name__ == "__main__":
    raise SystemExit(main())
