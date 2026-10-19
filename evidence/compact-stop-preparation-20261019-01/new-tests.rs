    #[test]
    fn compact_stop_public_stop_recovers_configured_budget_even_when_counter_is_already_over() {
        // The shared non-Search helper must retain its arbitrary-counter domain.
        let mut units = 5;
        assert_eq!(crate::work_clock::charge_search_unit(&mut units, Some(3)),
            Err(Stopped::NodeLimit(3)));
        assert_eq!(units, 5);

        fn check<const D: bool>() {
            let (mut search, mut node, mut history, entry) =
                selected::<D>("7k/8/8/8/8/8/8/K6R w - - 0 1", "h1h7");
            search.begin_sequence(Limits { nodes: Some(3) });
            // Internal callers can admit this state even though normal charging
            // reaches the first refusal at exactly the configured limit.
            search.stats.nodes = 5;
            for _ in 0..2 {
                let stop = search.continue_subtree(&mut node, &mut history, entry).err();
                assert_eq!(stop, Some(Stopped::NodeLimit(3)));
                assert_eq!(format!("{:?}", stop), "Some(NodeLimit(3))");
                assert_eq!(search.work().charged_search_units, 5);
                assert_eq!(history.search_ply(), entry.ply);
            }
            assert_eq!(search.charge_node(&history), Err(Stopped::NodeLimit(3)));
        }
        check::<true>();
        check::<false>();
    }

    #[test]
    fn compact_stop_timed_poll_io_kind_survives_compact_recursion_and_unwinds() {
        struct FailingPoll {
            kind: std::io::ErrorKind,
            calls: usize,
        }
        impl crate::host::Host for FailingPoll {
            fn command(&mut self) -> std::io::Result<Option<crate::host::Command>> {
                self.calls += 1;
                Err(std::io::Error::from(self.kind))
            }
        }
        fn check<const D: bool>(kind: std::io::ErrorKind) {
            let position = Position::from_fen(
                "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1").unwrap();
            let (mut search, _) = Quiescence::<D>::new(&position)
                .map_host(FailingPoll { kind, calls: 0 });
            search.config.tts_bytes = 65536;
            let mut history = SearchHistory::new(&position);
            let controls = crate::timed::Controls {
                average_cs: 1_000_000, maximum_cs: 1_000_000, origin: 0,
                seed: 0, randomness: 0, maximum_entered_iterations: 6,
            };
            match search.run_work_timed(position, &mut history, controls,
                Limits { nodes: Some(8192) }) {
                Err(crate::ordinary::Error::Stopped(stop)) =>
                    assert_eq!(stop, Stopped::HostIo(kind)),
                _ => panic!("the first credited poll must return its host error"),
            }
            assert_eq!(search.host.calls, 1);
            assert_eq!(search.work().charged_search_units, 4096);
            assert_eq!(history.search_ply(), 0);
            assert!(search.timing.is_none());
        }
        for kind in [std::io::ErrorKind::PermissionDenied, std::io::ErrorKind::ConnectionReset] {
            check::<true>(kind);
            check::<false>(kind);
        }
    }

