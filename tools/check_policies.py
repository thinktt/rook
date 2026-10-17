#!/usr/bin/env python3
"""Generate an external Rust test crate from released policy expectations.

Expected answers compile only into the separate test executable. The engine
library does all policy computation; no fixture data enters production source.
This checks native seams, not DIAG input validation or complete conformance.
"""
import argparse
import collections
import hashlib
import io
import json
import os
from pathlib import Path
import subprocess
import tarfile
import time

FILES = ["selective-depth-v1.json", "tactical-capture-order-v1.json",
         "search-candidate-order-v1.json", "material-threat-v1.json",
         "move-extensions-v1.json", "cutoff-memory-v1.json"]
KINDS = ("pawn", "knight", "bishop", "rook", "queen", "king")
SIDES = ("white", "black")
HELPERS = {0, 1, 2, 3, 4, 5, 8, 9, 10, 11, 12, 13}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def lit(value):
    return json.dumps(value, ensure_ascii=True)


def array(values):
    return "[" + ",".join(str(v) for v in values) + "]"


def move(value):
    return "None" if value is None else f"Some(m({lit(value['move'])},{lit(value['kind'])}))"


def bare_move(value):
    return move(value)[5:-1]


def profile(value):
    # Input representation only; native relation/capture algorithms remain in Rust.
    return sum(value[k] * w for k, w in zip(("weak", "queen", "rook", "minor", "pawn"), (1, 2, 4, 16, 64))) % 256


def history_setup(value, variable):
    lines = []
    for entry in value.get("history", []):
        lines.append(f"{variable}.history[{SIDES.index(entry['side'])}][{KINDS.index(entry['piece'])}][sq({lit(entry['square'])}).0 as usize]={entry['value']};")
    for entry in value.get("killers", []):
        lines.append(f"{variable}.killers[{entry['ply']}]={array(move(m) for m in entry['moves'])}.map(|x|x.unwrap_or(Move::NONE));")
    return lines


def context(query):
    fen = query["placement"] + (" w" if query["side"] == "white" else " b") + " - - 0 1"
    values = array(array(query["values"][side][k] for k in KINDS[:5]) for side in SIDES)
    lines = [f"let position=Position::from_fen({lit(fen)}).unwrap();",
             "let mut root=RootContext::neutral(&position);",
             f"root.values={values};root.squares=[[[0;64];5];2];"]
    for entry in query["squareAdjustments"]:
        lines.append(f"root.squares[{SIDES.index(entry['side'])}][{KINDS.index(entry['piece'])}][sq({lit(entry['square'])}).0 as usize]={entry['value']};")
    return lines


def generate(case):
    op, q, e = case["request"]["operation"], case["request"]["input"], case["expected"]
    if op == "search.selectiveDepth":
        data = []
        for query, answer in zip(q["queries"], e["results"], strict=True):
            data.append("(" + ",".join(str(x) for x in [query["iterationDepth"], query["selectivity"], query["endgameWeight"], query["targetPly"], answer["nodeAdjustment"], answer["rootMateMargin"], answer["adjustedTarget"]]) + ")")
        return [f"let cases:&[(i32,i32,u16,i32,i32,i32,i32)]=&{array(data)};",
                "for &(d,s,e,t,a,m,u) in cases {let v=policy::selective_depth(d,s,e,t);assert_eq!((v.adjustment,v.margin,v.adjusted_target),(a,m,u));}"]
    if op == "ordering.prioritySequence":
        return [f"let priorities:Vec<u32>=vec!{array(q['priorities'])};",
                f"assert_eq!(permutation(priorities),vec!{array(e['orderedIndices'])});"]
    if op == "tactics.capturePreferenceOrder":
        lines = ["let values:Vec<u32>=vec!["]
        for c in q["candidates"]:
            bonus = {"none": 0, "knight": 256, "bishop": 512, "rook": 768, "queen": 1024}[c["promotion"]]
            lines.append(f"policy::capture_magnitude(PieceKind::{c['attacker'].title()},{c['attackerValue']},{c['victimEffectiveValue']},{profile(c['own'])},{profile(c['opponent'])},{bonus}),")
        lines += ["];"]
        lines += [f"assert_eq!(values.iter().map(|&v|v!=0).collect::<Vec<_>>(),vec!{array(str(v).lower() for v in e['capturePreferred'])});",
                  f"assert_eq!(permutation(values.clone()),vec!{array(e['orderedIndices'])});",
                  "let mut groups:Vec<Vec<usize>>=Vec::new();let mut indices:Vec<usize>=(0..values.len()).collect();indices.sort_by_key(|&i|std::cmp::Reverse(values[i]));",
                  "for i in indices {if groups.last().is_some_and(|g|values[g[0]]==values[i]) {groups.last_mut().unwrap().push(i);} else {groups.push(vec![i]);}}",
                  f"let expected:Vec<Vec<usize>>=vec!{array('vec!'+array(g) for g in e['equalPreferenceGroups'])};assert_eq!(groups,expected);"]
        return lines
    if op == "search.orderCandidates":
        lines = context(q) + ["let influence=Influence::build(&position);let mut learned=Learning::default();"]
        lines += history_setup({"history": q["history"]}, "learned")
        lines += [f"learned.killers[{q['ply']}]={array(move(m) for m in q['killers']['current'])}.map(|x|x.unwrap_or(Move::NONE));"]
        if q["ply"] >= 3:
            lines += [f"learned.killers[{q['ply']-2}]={array(move(m) for m in q['killers']['twoPliesEarlier'])}.map(|x|x.unwrap_or(Move::NONE));"]
        lines += [f"let original:Vec<Move>=vec!{array(bare_move(m) for m in q['candidates'])};let mut list=MoveList::new();for &m in &original {{list.push(m);}}",
                  f"tactical::order_by(&mut list,&mut OrderingScratch::new(),|candidate|policy::priority(&position,&root,&influence,&learned,{q['ply']},{move(q['hashMove'])},candidate));",
                  "let actual:Vec<usize>=list.as_slice().iter().map(|m|original.iter().position(|x|x==m).unwrap()).collect();",
                  f"assert_eq!(actual,vec!{array(e['orderedIndices'])});"]
        return lines
    if op == "evaluation.materialThreat":
        return context(q) + ["let influence=Influence::build(&position);let mut charges=0;",
            f"for _ in 0..{q['repetitions']} {{let t=policy::material_threat(&position,&root,&influence,{q['passedPawnBalance']});assert_eq!(t.value,{e['threat']});charges+=t.queries;}}",
            f"assert_eq!(charges,{e['chargedRelationQueries']});"]
    if op == "search.moveExtensions":
        lines = [f"let mut position=Position::from_fen({lit(q['fen'])}).unwrap();let mut previous=position;let mut arrival=None;"]
        for token in q["moves"]:
            lines += ["let mut legal=MoveList::new();generate_legal(&position,&mut legal);",
                      f"let movement=*legal.as_slice().iter().find(|m|m.to_string()=={lit(token)}).unwrap();previous=position;arrival=Some(movement);position=position.played_unchecked(movement);"]
        lines += ["let mut legal=MoveList::new();generate_legal(&position,&mut legal);let checked=in_check(&position,position.side);",
                  f"assert_eq!(checked,{str(e['inCheck']).lower()});",
                  f"let extensions=policy::Extensions::new(&position,legal.as_slice(),&previous,arrival,{q['previousExtension']},checked);",
                  "let actual:Vec<(Move,u8)>=legal.as_slice().iter().map(|&m|(m,extensions.for_move(&position,m))).collect();",
                  f"let expected:Vec<(Move,u8)>=vec!{array('('+bare_move(v['move'])+','+str(v['extension'])+')' for v in e['candidates'])};assert_eq!(actual,expected);"]
        return lines
    if op == "search.cutoffMemory":
        lines = ["let mut actual=Learning::default();"] + history_setup(q, "actual")
        lines += [f"actual.total={sum(v['value'] for v in q['history'])};"]
        for index, snapshot in enumerate(e["snapshots"]):
            if index:
                event = q["events"][index - 1]
                if event.get("reset"):
                    lines += ["actual.clear();"]
                else:
                    fen = event["placement"] + (" w" if event["side"] == "white" else " b") + " - - 0 1"
                    lines += [f"let position=Position::from_fen({lit(fen)}).unwrap();for _ in 0..{event['times']} {{actual.record(&position,{event['ply']},{event['depth']},{move(event['move'])});}}"]
            lines += ["let mut expected=Learning::default();"] + history_setup(snapshot, "expected")
            lines += [f"assert_eq!(actual.total,{snapshot['total']});assert_eq!(actual.history,expected.history);assert_eq!(actual.killers,expected.killers);"]
        return lines
    return None


HEADER = '''#![allow(unused_imports,unused_mut,unused_assignments,dead_code)]
use rook2::{ordinary_policy as policy,tactical::{self,OrderingScratch},influence::Influence,
 evaluation::RootContext,position::Position,movegen::{MoveList,generate_legal,in_check},
 ordinary_policy::Learning,types::{Move,MoveKind,PieceKind,Square}};
fn sq(s:&str)->Square {Square::parse(s).unwrap()}
fn m(s:&str,kind:&str)->Move {let k=if kind=="castle" {MoveKind::Castle} else if kind=="enPassant" {MoveKind::EnPassant}
 else if s.len()==5 {MoveKind::Promotion(match s.as_bytes()[4] {b'n'=>PieceKind::Knight,b'b'=>PieceKind::Bishop,b'r'=>PieceKind::Rook,b'q'=>PieceKind::Queen,_=>panic!()})} else {MoveKind::Ordinary};Move::new(sq(&s[..2]),sq(&s[2..4]),k)}
fn permutation(mut values:Vec<u32>)->Vec<usize> {let mut moves:Vec<Move>=(1..=values.len()).map(|i|Move(i as u16)).collect();tactical::priority_sequence(&mut moves,&mut values);moves.iter().map(|m|m.0 as usize-1).collect()}
'''


def main(files=None, generator=None, header=None, checker_path=None, prepare=None, test_threads=None):
    files = FILES if files is None else files
    generator = generate if generator is None else generator
    header = HEADER if header is None else header
    checker_path = Path(__file__) if checker_path is None else Path(checker_path)
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--spec", type=Path, default=Path("/home/legolas/king-spec/conformance/fixtures"))
    parser.add_argument("--release", action="store_true", help="use root release optimization settings with test-harness unwinding")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    output = args.output.resolve()
    if output.exists() or not output.parent.is_dir():
        parser.error("output must be absent and its parent must exist")
    generated, mapping, unsupported, counts = [header], [], [], collections.Counter()
    for name in files:
        for case in json.loads((args.spec / name).read_text())["cases"]:
            body = generator(case)
            if body is None:
                unsupported.append({"fixture": name, "id": case["id"], "operation": case["request"]["operation"]})
                continue
            function = f"case_{len(mapping):04d}"
            generated += [f"#[test] fn {function}() {{", *body, "}"]
            mapping.append({"test": function, "fixture": name, "id": case["id"], "operation": case["request"]["operation"]})
            counts[case["request"]["operation"]] += 1
    output.mkdir()
    (output / "src").mkdir()
    if prepare is not None:
        prepare(output)
    (output / "src/lib.rs").write_text("\n".join(generated) + "\n")
    (output / "Cargo.toml").write_text('[package]\nname="rook2-policy-check"\nversion="0.0.0"\nedition="2021"\n[dependencies]\nrook2={path=' + lit(str(root)) + '}\n')
    if args.release:
        import tomllib
        profile = tomllib.loads((root / "Cargo.toml").read_text())["profile"]["release"]
        with (output / "Cargo.toml").open("a") as manifest:
            manifest.write('\n[profile.release]\n')
            for key, value in profile.items():
                if key != "panic":
                    manifest.write(f'{key}={json.dumps(value)}\n')
            manifest.write('panic="unwind"\n')
    before = {str(p.relative_to(root)): sha(p) for p in sorted((root / "src").rglob("*.rs"))}
    receipt = {"schema": "rook2-external-native-policy-check-v1", "conformance_claim": False,
               "scope": "native computation seams; excludes DIAG validation and whole-search qualification",
               "unsupported": unsupported, "case_mapping": mapping, "cases_by_operation": counts,
               "fixture_sha256": {name: sha(args.spec / name) for name in files},
               "engine_sources_before": before, "checker_sha256": sha(checker_path), "runner_sha256": sha(Path(__file__)),
               "generated_test_sha256": sha(output / "src/lib.rs")}
    receipt["generated_sources_before"] = {str(p.relative_to(output)): sha(p) for p in sorted((output / "src").glob("*.rs"))}
    receipt["engine_manifest_sha256"] = sha(root / "Cargo.toml")
    receipt["engine_lock_sha256"] = sha(root / "Cargo.lock")
    receipt["toolchain"] = subprocess.check_output(["rustc", "-vV"], text=True)
    receipt["build_profile"] = "release-optimization-test-unwind" if args.release else "dev-test"
    receipt["build_environment"] = {key: os.environ.get(key) for key in ("RUSTFLAGS", "CARGO_ENCODED_RUSTFLAGS", "RUSTC", "RUSTC_WRAPPER", "RUSTC_WORKSPACE_WRAPPER")}
    data_paths = sorted((output / "cases").glob("*.json"))
    receipt["test_data_sha256"] = {str(p.relative_to(output)): sha(p) for p in data_paths}
    affinity = os.sched_getaffinity(0)
    started = time.monotonic()
    try:
        os.sched_setaffinity(0, HELPERS)
        argv = ["cargo", "test", "--offline", "--manifest-path", str(output / "Cargo.toml"),
                "--target-dir", str(root / "target/policy-check"), "--jobs", "4"]
        if args.release:
            argv.insert(2,"--release")
        if test_threads is not None:
            argv += ["--", "--test-threads", str(test_threads)]
        with (output / "stdout.raw").open("xb") as stdout, (output / "stderr.raw").open("xb") as stderr:
            result = subprocess.run(argv, cwd=root, stdout=stdout, stderr=stderr, timeout=120)
        receipt.update({"argv": argv, "exit_code": result.returncode, "elapsed_s": time.monotonic() - started,
                        "helper_affinity": sorted(HELPERS)})
    finally:
        os.sched_setaffinity(0, affinity)
    receipt["engine_sources_unchanged"] = before == {str(p.relative_to(root)): sha(p) for p in sorted((root / "src").rglob("*.rs"))}
    receipt["test_data_identity_unchanged"] = receipt["test_data_sha256"] == {str(p.relative_to(output)): sha(p) for p in sorted((output / "cases").glob("*.json"))}
    receipt["stdout_sha256"] = sha(output / "stdout.raw")
    receipt["stderr_sha256"] = sha(output / "stderr.raw")
    archive_path = output / "verified-test-source.tar.gz"
    with tarfile.open(archive_path, "w:gz") as archive:
        names = ["Cargo.toml", "Cargo.lock"] + [str(p.relative_to(output)) for p in sorted((output / "src").glob("*.rs"))] + [str(p.relative_to(output)) for p in data_paths]
        for name in names:
            data = (output / name).read_bytes()
            member = tarfile.TarInfo(name)
            member.size = len(data)
            member.mode = 0o644
            archive.addfile(member, io.BytesIO(data))
    with tarfile.open(archive_path) as archive:
        for member in archive.getmembers():
            if archive.extractfile(member).read() != (output / member.name).read_bytes():
                raise ValueError("generated test archive changed bytes")
    receipt["test_source_archive_sha256"] = sha(archive_path)
    receipt["generated_test_source_unchanged"] = receipt["generated_sources_before"] == {str(p.relative_to(output)): sha(p) for p in sorted((output / "src").glob("*.rs"))}
    receipt["engine_manifest_lock_unchanged"] = (sha(root / "Cargo.toml") == receipt["engine_manifest_sha256"] and sha(root / "Cargo.lock") == receipt["engine_lock_sha256"])
    (output / "receipt.json").write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps({"output": str(output), "cases": len(mapping), "exit_code": result.returncode,
                      "engine_sources_unchanged": receipt["engine_sources_unchanged"]}))
    return result.returncode or int(not (receipt["engine_sources_unchanged"] and receipt["test_data_identity_unchanged"] and receipt["generated_test_source_unchanged"] and receipt["engine_manifest_lock_unchanged"]))


if __name__ == "__main__":
    raise SystemExit(main())
