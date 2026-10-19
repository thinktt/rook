"""Independent offline four-witness raw review. Never imports/executes the collector."""
from pathlib import Path
import hashlib,json,re,stat,os
E=Path(__file__).resolve().parent
P=Path('/home/legolas/rook2/evidence/production-wire-directed-runner-preparation-20261019-01')
D=Path('/home/legolas/rook2/evidence/production-wire-directed-preparation-20261019-01')
O=P/'execution';H=[0,1,2,3,4,5,8,9,10,11,12,13]
load=lambda p:json.loads(Path(p).read_text())
def digest(data):return hashlib.sha256(data).hexdigest()
def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as f:
  for data in iter(lambda:f.read(65536),b''):h.update(data)
 return h.hexdigest()
def save(n,x):
 with (E/n).open('x') as f:json.dump(x,f,indent=2);f.write('\n')
def all_writes(case):
 if 'steps' in case:return [s['write'].encode('ascii') for s in case['steps'] if 'write' in s]
 return [('\n'.join(case['setup'])+'\n').encode('ascii'),case['atomic_write'].encode('ascii')]+[s['write'].encode('ascii') for s in case.get('after_abort_steps',case.get('after_move_steps',[])) if 'write' in s]
def main():
 assert sorted(os.sched_getaffinity(0))==H and os.environ['TMPDIR']=='/home/legolas/rook2-build-tmp'
 cases=load(P/'cases.json');plan=load(P/'plan.json');result=load(O/'result.json');terminal=load(O/'tool-terminal.json');closure=load(O/'input-closure.json')
 assert terminal['actual_tool_terminal_observed'] and terminal['exit_code']==0 and terminal['terminal_chunk_id']=='6cd582'
 assert result['complete'] and result['failure'] is None and result['all_owned_cleanup_confirmed'] and len(result['cases'])==4
 assert result['input_sha256']==closure and load(O/'request-plan.json')==cases==load(D/'cases.json')
 assert result['engine_sha256']==cases['artifact_sha256']==plan['engine_sha256']=='36251ecf12cfdc9437c9bfc5b7a571c1992471bee611cab024fc692ac79e91b2'
 assert result['source72_graph']==plan['source72_graph']=='e89dcb3315e4d8aaa5089ec445d0a7d0bda7f0928001c502c6343899a5195aa5'
 assert result['performance_measurement'] is False and result['protocol_qualification'] is False and result['no_retries']
 assert all(sha(p)==h for p,h in closure.items())
 runner=(P/'run.py').read_text();assert "len(data)>os.fpathconf(self.child.stdin.fileno(),'PC_PIPE_BUF')" in runner and "if atomic and n!=len(data)" in runner
 proof=load(plan['source_proof']);assert len(proof['native49_tools23'])==72
 source_checks=0
 for root in proof['verified_source_roots']:
  for rel,h in proof['native49_tools23'].items():assert sha(Path(root)/rel)==h;source_checks+=1
 assert source_checks==216
 image=Path(cases['artifact']);assert sha(image)==cases['artifact_sha256'] and image.stat().st_size==plan['engine_bytes'] and stat.S_IMODE(image.stat().st_mode)==0o555
 # Independently derive the graceful expected stream from released first-search observations.
 fixturepath=Path('/home/legolas/king-spec/conformance/fixtures/interrupted-sessions-v1.json')
 fx=next(c for c in load(fixturepath)['cases'] if c['id']=='interrupted-session-start-stop')
 fixture_events=fx['expected']['results'][0]['events'];generated=''
 for e in fixture_events:
  if e['type']=='post':
   assert 'O-O' not in e['pv'] and '=' not in e['pv']
   generated+=f"{e['depthToken']:5d} {e['evaluation']:+5d} {e['engineCentiseconds']:6d} {e['searchId']:9d} {e['pv']}\n"
  else:assert e['type']=='move';generated+='move '+e['move']+'\n'
 generated=generated.encode('ascii');assert generated==(P/'graceful-first-stop-expected.stdout').read_bytes()==(O/'graceful-first-stop-expected.stdout').read_bytes()
 assert digest(generated)==cases['cases'][3]['expect_exact_file_sha256']
 pins={str(p):sha(p) for p in [P/'run.py',P/'plan.json',P/'cases.json',P/'helper-pins.json',P/'execution-clearance.json',D/'cases.json',O/'request-plan.json',O/'result.json',O/'input-closure.json',O/'tool-terminal.json',fixturepath,P/'graceful-first-stop-expected.stdout',O/'graceful-first-stop-expected.stdout']}
 output=[];pids=[];total_raw=0;atomic_packets=[];quiet_evidence=[]
 for case,record in zip(cases['cases'],result['cases']):
  name=case['id'];assert name==record['case'];C=O/name;assert load(C/'result.json')==record
  assert record['complete'] and record['failure'] is None and record['disposition']=='directed_witness_pass'
  assert record['events_discarded_observed']==0 and record['retention_write_error'] is None
  streams={k:(C/(k+'.raw')).read_bytes() for k in ['stdin','stdout','stderr']};events_bytes=(C/'events.jsonl').read_bytes();assert events_bytes.endswith(b'\n') and len(events_bytes)==record['event_bytes']
  events=[json.loads(s) for s in events_bytes.splitlines()];assert all(events[i]['monotonic_ns']<=events[i+1]['monotonic_ns'] for i in range(len(events)-1))
  assert set(e['kind'] for e in events)<={'native-start','step','write-request','write','flush','read','expected-bytes','own-pipe-unread','fragment-consumed-quiet-begin','fragment-consumed-quiet-end','stdin-eof','pipe-eof','normal-exit'}
  native=record['native'];identity=record['identity'];pids.append(identity['pid'])
  assert identity['exe']==cases['artifact'] and identity['affinity']==H and identity['pgid']==identity['sid']==identity['pid'] and int(identity['start_ticks'])>0
  assert native['pid']==identity['pid'] and native['confirmed'] and native['launched'] and native['normal_exit'] and native['actual_return_observed']
  assert native['returncode']==native['exit_code']==0 and native['signal'] is None and not native['term_sent'] and not native['kill_sent']
  assert native['term_attempted_monotonic'] is native['kill_attempted_monotonic'] is None and native['unexpected_children']==[] and not native['ownership_unknown'] and native['errors']==[]
  assert 0<=native['cleanup_elapsed_s']<=plan['cleanup_seconds']
  assert abs(native['cleanup_elapsed_s']-(native['cleanup_completed_observed_monotonic']-native['cleanup_started_monotonic']))<1e-9
  starts=[e for e in events if e['kind']=='native-start'];ends=[e for e in events if e['kind']=='normal-exit'];assert len(starts)==len(ends)==1 and starts[0]['identity']==identity and starts[0]['argv']==cases['argv'] and ends[0]['returncode']==0
  assert cases['argv']==[cases['artifact'],'--work-clock=kingwcr']
  assert (ends[0]['monotonic_ns']-starts[0]['monotonic_ns'])/1e9<plan['lifetime_seconds']
  assert native['cleanup_completed_observed_monotonic']<=ends[0]['monotonic_ns']/1e9
  assert not streams['stderr'];assert len(streams['stdout'])<=plan['raw_stream_bytes'] and len(events_bytes)<=plan['event_bytes']
  writes=all_writes(case);assert b''.join(writes)==streams['stdin']
  for line in streams['stdin'].splitlines(keepends=True):
   assert line.endswith(b'\n') and line.isascii() and len(line)<=1023
   payload=line[:-1].removesuffix(b'\r');assert b'\r' not in payload and b'\0' not in payload and len(payload.split())<=40
  for step in case.get('steps',[]):
   if 'assert_record_bytes' in step:assert len(step['write'].encode())==step['assert_record_bytes']==1023
  for k,data in streams.items():
   meta=record['raw'][k];assert meta['path']==str(C/(k+'.raw')) and meta['observed']==meta['retained']==len(data) and meta['discarded_observed']==0 and meta['sha256']==digest(data)
   ev=[e for e in events if (e['kind']=='write' and k=='stdin') or (e['kind']=='read' and e['stream']==k)]
   pos=0
   for e in ev:
    n=e['actual_bytes'] if k=='stdin' else e['observed_bytes'];assert e['offset']==pos and e['retained_bytes']==n and e['sha256']==digest(data[pos:pos+n]);pos+=n
   assert pos==len(data);total_raw+=len(data)
  requests=[(i,e) for i,e in enumerate(events) if e['kind']=='write-request'];assert len(requests)==len(writes)
  write_ends=[]
  for j,((ix,e),data) in enumerate(zip(requests,writes)):
   stop=requests[j+1][0] if j+1<len(requests) else len(events);chunk=[x for x in events[ix+1:stop] if x['kind']=='write'];flush=[x for x in events[ix+1:stop] if x['kind']=='flush']
   assert e['bytes']==len(data) and e['sha256']==digest(data) and sum(x['actual_bytes'] for x in chunk)==len(data) and len(flush)==1 and flush[0]['stream']=='stdin'
   assert e['monotonic_ns']<=chunk[0]['monotonic_ns']<=chunk[-1]['monotonic_ns']<flush[0]['monotonic_ns'];write_ends.append(flush[0]['monotonic_ns'])
   if e['atomic']:
    assert data==case['atomic_write'].encode() and len(chunk)==1 and chunk[0]['actual_bytes']==len(data) and len(data)<=512
    atomic_packets.append(dict(case=name,bytes=len(data),actual_write_calls=1,request_event=ix,numeric_PC_PIPE_BUF_not_recorded=True,runtime_fpathconf_guard_bound_by_frozen_runner=True))
  assert [e['atomic'] for _,e in requests]==([False,True]+[False]*(len(writes)-2) if 'atomic_write' in case else [False]*len(writes))
  # Independently build the complete expected byte stream and expected-consumption segments.
  status_rows=[];segments=[]
  if 'steps' in case:
   expected=b''
   for step in case['steps']:
    value=step.get('expect_exact',step.get('expect_exact_before_next_write_or_eof'))
    if value is not None:segments.append((len(expected),value.encode()));expected+=value.encode()
  else:
   expected=case['setup_expected_stdout'].encode();segments=[(0,expected)]
   if 'expect_order' in case:
    rest=streams['stdout'][len(expected):];actual_lines=rest.splitlines(keepends=True);assert len(actual_lines)>=3;last=-1
    for line,wanted in zip(actual_lines[:2],case['expect_order'][:2]):
     m=re.fullmatch(rb'stat01: +(-?\d+) +(\d+) +(-?\d+) +(\d+) +(\d+)(?: (.*))?\n',line);assert m
     cs,sid,depth,remaining,total=map(int,m.groups()[:5]);pv=m[6].decode() if m[6] is not None else None
     canonical=f'stat01: {cs:>6} {sid:>9} {depth:>5} {remaining:>3} {total:>3}'+(' '+pv if pv is not None else '')+'\n';assert line==canonical.encode()
     assert sid==wanted['searchId'] and total==wanted['total'] and wanted['remaining_range_inclusive'][0]<=remaining<=wanted['remaining_range_inclusive'][1] and cs>=last;last=cs
     assert pv is None or (pv and ' '.join(pv.split(' '))==pv and all(pv.split(' ')))
     status_rows.append(dict(search_id=sid,elapsed_cs=cs,depth=depth,remaining=remaining,total=total,path=pv,line_sha256=digest(line)));expected+=line
    abort=case['expect_order'][2]['exact'].encode();segments.append((len(expected),abort));expected+=abort
    assert record['checks']==[dict(kind='observed-poll',search_id=r['search_id'],line_sha256=r['line_sha256']) for r in status_rows]
    after=case['after_abort_steps']
   else:
    segments.append((len(expected),generated));expected+=generated;after=case['after_move_steps'];assert record['checks']==[]
   for step in after:
    if 'expect_exact' in step:segments.append((len(expected),step['expect_exact'].encode()));expected+=step['expect_exact'].encode()
  assert streams['stdout']==expected and streams['stdout'].isascii() and b'\r' not in streams['stdout']
  acks=[(i,e) for i,e in enumerate(events) if e['kind']=='expected-bytes'];assert len(acks)==len(segments)
  for (ix,e),(offset,data) in zip(acks,segments):
   assert e['bytes']==len(data) and e['sha256']==digest(data)
   available=sum(x['retained_bytes'] for x in events[:ix] if x['kind']=='read' and x['stream']=='stdout');assert available>=offset+len(data)
  # Every response claimed before a next host write has an actual consumption timestamp.
  if 'steps' in case:
   ackno=0
   for j,step in enumerate(case['steps']):
    if 'expect_exact' in step or 'expect_exact_before_next_write_or_eof' in step:
     t=acks[ackno][1]['monotonic_ns'];assert t>write_ends[j]
     if j+1<len(requests):assert t<requests[j+1][1]['monotonic_ns']
     ackno+=1
  else:
   assert acks[0][1]['monotonic_ns']<requests[1][1]['monotonic_ns']
   assert acks[1][1]['monotonic_ns']<requests[2][1]['monotonic_ns']
   for j,ack in enumerate(acks[2:],2):assert ack[1]['monotonic_ns']<requests[j+1][1]['monotonic_ns']
  if case['id']=='boundary-lf-fragment-idle-eof':
   begins=[(i,e) for i,e in enumerate(events) if e['kind']=='fragment-consumed-quiet-begin'];quietends=[(i,e) for i,e in enumerate(events) if e['kind']=='fragment-consumed-quiet-end'];assert len(begins)==len(quietends)==2
   for j,((bi,be),(ei,en)) in enumerate(zip(begins,quietends)):
    assert be['duration_ms']==100 and en['monotonic_ns']-be['monotonic_ns']>=100000000
    assert events[bi-1]['kind']=='own-pipe-unread' and events[bi-1]['bytes']==0 and requests[j+2][1]['monotonic_ns']<be['monotonic_ns']<en['monotonic_ns']<requests[j+3][1]['monotonic_ns']
    assert not any(z['kind']=='read' and z['observed_bytes'] for z in events[bi:ei+1])
    quiet_evidence.append(dict(interval=j+1,FIONREAD_bytes=0,quiet_ns=en['monotonic_ns']-be['monotonic_ns'],next_fragment_after_quiet=True))
  else:assert not any(e['kind'].startswith('fragment-') or e['kind']=='own-pipe-unread' for e in events)
  eof=[e for e in events if e['kind']=='stdin-eof'];assert len(eof)==(1 if 'eof' in name else 0)
  assert ends[0]['stdin_kept_open']==('eof' not in name)
  assert sorted(e['stream'] for e in events if e['kind']=='pipe-eof')==['stderr','stdout']
  assert all(e['monotonic_ns']<ends[0]['monotonic_ns'] for e in events if e['kind']=='pipe-eof')
  for p in C.iterdir():
   if p.is_file():pins[str(p)]=sha(p)
  output.append(dict(case=name,complete=True,pid=identity['pid'],exit_code=0,signal=None,raw_bytes={k:len(v) for k,v in streams.items()},events=len(events),input_packets=len(writes),status_rows=status_rows,all_raw_chunks_contiguous_and_hashed=True,all_expected_bytes_match=True,cleanup_confirmed_from_closed_return_and_pipe_group_observations=True))
 assert len(set(pids))==4 and len(atomic_packets)==2 and len(quiet_evidence)==2
 assert all(sha(p)==h for p,h in closure.items()) and all(sha(p)==h for p,h in pins.items())
 save('input-pins.json',dict(collector_input_closure=closure,reviewed_files=pins,all_inputs_unchanged=True,source_member_rechecks=216))
 report=dict(complete=True,failure=None,collector_actual_terminal='6cd582/0',exact_artifact_sha256=cases['artifact_sha256'],cases=output,fresh_native_processes=4,unique_pids=pids,raw_bytes=total_raw,atomic_packets=atomic_packets,fragment_quiet_evidence=quiet_evidence,collector_input_pins_rechecked=len(closure),source_member_rechecks=source_checks,all_inputs_unchanged=True,no_native_or_runner_import_or_execution=True,scope='Finite four production-wire witnesses only; no complete protocol/performance qualification.',limitations=['Numeric runtime PC_PIPE_BUF result is not logged; the frozen executed guard plus single full22/11B writes and POSIX minimum512B support the bound, not a fabricated measured value.','FIONREAD is own-pipe occupancy evidence and quiet intervals are observed schedules, not all possible transport timing.','Fifth force has no public terminalN assertion.','Move/idle followups are finite public effects, not complete hidden-state identity or universal detached-child cleanup.'])
 save('independent-verification.json',report)
 print(json.dumps({k:v for k,v in report.items() if k not in ['cases','atomic_packets','fragment_quiet_evidence','limitations']}))
if __name__=='__main__':
 try:main()
 except BaseException as e:save('failure.json',dict(complete=False,error=repr(e)));raise
