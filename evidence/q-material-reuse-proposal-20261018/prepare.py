#!/usr/bin/env python3
"""Cold Q-only material-endpoint reuse proposal; no compiler or engine execution."""
from pathlib import Path
import difflib
import gzip
import hashlib
import io
import json
import shutil
import tarfile
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
BASE = Path("/tmp/imp2-eval-pawn-observers-20261018")


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def snapshot(path):
    return {str(p.relative_to(path)): sha(p) for p in
            [path / "Cargo.toml", path / "Cargo.lock", *sorted((path / "src").rglob("*.rs"))]}


def once(path, old, new):
    text = path.read_text()
    if text.count(old) != 1:
        raise RuntimeError("Expected unique source anchor: " + str(path))
    path.write_text(text.replace(old, new, 1))


def main():
    baseline = snapshot(BASE)
    reference = json.loads((ROOT / "evidence/material-allowance-census-preparation-20261018/prepared.json").read_text())
    if baseline != reference["baseline_source_sha256"]:
        raise RuntimeError("Requested frozen79 baseline does not match census baseline43")
    target = Path(tempfile.mkdtemp(prefix="imp2-q-material-endpoint-reuse79-20261018-"))
    for name in ("Cargo.toml", "Cargo.lock"):
        shutil.copyfile(BASE / name, target / name)
    shutil.copytree(BASE / "src", target / "src")
    shutil.copytree(BASE / "tools", target / "tools",
                    ignore=shutil.ignore_patterns("__pycache__"))
    path = target / "src/quiescence_policy.rs"
    old = '''    let after = root.material(&after);
    let sign = if victim.color() == Color::White {
'''
    new = '''    let after = root.material(&after);
    finish_allowance(parent, movement, retained_positional, pawn_progress, before, after)
}

/// One immutable parent/root within a single Q candidate loop.
/// Constructed lazily at the first admitted ordinary-capture allowance request.
pub(crate) struct AllowanceMaterial {
    before: i16,
    after: [i16; 10],
    seen: u16,
}

impl AllowanceMaterial {
    pub(crate) fn new(root: &RootContext, parent: &Position) -> Self {
        Self {
            // RootContext::material always clamps to -7000..=7000.
            before: root.material(parent) as i16,
            after: [0; 10],
            seen: 0,
        }
    }

    pub(crate) fn allowance(
        &mut self,
        root: &RootContext,
        parent: &Position,
        movement: &Move,
        retained_positional: i32,
        pawn_progress: i32,
    ) -> i32 {
        debug_assert_eq!(movement.kind(), MoveKind::Ordinary);
        let victim = parent.board[movement.to().0 as usize];
        debug_assert!(!victim.is_empty() && victim.kind() != PieceKind::King);
        let tag = victim.color().index() * 5 + victim.kind().index();
        let bit = 1u16 << tag;
        if self.seen & bit == 0 {
            // Only counts are hypothetical, exactly as in the uncached helper.
            let mut after = *parent;
            after.counts[victim.color().index()][victim.kind().index()] -= 1;
            self.after[tag] = root.material(&after) as i16;
            self.seen |= bit;
        }
        finish_allowance(
            parent,
            movement,
            retained_positional,
            pawn_progress,
            self.before as i32,
            self.after[tag] as i32,
        )
    }
}

/// Shared native finishing rule; material endpoints are complete adjusted scores.
fn finish_allowance(
    parent: &Position,
    movement: &Move,
    retained_positional: i32,
    pawn_progress: i32,
    before: i32,
    after: i32,
) -> i32 {
    let victim = parent.board[movement.to().0 as usize];
    let sign = if victim.color() == Color::White {
'''
    once(path, old, new)
    tests = r'''    fn compare_cached_allowances(
        parent: &Position,
        root: &RootContext,
        source: &str,
        destinations: &[&str],
    ) {
        let saved = *parent;
        let mut material = AllowanceMaterial::new(root, parent);
        // Repeat in reverse order with different retained terms: only material
        // endpoints, not whole allowances, may be reused by victim tuple.
        for reverse in [false, true] {
            for index in 0..destinations.len() {
                let index = if reverse {
                    destinations.len() - 1 - index
                } else {
                    index
                };
                let capture = ordinary(source, destinations[index]);
                for (positional, progress) in [(0, 0), (19, 31), (-19, -31), (127, -317)] {
                    assert_eq!(
                        material.allowance(root, parent, &capture, positional, progress),
                        allowance(root, parent, &capture, positional, progress),
                        "destination {} retained {positional}/{progress}",
                        destinations[index],
                    );
                }
            }
        }
        assert_eq!(*parent, saved);
    }

    #[test]
    fn q_material_reuse_matches_uncached_across_victim_types_roots_and_rounding() {
        for (fen, destinations) in [
            (
                "7k/8/8/2npb3/3Q1r2/8/3q4/K7 w - - 0 1",
                ["c5", "d5", "e5", "f4", "d2"],
            ),
            (
                "7k/8/8/2NPB3/3q1R2/8/3Q4/K7 b - - 0 1",
                ["c5", "d5", "e5", "f4", "d2"],
            ),
        ] {
            let parent = pos(fen);
            for root_side in [Color::White, Color::Black] {
                for average_depth in [-99, -1, 0, 1, 99] {
                    let mut root_position = pos("7k/8/8/8/8/8/P7/K7 w - - 0 1");
                    root_position.side = root_side;
                    let root = RootContext::new(
                        &root_position,
                        [[73, 211, 37, 155, 1000], [183, 19, 317, 67, 11]],
                        average_depth,
                    );
                    compare_cached_allowances(&parent, &root, "d4", &destinations);
                }
            }
        }
    }

    #[test]
    fn q_material_reuse_shares_same_type_destinations_without_caching_retained_terms() {
        let parent = pos("7k/8/8/2n1n3/2rQ1r2/8/8/K7 w - - 0 1");
        for root_side in [Color::White, Color::Black] {
            for queen_value in [49, 50, 51, 99, 100, 101, 151, 152, 153] {
                let mut root = RootContext::neutral(&parent);
                root.side = root_side;
                root.values = [[0; 5]; 2];
                root.values[0][PieceKind::Queen.index()] = queen_value;
                root.values[1][PieceKind::Knight.index()] = 0;
                root.values[1][PieceKind::Rook.index()] = 51;
                for average_depth in [-1, 0, 1] {
                    root.average_depth = average_depth;
                    compare_cached_allowances(&parent, &root, "d4", &["c4", "f4", "c5", "e5"]);
                }
            }
        }
    }

    #[test]
    fn q_material_reuse_keeps_clipped_endpoints_and_zero_value_nonpawn_presence() {
        for fen in [
            "7k/8/8/8/2n5/QQQQQQQ1/QQQQQQQQ/K7 w - - 0 1",
            "7k/8/8/8/2N5/qqqqqqq1/qqqqqqqq/K7 b - - 0 1",
        ] {
            let parent = pos(fen);
            let root = RootContext::neutral(&parent);
            assert_eq!(root.material(&parent).abs(), 7000);
            compare_cached_allowances(&parent, &root, "c3", &["c4"]);
        }
        let parent = pos("7k/8/8/8/3n4/2P5/8/K7 w - - 0 1");
        let mut root = RootContext::neutral(&parent);
        root.values = [[0; 5]; 2];
        root.values[0][PieceKind::Pawn.index()] = 200;
        let before = root.material(&parent);
        let mut removed = parent;
        removed.counts[1][PieceKind::Knight.index()] -= 1;
        // Removing a zero-valued last nonpawn still changes the advantage gate.
        assert_ne!(before, root.material(&removed));
        compare_cached_allowances(&parent, &root, "c3", &["d4"]);
    }

'''
    once(path, "    #[test]\n    fn allowance_uses_complete_fixed_root_material_delta_and_no_transition() {",
         tests + "    #[test]\n    fn allowance_uses_complete_fixed_root_material_delta_and_no_transition() {")
    path = target / "src/quiescence.rs"
    once(path, "        let previous = history.previous_move();\n",
         "        let mut allowance_material = None;\n        let previous = history.previous_move();\n")
    old = '''                        + policy::allowance(
                            &self.evaluator.root,
                            &position,
                            &movement,
                            node.retained.positional,
                            node.retained.pawn_progress,
                        );'''
    new = '''                        + allowance_material
                            .get_or_insert_with(|| {
                                policy::AllowanceMaterial::new(&self.evaluator.root, &position)
                            })
                            .allowance(
                                &self.evaluator.root,
                                &position,
                                &movement,
                                node.retained.positional,
                                node.retained.pawn_progress,
                            );'''
    once(path, old, new)
    after = snapshot(target)
    changed = [name for name in baseline if baseline[name] != after[name]]
    if changed != ["src/quiescence.rs", "src/quiescence_policy.rs"]:
        raise RuntimeError("Unexpected source changes " + str(changed))
    if snapshot(BASE) != baseline:
        raise RuntimeError("Frozen79 baseline changed")
    protected = ["src/evaluation.rs", "src/evaluator.rs", "src/position.rs",
                 "src/ordinary.rs", "src/ordinary_policy.rs", "src/tactical.rs",
                 "src/session.rs", "src/wire.rs", "src/bin/rook2.rs"]
    if any(baseline[n] != after[n] for n in protected):
        raise RuntimeError("Protected state/ordinary/protocol changed")
    patch = HERE / "q-material-reuse.patch"
    patch.write_text("".join(
        "".join(difflib.unified_diff(
            (BASE / name).read_text().splitlines(keepends=True),
            (target / name).read_text().splitlines(keepends=True),
            fromfile="a/" + name, tofile="b/" + name))
        for name in changed))
    files = {str(p.relative_to(target)): sha(p) for p in
             [target / "Cargo.toml", target / "Cargo.lock",
              *sorted((target / "src").rglob("*.rs")), *sorted((target / "tools").rglob("*"))]
             if p.is_file()}
    archive = HERE / "prepared-source.tar.gz"
    with archive.open("xb") as raw:
        with gzip.GzipFile(filename="", fileobj=raw, mode="wb", mtime=0) as compressed:
            with tarfile.open(fileobj=compressed, mode="w") as output:
                for name, identity in sorted(files.items()):
                    data = (target / name).read_bytes()
                    if hashlib.sha256(data).hexdigest() != identity:
                        raise RuntimeError("Source changed during archive")
                    member = tarfile.TarInfo(name)
                    member.size = len(data)
                    member.mode = 0o644
                    output.addfile(member, io.BytesIO(data))
    with tarfile.open(archive, "r:gz") as handle:
        if {m.name: hashlib.sha256(handle.extractfile(m).read()).hexdigest()
                for m in handle} != files:
            raise RuntimeError("Archive readback mismatch")
    result = {
        "status": "Cold uncompiled Q-only endpoint reuse proposal; not executed or selected",
        "baseline": str(BASE), "path": str(target),
        "baseline_source_sha256": baseline, "variant_source_sha256": after,
        "modified_existing_files": changed, "new_native_files": [],
        "patch_sha256": sha(patch), "archive": archive.name,
        "archive_sha256": sha(archive), "archive_files": files,
        "generator_sha256": sha(Path(__file__)),
        "protected_source_paths_unchanged": protected,
        "execution": "Cold file preparation/hash/archive verification only; no builds/rustc/tests/engine/profiler.",
        "scope": "Only Q ordinary-capture material endpoints are reused per immutable parent loop; shared native allowance finisher; no persistent field or ordinary/frontier reuse.",
        "representation": "Lazy Option of before:i16, after:[i16;10], seen:u16; endpoints clamp to +/-7000, difference formed in i32. Frame and first-use initialization costs unmeasured.",
    }
    (HERE / "prepared.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({key: result[key] for key in
                      ["status", "path", "modified_existing_files", "patch_sha256", "archive_sha256"]}))


if __name__ == "__main__":
    main()
