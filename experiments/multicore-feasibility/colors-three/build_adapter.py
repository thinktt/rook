#!/usr/bin/env python3
"""Run unchanged tools/build.py with only its housekeeping mask adapted.

Both control and candidate use the same --crate arguments and Rust build recipe.
The original helper assumes CPUs4/5 are available; this experiment reserves those
CPUs from its housekeeping mask. The original source bytes remain unchanged.
"""
import sys
from pathlib import Path

sys.dont_write_bytecode = True
from common import HERE, ROOT, HELPERS, module, read, sha, write


def main():
    original = ROOT/'tools/build.py'
    digest = sha(original)
    build = module('colors_three_original_build_helper', original)
    original_helpers = sorted(build.HELPERS)
    build.HELPERS = set(HELPERS)
    output = Path(sys.argv[sys.argv.index('--output')+1]).resolve()
    try:
        return build.main()
    finally:
        assert sha(original) == digest
        receipt = output/'receipt.json'
        if receipt.exists():
            value = read(receipt)
            value['affinity_adapter'] = dict(path=str(Path(__file__)), sha256=sha(Path(__file__)),
                original_tool=str(original), original_tool_sha256=digest, only_override='HELPERS',
                original_helpers=original_helpers, helpers=sorted(HELPERS))
            write(receipt, value)


if __name__ == '__main__':
    raise SystemExit(main())
