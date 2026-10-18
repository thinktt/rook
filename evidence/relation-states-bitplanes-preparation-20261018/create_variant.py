#!/usr/bin/env python3
"""Prepare a pure formula-derived relation-state prototype; executes no engine."""
import gzip
import hashlib
import io
import json
from pathlib import Path
import shutil
import tarfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
TARGET = Path('/tmp/imp2-relation-states-bitplanes-20261018')


def sha(data):
    return hashlib.sha256(data).hexdigest()


def sources(root):
    files = [root/'Cargo.toml',root/'Cargo.lock',*sorted((root/'src').rglob('*.rs'))]
    return {str(p.relative_to(root)):sha(p.read_bytes()) for p in files}


def features(code):
    digits = [code%2,code//2%2,code//4%4,code//16%4,code//64%4]
    count = min(sum(digits),4)
    tier = next((tier for value,tier in zip(reversed(digits),[1,3,5,9,99]) if value),0)
    return count,tier


def relation(own,opponent,tested):
    d,u = own; a,v = opponent
    if a == 0: return 'Favorable'
    if d == 0 or v < tested: return 'Unfavorable'
    if v == tested: return 'Contested' if a <= d else 'Unfavorable'
    return 'Favorable' if a <= d or v > tested+u else 'Unfavorable'


def main():
    baseline = sources(ROOT)
    reference = json.loads((ROOT/'evidence/production-bitplanes-use-build-20261018/receipt.json').read_text())
    assert baseline == reference['source_sha256_before'],'native baseline changed'
    states = sorted(set(features(code) for code in range(256)))
    assert len(states) == 16
    classes = [states.index(features(code)) for code in range(256)]
    lines = ['//! Generated from EVAL-RELATIONS features/formula; no fixture input.',
             'use crate::influence::Relation;',
             'pub(crate) static CLASS: [u8;256] = [']
    lines += ['    '+','.join(map(str,classes[i:i+16]))+',' for i in range(0,256,16)]
    lines += ['];','pub(crate) static RELATIONS: [[Relation;256];4] = [']
    for tested in [1,3,5,9]:
        lines.append('    [')
        for own in states:
            lines.append('        '+','.join('Relation::'+relation(own,opponent,tested) for opponent in states)+',')
        lines.append('    ],')
    lines.append('];\n')
    table = '\n'.join(lines)
    TARGET.mkdir()
    for name in ['Cargo.toml','Cargo.lock']: shutil.copy2(ROOT/name,TARGET/name)
    shutil.copytree(ROOT/'src',TARGET/'src')
    shutil.copytree(ROOT/'tools',TARGET/'tools',ignore=shutil.ignore_patterns('__pycache__'))
    (TARGET/'src/relation_table.rs').write_text(table)
    lib = TARGET/'src/lib.rs'; text = lib.read_text()
    assert text.count('pub mod influence;') == 1
    lib.write_text(text.replace('pub mod influence;','pub mod influence;\nmod relation_table;'))
    influence = TARGET/'src/influence.rs'; text = influence.read_text()
    start = text.index('#[inline]\nfn least_tier(')
    end = text.index('/// Exclude from normalized own support',start)
    replacement = '''/// Classify the same four tested-piece tiers using capped count/tier states.
/// Pure lookup; consumers retain all semantic charge decisions.
#[inline]
pub fn relation(own: u8, opponent: u8, kind: PieceKind) -> Relation {
    let tested = match kind {
        PieceKind::Pawn => 0,
        PieceKind::Knight | PieceKind::Bishop => 1,
        PieceKind::Rook => 2,
        PieceKind::Queen => 3,
        PieceKind::King => panic!("king has no tested-piece relation tier"),
    };
    if opponent == 0 { return Relation::Favorable; }
    let own = (crate::relation_table::CLASS[own as usize] & 15) as usize;
    let opponent = (crate::relation_table::CLASS[opponent as usize] & 15) as usize;
    crate::relation_table::RELATIONS[tested][(own << 4) | opponent]
}

'''
    influence.write_text(text[:start]+replacement+text[end:])
    assert sources(ROOT) == baseline,'root source changed'
    after = sources(TARGET)
    archive = HERE/'prepared-source.tar.gz'
    paths = [*sorted((TARGET/'src').rglob('*.rs')),*sorted((TARGET/'tools').rglob('*')),TARGET/'Cargo.toml',TARGET/'Cargo.lock']
    expected = {str(p.relative_to(TARGET)):sha(p.read_bytes()) for p in paths if p.is_file()}
    with archive.open('xb') as raw:
        with gzip.GzipFile(filename='',mode='wb',fileobj=raw,mtime=0) as gz:
            with tarfile.open(fileobj=gz,mode='w') as output:
                for name in sorted(expected):
                    data = (TARGET/name).read_bytes(); member = tarfile.TarInfo(name)
                    member.size,member.mode = len(data),0o644
                    output.addfile(member,io.BytesIO(data))
    with tarfile.open(archive,'r:gz') as check:
        actual = {m.name:sha(check.extractfile(m).read()) for m in check}
    assert actual == expected
    result = dict(status='Uncompiled, untested source preparation; no runtime or CPU claim',path=str(TARGET),
                  baseline_source_sha256=baseline,variant_source_sha256=after,
                  modified_existing_files=[name for name in baseline if after[name] != baseline[name]],
                  generator_sha256=sha(Path(__file__).read_bytes()),states=states,data_bytes=1280,
                  archive=archive.name,archive_sha256=sha(archive.read_bytes()),archive_files=expected,verified_readback=True,
                  planned_validation='Existing independent full-digit exhaustive byte-pair/exclusion oracle, all131 library+2 CLI tests, all54 strict replays; six-case balanced generic native CPU pilot after the live canonical full54 collection terminates.',
                  scope='Relation and adjusted-relation pure kernel only. Influence, Position/Node layout, pawn cache, ordering, queries/charges and lifetimes unchanged.')
    with (HERE/'prepared.json').open('x') as stream: json.dump(result,stream,indent=2);stream.write('\n')
    print(json.dumps({key:result[key] for key in ['status','path','modified_existing_files','data_bytes','archive_sha256']}))


if __name__ == '__main__':
    main()
