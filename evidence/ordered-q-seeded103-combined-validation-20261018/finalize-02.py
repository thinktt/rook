from pathlib import Path
import json,hashlib,os,re,collections,tarfile,datetime
E=Path('/home/legolas/rook2/evidence');V=Path(__file__).parent;C=V/'codegen';P=E/'ordered-q-seeded103-combined-validation-preparation-20261018';F=E/'ordered-q-seeded103-combined-proposal-20261018'
paths=json.loads((P/'paths.json').read_text());sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,d):p.write_text(json.dumps(d,indent=2)+'\n')
assert sorted(os.sched_getaffinity(0))==[0,1,2,3,4,5,8,9,10,11,12,13]
assert os.environ['TMPDIR']=='/home/legolas/rook2-build-tmp'
inputs=json.loads((C/'inputs.json').read_text());after={}
for label,a in inputs['artifacts'].items():
 b=Path(a['build']);assert sha(a['binary'])==a['binary_sha256'];assert sha(b/'receipt.json')==a['receipt_sha256']
 for mapping in ['source_sha256','tool_source_sha256']:
  for rel,h in a[mapping].items():assert sha(b/'source-before'/rel)==h
 after[label]={'binary_sha256':sha(a['binary']),'receipt_sha256':sha(b/'receipt.json'),'verified_snapshot_files':66,'stable':True}
write(C/'inputs-after.json',after)
fixed={}
for label in ['control102','combined103']:
 text=(C/f'{label}-default-fixed-entry.txt').read_text();rows=text.splitlines();calls=[]
 for i,l in enumerate(rows):
  if re.search(r'\bcall\s',l):
   rel=rows[i+1] if i+1<len(rows) and 'R_X86_64_' in rows[i+1] else l
   calls.append(re.sub(r'17h[0-9a-f]{16}E','17hHASH',rel.strip().split('\t')[-1]))
 counters=dict(collections.Counter(calls));fixed[label]={'body_bytes':4322 if label=='control102' else 4500,'explicit_frame_bytes':0xd38,'callee_saved_pushes':6,'static_calls':len(calls),'call_roles':counters,'entry_text_sha256':sha(C/f'{label}-default-fixed-entry.txt')}
 for role in ['__rust_alloc-0x4','__rust_dealloc-0x4','memcpy-0x4']:
  assert counters[role]=={'__rust_alloc-0x4':2,'__rust_dealloc-0x4':13,'memcpy-0x4':4}[role]
 assert not any(s in text for s in ['random_adjustment','score_add','observe_raw','run_seeded'])
assert fixed['control102']['static_calls']==59 and fixed['combined103']['static_calls']==61
# Literal register-indirect referents are established from captured GOT-load relocations and intervening operand windows, not relocation totals.
registers={'control102':[(0x1bb,'r12','memcpy',[0x1cf,0x226]),(0x32d,'r15','memcpy',[0x334,0x3c7]),(0x687,'r12','__rust_alloc',[0x6e2,0x724,0x785])], 'combined103':[(0x1c4,'r14','memcpy',[0x1d6,0x22d]),(0x3c4,'rbp','memcpy',[0x3cb,0x44a]),(0x70c,'r12','__rust_alloc',[0x767,0x7b5,0x812])]}
proof={}
for label,groups in registers.items():
 rows=(C/f'{label}-default-fixed-entry.txt').read_text().splitlines();parsed=[]
 for i,l in enumerate(rows):
  m=re.match(r'\s*([0-9a-f]+):\s*(.*)',l)
  if m and 'R_X86_64_' not in l:parsed.append((int(m[1],16),i,m[2]))
 groupsout=[]
 for load,reg,role,ips in groups:
  row=next(x for x in parsed if x[0]==load);assert re.search(r'mov\s+0x0\(%rip\),%'+reg+r'\b',row[2]);assert role+'-0x4' in rows[row[1]+1]
  for ip in ips:assert next(x[2] for x in parsed if x[0]==ip).strip()=='call   *%'+reg
  windows='\n'.join(rows[row[1]:next(x[1] for x in parsed if x[0]==ips[-1])+1])
  groupsout.append({'GOT_load_instruction':hex(load),'register':reg,'linker_relocation_role':role,'call_instructions':[hex(x) for x in ips],'captured_operand_window':windows,'review':'Register referent retained across the listed call sites; intervening callee-saved uses inspected. Imported runtime implementation not proved by a relocation.'})
 proof[label]={'register_indirect_groups':groupsout,'unresolved_register_call_sites':0,'direct_import_call_sites':{'memcpy':4,'__rust_alloc':2},'decoded_register_indirect_call_sites':{'memcpy':4,'__rust_alloc':3},'all_static_calls_with_these_import_roles':{'memcpy':8,'__rust_alloc':5},'scope':'Static linker roles and sites, not dynamic call counts, path equality, allocator effects, argument equality, or copying-cost equality.'}
write(C/'default-false-register-referents.json',proof)
fixed['meaning']='Forced public Search<false>::run_iterations object only, never executed. Const-false source body and actual root request/return windows examined; seeded args, mixer, callback and saturation are absent from this body. Indirect existing library copy calls remain; this is not an instruction identity or no-spill claim.'
write(C/'default-false-analysis.json',fixed)
old=E/'ordered-q-bitview-phase2-validation-20261018/codegen/phase2-ordered_attackers-0-normalized.txt';new=C/'combined103-ordered_attackers-0-normalized.txt'
assert old.read_bytes()==new.read_bytes()
anchor95=E/'admission-combined95-native-build-20261018/source-before/src/quiescence.rs'
def stats(p):return re.search(r'pub struct Stats \{.*?\n\}',p.read_text(),re.S).group()
newstats=stats(Path(paths['source'])/'src/quiescence.rs');oldstats=stats(anchor95)
fields=lambda t:re.findall(r'pub (\w+): u64',t)
assert len(fields(oldstats))==28 and len(fields(newstats))==29
write(C/'source-anchors.json',{'ordered_kernel_phase2_normalized_equal':True,'phase2_path':str(old),'phase2_sha256':sha(old),'combined_sha256':sha(new),'root95_stats_source':str(anchor95),'root95_stats_source_sha256':sha(anchor95),'root95_stats_fields':fields(oldstats),'combined_stats_fields':fields(newstats),'new_stats_fields':list(set(fields(newstats))-set(fields(oldstats))),'current_layouts_equal102':json.loads((C/'probes.json').read_text())['current_layouts_and_offsets_equal']})
terms=[{'stage':'capture','terminal_chunk':'311236','exit_code':0},{'stage':'probes','session':54427,'initial_chunk':'6a4cfd','terminal_chunk':'0c2a0c','exit_code':0},{'stage':'analysis','session':38612,'initial_chunk':'24ea8b','terminal_chunk':'5738ab','exit_code':0},{'stage':'focused','terminal_chunk':'1acdbf','exit_code':0}]
write(C/'actual-terminals.json',terms)
focused=json.loads((C/'focused-analysis.json').read_text());table=[]
for name in ['visit_q_impl','visit_ordinary','full_impl','generate_legal','legal_replies_up_to_two']:
 a=focused['artifacts']['control102']['functions'][name];b=focused['artifacts']['combined103']['functions'][name]
 table.append(f"| {name} | {a['size']} → {b['size']} | {a['prologue'][6] if len(a['prologue'])>6 else ''} | {a['direct_or_indirect_calls']} → {b['direct_or_indirect_calls']} |")
report="""Bounded default codegen review passed its inspection scope, with material residual code shape changes retained for parent review. No source fix was made, no promotion is implied, and no CPU neutrality or performance conclusion follows.

The exact generic control102 c4df447422ff8666ede8e15d8d599889a9cf1d2d4316c241dd313be1a15454d5 and combined103 1befaa6d9c439d3d806e6e189a27756ab86f4c5b5ce3b74f59ed302d98ee5c0d use identical rustc1.85.1/LLVM19.1.7, cargo1.85.1, generic x86-64 target, release settings, no PGO, and exact23 tool files. All43 native and23 tool snapshots were rehashed before/after. Changes against102 are exactly attacks/movegen/ordinary/quiescence. Inputs, original commands, tool versions/executable hashes and every captured output are retained here. The scoped source ownership/inverse proofs are in the frozen proposal and parent source review.

| Owner | Body bytes control102 → combined | Explicit frame | Static calls |
|---|---:|---:|---:|
| visit_q_impl |7358 →7584 (+226)|0x4c8 →0x4a8 (-32)|55 →56|
| visit_ordinary |8736 →8880 (+144)|0x438 unchanged|73 →74|
| full_impl |2415 unchanged|0x138 unchanged|12 unchanged|
| ordering_phase |2494 unchanged|0x1f8 unchanged|23 unchanged|
| generate_legal |5445 →5405 (-40)|0x128 →0x108 (-32)|29 →29|
| legal_replies_up_to_two |3311 →3338 (+27)|0xf8 →0xe8 (-16)|30 →30|

Q/ordinary/full retain six callee-saved pushes. Q stack-operand instructions422→395, ordinary625→630, full88→88. These include locals, argument/address construction and are not spill counts or retired work. Registers, scheduling and local live ranges change; equal frames do not establish equal copying or costs. Ordinary removes an outlined in_check call, adds attacked plus an explicit bounds panic path; its source policy is unchanged. Q removes in_check and two mailbox finders, adds two attacked calls, one ordered_attackers and a bounds-panic call. Full evaluator keeps its call roles and normalized body after resolving both anonymous operands to the same src/position.rs187:13 panic location. No observed-detail materialization or callback work is introduced in the examined default caller paths; this conclusion uses the const-gated source, actual call/operand bodies and layouts, not symbol absence alone. Whole-program reachability under arbitrary external consumers is not proven.

The candidate has one1554-byte ordered_attackers and a second527-byte attacked outline. Existing attacked is normalized-identical; its additional clone differs only in its verified panic-location filename (relative versus the actual source absolute path), with the same138:21 location. MASKS6208bytes and KNIGHT_SOURCES576bytes match as whole objects. The ordered kernel normalized body is exact previously validated phase2 (source-anchors.json). One676-byte in_check outline and one3781-byte mailbox-finder outline disappear. Automatic occurrence-index pairing of the remaining find_attackers is not a full/capped semantic match and is not used to claim equivalence. Global825 matched symbols/666normalized matches are context, not a proof of unchanged execution.

Actual Q uses one32-byte projected view at rsp+0x1e8: four stores39d04/39d0c/39d14/39d1c; ordered route call39d41 reads that same pointer, returns through separate rsp+0xc0 scratch, saturates at two and tests moved-to membership. Final own-king safety3999a receives the same view. Initial entry safety38b9d uses a separate original-position view at rsp+0x298. Focused CFG decodes all three switch tables (8/7/6 targets), checks valid targets, and shows route and all four stores dominate final safety. Source inverse proof preserves optimistic best before rejection, route eligibility, reply/scout/history/child creation ordering and charges; no second projection or new early safety query is present. Address order alone would be misleading here. Static dominance does not establish runtime frequency or per-iteration freshness by itself.

A separate forced Search<false>::run_iterations public-API OBJECT (never executed; normal CLI uses timed controller) retains the same typed ABI, six pushes and0xd38 frame, but4322→4500 bytes (+178),59→61calls. Literal call counters retain2 direct allocator sites,13deallocator and4direct memcpy sites. Saved GOT-load relocations and full intervening operand windows decode the seven register-indirect calls: four memcpy and three allocator sites in each body (eight memcpy/five allocator sites total). The imported runtime implementations, dynamic path frequencies, arguments and effect/cost equivalence are not proved; default-false-register-referents.json retains every load/call address and window. The two in_check calls become attacked with inlined king/count lookup; one extra slice-end panic and one bounds panic explain the call-count increment, with additional lookup/control instructions. Root child/history-push/ordinary-return/history-pop order is unchanged; the inspected default request still uses unadjusted window, and actual return is negated then compared directly with best. No seeded randomness, score saturation or raw-score callback appears in this forced false body. The const-false owner source prunes all three branches. This is bounded pruning evidence, not exact-byte equality or a claim that all growth is exclusively caused by any one source edit.

Layouts/public offsets match exact102. Stats232, SearchFalse/True25600, Ordinary/FirstOutcome376, QOutcome328, Node176, Retained16, EvaluatorFalse9736 and Position160. The preexisting observer Stats field already grows Stats/outcomes by8 compared with the old generation2/95 anchor; Search size is unchanged due to padding. root95 has28u64 Stats fields and combined29; that cumulative default storage/ABI/copying risk remains relevant to parent’s planned95→combined CPU gate. No new layout change relative102 is hidden by this comparison.

All capture/probe/analyzer processes actually exited0 (actual-terminals.json); probes only read layouts/offsets and forced-object code, never execute search. All native/strict/DIAG regressions are independent evidence, not a performance proof. Link layout, source paths, outlined monomorph choices, relocation normalization, compiler inlining and unmeasured path frequencies limit conclusions. The parent decides whether residual codegen changes are acceptable before promotion or CPU measurement.
"""
(C/'report.md').write_text(report)
# Validate exact frozen/current whole source, without changing any bound input.
manifest=json.loads((F/'source-manifest.json').read_text())['files'];assert len(manifest)==102
for rel,h in manifest.items():
 assert sha(Path(paths['source'])/rel)==h,rel
 assert sha(Path(paths['frozen_proposal'])/rel)==h,rel
write(V/'source-final-stability.json',{'complete':True,'files':102,'native':43,'tools':23,'diagnostic':36,'source_manifest_sha256':sha(F/'source-manifest.json'),'execution_and_frozen_proposal_exact':True,'affinity':sorted(os.sched_getaffinity(0))})
# No process except this packaging command is allowed to retain our native jobs.
needles=[paths['source'],paths['generic_build']+'/rook2-exact',paths['diagnostic_build']+'/rook2-diag-exact',str(V/'unit-bin'),str(Path(paths['diagnostic_validation'])/'unit-bin')]
active=[]
for d in Path('/proc').iterdir():
 if not d.name.isdigit() or int(d.name) in [os.getpid(),os.getppid()]:continue
 try:
  cmd=(d/'cmdline').read_bytes().replace(b'\0',b' ').decode(errors='replace');exe=os.readlink(d/'exe')
 except (FileNotFoundError,ProcessLookupError,PermissionError):continue
 # Match actual executable, not unrelated parent messages/command strings.
 if any(exe.startswith(n) for n in needles):active.append({'pid':int(d.name),'exe':exe,'command':cmd})
assert not active,active
write(V/'owned-process-closure.json',{'complete':True,'no_owned_native_jobs':True,'matches':active,'method':'/proc executable ownership check for own execution source/target, generic/DIAG frozen images and unit-bin paths; all recorded stage terminals independently0','excluded_packaging_pid':os.getpid(),'affinity':sorted(os.sched_getaffinity(0)),'cpu_pgo_profiler_runs':0})
write(C/'output-hashes.json',{str(p.relative_to(C)):sha(p) for p in C.rglob('*') if p.is_file() and p.name!='output-hashes.json'})
summary={'complete':True,'scope':'Untimed exact combined103bits; parent review required before promotion','binary_sha256':sha(Path(paths['generic_build'])/'rook2-exact'),'receipt_sha256':sha(Path(paths['generic_build'])/'receipt.json'),'source_manifest_sha256':sha(F/'source-manifest.json'),'native_units':158,'diagnostic_units':175,'operations':103,'cases':7514,'whole_files':100,'strict':54,'wire_fixtures':8,'wire_searches':24,'stage_terminals':{p.name:json.loads(p.read_text()) for p in V.glob('*-actual-terminal.json')},'codegen_report_sha256':sha(C/'report.md'),'codegen_output_manifest_sha256':sha(C/'output-hashes.json'),'source_final_sha256':sha(V/'source-final-stability.json'),'owned_process_closure_sha256':sha(V/'owned-process-closure.json'),'failures':[{'stage':'metadata packaging only','terminal_chunk':'fa17d2','exit_code':1,'preserved':'finalize.py +final-packaging-attempt01-actual-terminal.json','reason':'counted memcpy address-load relocations as direct calls; actual call sites4 not6'}],'no_cpu_neutrality_claim':True,'source_fixes':0}
write(V/'final-summary.json',summary)
(V/'report.md').write_text('Exact combined103bits passed158native, strict54,8wire/24searches,175DIAGunits and7514original mandatory cases/103ops/100wholefiles. Independent original raw/expected/exit/source/archive reconciliation passed. No source corrections or native/regression failures occurred; metadata-only packaging attempt01 failed a hardcoded memcpy-site assertion and is preserved separately. Generic image '+summary['binary_sha256']+'; receipt '+summary['receipt_sha256']+'.\n\nActual terminals: native11488/197b07, build89073/75ffd5, strict71742/a201b4, DIAG92381/608d4d, independent45891/670489, all0. All helpers and actual62 regression-engine PIDs used CPUs0-5,8-13; homeTMPDIR. Parent root-scheduler functional work and sibling102 packaging overlapped only untimed housekeeping. Frozen sources remain exact102files.\n\nCodegen/report.md records residual Q+226, ordinary+144 and forced fixed false+178bytes, Qframe-32, identical full evaluator scope and current102layout. Stats/outcome+8 compared95 remains a cumulative ABI/storage/copying risk. This is no CPU-neutrality or promotion claim. No CPU/PGO/profiler run was performed. All owned native processes are terminal; parent owns final review/measurement/promotion.\n')
# Supplement immutable execution input closure: new reconciliation/codegen/final receipts, without altering prior25-file archive.
files=[]
for root in [P,V]:
 for p in root.rglob('*'):
  if p.is_file() and (p.suffix in ['.py','.rs'] or p.name in ['final-summary.json','report.md','source-final-stability.json','owned-process-closure.json','actual-terminals.json','inputs-after.json','output-hashes.json','default-false-analysis.json','source-anchors.json','default-false-register-referents.json','focused-analysis.json','independent-verification.json','diagnostic-native-binding.json']):files.append(p)
write(V/'supplemental-metadata-manifest.json',{str(p):sha(p) for p in sorted(set(files))})
with tarfile.open(V/'supplemental-metadata.tar.gz','w:gz') as tar:
 for p in sorted(set(files)):tar.add(p,arcname=str(p).lstrip('/'),recursive=False)
write(V/'final-packaging.json',{'complete':True,'final_summary_sha256':sha(V/'final-summary.json'),'report_sha256':sha(V/'report.md'),'metadata_manifest_sha256':sha(V/'supplemental-metadata-manifest.json'),'metadata_archive_sha256':sha(V/'supplemental-metadata.tar.gz'),'codegen_report_sha256':sha(C/'report.md'),'actual_helper_exit':'outer tool terminal to be recorded after observation; not inferred by this file','no_more_native_commands_required':True})
print(json.dumps(json.loads((V/'final-packaging.json').read_text()),indent=2))
