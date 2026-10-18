#!/usr/bin/env python3
"""Parent-invoked diagnostic census; never build, train or time an engine."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import tarfile
from datetime import datetime, timezone

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[1]
PREP = ROOT / "evidence/material-allowance-census-preparation-20261018"
BUILD = ROOT / "evidence/material-allowance-census-build-20261018"
SPEC = Path("/home/legolas/king-spec/conformance/profiling")
HOUSEKEEPING = [0, 1, 2, 3, 4, 5, 8, 9, 10, 11, 12, 13]
FAMILIES = ("q", "ordinary")
FIELDS = ("loops", "checked_loops", "nonempty_loops", "calls", "unique_keys",
          "old_endpoints", "lazy_endpoints")
SCALARS = {f"{family}_{field}" for family in FAMILIES for field in FIELDS} | {"full", "fast"}
ARRAYS = {f"{family}_{field}" for family in FAMILIES
          for field in ("calls_by_victim", "unique_by_victim")}
COUNT_KEYS = SCALARS | ARRAYS | {"schema"}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("Duplicate JSON key: " + key)
        result[key] = value
    return result


def load(path):
    return json.loads(path.read_text(), object_pairs_hook=unique_object)


def write_new(path, value):
    with path.open("x") as stream:
        json.dump(value, stream, indent=2)
        stream.write("\n")


def utc():
    return datetime.now(timezone.utc).isoformat()


def terminal(path):
    value = load(path)
    assert type(value.get("exit_code")) is int and value["exit_code"] == 0, path
    assert type(value.get("session_id")) is int and value["session_id"] > 0, path
    assert isinstance(value.get("chunk_id"), str) and value["chunk_id"], path
    assert isinstance(value.get("origin"), str) and "actual" in value["origin"].lower(), path
    return value


def validate_counts(counts):
    assert set(counts) == COUNT_KEYS
    assert counts["schema"] == "rook2-material-allowance-census-v1"
    assert all(type(counts[key]) is int and counts[key] >= 0 for key in SCALARS)
    assert all(isinstance(counts[key], list) and len(counts[key]) == 10
               and all(type(v) is int and v >= 0 for v in counts[key]) for key in ARRAYS)
    for family in FAMILIES:
        item = lambda key: counts[f"{family}_{key}"]
        loops, checked, nonempty = item("loops"), item("checked_loops"), item("nonempty_loops")
        calls, distinct = item("calls"), item("unique_keys")
        assert 0 <= checked <= loops and 0 <= nonempty <= loops
        assert nonempty <= distinct <= calls and distinct <= 5 * nonempty
        assert item("old_endpoints") == 2 * calls
        assert item("lazy_endpoints") == nonempty + distinct <= item("old_endpoints")
        assert sum(item("calls_by_victim")) == calls
        assert sum(item("unique_by_victim")) == distinct
        assert all(a <= b for a, b in zip(item("unique_by_victim"), item("calls_by_victim")))
        if family == "q":
            assert nonempty <= loops - checked


def ratio(a, b):
    return a / b if b else None


def derived(counts):
    demand = counts["full"] + counts["fast"] + sum(
        counts[f"{f}_old_endpoints"] for f in FAMILIES)
    families = {}
    for family in FAMILIES:
        old = counts[f"{family}_old_endpoints"]
        lazy = counts[f"{family}_lazy_endpoints"]
        families[family] = {
            "zero_call_loops": counts[f"{family}_loops"] - counts[f"{family}_nonempty_loops"],
            "avoided_endpoint_demands": old - lazy,
            "avoided_fraction_of_allowance_endpoints": ratio(old - lazy, old),
            "avoided_fraction_of_segment_material_demands": ratio(old - lazy, demand),
        }
    old = sum(counts[f"{f}_old_endpoints"] for f in FAMILIES)
    lazy = sum(counts[f"{f}_lazy_endpoints"] for f in FAMILIES)
    return {
        "families": families,
        "segment_material_demands": demand,
        "allowance_old_endpoint_demands": old,
        "allowance_lazy_endpoint_model": lazy,
        "avoided_endpoint_demands": old - lazy,
        "allowance_fraction_of_segment_material_demands": ratio(old, demand),
        "avoided_fraction_of_segment_material_demands": ratio(old - lazy, demand),
        "scope": "Source requests after begin_sequence; excludes root-preparation full. Not emitted calls or CPU gain.",
    }


def validate_report(report, case, engine, oracle, workloads_hash, oracle_hash):
    assert report["status"] == "pass" and report["selectedCases"] == [case]
    assert report["fixture"] == oracle["id"]
    assert report["workloadSha256"] == workloads_hash and report["oracleSha256"] == oracle_hash
    assert len(report["results"]) == 1
    native = report["results"][0]
    assert native["case"] == case and native["status"] == "pass"
    assert native["exit"] == {"code": 0, "signal": None}
    assert native["complete"] is True and native["truncated"] is False
    assert native["error"] is None and native["discardedObservedBytes"] == 0
    assert type(native["pid"]) is int and native["pid"] > 0
    assert native["stderr"] == "" and isinstance(native["stdout"], str)
    assert native["command"] == ["/usr/bin/taskset", "-c", "14", str(engine), *oracle["mode"]]
    return native


def readiness(args):
    prepared_path = PREP / "prepared.json"
    prepared = load(prepared_path)
    assert prepared["path"] == "/tmp/imp2-material-allowance-census79-20261018-a1gikj0f"
    archive = PREP / prepared["archive"]
    assert sha(archive) == prepared["archive_sha256"]
    assert sha(PREP / "census.patch") == prepared["patch_sha256"]
    with tarfile.open(archive, "r:gz") as handle:
        members = list(handle)
        assert all(member.isfile() for member in members)
        identities = {m.name: hashlib.sha256(handle.extractfile(m).read()).hexdigest() for m in members}
        assert len(identities) == len(members) and identities == prepared["archive_files"]
    build = load(args.build_receipt)
    assert build["schema"] == "rook2-development-build-v1"
    assert build["crate"] == prepared["path"] and build["binary_name"] == "rook2-material-allowance-probe"
    assert build["cargo_exit_code"] == 0 and build["outcome"] == "build-succeeded-with-stable-input-snapshot"
    assert build["source_identity_unchanged"] is True and build["tool_identity_unchanged"] is True
    assert build["cargo_config_unchanged"] is True
    assert build["source_sha256_before"] == build["source_sha256_after"] == prepared["variant_source_sha256"]
    expected_tools = {k: v for k, v in prepared["archive_files"].items() if k.startswith("tools/")}
    assert build["tool_sha256_before"] == build["tool_sha256_after"] == expected_tools
    assert build["binary_output"]["sha256"] == args.expected_engine_sha256 == sha(args.engine)
    assert build["source_archive"]["verified_against_before_hashes"] is True
    source_archive = Path(build["source_archive"]["path"])
    if not source_archive.is_absolute():
        source_archive = args.build_receipt.parent / source_archive
    frozen = []
    for name, identity in (prepared["variant_source_sha256"] | expected_tools).items():
        path = source_archive / name
        assert sha(path) == identity
        frozen.append(path)
    logs = []
    for log in build["logs"].values():
        path = args.build_receipt.parent / log["path"]
        assert sha(path) == log["sha256"] and path.stat().st_size == log["bytes"]
        logs.append(path)
    actual = terminal(args.build_terminal)
    receipt_binding = actual.get("receipt_sha256", actual.get("build_json_sha256"))
    assert receipt_binding == sha(args.build_receipt)
    assert actual["native_artifact_sha256"] == args.expected_engine_sha256
    native_terminal = terminal(args.native_terminal)
    native_path = args.native_terminal.parent / "native-verification.json"
    native = load(native_path)
    assert native_terminal["native_verification_sha256"] == sha(native_path)
    assert native["complete"] is True and native["failure"] is None and native["inputs_stable"] is True
    assert native["source_before"] == native["source_after"] == prepared["variant_source_sha256"]
    assert len(native["stages"]) == 3
    assert all(stage["exit_code"] == 0 for stage in native["stages"])
    assert native["units"]["rook2"]["passed"] == 133 and native["units"]["rook2-dev"]["passed"] == 2
    native_files = [native_path]
    for unit, stage in zip(("unit-build", "rook2-tests", "rook2-dev-tests"), native["stages"]):
        for suffix in ("stdout", "stderr"):
            path = args.native_terminal.parent / f"{unit}.{suffix}"
            assert sha(path) == stage[f"{suffix}_sha256"]
            native_files.append(path)
    strict_terminal = terminal(args.strict_terminal)
    strict_path = args.strict_terminal.parent / "identity.json"
    strict = load(strict_path)
    assert strict_terminal["identity_sha256"] == sha(strict_path)
    assert strict["status"] == "all54-strict-replays-and-eight-interruption-fixtures-pass"
    assert strict["source_before"] == strict["source_after"]
    assert all(stage["exit_code"] == 0 for stage in strict["stages"].values())
    strict_files = [strict_path]
    for label, stage in strict["stages"].items():
        filename = "profile-all" if label == "replay" else label
        for suffix in ("stdout", "stderr"):
            path = args.strict_terminal.parent / f"{filename}.{suffix}"
            assert sha(path) == stage[f"{suffix}_sha256"]
            strict_files.append(path)
    stage_paths = [args.build_terminal, args.native_terminal, args.strict_terminal]
    if args.parent_readiness is not None:
        parent = load(args.parent_readiness)
        assert parent["ready"] is True and parent["purpose"] == "material-allowance-census"
        for path in stage_paths:
            assert parent["input_sha256"][str(path)] == sha(path)
    files = [Path(__file__).resolve(), OUT / "reconcile.py", OUT / "README.md",
             prepared_path, archive, PREP / "census.patch", PREP / "README.md",
             args.build_receipt, args.engine, *stage_paths, *native_files, *strict_files, *logs, *frozen,
             SPEC / "workloads.json", SPEC / "replay-oracle.json", SPEC / "replay-check.mjs"]
    if args.parent_readiness is not None:
        files.append(args.parent_readiness)
    return prepared, {str(p): sha(p) for p in files}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--build-receipt", type=Path, default=BUILD / "receipt.json")
    parser.add_argument("--engine", type=Path, default=BUILD / "rook2-exact")
    parser.add_argument("--build-terminal", type=Path, default=BUILD / "tool-terminal.json")
    parser.add_argument("--native-terminal", type=Path, default=PREP / "native-tool-terminal.json")
    parser.add_argument("--strict-terminal", type=Path, required=True)
    parser.add_argument("--expected-engine-sha256", required=True)
    parser.add_argument("--parent-readiness", type=Path)
    args = parser.parse_args()
    for name in ("build_receipt", "engine", "build_terminal", "native_terminal", "strict_terminal"):
        setattr(args, name, getattr(args, name).resolve())
    if args.parent_readiness is not None:
        args.parent_readiness = args.parent_readiness.resolve()
    assert re.fullmatch("[0-9a-f]{64}", args.expected_engine_sha256)
    assert sorted(os.sched_getaffinity(0)) == HOUSEKEEPING
    assert not any((OUT / name).exists() for name in
                   ("manifest.json", "summary.json", "partial.json", "tool-terminal.json"))
    prepared, inputs = readiness(args)
    workloads = load(SPEC / "workloads.json")
    oracle = load(SPEC / "replay-oracle.json")
    cases = workloads["cases"]
    assert len(cases) == 54 and len({c["id"] for c in cases}) == 54
    assert all(c["lifetime"]["searches"] == 1 and c["protocol"]["searchRecord"] == "go"
               and c["protocol"]["cleanupRecord"] == "quit" for c in cases)
    assert all(not (OUT / c["id"]).exists() for c in cases)
    manifest = {
        "schema": "rook2-material-allowance-collection-v1",
        "started_utc": utc(), "case_order": [c["id"] for c in cases],
        "input_sha256": inputs, "helper_affinity": HOUSEKEEPING, "engine_affinity": [14],
        "engine": str(args.engine), "expected_engine_sha256": args.expected_engine_sha256,
        "build_receipt": str(args.build_receipt), "build_terminal": str(args.build_terminal),
        "native_terminal": str(args.native_terminal), "strict_terminal": str(args.strict_terminal),
        "parent_readiness": str(args.parent_readiness) if args.parent_readiness else None,
        "preparation": str(PREP / "prepared.json"), "source": prepared["path"],
        "counter_env": "ROOK2_MATERIAL_ALLOWANCE_PROBE",
        "interpretation": "Untimed frozen79 diagnostic source-demand opportunity only; no caching, CPU/PMU result or qualification.",
        "scope": "Last search segment after begin_sequence, root preparation excluded; every released case has one search.",
        "bounds": "Unchanged released checker owns setup/search/stream/cleanup limits; stop first failure.",
    }
    write_new(OUT / "manifest.json", manifest)
    rows = []
    for case in cases:
        name = case["id"]
        directory = OUT / name
        directory.mkdir()
        record = directory / "counts.json"
        command = ["/usr/bin/node", str(SPEC / "replay-check.mjs"), "--case", name, "--",
                   "/usr/bin/taskset", "-c", "14", str(args.engine)]
        write_new(directory / "invocation.json", {
            "command": command, "counter_env": {manifest["counter_env"]: str(record)},
            "engine_sha256_before": sha(args.engine), "started_utc": utc(),
        })
        assert sha(args.engine) == args.expected_engine_sha256
        env = dict(os.environ, ROOK2_MATERIAL_ALLOWANCE_PROBE=str(record))
        with (directory / "comparator.stdout").open("xb") as stdout, \
                (directory / "comparator.stderr").open("xb") as stderr:
            child = subprocess.run(command, env=env, stdout=stdout, stderr=stderr)
        write_new(directory / "comparator-terminal.json", {
            "origin": "Actual subprocess.run returncode observed by collector",
            "returncode": child.returncode, "finished_utc": utc(),
            "comparator_stdout_sha256": sha(directory / "comparator.stdout"),
            "comparator_stderr_sha256": sha(directory / "comparator.stderr"),
        })
        assert child.returncode == 0 and not (directory / "comparator.stderr").stat().st_size
        report = load(directory / "comparator.stdout")
        native = validate_report(report, name, args.engine, oracle,
                                 sha(SPEC / "workloads.json"), sha(SPEC / "replay-oracle.json"))
        counts = load(record)
        validate_counts(counts)
        raw = {str(directory / n): sha(directory / n) for n in
               ("counts.json", "comparator.stdout", "comparator.stderr",
                "comparator-terminal.json", "invocation.json")}
        rows.append({"case": name, "comparator_exit": child.returncode,
                     "native_pid": native["pid"], "native_exit": native["exit"],
                     "counts": counts, "derived": derived(counts), "raw_sha256": raw})
        with (OUT / "partial.json").open("w") as stream:
            json.dump(rows, stream, indent=2)
            stream.write("\n")
        print(json.dumps({"case": name, "q_calls": counts["q_calls"],
                          "ordinary_calls": counts["ordinary_calls"],
                          "avoided_endpoint_demands": derived(counts)["avoided_endpoint_demands"]}),
              flush=True)
    after = {name: sha(Path(name)) for name in inputs}
    assert after == inputs and len(rows) == 54
    totals = {"schema": "rook2-material-allowance-census-v1",
              **{k: sum(row["counts"][k] for row in rows) for k in SCALARS},
              **{k: [sum(row["counts"][k][i] for row in rows) for i in range(10)] for k in ARRAYS}}
    validate_counts(totals)
    summary = {"complete": True, "finished_utc": utc(), "rows": rows, "totals": totals,
               "derived": derived(totals), "input_sha256_after": after,
               "interpretation": manifest["interpretation"]}
    write_new(OUT / "summary.json", summary)
    print(json.dumps({"complete": True, "summary_sha256": sha(OUT / "summary.json"),
                      "derived": summary["derived"]}), flush=True)


if __name__ == "__main__":
    main()
