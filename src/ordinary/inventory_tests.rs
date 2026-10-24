//! Exact native producer/order and ordinary-owner lifetime controls.
use super::*;
use crate::evaluator::{inventory_domain, ResearchFullMode};
use crate::inventory_worker::Stats as InventoryStats;
use std::panic::{catch_unwind, AssertUnwindSafe};

const START: &str = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1";
const ENDING: &str = "6k1/5pp1/6p1/3P4/8/2N5/5P2/6K1 w - - 0 40";

fn accounting(stats: InventoryStats) {
    assert_eq!(stats.eligible,stats.launches+stats.busy+stats.domain_skips);
    assert_eq!(stats.launches,stats.completed);
    assert_eq!(stats.launches,stats.consumed+stats.discarded);
    assert_eq!(stats.consumed,stats.ready_consumed+stats.local_consumed);
    assert_eq!(stats.null_settles,stats.null_ready+stats.null_waited);
    assert!(stats.local_consumed<=stats.null_settles);
    assert!(stats.ready_miss<=stats.discarded);
}

fn equal_search<const D:bool>(actual:&Outcome,expected:&Outcome,worker:&mut Search<D>,serial:&mut Search<D>) {
    assert_eq!((&actual.initial_candidates,actual.score,&actual.pv,actual.work,actual.stats,actual.evaluations),
        (&expected.initial_candidates,expected.score,&expected.pv,expected.work,expected.stats,expected.evaluations));
    assert_eq!(actual.iterations.len(),expected.iterations.len());
    for (a,b) in actual.iterations.iter().zip(&expected.iterations) {
        assert_eq!((a.depth,&a.candidates,&a.steps,a.score,&a.pv,a.work),
            (b.depth,&b.candidates,&b.steps,b.score,&b.pv,b.work));
    }
    assert_eq!(worker.learning.history,serial.learning.history);
    assert_eq!(worker.learning.killers,serial.learning.killers);
    assert_eq!(worker.learning.total,serial.learning.total);
    assert_eq!(worker.evaluator.test_pawn_cache(),serial.evaluator.test_pawn_cache());
    #[cfg(feature="branch-transactions")]
    assert!(worker.research_eq(serial));
}

#[test]
fn exact_native_unsorted_inventory_handles_checked_castle_ep_and_promotions() {
    let initial=Position::from_fen(START).unwrap();
    let mut evaluator=crate::evaluator::Evaluator::<true>::new(&initial);
    evaluator.set_research_full_mode(ResearchFullMode::Inventory).unwrap();
    let scope=evaluator.full_worker_scope().unwrap();
    let fixtures=[START,
        "4k3/8/8/8/8/8/4r3/4K3 w - - 0 1",
        "r3k2r/8/8/8/8/8/8/R3K2R w KQkq - 0 1",
        "4k3/8/8/3pP3/8/8/8/4K3 w - d6 0 1",
        "7k/P7/8/8/8/8/8/K7 w - - 0 1"];
    for fen in fixtures {
        let position=Position::from_fen(fen).unwrap(); position.validate().unwrap();
        assert!(inventory_domain(&position,true));
        let mut expected=MoveList::new(); movegen::generate_legal(&position,&mut expected);
        let mut ticket=evaluator.launch_inventory(&position,true).unwrap();
        ticket.settle_for_null().unwrap();
        let mut actual=MoveList::new(); assert!(ticket.consume_into(&mut actual).unwrap());
        assert_eq!(actual.as_slice(),expected.as_slice());
    }
    drop(scope); assert!(evaluator.inventory_is_parked());
    let stats=evaluator.inventory_stats(); accounting(stats);
    assert_eq!(stats.launches,5); assert_eq!(stats.local_consumed,5); assert_eq!(stats.discarded,0);
}

#[test]
fn admitted_domain_excludes_unsafe_early_generation_without_launching() {
    let position=Position::from_fen(START).unwrap();
    let mut evaluator=crate::evaluator::Evaluator::<true>::new(&position);
    evaluator.set_research_full_mode(ResearchFullMode::Inventory).unwrap();
    let scope=evaluator.full_worker_scope().unwrap();
    assert!(evaluator.launch_inventory(&position,false).is_none());
    let mut missing=position; missing.counts[0][PieceKind::King.index()]=0;
    assert!(evaluator.launch_inventory(&missing,true).is_none());
    let enemy_checked=Position::from_fen("4k3/8/8/8/8/8/4R3/4K3 w - - 0 1").unwrap();
    assert!(evaluator.launch_inventory(&enemy_checked,true).is_none());
    drop(scope);
    let stats=evaluator.inventory_stats(); accounting(stats);
    assert_eq!((stats.eligible,stats.domain_skips,stats.launches),(3,3,0));
}

#[test]
fn real_search_order_work_shared_state_and_repeated_roots_match_inline() {
    fn verify<const D:bool>() {
        let initial=Position::from_fen(START).unwrap();
        let mut serial=Search::<D>::new(&initial); serial.config.tts_bytes=65536;
        let mut worker=Search::<D>::new(&initial); worker.config.tts_bytes=65536;
        worker.evaluator.set_research_full_mode(ResearchFullMode::Inventory).unwrap();
        for fen in [START,ENDING,START] {
            let position=Position::from_fen(fen).unwrap();
            let (mut ah,mut bh)=(SearchHistory::new(&position),SearchHistory::new(&position));
            let expected=serial.run_iterations(position,&mut ah,3,Limits{nodes:Some(200000)}).unwrap();
            let actual=worker.run_iterations(position,&mut bh,3,Limits{nodes:Some(200000)}).unwrap();
            equal_search(&actual,&expected,&mut worker,&mut serial);
            assert_eq!((ah.search_ply(),bh.search_ply()),(0,0));
            assert!(worker.evaluator.inventory_is_parked()); accounting(worker.evaluator.inventory_stats());
            for limit in [0,25] {
                let expected=serial.run_iterations(position,&mut ah,3,Limits{nodes:Some(limit)});
                let actual=worker.run_iterations(position,&mut bh,3,Limits{nodes:Some(limit)});
                assert!(matches!(expected,Err(Error::Stopped(Stopped::NodeLimit(n))) if n==limit));
                assert!(matches!(actual,Err(Error::Stopped(Stopped::NodeLimit(n))) if n==limit));
                assert_eq!(worker.work(),serial.work()); assert_eq!(worker.stats,serial.stats);
                assert_eq!(worker.evaluator.stats,serial.evaluator.stats);
                assert_eq!(worker.evaluator.test_pawn_cache(),serial.evaluator.test_pawn_cache());
                assert_eq!((ah.search_ply(),bh.search_ply()),(0,0));
                assert!(worker.evaluator.inventory_is_parked()); accounting(worker.evaluator.inventory_stats());
            }
        }
        assert!(worker.evaluator.inventory_stats().launches>0);
        assert_eq!(worker.evaluator.inventory_stats().busy,0,"parent slot leaked into recursive work");
    }
    verify::<true>(); verify::<false>();
}

fn null_call(inventory:bool,cutoff:bool,node_limit:u64)->(Result<i32,Stopped>,Search<true>,Node) {
    let initial=Position::from_fen(START).unwrap();
    let previous=initial.null_child(); let position=previous.null_child();
    let mut search=Search::<true>::new(&position); search.config.tts_bytes=65536;
    if inventory {search.evaluator.set_research_full_mode(ResearchFullMode::Inventory).unwrap();}
    let scope=search.evaluator.full_worker_scope();
    search.ensure_table().unwrap(); search.bind_geometry_permission(&position);
    let (mut node,map)=search.prepare_root_with_influence(position);
    let score=search.evaluator.full(&mut node,&map,false).score;
    if !cutoff {assert!(score>0,"symmetric native FULL supplies the null-continue fixture");}
    let upper=if cutoff {-1000} else {score};
    let mut history=SearchHistory::new(&previous); history.push(&position,None);
    search.begin_owned_sequence(Limits{nodes:Some(node_limit)});
    let returned=search.visit_ordinary(&mut node,&mut history,
        Request{ply:1,depth:3,lower:upper-1,upper,previous_extension:0,iteration:4,checked:Some(false)},
        Predecessor{position:&previous,influence:&map,checked:false,movement:None});
    assert!(search.stats.null_trials>0); assert_eq!(history.search_ply(),1);
    history.pop(); drop(scope);
    (returned,search,node)
}

#[test]
fn recursive_null_settles_parent_then_consumes_or_discards_owned_list() {
    for cutoff in [true,false] {
        let (expected,mut serial,expected_node)=null_call(false,cutoff,200000);
        let (actual,mut worker,actual_node)=null_call(true,cutoff,200000);
        assert_eq!(actual,expected); assert!(actual.is_ok()); assert_eq!(actual_node,expected_node);
        assert_eq!(worker.work(),serial.work()); assert_eq!(worker.stats,serial.stats);
        assert_eq!(worker.evaluator.stats,serial.evaluator.stats);
        assert_eq!(worker.evaluator.test_pawn_cache(),serial.evaluator.test_pawn_cache());
        assert_eq!(worker.learning.history,serial.learning.history); assert_eq!(worker.learning.killers,serial.learning.killers);
        assert_eq!(worker.learning.total,serial.learning.total);
        let stats=worker.evaluator.inventory_stats(); accounting(stats);
        assert!(stats.null_settles>0); assert_eq!(stats.busy,0); assert!(worker.evaluator.inventory_is_parked());
        if cutoff {assert_eq!(stats.consumed,0); assert_eq!(stats.discarded,stats.launches);}
        else {assert!(stats.local_consumed>0);}
        #[cfg(feature="branch-transactions")]
        assert!(worker.research_eq(&serial));
    }
}

#[test]
fn stopped_null_restores_history_discards_parent_and_allows_next_lifetime() {
    let (expected,mut serial,expected_node)=null_call(false,true,1);
    let (actual,mut worker,actual_node)=null_call(true,true,1);
    assert_eq!(expected,Err(Stopped::NodeLimit(1))); assert_eq!(actual,expected);
    assert_eq!(actual_node,expected_node); assert_eq!(worker.work(),serial.work());
    assert_eq!(worker.stats,serial.stats); assert_eq!(worker.evaluator.stats,serial.evaluator.stats);
    assert_eq!(worker.evaluator.test_pawn_cache(),serial.evaluator.test_pawn_cache());
    let stats=worker.evaluator.inventory_stats(); accounting(stats);
    assert_eq!((stats.null_settles,stats.consumed,stats.discarded),(1,0,1));
    assert!(worker.evaluator.inventory_is_parked());
    let position=Position::from_fen(START).unwrap();
    let (mut ah,mut bh)=(SearchHistory::new(&position),SearchHistory::new(&position));
    let expected=serial.run_iterations(position,&mut ah,1,Limits::default()).unwrap();
    let actual=worker.run_iterations(position,&mut bh,1,Limits::default()).unwrap();
    equal_search(&actual,&expected,&mut worker,&mut serial);
    assert!(worker.evaluator.inventory_is_parked()); accounting(worker.evaluator.inventory_stats());
}

#[test]
fn direct_full_fast_and_quiescence_do_not_launch_inventory() {
    let position=Position::from_fen(START).unwrap();
    let mut serial=Search::<true>::new(&position); serial.config.tts_bytes=65536;
    let mut worker=Search::<true>::new(&position); worker.config.tts_bytes=65536;
    worker.evaluator.set_research_full_mode(ResearchFullMode::Inventory).unwrap();
    let map=Influence::build(&position);
    let (mut a,mut b)=(Node::root(position,&serial.evaluator.root),Node::root(position,&worker.evaluator.root));
    assert_eq!(worker.evaluator.full(&mut b,&map,false),serial.evaluator.full(&mut a,&map,false));
    assert_eq!(b,a); assert_eq!(worker.evaluator.fast(&b,false),serial.evaluator.fast(&a,false));
    assert_eq!(worker.evaluator.inventory_stats(),InventoryStats::default()); assert!(worker.evaluator.inventory_is_parked());
    let (mut ah,mut bh)=(SearchHistory::new(&position),SearchHistory::new(&position));
    let expected=serial.run_iterations(position,&mut ah,1,Limits::default()).unwrap();
    let actual=worker.run_iterations(position,&mut bh,1,Limits::default()).unwrap();
    equal_search(&actual,&expected,&mut worker,&mut serial);
    assert_eq!(worker.evaluator.inventory_stats(),InventoryStats::default()); assert!(worker.evaluator.inventory_is_parked());
}

#[test]
fn failed_worker_cannot_publish_partial_inventory_and_mode_change_joins_it() {
    let position=Position::from_fen(START).unwrap();
    let mut search=Search::<true>::new(&position); search.config.tts_bytes=65536;
    search.evaluator.set_research_full_mode(ResearchFullMode::Inventory).unwrap();
    search.evaluator.inventory_fail_next();
    let mut history=SearchHistory::new(&position);
    assert!(catch_unwind(AssertUnwindSafe(||search.run_iterations(position,&mut history,2,Limits::default()))).is_err());
    assert!(search.evaluator.set_research_full_mode(ResearchFullMode::Inline).is_err());
    let mut serial=Search::<true>::new(&position); serial.config.tts_bytes=65536;
    let (mut ah,mut bh)=(SearchHistory::new(&position),SearchHistory::new(&position));
    let expected=serial.run_iterations(position,&mut ah,2,Limits::default()).unwrap();
    let actual=search.run_iterations(position,&mut bh,2,Limits::default()).unwrap();
    equal_search(&actual,&expected,&mut search,&mut serial);
}

#[cfg(feature="branch-transactions")]
#[test]
fn pure_generation_can_record_serial_journal_but_detached_clone_rejects_worker() {
    let position=Position::from_fen(START).unwrap();
    let mut serial=Search::<true>::new(&position); serial.config.tts_bytes=65536; serial.ensure_table().unwrap();
    let mut worker=Search::<true>::new(&position); worker.config.tts_bytes=65536; worker.ensure_table().unwrap();
    worker.evaluator.set_research_full_mode(ResearchFullMode::Inventory).unwrap();
    assert!(catch_unwind(AssertUnwindSafe(||worker.research_clone())).is_err());
    let a=crate::branch_journal::Sink::new(16384); let b=crate::branch_journal::Sink::new(16384);
    serial.research_attach_sink(Some(a.clone())); worker.research_attach_sink(Some(b.clone()));
    let (mut ah,mut bh)=(SearchHistory::new(&position),SearchHistory::new(&position));
    let expected=serial.run_iterations(position,&mut ah,2,Limits::default()).unwrap();
    let actual=worker.run_iterations(position,&mut bh,2,Limits::default()).unwrap();
    serial.research_attach_sink(None); worker.research_attach_sink(None);
    let (a,b)=(a.take(),b.take()); assert!(!a.overflowed && !b.overflowed);
    assert_eq!(format!("{:?}",a.events),format!("{:?}",b.events));
    equal_search(&actual,&expected,&mut worker,&mut serial);
}
