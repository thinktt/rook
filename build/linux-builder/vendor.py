#!/usr/bin/env python3
"""Materialize checksum-locked Cargo directory sources before offline builds."""
import argparse
import hashlib
import io
import json
from pathlib import Path, PurePosixPath
import re
import tarfile
import tomllib
import urllib.request


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--lock", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--cache", type=Path, help="optional local directory of checksum-verified .crate archives")
    args = parser.parse_args()
    args.output.mkdir()
    inventory = {}
    for package in tomllib.loads(args.lock.read_text())["package"]:
        if "source" not in package:
            continue
        if package["source"] != "registry+https://github.com/rust-lang/crates.io-index":
            raise ValueError("unsupported dependency source")
        name, version = package["name"], package["version"]
        if not re.fullmatch(r"[A-Za-z0-9_-]+", name) or not re.fullmatch(r"[A-Za-z0-9.+_-]+", version):
            raise ValueError("invalid archive name")
        stem = name + "-" + version
        if args.cache:
            data = (args.cache / (stem + ".crate")).read_bytes()
        else:
            url = "https://static.crates.io/crates/" + name + "/" + stem + ".crate"
            with urllib.request.urlopen(url, timeout=60) as response:
                data = response.read()
        checksum = hashlib.sha256(data).hexdigest()
        if checksum != package["checksum"]:
            raise ValueError("archive checksum mismatch: " + stem)
        directory = args.output / stem
        directory.mkdir()
        seen = set()
        with tarfile.open(fileobj=io.BytesIO(data), mode="r:gz") as archive:
            for member in archive:
                parts = PurePosixPath(member.name).parts
                if not parts or parts[0] != stem or ".." in parts or member.name.startswith("/"):
                    raise ValueError("archive path escapes package: " + member.name)
                relative = Path(*parts[1:])
                path = directory / relative
                if member.isdir():
                    path.mkdir(parents=True, exist_ok=True)
                elif member.isfile() and len(parts) > 1:
                    if relative in seen or relative == Path(".cargo-checksum.json"):
                        raise ValueError("duplicate/reserved archive path")
                    seen.add(relative)
                    path.parent.mkdir(parents=True, exist_ok=True)
                    path.write_bytes(archive.extractfile(member).read())
                    path.chmod(0o644)
                else:
                    raise ValueError("unsupported archive member: " + member.name)
        files = {p.relative_to(directory).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
                 for p in sorted(directory.rglob("*")) if p.is_file()}
        (directory / ".cargo-checksum.json").write_text(json.dumps({"files": files, "package": checksum}, sort_keys=True) + "\n")
        inventory[stem] = checksum
    (args.output / "inventory.json").write_text(json.dumps(inventory, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"vendoredPackages": len(inventory), "lockSha256": hashlib.sha256(args.lock.read_bytes()).hexdigest()}))


if __name__ == "__main__":
    main()
