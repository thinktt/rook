

#[cfg(test)]
mod retained_search_tests {
    use super::*;

    const START: &str = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR";
    const TIED: &str = "8/P1P5/8/8/3K3k/8/p7/8";

    fn ordered(placement: &str, side: &str, white: &[&str], black: &[&str]) -> Value {
        json!({"placement":placement,"sideToMove":side,"pawnOrder":{"white":white,"black":black}})
    }

    fn retained(mut position: Value, clear: bool) -> Value {
        position["clear"] = json!(clear);
        position["phase"] = json!({"opening":0,"middlegame":128,"endgame":128});
        position["materialScore"] = json!(17);
        position["weights"] = json!({"white":{"structure":799,"progress":1873},
            "black":{"structure":1321,"progress":613}});
        position
    }

    fn search(positions: Vec<Value>, side: &str) -> Value {
        let owner = |offset| Value::Object(scores::NAMES.iter().enumerate()
            .map(|(index, name)| (name.to_string(), json!(100 + index + offset))).collect());
        json!({"rootSide":side,"averageDepth":7,
            "percentages":{"own":owner(0),"opponent":owner(7)},"positions":positions})
    }

    fn run_retained(steps: Vec<Value>) -> Value {
        dispatch("evaluation.retainedPawnSubtotal", &json!({"steps":steps})).unwrap()["results"].clone()
    }

    fn run_search(input: &Value) -> Value {
        dispatch("evaluation.searchPawnSequence", input).unwrap()["results"].clone()
    }

    #[test]
    fn retained_order_survives_reuse_until_clear_and_next_request_starts_empty() {
        let a = retained(ordered(TIED, "white", &["a7", "c7"], &["a2"]), false);
        let b = retained(ordered(TIED, "white", &["c7", "a7"], &["a2"]), false);
        let mut cleared = b.clone();
        cleared["clear"] = json!(true);
        let out = run_retained(vec![a.clone(), b.clone(), cleared, a]);
        assert_eq!(out[0]["reused"], false);
        assert_eq!(out[1]["reused"], true);
        assert_eq!(out[1]["pawn"]["candidates"]["white"], json!(["a7", "c7"]));
        assert_eq!(out[1]["pawn"]["endingScore"], 400);
        assert_eq!(out[2]["reused"], false);
        assert_eq!(out[2]["pawn"]["endingScore"], 100);
        assert_eq!(out[3]["pawn"]["candidates"]["white"], json!(["c7", "a7"]));
        assert_eq!(out[3]["pawn"]["endingScore"], 100);
        let isolated = run_retained(vec![b]);
        assert_eq!(isolated[0]["reused"], false);
        assert_eq!(isolated[0]["pawn"], out[2]["pawn"]);
    }

    #[test]
    fn full_collision_keeps_base_piece_geometry_but_filters_current_candidates() {
        // Released collision-pieces-0-N-16: distinct arrangements have the same
        // full pawn identity. The fresh-current terms distinguish a rebuild.
        let a = retained(ordered("7k/6P1/Np1pPn2/4pP2/8/2p5/4P3/K7", "white",
            &["g7", "e6", "f5", "e2"], &["b6", "d6", "e5", "c3"]), true);
        let b = retained(ordered("7k/8/N1p2n1P/2p5/7P/1p6/p5PP/K7", "white",
            &["h2", "g2", "h4", "h6"], &["a2", "b3", "c5", "c6"]), false);
        let mut fresh_b = b.clone(); fresh_b["clear"] = json!(true);
        let out = run_retained(vec![a, b.clone(), fresh_b]);
        assert_eq!(out[0]["identity"]["pawn"], out[1]["identity"]["pawn"]);
        assert_ne!(out[0]["identity"]["secondary"], out[1]["identity"]["secondary"]);
        assert_eq!(out[1]["reused"], true);
        assert_eq!(out[1]["pawn"]["terms"]["white"]["structureScore"], -19);
        assert_eq!(out[1]["pawn"]["terms"]["black"]["pieceTerm"], 1);
        assert_eq!(out[1]["pawn"]["candidates"], json!({"white":[],"black":[]}));
        assert_eq!(out[2]["pawn"]["terms"]["white"]["structureScore"], -28);
        assert_eq!(out[2]["pawn"]["terms"]["black"]["pieceTerm"], 0);
        let isolated = run_retained(vec![b]);
        assert_eq!(isolated[0]["pawn"], out[2]["pawn"]);
    }

    #[test]
    fn repeated_hits_recompute_phase_selected_piece_work_even_with_zero_weights() {
        let mut gated = retained(ordered("1r5q/8/8/3R4/8/8/P6P/K6k", "white",
            &["a2", "h2"], &[]), false);
        gated["phase"] = json!({"opening":0,"middlegame":16,"endgame":240});
        gated["weights"] = json!({"white":{"structure":0,"progress":0},"black":{"structure":0,"progress":0}});
        let mut active = gated.clone();
        active["phase"] = json!({"opening":17,"middlegame":0,"endgame":239});
        let out = run_retained(vec![gated.clone(), active.clone(), active, gated]);
        assert_eq!(out[0]["pawn"]["relationQueries"], 0);
        assert_eq!(out[1]["reused"], true);
        assert_eq!(out[1]["pawn"]["terms"]["white"]["pieceTerm"], 1);
        assert_eq!(out[1]["pawn"]["relationQueries"], 1);
        assert_eq!(out[2]["pawn"]["relationQueries"], 1);
        assert_eq!(out[1]["pawn"], out[2]["pawn"]);
        assert_eq!(out[3]["pawn"]["relationQueries"], 0);
        assert_eq!(out[3]["pawn"]["terms"]["white"]["pieceTerm"], 0);
    }

    #[test]
    fn search_root_context_stays_fixed_across_current_side_phase_and_count_changes() {
        for side in ["white", "black"] {
            let root = ordered(START, side, &["a2","b2","c2","d2","e2","f2","g2","h2"],
                &["a7","b7","c7","d7","e7","f7","g7","h7"]);
            let a = ordered("7k/8/8/8/8/8/P7/K7", "white", &["a2"], &[]);
            let b = ordered("7k/8/8/8/8/8/P7/K7", "black", &["a2"], &[]);
            let mut input = search(vec![root.clone(), a.clone(), b.clone()], side);
            input["averageDepth"] = json!(-100);
            for owner in ["own", "opponent"] {
                for name in scores::NAMES { input["percentages"][owner][name] = json!(1000); }
            }
            // Ownership is asymmetric, and produced coefficients reach 10240.
            input["percentages"]["opponent"]["pawnStructure"] = json!(0);
            let out = run_search(&input);
            for (index, current) in [root, a, b].iter().enumerate() {
                let query = json!({"rootPlacement":START,"placement":current["placement"],
                    "rootSide":side,"sideToMove":current["sideToMove"],"averageDepth":-100,
                    "percentages":input["percentages"],"pawnOrder":current["pawnOrder"]});
                let expected = dispatch("evaluation.contextPawnSubtotal", &json!({"queries":[query]})).unwrap();
                for field in ["rootPhase", "currentPhase", "materialScore", "pawn", "central"] {
                    assert_eq!(out[index][field], expected["results"][0][field], "{side}/{index}/{field}");
                }
            }
            assert_eq!(out[1]["rootPhase"], json!({"opening":256,"middlegame":0,"endgame":0}));
            assert_eq!(out[1]["currentPhase"], json!({"opening":0,"middlegame":0,"endgame":256}));
            assert_eq!(out[1]["materialScore"], out[2]["materialScore"]);
            assert_eq!(out[2]["reused"], true);
        }
    }

    #[test]
    fn search_collision_retains_structure_but_uses_current_piece_positions_and_fresh_request_state() {
        let a = ordered("1q5k/6P1/Np1pPn2/4pP2/8/2p5/4P3/KQ6", "white",
            &["g7","e6","f5","e2"], &["b6","d6","e5","c3"]);
        let b = ordered("1q5k/8/N1p2n1P/2p5/7P/1p6/p5PP/KQ6", "white",
            &["h2","g2","h4","h6"], &["a2","b3","c5","c6"]);
        let input = search(vec![a.clone(), b.clone(), b.clone(), a], "white");
        let out = run_search(&input);
        assert_eq!(out[0]["reused"], false);
        assert_eq!(out[1]["reused"], true);
        assert_eq!(out[1]["identity"]["pawn"], out[0]["identity"]["pawn"]);
        assert_eq!(out[0]["pawn"]["terms"]["black"]["pieceTerm"], 1);
        assert_eq!(out[1]["pawn"]["terms"]["black"]["pieceTerm"], 0);
        assert_eq!(out[1]["pawn"]["terms"]["white"]["structureScore"], -19);
        assert_eq!(out[1]["pawn"]["candidates"], json!({"white":[],"black":[]}));
        assert_eq!(out[1], out[2]);
        assert_eq!(run_search(&input), out);
        let isolated = run_search(&search(vec![b], "white"));
        assert_eq!(isolated[0]["reused"], false);
        assert_ne!(isolated[0]["pawn"]["terms"], out[1]["pawn"]["terms"]);
    }

    #[test]
    fn pawnless_zero_identity_is_reused_against_cleared_state_in_each_operation() {
        let position = ordered("7k/8/8/8/8/8/8/K7", "black", &[], &[]);
        let a = run_retained(vec![retained(position.clone(), true)]);
        let b = run_search(&search(vec![position], "black"));
        for result in [&a[0], &b[0]] {
            assert_eq!(result["identity"]["pawn"], 0);
            assert_eq!(result["reused"], true);
            assert_eq!(result["pawn"]["terms"], json!({"white":{"structureScore":0,"pieceTerm":0},"black":{"structureScore":0,"pieceTerm":0}}));
            assert_eq!(result["pawn"]["candidates"], json!({"white":[],"black":[]}));
            assert_eq!(result["pawn"]["relationQueries"], 0);
        }
    }

    #[test]
    fn retained_whole_schema_and_late_ignored_context_fields_validate_before_state() {
        let good = retained(ordered(TIED, "white", &["a7","c7"], &["a2"]), false);
        for (field, value) in [("clear",json!(1)), ("phase",json!({"opening":0,"middlegame":16,"endgame":239})),
            ("materialScore",json!(10001)), ("rootSide",json!("white")), ("sideToMove",json!("White"))] {
            let mut bad = good.clone(); bad[field] = value;
            assert!(RetainedStep::parse(&json!({"steps":[good.clone(),bad]})).is_err(), "{field}");
        }
        for order in [json!(["a7"]),json!(["a7","a7"]),json!(["a7","h8"])] {
            let mut bad = good.clone(); bad["pawnOrder"]["white"] = order;
            assert!(RetainedStep::parse(&json!({"steps":[good.clone(),bad]})).is_err());
        }
        let mut bad = good.clone(); bad["weights"]["black"]["progress"] = json!(10001);
        bad["phase"] = json!({"opening":256,"middlegame":0,"endgame":0});
        assert!(RetainedStep::parse(&json!({"steps":[good.clone(),bad]})).is_err());
        assert!(RetainedStep::parse(&json!({"steps":[]})).is_err());
        assert!(RetainedStep::parse(&json!({"steps":vec![good;4097]})).is_err());
    }

    #[test]
    fn search_rejects_late_fields_incomplete_percentages_and_root_mismatch_before_context() {
        let position = ordered(TIED, "white", &["a7","c7"], &["a2"]);
        let good = search(vec![position.clone(), position], "white");
        for field in ["phase","weights","materialScore","clear","rootSide"] {
            let mut bad = good.clone(); bad["positions"][1][field] = Value::Null;
            assert!(SearchSequence::parse(&bad).is_err(), "{field}");
        }
        for value in [json!(-1),json!(1001),json!(1.5),Value::Null] {
            let mut bad = good.clone(); bad["percentages"]["opponent"]["king"] = value;
            assert!(SearchSequence::parse(&bad).is_err());
        }
        let mut bad = good.clone(); bad["percentages"]["own"].as_object_mut().unwrap().remove("mobility");
        assert!(SearchSequence::parse(&bad).is_err());
        let mut bad = good.clone(); bad["positions"][1]["pawnOrder"]["white"] = json!(["a7"]);
        assert!(SearchSequence::parse(&bad).is_err());
        let mut bad = good.clone(); bad["rootSide"] = json!("black");
        assert!(SearchSequence::parse(&bad).is_err());
        let mut bad = good.clone(); bad["averageDepth"] = json!(101);
        assert!(SearchSequence::parse(&bad).is_err());
        let mut bad = good.clone(); bad["positions"] = json!([]);
        assert!(SearchSequence::parse(&bad).is_err());
        let mut bad = good.clone(); bad["positions"] = json!(vec![good["positions"][0].clone();4097]);
        assert!(SearchSequence::parse(&bad).is_err());
    }

    #[test]
    fn component_placements_admit_adjacent_kings_but_keep_bounded_material_limits() {
        let adjacent = ordered("8/8/8/8/8/8/k7/K7", "white", &[], &[]);
        assert!(SearchSequence::parse(&search(vec![adjacent.clone()], "white")).is_ok());
        assert!(RetainedStep::parse(&json!({"steps":[retained(adjacent,false)]})).is_ok());
        for placement in ["P6k/8/8/8/8/8/8/K7", "7k/8/8/8/8/NNNNNNNN/NNN5/K7",
            "7k/8/8/8/8/8/PPPPPPPP/KP6"] {
            let bad = ordered(placement, "white", &[], &[]);
            assert!(SearchSequence::parse(&search(vec![bad.clone()], "white")).is_err());
            assert!(RetainedStep::parse(&json!({"steps":[retained(bad,false)]})).is_err());
        }
    }
}
