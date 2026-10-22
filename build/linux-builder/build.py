#!/usr/bin/env python3
"""Build isolated ordinary GNU and/or dynamic-musl images; never publish or train."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess

HERE = Path(__file__).resolve().parent
TARGETS = {"glibc": "x86_64-unknown-linux-gnu", "musl": "x86_64-unknown-linux-musl"}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path, value):
    with path.open("x") as stream:
        json.dump(value, stream, indent=2, sort_keys=True)
        stream.write("\n")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--variant", choices=["both", *TARGETS], default="both")
    parser.add_argument("--mode", choices=["plain", "generate", "use"], default="plain")
    parser.add_argument("--source", type=Path, default=Path("/source"))
    parser.add_argument("--output", type=Path, default=Path("/out"))
    parser.add_argument("--profiles", type=Path, default=Path("/profiles"))
    parser.add_argument("--jobs", type=int, default=4)
    parser.add_argument("--source-date-epoch", type=int, default=1742256000)
    args = parser.parse_args()
    if not 1 <= args.jobs <= 64 or args.source_date_epoch < 0:
        parser.error("jobs must be1..64 and epoch nonnegative")
    if not args.output.is_dir() or any(args.output.iterdir()):
        parser.error("output must be an existing empty mounted directory")
    source = Path("/build/source")
    if source.exists():
        parser.error("build directory already used; start a fresh container")
    names = ["Cargo.toml", "Cargo.lock"]
    names += [str(p.relative_to(args.source)) for p in sorted((args.source / "src").rglob("*")) if p.is_file()]
    if (args.source / "build.rs").exists():
        parser.error("this curated ordinary builder does not admit unreviewed build.rs inputs")
    snapshot = {}
    for name in names:
        path = source / name
        path.parent.mkdir(parents=True, exist_ok=True)
        data = (args.source / name).read_bytes()
        path.write_bytes(data)
        os.utime(path, (args.source_date_epoch, args.source_date_epoch))
        snapshot[name] = hashlib.sha256(data).hexdigest()
    Path("/build/home").mkdir()
    env = {"PATH": "/usr/local/cargo/bin:/usr/local/bin:/usr/bin:/bin", "HOME": "/build/home",
           "RUSTUP_HOME": "/usr/local/rustup", "CARGO_HOME": "/build/cargo-home",
           "RUSTUP_TOOLCHAIN": "1.85.1-x86_64-unknown-linux-gnu", "LANG": "C", "LC_ALL": "C", "TZ": "UTC",
           "CARGO_NET_OFFLINE": "true", "CARGO_INCREMENTAL": "0", "CARGO_BUILD_JOBS": str(args.jobs),
           "SOURCE_DATE_EPOCH": str(args.source_date_epoch)}
    version = subprocess.check_output(["rustc", "-vV"], env=env, text=True)
    builder_pin = hashlib.sha256(b"".join((HERE / n).read_bytes() for n in ("Dockerfile", "build.py", "musl-linker.sh"))).hexdigest()
    variants = TARGETS if args.variant == "both" else [args.variant]
    for variant in variants:
        out = args.output / variant
        out.mkdir()
        target = TARGETS[variant]
        flags = ["-C", "target-cpu=x86-64", "-C", "linker=" + ("/usr/bin/gcc" if variant == "glibc" else str(HERE / "musl-linker.sh"))]
        if variant == "musl":
            flags += ["-C", "target-feature=-crt-static"]
        metadata = {"schema": "rook-builder-profile-v1", "target": target, "source_sha256": snapshot,
                    "source_date_epoch": args.source_date_epoch,
                    "rustc_vv": version, "builder_pin": builder_pin, "base_flags": list(flags)}
        if args.mode == "generate":
            raw_profiles = Path("/profiles-out") / variant
            raw_profiles.mkdir()
            flags += ["-C", "profile-generate=" + str(raw_profiles)]
        elif args.mode == "use":
            profile = args.profiles / (variant + ".profdata")
            supplied = json.loads((args.profiles / (variant + ".json")).read_text())
            for key, value in metadata.items():
                if supplied.get(key) != value:
                    raise ValueError("profile provenance mismatch: " + variant + ":" + key)
            if supplied.get("profile_sha256") != sha(profile):
                raise ValueError("profile checksum mismatch: " + variant)
            flags += ["-C", "profile-use=" + str(profile), "-C",
                      "llvm-args=-pgo-warn-missing-function -enable-ext-tsp-block-placement=true -ext-tsp-apply-without-profile=false"]
        build_env = {**env, "RUSTFLAGS": " ".join(flags), "CARGO_ENCODED_RUSTFLAGS": "\x1f".join(flags)}
        target_dir = Path("/build/target") / variant
        command = ["cargo", "build", "--offline", "--locked", "--release", "--verbose", "--target", target,
                   "--target-dir", str(target_dir), "--jobs", str(args.jobs), "--bin", "rook2"]
        with (out / "build.stdout").open("xb") as stdout, (out / "build.stderr").open("xb") as stderr:
            subprocess.run(command, cwd=source, env=build_env, stdout=stdout, stderr=stderr, check=True)
        log = (out / "build.stderr").read_text().lower()
        if args.mode == "use" and any(s in log for s in ("no profile data available for function", "profile data may be out of date",
                "profile data mismatch", "malformed instrumentation profile data", "hash mismatch", "unprofiled function")):
            raise ValueError("missing/stale PGO diagnostics: " + variant)
        image = out / "rook"
        shutil.copyfile(target_dir / target / "release/rook2", image)
        image.chmod(0o755)
        program = subprocess.check_output(["readelf", "-lW", str(image)], text=True)
        dynamic = subprocess.check_output(["readelf", "-dW", str(image)], text=True)
        versions = subprocess.check_output(["readelf", "-VW", str(image)], text=True)
        needed = re.findall(r"Shared library: \[(.*?)\]", dynamic)
        if variant == "musl":
            if "/lib/ld-musl-x86_64.so.1" not in program or "libc.musl-x86_64.so.1" not in needed or "GLIBC_" in versions:
                raise ValueError("dynamic-musl ELF contains an unexpected runtime")
            if set(needed) - {"libc.musl-x86_64.so.1", "libgcc_s.so.1"}:
                raise ValueError("unexpected musl dependency: " + repr(needed))
        elif "/lib64/ld-linux-x86-64.so.2" not in program or "libc.so.6" not in needed:
            raise ValueError("GNU ELF contains an unexpected runtime")
        if any(sha(source / name) != expected or sha(args.source / name) != expected for name, expected in snapshot.items()):
            raise ValueError("source changed during build")
        if args.mode == "use" and sha(profile) != supplied["profile_sha256"]:
            raise ValueError("profile changed during build")
        write(out / "profile-template.json", metadata)
        write(out / "build.json", {**metadata, "mode": args.mode, "argv": command, "flags": flags,
              "source_date_epoch": args.source_date_epoch, "needed": needed, "binary_sha256": sha(image),
              "bytes": image.stat().st_size, "qualification": "new unqualified build; no engine execution or promotion"})
        (out / "SHA256SUMS").write_text(sha(image) + "  rook\n")
        print(json.dumps({"variant": variant, "sha256": sha(image), "bytes": image.stat().st_size}), flush=True)


if __name__ == "__main__":
    main()
