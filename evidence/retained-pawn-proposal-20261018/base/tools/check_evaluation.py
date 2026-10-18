#!/usr/bin/env python3
"""Data-driven external native evaluation checks; expected data stays outside the engine."""
import json
from pathlib import Path
import shutil
import check_policies as runner

FILES = ["central-balance-v1.json", "board-patterns-v1.json", "pawn-candidates-v1.json",
         "pawn-endings-v1.json", "pawn-race-v1.json", "pawn-race-boundaries-v1.json",
         "pawn-fresh-v1.json", "endgame-material-v1.json", "endgame-blend-v1.json",
         "fortress-bounds-v1.json", "rook-fortress-v1.json", "endgame-adjust-v1.json",
         "final-score-v1.json", "evaluation-subtotal-v1.json", "fresh-score-v1.json",
         "first-iteration-v1.json", "ordinary-iterations-v1.json", "ordinary-iterations-selected-v1.json"]

CASES = []
def generate(case):
    index = len(CASES)
    CASES.append({"operation":case["request"]["operation"],"input":case["request"]["input"],"expected":case["expected"]})
    return [f'probe::run(concat!(env!("CARGO_MANIFEST_DIR"), "/cases/{index:04d}.json"));']

def prepare(output):
    (output/"cases").mkdir()
    for index, case in enumerate(CASES):
        (output/"cases"/f"{index:04d}.json").write_text(json.dumps(case,separators=(",",":"))+"\n")
    shutil.copyfile(Path(__file__).with_name("evaluation_probe.rs"), output/"src/probe.rs")

if __name__ == "__main__":
    raise SystemExit(runner.main(FILES,generate,"mod probe;",Path(__file__),prepare,test_threads=2))
