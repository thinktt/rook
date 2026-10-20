#!/usr/bin/env python3
"""Offline development builds with explicit CPU target and retained evidence."""

from __future__ import annotations

import argparse
import datetime
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time


HELPERS = {0, 1, 2, 3, 4, 5, 8, 9, 10, 11, 12, 13}
TARGET = "x86_64-unknown-linux-gnu"


def digest(path: Path) -> str:
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def utc() -> str:
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def command_record(argv: list[str], cwd: Path, env: dict) -> dict:
    result = subprocess.run(argv, cwd=cwd, env=env, capture_output=True, text=True)
    return {"argv": argv, "exit_code": result.returncode,
            "stdout": result.stdout, "stderr": result.stderr}


def source_snapshot(root: Path) -> dict:
    paths = [root / "Cargo.toml", root / "Cargo.lock"]
    paths += sorted(path for path in (root / "src").rglob("*") if path.is_file())
    for name in ("build.rs", "rust-toolchain", "rust-toolchain.toml"):
        if (root / name).is_file():
            paths.append(root / name)
    return {str(path.relative_to(root)): digest(path) for path in paths}


def tool_snapshot(root: Path) -> dict:
    paths = sorted(path for path in (root / "tools").rglob("*")
                   if path.is_file() and "__pycache__" not in path.parts
                   and path.suffix in (".py", ".c", ".rs", ".md", ".sh", ".mjs"))
    return {str(path.relative_to(root)): digest(path) for path in paths}


def archive_sources(root: Path, output: Path, expected: dict) -> dict:
    """Capture exact pre-build bytes, reject races against the bound snapshot."""
    archive = output / "source-before"
    archive.mkdir()
    total_bytes = 0
    for name, expected_hash in expected.items():
        data = (root / name).read_bytes()
        if hashlib.sha256(data).hexdigest() != expected_hash:
            raise ValueError(f"source changed before archive capture: {name}")
        destination = archive / name
        destination.parent.mkdir(parents=True, exist_ok=True)
        with destination.open("xb") as stream:
            stream.write(data)
        if digest(destination) != expected_hash:
            raise ValueError(f"archived bytes do not match pre-build hash: {name}")
        total_bytes += len(data)
    if source_snapshot(root) | tool_snapshot(root) != expected:
        raise ValueError("source tree changed during pre-build archive capture")
    return {"path": "source-before", "file_count": len(expected),
            "total_bytes": total_bytes, "verified_against_before_hashes": True,
            "source_rechecked_before_build": True}


def cargo_configs(root: Path) -> dict:
    paths = set()
    for parent in [root, *root.parents]:
        paths.update(parent / ".cargo" / name for name in ("config", "config.toml"))
    cargo_home = Path(os.environ.get("CARGO_HOME", str(Path.home() / ".cargo")))
    paths.update(cargo_home / name for name in ("config", "config.toml"))
    return {str(path): digest(path) for path in sorted(paths) if path.is_file()}


def git_snapshot(root: Path, env: dict) -> dict:
    git = shutil.which("git")
    if git is None:
        return {"available": False}
    return {
        "head": command_record([git, "rev-parse", "--verify", "HEAD"], root, env),
        "status": command_record(
            [git, "status", "--porcelain=v1", "--untracked-files=all"], root, env),
    }


def write_receipt(path: Path, receipt: dict) -> None:
    temporary = path.with_suffix(".json.tmp")
    with temporary.open("x") as stream:
        json.dump(receipt, stream, indent=2, allow_nan=False)
        stream.write("\n")
    temporary.replace(path)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, type=Path,
                        help="fresh absent receipt directory; parent must exist")
    parser.add_argument("--crate", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--mode", choices=("generic", "native"), default="generic")
    parser.add_argument("--jobs", type=int, default=4)
    parser.add_argument("--bin", dest="binary_name", help="build and hash this Cargo binary target")
    pgo = parser.add_mutually_exclusive_group()
    pgo.add_argument("--pgo-generate", type=Path,
                     help="compiler instrumentation only; fresh absent profile directory")
    pgo.add_argument("--pgo-use", type=Path,
                     help="immutable merged profile; requires --training-record")
    parser.add_argument("--training-record", type=Path,
                        help="completed native training provenance for --pgo-use")
    parser.add_argument("--ext-tsp-profiled", action="store_true",
                        help="use-only ExtTSP placement for profile-covered functions; requires --pgo-use")
    parser.add_argument("--dry-run", action="store_true",
                        help="inspect sources/tools and print plan; do not build or write receipts")
    args = parser.parse_args()
    try:
        root = args.crate.resolve(strict=True)
        if not root.is_dir() or not (root / "Cargo.toml").is_file() or not (root / "Cargo.lock").is_file():
            raise ValueError("crate must contain Cargo.toml and Cargo.lock; helper never generates or updates the lockfile")
        output = args.output.absolute()
        if output.exists() or output.is_symlink() or not output.parent.is_dir():
            raise ValueError("receipt output must be absent with an existing parent directory")
        if not 1 <= args.jobs <= len(HELPERS):
            raise ValueError("jobs must be 1..12 (default 4)")
        if args.binary_name is not None and (not args.binary_name or any(
                character in args.binary_name for character in ("/", "\\"))):
            raise ValueError("--bin must be a Cargo binary target name, not a path")
        if (args.pgo_generate or args.pgo_use) and args.binary_name != "rook2":
            raise ValueError("PGO recording currently supports only --bin rook2")
        if args.training_record and not args.pgo_use:
            raise ValueError("--training-record requires --pgo-use")
        if args.ext_tsp_profiled and not args.pgo_use:
            raise ValueError("--ext-tsp-profiled requires --pgo-use")
        if args.pgo_generate:
            args.pgo_generate = args.pgo_generate.absolute()
            if (args.pgo_generate.exists() or args.pgo_generate.is_symlink()
                    or not args.pgo_generate.parent.is_dir()):
                raise ValueError("profile generation directory must be absent with an existing parent")
        pgo_input = None
        if args.pgo_use:
            if args.training_record is None:
                raise ValueError("--pgo-use requires a completed --training-record")
            args.pgo_use = args.pgo_use.resolve(strict=True)
            args.training_record = args.training_record.resolve(strict=True)
            training = json.loads(args.training_record.read_text())
            cpu = "x86-64" if args.mode == "generic" else "native"
            if (training.get("schema") != "rook2-pgo-training-v1"
                    or training.get("complete") is not True
                    or training.get("engine_source_sha256") != source_snapshot(root)
                    or training.get("target_triple") != TARGET
                    or training.get("base_rust_flags") != ["-C", f"target-cpu={cpu}"]
                    or training.get("profile_sha256") != digest(args.pgo_use)):
                raise ValueError("training provenance does not match source, CPU target or merged profile")
            pgo_input = {str(path): digest(path)
                         for path in (args.pgo_use, args.training_record)}
        if not HELPERS <= os.sched_getaffinity(0):
            raise ValueError("inherited affinity must permit all housekeeping CPUs")
        cargo = shutil.which("cargo")
        rustc = shutil.which("rustc")
        if cargo is None or rustc is None:
            raise ValueError("cargo and rustc must be installed on PATH")
    except (OSError, ValueError) as error:
        parser.error(str(error))

    original_affinity = os.sched_getaffinity(0)
    receipt = {}
    exit_code = 1
    try:
        os.sched_setaffinity(0, HELPERS)
        cpu = "x86-64" if args.mode == "generic" else "native"
        flags = ["-C", f"target-cpu={cpu}"]
        pgo_record = {"mode": "none", "training_runs_by_build_helper": 0}
        build_mode = "dev-" + args.mode
        if args.pgo_generate:
            flags += ["-C", f"profile-generate={args.pgo_generate}"]
            pgo_record.update(mode="instrumented", profile_directory=str(args.pgo_generate))
            build_mode += "-pgo-generate"
        if args.pgo_use:
            llvm_args = "-pgo-warn-missing-function"
            if args.ext_tsp_profiled:
                llvm_args += (" -enable-ext-tsp-block-placement=true"
                              " -ext-tsp-apply-without-profile=false")
                pgo_record["code_layout"] = {
                    "algorithm": "ext-tsp", "profiled_functions_only": True,
                    "application": "use-only", "fresh_training": False,
                    "llvm_args": llvm_args.split(),
                }
            flags += ["-C", f"profile-use={args.pgo_use}",
                      "-C", f"llvm-args={llvm_args}"]
            pgo_record.update(mode="profile-use", input_sha256_before=pgo_input,
                              profile=str(args.pgo_use), training_record=str(args.training_record))
            build_mode += "-pgo-use"
        overrides = {
            "RUSTC": rustc,
            "RUSTC_WRAPPER": "", "RUSTC_WORKSPACE_WRAPPER": "",
            "RUSTFLAGS": " ".join(flags),
            "CARGO_ENCODED_RUSTFLAGS": "\x1f".join(flags),
            "CARGO_NET_OFFLINE": "true",
            "CARGO_BUILD_JOBS": str(args.jobs),
        }
        env = {**os.environ, **overrides}
        target_dir = root / "target" / build_mode
        argv = [cargo, "build", "--offline", "--locked", "--release", "--verbose",
                "--target", TARGET, "--jobs", str(args.jobs),
                "--target-dir", str(target_dir), "--manifest-path", str(root / "Cargo.toml")]
        if args.binary_name is not None:
            argv += ["--bin", args.binary_name]
        inherited_keys = {key for key in os.environ if key.startswith(
            ("CARGO_BUILD_", "CARGO_TARGET_", "CARGO_PROFILE_"))}
        inherited_keys.update(("RUSTFLAGS", "CARGO_ENCODED_RUSTFLAGS", "RUSTC",
                               "RUSTC_WRAPPER", "RUSTC_WORKSPACE_WRAPPER",
                               "RUSTUP_TOOLCHAIN", "CARGO_HOME", "LLVM_PROFILE_FILE",
                               "CC", "CFLAGS", "CXX", "CXXFLAGS", "AR", "LDFLAGS"))
        receipt = {
            "schema": "rook2-development-build-v1", "started_utc": utc(),
            "crate": str(root), "mode": args.mode, "target_triple": TARGET,
            "target_cpu": cpu, "target_directory": str(target_dir),
            "jobs": args.jobs, "argv": argv, "cwd": str(root),
            "environment_overrides": overrides,
            "inherited_build_environment": {key: os.environ.get(key) for key in sorted(inherited_keys)},
            "build_effective_environment": {key: env.get(key) for key in sorted(inherited_keys | set(overrides))},
            "source_sha256_before": source_snapshot(root),
            "tool_sha256_before": tool_snapshot(root),
            "cargo_config_sha256_before": cargo_configs(root),
            "git_before": git_snapshot(root, env),
            "toolchain": {"rustc": command_record([rustc, "-vV"], root, env),
                          "cargo": command_record([cargo, "--version"], root, env),
                          "rustc_executable_sha256": digest(Path(rustc).resolve()),
                          "cargo_executable_sha256": digest(Path(cargo).resolve())},
            "helper_sha256": digest(Path(__file__).resolve()),
            "initial_affinity": sorted(original_affinity),
            "build_affinity": sorted(os.sched_getaffinity(0)),
            "uname": list(os.uname()),
            "engine_runs": 0, "pgo": pgo_record,
            "rust_flags": flags,
            "identity_limit": "manifest/lock/src, tools source files, optional build.rs/toolchain files; not a full external/path-dependency or generated-input closure",
            "binary_name": args.binary_name, "binary_output": None,
            "binary_note": "no binary target requested for hashing; no executable identity asserted" if args.binary_name is None else None,
            "source_archive_planned": "source-before (captured before Cargo, verified against source_sha256_before)",
        }
        if args.pgo_use and training["engine_source_sha256"] != receipt["source_sha256_before"]:
            raise ValueError("source changed after profile-use admission")
        if args.dry_run:
            receipt["outcome"] = "plan-only; no Cargo build or receipt writes"
            print(json.dumps(receipt, indent=2, allow_nan=False))
            return 0
        output.mkdir()
        if args.pgo_generate:
            args.pgo_generate.mkdir()
        receipt["source_archive"] = archive_sources(
            root, output, receipt["source_sha256_before"] | receipt["tool_sha256_before"])
        write_receipt(output / "receipt.json", {**receipt, "outcome": "build-started"})
        began = time.monotonic()
        with (output / "build.stdout").open("xb") as stdout, (output / "build.stderr").open("xb") as stderr:
            result = subprocess.run(argv, cwd=root, env=env, stdout=stdout, stderr=stderr)
        receipt["build_elapsed_s"] = time.monotonic() - began
        receipt["cargo_exit_code"] = result.returncode
        receipt["source_sha256_after"] = source_snapshot(root)
        receipt["tool_sha256_after"] = tool_snapshot(root)
        receipt["cargo_config_sha256_after"] = cargo_configs(root)
        receipt["git_after"] = git_snapshot(root, env)
        receipt["source_identity_unchanged"] = receipt["source_sha256_before"] == receipt["source_sha256_after"]
        receipt["tool_identity_unchanged"] = receipt["tool_sha256_before"] == receipt["tool_sha256_after"]
        receipt["cargo_config_unchanged"] = receipt["cargo_config_sha256_before"] == receipt["cargo_config_sha256_after"]
        if pgo_input is not None:
            pgo_record["input_sha256_after"] = {path: digest(Path(path)) for path in pgo_input}
            pgo_record["inputs_unchanged"] = pgo_input == pgo_record["input_sha256_after"]
        if args.binary_name is not None and result.returncode == 0:
            binary = target_dir / TARGET / "release" / args.binary_name
            receipt["binary_output"] = {"path": str(binary), "sha256": digest(binary)}
        succeeded = (result.returncode == 0 and receipt["source_identity_unchanged"]
                     and receipt["tool_identity_unchanged"]
                     and receipt["cargo_config_unchanged"]
                     and pgo_record.get("inputs_unchanged", True))
        receipt["outcome"] = "build-succeeded-with-stable-input-snapshot" if succeeded else "failed-or-inputs-changed"
        exit_code = 0 if succeeded else 1
    except BaseException as error:
        receipt["outcome"] = "helper-error-or-interruption"
        receipt["error"] = f"{type(error).__name__}: {error}"
        if not output.is_dir():
            raise
    finally:
        os.sched_setaffinity(0, original_affinity)
        if receipt and not args.dry_run and output.is_dir():
            receipt["finished_utc"] = utc()
            receipt["restored_affinity"] = sorted(os.sched_getaffinity(0))
            receipt["logs"] = {name: {"path": name, "bytes": (output / name).stat().st_size,
                                      "sha256": digest(output / name)}
                               for name in ("build.stdout", "build.stderr") if (output / name).is_file()}
            write_receipt(output / "receipt.json", receipt)
    print(json.dumps({"receipt": str(output / "receipt.json"),
                      "outcome": receipt.get("outcome"), "engine_runs": 0,
                      "binary_output": receipt.get("binary_output")}))
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
