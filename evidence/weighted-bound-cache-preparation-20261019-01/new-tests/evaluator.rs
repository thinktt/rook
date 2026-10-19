#[cfg(test)]
mod weighted_bound_tests {
    use super::*;
    const START: &str = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1";

    #[test]
    fn bound_storage_is_lazy_thin_exact_key_collision_and_clear() {
        assert_eq!(std::mem::size_of::<BoundComponents>(), 24);
        assert_eq!(std::mem::size_of::<BoundEntry>(), 64);
        assert_eq!(std::mem::align_of::<BoundEntry>(), 64);
        assert_eq!(std::mem::size_of::<Option<Box<[BoundEntry; 1024]>>>(),
            std::mem::size_of::<usize>());
        let start = Position::from_fen(START).unwrap();
        let mut evaluator = Evaluator::<true>::new(&start);
        assert!(!evaluator.bound_test_allocated());
        evaluator.begin_search(&start);
        assert!(!evaluator.bound_test_allocated());
        evaluator.prepare_bound_cache();
        let entries = evaluator.bound.as_ref().unwrap();
        assert_eq!(entries.as_ptr() as usize % 64, 0);
        assert_eq!((&entries[1] as *const BoundEntry as usize)
            - (&entries[0] as *const BoundEntry as usize), 64);
        // Pigeonhole over >1024 distinct coherent boards; no forged fingerprints.
        let mut seen = vec![None; 1024];
        let mut collision = None;
        'outer: for a in 1..63 {
            for b in a + 1..63 {
                let mut fen = String::new();
                for rank in (0..8).rev() {
                    let mut empty = 0;
                    for file in 0..8 {
                        let square = rank * 8 + file;
                        let tag = if square == 0 { Some('K') }
                            else if square == 63 { Some('k') }
                            else if square == a || square == b { Some('N') } else { None };
                        if let Some(tag) = tag {
                            if empty != 0 { fen.push(char::from(b'0' + empty)); empty = 0; }
                            fen.push(tag);
                        } else { empty += 1; }
                    }
                    if empty != 0 { fen.push(char::from(b'0' + empty)); }
                    if rank != 0 { fen.push('/'); }
                }
                fen.push_str(" w - - 0 1");
                let position = Position::from_fen(&fen).unwrap();
                let slot = Evaluator::<true>::bound_index(&position);
                if let Some(first) = seen[slot] {
                    collision = Some((first, position)); break 'outer;
                }
                seen[slot] = Some(position);
            }
        }
        let (a, b) = collision.expect("real1024-slot collision");
        assert_ne!(a.attack_view(), b.attack_view());
        let x = BoundComponents { pieces: [3, 5], activity: 7, shelter: 11, relation_queries: 13 };
        let y = BoundComponents { relation_queries: 17, ..x };
        evaluator.bound_insert(&a, x);
        assert_eq!(evaluator.bound_get(&a), Some(x));
        assert_eq!(evaluator.bound_get(&b), None);
        evaluator.bound_insert(&b, y);
        assert_eq!(evaluator.bound_get(&a), None);
        assert_eq!(evaluator.bound_get(&b), Some(y));
        evaluator.prepare_bound_cache();
        assert!(evaluator.bound.as_ref().unwrap().iter().all(|e| *e == BoundEntry::EMPTY));
    }

    #[test]
    fn bound_hits_preserve_live_tempo_retained_pawn_effects_and_nonzero_relation_work() {
        let position = Position::from_fen(START).unwrap();
        let mut cached = Evaluator::<true>::new(&position);
        let mut plain = Evaluator::<true>::new(&position);
        for evaluator in [&mut cached, &mut plain] {
            evaluator.parameters.own[7] = 271;
            evaluator.parameters.opponent[7] = 43;
            evaluator.parameters.own[8] = 377;
            evaluator.begin_search(&position);
        }
        cached.prepare_bound_cache();
        let map = Influence::build(&position);
        let mut a = Node::root(position, &cached.root);
        let mut b = Node::root(position, &plain.root);
        assert_eq!(cached.full_bound::<true>(&mut a, &map, false), plain.full(&mut b, &map, false));
        assert!(cached.bound_get(&position).unwrap().relation_queries > 0);
        let mut changed = position;
        for side in 0..2 {
            changed.squares[side][..8].reverse();
            changed.squares[side][8..10].reverse();
            changed.squares[side][10..12].reverse();
            changed.squares[side][12..14].reverse();
        }
        changed.side = Color::Black;
        changed.rights = 0;
        changed.ep = 20;
        changed.halfmove = 83;
        changed.validate().unwrap();
        assert_eq!(changed.attack_view(), position.attack_view());
        assert_eq!(Influence::build(&changed), map);
        for checked in [false, true] {
            let before = cached.bound_test_events();
            a = Node::root(changed, &cached.root);
            b = Node::root(changed, &plain.root);
            a.retained.age = 19; b.retained.age = 19;
            a.retained.positional = -371; b.retained.positional = -371;
            let mut left = None;
            let mut right = None;
            // Private test observation only: no production observed entry gets permission.
            let x = cached.full_impl::<false, true, _, _>(&mut a, &map, checked,
                |components| left = Some(components), |_| {});
            let y = plain.full_observed(&mut b, &map, checked,
                |components| right = Some(components));
            assert_eq!((x, left), (y, right));
            assert_eq!((a, cached.stats), (b, plain.stats));
            assert_eq!(cached.bound_test_events().hits, before.hits + 1);
        }
        // A real PawnCache collision must still replace on a pure hit.
        let first = Position::from_fen("7k/8/8/8/6P1/3P4/8/K7 w - - 0 1").unwrap();
        let other = Position::from_fen("7k/8/6P1/8/8/3P4/8/K7 w - - 0 1").unwrap();
        assert_eq!(first.pawn % 128, other.pawn % 128);
        assert_ne!(first.pawn, other.pawn);
        for (i, position) in [first, other, first].into_iter().enumerate() {
            let map = Influence::build(&position);
            let mut a = Node::root(position, &cached.root);
            let mut b = Node::root(position, &plain.root);
            let before = cached.stats;
            let hits = cached.bound_test_events().hits;
            let actual = if i == 1 { cached.full(&mut a, &map, false) }
                else { cached.full_bound::<true>(&mut a, &map, false) };
            assert_eq!(actual, plain.full(&mut b, &map, false));
            assert_eq!((a, cached.stats), (b, plain.stats));
            if i == 2 {
                assert_eq!(cached.bound_test_events().hits, hits + 1);
                assert_eq!(cached.stats.pawn_replacements, before.pawn_replacements + 1);
            }
        }
    }

    #[test]
    fn bound_native_rook_cycle_and_ep_nulls_hit_without_freezing_live_state() {
        fn legal(position: &Position, text: &str) -> Move {
            let mut list = crate::movegen::MoveList::new();
            crate::movegen::generate_legal(position, &mut list);
            *list.as_slice().iter().find(|m| m.to_string() == text).unwrap()
        }
        let start = Position::from_fen("7k/8/8/8/8/8/8/R1R4K w - - 0 1").unwrap();
        let mut cached = Evaluator::<true>::new(&start);
        let mut plain = Evaluator::<true>::new(&start);
        cached.prepare_bound_cache();
        let mut a = Node::root(start, &cached.root);
        let mut b = Node::root(start, &plain.root);
        let map = Influence::build(&start);
        assert_eq!(cached.full_bound::<true>(&mut a, &map, false), plain.full(&mut b, &map, false));
        for text in ["a1a2", "h8g8", "c1a1", "g8h8", "a2c2", "h8g8", "c2c1", "g8h8"] {
            let movement = legal(&a.position, text);
            a = a.child(&cached.root, movement);
            b = b.child(&plain.root, movement);
            a.position.validate().unwrap();
        }
        assert_eq!(a.position.board, start.board);
        assert_eq!(a.position.side, start.side);
        assert_ne!(a.position.squares, start.squares);
        assert_eq!(Influence::build(&a.position), map);
        let hits = cached.bound_test_events().hits;
        assert_eq!(cached.full_bound::<true>(&mut a, &map, false), plain.full(&mut b, &map, false));
        assert_eq!((a, cached.stats), (b, plain.stats));
        assert_eq!(cached.bound_test_events().hits, hits + 1);

        let start = Position::from_fen("7k/8/8/8/3p4/8/4P3/7K w - - 0 1").unwrap();
        let mut cached = Evaluator::<true>::new(&start);
        let mut plain = Evaluator::<true>::new(&start);
        cached.prepare_bound_cache();
        let movement = legal(&start, "e2e4");
        let mut a = Node::root(start, &cached.root).child(&cached.root, movement);
        let mut b = Node::root(start, &plain.root).child(&plain.root, movement);
        assert_ne!(a.position.ep, crate::types::NO_SQUARE);
        let original = a.position;
        let map = Influence::build(&original);
        assert_eq!(cached.full_bound::<true>(&mut a, &map, false), plain.full(&mut b, &map, false));
        for _ in 0..2 {
            a = a.null_child(); b = b.null_child();
            assert_eq!(Influence::build(&a.position), map);
            let hits = cached.bound_test_events().hits;
            assert_eq!(cached.full_bound::<true>(&mut a, &map, false), plain.full(&mut b, &map, false));
            assert_eq!((a, cached.stats), (b, plain.stats));
            assert_eq!(cached.bound_test_events().hits, hits + 1);
        }
        assert_eq!(a.position.board, original.board);
        assert_eq!(a.position.side, original.side);
        assert_eq!(a.position.ep, crate::types::NO_SQUARE);
    }

    fn public_call(which: usize, evaluator: &mut Evaluator, node: &mut Node,
        map: &Influence) -> Evaluation
    {
        match which {
            0 => evaluator.full(node, map, false),
            1 => evaluator.full_observed(node, map, false, |_| {}),
            2 => evaluator.fresh_observed(node, map, false, |_| {}),
            3 => evaluator.full_detailed_observed(node, map, false, |_| {}),
            4 => evaluator.fresh_detailed_observed(node, map, false, |_| {}),
            5 => evaluator.select_noncheck(node, -10000, 10000, true, &mut Some(*map)).evaluation,
            6 => evaluator.select_noncheck_detailed_observed(node, -10000, 10000, true,
                &mut Some(*map), |_| {}, |_| {}).evaluation,
            7 => evaluator.select_noncheck_stages_observed(node, -10000, 10000, true,
                &mut Some(*map), |_| {}).evaluation,
            _ => unreachable!(),
        }
    }
    #[test]
    fn bound_public_custom_maps_and_public_root_rebind_never_lookup_or_populate() {
        let position = Position::from_fen(START).unwrap();
        let other = Position::from_fen("7k/8/8/8/8/8/P7/K7 b - - 0 1").unwrap();
        let custom = Influence { profiles: [[255; 64]; 2] };
        for which in 0..8 {
            for poisoned in [false, true] {
                for mutation in 0..3 {
                    let mut cached = Evaluator::<true>::new(&position);
                    let mut plain = Evaluator::<true>::new(&position);
                    if mutation == 1 {
                        cached.root = RootContext::neutral(&other);
                        plain.root = cached.root.clone();
                    } else if mutation == 2 {
                        for evaluator in [&mut cached, &mut plain] {
                            evaluator.parameters.own[7] = 271;
                            evaluator.parameters.opponent[8] = 17;
                            evaluator.begin_search(&other);
                        }
                    }
                    cached.prepare_bound_cache();
                    if poisoned {
                        cached.bound_insert(&position, BoundComponents { pieces: [-17, 29],
                            activity: -733, shelter: 997, relation_queries: 99999 });
                    }
                    let before = cached.bound.as_ref().unwrap().to_vec();
                    let events = cached.bound_test_events();
                    let mut a = Node::root(position, &cached.root);
                    let mut b = Node::root(position, &plain.root);
                    assert_eq!(public_call(which, &mut cached, &mut a, &custom),
                        public_call(which, &mut plain, &mut b, &custom));
                    assert_eq!((a, cached.stats), (b, plain.stats));
                    assert_eq!(cached.bound_test_events(), events);
                    assert_eq!(&cached.bound.as_ref().unwrap()[..], before.as_slice());
                    assert!(!plain.bound_test_allocated());
                }
            }
        }
    }
}
