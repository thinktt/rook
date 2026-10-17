// Standalone research microexperiment; not an engine crate or legal generator.
use std::{array, hint::black_box, mem::{align_of, offset_of, size_of}, time::Instant};
const NONE: u8 = 255;
const P: usize = 0;
const R: usize = 3;
const Q: usize = 4;
const K: usize = 5;
type Keys = [[[u32; 2]; 64]; 12];

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
#[repr(C)]
struct Rules { side: u8, rights: u8, ep: u8, halfmove: u8 }
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
#[repr(C)]
struct Position {
    board: [u8; 64],
    squares: [[u8; 16]; 2],
    counts: [[u8; 6]; 2],
    identity: [u32; 3],
    rules: Rules,
    raw_start: u8,
}
#[allow(dead_code)]
#[repr(C)]
struct WithSquare { pos: Position, square: i32 }
#[allow(dead_code)]
#[repr(C)]
struct BranchFrame { pos: Position, square: i32, retained: [i32; 2], age: u8 }
#[derive(Clone, Copy, Default)]
#[repr(C)]
struct Edit { kind: u8, piece: u8, index: u8, square: u8 }
#[derive(Clone, Copy)]
#[repr(C)]
struct Undo {
    identity: [u32; 3], edits: [Edit; 3],
    board_squares: [u8; 4], board_old: [u8; 4],
    rules: Rules, raw_start: u8, nb: u8, ne: u8,
}
#[derive(Clone, Copy)]
struct Move { from: u8, to: u8, promotion: u8, kind: u8 }
fn sq(s: &str) -> u8 { let b = s.as_bytes(); (b[1] - b'1') * 8 + b[0] - b'a' }
fn pc(side: usize, kind: usize) -> u8 { (side * 6 + kind + 1) as u8 }
fn split(piece: u8) -> (usize, usize) { (((piece - 1) / 6) as usize, ((piece - 1) % 6) as usize) }
fn mv(from: &str, to: &str, promotion: u8, kind: u8) -> Move {
    Move { from: sq(from), to: sq(to), promotion, kind }
}
fn keys() -> Keys {
    let mut state = 0x01234567u32;
    let coefficients: [u32; 1920] = array::from_fn(|_| {
        state = state.wrapping_mul(0xbb40e62d).wrapping_add(1);
        let high = ((state as i32) >> 16) as u32;
        state = state.wrapping_mul(0xbb40e62d).wrapping_add(1);
        high ^ state
    });
    array::from_fn(|piece| array::from_fn(|square| {
        let (side, kind) = split((piece + 1) as u8);
        let i = 80 * (2 * kind + side) + 10 * (square / 8) + square % 8 + 1;
        [coefficients[i], coefficients[960 + i]]
    }))
}
fn start_credit(square: u8, piece: u8) -> u8 {
    if piece == 0 { return 0; }
    let (side, kind) = split(piece);
    let rank = square / 8;
    let file = square % 8;
    if rank as usize == 7 * side {
        return match (kind, file) {
            (R, 0 | 7) | (1, 1 | 6) | (2, 2 | 5) | (Q, 3) => 2,
            _ => 0,
        };
    }
    if kind == P && rank as usize == if side == 0 { 1 } else { 6 } && (file == 3 || file == 4) { 1 } else { 0 }
}
fn derive(board: &[u8; 64], keys: &Keys) -> ([u32; 3], u8) {
    let mut identity = [0; 3];
    let mut start = 0;
    for (square, &piece) in board.iter().enumerate() {
        if piece != 0 {
            let contribution = keys[piece as usize - 1][square];
            identity[0] ^= contribution[0]; identity[1] ^= contribution[1];
            if split(piece).1 == P { identity[2] ^= contribution[0]; }
            start += start_credit(square as u8, piece);
        }
    }
    (identity, start)
}
fn mask(square: u8) -> u8 {
    match square { 0 => 1, 4 => 3, 7 => 2, 56 => 4, 60 => 12, 63 => 8, _ => 0 }
}
impl Position {
    fn group_start(&self, side: usize, kind: usize) -> usize {
        self.counts[side][..kind].iter().map(|&x| x as usize).sum()
    }
    fn len(&self, side: usize) -> usize { self.counts[side].iter().map(|&x| x as usize).sum() }
    fn locate(&self, piece: u8, square: u8) -> usize {
        let (side, kind) = split(piece);
        let start = self.group_start(side, kind);
        start + self.squares[side][start..start + self.counts[side][kind] as usize]
            .iter().position(|&s| s == square).unwrap()
    }
    fn remove(&mut self, piece: u8, index: usize) {
        let (side, kind) = split(piece); let len = self.len(side);
        self.squares[side].copy_within(index + 1..len, index);
        self.squares[side][len - 1] = NONE; self.counts[side][kind] -= 1;
    }
    fn insert(&mut self, piece: u8, index: usize, square: u8) {
        let (side, kind) = split(piece); let len = self.len(side);
        assert!(len < 16);
        self.squares[side].copy_within(index..len, index + 1);
        self.squares[side][index] = square; self.counts[side][kind] += 1;
    }
    fn validate(&self, keys: &Keys) {
        let mut board = [0; 64];
        for side in 0..2 {
            assert!(self.len(side) <= 16 && self.counts[side][P] <= 8 && self.counts[side][K] == 1);
            for kind in 0..6 {
                let start = self.group_start(side, kind);
                for &square in &self.squares[side][start..start + self.counts[side][kind] as usize] {
                    assert!(square < 64 && board[square as usize] == 0);
                    if kind == P { assert!(square / 8 != 0 && square / 8 != 7); }
                    board[square as usize] = pc(side, kind);
                }
            }
            assert!(self.squares[side][self.len(side)..].iter().all(|&s| s == NONE));
        }
        assert_eq!(board, self.board);
        assert_eq!(derive(&board, keys), (self.identity, self.raw_start));
    }
}
impl Undo {
    fn new(pos: &Position) -> Self {
        Self { identity: pos.identity, edits: [Edit::default(); 3], board_squares: [0; 4], board_old: [0; 4],
               rules: pos.rules, raw_start: pos.raw_start, nb: 0, ne: 0 }
    }
    fn edit(&mut self, kind: u8, piece: u8, index: usize, square: u8) {
        self.edits[self.ne as usize] = Edit { kind, piece, index: index as u8, square }; self.ne += 1;
    }
    fn write(&mut self, pos: &mut Position, square: u8, piece: u8, keys: &Keys) {
        let old = pos.board[square as usize];
        if !self.board_squares[..self.nb as usize].contains(&square) {
            self.board_squares[self.nb as usize] = square; self.board_old[self.nb as usize] = old; self.nb += 1;
        }
        for value in [old, piece] {
            if value == 0 { continue; }
            let k = keys[value as usize - 1][square as usize];
            pos.identity[0] ^= k[0]; pos.identity[1] ^= k[1];
            if split(value).1 == P { pos.identity[2] ^= k[0]; }
        }
        pos.raw_start = pos.raw_start - start_credit(square, old) + start_credit(square, piece);
        pos.board[square as usize] = piece;
    }
    fn restore(self, pos: &mut Position) {
        for e in self.edits[..self.ne as usize].iter().rev() {
            match e.kind {
                0 => pos.squares[split(e.piece).0][e.index as usize] = e.square,
                1 => pos.insert(e.piece, e.index as usize, e.square),
                2 => pos.remove(e.piece, e.index as usize),
                _ => unreachable!(),
            }
        }
        for i in 0..self.nb as usize { pos.board[self.board_squares[i] as usize] = self.board_old[i]; }
        pos.identity = self.identity; pos.rules = self.rules; pos.raw_start = self.raw_start;
    }
}
fn advance(pos: &mut Position, m: Move, keys: &Keys) -> Undo {
    let mut undo = Undo::new(pos);
    pos.rules.ep = NONE;
    if m.kind == 3 { pos.rules.side ^= 1; pos.rules.halfmove = pos.rules.halfmove.wrapping_add(1); return undo; }
    let piece = pos.board[m.from as usize]; let (side, kind) = split(piece);
    assert_eq!(side, pos.rules.side as usize);
    let victim_square = if m.kind == 1 { if side == 0 { m.to - 8 } else { m.to + 8 } } else { m.to };
    let victim = pos.board[victim_square as usize];
    if victim != 0 {
        assert_ne!(split(victim).0, side);
        let i = pos.locate(victim, victim_square); undo.edit(1, victim, i, victim_square); pos.remove(victim, i);
        undo.write(pos, victim_square, 0, keys);
    }
    let i = pos.locate(piece, m.from);
    let result = if m.promotion != NONE {
        undo.edit(1, piece, i, m.from); pos.remove(piece, i);
        let promoted = pc(side, m.promotion as usize);
        let j = pos.group_start(side, m.promotion as usize) + pos.counts[side][m.promotion as usize] as usize;
        undo.edit(2, promoted, j, m.to); pos.insert(promoted, j, m.to); promoted
    } else { undo.edit(0, piece, i, m.from); pos.squares[side][i] = m.to; piece };
    undo.write(pos, m.from, 0, keys); undo.write(pos, m.to, result, keys);
    if m.kind == 2 {
        let (rook_from, rook_to) = if m.to > m.from { (m.from + 3, m.from + 1) } else { (m.from - 4, m.from - 1) };
        let rook = pc(side, R); let j = pos.locate(rook, rook_from);
        undo.edit(0, rook, j, rook_from); pos.squares[side][j] = rook_to;
        undo.write(pos, rook_from, 0, keys); undo.write(pos, rook_to, rook, keys);
    }
    pos.rules.rights &= !(mask(m.from) | mask(m.to));
    if kind == P && m.from.abs_diff(m.to) == 16 {
        let file = m.to % 8;
        if (file != 0 && pos.board[m.to as usize - 1] == pc(side ^ 1, P)) ||
           (file != 7 && pos.board[m.to as usize + 1] == pc(side ^ 1, P)) { pos.rules.ep = (m.from + m.to) / 2; }
    }
    pos.rules.halfmove = if kind == P || victim != 0 { 0 } else { pos.rules.halfmove.wrapping_add(1) };
    pos.rules.side ^= 1;
    undo
}

// Independent chronology reference uses one Vec per type and recomputed derived fields.
fn reference(mut pos: Position, m: Move, keys: &Keys) -> Position {
    let mut groups: [[Vec<u8>; 6]; 2] = array::from_fn(|side| array::from_fn(|kind| {
        let start = pos.group_start(side, kind);
        pos.squares[side][start..start + pos.counts[side][kind] as usize].to_vec()
    }));
    pos.rules.ep = NONE;
    if m.kind != 3 {
        let source = pos.board[m.from as usize]; let (side, kind) = split(source);
        let capture_square = if m.kind == 1 { if side == 0 { m.to - 8 } else { m.to + 8 } } else { m.to };
        let captured = pos.board[capture_square as usize];
        if captured != 0 { let (s, k) = split(captured); groups[s][k].retain(|&q| q != capture_square); pos.board[capture_square as usize] = 0; }
        if m.promotion != NONE {
            groups[side][kind].retain(|&q| q != m.from); groups[side][m.promotion as usize].push(m.to);
            pos.board[m.to as usize] = pc(side, m.promotion as usize);
        } else {
            *groups[side][kind].iter_mut().find(|q| **q == m.from).unwrap() = m.to; pos.board[m.to as usize] = source;
        }
        pos.board[m.from as usize] = 0;
        if m.kind == 2 {
            let base = if side == 0 { 0 } else { 56 };
            let (from, to) = if m.to % 8 == 6 { (base + 7, base + 5) } else { (base, base + 3) };
            *groups[side][R].iter_mut().find(|q| **q == from).unwrap() = to;
            pos.board[from as usize] = 0; pos.board[to as usize] = pc(side, R);
        }
        pos.rules.rights &= !(mask(m.from) | mask(m.to));
        if kind == P && m.from.abs_diff(m.to) == 16 {
            let rank = m.to / 8; let file = m.to % 8;
            for other in 0..8 {
                if file.abs_diff(other) == 1 && pos.board[(rank * 8 + other) as usize] == pc(side ^ 1, P) { pos.rules.ep = (m.from + m.to) / 2; }
            }
        }
        pos.rules.halfmove = if kind == P || captured != 0 { 0 } else { pos.rules.halfmove.wrapping_add(1) };
    } else { pos.rules.halfmove = pos.rules.halfmove.wrapping_add(1); }
    pos.rules.side ^= 1;
    pos.squares = [[NONE; 16]; 2];
    for side in 0..2 { let mut i = 0; for kind in 0..6 { pos.counts[side][kind] = groups[side][kind].len() as u8; for &square in &groups[side][kind] { pos.squares[side][i] = square; i += 1; } } }
    (pos.identity, pos.raw_start) = derive(&pos.board, keys); pos
}
fn setup(pieces: &[(usize, usize, &str)], rules: Rules, keys: &Keys) -> Position {
    let mut pos = Position { board: [0; 64], squares: [[NONE; 16]; 2], counts: [[0; 6]; 2], identity: [0; 3], rules, raw_start: 0 };
    for &(side, kind, name) in pieces { let square = sq(name); assert_eq!(pos.board[square as usize], 0); pos.board[square as usize] = pc(side, kind); }
    for side in 0..2 { for kind in 0..6 { for &(s, k, name) in pieces { if (s, k) == (side, kind) { let end = pos.len(side); pos.insert(pc(side, kind), end, sq(name)); } } } }
    (pos.identity, pos.raw_start) = derive(&pos.board, keys); pos.validate(keys); pos
}
fn cases(keys: &Keys) -> Vec<(&'static str, Position, Move)> {
    let rules = |side, rights, ep, halfmove| Rules { side, rights, ep, halfmove };
    let mut out = Vec::new();
    let common = [(0,K,"e1"),(1,K,"e8")];
    let mut add = |name, pieces: &[(usize,usize,&str)], rules, m| {
        out.push((name, setup(pieces, rules, keys), m));
    };
    add("quiet-wrap", &[(0,K,"e1"),(1,K,"e8"),(0,1,"g1"),(0,1,"b1")], rules(0,0,NONE,255), mv("b1","c3",NONE,0));
    add("capture-middle", &[(0,K,"e1"),(1,K,"e8"),(0,2,"f1"),(0,2,"c4"),(1,P,"h7"),(1,P,"f7"),(1,P,"a7")], rules(0,0,NONE,37), mv("c4","f7",NONE,0));
    add("promotion-append", &[(0,K,"e1"),(1,K,"e8"),(0,P,"c2"),(0,P,"f7"),(0,P,"h2"),(0,Q,"d4"),(0,Q,"a2")], rules(0,0,NONE,10), mv("f7","f8",Q as u8,0));
    add("capture-underpromotion", &[(0,K,"e1"),(1,K,"g8"),(0,P,"b7"),(0,1,"g1"),(0,1,"c3"),(1,R,"h8"),(1,R,"a8"),(1,R,"b5")], rules(0,12,NONE,18), mv("b7","a8",1,0));
    add("white-short-castle", &[(0,K,"e1"),(1,K,"e8"),(0,R,"h1"),(0,R,"a1")], rules(0,3,NONE,99), mv("e1","g1",NONE,2));
    add("black-long-castle", &[(0,K,"e1"),(1,K,"e8"),(1,R,"h8"),(1,R,"a8")], rules(1,12,NONE,10), mv("e8","c8",NONE,2));
    add("white-en-passant", &[(0,K,"a1"),(1,K,"h8"),(0,P,"e5"),(1,P,"h6"),(1,P,"d5"),(1,P,"a6")], rules(0,0,sq("d6"),20), mv("e5","d6",NONE,1));
    add("black-en-passant", &[(0,K,"a1"),(1,K,"h8"),(1,P,"d4"),(0,P,"h3"),(0,P,"e4"),(0,P,"a3")], rules(1,0,sq("e3"),20), mv("d4","e3",NONE,1));
    add("joined-rook-ep-victim", &[(0,K,"a1"),(1,K,"g8"),(0,P,"e5"),(1,R,"f8"),(1,R,"d5"),(1,R,"h7")], rules(0,0,sq("d6"),20), mv("e5","d6",NONE,1));
    add("null-wrap-expire", &[(0,K,"a1"),(1,K,"h8"),(0,P,"f5"),(1,P,"e5")], rules(0,0,sq("e6"),255), Move{from:0,to:0,promotion:NONE,kind:3});
    let mut push = common.to_vec(); push.extend([(0,P,"e2"),(1,P,"d4")]);
    add("double-push-neighbor", &push, rules(0,0,NONE,0), mv("e2","e4",NONE,0));
    add("double-push-no-neighbor", &[(0,K,"e1"),(1,K,"e8"),(0,P,"e2")], rules(0,0,NONE,0), mv("e2","e4",NONE,0));
    out
}
fn digest(pos: &Position) -> u64 {
    let mut h = 0x81237811u64;
    for byte in pos.board.iter().chain(pos.squares.iter().flatten()).chain(pos.counts.iter().flatten()) {
        h = h.rotate_left(5) ^ *byte as u64;
    }
    for &word in &pos.identity { h = h.rotate_left(5) ^ word as u64; }
    for byte in [pos.rules.side,pos.rules.rights,pos.rules.ep,pos.rules.halfmove,pos.raw_start] { h = h.rotate_left(5) ^ byte as u64; }
    h
}
#[inline(never)]
fn copy_route(parent: &Position, m: Move, keys: &Keys) -> u64 {
    let mut child = *black_box(parent); let _unused_undo = advance(&mut child, m, keys);
    let child_output = digest(black_box(&child));
    black_box(child_output ^ digest(black_box(parent)))
}
#[inline(never)]
fn delta_route(parent: &mut Position, m: Move, keys: &Keys) -> u64 {
    let undo = advance(black_box(parent), m, keys);
    let child_output = digest(black_box(&*parent)); undo.restore(parent);
    black_box(child_output ^ digest(black_box(&*parent)))
}
fn run(cases: &[(&str,Position,Move)], keys: &Keys, repeats: usize, delta: bool) -> (u128,u64) {
    let mut parents: Vec<Position> = cases.iter().map(|c| c.1).collect();
    let start = Instant::now(); let mut fold = 0u64;
    for _ in 0..repeats { for (i, case) in cases.iter().enumerate() {
        let value = if delta { delta_route(&mut parents[i],case.2,keys) } else { copy_route(&parents[i],case.2,keys) };
        fold = fold.wrapping_mul(0x100000001b3).wrapping_add(value);
    } }
    (start.elapsed().as_nanos(), black_box(fold))
}
fn main() {
    let keys = keys(); let cases = cases(&keys);
    for (_, parent, m) in &cases {
        let expected = reference(*parent,*m,&keys); let mut child = *parent;
        let undo = advance(&mut child,*m,&keys); child.validate(&keys); assert_eq!(child,expected);
        undo.restore(&mut child); child.validate(&keys); assert_eq!(child,*parent);
        let mut mutable = *parent; assert_eq!(copy_route(parent,*m,&keys),delta_route(&mut mutable,*m,&keys)); assert_eq!(mutable,*parent);
    }
    // Prove broad setup capacity: one king plus fifteen of any non-pawn type.
    for kind in 1..5 {
        let mut pieces = vec![(0,K,"a1"),(1,K,"h8")];
        let names = ["a2","b2","c2","d2","e2","f2","g2","h2","a3","b3","c3","d3","e3","f3","g3"];
        pieces.extend(names.iter().map(|&s| (0,kind,s)));
        let pos = setup(&pieces,Rules{side:0,rights:0,ep:NONE,halfmove:0},&keys); assert_eq!(pos.len(0),16); assert_eq!(pos.counts[0][kind],15);
    }
    assert_eq!(size_of::<Position>(),128); assert_eq!(size_of::<Undo>(),40);
    println!("{{\"proof\":\"pass\",\"cases\":{},\"capacity_cases\":4,\"layout\":{{\"position_bytes\":{},\"alignment\":{},\"identity_offset\":{},\"rules_offset\":{},\"raw_start_offset\":{},\"with_square_bytes\":{},\"branch_frame_bytes\":{},\"undo_bytes\":{}}},\"repeats\":4096,\"samples\":[",cases.len(),size_of::<Position>(),align_of::<Position>(),offset_of!(Position,identity),offset_of!(Position,rules),offset_of!(Position,raw_start),size_of::<WithSquare>(),size_of::<BranchFrame>(),size_of::<Undo>());
    let _ = run(&cases,&keys,512,false); let _ = run(&cases,&keys,512,true);
    for sample in 0..3 {
        let (copy,delta) = if sample % 2 == 0 { (run(&cases,&keys,4096,false),run(&cases,&keys,4096,true)) }
            else { let delta=run(&cases,&keys,4096,true); let copy=run(&cases,&keys,4096,false); (copy,delta) };
        assert_eq!(copy.1,delta.1);
        println!("{{\"copy_ns\":{},\"delta_ns\":{},\"fold\":{}}}{}",copy.0,delta.0,copy.1,if sample==2 {""} else {","});
    }
    println!("]}}");
}
