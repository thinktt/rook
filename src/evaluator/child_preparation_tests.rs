use super::*;
use crate::{engine::Search,history::SearchHistory,quiescence::Limits};

#[test]
fn queued_children_preserve_native_sequence_and_all_counted_work() {
    for fen in ["rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",
        "r3k2r/ppp2ppp/2n5/3pp3/3PP3/2N5/PPP2PPP/R3K2R w KQkq - 0 1"] {
        let position=Position::from_fen(fen).unwrap();
        let mut a=Search::<true>::new(&position);
        let mut b=Search::<true>::new(&position);
        for s in [&mut a,&mut b] {
            s.config.tts_bytes=65536;
            s.evaluator.parameters.own=[100,112,134,95,87,0,90,130,75,110,120];
            s.evaluator.parameters.opponent=[95,104,120,110,98,0,115,80,125,105,90];
        }
        b.evaluator.set_child_preparation_budget(2).unwrap();
        let mut ha=SearchHistory::new(&position);let mut hb=ha.clone();
        let x=a.run_seeded_iterations(position,&mut ha,4,Limits::default(),123,31, |_|{}).unwrap();
        let y=b.run_seeded_iterations(position,&mut hb,4,Limits::default(),123,31, |_|{}).unwrap();
        assert_eq!((x.score,x.pv,x.work,x.stats,x.evaluations),(y.score,y.pv,y.work,y.stats,y.evaluations));
        assert_eq!(ha,hb);
        assert_eq!(a.stats,b.stats);
        #[cfg(feature="branch-transactions")]
        assert!(a.research_eq(&b));
        let stats=b.evaluator.finish_child_preparation().unwrap();
        assert!(stats.contains("published"));
    }
}

#[test]
fn child_pool_cannot_nest_the_full_worker() {
    let p=Position::from_fen("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1").unwrap();
    let mut e=Evaluator::<true>::new(&p);
    e.set_child_preparation_budget(2).unwrap();
    assert!(e.set_threads(2).is_err());
    e.finish_child_preparation().unwrap();
}
