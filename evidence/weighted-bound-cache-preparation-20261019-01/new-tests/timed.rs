#[cfg(test)]
mod weighted_bound_tests {
    use super::*;
    const START: &str = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1";
    fn controls() -> Controls {
        Controls { average_cs: 0, maximum_cs: 1, origin: 0xfffffff0,
            seed: 0, randomness: 50, maximum_entered_iterations: 6 }
    }

    #[test]
    fn bound_actual_timed_poll_matches_public_uncached_records_work_and_history() {
        let position = Position::from_fen(START).unwrap();
        let mut cached = Search::<true>::new(&position);
        let mut plain = Search::<true>::new(&position);
        cached.config.tts_bytes = 65536; plain.config.tts_bytes = 65536;
        let mut a = SearchHistory::new(&position);
        let mut b = SearchHistory::new(&position);
        let x = cached.run_session_timed(position, &mut a, controls(), Limits::default()).unwrap();
        let y = plain.run_work_timed(position, &mut b, controls(), Limits::default()).unwrap();
        assert_eq!((a.search_ply(), b.search_ply()), (0, 0));
        assert!(cached.timing.is_none() && plain.timing.is_none());
        assert_eq!(x.stop.point, Point::Poll);
        assert!(x.stop.pending.is_some() && x.result.is_some());
        assert_eq!((&x.result, &x.stop, &x.publications, x.ledger),
            (&y.result, &y.stop, &y.publications, y.ledger));
        assert_eq!((&x.initial_candidates, &x.iterations, &x.checks, x.seed),
            (&y.initial_candidates, &y.iterations, &y.checks, y.seed));
        assert_eq!((x.stats, x.evaluations), (y.stats, y.evaluations));
        assert!(x.evaluations.relation_queries > 0);
        assert_eq!(crate::output::completed_events(position, &x,
            cached.evaluator.draw_preference, cached.config.selectivity, true).unwrap(),
            crate::output::completed_events(position, &y,
            plain.evaluator.draw_preference, plain.config.selectivity, true).unwrap());
        let events = cached.evaluator.bound_test_events();
        assert_eq!(events.epochs, 1);
        assert!(events.lookups > 1 && events.stores > 1);
        assert_eq!(plain.evaluator.bound_test_events(), Default::default());
        assert!(!plain.evaluator.bound_test_allocated());
    }

    #[test]
    fn bound_a_b_a_root_rebindings_clear_before_first_full_and_node_limit_unwinds() {
        let first = Position::from_fen(START).unwrap();
        let other = Position::from_fen("7k/8/8/8/8/8/P7/K7 b - - 0 1").unwrap();
        let mut cached = Search::<true>::new(&first);
        let mut plain = Search::<true>::new(&first);
        cached.config.tts_bytes = 65536; plain.config.tts_bytes = 65536;
        for (index, position) in [first, other, first].into_iter().enumerate() {
            for search in [&mut cached, &mut plain] {
                search.evaluator.parameters.own[7] = 111 + index as i32 * 73;
                search.evaluator.parameters.opponent[8] = 307 - index as i32 * 19;
            }
            let before = cached.evaluator.bound_test_events();
            let mut a = SearchHistory::new(&position);
            let mut b = SearchHistory::new(&position);
            assert!(matches!(cached.run_session_timed(position, &mut a, controls(), Limits { nodes: Some(0) }),
                Err(Error::Stopped(Stopped::NodeLimit(0)))));
            assert!(matches!(plain.run_work_timed(position, &mut b, controls(), Limits { nodes: Some(0) }),
                Err(Error::Stopped(Stopped::NodeLimit(0)))));
            let after = cached.evaluator.bound_test_events();
            assert_eq!((after.epochs, after.lookups, after.stores, after.hits),
                (before.epochs + 1, before.lookups + 1, before.stores + 1, before.hits));
            assert_eq!((cached.work(), cached.evaluator.stats), (plain.work(), plain.evaluator.stats));
            assert_eq!((a.search_ply(), b.search_ply()), (0, 0));
            assert!(cached.timing.is_none() && plain.timing.is_none());
        }
        assert_eq!(plain.evaluator.bound_test_events(), Default::default());
        assert!(!plain.evaluator.bound_test_allocated());
    }

    #[test]
    fn bound_host_seed_and_start_errors_leave_false_routes_inert_and_next_true_rebinds() {
        struct Fails(u8);
        impl crate::host::Host for Fails {
            fn acquire_seed(&mut self, supplied: u32, _: u32) -> std::io::Result<u32> {
                if self.0 == 0 { Err(std::io::ErrorKind::Other.into()) } else { Ok(supplied) }
            }
            fn started(&mut self, _: u32) -> std::io::Result<()> {
                Err(std::io::ErrorKind::Other.into())
            }
        }
        let position = Position::from_fen(START).unwrap();
        for point in [0, 1] {
            let mut search = Search::<true>::new(&position);
            search.config.tts_bytes = 65536;
            let (mut search, _) = search.map_host(Fails(point));
            let mut history = SearchHistory::new(&position);
            assert!(matches!(search.run_session_timed(position, &mut history, controls(), Limits::default()),
                Err(Error::Host(_))));
            assert!(search.timing.is_none());
            assert_eq!(history.search_ply(), 0);
            let before = search.evaluator.bound_test_events();
            assert_eq!((before.epochs, before.lookups, before.stores, before.hits), (1, 1, 1, 0));
            let (mut search, _) = search.map_host(crate::host::NoHost);
            assert!(matches!(search.run_work_timed(position, &mut history, controls(), Limits { nodes: Some(0) }),
                Err(Error::Stopped(Stopped::NodeLimit(0)))));
            assert_eq!(search.evaluator.bound_test_events(), before);
            assert!(matches!(search.run_session_timed(position, &mut history, controls(), Limits { nodes: Some(0) }),
                Err(Error::Stopped(Stopped::NodeLimit(0)))));
            let after = search.evaluator.bound_test_events();
            assert_eq!((after.epochs, after.lookups, after.stores, after.hits), (2, 2, 2, 0));
            assert_eq!(history.search_ply(), 0);
            assert!(search.timing.is_none());
        }
    }
}
