from pathlib import Path
import json,hashlib,os,re,subprocess,shutil
C=Path(__file__).parent;E=C.parent;P=E/'post-lifecycle109-validation-preparation-20261018';plan=json.loads((P/'plan.json').read_text());CAP=json.loads((C/'capture.json').read_text())
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();load=lambda p:json.loads(Path(p).read_text());write=lambda p,d:p.write_text(json.dumps(d,indent=2)+'\n')
ns={'__file__':str(C/'analyze.py')};s=(C/'analyze.py').read_text();exec(s[:s.index('\nDATA={};')],ns);ELF=ns['ELF']
assert sorted(os.sched_getaffinity(0))==plan['affinity'] and os.environ['TMPDIR']==plan['TMPDIR']
identities={}
for tag,dirname in [('control','controlled-root108-generic-build-20261018'),('candidate','post-lifecycle109-generic-build-20261018')]:
 B=E/dirname;r=load(B/'receipt.json');a=load(B/'archive-receipt.json');assert r['outcome']=='build-succeeded-with-stable-input-snapshot' and r['cargo_exit_code']==0
 assert r['source_sha256_before']==r['source_sha256_after'] and r['tool_sha256_before']==r['tool_sha256_after']
 for rel,h in r['source_sha256_before'].items():assert sha(B/'source-before'/rel)==h
 for rel,h in r['tool_sha256_before'].items():assert sha(B/'source-before'/rel)==h
 assert sha(B/'rook2-exact')==r['binary_output']['sha256']==CAP['tags'][tag]['engine_sha256']==a['binary_sha256']
 assert sha(B/a['archive'])==a['sha256'];cap=CAP['tags'][tag];assert sha(cap['rlib'])==cap['rlib_sha256'] and sha(C/(tag+'-probe'))==cap['probe_sha256'] and sha(C/(tag+'-probe.rs'))==cap['source_sha256']
 identities[tag]={'build':str(B),'receipt_sha256':sha(B/'receipt.json'),'archive_receipt_sha256':sha(B/'archive-receipt.json'),'archive_sha256':a['sha256'],'native_source':r['source_sha256_before'],'tools23':r['tool_sha256_before'],'engine_sha256':sha(B/'rook2-exact'),'rlib_sha256':sha(cap['rlib']),'probe_sha256':sha(C/(tag+'-probe')),'settings':{k:r[k] for k in ['mode','target_triple','target_cpu','rust_flags','pgo','toolchain','build_effective_environment']}}
for k in ['mode','target_triple','target_cpu','rust_flags','pgo','toolchain','build_effective_environment']:assert identities['control']['settings'][k]==identities['candidate']['settings'][k],k
assert identities['control']['tools23']==identities['candidate']['tools23']
changed=[rel for rel in sorted(set(identities['control']['native_source'])|set(identities['candidate']['native_source'])) if identities['control']['native_source'].get(rel)!=identities['candidate']['native_source'].get(rel)]
assert set(changed)=={'src/lib.rs','src/output.rs','src/post_lifecycle.rs','src/session.rs','src/timed.rs'}
write(C/'inputs-final.json',{'complete':True,'before_after_stable':True,'artifacts':identities,'native_delta':changed,'same_tools23_and_compiler_generic_settings':True,'matched_probe_sources_equal':(C/'control-probe.rs').read_bytes()==(C/'candidate-probe.rs').read_bytes()})
# All12 NoHost register-indirect sites, separately bound to actual import loads.
groups={'control':[(0x34db1,'r12','memcpy',[0x34dc3,0x34e10]),(0x350b8,'r12','memcpy',[0x350bf,0x35137]),(0x3556d,'r15','memcpy',[0x35574,0x355e2]),(0x356fc,'r8','malloc',[0x3577d]),(0x365af,'r13','free',[0x365d5]),(0x3662d,'rbp','free',[0x36694,0x366a1,0x366ad,0x366d8])], 'candidate':[(0x34d4c,'r13','memcpy',[0x34d5e,0x34db0]),(0x3504e,'rbp','memcpy',[0x35055,0x350cb]),(0x35509,'r15','memcpy',[0x35510,0x3557e]),(0x356aa,'rdx','malloc',[0x35717]),(0x36527,'r13','free',[0x36545]),(0x3657f,'rbp','free',[0x365e4,0x365f1,0x365fd,0x36628])]}
registerproof={}
for tag,groupset in groups.items():
 elf=ELF(C/(tag+'-probe'),C/(tag+'-probe-symbols.stdout'));fn=next(x for x in CAP['tags'][tag]['functions']['probe'] if x['symbol']=='default_root');rows=[]
 for l in (C/fn['file']).read_text().splitlines():
  m=re.match(r'\s*([0-9a-f]+):\s*(.*)',l)
  if m:rows.append((int(m[1],16),m[2],l.strip()))
 out=[]
 for ip,reg,role,calls in groupset:
  i=next(i for i,x in enumerate(rows) if x[0]==ip);ins=rows[i][1];assert re.match(r'mov\s+[^,]+,%'+reg+r'\s',ins)
  got=int(re.search(r'# ([0-9a-f]+)',ins)[1],16);resolved=elf.resolve(got);assert resolved['role']==role
  for call in calls:assert next(r[1] for r in rows if r[0]==call)=='call   *%'+reg
  end=next(i for i,r in enumerate(rows) if r[0]==calls[-1]);out.append({'load':hex(ip),'register':reg,'import':resolved,'calls':[hex(x) for x in calls],'intervening_operand_window':[x[2] for x in rows[i:end+1]],'scope':'Static retained register referents; no runtime frequency/allocator effect or copying-cost equivalence asserted.'})
 assert sum(len(x['calls']) for x in out)==12;registerproof[tag]=out
write(C/'nohost-register-referents.json',registerproof)
for tag,lo,hi in [('control',0x47170,0x47685),('candidate',0x47080,0x47510)]:
 fn=next(x for x in CAP['tags'][tag]['functions']['engine'] if x['symbol']=='rook2::run');rows=[]
 for l in (C/fn['file']).read_text().splitlines():
  m=re.match(r'\s*([0-9a-f]+):',l)
  if m and lo<=int(m[1],16)<hi:rows.append(l)
 (C/(tag+'-actual-final-post-window.txt')).write_text('\n'.join(rows)+'\n')
tools={}
for tool in ['objdump','nm','readelf','size','python3']:
 path=Path(shutil.which(tool));done=subprocess.run([str(path),'--version'],stdout=subprocess.PIPE,stderr=subprocess.PIPE);assert done.returncode==0
 dest=C/(tool+'-version.txt');dest.write_bytes(done.stdout+done.stderr);tools[tool]={'path':str(path),'executable_sha256':sha(path),'version_output_sha256':sha(dest),'exit_code':done.returncode}
write(C/'tool-identities.json',tools)
write(C/'actual-terminals.json',{'capture':load(C/'capture-actual-terminal.json'),'analysis':{'terminal_chunk_id':'b453ab','exit_code':0,'actual_tool_terminal_observed':True},'focused01':load(C/'focused-reader01-actual-terminal.json'),'focused02':{'terminal_chunk_id':'47d4da','exit_code':0,'actual_tool_terminal_observed':True,'native_or_probe_reruns':0},'close_script_preparation_failure':{'terminal_chunk_id':'7a429b','exit_code':1,'scope':'outer Python quoting SyntaxError before intended script/output writes; no source/native change; exact failure remains in tool transcript'}})
assert (C/'report.md').is_file()
outputs={str(p.relative_to(C)):sha(p) for p in C.rglob('*') if p.is_file() and p.name not in ['output-hashes.json','bounded-gate.json']};write(C/'output-hashes.json',outputs)
write(C/'bounded-gate.json',{'complete':True,'capture_sha256':sha(C/'capture.json'),'report_sha256':sha(C/'report.md'),'focused_summary_sha256':sha(C/'focused-summary.json'),'inputs_final_sha256':sha(C/'inputs-final.json'),'output_manifest_sha256':sha(C/'output-hashes.json'),'material_risks':['ActiveHost main-469bytes/-32frame, clone/retention+publisher outline+571bytes/+72helperframe/one extra saved register; changed partition, not dynamic cost','NoHost public root+36bytes/+25boundedinstructions/+3staticcalls/+16frame','capture_fields+16bytes/+4instructions and Session Option<Result> actual scalar/vector aggregate lowering differs','Rust local generic aggregate/clone/drop/transfer scheduling and branch frequency remain unmeasured'],'recursive_scopes_and_current_layouts_match':True,'cpu_neutrality_claim':False,'promotion_authorized':False,'native_source_fixes':False,'preserved_metadata_failures':['865fc0/1 focused.py; exactfocused-02delta, no native rerun','7a429b/1 outer script-creation quoting; no output/source writes'],'actual_final_packaging_terminal_required_externally':True})
print(json.dumps({'complete':True,'report_sha256':sha(C/'report.md'),'gate_sha256':sha(C/'bounded-gate.json'),'output_manifest_sha256':sha(C/'output-hashes.json'),'no_more_native_commands_required':True},indent=2))
