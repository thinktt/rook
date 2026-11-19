// Offline use of the released checker; no engine execution.
import assert from 'node:assert/strict';
import {readFileSync,writeFileSync} from 'node:fs';
import {checkReplay,workloads,oracle} from '/home/legolas/king-spec/conformance/profiling/replay-check.mjs';
const directory=process.argv[2];const summary=JSON.parse(readFileSync(directory+'/summary.json','utf8'));
assert(summary.runs.length);
for(const row of summary.runs) checkReplay(row,workloads.cases.find(x=>x.id===row.case),oracle.cases.find(x=>x.id===row.case));
writeFileSync(directory+'/oracle-check.json',JSON.stringify({pass:true,requests:summary.runs.length,engineExecutions:0},null,2)+'\n');
