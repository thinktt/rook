#[cfg(test)]
mod weighted_bound_tests {
    use super::*;
    #[test]
    fn bound_incoherent_public_session_root_keeps_old_false_node_limit_admission() {
        let mut invalid = Session::<true>::default();
        invalid.parameters.values[27] = 1;
        invalid.parameters.values[24] = 0;
        invalid.parameters.values[29] = 65536;
        invalid.states.last_mut().unwrap().starting_units ^= 1;
        assert!(invalid.position().validate().is_err());
        assert!(matches!(invalid.go(0, Limits { nodes: Some(0) }, 6),
            Err(Error::Search(ordinary::Error::Stopped(crate::quiescence::Stopped::NodeLimit(0))))));
        let search = invalid.search.as_ref().unwrap();
        assert_eq!(search.evaluator.bound_test_events(), Default::default());
        assert!(!search.evaluator.bound_test_allocated());
        assert!(search.timing.is_none());
        assert_eq!(invalid.game_ply(), 0);
        assert!(invalid.position().validate().is_err());
    }
}
