#!/usr/bin/env python3
"""Cold file preparation only; never build or execute an engine."""
from pathlib import Path
import difflib
import gzip
import hashlib
import io
import json
import shutil
import tarfile
import tempfile

PREP = Path(__file__).resolve().parent
ROOT = PREP.parents[1]
BASE = Path("/tmp/imp2-eval-pawn-observers-20261018")


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def snapshot(path):
    return {
        str(p.relative_to(path)): sha(p)
        for p in [path / "Cargo.toml", path / "Cargo.lock",
                  *sorted((path / "src").rglob("*.rs"))]
    }


def replace(path, old, new):
    text = path.read_text()
    if text.count(old) != 1:
        raise RuntimeError("Expected unique anchor: " + str(path) + " " + old[:80])
    path.write_text(text.replace(old, new, 1))


def main():
    before = snapshot(BASE)
    if before != snapshot(ROOT) or len(before) != 43:
        raise RuntimeError("Current root native43 does not match requested79 source")
    target = Path(tempfile.mkdtemp(prefix="imp2-material-allowance-census79-20261018-"))
    for name in ["Cargo.toml", "Cargo.lock"]:
        shutil.copyfile(BASE / name, target / name)
    shutil.copytree(BASE / "src", target / "src")
    shutil.copytree(BASE / "tools", target / "tools",
                    ignore=shutil.ignore_patterns("__pycache__"))
    stats = r'''/// Diagnostic source-demand counts, never cached material values.
#[derive(Clone, Copy, Debug, Default, PartialEq, Eq)]
pub struct AllowanceLoopStats {
    pub loops: u64,
    pub checked_loops: u64,
    pub nonempty_loops: u64,
    pub calls: u64,
    pub unique_keys: u64,
    pub old_endpoints: u64,
    pub lazy_endpoints: u64,
    pub calls_by_victim: [u64; 10],
    pub unique_by_victim: [u64; 10],
}

impl AllowanceLoopStats {
    pub(crate) fn begin(&mut self, checked: bool) {
        self.loops += 1;
        self.checked_loops += u64::from(checked);
    }

    pub(crate) fn observe(&mut self, seen: &mut u16, victim: crate::types::Piece) {
        // Actual occupied destination: color*5 + Pawn/Knight/Bishop/Rook/Queen.
        // The original allowance caller excludes empty/king and special moves.
        let tag = victim.color().index() * 5 + victim.kind().index();
        let bit = 1u16 << tag;
        self.calls += 1;
        self.old_endpoints += 2;
        self.calls_by_victim[tag] += 1;
        if *seen == 0 {
            self.nonempty_loops += 1;
            self.lazy_endpoints += 1; // One hypothetical lazy parent endpoint.
        }
        if *seen & bit == 0 {
            *seen |= bit;
            self.unique_keys += 1;
            self.unique_by_victim[tag] += 1;
            self.lazy_endpoints += 1; // One hypothetical lazy after endpoint.
        }
    }
}

'''
    path = target / "src/quiescence.rs"
    marker = "#[derive(Clone, Copy, Debug, Default, PartialEq, Eq)]\npub struct Stats {\n"
    replace(path, marker, stats + marker
            + "    pub allowance_q: AllowanceLoopStats,\n"
            + "    pub allowance_ordinary: AllowanceLoopStats,\n")
    anchor = "        let count = self.candidates[ply].len;\n"
    replace(path, anchor, anchor + '''        let mut allowance_seen = 0u16;
        if DIAGNOSTICS {
            self.stats.allowance_q.begin(checked);
        }
''')
    anchor = "                if !special && !victim.is_empty() {\n"
    replace(path, anchor, anchor + '''                    if DIAGNOSTICS {
                        self.stats.allowance_q.observe(&mut allowance_seen, victim);
                    }
''')
    path = target / "src/ordinary.rs"
    anchor = ("        movegen::generate_legal(&position, &mut self.candidates[p]);\n"
              "        let count = self.candidates[p].len;\n")
    replace(path, anchor, anchor + '''        let mut allowance_seen = 0u16;
        if DIAGNOSTICS {
            self.stats.allowance_ordinary.begin(checked);
        }
''')
    anchor = '''                Some(policy::frontier_estimate(
                    &position,
                    &self.evaluator.root,
                    movement,
                    checking,
                    evaluation.score,
                    node.retained.positional,
                    node.retained.pawn_progress,
                ))'''
    replace(path, anchor, '''                Some(policy::frontier_estimate_observed(
                    &position,
                    &self.evaluator.root,
                    movement,
                    checking,
                    evaluation.score,
                    node.retained.positional,
                    node.retained.pawn_progress,
                    |victim| {
                        if DIAGNOSTICS {
                            self.stats
                                .allowance_ordinary
                                .observe(&mut allowance_seen, victim);
                        }
                    },
                ))''')
    path = target / "src/ordinary_policy.rs"
    start = '''pub fn frontier_estimate(
    position: &Position,
    root: &RootContext,
    movement: Move,
    checking: bool,
    score: i32,
    positional: i32,
    progress: i32,
) -> i32 {
'''
    wrapper = start + '''    frontier_estimate_observed(
        position, root, movement, checking, score, positional, progress, |_| {},
    )
}

/// The observer runs only on the original occupied ordinary-capture branch.
pub(crate) fn frontier_estimate_observed<F: FnOnce(crate::types::Piece)>(
    position: &Position,
    root: &RootContext,
    movement: Move,
    checking: bool,
    score: i32,
    positional: i32,
    progress: i32,
    observer: F,
) -> i32 {
'''
    replace(path, start, wrapper)
    anchor = '''    if !position.board[movement.to().0 as usize].is_empty() {
        return score
            + quiescence_policy::allowance(root, position, &movement, positional, progress);
    }
'''
    replace(path, anchor, anchor.replace(
        "        return score\n",
        "        observer(position.board[movement.to().0 as usize]);\n        return score\n"))
    path = target / "src/session.rs"
    exporter = '''    /// Private diagnostic wrapper transport; counts for the last search segment.
    pub fn diagnostic_material_allowance_census(
        &self,
    ) -> Option<([u64; 14], [[u64; 10]; 4], [u64; 2])> {
        self.search.as_ref().map(|search| {
            let q = search.stats.allowance_q;
            let o = search.stats.allowance_ordinary;
            (
                [
                    q.loops, q.checked_loops, q.nonempty_loops, q.calls,
                    q.unique_keys, q.old_endpoints, q.lazy_endpoints,
                    o.loops, o.checked_loops, o.nonempty_loops, o.calls,
                    o.unique_keys, o.old_endpoints, o.lazy_endpoints,
                ],
                [
                    q.calls_by_victim, q.unique_by_victim,
                    o.calls_by_victim, o.unique_by_victim,
                ],
                [search.evaluator.stats.full, search.evaluator.stats.fast],
            )
        })
    }
'''
    replace(path, "impl<const D: bool> Session<D> {\n",
            "impl<const D: bool> Session<D> {\n" + exporter)
    wire = (BASE / "src/bin/rook2.rs").read_text().replace(
        "Session::<false>", "Session::<true>")
    wire = wire.replace(
        "    // Disable development counters and root traces in the ordinary binary.\n", "")
    quit_block = r'''            Action::Quit => {
                let (c, tags, evaluations) = session
                    .diagnostic_material_allowance_census()
                    .ok_or_else(|| io::Error::other("missing census stats"))?;
                let path = std::env::var_os("ROOK2_MATERIAL_ALLOWANCE_PROBE")
                    .ok_or_else(|| io::Error::other("missing private census file"))?;
                let mut file = std::fs::OpenOptions::new()
                    .write(true).create_new(true).open(path)?;
                writeln!(file,
                    "{{\"schema\":\"rook2-material-allowance-census-v1\",\"q_loops\":{},\"q_checked_loops\":{},\"q_nonempty_loops\":{},\"q_calls\":{},\"q_unique_keys\":{},\"q_old_endpoints\":{},\"q_lazy_endpoints\":{},\"ordinary_loops\":{},\"ordinary_checked_loops\":{},\"ordinary_nonempty_loops\":{},\"ordinary_calls\":{},\"ordinary_unique_keys\":{},\"ordinary_old_endpoints\":{},\"ordinary_lazy_endpoints\":{},\"q_calls_by_victim\":{:?},\"q_unique_by_victim\":{:?},\"ordinary_calls_by_victim\":{:?},\"ordinary_unique_by_victim\":{:?},\"full\":{},\"fast\":{}}}",
                    c[0],c[1],c[2],c[3],c[4],c[5],c[6],
                    c[7],c[8],c[9],c[10],c[11],c[12],c[13],
                    tags[0],tags[1],tags[2],tags[3],evaluations[0],evaluations[1])?;
                return Ok(());
            }'''
    anchor = "            Action::Quit => return Ok(()),"
    if wire.count(anchor) != 1:
        raise RuntimeError("Missing wire quit")
    (target / "src/bin/rook2-material-allowance-probe.rs").write_text(
        wire.replace(anchor, quit_block))
    after = snapshot(target)
    if snapshot(BASE) != before or snapshot(ROOT) != before:
        raise RuntimeError("Baseline changed during cold preparation")
    modified = [name for name in before if before[name] != after[name]]
    if modified != ["src/ordinary.rs", "src/ordinary_policy.rs",
                    "src/quiescence.rs", "src/session.rs"]:
        raise RuntimeError("Unexpected edits " + str(modified))
    for name in ["src/evaluation.rs", "src/evaluator.rs", "src/quiescence_policy.rs",
                 "src/position.rs", "src/bin/rook2.rs", "src/wire.rs"]:
        if before[name] != after[name]:
            raise RuntimeError("Protected calculation/protocol changed " + name)
    patches = []
    for name in sorted(after):
        a = (BASE / name).read_text() if name in before else ""
        b = (target / name).read_text()
        if a != b:
            patches.append("".join(difflib.unified_diff(
                a.splitlines(keepends=True), b.splitlines(keepends=True),
                fromfile="a/" + name if name in before else "/dev/null",
                tofile="b/" + name)))
    patch = PREP / "census.patch"
    patch.write_text("".join(patches))
    files = {
        str(p.relative_to(target)): sha(p)
        for p in [target / "Cargo.toml", target / "Cargo.lock",
                  *sorted((target / "src").rglob("*.rs")),
                  *sorted((target / "tools").rglob("*"))]
        if p.is_file()
    }
    archive = PREP / "prepared-source.tar.gz"
    with archive.open("xb") as raw:
        with gzip.GzipFile(filename="", fileobj=raw, mode="wb", mtime=0) as compressed:
            with tarfile.open(fileobj=compressed, mode="w") as out:
                for name, identity in sorted(files.items()):
                    data = (target / name).read_bytes()
                    if hashlib.sha256(data).hexdigest() != identity:
                        raise RuntimeError("Source changed while archiving")
                    member = tarfile.TarInfo(name)
                    member.size = len(data)
                    member.mode = 0o644
                    out.addfile(member, io.BytesIO(data))
    with tarfile.open(archive, "r:gz") as archived:
        if {m.name: hashlib.sha256(archived.extractfile(m).read()).hexdigest()
                for m in archived} != files:
            raise RuntimeError("Archive mismatch")
    result = dict(
        status="COLD uncompiled diagnostic census only; no cache or benefit claim",
        baseline=str(BASE), path=str(target),
        baseline_source_sha256=before, variant_source_sha256=after,
        modified_existing_files=modified,
        new_files=[name for name in after if name not in before],
        archive=archive.name, archive_sha256=sha(archive), archive_files=files,
        patch_sha256=sha(patch), generator_sha256=sha(Path(__file__)),
        protected_calculations_unchanged=True,
        execution="File edits/hashes/archive verification only; no build/rustc/test/engine/profiler.",
        transport="Separate Session<true> probe; create_new JSON on existing quit via ROOK2_MATERIAL_ALLOWANCE_PROBE; ordinary wire/protocol admission unchanged.",
        scope="Q and ordinary immutable-parent candidate inventories; actual qualifying allowance branches. Local key bitsets store no material. Existing full/fast stats supply the search-segment demand denominator; root preparation excluded.")
    (PREP / "prepared.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({key: result[key] for key in [
        "status", "path", "modified_existing_files", "new_files",
        "archive_sha256", "patch_sha256"]}))


if __name__ == "__main__":
    main()
