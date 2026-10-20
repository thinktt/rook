// Offline reconciliation, expressed independently of the live validator.
import assert from 'node:assert/strict';
export function checkIndependentTT(c,pid){
 const names=(o,a)=>assert.deepEqual(Object.keys(o).sort(),a.sort());
 const v=x=>{assert(Number.isSafeInteger(x)&&x>=0);return BigInt(x);};
 const total=a=>a.reduce((s,x)=>s+v(x),0n);
 const dims=(a,rows,cols)=>{assert.equal(a.length,rows);for(const r of a){assert.equal(r.length,cols);r.forEach(v);}};
 names(c,['schema','pid','complete','overflow','invalid','probes','stores','lifecycle']);
 assert.equal(c.schema,'rook2-tt-probe-store-census-v1');assert.equal(c.pid,pid);assert.equal(c.complete,true);assert.equal(c.overflow,false);assert.equal(c.invalid,false);
 const {probes:p,stores:s,lifecycle:l}=c;
 names(p,['calls','joint','filter','consider','mate_depth','returns_score','returns_no_score','read_line_hist','mate_write_line_hist','group_phase']);
 dims(p.joint,4,8);dims(p.filter,4,3);dims(p.consider,4,3);dims(p.mate_depth,4,2);
 [p.calls,p.returns_score,p.returns_no_score].forEach(v);
 for(const[k,length]of [['read_line_hist',3],['mate_write_line_hist',3],['group_phase',64]]){assert.equal(p[k].length,length);p[k].forEach(v);}
 assert(v(p.calls)>0n);
 let probes=0n,recentReturned=0n,retainedConsider=0n,scored=0n;
 const expectedRecent=[0n,0n,0n,0n],expectedRetained=[[0n,0n],[0n,0n],[0n,0n]];
 for(let r=0;r<4;r++)for(let col=0;col<8;col++){
  const x=v(p.joint[r][col]);probes+=x;expectedRecent[r]+=x;
  if(r===3){assert.equal(col===0?0n:x,0n);recentReturned+=x;scored+=x;}
  else{if(col===0)assert.equal(x,0n);if(col>=2){const slot=Math.floor((col-2)/2),score=(col-2)%2;expectedRetained[slot][score]+=x;retainedConsider+=x;if(score)scored+=x;}}
 }
 assert.equal(probes,v(p.calls));assert.equal(v(p.returns_score),scored);assert.equal(v(p.returns_no_score),probes-scored);
 assert.equal(v(p.filter[3][0]),expectedRecent[0]);assert.equal(v(p.filter[3][1]),expectedRecent[1]);
 assert.equal(v(p.consider[3][2]),expectedRecent[2]);assert.equal(v(p.consider[3][0])+v(p.consider[3][1]),expectedRecent[3]);
 assert.equal(total(p.filter[3]),probes);
 let attempt=probes-recentReturned;
 for(let slot=0;slot<3;slot++){
  assert.equal(total(p.filter[slot]),attempt);
  assert.equal(v(p.consider[slot][2]),expectedRetained[slot][0]);
  assert.equal(v(p.consider[slot][0])+v(p.consider[slot][1]),expectedRetained[slot][1]);
  attempt-=v(p.filter[slot][2]);
 }
 assert.equal(attempt,total(p.joint.map(r=>r[1])));
 assert.equal(p.consider.slice(0,3).reduce((a,row)=>a+total(row),0n),retainedConsider);
 let mates=0n;
 for(let slot=0;slot<4;slot++){
  assert.equal(v(p.filter[slot][2]),total(p.consider[slot]));
  const m=total(p.mate_depth[slot]);assert.equal(m,v(p.consider[slot][1]));mates+=m;
 }
 assert.equal(total(p.read_line_hist),probes);assert.equal(p.read_line_hist[0],0);
 assert.deepEqual(p.mate_write_line_hist.map(v),[probes-mates,mates,0n]);
 assert.equal(total(p.group_phase),probes);p.group_phase.forEach((x,phase)=>{if(phase%4)assert.equal(x,0);});
 names(s,['calls','filter','branches','branch_slot','retained_writes','recent_writes','empty_scan','least_depth_comparisons']);
 dims(s.filter,3,3);dims(s.branch_slot,5,3);dims(s.empty_scan,3,2);
 for(const[k,length]of [['branches',5],['retained_writes',3],['recent_writes',4]]){assert.equal(s[k].length,length);s[k].forEach(v);}
 v(s.calls);v(s.least_depth_comparisons);assert.equal(total(s.branches),v(s.calls));
 let storesRemaining=v(s.calls);
 for(let i=0;i<3;i++){
  assert.equal(total(s.filter[i]),storesRemaining);
  assert.equal(v(s.filter[i][2]),v(s.branch_slot[0][i])+v(s.branch_slot[1][i]));
  storesRemaining-=v(s.filter[i][2]);
  assert.equal(v(s.retained_writes[i]),total([s.branch_slot[1][i],s.branch_slot[2][i],s.branch_slot[3][i]]));
  assert.equal(v(s.empty_scan[i][1]),v(s.branch_slot[2][i]));
 }
 assert.equal(storesRemaining,total(s.branches.slice(2)));
 for(let branch=0;branch<5;branch++)assert.equal(total(s.branch_slot[branch]),v(s.branches[branch]));
 let emptyRemaining=storesRemaining;
 for(let i=0;i<3;i++){assert.equal(total(s.empty_scan[i]),emptyRemaining);emptyRemaining-=v(s.empty_scan[i][1]);}
 assert.equal(emptyRemaining,v(s.branches[3])+v(s.branches[4]));
 assert.deepEqual(s.recent_writes.map(v),[0,2,3,4].map(i=>v(s.branches[i])));
 assert.equal(v(s.least_depth_comparisons),2n*emptyRemaining);
 names(l,['allocations','groups_allocated','capacity_groups_allocated','initialized_groups','max_groups','max_capacity_groups','generation_clears','wrap_clears','wrap_groups_cleared']);
 Object.values(l).forEach(v);assert(v(l.allocations)>0n);assert.equal(l.initialized_groups,l.groups_allocated);
 assert(l.capacity_groups_allocated>=l.groups_allocated&&l.max_capacity_groups>=l.max_groups&&l.groups_allocated>=l.max_groups&&l.capacity_groups_allocated>=l.max_capacity_groups);
 assert(v(l.wrap_groups_cleared)<=v(l.wrap_clears)*v(l.max_groups));
 return c;
}
