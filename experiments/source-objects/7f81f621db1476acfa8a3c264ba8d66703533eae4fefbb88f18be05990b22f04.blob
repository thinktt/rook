from pathlib import Path
import json,hashlib,difflib,re,tarfile,os,datetime
E=Path(__file__).parent;paths=json.loads((E/'paths.json').read_text());S=Path(paths['source']);B=Path(paths['base']);F=Path(paths['base_manifest']).parent
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,d):p.write_text(json.dumps(d,indent=2)+'\n')
assert sorted(os.sched_getaffinity(0))==[0,1,2,3,4,5,8,9,10,11,12,13]
assert os.environ['TMPDIR']=='/home/legolas/rook2-build-tmp'
base=json.loads(Path(paths['base_manifest']).read_text());files=base['files'];assert len(files)==102
for rel,h in files.items():assert sha(B/rel)==h,rel
# These are literal whole-body inversions, not Rust parsing/typing or test execution.
p=(S/'src/position.rs').read_text()
p=p.replace("""    fn set_square(&mut self, square: Square, piece: Piece) {
        self.set_square_inner::<true>(square, piece);
    }

    #[inline]
    fn set_square_inner<const MAINTAIN_PLANES: bool>(&mut self, square: Square, piece: Piece) {
""","""    fn set_square(&mut self, square: Square, piece: Piece) {
""")
p=p.replace("""        if MAINTAIN_PLANES {
            self.attack_bits.replace(square, old, piece);
        }
""","""        self.attack_bits.replace(square, old, piece);
""")
start=p.index('    /// Construction-only transport:');end=p.index('    /// Cold ingress primitive,',start);p=p[:start]+p[end:]
p=p.replace("""    pub fn apply_unchecked(&mut self, movement: Move) {
        self.apply_unchecked_inner::<true>(movement);
    }

    #[inline]
    fn apply_unchecked_inner<const MAINTAIN_PLANES: bool>(&mut self, movement: Move) {
""","""    pub fn apply_unchecked(&mut self, movement: Move) {
""").replace('self.set_square_inner::<MAINTAIN_PLANES>(', 'self.set_square(')
assert p==(B/'src/position.rs').read_text(),'whole Position inversion'
e=(S/'src/evaluator.rs').read_text();start=e.index('    pub fn child(&self, root:');end=e.index('        let moving =',start)
e=e[:start]+'    pub fn child(&self, root: &RootContext, movement: Move) -> Self {\n'+e[end:]
e=e.replace('            position: placement(),','            position: self.position.played_unchecked(movement),')
assert e==(B/'src/evaluator.rs').read_text(),'whole evaluator inversion'
q=(S/'src/quiescence.rs').read_text();q=q.replace("""                let mut child_checked = None;
                let mut complete_replies = false;
                let mut child = if !checked {
                    let mut prepared_child = None;
""","""                let mut prepared_child = None;
                let mut child_checked = None;
                let mut complete_replies = false;
                if !checked {
""")
q=q.replace('                            let child = node.child_with_projection(&self.evaluator.root, movement, projected);','                            let child = node.child(&self.evaluator.root, movement);')
q=q.replace("""                    prepared_child.unwrap_or_else(|| {
                        node.child_with_projection(&self.evaluator.root, movement, projected)
                    })
                } else {
                    node.child(&self.evaluator.root, movement)
                };
                let capture_exception = policy::capture_exception(&position, &movement);
""","""                }
                let mut child =
                    prepared_child.unwrap_or_else(|| node.child(&self.evaluator.root, movement));
                let capture_exception = policy::capture_exception(&position, &movement);
""")
assert q==(B/'src/quiescence.rs').read_text(),'whole Q inversion'
a=(S/'src/attacks.rs').read_text();marker=a.index('\n    // Entire native child oracle:');assert a[:marker]+'\n}\n'==(B/'src/attacks.rs').read_text(),'whole attacks old tests/production exact'
newfiles={rel:sha(S/rel) for rel in files};changed=[rel for rel in files if files[rel]!=newfiles[rel]]
assert set(changed)=={'src/attacks.rs','src/evaluator.rs','src/position.rs','src/quiescence.rs'}
assert all(newfiles[rel]==h for rel,h in base['tools23'].items())
assert all(newfiles[rel]==h for rel,h in base['diagnostic36'].items())
# Supply path is only the local-copy constructor. No stale mutable receiver escapes.
pos=(S/'src/position.rs').read_text();body=pos[pos.index('    fn apply_unchecked_inner<'):pos.index('    pub fn null_child')]
assert 'attack_bits' not in body and 'attack_view' not in body and 'return' not in body
assert body.count('self.set_square_inner::<MAINTAIN_PLANES>(')==5
setter=pos[pos.index('    fn set_square_inner<'):pos.index('    #[inline]\n    pub fn played_unchecked')]
assert setter.count('self.attack_bits')==1
assert 'if MAINTAIN_PLANES {\n            self.attack_bits.replace(square, old, piece);\n        }' in setter
constructor=pos[pos.index('    pub(crate) fn played_with_projection'):pos.index('    /// Cold ingress primitive,')]
assert constructor.index('let mut child = *self;')<constructor.index('child.apply_unchecked_inner::<false>(movement);')<constructor.index('child.attack_bits = projected;')<constructor.index('        child\n')
# Callgraph read audit: these are tag/mailbox/list/scalar helpers, no attack queries.
read_audit={'apply_unchecked_inner':['remove_ordered','locate','append_ordered','set_square_inner','rights_mask','Piece/Move/Square/Color tag accessors'], 'remove_ordered':['locate','piece_count','array copy_within'], 'locate':['group_start','piece_squares','slice position'], 'append_ordered':['piece_count','group_start','array copy_within'], 'set_square_inner(false)':['identity::piece_keys (static KEYS table)','starting_credit (piece tags/square coordinates)','mailbox store'], 'no_plane_read_before_install':True,'private_false_receiver_not_exposed':True,'panic_path':'Any panic leaves only an unreturned copied local with stale planes; no callback/state/history/evaluator consumer occurs inside transition.'}
proof={'whole_position_after_inverse_equals_base':True,'whole_evaluator_after_inverse_equals_base':True,'whole_Q_after_inverse_equals_base':True,'whole_attacks_production_and_old_tests_unchanged':True,'tools23_and_diagnostic36_exact':True,'new_fields_or_tables':False,'new_layout_state':False,'default_Position_Node_APIs_unchanged':True,'no_dummy_view_in_default_API':True,'projection_computed_once_at_same_Q_site':True,'prepared_reply_child_at_same_site':True,'noncheck_final_child_only_after_same_safety':True,'checked_default_child_at_same_join':True,'retry_reuses_prepared_child':True,'stale_plane_callgraph_audit':read_audit,'limits':'Literal source proof only; Rust syntax/borrow typing, monomorph erasure, ABI/codegen/copy cost, tests and engine semantics remain unexecuted.'}
write(E/'source-proof.json',proof)
write(E/'source-manifest.json',{'files':newfiles,'native43':{rel:newfiles[rel] for rel in base['native43']},'tools23':base['tools23'],'diagnostic36':base['diagnostic36']})
write(E/'base-source-manifest.json',base)
patch=''.join(''.join(difflib.unified_diff((B/rel).read_text().splitlines(True),(S/rel).read_text().splitlines(True),fromfile='a/'+rel,tofile='b/'+rel)) for rel in sorted(changed))
(E/'trial.patch').write_text(patch)
# Declaration inventory is lexical source only, not discovery by a Rust test harness.
def declarations(root):
 result={}
 for rel in files:
  if rel.endswith('.rs'):
   text=(root/rel).read_text();found=re.findall(r'#\[test\]\s*(?:#\[[^\n]*\]\s*)*fn\s+([A-Za-z0-9_]+)',text)
   if found:result[rel]=found
 return result
oldtests=declarations(B);tests=declarations(S)
count=lambda d,front:sum(len(v) for k,v in d.items() if k.startswith('diagnostic/')==front)
assert count(oldtests,False)==158 and count(tests,False)==161
assert count(tests,True)==175
newtests={rel:[x for x in names if x not in oldtests.get(rel,[])] for rel,names in tests.items()};newtests={k:v for k,v in newtests.items() if v};assert sum(map(len,newtests.values()))==3
write(E/'test-declarations.json',{'lexical_only_unrun':True,'old_native':158,'native_expected':161,'lib_expected':159,'dev_expected':2,'diagnostic_expected':175,'new_tests':newtests,'all':tests})
# Reuse the immutable full official corpus identity, without adding a route/admission.
fixture=F/'original-fixtures-100.tar.gz';fixturehash=sha(fixture);oldprepared=json.loads((F/'prepared.json').read_text());assert fixturehash==oldprepared['fixture_archive_sha256']
for n in ['operation-counts.json','fixture-union-plan.json','whole-fixture-inventory.json','whole-case-selection.json']:
 assert sha(F/n)==oldprepared['artifacts'][n]
write(E/'fixture-union-plan.json',{'operations':103,'cases':7514,'whole_files':100,'new_operations':0,'new_cases':0,'partial_files':0,'duplicate_ids':0,'source':'Exact inherited103 union; this performance prototype adds no frontend routes','source_plan':str(F/'fixture-union-plan.json'),'source_plan_sha256':sha(F/'fixture-union-plan.json'),'operation_counts':str(F/'operation-counts.json'),'operation_counts_sha256':sha(F/'operation-counts.json'),'original_whole_fixture_archive':str(fixture),'original_whole_fixture_archive_sha256':fixturehash,'new_fixture_inventory_scan':False})
with tarfile.open(E/'source-102.tar.gz','w:gz') as t:
 for rel in sorted(files):t.add(S/rel,arcname=rel,recursive=False)
with tarfile.open(E/'source-102.tar.gz') as t:
 actual={m.name:hashlib.sha256(t.extractfile(m).read()).hexdigest() for m in t.getmembers() if m.isfile()}
assert actual==newfiles
for rel,h in files.items():assert sha(B/rel)==h
for rel,h in newfiles.items():assert sha(S/rel)==h
write(E/'provenance.json',{'base_source':str(B),'base102_manifest':paths['base_manifest'],'base_manifest_sha256':sha(Path(paths['base_manifest'])),'base_generic':{'image':'/home/legolas/rook2/evidence/ordered-q-seeded103-combined-generic-build-20261018/rook2-exact','sha256':'1befaa6d9c439d3d806e6e189a27756ab86f4c5b5ce3b74f59ed302d98ee5c0d','validation':'native158/strict54/wire24/DIAG175/7514/103/100 accepted, this new candidate unrun'},'base_parent_review':'/home/legolas/rook2/evidence/ordered-q-seeded103-combined-parent-review-20261018/codegen-judgment.json','base_prior_phase1_and_phase2_provenance':'Entire inherited102file source from accepted combined103bits; no root105 rebase, root scheduler, known-check, or other prototype adopted','prior_feasibility':'/home/legolas/rook2/evidence/q-projected-plane-transport-review-20261018/review.md','live_pilot_source_only_boundaries':'Small source/text edits began while40749/82e536 live; no native/hash/archive/fixtureinventory/Git until formal parent CPU+independent closure b0ddb2/b58182 and metadata5f85ed0','freeze_scope':'Source-only metadata/archives explicitly authorized after closure; no Rust parsing/compilation/test/engine/codegen/PGO/profiler','root_and_frozen_sources_unchanged':True,'native_artifacts_new':0,'source_fixes_after_execution':0})
prepared={'status':'FROZEN SOURCE-ONLY UNRUN; no adoption/performance claim','source':str(S),'base':str(B),'source_files':102,'native43':43,'tools23':23,'diagnostic36':36,'changed_files':sorted(changed),'native_declarations_expected':161,'lib_expected':159,'dev_expected':2,'diagnostic_declarations_expected':175,'operation_count':103,'case_count':7514,'whole_fixture_files':100,'rust_parse_compile_test_engine_codegen_pgo_profiler_runs':0,'source_archive_sha256':sha(E/'source-102.tar.gz'),'source_graph_sha256':hashlib.sha256(json.dumps(newfiles,sort_keys=True,separators=(',',':')).encode()).hexdigest(),'patch_sha256':sha(E/'trial.patch'),'proof_sha256':sha(E/'source-proof.json'),'all_parent_source_stable':True,'affinity':sorted(os.sched_getaffinity(0)),'TMPDIR':os.environ['TMPDIR']}
write(E/'prepared.json',prepared)
print(json.dumps(prepared,indent=2))
