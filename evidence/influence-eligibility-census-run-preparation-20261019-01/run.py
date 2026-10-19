#!/usr/bin/env python3
"""Two fixed diagnostic lifetimes; source/build/schema/parent admission required."""
from pathlib import Path
import hashlib,json,os,subprocess,tarfile
P=Path(__file__).resolve().parent
H=[0,1,2,3,4,5,8,9,10,11,12,13]
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
load=lambda p:json.loads(Path(p).read_text())
def write(p,j):
 with Path(p).open('x') as f:json.dump(j,f,indent=2);f.write('\n')
def cpu15():
 rows=[line.split()[1:] for line in Path('/proc/stat').read_text().splitlines() if line.startswith('cpu15 ')]
 assert len(rows)==1
 return list(map(int,rows[0]))
def main():
 plan=load(P/'plan.json')
 assert plan['launch'] is True and plan['all_native_and_timing_jobs_closed'] is True
 assert plan['cases']==['profile-35','profile-08'] and plan['lifetimes']==2 and plan['repetitions_per_case']==1 and plan['no_retries'] and plan['no_sample_deletion']
 assert sorted(os.sched_getaffinity(0))==H and os.environ.get('TMPDIR')=='/home/legolas/rook2-build-tmp'
 assert os.environ.get('PATH')=='/usr/bin:/bin'
 assert not any(os.environ.get(k) for k in ['LD_PRELOAD','LD_LIBRARY_PATH','LLVM_PROFILE_FILE','NODE_OPTIONS',plan['env_key']])
 assert plan['census_schema_contract'] and plan['census_source_review'] and plan['parent_review']
 pins=dict(plan['known_inputs'])
 for field in ['parent_review','census_source_review','source_manifest','build_terminal']:
  row=plan[field];assert row and sha(row['path'])==row['sha256'];pins[row['path']]=row['sha256']
 for field in ['parent_review','census_source_review']:assert load(plan[field]['path'])['complete'] is True
 review=load(plan['parent_review']['path']);assert review['allow_engine_execution'] is True and review['cases']==plan['cases'] and review['engine_sha256']==plan['engine_sha256']
 terminal=load(plan['build_terminal']['path']);assert terminal['actual_tool_terminal_observed'] and terminal['exit_code']==0 and (terminal.get('terminal_chunk_id') or terminal.get('chunk_id'))
 assert plan['expected_script_sha256'] and all(sha(P/n)==h for n,h in plan['expected_script_sha256'].items())
 for n,h in plan['expected_script_sha256'].items():pins[str(P/n)]=h
 for name in ['engine','build_receipt','source_archive']:
  assert plan[name] and plan[name+'_sha256'];pins[plan[name]]=plan[name+'_sha256']
 r=load(plan['build_receipt']);base=load(plan['compiler_baseline_receipt'])
 assert r['mode']=='generic' and r['pgo']['mode']=='none' and r['cargo_exit_code']==0
 assert r['source_identity_unchanged'] and r['tool_identity_unchanged'] and r['cargo_config_unchanged']
 assert r['cargo_config_sha256_before']==r['cargo_config_sha256_after']
 assert Path(plan['engine']).stat().st_mode & 0o777==0o555
 assert r['binary_output']['sha256']==plan['engine_sha256'] and r['rust_flags']==plan['expected_rust_flags']
 for field in ['toolchain','target_triple','target_cpu','jobs','cargo_config_sha256_before']:assert r[field]==base[field],field
 assert r['target_cpu']=='x86-64' and not any('target-feature' in flag or 'profile-use' in flag or 'profile-generate' in flag for flag in r['rust_flags'])
 assert r['tool_sha256_before']==base['tool_sha256_before'] and r['rust_flags']==base['rust_flags']
 assert r['source_sha256_before']==r['source_sha256_after']==plan['source_sha256'] and r['tool_sha256_before']==r['tool_sha256_after']==plan['tool_source_sha256']
 counts=plan['source_counts'];assert len(plan['source_sha256'])==counts['native'] and len(plan['tool_source_sha256'])==counts['tools']==23 and counts['total']==counts['native']+23
 expected=plan['source_sha256']|plan['tool_source_sha256']
 assert plan['census_schema_contract']['source_sha256']==expected[plan['census_source_file']] and plan['census_schema_contract']['all_work_fields']
 manifest=load(plan['source_manifest']['path']);assert manifest['schema']=='relative-path-sha256-v1' and manifest['graph_sha256']==plan['source_graph_sha256'] and manifest['files']==expected
 with tarfile.open(plan['source_archive'],'r:gz') as tar:
  members=tar.getmembers();assert len(members)==len(expected) and len({m.name for m in members})==len(members)
  assert all(m.isfile() and not m.name.startswith('/') and '..' not in Path(m.name).parts and m.name in expected for m in members)
  assert {m.name:hashlib.sha256(tar.extractfile(m).read()).hexdigest() for m in members}==expected
 for name,h in expected.items():pins[str(Path(plan['build_receipt']).parent/'source-before'/name)]=h
 pins[str(P/'plan.json')]=sha(P/'plan.json')
 assert all(sha(p)==h for p,h in pins.items())
 reference=load(plan['strict_reference']);assert reference['status']=='pass'
 output=Path(plan['output']);assert not output.exists();output.mkdir()
 write(output/'plan.json',plan);write(output/'input-closure.json',pins)
 result=dict(complete=False,failure=None,cases=[],attempted_cases=0,engine_runs=None,performance_claim=False)
 before=cpu15();write(output/'cpu15-before.json',before)
 try:
  for case in plan['cases']:
   d=output/case;d.mkdir();census=d/'census.json';assert not census.exists()
   input_case=next(x for x in load('/home/legolas/king-spec/conformance/profiling/workloads.json')['cases'] if x['id']==case)
   expected_case=next(x for x in load('/home/legolas/king-spec/conformance/profiling/replay-oracle.json')['cases'] if x['id']==case)
   write(d/'input-expected.json',dict(input=input_case,expected=expected_case))
   env=dict(os.environ);env[plan['env_key']]=str(census.resolve())
   argv=['/usr/bin/node','/home/legolas/king-spec/conformance/profiling/replay-check.mjs','--case',case,'--','/usr/bin/python3','/home/legolas/rook2/tools/account_native.py','--engine',plan['engine'],'--record',str((d/'native.json').resolve()),'--known-single-process']
   with (d/'checker.stdout').open('xb') as out,(d/'checker.stderr').open('xb') as err:
    child=subprocess.Popen(argv,stdout=out,stderr=err,env=env);code=child.wait()
   command=dict(argv=argv,pid=child.pid,actual_child_return_observed=True,exit_code=code,census_env={plan['env_key']:str(census.resolve())})
   write(d/'command.json',command);result['attempted_cases']+=1
   assert code==0 and not (d/'checker.stderr').stat().st_size
   report=load(d/'checker.stdout');assert report['status']=='pass' and report['selectedCases']==[case] and len(report['results'])==1
   row=report['results'][0];native=load(d/'native.json');ref=next(x for x in reference['results'] if x['case']==case)
   assert row['complete'] and row['error'] is None and not row['truncated'] and not row.get('cleanupUnconfirmed',False) and row['discardedObservedBytes']==0 and row['exit']==dict(code=0,signal=None)
   assert row['stdout']==ref['stdout'] and row['stderr']==ref['stderr']==''
   assert native['failure'] is None and native['native_exit_code']==0 and native['native_wait_status']==0 and native['native_pid']!=row['pid'] and native['supervisor_pid']==row['pid']
   assert native['native_pre_exec']['affinity']==native['native_post_exec']['affinity']==[14] and native['supervisor_affinity']==H and native['native_post_exec']['tasks']==[str(native['native_pid'])]
   assert native['engine_sha256_before']==native['engine_sha256_after']==plan['engine_sha256'] and census.is_file()
   assert census.stat().st_size<=plan['census_file_cap_bytes']
   aggregate=load(census);assert aggregate['schema']==plan['census_schema'] and aggregate['native_pid']==native['native_pid'] and aggregate['complete'] and aggregate['engine_success']
   for stream in ['stdout','stderr']:(d/(stream+'.raw')).write_bytes(row[stream].encode())
   result['cases'].append(dict(case=case,native_pid=native['native_pid'],native_exit=0,census_sha256=sha(census),checker_sha256=sha(d/'checker.stdout'),native_receipt_sha256=sha(d/'native.json'),stdout_sha256=sha(d/'stdout.raw'),stderr_sha256=sha(d/'stderr.raw')))
  assert result['attempted_cases']==2 and len({r['native_pid'] for r in result['cases']})==2
  result['engine_runs']=2
  after=cpu15();write(output/'cpu15-after.json',after)
  delta=[b-a for a,b in zip(before,after)];assert all(x>=0 for x in delta)
  busy=sum(delta[i] for i in [0,1,2,5,6,7]) # Disclosure only: OS activity does not invalidate counts.
  result['cpu15_point_delta']=delta;result['cpu15_point_nonidle_ticks']=busy
  assert all(sha(p)==h for p,h in pins.items())
  result['complete']=True
 except BaseException as error:result['failure']=repr(error);raise
 finally:write(output/'result.json',result)
 print(json.dumps(dict(complete=True,cases=plan['cases'],engine_runs=2,performance_claim=False)))
if __name__=='__main__':main()
