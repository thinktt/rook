//! Independent coordinate/count controls. Expected values never use plane masks,
//! ray tables, prefixes, expansion tables or the new byte emitter.
use super::*;
use crate::types::{MoveKind, Piece};

fn sq(text: &str) -> Square { Square::parse(text).unwrap() }
fn at(source: usize, df: i32, dr: i32) -> Option<usize> {
    let f = (source % 8) as i32 + df;
    let r = (source / 8) as i32 + dr;
    if (0..8).contains(&f) && (0..8).contains(&r) { Some((8 * r + f) as usize) } else { None }
}
const STEPS: [(i32, i32); 8] = [(1,1),(-1,-1),(-1,1),(1,-1),(0,1),(0,-1),(1,0),(-1,0)];
fn placement(mut board: [Piece; 64]) -> Position {
    // Add only missing kings, away from the fixed d4 ray witnesses when possible.
    for (side, preferred) in [(Color::White, 0usize), (Color::Black, 63usize)] {
        if !board.iter().any(|&p| p == Piece::new(side, PieceKind::King)) {
            let slot = if board[preferred].is_empty() { preferred }
                else { (0..64).find(|&i| board[i].is_empty()).unwrap() };
            board[slot] = Piece::new(side, PieceKind::King);
        }
    }
    let mut fen = String::new();
    for rank in (0..8).rev() {
        if rank != 7 { fen.push('/'); }
        let mut empty = 0u8;
        for file in 0..8 {
            let piece = board[8 * rank + file];
            if piece.is_empty() { empty += 1; }
            else {
                if empty != 0 { fen.push((b'0' + empty) as char); empty = 0; }
                let c = ['p','n','b','r','q','k'][piece.kind().index()];
                fen.push(if piece.color() == Color::White { c.to_ascii_uppercase() } else { c });
            }
        }
        if empty != 0 { fen.push((b'0' + empty) as char); }
    }
    Position::from_fen(&format!("{fen} w - - 0 1")).unwrap()
}
fn described(pieces: &[(&str, Color, PieceKind)]) -> Position {
    let mut board = [Piece::EMPTY;64];
    for &(name, side, kind) in pieces { let i=sq(name).0 as usize; assert!(board[i].is_empty()); board[i]=Piece::new(side,kind); }
    placement(board)
}

// Scalar coordinate ray witness: add before inspecting an occupant, and an
// explicit one-extra iteration for a stopping forward pawn. Independent from
// the production first-opaque/first-queen set construction.
fn ray_masks_ref(board: &[Piece;64], side: Color, source: Square, kind: PieceKind) -> (u64,u64) {
    let mut normal = 0; let mut weak = 0;
    for (i,(df,dr)) in STEPS.into_iter().enumerate() {
        if (kind==PieceKind::Bishop && i>=4) || (kind==PieceKind::Rook && i<4) { continue; }
        let mut weakened = false;
        for distance in 1..8 {
            let Some(target)=at(source.0 as usize,distance*df,distance*dr) else { break; };
            if weakened { weak |= 1u64<<target; } else { normal |= 1u64<<target; }
            let piece=board[target]; if piece.is_empty() { continue; }
            let occupant=piece.kind(); let own=piece.color()==side;
            if !own && occupant==PieceKind::King { continue; }
            if own && occupant==PieceKind::Queen { weakened=true; continue; }
            if own && ((i<4 && occupant==PieceKind::Bishop) || (i>=4 && occupant==PieceKind::Rook)) { continue; }
            if own && occupant==PieceKind::Pawn && i<4 && dr==(if side==Color::White {1} else {-1}) {
                if let Some(extra)=at(target,df,dr) {
                    if weakened { weak|=1u64<<extra; } else { normal|=1u64<<extra; }
                }
            }
            break;
        }
    }
    (normal,weak)
}

// Target-centric oracle: source inventory remains authoritative, while path
// decisions use integer coordinates and actual mailbox pieces. Accumulate
// category counts, then normalize by division rather than wrapping byte adds.
fn map_ref(position: &Position) -> [[u8;64];2] {
    let mut result=[[0;64];2];
    for target in 0..64 {
        let mut counts=[[0u16;5];2];
        for side in [Color::White,Color::Black] { for kind in PieceKind::ALL {
            for &source in position.piece_squares(side,kind) {
                if source.0 as usize==target { continue; }
                let dx=(target%8) as i32-i32::from(source.file());
                let dy=(target/8) as i32-i32::from(source.rank());
                let simple=match kind {
                    PieceKind::Pawn => (dx.abs()==1 && dy==(if side==Color::White {1} else {-1})).then_some(4),
                    PieceKind::Knight => (dx.abs()*dy.abs()==2).then_some(3),
                    PieceKind::King => (dx.abs().max(dy.abs())==1).then_some(0), _=>None };
                if let Some(category)=simple { counts[side.index()][category]+=1; continue; }
                let diagonal=dx.abs()==dy.abs(); let orthogonal=dx==0 || dy==0;
                let mut category=match kind { PieceKind::Bishop if diagonal=>3, PieceKind::Rook if orthogonal=>2,
                    PieceKind::Queen if diagonal || orthogonal=>1, _=>continue };
                let step=(dx.signum(),dy.signum());
                let mut cursor=at(source.0 as usize,step.0,step.1).unwrap();
                let reached=loop {
                    if cursor==target { break true; }
                    let piece=position.board[cursor];
                    if !piece.is_empty() {
                        let own=piece.color()==side;let occupant=piece.kind();
                        if own && occupant==PieceKind::Queen { category=0; }
                        else if (!own && occupant==PieceKind::King)
                            || (own && diagonal && occupant==PieceKind::Bishop)
                            || (own && orthogonal && occupant==PieceKind::Rook) { }
                        else { break own && occupant==PieceKind::Pawn && diagonal
                            && step.1==(if side==Color::White {1} else {-1}) && at(cursor,step.0,step.1)==Some(target); }
                    }
                    cursor=at(cursor,step.0,step.1).unwrap();
                };
                if reached { counts[side.index()][category]+=1; }
            }
        } }
        for side in 0..2 {
            for (digit,radix) in [2,2,4,4].into_iter().enumerate() {
                let carry=counts[side][digit]/radix;counts[side][digit]%=radix;counts[side][digit+1]+=carry;
            }
            counts[side][4]%=4;
            result[side][target]=(counts[side][0]+2*counts[side][1]+4*counts[side][2]+16*counts[side][3]+64*counts[side][4]) as u8;
        }
    }
    result
}
fn check(position: &Position) {
    position.validate().unwrap();
    let expected=map_ref(position);
    assert_eq!(Influence::build(position).profiles,expected,"old scalar versus independent counts");
    assert_eq!(Influence::build_coherent(position).profiles,expected,"new full128 bytes");
}
fn emitted<const SHIFT:i32>(previous:[u8;64],normal:u64,weak:u64) {
    assert_eq!(normal & weak,0);
    let actual=coherent::emit_for_test::<SHIFT>(previous,normal,weak);
    for lane in 0..64 {
        let add=if normal & (1u64<<lane)!=0 {1u16<<SHIFT} else if weak & (1u64<<lane)!=0 {1} else {0};
        assert_eq!(actual[lane],((u16::from(previous[lane])+add)%256) as u8,"lane={lane} shift={SHIFT}");
    }
}

#[test]
fn experiment37_emission_all_fragment_lanes_previous_bytes_and_wrap() {
    for fragment in 0..=255u16 { for chunk in 0..8 {
        let normal=u64::from(fragment)<<(8*chunk);
        let previous=std::array::from_fn(|i| (i as u8).wrapping_mul(73).wrapping_add(fragment as u8));
        let weak=0x5555_aaaa_5555_aaaau64 & !normal;
        emitted::<1>(previous,normal,weak);emitted::<2>(previous,normal,weak);emitted::<4>(previous,normal,weak);
    } }
    for prior in 0..=255u16 { for lane in 0..64 {
        let normal=1u64<<lane;let weak=0xaaaa_5555_aaaa_5555u64 & !normal;
        emitted::<1>([prior as u8;64],normal,weak);emitted::<2>([prior as u8;64],normal,weak);emitted::<4>([prior as u8;64],normal,weak);
    }
        // Also exercise the no-weak expansion branch and zero masks.
        emitted::<1>([prior as u8;64],u64::MAX,0);emitted::<2>([prior as u8;64],u64::MAX,0);
        emitted::<4>([prior as u8;64],u64::MAX,0);emitted::<4>([prior as u8;64],0,0);
    }
}

#[test]
fn experiment37_slider_masks_and_full_bytes_match_coordinate_ray_controls() {
    let source=sq("d4");
    for side in [Color::White,Color::Black] { for kind in [PieceKind::Bishop,PieceKind::Rook,PieceKind::Queen] {
        for (i,(df,dr)) in STEPS.into_iter().enumerate() {
            if (kind==PieceKind::Bishop && i>=4) || (kind==PieceKind::Rook && i<4) {continue;}
            for pattern in 0..10 {
                let mut board=[Piece::EMPTY;64];board[source.0 as usize]=Piece::new(side,kind);
                let one=at(source.0 as usize,df,dr).unwrap();let two=at(source.0 as usize,2*df,2*dr).unwrap();let three=at(source.0 as usize,3*df,3*dr).unwrap();
                let matching=if i<4 {PieceKind::Bishop} else {PieceKind::Rook};
                match pattern {
                    0=>{},
                    1=>{board[one]=Piece::new(side.opponent(),PieceKind::King);board[three]=Piece::new(side.opponent(),PieceKind::Rook);},
                    2=>{board[one]=Piece::new(side,PieceKind::King);},
                    3=>{board[one]=Piece::new(side,PieceKind::Queen);board[two]=Piece::new(side,PieceKind::Queen);board[three]=Piece::new(side.opponent(),PieceKind::Rook);},
                    4=>{board[one]=Piece::new(side,matching);board[two]=Piece::new(side,PieceKind::Queen);board[three]=Piece::new(side.opponent(),PieceKind::Bishop);},
                    5=>{board[two]=Piece::new(side,PieceKind::Pawn);board[three]=Piece::new(side.opponent(),PieceKind::Queen);},
                    6=>{board[one]=Piece::new(side,PieceKind::Queen);board[two]=Piece::new(side,PieceKind::Pawn);board[three]=Piece::new(side.opponent(),PieceKind::Knight);},
                    7=>{board[one]=Piece::new(side.opponent(),PieceKind::Pawn);board[two]=Piece::new(side,PieceKind::Queen);},
                    8=>{board[two]=Piece::new(side,PieceKind::Pawn);board[three]=Piece::new(side,PieceKind::Queen);},
                    9=>{board[one]=Piece::new(side,PieceKind::Queen);board[two]=Piece::new(side,PieceKind::Pawn);board[three]=Piece::new(side,PieceKind::Queen);},_=>unreachable!()
                }
                let position=placement(board);
                let actual=match kind {PieceKind::Bishop=>coherent::slider_masks::<2>(position.attack_planes(),side,source),
                    PieceKind::Rook=>coherent::slider_masks::<3>(position.attack_planes(),side,source),
                    PieceKind::Queen=>coherent::slider_masks::<4>(position.attack_planes(),side,source),_=>unreachable!()};
                assert_eq!(actual,ray_masks_ref(&position.board,side,source,kind),"side={side:?} kind={kind:?} direction={i} pattern={pattern}");
                assert_eq!(actual.0 & actual.1,0);check(&position);
            }
        }
    } }
}

#[test]
fn experiment37_complete_maps_carries_transitions_null_and_chronology() {
    use Color::White as W;use PieceKind::*;
    let crowded=described(&[("d3",W,Pawn),("f3",W,Pawn),("c3",W,Knight),("c5",W,Knight),("d2",W,Knight),
        ("d6",W,Knight),("f2",W,Knight),("f6",W,Knight),("g3",W,Knight),("g5",W,Knight)]);
    check(&crowded);assert_eq!(Influence::build_coherent(&crowded).code(W,sq("e4")),0);
    let bishops=described(&[("d3",W,Pawn),("f3",W,Pawn),("b1",W,Bishop),("c2",W,Bishop),("d5",W,Bishop),
        ("c6",W,Bishop),("b7",W,Bishop),("a8",W,Bishop),("f5",W,Bishop),("g6",W,Bishop),("h7",W,Bishop),("g2",W,Bishop)]);
    check(&bishops);assert_eq!(Influence::build_coherent(&bishops).code(W,sq("e4")),32);
    for original in [crowded,bishops] {
        let mut board=[Piece::EMPTY;64];
        for (i,piece) in original.board.into_iter().enumerate() {
            if !piece.is_empty() {board[i^56]=Piece::new(piece.color().opponent(),piece.kind());}
        }
        let mirrored=placement(board);check(&mirrored);
        let before=Influence::build_coherent(&original);let after=Influence::build_coherent(&mirrored);
        for side in [Color::White,Color::Black] {for i in 0..64 {assert_eq!(before.profiles[side.index()][i],after.profiles[side.opponent().index()][i^56]);}}
    }
    let roots=["rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",
        "r3k2r/8/8/8/8/8/8/R3K2R w KQkq - 0 1","7k/P7/8/3pP3/8/8/8/K7 w - d6 0 1",
        "7k/8/8/8/8/8/4P3/K7 w - - 0 1"];
    for fen in roots {let mut position=Position::from_fen(fen).unwrap();for step in 0..12 {
        check(&position);check(&position.null_child());
        let mut chronology=position;
        for side in 0..2 {let mut begin=0;for count in chronology.counts[side] {let end=begin+usize::from(count);chronology.squares[side][begin..end].reverse();begin=end;}}
        check(&chronology);assert_eq!(Influence::build_coherent(&position),Influence::build_coherent(&chronology));
        let mut moves=crate::movegen::MoveList::new();crate::movegen::generate_legal(&position,&mut moves);if moves.as_slice().is_empty(){break;}
        position=position.played_unchecked(moves.as_slice()[(7*step+1)%moves.as_slice().len()]);
    }}
    for (fen,from,to,expected_kind) in [
        ("r3k2r/8/8/8/8/8/8/R3K2R w KQkq - 0 1","e1","g1",MoveKind::Castle),
        ("7k/8/8/3pP3/8/8/8/K7 w - d6 0 1","e5","d6",MoveKind::EnPassant),
        ("7k/P7/8/8/8/8/8/K7 w - - 0 1","a7","a8",MoveKind::Promotion(Queen)),
        ("7k/8/8/3n4/4B3/8/8/K7 w - - 0 1","e4","d5",MoveKind::Ordinary)] {
        let parent=Position::from_fen(fen).unwrap();let mut moves=crate::movegen::MoveList::new();crate::movegen::generate_legal(&parent,&mut moves);
        let movement=*moves.as_slice().iter().find(|m| m.from()==sq(from)&&m.to()==sq(to)&&m.kind()==expected_kind).expect("required native legal special/capture witness");
        check(&parent);let child=parent.played_unchecked(movement);check(&child);check(&child.null_child());
    }
}

#[test]
fn experiment37_public_scalar_mailbox_domain_is_not_redirected() {
    use Color::White as W;use PieceKind::*;
    let base=described(&[("c1",W,Bishop)]);let mut stale=base;
    stale.board[sq("d2").0 as usize]=Piece::new(W,Queen);
    assert_eq!(stale.attack_view(),base.attack_view());
    assert_eq!(Influence::build(&stale).profiles,map_ref(&stale));
    assert_ne!(Influence::build(&stale),Influence::build(&base));
    for raw in 1..=255u16 {if (1..=6).contains(&((raw as u8)&7)) {
        let mut alias=base;alias.board[sq("d2").0 as usize]=Piece(raw as u8);
        assert_eq!(Influence::build(&alias).profiles,map_ref(&alias));
    }}
    let mut unvisited=base;unvisited.board[sq("e8").0 as usize]=Piece(0x87);
    assert_eq!(Influence::build(&unvisited).profiles,map_ref(&unvisited));
    let mut visited=base;visited.board[sq("d2").0 as usize]=Piece(0x08);
    assert!(std::panic::catch_unwind(|| Influence::build(&visited)).is_err());
    // Deliberately do not call build_coherent on any violated precondition.
    // Component panic assertions do not imply Session unwind/recovery support.
}


#[test]
fn experiment43_actual_bitplanes_transpose_carries_and_multiplicity() {
    for bit in 0..8 { for target in 0..64 {
        let mut planes = [0;8]; planes[bit] = 1u64 << target;
        let mut expected = [0;64]; expected[target] = 1u8 << bit;
        assert_eq!(coherent::bitplanes_for_test(planes), expected, "bit={bit} target={target}");
    }}
    for prior in 0..=255u16 { for shift in [0usize,1,2,4,6] {
        let normal = 0x55aa_33cc_f00f_0ff0u64;
        let weak = if (1..=4).contains(&shift) { !normal } else { 0 };
        let actual = coherent::bits_sources_for_test([prior as u8;64], &[(shift,normal,weak)]);
        for target in 0..64 {
            let add = (((normal >> target) & 1) << shift) + ((weak >> target) & 1);
            assert_eq!(actual[target], ((u64::from(prior)+add)%256) as u8);
        }
    }}
    // All carries can leave bit7: full physical multiplicity must wrap, not cap.
    let mut sources = vec![(4usize,1u64<<27,0);8];
    sources.extend([(6,1u64<<27,0);2]);
    assert_eq!(coherent::bits_sources_for_test([0;64],&sources)[27],0);
    let mut seed = 0x8c52_b731_e4a9_6d0fu64;
    let mut next = || { seed ^= seed << 13; seed ^= seed >> 7; seed ^= seed << 17; seed };
    for _ in 0..64 {
        let previous = std::array::from_fn(|_| next() as u8);
        let mut expected = previous;
        let mut sources = Vec::new();
        for _ in 0..32 {
            let shift = [1usize,2,4][(next()%3) as usize];
            let normal = next(); let weak = next() & !normal;
            sources.push((shift,normal,weak));
            for target in 0..64 {
                let add = (((normal>>target)&1)<<shift) + ((weak>>target)&1);
                expected[target] = ((u64::from(expected[target])+add)%256) as u8;
            }
        }
        assert_eq!(coherent::bits_sources_for_test(previous,&sources),expected);
    }
}

#[test]
fn experiment43_existing_leaper_masks_match_coordinate_destinations() {
    const LEAPS: [(i32,i32);8] = [(1,2),(1,-2),(-1,2),(-1,-2),(2,1),(2,-1),(-2,1),(-2,-1)];
    for source in 0..64 {
        let mut king = 0; let mut knight = 0;
        for (df,dr) in STEPS { if let Some(target)=at(source,df,dr) { king |= 1u64<<target; } }
        for (df,dr) in LEAPS { if let Some(target)=at(source,df,dr) { knight |= 1u64<<target; } }
        let square = Square(source as u8);
        assert_eq!(crate::attacks::influence_king_targets(square),king);
        assert_eq!(crate::attacks::influence_knight_targets(square),knight);
        for side in [Color::White,Color::Black] {
            let mut pawn = 0; let forward = if side==Color::White {1} else {-1};
            for df in [-1,1] { if let Some(target)=at(source,df,forward) { pawn |= 1u64<<target; } }
            assert_eq!(crate::attacks::influence_pawn_targets(side,square),pawn);
        }
    }
}

#[test]
fn experiment43_zero_one_and_promoted_slider_full_maps() {
    use Color::{White as W,Black as B};use PieceKind::*;
    let pieces = [("d3",W,Pawn),("f3",W,Pawn),("c3",W,Knight),("c5",W,Knight),
        ("d2",W,Knight),("d6",W,Knight),("f2",W,Knight),("f6",W,Knight),
        ("g3",W,Knight),("g5",W,Knight)];
    let zero = described(&pieces);
    assert!(zero.piece_squares(W,Bishop).is_empty() && zero.piece_squares(W,Rook).is_empty() && zero.piece_squares(W,Queen).is_empty());
    check(&zero);assert_eq!(Influence::build_coherent(&zero).code(W,sq("e4")),0);
    let mut one_pieces = pieces.to_vec();one_pieces.push(("a8",W,Bishop));
    let one = described(&one_pieces);
    assert_eq!(one.piece_squares(W,Bishop).len(),1);
    assert!(one.piece_squares(W,Rook).is_empty() && one.piece_squares(W,Queen).is_empty());
    check(&one);assert_eq!(Influence::build_coherent(&one).code(W,sq("e4")),16);
    // Three promoted-capable queens on one ray; their contributions stay separate.
    // Enemy king is transparent after the first friendly queen has weakened it.
    let queens = described(&[("a4",W,Queen),("c4",W,Queen),("e4",W,Queen),("g4",B,King)]);
    check(&queens);assert_eq!(Influence::build_coherent(&queens).code(W,sq("h4")),4);
    for original in [zero,one,queens] {
        let mut board = [Piece::EMPTY;64];
        for (i,piece) in original.board.into_iter().enumerate() {
            if !piece.is_empty() { board[i^56]=Piece::new(piece.color().opponent(),piece.kind()); }
        }
        let mirrored = placement(board);check(&mirrored);
        let before = Influence::build_coherent(&original);let after = Influence::build_coherent(&mirrored);
        for side in [W,B] { for target in 0..64 {
            assert_eq!(before.profiles[side.index()][target],after.profiles[side.opponent().index()][target^56]);
        }}
    }
}

#[test]
fn experiment43_public_and_supplied_maps_keep_their_original_authority() {
    use crate::evaluator::{Evaluator,Node,coherent_build_count};
    let position = Position::from_fen("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1").unwrap();
    let custom = Influence { profiles: std::array::from_fn(|color| std::array::from_fn(|target| (71*target+113*color+17) as u8)) };
    assert_ne!(custom.profiles,map_ref(&position));
    let before = coherent_build_count();
    let mut evaluator = Evaluator::<true>::new(&position);
    let mut scratch = Some(custom);
    assert_eq!(*evaluator.ensure_influence(&position,&mut scratch),custom);
    assert_eq!(*evaluator.ensure_influence_for_search(&position,&mut scratch,true),custom);
    assert_eq!(scratch,Some(custom));assert_eq!(coherent_build_count(),before);
    assert_eq!(evaluator.stats.influence_builds,0);
    let mut node = Node::root(position,&evaluator.root);let mut observed = None;
    let actual = evaluator.full_observed(&mut node,&custom,false,|parts| observed=Some(parts));
    let mut other = Evaluator::<true>::new(&position);let mut other_node = Node::root(position,&other.root);
    assert_eq!(actual,other.full(&mut other_node,&custom,false));
    assert!(observed.is_some());assert_eq!(node.retained,other_node.retained);
    assert_eq!(coherent_build_count(),before);assert_eq!(evaluator.stats.influence_builds,0);
    let mut empty = None;
    assert_eq!(evaluator.ensure_influence(&position,&mut empty).profiles,map_ref(&position));
    assert_eq!(coherent_build_count(),before);assert_eq!(evaluator.stats.influence_builds,1);
    let mut trusted_empty = None;
    assert_eq!(evaluator.ensure_influence_for_search(&position,&mut trusted_empty,true).profiles,map_ref(&position));
    assert_eq!(coherent_build_count(),before+1);assert_eq!(evaluator.stats.influence_builds,2);
    // A stale private plane at a newly transparent mailbox cell stays public-scalar.
    let base = described(&[("c1",Color::White,PieceKind::Bishop)]);let mut stale = base;
    stale.board[sq("d2").0 as usize]=Piece::new(Color::White,PieceKind::Queen);
    let mut scratch = None;
    assert_eq!(evaluator.ensure_influence(&stale,&mut scratch).profiles,map_ref(&stale));
    assert_eq!(coherent_build_count(),before+1);
}


// The oracle visits physical source coordinates, never the seed shifts/masks.
fn experiment58_coordinate_pawn_bytes(side: Color, pawns: u64) -> [u8; 64] {
    let mut expected = [0u8; 64];
    let forward = if side == Color::White { 1 } else { -1 };
    for source in 0..64 {
        if pawns & (1u64 << source) == 0 { continue; }
        for df in [-1, 1] {
            if let Some(target) = at(source, df, forward) {
                expected[target] = expected[target].wrapping_add(64);
            }
        }
    }
    expected
}

#[test]
fn experiment58_fresh_pawn_seed_coordinate_singles_pairs_and_many_masks() {
    for side in [Color::White, Color::Black] {
        let verify = |pawns| {
            let expected = experiment58_coordinate_pawn_bytes(side, pawns);
            let (planes, bytes) = coherent::pawn_seed_for_test(side, pawns);
            assert_eq!(bytes, expected, "side={side:?} pawns={pawns:016x}");
            assert_eq!(&planes[..6], &[0; 6]);
            for target in 0..64 {
                assert_eq!((planes[6] >> target) & 1, u64::from((expected[target] >> 6) & 1));
                assert_eq!((planes[7] >> target) & 1, u64::from((expected[target] >> 7) & 1));
            }
        };
        verify(0);
        for first in 0..64 {
            verify(1u64 << first);
            for second in first + 1..64 { verify((1u64 << first) | (1u64 << second)); }
        }
        // Pure counter inputs, not claims that all these masks are admitted Positions.
        for pawns in [u64::MAX, 0xff, 0xff00_0000_0000_0000,
            0x8181_8181_8181_8181, 0x00ff_ff00_00ff_ff00, 0x55aa_55aa_55aa_55aa] {
            verify(pawns);
        }
        let mut seed = 0xa718_d3c6_95e2_40bfu64;
        for _ in 0..64 {
            seed ^= seed << 13; seed ^= seed >> 7; seed ^= seed << 17;
            verify(seed);
        }
    }
}

#[test]
fn experiment58_complete_maps_pawn_seed_wrap_weak_edges_and_no_sliders() {
    use Color::{White as W, Black as B}; use PieceKind::*;
    let pieces = [("c3",W,Pawn),("e3",W,Pawn),
        ("b3",W,Knight),("b5",W,Knight),("c2",W,Knight),("c6",W,Knight),
        ("e2",W,Knight),("e6",W,Knight),("f3",W,Knight),("f5",W,Knight)];
    let zero = described(&pieces);
    assert!(zero.piece_squares(W,Bishop).is_empty() && zero.piece_squares(W,Rook).is_empty() && zero.piece_squares(W,Queen).is_empty());
    check(&zero); assert_eq!(Influence::build_coherent(&zero).code(W,sq("d4")),0);
    let mut with_slider = pieces.to_vec(); with_slider.push(("a8",W,Bishop));
    let one = described(&with_slider);
    check(&one); assert_eq!(Influence::build_coherent(&one).code(W,sq("d4")),0);
    let no_pawns = described(&[("a4",W,Queen),("c4",W,Queen),("e4",W,Queen),("g4",B,King)]);
    assert!(no_pawns.piece_squares(W,Pawn).is_empty());
    check(&no_pawns); assert_eq!(Influence::build_coherent(&no_pawns).code(W,sq("h4")),4);
    let weak_and_extra = described(&[("d4",W,Bishop),("c5",W,Pawn),("b6",B,Knight),
        ("e3",W,Queen),("f2",W,Queen),("g1",B,King),("h2",B,Pawn)]);
    let edges = described(&[("a8",W,Pawn),("h8",W,Pawn),("a1",W,Pawn),("h1",W,Pawn),
        ("a2",W,Pawn),("h2",W,Pawn),("b7",W,Pawn),("g7",W,Pawn),("d4",W,Rook)]);
    for position in [zero,one,no_pawns,weak_and_extra,edges] {
        check(&position);
        let before = Influence::build_coherent(&position);
        let mut board = [Piece::EMPTY;64];
        for (i,piece) in position.board.into_iter().enumerate() {
            if !piece.is_empty() { board[i^56] = Piece::new(piece.color().opponent(),piece.kind()); }
        }
        let mirrored = placement(board); check(&mirrored);
        let after = Influence::build_coherent(&mirrored);
        for side in [W,B] { for target in 0..64 {
            assert_eq!(before.profiles[side.index()][target],after.profiles[side.opponent().index()][target^56]);
        }}
        let mut chronology = position;
        for side in 0..2 { let mut begin=0; for count in chronology.counts[side] {
            let end=begin+usize::from(count); chronology.squares[side][begin..end].reverse(); begin=end;
        }}
        check(&chronology); assert_eq!(Influence::build_coherent(&chronology),before);
    }
}

#[test]
fn experiment58_pawn_seed_public_scalar_and_supplied_map_authority() {
    use crate::evaluator::{Evaluator,coherent_build_count};
    let position = Position::from_fen("4k3/8/8/3p4/2P5/8/8/2B1K3 w - - 0 1").unwrap();
    check(&position);
    let custom = Influence { profiles: std::array::from_fn(|color| std::array::from_fn(|target| (29*target+97*color+11) as u8)) };
    assert_ne!(custom,Influence::build(&position));
    let mut evaluator = Evaluator::<true>::new(&position);
    let before = coherent_build_count(); let mut supplied = Some(custom);
    assert_eq!(*evaluator.ensure_influence(&position,&mut supplied),custom);
    assert_eq!(*evaluator.ensure_influence_for_search(&position,&mut supplied,true),custom);
    assert_eq!(supplied,Some(custom)); assert_eq!(coherent_build_count(),before);
    assert_eq!(evaluator.stats.influence_builds,0);
    let mut fresh = None;
    assert_eq!(evaluator.ensure_influence_for_search(&position,&mut fresh,true).profiles,map_ref(&position));
    assert_eq!(coherent_build_count(),before+1); assert_eq!(evaluator.stats.influence_builds,1);
    let mut stale = position;
    stale.board[sq("d2").0 as usize] = Piece::new(Color::White,PieceKind::Pawn);
    assert_eq!(stale.attack_view(),position.attack_view());
    assert_ne!(Influence::build(&stale),Influence::build(&position));
    assert_eq!(Influence::build(&stale).profiles,map_ref(&stale));
    let mut public = None;
    assert_eq!(evaluator.ensure_influence(&stale,&mut public).profiles,map_ref(&stale));
    assert_eq!(coherent_build_count(),before+1); assert_eq!(evaluator.stats.influence_builds,2);
    // Coherent producer is deliberately never called on the stale private planes.
}
