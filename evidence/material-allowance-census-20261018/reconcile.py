#!/usr/bin/env python3
"""Independently reread completed raw census records; never launch any engine."""
import argparse
import hashlib
import json
from pathlib import Path
import tarfile

OUT = Path(__file__).resolve().parent
SPEC = Path("/home/legolas/king-spec/conformance/profiling")
HOUSEKEEPING = [0, 1, 2, 3, 4, 5, 8, 9, 10, 11, 12, 13]


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def object_once(pairs):
    answer = {}
    for name, value in pairs:
        assert name not in answer, ("duplicate key", name)
        answer[name] = value
    return answer


def read(path):
    return json.loads(path.read_text(), object_pairs_hook=object_once)


def actual_success(path):
    record = read(path)
    assert type(record.get("exit_code")) is int and record["exit_code"] == 0
    assert type(record.get("session_id")) is int and record["session_id"] > 0
    assert isinstance(record.get("chunk_id"), str) and record["chunk_id"]
    assert isinstance(record.get("origin"), str) and "actual" in record["origin"].lower()
    return record


def count_rules(value):
    scalar = {"full", "fast"}
    array = set()
    for prefix in ("q", "ordinary"):
        scalar.update(prefix + "_" + n for n in
                      ("loops", "checked_loops", "nonempty_loops", "calls",
                       "unique_keys", "old_endpoints", "lazy_endpoints"))
        array.update(prefix + "_" + n for n in ("calls_by_victim", "unique_by_victim"))
    assert set(value) == scalar | array | {"schema"}
    assert value["schema"] == "rook2-material-allowance-census-v1"
    for name in scalar:
        assert type(value[name]) is int and value[name] >= 0
    for name in array:
        assert type(value[name]) is list and len(value[name]) == 10
        assert all(type(n) is int and n >= 0 for n in value[name])
    for prefix in ("q", "ordinary"):
        loops = value[prefix + "_loops"]
        checked = value[prefix + "_checked_loops"]
        active = value[prefix + "_nonempty_loops"]
        calls = value[prefix + "_calls"]
        keys = value[prefix + "_unique_keys"]
        assert checked <= loops and active <= loops
        assert active <= keys <= calls and keys <= 5 * active
        assert value[prefix + "_old_endpoints"] == calls + calls
        assert value[prefix + "_lazy_endpoints"] == active + keys
        assert active + keys <= calls + calls
        per_call = value[prefix + "_calls_by_victim"]
        per_key = value[prefix + "_unique_by_victim"]
        assert sum(per_call) == calls and sum(per_key) == keys
        for index in range(10):
            assert per_key[index] <= per_call[index]
        if prefix == "q":
            assert active <= loops - checked
    return scalar, array


def independent_model(value):
    endpoint_requests = 2 * (value["q_calls"] + value["ordinary_calls"])
    demand = value["full"] + value["fast"] + endpoint_requests
    fractions = lambda a, b: a / b if b != 0 else None
    local = {}
    saved_total = 0
    for prefix in ("q", "ordinary"):
        saved = (2 * value[prefix + "_calls"] - value[prefix + "_nonempty_loops"]
                 - value[prefix + "_unique_keys"])
        saved_total += saved
        local[prefix] = {
            "zero_call_loops": value[prefix + "_loops"] - value[prefix + "_nonempty_loops"],
            "avoided_endpoint_demands": saved,
            "avoided_fraction_of_allowance_endpoints": fractions(saved, 2 * value[prefix + "_calls"]),
            "avoided_fraction_of_segment_material_demands": fractions(saved, demand),
        }
    return {
        "families": local,
        "segment_material_demands": demand,
        "allowance_old_endpoint_demands": endpoint_requests,
        "allowance_lazy_endpoint_model": endpoint_requests - saved_total,
        "avoided_endpoint_demands": saved_total,
        "allowance_fraction_of_segment_material_demands": fractions(endpoint_requests, demand),
        "avoided_fraction_of_segment_material_demands": fractions(saved_total, demand),
        "scope": "Source requests after begin_sequence; excludes root-preparation full. Not emitted calls or CPU gain.",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--terminal", type=Path, default=OUT / "tool-terminal.json")
    args = parser.parse_args()
    manifest = read(OUT / "manifest.json")
    summary = read(OUT / "summary.json")
    terminal = actual_success(args.terminal.resolve())
    assert terminal["summary_sha256"] == digest(OUT / "summary.json")
    if "manifest_sha256" in terminal:
        assert terminal["manifest_sha256"] == digest(OUT / "manifest.json")
    assert manifest["schema"] == "rook2-material-allowance-collection-v1"
    assert manifest["helper_affinity"] == HOUSEKEEPING and manifest["engine_affinity"] == [14]
    assert manifest["counter_env"] == "ROOK2_MATERIAL_ALLOWANCE_PROBE"
    assert summary["complete"] is True
    assert manifest["input_sha256"] == summary["input_sha256_after"]
    for filename, identity in manifest["input_sha256"].items():
        assert digest(Path(filename)) == identity, filename
    workloads = read(SPEC / "workloads.json")
    oracle = read(SPEC / "replay-oracle.json")
    order = [case["id"] for case in workloads["cases"]]
    assert manifest["case_order"] == order and len(order) == 54 and len(set(order)) == 54
    assert len(summary["rows"]) == 54
    for case in workloads["cases"]:
        assert case["lifetime"]["searches"] == 1
        assert case["protocol"]["searchRecord"] == "go" and case["protocol"]["cleanupRecord"] == "quit"
    engine = Path(manifest["engine"])
    assert digest(engine) == manifest["expected_engine_sha256"]
    prepared_path = Path(manifest["preparation"])
    prepared = read(prepared_path)
    build_path = Path(manifest["build_receipt"])
    build = read(build_path)
    assert build["schema"] == "rook2-development-build-v1"
    assert build["crate"] == manifest["source"] == prepared["path"]
    assert build["binary_name"] == "rook2-material-allowance-probe"
    assert build["source_sha256_before"] == build["source_sha256_after"] == prepared["variant_source_sha256"]
    assert build["source_identity_unchanged"] is True and build["tool_identity_unchanged"] is True
    assert build["cargo_config_unchanged"] is True and build["cargo_exit_code"] == 0
    assert build["outcome"] == "build-succeeded-with-stable-input-snapshot"
    assert build["binary_output"]["sha256"] == digest(engine)
    tools = {name: identity for name, identity in prepared["archive_files"].items()
             if name.startswith("tools/")}
    assert build["tool_sha256_before"] == build["tool_sha256_after"] == tools
    assert build["source_archive"]["verified_against_before_hashes"] is True
    frozen_path = Path(build["source_archive"]["path"])
    if not frozen_path.is_absolute():
        frozen_path = build_path.parent / frozen_path
    for filename, identity in (prepared["variant_source_sha256"] | tools).items():
        path = frozen_path / filename
        assert digest(path) == identity
        assert manifest["input_sha256"][str(path)] == identity
    for log in build["logs"].values():
        path = build_path.parent / log["path"]
        assert digest(path) == log["sha256"] and path.stat().st_size == log["bytes"]
    build_done = actual_success(Path(manifest["build_terminal"]))
    assert build_done.get("receipt_sha256", build_done.get("build_json_sha256")) == digest(build_path)
    assert build_done["native_artifact_sha256"] == digest(engine)
    native_done = actual_success(Path(manifest["native_terminal"]))
    native_path = Path(manifest["native_terminal"]).parent / "native-verification.json"
    native_proof = read(native_path)
    assert native_done["native_verification_sha256"] == digest(native_path)
    assert native_proof["complete"] is True and native_proof["failure"] is None
    assert native_proof["inputs_stable"] is True
    assert native_proof["source_before"] == native_proof["source_after"] == prepared["variant_source_sha256"]
    assert len(native_proof["stages"]) == 3
    assert all(stage["exit_code"] == 0 for stage in native_proof["stages"])
    assert native_proof["units"]["rook2"]["passed"] == 133
    assert native_proof["units"]["rook2-dev"]["passed"] == 2
    strict_done = actual_success(Path(manifest["strict_terminal"]))
    strict_path = Path(manifest["strict_terminal"]).parent / "identity.json"
    strict_proof = read(strict_path)
    assert strict_done["identity_sha256"] == digest(strict_path)
    assert strict_proof["status"] == "all54-strict-replays-and-eight-interruption-fixtures-pass"
    assert strict_proof["source_before"] == strict_proof["source_after"]
    assert all(stage["exit_code"] == 0 for stage in strict_proof["stages"].values())
    if manifest["parent_readiness"] is not None:
        ready = read(Path(manifest["parent_readiness"]))
        assert ready["ready"] is True and ready["purpose"] == "material-allowance-census"
        for name in ("build_terminal", "native_terminal", "strict_terminal"):
            assert ready["input_sha256"][manifest[name]] == digest(Path(manifest[name]))
    archive = prepared_path.parent / prepared["archive"]
    assert digest(archive) == prepared["archive_sha256"]
    with tarfile.open(archive, "r:gz") as handle:
        all_members = list(handle)
        assert all(item.isfile() for item in all_members)
        archived = {item.name: hashlib.sha256(handle.extractfile(item).read()).hexdigest()
                    for item in all_members}
        assert len(archived) == len(all_members) and archived == prepared["archive_files"]
    raw_hashes = {}
    calculated_rows = []
    scalar_names = array_names = None
    totals = None
    for case, row in zip(order, summary["rows"]):
        assert row["case"] == case and row["comparator_exit"] == 0
        directory = OUT / case
        counts = read(directory / "counts.json")
        scalar_names, array_names = count_rules(counts)
        assert counts == row["counts"] and independent_model(counts) == row["derived"]
        report = read(directory / "comparator.stdout")
        assert not (directory / "comparator.stderr").stat().st_size
        assert report["status"] == "pass" and report["selectedCases"] == [case]
        assert report["fixture"] == oracle["id"] and len(report["results"]) == 1
        assert report["workloadSha256"] == digest(SPEC / "workloads.json")
        assert report["oracleSha256"] == digest(SPEC / "replay-oracle.json")
        native = report["results"][0]
        assert native["case"] == case and native["status"] == "pass"
        assert native["complete"] is True and native["truncated"] is False
        assert native["error"] is None and native["discardedObservedBytes"] == 0
        assert native["exit"] == row["native_exit"] == {"code": 0, "signal": None}
        assert type(native["pid"]) is int and native["pid"] > 0 and native["pid"] == row["native_pid"]
        assert native["stderr"] == "" and isinstance(native["stdout"], str)
        assert native["command"] == ["/usr/bin/taskset", "-c", "14", str(engine), *oracle["mode"]]
        invocation = read(directory / "invocation.json")
        assert invocation["command"] == [
            "/usr/bin/node", str(SPEC / "replay-check.mjs"), "--case", case, "--",
            "/usr/bin/taskset", "-c", "14", str(engine)]
        assert invocation["counter_env"] == {"ROOK2_MATERIAL_ALLOWANCE_PROBE": str(directory / "counts.json")}
        assert invocation["engine_sha256_before"] == digest(engine)
        completion = read(directory / "comparator-terminal.json")
        assert completion["origin"] == "Actual subprocess.run returncode observed by collector"
        assert completion["returncode"] == 0
        assert completion["comparator_stdout_sha256"] == digest(directory / "comparator.stdout")
        assert completion["comparator_stderr_sha256"] == digest(directory / "comparator.stderr")
        original = {str(directory / name): digest(directory / name) for name in
                    ("counts.json", "comparator.stdout", "comparator.stderr",
                     "comparator-terminal.json", "invocation.json")}
        assert original == row["raw_sha256"]
        raw_hashes.update(original)
        calculated_rows.append({"case": case, "derived": independent_model(counts)})
        if totals is None:
            totals = {"schema": counts["schema"], **{k: 0 for k in scalar_names},
                      **{k: [0] * 10 for k in array_names}}
        for name in scalar_names:
            totals[name] += counts[name]
        for name in array_names:
            for index, value in enumerate(counts[name]):
                totals[name][index] += value
    count_rules(totals)
    assert totals == summary["totals"]
    model = independent_model(totals)
    assert model == summary["derived"]
    result = {
        "complete": True, "strict_cases_independently_reconciled": 54,
        "totals": totals, "derived": model, "per_case_derived": calculated_rows,
        "raw_file_sha256": raw_hashes,
        "input_receipts_sha256": manifest["input_sha256"],
        "terminal_sha256": digest(args.terminal.resolve()),
        "manifest_sha256": digest(OUT / "manifest.json"),
        "summary_sha256": digest(OUT / "summary.json"),
        "reconciler_sha256": digest(Path(__file__).resolve()),
        "interpretation": "Opportunity source requests only, not CPU gain, emitted call counts, implementation selection or qualification.",
    }
    with (OUT / "verification.json").open("x") as stream:
        json.dump(result, stream, indent=2)
        stream.write("\n")
    print(json.dumps({"complete": True, "strict_cases_independently_reconciled": 54,
                      "derived": model}))


if __name__ == "__main__":
    main()
