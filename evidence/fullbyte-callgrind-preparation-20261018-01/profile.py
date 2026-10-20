"""Future fixed two-case diagnostic simulation. Inert until main/parent launch."""
from pathlib import Path
import argparse,hashlib,json,os,subprocess,sys,tarfile
HERE=Path(__file__).resolve().parent
PLAN=json.loads((HERE/'plan.json').read_text())
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
load=lambda p:json.loads(Path(p).read_text())
def write(path,value):
 with Path(path).open('x') as f:json.dump(value,f,indent=2);f.write('\n')
def main():
 a=argparse.ArgumentParser();a.add_argument('--clearance',type=Path,default=HERE/'execution-clearance.json');args=a.parse_args()
 clearance=load(args.clearance);assert clearance['profile'] is True and clearance['all_native_and_CPU_windows_closed'] is True
 review=clearance['parent_review'];assert review and sha(review['path'])==review['sha256']
 assert all(sha(path)==h for path,h in load(HERE/'input-pins.json').items())
 assert all(sha(HERE/name)==h for name,h in load(HERE/'helper-pins.json').items())
 assert sorted(os.sched_getaffinity(0))==PLAN['helper_affinity'] and os.environ.get('TMPDIR')=='/home/legolas/rook2-build-tmp'
 assert not os.environ.get('LLVM_PROFILE_FILE') and not os.environ.get('LD_PRELOAD') and not os.environ.get('LD_LIBRARY_PATH') and not os.environ.get('NODE_OPTIONS')
 out=Path(PLAN['output']);assert not out.exists()
 engine=Path(PLAN['engine']);build=load(PLAN['build_receipt']);source=Path(PLAN['source_root']);compiled=Path(build['crate']);assert str(compiled)==PLAN['compiled_source_root'];prefix=Path(PLAN['valgrind_prefix']);spec=Path(PLAN['spec'])
 inputs={Path(path):digest for path,digest in PLAN['public_input_sha256'].items()}
 inputs.update({engine:PLAN['engine_sha256'],Path(PLAN['build_receipt']):PLAN['build_receipt_sha256'],Path(PLAN['source_archive']):PLAN['source_archive_sha256'],Path(PLAN['strict_reference']):PLAN['strict_reference_sha256']})
 inputs.update({source/path:digest for path,digest in (PLAN['source_sha256']|PLAN['tool_source_sha256']).items()})
 # DWARF can retain absolute compilation paths. Bind BOTH possible source
 # roots; archived cwd/include alone does not redirect absolute lookups.
 inputs.update({compiled/path:digest for path,digest in (PLAN['source_sha256']|PLAN['tool_source_sha256']).items()})
 inputs.update({Path(PLAN['current_source_root'])/path:digest for path,digest in (PLAN['source_sha256']|PLAN['tool_source_sha256']).items()})
 inputs.update({Path(path):h for path,h in PLAN['expected_runtime_sha256'].items()})
 inputs.update({Path(path):h for path,h in load(HERE/'input-pins.json').items()})
 inputs.update({Path(PLAN['pgo_proof']):PLAN['pgo_proof_sha256']})
 inputs.update({Path(path):h for path,h in PLAN['pgo_input_sha256'].items()})
 assert all(sha(path)==digest for path,digest in inputs.items())
 assert build['binary_output']['sha256']==PLAN['engine_sha256'] and build['pgo']['mode']=='profile-use' and build['source_sha256_before']==build['source_sha256_after']==PLAN['source_sha256']
 assert build['tool_sha256_before']==build['tool_sha256_after']==PLAN['tool_source_sha256']
 proof=load(PLAN['pgo_proof']);assert all(proof[k] is True for k in ['complete','own_profile_only','strict_training54','fresh_strict54','wire8_searches24'])
 assert proof['variants']['full-byte-pair-relations']['artifact_sha256']==PLAN['engine_sha256']
 assert proof['variants']['full-byte-pair-relations']['source_sha256']==PLAN['source_sha256']
 assert proof['variants']['full-byte-pair-relations']['profile_sha256']==PLAN['pgo_profile_sha256']
 assert build['pgo']['input_sha256_before']==build['pgo']['input_sha256_after']==PLAN['pgo_input_sha256'] and build['pgo']['inputs_unchanged']
 with tarfile.open(PLAN['source_archive'],'r:gz') as tar:
  members={m.name:hashlib.sha256(tar.extractfile(m).read()).hexdigest() for m in tar}
 assert members==PLAN['source_sha256']|PLAN['tool_source_sha256']
 tools=[prefix/'bin/valgrind',prefix/'bin/callgrind_annotate',prefix/'libexec/valgrind/callgrind-amd64-linux']
 tools+=sorted((prefix/'libexec/valgrind').glob('vgpreload*callgrind*'))+sorted((prefix/'libexec/valgrind').glob('vgpreload_core*'))
 assert len(tools)>=4 and all(p.is_file() for p in tools)
 for p in tools+[HERE/'profile.py',HERE/'verify.py',HERE/'recheck.mjs',HERE/'plan.json',args.clearance,HERE/'helper-pins.json',HERE/'input-pins.json',Path(review['path']),Path(PLAN['node']).resolve()]:inputs[p]=sha(p)
 before={str(p):digest for p,digest in inputs.items()};out.mkdir()
 env=dict(os.environ,VALGRIND_LIB=str(prefix/'libexec/valgrind'))
 commands=[]
 def run(argv,stem,cwd=source,expected_exit=0,output_stream='stdout'):
  command=['/usr/bin/taskset','-c','0-5,8-13',*map(str,argv)]
  with (out/(stem+'.stdout')).open('xb') as x,(out/(stem+'.stderr')).open('xb') as y:r=subprocess.run(command,cwd=cwd,env=env,stdout=x,stderr=y)
  commands.append(dict(stem=stem,argv=command,exit_code=r.returncode,expected_exit_code=expected_exit,actual_child_return_observed=True,output_sha256={stream:sha(out/(stem+'.'+stream)) for stream in ['stdout','stderr']}));write(out/(stem+'-child-terminal.json'),commands[-1]);assert r.returncode==expected_exit,stem
  return load(out/(stem+'.stdout')) if stem.endswith('-oracle') else (out/(stem+'.'+output_stream)).read_text()
 result=dict(complete=False,event_scope=PLAN['event_scope'],cases={},failure=None)
 try:
  version=run([str(prefix/'bin/valgrind'),'--version'],'valgrind-version');assert 'valgrind-3.24.0' in version
  # Installed public annotator uses Perl die() for --version: expected
  # stderr and exit255, unlike actual annotation commands which require0.
  annotate_version=run([str(prefix/'bin/callgrind_annotate'),'--version'],'annotate-version',expected_exit=255,output_stream='stderr');assert annotate_version=='callgrind_annotate-3.24.0\n' and not (out/'annotate-version.stdout').stat().st_size
  reference=load(PLAN['strict_reference']);assert reference['status']=='pass'
  expected_inputs=load(spec/'workloads.json');expected_outputs=load(spec/'replay-oracle.json')
  write(out/'input-closure.json',before)
  for case in PLAN['cases']:
   command=[PLAN['node'],str(spec/'replay-check.mjs'),'--case',case,'--','/usr/bin/taskset','-c','14','/usr/bin/env','VALGRIND_LIB='+env['VALGRIND_LIB'],str(prefix/'bin/valgrind'),'--tool=callgrind','--cache-sim=no','--branch-sim=no','--callgrind-out-file='+str(out/(case+'.callgrind')),'--log-file='+str(out/(case+'.log')),str(engine)]
   report=run(command,case+'-oracle');assert report['status']=='pass' and report['selectedCases']==[case] and len(report['results'])==1
   row=report['results'][0];ref=next(x for x in reference['results'] if x['case']==case)
   assert row['status']=='pass' and row['complete'] and not row['truncated'] and row['error'] is None and row['exit']==dict(code=0,signal=None) and not row.get('cleanupUnconfirmed',False) and row['discardedObservedBytes']==0
   assert row['stdout'].encode()==ref['stdout'].encode() and row['stderr'].encode()==ref['stderr'].encode()==b''
   assert not (out/(case+'-oracle.stderr')).stat().st_size
   (out/(case+'-stdout.raw')).write_bytes(row['stdout'].encode());(out/(case+'-stderr.raw')).write_bytes(row['stderr'].encode())
   write(out/(case+'-input-expected.json'),dict(input=next(x for x in expected_inputs['cases'] if x['id']==case),expected=next(x for x in expected_outputs['cases'] if x['id']==case)))
   data=out/(case+'.callgrind');assert data.stat().st_size<=PLAN['profile_postrun_size_cap_bytes']
   lines=data.read_text().splitlines();assert [s for s in lines if s.startswith('events:')]==['events: Ir']
   totals=[int(s.split(':',1)[1]) for s in lines if s.startswith('summary:')];assert len(totals)==1 and totals[0]>0
   # Archived cwd/include only; never annotate mutable root source.
   run([str(prefix/'bin/callgrind_annotate'),'--auto=no','--inclusive=no','--threshold='+str(PLAN['function_threshold']),'--include='+str(source),str(data)],case+'-functions')
   annotation_records={}
   for name in PLAN['annotations']:
    absolute=compiled/name
    display=run([str(prefix/'bin/callgrind_annotate'),'--auto=no','--inclusive=no','--context=0','--threshold='+str(PLAN['source_threshold']),'--include='+str(source),str(data),str(absolute)],case+'-'+Path(name).stem+'-lines')
    assert '-- User-annotated source: '+str(absolute) in display
    annotation_records[name]=dict(compiled_source=str(absolute),source_sha256=PLAN['source_sha256'][name],has_information=('No information has been collected for '+str(absolute)) not in display,threshold=PLAN['source_threshold'])
   result['cases'][case]=dict(annotations=annotation_records,total_simulated_Ir=totals[0],original_strict_replay_pass=True,exact_raw_bytes_equal_current_own_pgo_reference=True,normal_exit=True,pid=row['pid'],profile_sha256=sha(data),log_sha256=sha(out/(case+'.log')))
  assert list(result['cases'])==PLAN['cases'] and all(sha(Path(p))==digest for p,digest in before.items())
  result.update(complete=True,input_sha256=before,commands=commands,engine_sha256=PLAN['engine_sha256'],source_archive_sha256=PLAN['source_archive_sha256'],annotation_source_root=str(source),compiled_source_root=str(compiled),one_fixed_lifetime_per_case=True,performance_claim=False,outer_actual_terminal_required=True)
 except BaseException as error:result['failure']=f'{type(error).__name__}: {error}'
 finally:write(out/'provenance.json',result)
 print(json.dumps(result));return 0 if result['complete'] else 1
if __name__=='__main__':sys.exit(main())
