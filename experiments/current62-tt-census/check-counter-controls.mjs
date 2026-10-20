// Hand-accounted two-store/one-probe story; no engine or future workload is run.
import assert from 'node:assert/strict';
import {census} from './counters.mjs';
import {checkIndependentTT} from './independent-counters.mjs';
const z=(a,b)=>Array.from({length:a},()=>Array(b).fill(0));
const c={schema:'rook2-tt-probe-store-census-v1',pid:123,complete:true,overflow:false,invalid:false,
 probes:{calls:1,joint:z(4,8),filter:z(4,3),consider:z(4,3),mate_depth:z(4,2),returns_score:1,returns_no_score:0,read_line_hist:[0,0,1],mate_write_line_hist:[1,0,0],group_phase:Array(64).fill(0)},
 stores:{calls:2,filter:[[1,0,1],[1,0,0],[1,0,0]],branches:[1,0,1,0,0],branch_slot:[[1,0,0],[0,0,0],[1,0,0],[0,0,0],[0,0,0]],retained_writes:[1,0,0],recent_writes:[1,1,0,0],empty_scan:[[0,1],[0,0],[0,0]],least_depth_comparisons:0},
 lifecycle:{allocations:1,groups_allocated:1,capacity_groups_allocated:1,initialized_groups:1,max_groups:1,max_capacity_groups:1,generation_clears:0,wrap_clears:0,wrap_groups_cleared:0}};
// Fill retained0, store same identity shallower into recent, then require depth
// between them: recent metadata continues, retained0 supplies a normal score.
c.probes.joint[2][3]=1;c.probes.filter[3][2]=1;c.probes.filter[0][2]=1;
c.probes.consider[3][2]=1;c.probes.consider[0][0]=1;c.probes.group_phase[32]=1;
const live=x=>census(Buffer.from(JSON.stringify(x)),123);
live(c);checkIndependentTT(c,123);
// A usable mate can perform its original depth store without changing depth.
const mate=structuredClone(c);mate.probes.consider[0]=[0,1,0];mate.probes.mate_depth[0]=[1,0];mate.probes.mate_write_line_hist=[0,1,0];
live(mate);checkIndependentTT(mate,123);
let rejected=0;
for(const damage of [
 x=>{x.probes.joint[2][3]=0;x.probes.joint[3][3]=1;}, // retained visited after usable recent
 x=>{x.probes.filter[1][0]=1;}, // examined beyond first live retained match
 x=>{x.probes.mate_write_line_hist=[1,0,0];}, // missed unchanged-value mate store
 x=>{x.stores.retained_writes[1]=1;}, // write/selected-slot mismatch
 x=>{x.overflow=true;},
 x=>{x.probes.calls=Number.MAX_SAFE_INTEGER+1;},
]){
 const bad=structuredClone(mate);damage(bad);
 assert.throws(()=>live(bad));assert.throws(()=>checkIndependentTT(bad,123));rejected++;
}
console.log(JSON.stringify({complete:true,hand_accounted_controls:2,rejected_corruptions:rejected,engineRuns:0}));
