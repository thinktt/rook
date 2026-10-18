#!/usr/bin/env python3
"""Freeze a source-only exact ordered checker query experiment."""
import difflib
import hashlib
import io
import json
from pathlib import Path
import sys
import tarfile

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[1]
sys.dont_write_bytecode = True
sys.path.insert(0, str(ROOT/'tools'))
from build import source_snapshot, tool_snapshot


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def write(p, value):
    with p.open('x') as stream:
        json.dump(value, stream, indent=2); stream.write('\n')


def main():
    paths = json.loads((OUT/'paths.json').read_text())
    base, source = Path(paths['base']), Path(paths['source'])
    before, after, tools = source_snapshot(base), source_snapshot(source), tool_snapshot(source)
    assert before == paths['source_before'] and tools == paths['tools_before'] == tool_snapshot(base)
    changed = [p for p,h in before.items() if after[p] != h]
    assert changed == ['src/attacks.rs','src/movegen.rs']
    patch = ''.join(''.join(difflib.unified_diff((base/p).read_text().splitlines(True),
        (source/p).read_text().splitlines(True),fromfile='a/'+p,tofile='b/'+p)) for p in changed)
    assert (OUT/'phase1.patch').read_text() == patch
    archive = OUT/'prepared-source-02.tar.gz'
    with tarfile.open(archive, 'x:gz') as bundle:
        for name,digest in (after|tools).items():
            data = (source/name).read_bytes()
            assert hashlib.sha256(data).hexdigest() == digest
            entry = tarfile.TarInfo(name)
            entry.size, entry.mode = len(data), 0o644
            bundle.addfile(entry, io.BytesIO(data))
    with tarfile.open(archive) as bundle:
        assert {m.name:hashlib.sha256(bundle.extractfile(m).read()).hexdigest()
            for m in bundle.getmembers()} == after|tools
    assert source_snapshot(source) == after and tool_snapshot(source) == tools
    write(OUT/'preparation-failure.json',dict(actual_terminal_chunk='d97dfc',exit_code=1,
        reason='Ephemeral freeze script iterated dictionary keys as key/value tuples; partial empty source archive retained',
        source_changes_from_failure=False,native_runs=0,
        preserved_archive='prepared-source.tar.gz',preserved_archive_sha256=sha(OUT/'prepared-source.tar.gz'),
        recovery='New explicit freeze.py and prepared-source-02.tar.gz; same unchanged source/patch'))
    write(OUT/'prepared.json',dict(status='Source-only phase1 ordered checker candidate; uncompiled and unexecuted',
        source=str(source),control_source=str(base),changed_paths=changed,
        baseline_source_sha256=before,variant_source_sha256=after,tool_source_sha256=tools,
        source_archive=archive.name,source_archive_sha256=sha(archive),patch_sha256=sha(OUT/'phase1.patch'),
        expected_library_tests=141,expected_development_tests=2,expected_total_native_tests=143,
        control_artifact_sha256=paths['control_artifact_sha256'],control_receipt=paths['control_receipt'],
        control_receipt_sha256=sha(Path(paths['control_receipt'])),
        scope='Only unprojected Position checker discovery changes. Same existing persistent planes/tables; exact Pawn/KNIGHT/ray/adjacentKing order and first-two cap. Q/ordinary mailbox consumers, Boolean kernel, maintenance/layouts/charges remain unchanged.',
        proof='Same-rank pawn source low-bit order equals [-1,+1]; knights retain ordered table; ray nearest occupancy uses unchanged masks/directions, king only adjacent and interleaved. Valid tag/coherence premises remain inherited.',
        tests='One new fixed order/cap/three-route test; existing10000 setup loop gains exact old-mailbox1/2 identity comparisons for all64targets/bothcolors. Existing ordered/full/capped tests retained.',
        authority_review=str(ROOT/'evidence/ordered-bit-checkers-review-20261018/review-phase1-phase2-20261018T092625Z-3b886e.md'),
        freeze_driver_sha256=sha(Path(__file__)),native_jobs_started=0))
    print(json.dumps(dict(source=str(source),changed=changed,native_tests=143,archive_sha256=sha(archive))))


if __name__ == '__main__':
    main()
