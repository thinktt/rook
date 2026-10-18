#!/usr/bin/env python3
"""Cold source preparation only. No compilation, tests or engine execution."""
import hashlib
import json
from pathlib import Path
import shutil

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[1]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def sources(path):
    files = [path/'Cargo.toml', path/'Cargo.lock', *sorted((path/'src').rglob('*'))]
    return {str(p.relative_to(path)):sha(p) for p in files if p.is_file()}


def replace_once(text, old, new):
    assert text.count(old) == 1, old
    return text.replace(old, new)


def main():
    base = sources(ROOT)
    expected = json.loads((ROOT/'evidence/eval-geometry-build-20261018-02/receipt.json').read_text())['source_sha256_before']
    assert base == expected, 'baseline native source changed'
    report = dict(status='source-preparation-only; not compiled, tested, replayed or measured',
                  base_native_source_sha256=base, shared_kernel_sha256=sha(OUT/'attacks.rs'), variants={})
    for mode in ['persistent', 'local']:
        target = Path('/tmp')/f'imp2-bitplanes-{mode}-20261018'
        target.mkdir()
        for name in ['Cargo.toml', 'Cargo.lock']:
            shutil.copy2(ROOT/name, target/name)
        shutil.copytree(ROOT/'src', target/'src')
        shutil.copytree(ROOT/'tools', target/'tools', ignore=shutil.ignore_patterns('__pycache__'))
        shutil.copy2(OUT/'attacks.rs', target/'src/attacks.rs')
        p = target/'src/lib.rs'
        p.write_text(replace_once(p.read_text(), 'pub mod activity;', 'pub mod activity;\nmod attacks;'))

        p = target/'src/position.rs'
        text = p.read_text()
        text = replace_once(text, 'use crate::identity', 'use crate::attacks::AttackBits;\nuse crate::identity')
        accessor = '''    #[inline]
    pub(crate) fn attack_view(&self) -> AttackBits {
        SUPPLY
    }

'''.replace('SUPPLY', 'self.attack_bits' if mode == 'persistent' else 'AttackBits::from_position(self)')
        text = replace_once(text, '    #[inline]\n    fn group_start', accessor+'    #[inline]\n    fn group_start')
        if mode == 'persistent':
            text = replace_once(text, '    pub starting_units: u8,', '    pub starting_units: u8,\n    attack_bits: AttackBits,')
            text = replace_once(text, '            starting_units: 0,', '            starting_units: 0,\n            attack_bits: AttackBits::empty(),')
            text = replace_once(text, '        self.board[square.0 as usize] = piece;', '        self.attack_bits.replace(square, old, piece);\n        self.board[square.0 as usize] = piece;')
            text = replace_once(text, '        self.starting_units = self.recomputed_starting_units();', '        self.starting_units = self.recomputed_starting_units();\n        self.attack_bits = AttackBits::from_board(&self.board);')
            text = replace_once(text, '        let hashes = self.recomputed_identity();', '''        if !self.attack_bits.matches_board(&self.board) {
            return Err("attack planes/mailbox disagreement".into());
        }
        let hashes = self.recomputed_identity();''')
            text = replace_once(text, 'std::mem::size_of::<Position>(), 128', 'std::mem::size_of::<Position>(), 160')
            text = replace_once(text, 'std::mem::align_of::<Position>(), 4', 'std::mem::align_of::<Position>(), 8')
        p.write_text(text)
        if mode == 'persistent':
            p = target/'src/evaluator.rs'
            p.write_text(replace_once(p.read_text(), 'std::mem::size_of::<Node>(), 144', 'std::mem::size_of::<Node>(), 176'))

        p = target/'src/movegen.rs'
        text = p.read_text()
        text = replace_once(text, '    attacked(&position.board, king, side.opponent())', '    position.attack_view().attacked(king, side.opponent())')
        start = text.index('#[inline]\nfn legal_after(')
        end = text.index('\n/// The tactical caller', start)
        old = text[start:end]
        oracle = old.replace('#[inline]\nfn legal_after(', '#[cfg(test)]\nfn mailbox_legal_after(')
        common = '''#[inline]
fn legal_after_bits(position: &Position, mv: Move, king: Square, bits: crate::attacks::AttackBits) -> bool {
    let king = if position.board[mv.from().0 as usize].kind() == PieceKind::King { mv.to() } else { king };
    !bits.projected(position, mv).attacked(king, position.side.opponent())
}

#[inline]
fn legal_after(position: &Position, mv: Move, king: Square) -> bool {
    #[cfg(test)]
    if FORCE_PROJECTION.with(|forced| forced.get()) {
        return mailbox_legal_after(position, mv, king);
    }
    legal_after_bits(position, mv, king, position.attack_view())
}
'''
        text = text[:start]+oracle+'\n'+common+text[end:]
        if mode == 'local':
            text = replace_once(text, '    evasion_destinations: u64,', '    evasion_destinations: u64,\n    attack_view: std::cell::OnceCell<crate::attacks::AttackBits>,')
            text = replace_once(text, '            evasion_destinations,\n        }', '            evasion_destinations,\n            attack_view: std::cell::OnceCell::new(),\n        }')
            text = replace_once(text, '        legal_after(position, movement, self.king)\n    }', '''        let bits = self.attack_view.get_or_init(|| position.attack_view());
        legal_after_bits(position, movement, self.king, *bits)
    }''')
        p.write_text(text)
        report['variants'][mode] = dict(path=str(target), source_sha256=sources(target),
            layout=dict(position_bytes=160 if mode == 'persistent' else 128,
                        node_bytes=176 if mode == 'persistent' else 144),
            consumer_scope='Current-position in_check; generation safety Boolean projections including original EP/castling helper calls. Ordered checker/check_routes and quiescence mailbox reuse stay unchanged.',
            supply='Maintained exact tag planes' if mode == 'persistent' else 'Fresh ordered-list view for singleton queries; lazily reused OnceCell per immutable GenerationSafety fallback population; EP/castling helper queries build fresh views')
        assert sha(target/'src/attacks.rs') == report['shared_kernel_sha256']
    assert base == sources(ROOT), 'production native source changed during preparation'
    with (OUT/'prepared.json').open('x') as stream:
        json.dump(report, stream, indent=2); stream.write('\n')
    print(json.dumps(dict(status=report['status'], paths={k:v['path'] for k,v in report['variants'].items()})))


if __name__ == '__main__':
    main()
