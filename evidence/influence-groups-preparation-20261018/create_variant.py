#!/usr/bin/env python3
"""Cold typed-list influence prototype; no engine/compiler execution."""
import gzip
import hashlib
import io
import json
from pathlib import Path
import shutil
import tarfile

PREP = Path(__file__).resolve().parent
ROOT = PREP.parents[1]
TARGET = Path('/tmp/imp2-influence-groups-20261018')


def sha(data):
    return hashlib.sha256(data).hexdigest()


def sources(root):
    return {str(p.relative_to(root)):sha(p.read_bytes()) for p in
            [root/'Cargo.toml', root/'Cargo.lock', *sorted((root/'src').rglob('*.rs'))]}


def main():
    baseline = sources(ROOT)
    reference = json.loads((ROOT/'evidence/production-bitplanes-use-build-20261018/receipt.json').read_text())
    assert baseline == reference['source_sha256_before']
    TARGET.mkdir()
    for name in ['Cargo.toml', 'Cargo.lock']:
        shutil.copy2(ROOT/name, TARGET/name)
    shutil.copytree(ROOT/'src', TARGET/'src')
    shutil.copytree(ROOT/'tools', TARGET/'tools', ignore=shutil.ignore_patterns('__pycache__'))
    path = TARGET/'src/influence.rs'
    text = path.read_text()
    old = '''    pub fn build(position: &Position) -> Self {
        Self::build_board(&position.board)
    }'''
    replacement = '''    pub fn build(position: &Position) -> Self {
        let mut influence = Self { profiles: [[0; 64]; 2] };
        // Wrapping placement-only sums commute. Type/side ownership comes from
        // the coherent chronological lists; ray semantics still read the board.
        for side in [Color::White, Color::Black] {
            for &source in position.piece_squares(side, PieceKind::Pawn) {
                debug_assert!(source.0 < 64);
                let targets = &PAWN_TARGETS[side.index()][(source.0 & 63) as usize];
                for &target in &targets.squares[..targets.len as usize] {
                    influence.add(side, Square(target & 63), Contribution::Pawn as u8);
                }
            }
            for &source in position.piece_squares(side, PieceKind::Knight) {
                debug_assert!(source.0 < 64);
                let targets = &KNIGHT_SOURCES[(source.0 & 63) as usize];
                for &target in &targets.squares[..targets.len as usize] {
                    influence.add(side, Square(target & 63), Contribution::Minor as u8);
                }
            }
            for &source in position.piece_squares(side, PieceKind::King) {
                debug_assert!(source.0 < 64);
                let targets = &KING_TARGETS[(source.0 & 63) as usize];
                for &target in &targets.squares[..targets.len as usize] {
                    influence.add(side, Square(target & 63), Contribution::Weak as u8);
                }
            }
            for &source in position.piece_squares(side, PieceKind::Bishop) {
                for direction in 0..4 {
                    influence.ray(&position.board, side, source, direction, Contribution::Minor);
                }
            }
            for &source in position.piece_squares(side, PieceKind::Rook) {
                for direction in 4..8 {
                    influence.ray(&position.board, side, source, direction, Contribution::Rook);
                }
            }
            for &source in position.piece_squares(side, PieceKind::Queen) {
                for direction in 0..8 {
                    influence.ray(&position.board, side, source, direction, Contribution::Queen);
                }
            }
        }
        influence
    }'''
    assert text.count(old) == 1
    text = text.replace(old, replacement)
    assert text.count('    fn build_board(') == 1
    text = text.replace('    fn build_board(', '    #[cfg(test)]\n    fn build_board(')
    test = r'''
    #[test]
    fn typed_list_maps_match_mailbox_and_target_oracles_after_order_changes() {
        let mut random = 0x52a8_137f_0189_721du64;
        for count in 0..10000 {
            let mut board = board(&[("a1", Color::White, PieceKind::King), ("h8", Color::Black, PieceKind::King)]);
            for n in 0..(count % 31) {
                loop {
                    random ^= random << 13;
                    random ^= random >> 7;
                    random ^= random << 17;
                    let index = (random & 63) as usize;
                    if !board[index].is_empty() { continue; }
                    let side = if n % 2 == 0 { Color::White } else { Color::Black };
                    // At most three pawns/color and15 non-kings/color; promoted
                    // counts and arbitrary checks/adjacency remain admitted.
                    let mut kind = PieceKind::ALL[(n / 2) % 5];
                    if kind == PieceKind::Pawn && (index < 8 || index >= 56) { kind = PieceKind::Knight; }
                    board[index] = Piece::new(side, kind);
                    break;
                }
            }
            let mut rows = Vec::new();
            for rank in (0..8).rev() {
                let mut row = String::new();
                let mut empty = 0;
                for file in 0..8 {
                    let piece = board[rank * 8 + file];
                    if piece.is_empty() { empty += 1; continue; }
                    if empty != 0 { row.push(char::from(b'0' + empty)); empty = 0; }
                    row.push(piece.fen_char());
                }
                if empty != 0 { row.push(char::from(b'0' + empty)); }
                rows.push(row);
            }
            let mut position = Position::from_fen(&format!("{} w - - 0 1", rows.join("/"))).unwrap();
            let expected = Influence::build_board(&board);
            assert_eq!(expected.profiles, reference_map(&board));
            assert_eq!(Influence::build(&position), expected);
            for side in [Color::White, Color::Black] {
                let mut start = 0;
                for kind in PieceKind::ALL {
                    let len = position.counts[side.index()][kind.index()] as usize;
                    position.squares[side.index()][start..start + len].reverse();
                    start += len;
                }
            }
            position.validate().unwrap();
            assert_eq!(Influence::build(&position), expected);
        }
    }
'''
    end = text.rfind('\n}')
    assert end > 0
    path.write_text(text[:end] + '\n' + test + text[end:])
    assert sources(ROOT) == baseline
    after = sources(TARGET)
    archive = PREP/'prepared-source.tar.gz'
    files = {str(p.relative_to(TARGET)):sha(p.read_bytes()) for p in
             [*sorted((TARGET/'src').rglob('*.rs')), *sorted((TARGET/'tools').rglob('*')), TARGET/'Cargo.toml', TARGET/'Cargo.lock'] if p.is_file()}
    with archive.open('xb') as raw:
        with gzip.GzipFile(filename='', mode='wb', fileobj=raw, mtime=0) as gz:
            with tarfile.open(fileobj=gz, mode='w') as output:
                for name in sorted(files):
                    data = (TARGET/name).read_bytes()
                    member = tarfile.TarInfo(name)
                    member.size, member.mode = len(data), 0o644
                    output.addfile(member, io.BytesIO(data))
    with tarfile.open(archive, 'r:gz') as check:
        assert {m.name:sha(check.extractfile(m).read()) for m in check} == files
    result = dict(status='Cold source preparation only; uncompiled and unmeasured', path=str(TARGET),
                  baseline_source_sha256=baseline, variant_source_sha256=after,
                  modified_existing_files=[name for name in baseline if baseline[name] != after[name]],
                  generator_sha256=sha(Path(__file__).read_bytes()), archive=archive.name,
                  archive_sha256=sha(archive.read_bytes()), archive_files=files,
                  planned_native_tests=134,
                  scope='Influence production enumeration only; unchanged normalized sums, ray traversal, relations/R charges, Position/Node and state lifetimes. Old mailbox builder remains test-only oracle. No inferred CPU/PGO benefit.')
    with (PREP/'prepared.json').open('x') as stream:
        json.dump(result, stream, indent=2)
        stream.write('\n')
    print(json.dumps({k:result[k] for k in ['status', 'path', 'modified_existing_files', 'archive_sha256']}))


if __name__ == '__main__':
    main()
