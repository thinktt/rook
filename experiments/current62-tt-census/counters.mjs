import assert from 'node:assert/strict';
const keys=(v,ks)=>assert.deepEqual(Object.keys(v).sort(),ks.slice().sort());
const n=x=>{assert(Number.isSafeInteger(x)&&x>=0);return BigInt(x);};
const sum=a=>a.reduce((s,x)=>s+n(x),0n);
const matrix=(a,r,c)=>{assert(Array.isArray(a)&&a.length===r);for(const row of a){assert(Array.isArray(row)&&row.length===c);row.forEach(n);}};
const vector=(a,k)=>{assert(Array.isArray(a)&&a.length===k);a.forEach(n);};
export function census(raw,pid){
 assert(raw.length<=65536&&raw.every(x=>x<128));
 const c=JSON.parse(raw.toString('ascii'));
 keys(c,['schema','pid','complete','overflow','invalid','probes','stores','lifecycle']);
 assert.equal(c.schema,'rook2-tt-probe-store-census-v1');assert.equal(c.pid,pid);
 assert.equal(c.complete,true);assert.equal(c.overflow,false);assert.equal(c.invalid,false);
 const p=c.probes,s=c.stores,l=c.lifecycle;
 keys(p,['calls','joint','filter','consider','mate_depth','returns_score','returns_no_score','read_line_hist','mate_write_line_hist','group_phase']);
 matrix(p.joint,4,8);matrix(p.filter,4,3);matrix(p.consider,4,3);matrix(p.mate_depth,4,2);
 for(const k of ['calls','returns_score','returns_no_score'])n(p[k]);
 vector(p.read_line_hist,3);vector(p.mate_write_line_hist,3);vector(p.group_phase,64);
 assert(n(p.calls)>0n);assert.equal(sum(p.joint.flat()),n(p.calls));assert.equal(sum(p.filter[3]),n(p.calls));
 const row=r=>sum(p.joint[r]);const col=k=>sum(p.joint.map(r=>r[k]));
 assert.equal(row(0),n(p.filter[3][0]));assert.equal(row(1),n(p.filter[3][1]));
 assert.equal(row(2),n(p.consider[3][2]));assert.equal(row(3),n(p.consider[3][0])+n(p.consider[3][1]));
 for(let r=0;r<3;r++)assert.equal(p.joint[r][0],0);
 for(let k=1;k<8;k++)assert.equal(p.joint[3][k],0);
 assert.equal(col(0),row(3));
 for(let i=0;i<4;i++){
  assert.equal(n(p.filter[i][2]),sum(p.consider[i]));
  assert.equal(n(p.consider[i][1]),sum(p.mate_depth[i]));
 }
 assert.equal(sum(p.filter[0]),n(p.calls)-row(3));
 for(let i=1;i<3;i++)assert.equal(sum(p.filter[i]),n(p.filter[i-1][0])+n(p.filter[i-1][1]));
 assert.equal(col(1),n(p.filter[2][0])+n(p.filter[2][1]));
 for(let i=0;i<3;i++){
  assert.equal(col(2+2*i),n(p.consider[i][2]));
  assert.equal(col(3+2*i),n(p.consider[i][0])+n(p.consider[i][1]));
 }
 const scores=p.consider.reduce((v,a)=>v+n(a[0])+n(a[1]),0n),mates=sum(p.mate_depth.flat());
 assert.equal(n(p.returns_score),scores);assert.equal(n(p.returns_no_score)+scores,n(p.calls));
 assert.equal(sum(p.read_line_hist),n(p.calls));assert.equal(p.read_line_hist[0],0);
 assert.equal(sum(p.mate_write_line_hist),n(p.calls));assert.equal(p.mate_write_line_hist[2],0);
 assert.equal(n(p.mate_write_line_hist[1]),mates);assert.equal(sum(p.group_phase),n(p.calls));
 for(let i=0;i<64;i++)if(i%4)assert.equal(p.group_phase[i],0);
 keys(s,['calls','filter','branches','branch_slot','retained_writes','recent_writes','empty_scan','least_depth_comparisons']);
 n(s.calls);n(s.least_depth_comparisons);matrix(s.filter,3,3);matrix(s.branch_slot,5,3);matrix(s.empty_scan,3,2);
 vector(s.branches,5);vector(s.retained_writes,3);vector(s.recent_writes,4);
 assert.equal(sum(s.branches),n(s.calls));assert.equal(sum(s.filter[0]),n(s.calls));
 for(let i=1;i<3;i++)assert.equal(sum(s.filter[i]),n(s.filter[i-1][0])+n(s.filter[i-1][1]));
 for(let b=0;b<5;b++)assert.equal(sum(s.branch_slot[b]),n(s.branches[b]));
 for(let i=0;i<3;i++){
  assert.equal(n(s.filter[i][2]),n(s.branch_slot[0][i])+n(s.branch_slot[1][i]));
  assert.equal(n(s.retained_writes[i]),n(s.branch_slot[1][i])+n(s.branch_slot[2][i])+n(s.branch_slot[3][i]));
  assert.equal(n(s.empty_scan[i][1]),n(s.branch_slot[2][i]));
 }
 assert.equal(sum(s.empty_scan[0]),n(s.branches[2])+n(s.branches[3])+n(s.branches[4]));
 for(let i=1;i<3;i++)assert.equal(sum(s.empty_scan[i]),n(s.empty_scan[i-1][0]));
 assert.equal(n(s.empty_scan[2][0]),n(s.branches[3])+n(s.branches[4]));
 assert.deepEqual(s.recent_writes,[s.branches[0],s.branches[2],s.branches[3],s.branches[4]]);
 assert.equal(n(s.least_depth_comparisons),2n*(n(s.branches[3])+n(s.branches[4])));
 keys(l,['allocations','groups_allocated','capacity_groups_allocated','initialized_groups','max_groups','max_capacity_groups','generation_clears','wrap_clears','wrap_groups_cleared']);
 Object.values(l).forEach(n);assert(n(l.allocations)>0n);assert.equal(l.initialized_groups,l.groups_allocated);
 assert(n(l.capacity_groups_allocated)>=n(l.groups_allocated));assert(n(l.max_capacity_groups)>=n(l.max_groups));
 assert(n(l.groups_allocated)>=n(l.max_groups));assert(n(l.capacity_groups_allocated)>=n(l.max_capacity_groups));
 assert(n(l.wrap_groups_cleared)<=n(l.wrap_clears)*n(l.max_groups));
 return c;
}
