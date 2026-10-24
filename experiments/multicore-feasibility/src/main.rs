//! Standalone dependency/transport probe, never linked into the engine.
use rook2::{activity, endgame, evaluation::RootContext,
    evaluator::{Components, Evaluator, Node}, influence::Influence,
    movegen::{self, MoveList}, pawn_progress, pawn_structure::PawnCache,
    pawn_terms, positional_terms, position::Position, shelter, types::Color};
use std::{hint::{black_box, spin_loop}, sync::{Arc, Mutex, atomic::{AtomicUsize, Ordering}},
    thread, time::Instant};

const START: &str = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1";
const ITEMS: usize = 172_800; // divisible by 54 corpus entries and batches 1/8/32
#[repr(C)] struct Timespec { seconds: i64, nanos: i64 }
extern "C" {
    fn clock_gettime(clock: i32, out: *mut Timespec) -> i32;
    fn sched_setaffinity(pid: i32, bytes: usize, mask: *const u64) -> i32;
    fn sched_getaffinity(pid: i32, bytes: usize, mask: *mut u64) -> i32;
}
fn cpu_ns() -> u64 {
    let mut t = Timespec { seconds: 0, nanos: 0 };
    // Linux x86-64 CLOCK_PROCESS_CPUTIME_ID: includes both measured threads.
    assert_eq!(unsafe { clock_gettime(2, &mut t) }, 0);
    t.seconds as u64 * 1_000_000_000 + t.nanos as u64
}
fn pin(cpu: usize) {
    let mut mask = [0u64; 16]; mask[cpu/64] |= 1 << (cpu%64);
    assert_eq!(unsafe { sched_setaffinity(0, 128, mask.as_ptr()) }, 0);
    let mut actual = [0u64; 16];
    assert_eq!(unsafe { sched_getaffinity(0, 128, actual.as_mut_ptr()) }, 0);
    assert_eq!(actual, mask);
}
struct Input { p: Position, influence: Influence, material: i32, nonking: i32, checked: bool }
#[derive(Clone, Copy, Default, Debug, PartialEq, Eq)]
struct Chain { activity: activity::Activity, shelter: shelter::Shelter }
fn chain(x: &Input) -> Chain {
    let activity = activity::compute(black_box(&x.p), &x.influence, x.material, [1024;2]);
    let shelter = shelter::compute(&x.p, &x.influence, activity.pressure, x.material, [1024;2]);
    Chain { activity, shelter }
}
#[derive(Clone, Copy, Default)]
struct Owner { components: Components, queries: u64, reused: bool }
fn owner(x: &Input, cache: &mut PawnCache, root: &RootContext) -> Owner {
    let phase = x.p.phase();
    let selected = cache.select(&x.p, &x.influence);
    let pawn = pawn_terms::compute(&x.p, &x.influence, &selected.structure);
    let structure = pawn_progress::structure_weighted(phase, pawn.structure, pawn.piece, [1024;2]);
    let progress = if phase.middlegame == 0 && phase.endgame == 0 {0} else {
        pawn_progress::selected(&x.p, &x.influence, &selected.structure, phase, x.material, [1024;2]).weighted
    };
    let central = positional_terms::central(&x.influence, phase, [1024;2]);
    let patterns = positional_terms::patterns(&x.p);
    Owner { components: Components { material: x.material,
        squares: root.square_balance_from(&x.p, x.nonking), pawn_structure: structure,
        pawn_progress: progress, central: central.weighted, bishops: patterns.bishop_coordination,
        patterns: patterns.opening, ..Components::default() }, queries: pawn.relation_queries,
        reused: selected.reused }
}
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
struct Output { c: Components, queries: u64, reused: bool, score: i32, lower: i32, upper: i32 }
fn join(x: &Input, mut o: Owner, c: Chain, root: &RootContext) -> Output {
    let phase = x.p.phase();
    o.components.activity = c.activity.weighted; o.components.shelter = c.shelter.weighted;
    o.components.tempo = if x.checked {0} else {
        let magnitude = ((c.activity.pieces[x.p.side.index()] as i64+140)
            *(5*phase.opening as i64+4*phase.middlegame as i64+2*phase.endgame as i64)+16384)
            .div_euclid(32768) as i32;
        if x.p.side == Color::White {magnitude} else {-magnitude}
    };
    let finished = endgame::finish(&x.p, o.components.base(), 0, root.side, 0,
        x.p.primary ^ x.p.secondary, phase.endgame, x.checked, o.components.pawn_progress);
    Output { c:o.components, queries:o.queries+c.activity.relation_queries,
        reused:o.reused, score:finished.score, lower:finished.lower, upper:finished.upper }
}
fn digest(c: Components, q: u64) -> u64 {
    [c.material,c.squares,c.pawn_structure,c.pawn_progress,c.activity,c.central,c.shelter,
     c.bishops,c.patterns,c.tempo].into_iter().fold(q,|a,b|a.rotate_left(7)^b as u64)
}
fn chain_digest(c: Chain) -> u64 {
    [c.activity.pieces[0],c.activity.pieces[1],c.activity.pressure[0],c.activity.pressure[1],
     c.activity.weighted,c.shelter.terms[0],c.shelter.terms[1],c.shelter.weighted]
        .into_iter().fold(c.activity.relation_queries,|a,b|a.rotate_left(7)^b as u64)
}
#[repr(align(64))] struct Counter(AtomicUsize);
struct Slot { request: Counter, done: Counter, first: Counter, results: Mutex<Vec<Chain>> }
struct Worker { slot: Arc<Slot>, thread: Option<thread::JoinHandle<()>>, sequence: usize }
impl Worker {
    fn new(data: Arc<Vec<Input>>, count: usize, cpu: usize, empty: bool) -> Self {
        let slot = Arc::new(Slot { request:Counter(AtomicUsize::new(0)),
            done:Counter(AtomicUsize::new(0)), first:Counter(AtomicUsize::new(0)),
            results:Mutex::new(vec![Chain::default();count]) });
        let shared = Arc::clone(&slot);
        let thread = thread::spawn(move || {
            pin(cpu); let mut last = 0;
            shared.done.0.store(usize::MAX,Ordering::Release); // startup, outside timing
            loop {
                let generation = shared.request.0.load(Ordering::Acquire);
                if generation == usize::MAX {break;}
                if generation == last {spin_loop();continue;}
                let first = shared.first.0.load(Ordering::Relaxed);
                {
                    let mut values = shared.results.lock().unwrap();
                    for j in 0..count { values[j] = if empty {Chain::default()}
                        else {chain(&data[(first+j)%data.len()])}; }
                }
                last = generation;
                shared.done.0.store(last,Ordering::Release);
            }
        });
        while slot.done.0.load(Ordering::Acquire) != usize::MAX {spin_loop();}
        Self { slot, thread:Some(thread), sequence:0 }
    }
    fn send(&mut self, first: usize) {
        self.sequence+=1;
        self.slot.first.0.store(first,Ordering::Relaxed);
        self.slot.request.0.store(self.sequence,Ordering::Release);
    }
    fn wait(&self) { while self.slot.done.0.load(Ordering::Acquire)!=self.sequence {spin_loop();} }
}
impl Drop for Worker {
    fn drop(&mut self) {
        self.slot.request.0.store(usize::MAX,Ordering::Release);
        self.thread.take().unwrap().join().unwrap();
    }
}
fn load(path: &str, root: &RootContext) -> Vec<Input> {
    std::fs::read_to_string(path).unwrap().lines().map(|line| {
        let (_, moves) = line.split_once('\t').unwrap();
        let mut p=Position::from_fen(START).unwrap();
        for token in moves.split_whitespace() {
            let mut legal=MoveList::new();movegen::generate_legal(&p,&mut legal);
            let m=*legal.as_slice().iter().find(|m|m.to_string()==token).unwrap();
            p=p.played_unchecked(m);
        }
        Input { influence:Influence::build(&p), material:root.material(&p),
            nonking:root.nonking_square_balance(&p), checked:movegen::in_check(&p,p.side), p }
    }).collect()
}
fn verify(data: Arc<Vec<Input>>, root: &RootContext, worker_cpu: usize) {
    let mut reference=Evaluator::<false>::new(&Position::from_fen(START).unwrap());
    let mut cache=PawnCache::new();
    let mut worker=Worker::new(Arc::clone(&data),1,worker_cpu,false);
    for i in 0..data.len()*3 {
        let x=&data[i%data.len()]; worker.send(i%data.len());
        let o=owner(x,&mut cache,root);worker.wait();
        let c=worker.slot.results.lock().unwrap()[0];assert_eq!(c,chain(x));
        let actual=join(x,o,c,root);
        let mut node=Node::root(x.p,root); let mut details=None;
        let expected=reference.full_detailed_observed(&mut node,&x.influence,x.checked,|d|details=Some(d));
        let details=details.unwrap();
        assert_eq!(actual, Output {c:details.components,queries:expected.relation_queries,
            reused:details.pawn_entry_reused, score:expected.score,lower:expected.lower,upper:expected.upper});
        assert_eq!((node.retained.positional,node.retained.pawn_progress,node.retained.age),
            (actual.c.positional(),actual.c.pawn_progress,0));
    }
    println!("{{\"verification\":\"pass\",\"full_calls\":{},\"worker_cpu\":{worker_cpu}}}",data.len()*3);
}
fn run(data: &[Input], root: &RootContext, worker: &mut Option<Worker>,
       count: usize, items: usize, full: bool, empty: bool) -> u64 {
    let mut cache=PawnCache::new(); let mut total=0u64;
    let mut prepared=[Owner::default();32];
    for batch in 0..items/count {
        let first=(batch*count)%data.len();
        if let Some(w)=worker.as_mut() {w.send(first);}
        if full {for j in 0..count {prepared[j]=owner(&data[(first+j)%data.len()],&mut cache,root);}}
        if let Some(w)=worker.as_ref() {
            w.wait();let values=w.slot.results.lock().unwrap();
            for j in 0..count {
                let c=values[j]; let h=if full {
                    let o=join(&data[(first+j)%data.len()],prepared[j],c,root);
                    digest(o.c,o.queries)^o.score as u64^o.lower as u64^o.upper as u64^u64::from(o.reused)
                } else {chain_digest(c)};
                total=total.wrapping_add(h);
            }
        } else {
            for j in 0..count {
                let c=if empty {Chain::default()} else {chain(&data[(first+j)%data.len()])};
                let h=if full {
                    let o=join(&data[(first+j)%data.len()],prepared[j],c,root);
                    digest(o.c,o.queries)^o.score as u64^o.lower as u64^o.upper as u64^u64::from(o.reused)
                } else {chain_digest(c)};
                total=total.wrapping_add(h);
            }
        }
    }
    black_box(total)
}
fn main() {
    let args:Vec<_>=std::env::args().collect();
    let worker_cpu:usize=args[2].parse().unwrap();pin(14);
    let root=RootContext::neutral(&Position::from_fen(START).unwrap());
    let data=Arc::new(load(&args[1],&root));assert_eq!(data.len(),54);
    verify(Arc::clone(&data),&root,worker_cpu);
    for (name,full,empty) in [("empty",false,true),("chain",false,false),("full",true,false)] {
        let mut expected=None;
        for count in [0,1,8,32] {
            if empty && count>1 {continue;}
            let batch=count.max(1);
            let mut worker=if count==0 {None} else {Some(Worker::new(Arc::clone(&data),batch,worker_cpu,empty))};
            black_box(run(&data,&root,&mut worker,batch,1728,full,empty));
            for sample in 0..3 {
                let cpu=cpu_ns();let wall=Instant::now();
                let sink=run(&data,&root,&mut worker,batch,ITEMS,full,empty);
                let wall_ns=wall.elapsed().as_nanos();let cpu_ns=cpu_ns()-cpu;
                if let Some(e)=expected {assert_eq!(sink,e);} else {expected=Some(sink);}
                println!("{{\"kernel\":\"{name}\",\"batch\":{count},\"sample\":{sample},\"items\":{ITEMS},\"wall_ns\":{wall_ns},\"cpu_ns\":{cpu_ns},\"sink\":{sink},\"worker_cpu\":{worker_cpu}}}");
            }
        }
    }
}
