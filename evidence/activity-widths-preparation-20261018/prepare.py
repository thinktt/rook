#!/usr/bin/env python3
"""Prepare a range-justified private mobility arithmetic experiment."""
import gzip
import hashlib
import io
import json
from pathlib import Path
import re
import shutil
import tarfile

PREP = Path(__file__).resolve().parent
ROOT = PREP.parents[1]
TARGET = Path('/tmp/imp2-activity-widths-20261018')


def sha(data):
    return hashlib.sha256(data).hexdigest()


def sources(root):
    return {str(p.relative_to(root)):sha(p.read_bytes()) for p in
            [root/'Cargo.toml', root/'Cargo.lock', *sorted((root/'src').rglob('*.rs'))]}


def main():
    baseline = sources(ROOT)
    reference = ROOT/'evidence/production-eval-kernels-use-build-20261018/receipt.json'
    assert baseline == json.loads(reference.read_text())['source_sha256_before']
    old = (ROOT/'src/activity.rs').read_text()

    def maximum(name):
        literal = old.split('const '+name+':', 1)[1].split('=', 1)[1].split(';', 1)[0]
        return max(map(int, re.findall(r'\b\d+\b', literal)))

    maxima = {n:maximum(n) for n in ['DESTINATION_VALUE', 'ROOK_SEVENTH', 'LOW_MOBILITY', 'CURVE']}
    assert list(maxima.values()) == [23, 47, 12, 36]
    targets = 27
    category = 3
    total = targets * category * max(maxima['DESTINATION_VALUE'], maxima['ROOK_SEVENTH']) * 2
    raw = [-5*11-2-(12*3+6+15), maxima['CURVE']]
    pieces = [(276*(15*x)+128)//256 for x in raw]
    difference = ((pieces[1]-pieces[0])*12800+512)//1024
    weighted = (9*difference*512+2048)//4096
    review = dict(scope='Admitted coherent Position populations/phase; effective weights0..10240 and clamped material. Local component proof only, not global score/call audit or timing evidence.',
                  activity_source_sha256=baseline['src/activity.rs'], geometry_source_sha256=baseline['src/geometry.rs'],
                  reference_build_sha256=sha(reference.read_bytes()), constant_maxima=maxima,
                  normalized_profile_sum_max=11, geometric_destinations_max=targets, category_max=category,
                  mobility_categories_range=[0, targets*category], mobility_total_range=[0, total],
                  mobility_destination_queries_range=[0, targets], piece_queries_max=targets+1,
                  per_piece_raw_score_range=raw, per_color_scaled_pieces_range=pieces,
                  activity_queries_max=2*15*(targets+1), king_pressure_range=[0, 27*48+8*40-12],
                  public_weighted_activity_absolute_bound=weighted,
                  phase_index_numerator_bound=256*((3*total)//4)+128,
                  private_field_payload_bytes_before=24, private_field_payload_bytes_after=12,
                  proof='At most27 ray targets/8 knight targets; every category0..3; value<=47, vertical multiplier<=2. Each extra query consumes one target, plus at most one source query. Curve<=36, source attack penalty<=57 and low-mobility penalty<=57. At most15 activity pieces/color. Phase weights total256. All bounds are conservative; no attainability claimed.')
    with (PREP/'range-review.json').open('x') as stream:
        json.dump(review, stream, indent=2)
        stream.write('\n')
    TARGET.mkdir()
    for name in ['Cargo.toml', 'Cargo.lock']:
        shutil.copy2(ROOT/name, TARGET/name)
    shutil.copytree(ROOT/'src', TARGET/'src')
    shutil.copytree(ROOT/'tools', TARGET/'tools', ignore=shutil.ignore_patterns('__pycache__'))
    text = old.replace('    categories: i64,\n    total: i64,\n    queries: u64,',
                       '    categories: u32,\n    total: u32,\n    queries: u32,')
    assert text != old
    start = text.index('fn capture_priority(')
    end = text.index('fn piece_score(', start)
    text = text[:start] + text[start:end].replace('i64', 'u32') + text[end:]
    start = text.index('fn piece_score(')
    end = text.index('#[inline]\nfn pressure_value', start)
    body = text[start:end]
    body = body.replace('    let raw_mobility', '    debug_assert!(endgame <= 256);\n    let raw_mobility', 1)
    body = body.replace('(512 - endgame as i64)', '(512 - u32::from(endgame))')
    body = body.replace('CURVE[index] as i64', 'i32::from(CURVE[index])')
    body = body.replace('attack_count as i64', 'i32::from(attack_count)')
    body = body.replace('LOW_MOBILITY[rank][file] as i64', 'u32::from(LOW_MOBILITY[rank][file])')
    body = body.replace('score -= penalty;', 'score -= penalty as i32;')
    body = body.replace('(score, queries)', '(i64::from(score), u64::from(queries))')
    assert body != text[start:end]
    (TARGET/'src/activity.rs').write_text(text[:start] + body + text[end:])
    assert sources(ROOT) == baseline
    after = sources(TARGET)
    archive = PREP/'prepared-source.tar.gz'
    files = {str(p.relative_to(TARGET)):sha(p.read_bytes()) for p in
             [*sorted((TARGET/'src').rglob('*.rs')), *sorted((TARGET/'tools').rglob('*')), TARGET/'Cargo.toml', TARGET/'Cargo.lock'] if p.is_file()}
    with archive.open('xb') as raw_stream:
        with gzip.GzipFile(filename='', mode='wb', fileobj=raw_stream, mtime=0) as gz:
            with tarfile.open(fileobj=gz, mode='w') as output:
                for name in sorted(files):
                    data = (TARGET/name).read_bytes()
                    member = tarfile.TarInfo(name)
                    member.size, member.mode = len(data), 0o644
                    output.addfile(member, io.BytesIO(data))
    with tarfile.open(archive, 'r:gz') as check:
        assert {m.name:sha(check.extractfile(m).read()) for m in check} == files
    result = dict(status='Uncompiled private mobility/positive-index arithmetic prototype; no benefit inferred', path=str(TARGET),
                  baseline_source_sha256=baseline, variant_source_sha256=after,
                  modified_existing_files=[n for n in baseline if after[n] != baseline[n]],
                  generator_sha256=sha(Path(__file__).read_bytes()), range_review_sha256=sha((PREP/'range-review.json').read_bytes()),
                  archive=archive.name, archive_sha256=sha(archive.read_bytes()), archive_files=files,
                  scope='Private Mobility fields/arithmetic only; returned raw scores remaini64, R countersu64. Position/Node, ordering, caches/lifetimes and actual N/R charges unchanged.')
    with (PREP/'prepared.json').open('x') as stream:
        json.dump(result, stream, indent=2)
        stream.write('\n')
    print(json.dumps({k:result[k] for k in ['status', 'path', 'modified_existing_files', 'archive_sha256']}))


if __name__ == '__main__':
    main()
