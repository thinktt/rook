from pathlib import Path
import json,hashlib,os,tarfile
from guard import HERE,load,sha,write,clearance,terminal,check_sources,check_dependencies
plan=clearance();paths={k:Path(v) for k,v in plan['output'].items()};check_sources(plan);check_dependencies(plan)
for key in ['freeze','generic-build','native-validation','strict-check','diagnostic','reconciliation','codegen']:terminal(paths[key]/'tool-terminal.json')
I=paths['reconciliation'];ind=load(I/'independent-verification.json');assert ind['status']=='pass' and ind['source_stable'] and ind['all_raw_expected_and_actual_equal'] and ind['all_native_child_exits_confirmed']
assert (ind['native_units'],ind['diagnostic_units'],ind['diagnostic_cases'],ind['diagnostic_operations'],ind['whole_fixture_files'])==(169,192,7606,109,106)
B=paths['generic-build'];D=paths['diagnostic-build'];C=paths['codegen'];g=load(B/'receipt.json');d=load(D/'receipt.json')
for k in ['toolchain','mode','target_triple','target_cpu','rust_flags']:assert g[k]==d[k],k
assert g['pgo']['mode']==d['pgo']['mode']=='none'
assert sha(B/'rook2-exact')==g['binary_output']['sha256']==ind['native_artifact_sha256']
assert sha(D/'rook2-diag-exact')==d['binary_output']['sha256']==ind['diagnostic_artifact_sha256']
for key,counts in [('native-validation',{'rook2':167,'rook2-dev':2}),('diagnostic',{'rook2-diag':192})]:
 v=load(paths[key]/'verification.json');assert v['complete'] and v['failure'] is None and all(s['exit_code']==0 and s['actual_child_return_observed'] for s in v['stages'])
 for target,n in counts.items():assert v['units'][target]['passed']==n and sha(paths[key]/'unit-bin'/target/'unit-exact')==v['units'][target]['binary_sha256']
for key in ['generic-build','diagnostic-build']:
 r=load(paths[key]/'receipt.json');ar=load(paths[key]/'archive-receipt.json');assert sha(paths[key]/ar['archive'])==ar['sha256']
 for rel,h in (r['source_sha256_before']|r['tool_sha256_before']).items():assert sha(paths[key]/'source-before'/rel)==h
cap=load(C/'capture.json');gate=load(C/'bounded-gate.json');assert gate['complete'] and not gate['promotion_authorized'] and not gate['cpu_neutrality_claim']
assert cap['tags']['candidate']['engine_sha256']==sha(B/'rook2-exact') and gate['capture_sha256']==sha(C/'capture.json') and gate['report_sha256']==sha(C/'report.md')
for tag in ['control','candidate']:
 x=cap['tags'][tag];assert sha(Path(x['rlib']))==x['rlib_sha256'] and sha(C/(tag+'-probe'))==x['probe_sha256'] and sha(C/(tag+'-probe.rs'))==x['source_sha256']
for rel,h in load(C/'output-hashes.json').items():assert sha(C/rel)==h,rel
observed={n:load(paths['strict-check']/(n+'-actual-engine-affinity.json')) for n in ['strict54','wire']}
assert len(observed['strict54']['actual_observed_pids'])==54 and len(observed['wire']['actual_observed_pids'])==8
assert all(mask==plan['affinity'] for r in observed.values() for mask in r['actual_observed_pids'].values())
# /proc only for owned live jobs; do not identify siblings/parent by message text.
S=Path(plan['home_source']);exe_prefixes=[str(S)+'/',str(B/'rook2-exact'),str(D/'rook2-diag-exact'),str(paths['native-validation']/'unit-bin')+'/',str(paths['diagnostic']/'unit-bin')+'/',str(C/'control-probe'),str(C/'candidate-probe')]
script_prefixes=[str(HERE)+'/',str(C)+'/'];live=[]
for p in Path('/proc').iterdir():
 if not p.name.isdigit() or int(p.name) in [os.getpid(),os.getppid()]:continue
 try:
  exe=os.readlink(p/'exe');argv=(p/'cmdline').read_bytes().split(b'\0');argv=[x.decode(errors='replace') for x in argv if x]
 except (OSError,PermissionError):continue
 ownexe=any(exe.startswith(n) for n in exe_prefixes)
 ownscript=('python' in Path(exe).name) and len(argv)>1 and argv[1].endswith('.py') and any(argv[1].startswith(n) for n in script_prefixes)
 if ownexe or ownscript:live.append({'pid':int(p.name),'exe':exe,'argv':argv})
assert not live,live
write(HERE/'owned-process-closure.json',{'complete':True,'live_owned_processes':live,'all_owned_native_build_test_engine_codegen_probe_jobs_terminal':True,'only_current_finalizer_active':os.getpid(),'method':'/proc exact owned executable prefixes and Python script argv; current packaging process/parent wrapper excluded','all_actual_stage_terminals_0':True,'metadata_failures_preserved':['865fc0 reader __file__','7a429b outer report-helper creation quoting'],'CPU_PGO_profiler_runs':0,'affinity':sorted(os.sched_getaffinity(0))})
summary={'status':'FUNCTIONAL_PASS_BOUNDED_CODEGEN_PARENT_DECISION_PENDING','source':str(S),'frozen_source':plan['frozen_source'],'source_graph_sha256':load(Path(plan['proposal'])/'prepared.json')['source_graph_sha256'],'source_files':107,'native_source_files':45,'tools_source_files':23,'cold_source_files':39,'native_units':169,'strict_replays':54,'wire_fixtures':8,'wire_searches':24,'actual_engine_affinity_PIDs':62,'diagnostic_units':192,'operations':109,'cases':7606,'whole_files':106,'duplicate_ids':0,'partial_files':0,'generic_sha256':sha(B/'rook2-exact'),'generic_receipt_sha256':sha(B/'receipt.json'),'adapter_sha256':sha(D/'rook2-diag-exact'),'adapter_receipt_sha256':sha(D/'receipt.json'),'independent_sha256':sha(I/'independent-verification.json'),'codegen_report_sha256':sha(C/'report.md'),'codegen_gate_sha256':sha(C/'bounded-gate.json'),'material_codegen_risks':gate['material_risks'],'actual_terminals':{k:load(paths[k]/'tool-terminal.json') for k in ['freeze','generic-build','native-validation','strict-check','diagnostic','reconciliation','codegen']},'source_stable':True,'all_original_bytes_headers_expected_raw_actual_exits_reconciled':True,'native_reused':False,'source_corrections':False,'root_mutated_by_this_child':False,'canonical_domain_audit_limit':plan['canonical_domain_audit_limit'],'cpu_pgo_profiler':False,'promotion_authorized':False,'all_owned_native_jobs_terminal':True,'finalizer_actual_terminal_required_externally':True,'preserved_metadata_failures':['865fc0/1 focused-reader missing __file__, focused-02 fixed metadata only47d4da/0','7a429b/1 nested quote generator before file writes; corrected same intended helper creation77d4ee/0']}
write(HERE/'validation-summary.json',summary)
(HERE/'report.md').write_text('''Exact POST109 passed fresh169native (167lib+2dev), strict54, eightwire24,192DIAGunits and all7606original mandatory cases/109operations/106wholefiles. Independent reconciliation verifies original full bytes/headers, expected and raw outputs, actual child exits, source/tool/image identities and source/input/build archives; zero partial files or duplicate IDs. All62 actual regression-image PIDs were read back on CPUs0-5,8-13; helpers/probes/adapter children inherit the same explicit mask and homeTMPDIR. No source correction or failed native/regression stage occurred.

Frozen generic image17e75a5a60bcfe31f75ae9ea49859dead1b6fec542a405b0280b9b54e2e9c823; frozen adapterc2b9a2817434f432c3df581356064382a6e48560b4ed409ffa7b3bc60b66d83b. Source107=45native+23tools+39cold is exact frozen4ad036c6 proposal in disjoint HOME execution copy; root/frozen parents were not edited. Original failure history and the two new metadata-only failures are preserved. No native/probe replay or source repair was used to fix metadata readers.

Actual functional terminals: freeze92524/3c26b1; generic45168/777149; native95059/363990; strict34242/d1bed7; DIAG65395/ae62a1; independent49599/739e3f, all exit0. Codegen capture12167/e5bdaa, initial analysisb453ab, focused reader02 47d4da and report/hash closure21c964 all exit0. Metadata reader01 865fc0/1 lacked __file__; a one-line separate retry fixed only metadata binding. Outer helper creation7a429b/1 had a quoting SyntaxError before file/output writes; its corrected creation77d4ee/0 is retained in codegen actual-terminals. No failed source/runtime test is hidden.

Bounded backend report is post-lifecycle109-codegen-20261018/report.md. Against exact108, active-Host enclosing body-469bytes/-32frame while capture/retain/publisher outlining adds571bytes/+72helperframe/one save; forced NoHost root+36bytes/+3calls/+16frame; capture_fields+16bytes/+4instructions and Session Option<Result> lowering change. All12 NoHost indirect sites per body are actually decoded; constant inactive-host callback work is pruned, with no claim that aggregate/copy costs are neutral. Recursive Q/ordinary/ordering/full normalized operands/branches/call scopes and current layouts match108 after actual referent/table decoding. These are static observations, not dynamic performance evidence.

All native/compiler/test/engine/probe jobs are actually terminal and the finalizer's /proc check finds no owned jobs. Only final immutable evidence packaging remains until its outer actual terminal is recorded. Parent review/performance/integration decisions are pending; no CPU/PGO/profiler/promotion or full-engine completion claim is made. The separate inherited timed vocabulary audit limit remains open; this component does not solve broader timed controllers.
''')
# Supplemental archive: exact scripts/reports/terminals/identity metadata; complete raw streams stay in original immutable paths.
metadata=[]
for root in [HERE,C]:
 for p in root.iterdir():
  if p.is_file() and (p.suffix in ['.py','.rs'] or p.name in ['validation-summary.json','report.md','owned-process-closure.json','bounded-gate.json','inputs-final.json','actual-terminals.json','focused-summary.json','tool-terminal.json','nohost-register-referents.json','capture-actual-terminal.json','focused-reader01-actual-terminal.json']):metadata.append(p)
metadata += [paths[k]/'tool-terminal.json' for k in ['freeze','generic-build','native-validation','strict-check','diagnostic','reconciliation']]
write(HERE/'supplemental-metadata-manifest.json',{str(p):sha(p) for p in sorted(set(metadata))})
with tarfile.open(HERE/'supplemental-metadata.tar.gz','w:gz') as t:
 for p in sorted(set(metadata)):t.add(p,arcname=str(p).lstrip('/'),recursive=False)
 t.add(HERE/'supplemental-metadata-manifest.json',arcname=str(HERE/'supplemental-metadata-manifest.json').lstrip('/'),recursive=False)
# All retained raw/image/source/archive outputs get a stable final manifest; exclude its own future file.
files={}
for root in [HERE,paths['freeze'],paths['generic-build'],paths['native-validation'],paths['strict-check'],paths['interruption-wire'],paths['diagnostic'],paths['diagnostic-build'],paths['reconciliation'],C]:
 for p in sorted(root.rglob('*')):
  if p.is_file():files[str(p)]=sha(p)
write(HERE/'validation-file-manifest.json',files)
check_sources(plan);check_dependencies(plan)
print(json.dumps({'status':summary['status'],'summary_sha256':sha(HERE/'validation-summary.json'),'manifest_sha256':sha(HERE/'validation-file-manifest.json'),'supplemental_archive_sha256':sha(HERE/'supplemental-metadata.tar.gz'),'source_stable':True,'all_owned_native_jobs_terminal':True,'final_packaging_actual_terminal_required':True},indent=2))
