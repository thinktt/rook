#!/usr/bin/env python3
"""Focused released-fixture projections through rook2-dev inspect, not DIAG."""

import argparse
import collections
import datetime
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import time


HELPERS = {0, 1, 2, 3, 4, 5, 8, 9, 10, 11, 12, 13}
FIXTURES = [
    "position-setup-v1.json", "setup-move-sequence-v1.json",
    "identity-retention-v1.json", "evaluation-influence-v1.json",
    "square-relations-v1.json", "root-material-context-v1.json",
    "activity-v1.json", "positional-values-v1.json", "material-balance-v1.json",
]
KINDS = ("pawn", "knight", "bishop", "rook", "queen")


def digest(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def save(path, data):
    path.write_text(json.dumps(data, indent=2, allow_nan=False) + "\n")


def fen(query):
    return (f"{query['placement']} {'b' if query.get('sideToMove') == 'black' else 'w'} "
            f"{query.get('castling', '-')} {query.get('enPassant', '-')} 0 1")


def phase_key(phase):
    return tuple(phase[key] for key in ("opening", "middlegame", "endgame"))


def build_plan(spec):
    loaded = {name: json.loads((spec / name).read_text()) for name in FIXTURES}
    phase_cases = [case for case in loaded["root-material-context-v1.json"]["cases"]
                   if case["request"]["operation"] == "evaluation.phase"]
    known_phase = {case["request"]["input"]["placement"]: case["expected"]
                   for case in phase_cases}
    roots = {}
    for case in phase_cases:
        roots.setdefault(phase_key(case["expected"]), {
            "placement": case["request"]["input"]["placement"],
            "phase_fixture_case": case["id"]})
    jobs, unsupported = [], []

    def add(name, case, query_id, query, expected, projection, argv, omitted=(), bridge=None):
        jobs.append({"fixture": name, "case_id": case["id"],
                     "operation": case["request"]["operation"],
                     "query_id": query_id, "input": query,
                     "expected_projection": expected, "projection": projection,
                     "inspect_arguments": argv, "unsupported_fields": list(omitted),
                     "phase_bridge": bridge})

    def omit(name, case, reason):
        unsupported.append({"fixture": name, "case_id": case["id"],
                            "operation": case["request"]["operation"], "reason": reason})

    for name in FIXTURES:
        for case in loaded[name]["cases"]:
            op, query, expected = (case["request"]["operation"],
                                   case["request"]["input"], case["expected"])
            if op in ("position.setup", "position.identity", "evaluation.activity"):
                queries, answers = query["queries"], expected["results"]
                if len(queries) != len(answers):
                    raise ValueError(f"query/answer length mismatch: {case['id']}")
                for index, (item, answer) in enumerate(zip(queries, answers)):
                    argv = ["--fen", fen(item)]
                    omitted = []
                    if op == "evaluation.activity":
                        weights = item["activityWeights"]
                        argv += ["--activity-weights", f"{weights['white']},{weights['black']}",
                                 "--activity-material", str(item["materialScore"])]
                        fields = ("phase", "pieces", "activityPressure", "weightedActivity", "relationQueries")
                        answer = {key: answer[key] for key in fields}
                        omitted = ["expected.positionTerms", "input.positionWeights (only omitted positionTerms)"]
                    add(name, case, index, item, answer, op, argv, omitted)
            elif op == "position.setupMoveSequence":
                if len(expected["results"]) != len(query["moves"]) + 1:
                    raise ValueError(f"prefix/answer length mismatch: {case['id']}")
                for index, answer in enumerate(expected["results"]):
                    item = {"fen": query["fen"], "moves": query["moves"][:index]}
                    add(name, case, index, item, answer, op,
                        ["--fen", item["fen"], "--moves", " ".join(item["moves"])])
            elif op == "evaluation.influence":
                if len(query["queries"]) != len(expected["profiles"]):
                    raise ValueError(f"influence query/answer mismatch: {case['id']}")
                add(name, case, "ordered-square-queries", query,
                    {"profiles": expected["profiles"]}, op, ["--fen", fen(query)],
                    ["expected.chargedRelationQueries (not exposed by inspect)"])
            elif op == "evaluation.phase":
                add(name, case, 0, query, expected, op, ["--fen", fen(query)])
            elif op == "evaluation.rootMaterial":
                placement = query["placement"]
                counts = {side: {kind: placement.count(symbol if side == "black" else symbol.upper())
                                 for kind, symbol in zip(KINDS, "pnbrq")}
                          for side in ("white", "black")}
                neutral = all(value == 100 for side in query["materialPercent"].values()
                              for value in side.values())
                if query["averageDepth"] == 0 and neutral and query["currentCounts"] == counts:
                    add(name, case, 0, query, {key: expected[key] for key in ("phase", "score")}, op,
                        ["--fen", fen({"placement": placement, "sideToMove": query["rootSide"]})],
                        ["expected.values (not exposed by inspect)"])
                else:
                    omit(name, case, "inspect cannot supply nonneutral material percentages, changed currentCounts, or averageDepth")
            elif op == "evaluation.squareBalance":
                root = roots.get(phase_key(query["rootPhase"]))
                if known_phase.get(query["placement"]) == query["phase"] and root is not None:
                    add(name, case, 0, query,
                        {"balance": expected["balance"], "phase": query["phase"]}, op,
                        ["--fen", fen(query), "--root-fen", fen(root)],
                        ["expected.chargedRelationQueries (not exposed by inspect)"], root)
                else:
                    omit(name, case, "supplied current/root phases not representable by declared released phase-placement bridge")
            else:
                omit(name, case, "operation not exposed by inspect; no relation/score algorithm emulated in checker")
    return {"jobs": jobs, "unsupported_cases": unsupported,
            "fixture_sha256": {name: digest(spec / name) for name in FIXTURES},
            "scope": "selected exact projections only; no DIAG transport or mandatory conformance claim",
            "phase_bridge_policy": "current placement phase must be independently supplied by a selected evaluation.phase fixture; rootPhase selects a placement from those fixtures; all selected phase assertions are run",
            "scope_limits": ["no relation/adjusted-relation classifier output",
                             "no activity positionTerms", "no supplied material value tables",
                             "no arbitrary externally supplied phase",
                             "no legalMoves oracle (inventory is produced but not compared)",
                             "query receipt and correctness timings are not engine performance measurements"]}


def project(job, actual):
    op = job["projection"]
    if op == "position.identity":
        return actual["identity"]
    if op in ("position.setup", "position.setupMoveSequence"):
        result = {key: actual[key] for key in job["expected_projection"] if key != "pieceSequence"}
        if "pieceSequence" in job["expected_projection"]:
            result["pieceSequence"] = {}
            for side in ("white", "black"):
                order = actual["pieceOrder"][side]
                remaining = [square for kind in KINDS for square in order[kind]]
                # Cold setup's sequence is king first, then remaining actual
                # reported pieces in a1..h8 order; chronology is not reconstructed.
                remaining.sort(key=lambda square: (square[1], square[0]))
                result["pieceSequence"][side] = order["king"] + remaining
        return result
    if op == "evaluation.phase":
        return actual["phase"]
    if op == "evaluation.influence":
        profiles = []
        for query in job["input"]["queries"]:
            square = query["square"]
            index = (ord(square[1]) - ord('1')) * 8 + ord(square[0]) - ord('a')
            code = actual["influenceCodes"][query["side"] == "black"][index]
            profiles.append({"weak": code & 1, "queen": (code >> 1) & 1,
                             "rook": (code >> 2) & 3, "minor": (code >> 4) & 3,
                             "pawn": code >> 6})
        return {"profiles": profiles}
    if op == "evaluation.activity":
        return {"phase": actual["phase"], **actual["activity"]}
    if op == "evaluation.rootMaterial":
        return {"phase": actual["phase"], "score": actual["material"]}
    if op == "evaluation.squareBalance":
        return {"phase": actual["phase"], "balance": actual["squareBalance"]}
    raise ValueError(f"unsupported projection: {op}")


def differences(expected, actual, path=""):
    if type(expected) is not type(actual):
        return [{"path": path, "expected": expected, "actual": actual}]
    if isinstance(expected, dict):
        if set(expected) != set(actual):
            return [{"path": path, "expected_keys": sorted(expected), "actual_keys": sorted(actual)}]
        return [difference for key in expected
                for difference in differences(expected[key], actual[key], path + "/" + key)]
    if isinstance(expected, list):
        if len(expected) != len(actual):
            return [{"path": path, "expected_length": len(expected), "actual_length": len(actual)}]
        return [difference for index, (left, right) in enumerate(zip(expected, actual))
                for difference in differences(left, right, path + "/" + str(index))]
    return [] if expected == actual else [{"path": path, "expected": expected, "actual": actual}]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--engine", required=True, type=Path)
    parser.add_argument("--expect-sha256", required=True)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--fixtures", type=Path,
                        default=Path('/home/legolas/king-spec/conformance/fixtures'))
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    if args.output.exists() or args.output.is_symlink() or not args.output.parent.is_dir():
        parser.error("output must be a fresh directory with existing parent")
    if not HELPERS <= os.sched_getaffinity(0):
        parser.error("housekeeping CPUs must be available")
    engine_hash = digest(args.engine)
    if engine_hash != args.expect_sha256:
        parser.error("source executable hash does not match requested artifact")
    plan = build_plan(args.fixtures)
    plan.update({"source_engine": str(args.engine.resolve()), "source_engine_sha256": engine_hash,
                 "checker_sha256": digest(Path(__file__).resolve()),
                 "per_process_timeout_s": 2, "aggregate_timeout_s": 30,
                 "helper_cpus": sorted(HELPERS)})
    if args.dry_run:
        print(json.dumps({"launches": len(plan["jobs"]),
                          "unsupported_cases": len(plan["unsupported_cases"]),
                          "fixture_sha256": plan["fixture_sha256"]}, indent=2))
        return 0
    args.output.mkdir()
    (args.output / "runs").mkdir()
    staged = args.output / "rook2-dev-exact"
    shutil.copyfile(args.engine, staged)
    staged.chmod(0o500)
    if digest(staged) != engine_hash:
        raise RuntimeError("staged artifact changed while copied")
    save(args.output / "plan.json", plan)
    original = os.sched_getaffinity(0)
    start = time.monotonic()
    summary = {"started_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
               "conformance_claim": False, "performance_claim": False,
               "planned_launches": len(plan["jobs"]), "records": [],
               "initial_affinity": sorted(original), "unsupported_cases": plan["unsupported_cases"],
               "scope_limits": plan["scope_limits"], "source_engine_sha256": engine_hash}
    try:
        os.sched_setaffinity(0, HELPERS)
        summary["execution_affinity"] = sorted(os.sched_getaffinity(0))
        for index, job in enumerate(plan["jobs"]):
            remaining = 30 - (time.monotonic() - start)
            if remaining <= 0:
                break
            directory = args.output / "runs" / f"{index:05d}"
            directory.mkdir()
            argv = [str(staged.resolve()), "inspect", *job["inspect_arguments"]]
            record = {"index": index, "fixture": job["fixture"], "case_id": job["case_id"],
                      "operation": job["operation"], "query_id": job["query_id"],
                      "input": job["input"], "argv": argv,
                      "binary_sha256": engine_hash,
                      "fixture_sha256": plan["fixture_sha256"][job["fixture"]],
                      "unsupported_fields": job["unsupported_fields"],
                      "expected_projection": job["expected_projection"], "passed": False}
            began = time.monotonic()
            stdout = stderr = b""
            try:
                result = subprocess.run(argv, capture_output=True, timeout=min(2, remaining))
                stdout, stderr = result.stdout, result.stderr
                record["exit_code"] = result.returncode
                if result.returncode != 0 or stderr:
                    record["failure"] = "nonzero-exit-or-stderr"
                else:
                    actual = json.loads(stdout)
                    if actual.get("schema") != "rook2-development-inspect-v1":
                        raise ValueError("unexpected inspect schema")
                    observed = project(job, actual)
                    record["actual_projection"] = observed
                    mismatch = differences(job["expected_projection"], observed)
                    record["difference_count"] = len(mismatch)
                    record["differences"] = mismatch[:20]
                    record["passed"] = not mismatch
                    if mismatch:
                        record["failure"] = "projection-mismatch"
            except subprocess.TimeoutExpired as error:
                stdout, stderr = error.stdout or b"", error.stderr or b""
                record["failure"] = "process-timeout; incomplete"
            except (ValueError, KeyError, TypeError, IndexError, OSError) as error:
                record["failure"] = f"collection-or-projection-error:{type(error).__name__}:{error}"
            record["elapsed_s"] = time.monotonic() - began
            (directory / "stdout.raw").write_bytes(stdout)
            (directory / "stderr.raw").write_bytes(stderr)
            save(directory / "record.json", record)
            summary["records"].append({key: record[key] for key in
                                        ("index", "fixture", "case_id", "query_id", "operation", "passed")}
                                       | {"record": f"runs/{index:05d}/record.json",
                                          "failure": record.get("failure")})
    finally:
        os.sched_setaffinity(0, original)
        summary["restored_affinity"] = sorted(os.sched_getaffinity(0))
        summary["elapsed_s"] = time.monotonic() - start
        summary["executed_launches"] = len(summary["records"])
        summary["complete_selected_schedule"] = len(summary["records"]) == len(plan["jobs"])
        summary["unexecuted_jobs"] = [{key: job[key] for key in
                                       ("fixture", "case_id", "query_id", "operation")}
                                      for job in plan["jobs"][len(summary["records"]):]]
        summary["counts"] = dict(collections.Counter(
            "passed" if record["passed"] else "failed" for record in summary["records"]))
        summary["staged_engine_sha256_after"] = digest(staged)
        summary["source_engine_sha256_after"] = digest(args.engine)
        summary["artifact_identity_stable"] = summary["staged_engine_sha256_after"] == engine_hash
        save(args.output / "summary.json", summary)
    print(json.dumps({key: summary[key] for key in
                      ("executed_launches", "complete_selected_schedule", "counts", "elapsed_s",
                       "conformance_claim", "performance_claim")}
                     | {"output": str(args.output)}))
    return 0 if (summary["complete_selected_schedule"] and summary["artifact_identity_stable"]
                 and not summary["counts"].get("failed")) else 1


if __name__ == "__main__":
    raise SystemExit(main())
