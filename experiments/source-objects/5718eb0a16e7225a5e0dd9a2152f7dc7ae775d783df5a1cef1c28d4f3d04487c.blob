// Independent offline consumption of every captured game/continuity byte.
import assert from 'node:assert/strict';
import {readFileSync, writeFileSync, readdirSync} from 'node:fs';
import {createHash} from 'node:crypto';
import {join} from 'node:path';
import {semanticPost, validateFixture} from '/home/legolas/king-spec/conformance/gate-replay/run.mjs';
const directory=process.argv[2];
assert(directory?.startsWith('/'));
const controls=process.argv[3];
assert(controls?.startsWith('/'));
const kit='/home/legolas/king-spec/conformance/gate-replay';
const load=p=>JSON.parse(readFileSync(p));
const hash=data=>createHash('sha256').update(data).digest('hex');
const fixture=load(join(kit,'accepted-games-v1.json'));validateFixture(fixture);
const binding=load(join(directory,'binding.json'));
const approval=load('/home/legolas/rook2/evidence/bitplane-pin-summary-pregate-preparation-20261020-01/pregate-clearance.json');
assert.equal(approval.authorized,true);
assert.equal(binding.engine_sha256,approval.ordinary_artifact.sha256);
assert.equal(hash(readFileSync(approval.ordinary_artifact.image)),binding.engine_sha256);
for(const [path,expected] of Object.entries(binding.before))assert.equal(hash(readFileSync(path)),expected,path);
const plan=load(join(kit,'continuous-switching-v1.json'));
const continuous=plan.segments.map(segment=>{
  const game=fixture.games.find(g=>g.id===segment.game);assert(game);
  return {...game,plies:game.plies.slice(0,segment.searches)};
});
const checks=[];
function check(name,games){
  const rawDir=join(directory,name+'.raw');
  const receipt=load(join(rawDir,'receipt.json'));
  assert.equal(receipt.failure,null);assert(receipt.native);
  assert.deepEqual(receipt.exit,{code:0,signal:null});
  assert(receipt.native.tasks.length>0);
  for(const task of receipt.native.tasks)assert.equal(task.affinity,'0-5,8-13');
  const streams={};
  for(const stream of ['stdin','stdout','stderr']){
    const data=readFileSync(join(rawDir,stream+'.raw'));
    assert.equal(hash(data),receipt.raw[stream].sha256);
    assert.equal(data.length,receipt.raw[stream].bytes);
    assert.equal(data.length,receipt.raw[stream].observedBytes);
    assert(data.every(b=>b<=127),'nonASCII wire byte');
    streams[stream]=data.toString('ascii');
  }
  assert(streams.stdout.endsWith('\n'));assert(streams.stderr.endsWith('\n'));
  const stdout=streams.stdout.split('\n');stdout.pop();
  const stderr=streams.stderr.split('\n');stderr.pop();
  let cursor=0,searches=0;const input=[],traces=[];
  function take(expected){assert.equal(stdout[cursor++],expected,`${name} record${cursor}`);}
  for(const game of games){
    input.push('xboard','new','force','post','easy','level 0 5 0',...game.initialMoves,'cm_parm default');
    take('cm_parm default');
    for(const row of game.plies){
      const commands=game.personalityCommands[row.personality];
      input.push('force',...commands,`king_seed ${row.seed}`,`time ${row.clockCentiseconds}`,`otim ${row.clockCentiseconds}`,'go');
      for(const line of commands)take(line);
      take(`king_seed ${row.seed}`);
      for(const post of row.expected.posts)assert.deepEqual(semanticPost(stdout[cursor++]),post,`${name} search${searches}`);
      take('move '+row.expected.move);
      if(row.expected.result!==null)take(row.expected.result);
      traces.push(`KING_SEARCH_SEED seed=${row.seed}`);searches++;
    }
  }
  input.push('quit');
  assert.equal(streams.stdin,input.join('\n')+'\n',name+' complete input');
  assert.equal(cursor,stdout.length,name+' complete stdout');
  assert.deepEqual(stderr,traces,name+' complete stderr');
  const report=load(join(directory,name+'.json'));assert.equal(report.pass,true);
  assert.equal(report.executableSha256,binding.engine_sha256);
  assert.equal(report.processes.length,1);assert.equal(report.processes[0].code,0);
  assert.equal(report.processes[0].stdoutRecords,stdout.length);
  assert.equal(report.processes[0].stderrRecords,stderr.length);
  assert.equal(report.processes[0].outputBytes,receipt.raw.stdout.bytes+receipt.raw.stderr.bytes);
  checks.push({name,games:games.length,searches,stdoutRecords:stdout.length,stderrRecords:stderr.length});
}
for(const game of fixture.games)check(game.id,[game]);check('continuous',continuous);
assert.equal(checks.slice(0,12).reduce((n,x)=>n+x.searches,0),632);
assert.equal(checks.at(-1).searches,8);
const combined=load(join(directory,'combined.json'));
assert(combined.pass&&combined.completeFocusedReplay);
assert.equal(load(join(controls,'seed-command-controls.terminal.json')).exit_code,0);
assert.equal(load(join(controls,'seed-persistence-controls.terminal.json')).exit_code,0);
const outcome=load(join(controls,'outcome.json'));assert(outcome.complete);
assert.equal(outcome.engine_sha256,binding.engine_sha256);
const persistence=load(join(controls,'seed-persistence-controls.raw/receipt.json'));
assert.equal(persistence.failure,null);assert(persistence.native);
assert.deepEqual(persistence.exit,{code:0,signal:null});
for(const row of Object.values(persistence.raw)){
  assert.equal(hash(readFileSync(row.path)),row.sha256);
  assert.equal(row.bytes,row.observedBytes);
}
// Independently consume all required seed-control wire bytes, not just checker exits.
const readRaw=(dir)=>{
 const r=load(join(dir,'receipt.json')),streams={};
 for(const n of ['stdin','stdout','stderr']){const b=readFileSync(join(dir,n+'.raw'));assert.equal(hash(b),r.raw[n].sha256);assert.equal(b.length,r.raw[n].bytes);streams[n]=b.toString('utf8');}
 return {r,...streams};
};
const controlCases=[
 {input:'xboard\nking_seed 0\nking_seed 4294967295\nking_seed 0xffffffff\nking_seed 010\nking_seed +7\nking_seed -0\n\tking_seed\t0X10  \nking_seed 31\r\nquit\n',out:'king_seed 0\nking_seed 4294967295\nking_seed 4294967295\nking_seed 8\nking_seed 7\nking_seed 0\nking_seed 16\nking_seed 31\n',err:'',exit:0},
 ...['08','4294967296','-1','7 extra','1.0','+','abc',''].map(v=>({input:`king_seed ${v}\n`,out:'',err:'king-native: invalid diagnostic seed command\n',exit:1})),
 {input:'king_seed\nquit\n',out:'Error (unknown command): king_seed\n',err:'',exit:0},
 {input:'king_seed 7\nquit\n',out:'Error (unknown command): king_seed\n',err:'',exit:0,ordinary:true}];
assert.equal(readdirSync(join(controls,'seed-command-controls.raw')).length,11);
for(const [i,c] of controlCases.entries()){
 const b=readRaw(join(controls,'seed-command-controls.raw',String(i).padStart(2,'0')));
 assert.equal(b.stdin,c.input);assert.equal(b.stdout,c.out);assert.equal(b.stderr,c.err);
 assert.equal(b.r.status,c.exit);assert.equal(b.r.signal,null);assert.equal(b.r.error,null);
 assert.equal(b.r.imageBefore,binding.engine_sha256);assert.equal(b.r.imageAfter,binding.engine_sha256);
 assert.deepEqual(b.r.argv,[receiptImage(),...(c.ordinary?[]:['--diagnostic-seed-command'])]);assert(b.r.pid>0);
}
function receiptImage(){return binding.image;}
const pc=readRaw(join(controls,'seed-persistence-controls.raw'));
const setup=['xboard','new','force','nopost','easy','level 0 5 0','cm_parm default md=1 rnd=0'];
const search=['time 18100','otim 18100','go'];
assert.equal(pc.stdin,[...setup,'king_seed 3735928559',...search,...setup,...search,...setup,'king_seed 17',...search,'quit'].join('\n')+'\n');
assert.equal(pc.stderr,'KING_SEARCH_SEED seed=3735928559\nKING_SEARCH_SEED seed=3735928559\nKING_SEARCH_SEED seed=17\n');
assert(pc.stdout.endsWith('\n'));const pl=pc.stdout.split('\n');assert.equal(pl.pop(),'');assert.equal(pl.length,8);
assert.equal(pl[0],'cm_parm default md=1 rnd=0');assert.equal(pl[1],'king_seed 3735928559');
assert.equal(pl[3],'cm_parm default md=1 rnd=0');assert.equal(pl[5],'cm_parm default md=1 rnd=0');assert.equal(pl[6],'king_seed 17');
for(const i of [2,4,7])assert.match(pl[i],/^move [a-h][1-8][a-h][1-8][qrbn]?$/i);
const result={complete:true,checks,independentGames:12,independentSearches:632,continuousSearches:8,
  engineSha256:binding.engine_sha256,reconcilerSha256:hash(readFileSync(new URL(import.meta.url))),
  controls,requiredControlChildren:11,persistenceSearches:3,optionalSequenceConflict:false,
  scope:'Every game/continuous input/output byte consumed against released fixture; required seed controls separately checked by original runners with optional unsupported sequence check omitted. Untimed exact own-PGO image only; no performance transfer.'};
writeFileSync(join(directory,'independent-raw-reconciliation.json'),JSON.stringify(result,null,2)+'\n',{flag:'wx'});
console.log(JSON.stringify(result));
