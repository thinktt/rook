#!/usr/bin/env python3
"""Prepare an exact local payload and proposed finite schedule; never execute it."""
import hashlib
import json
import os
from pathlib import Path
import shutil

REPO = Path("/home/legolas/rook2")
SPEC = Path("/home/legolas/king-spec")
ARCHIVE = Path("/home/legolas/rook2-experiments/original-worktree")
OUTPUT = Path("/home/legolas/rook2-experiments/retained62-external-comparison-preparation-20261020-01")
IMAGES = {
    "rook2": (
        ARCHIVE / "evidence/exttsp-profiled-pgo-use-build-20261020-01/rook2-exact",
        "01237e6dfe89822e540d0f07c7b70f7227537a846ce8c69ea9e91167b759e98d",
    ),
    "rook2-diag": (
        ARCHIVE / "evidence/bitplane-pin-summary-conformance-build-20261020-01/rook2-diag-exact",
        "eda652abd182cb536736dd758d330f779e94b1e7ad0e779ff7792c2235fffde2",
    ),
}


def sha(path):
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def write_json(path, value):
    with path.open("x") as output:
        json.dump(value, output, indent=2)
        output.write("\n")


def main():
    inventory_path = SPEC / "performance/inventory.json"
    inventory = json.loads(inventory_path.read_text())
    corpus = inventory["corpus"]
    pins = {}
    for path_key, hash_key in [
        ("path", "sha256"),
        ("oraclePath", "oracleSha256"),
        ("checkerPath", "checkerSha256"),
    ]:
        path = (SPEC / "performance" / corpus[path_key]).resolve()
        observed = sha(path)
        assert observed == corpus[hash_key], (path, observed)
        pins[str(path)] = observed
    workloads_path = (SPEC / "performance" / corpus["path"]).resolve()
    workloads = json.loads(workloads_path.read_text())
    cases = [case["id"] for case in workloads["cases"]]
    assert len(cases) == len(set(cases)) == 54
    assert inventory["reference"]["binarySha256"] == (
        "bf71485c48e780e29f32813219e4283cc54c04015abce0bccda62c190e2ba080"
    )
    promotion_path = ARCHIVE / "evidence/exttsp-profiled-integration-20261020-01/source-promotion.json"
    promotion = json.loads(promotion_path.read_text())
    mismatches = [
        name for name, expected in promotion["files_sha256"].items()
        if not (REPO / name).is_file() or sha(REPO / name) != expected
    ]
    assert not mismatches, mismatches
    for source, expected in IMAGES.values():
        assert sha(source) == expected, str(source)
    for path in [
        inventory_path, promotion_path,
        ARCHIVE / "evidence/exttsp-profiled-pgo-use-build-20261020-01/receipt.json",
        REPO / "experiments/retained62-reference-pair/README.md",
        Path(__file__).resolve(),
    ]:
        pins[str(path)] = sha(path)

    # Refuse replacement of an earlier preparation, even when contents match.
    OUTPUT.mkdir()
    payload = OUTPUT / "payload"
    payload.mkdir()
    members = {}
    for name, (source, expected) in IMAGES.items():
        destination = payload / name
        shutil.copyfile(source, destination)
        os.chmod(destination, 0o555)
        assert sha(destination) == expected
        members[name] = {
            "path": str(destination), "origin": str(source), "sha256": expected,
            "bytes": destination.stat().st_size, "mode": "0555",
        }
    schedule = []
    for case_index, case in enumerate(cases):
        for repetition in range(4):
            order = ["reference", "candidate"]
            if (case_index + repetition) % 2:
                order.reverse()
            for variant in order:
                schedule.append({
                    "case": case, "variant": variant,
                    "repetition": repetition, "warmup": repetition == 0,
                })
    assert len(schedule) == 432
    assert sum(row["warmup"] for row in schedule) == 108
    write_json(OUTPUT / "schedule.json", schedule)
    manifest = {
        "status": "prepared-locally-external-authority-pending",
        "candidate": 62,
        "reference_sha256": inventory["reference"]["binarySha256"],
        "package_members": members,
        "canonical_source_files_verified": len(promotion["files_sha256"]),
        "source_graph_sha256": promotion["source_graph_sha256"],
        "native_source_graph_sha256": promotion["native_source_graph_sha256"],
        "input_and_provenance_sha256": pins,
        "schedule_sha256": sha(OUTPUT / "schedule.json"),
        "lifetimes_requested": 432,
        "warmups": 108,
        "measured": 324,
        "launch_flags": corpus["launchFlags"],
        "seed_policy": corpus["seedPolicy"],
        "external_transfer_or_contact": False,
        "engine_executions": 0,
        "diagnostic_executions_selected": False,
        "performance_acceptance": False,
        "external_full_game_gate": False,
    }
    write_json(OUTPUT / "manifest.json", manifest)
    write_json(REPO / "experiments/retained62-reference-pair/prepared.json", {
        "status": manifest["status"],
        "preparation": str(OUTPUT),
        "manifest_sha256": sha(OUTPUT / "manifest.json"),
        "schedule_sha256": manifest["schedule_sha256"],
        "canonical_source_files_verified": manifest["canonical_source_files_verified"],
        "engine_executions": 0,
        "external_transfer_or_contact": False,
    })
    print(json.dumps({
        "prepared": str(OUTPUT), "source_files_verified": len(promotion["files_sha256"]),
        "payload_hashes_verified": len(members), "schedule_lifetimes": len(schedule),
        "engine_executions": 0, "external_transfer_or_contact": False,
    }))


if __name__ == "__main__":
    main()
