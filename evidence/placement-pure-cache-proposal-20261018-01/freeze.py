from pathlib import Path
import hashlib, json, difflib, re, tarfile
E = Path(__file__).resolve().parent
P = json.loads((E / 'paths.json').read_text())
S, B = Path(P['source']), Path(P['basis'])
def sha(data): return hashlib.sha256(data).hexdigest()
def emit(name, value):
    (E / name).write_text(json.dumps(value, sort_keys=True, indent=2) + '\n')
def files(root):
    return sorted([Path('Cargo.toml'), Path('Cargo.lock')] +
        [q.relative_to(root) for d in ['src','tools'] for q in (root/d).rglob('*')
         if q.is_file() and '__pycache__' not in q.parts])
rels = files(S)
assert rels == files(B) and len(rels) == 69
before = {str(r): sha((B/r).read_bytes()) for r in rels}
after = {str(r): sha((S/r).read_bytes()) for r in rels}
changed = [r for r in before if before[r] != after[r]]
assert changed == ['src/activity.rs','src/evaluator.rs','src/ordinary.rs','src/quiescence.rs','src/shelter.rs'], changed
native = {k:v for k,v in after.items() if not k.startswith('tools/')}
tools = {k:v for k,v in after.items() if k.startswith('tools/')}
assert (len(native),len(tools)) == (46,23)
for side, root in [('basis',B),('proposed',S)]:
    for name in changed:
        q=E/side/name; q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes((root/name).read_bytes())
patch = ''.join(''.join(difflib.unified_diff((B/r).read_text().splitlines(True),
    (S/r).read_text().splitlines(True),fromfile='a/'+r,tofile='b/'+r)) for r in changed)
inverse = ''.join(''.join(difflib.unified_diff((S/r).read_text().splitlines(True),
    (B/r).read_text().splitlines(True),fromfile='a/'+r,tofile='b/'+r)) for r in changed)
(E/'trial.patch').write_text(patch); (E/'inverse.patch').write_text(inverse)
# Exact inverse checks on every narrow production edit outside evaluator.
assert (S/'src/activity.rs').read_text().replace('pub(crate) fn weighted(', 'fn weighted(', 1) == (B/'src/activity.rs').read_text()
assert (S/'src/shelter.rs').read_text().replace('pub(crate) fn combine(', 'fn combine(', 1) == (B/'src/shelter.rs').read_text()
assert (S/'src/ordinary.rs').read_text().replace('self.evaluator.full_search(node, map, checked)', 'self.evaluator.full(node, map, checked)', 1) == (B/'src/ordinary.rs').read_text()
q=(S/'src/quiescence.rs').read_text().replace('self.evaluator.full_search(\n','self.evaluator.full(\n',1).replace('self.evaluator.select_noncheck_search_stages(','self.evaluator.select_noncheck_stages_observed(',1).replace('self.evaluator.select_noncheck_search(\n','self.evaluator.select_noncheck(\n',1)
assert q == (B/'src/quiescence.rs').read_text()
a=(S/'src/evaluator.rs').read_text();b=(B/'src/evaluator.rs').read_text()
# Entire preexisting test tail, Node/Retained owners, and full composition after
# the activity/shelter substitution remain literal old source.
old_tail=b[b.index('    fn initialized() -> (Evaluator, Node) {'):]
assert a[a.index('    fn initialized() -> (Evaluator, Node) {'):] == old_tail
assert a[:a.index('// This cache has a deliberately narrower domain')] == b[:b.index('pub struct Evaluator<const DIAGNOSTICS: bool = true>')]
start='        let structure = pawn_progress::structure_weighted('
end='    fn finish_observed<F: FnOnce(endgame::Finished)>('
assert a[a.index(start):a.index(end)] == b[b.index(start):b.index(end)]
assert a[a.index(end):a.index('    /// Select and refresh from the finished current-side score.')] == b[b.index(end):b.index('    /// Select and refresh from the finished current-side score.')]
# Pawn selection/material prefix before the cache probe is byte-identical.
start='        let position = &node.position;'
aa=a[a.index('    fn full_impl<'):];bb=b[b.index('    fn full_impl<'):]
assert aa[aa.index(start):aa.index('        // PawnCache selection')] == bb[bb.index(start):bb.index('        let activity = activity::compute')]
# Every old public map-accepting full/selector wrapper is forced CACHE=false.
for name in ['full','full_observed','fresh_observed','fresh_detailed_observed','full_detailed_observed']:
    match=re.search(r'    pub fn '+name+r'(?:<|\()',a); assert match,name
    segment=a[match.start():]; segment=segment[:segment.index('\n    }')]
    assert re.search(r'full_impl::<(?:false|true), false,',segment),name
for name in ['select_noncheck','select_noncheck_detailed_observed','select_noncheck_stages_observed']:
    match=re.search(r'    pub fn '+name+r'(?:<|\()',a);assert match,name
    segment=a[match.start():];segment=segment[:segment.index('\n    }')]
    assert re.search(r'select_noncheck_impl::<(?:false|true), (?:false|true), false,',segment),name
counts={}
for r in rels:
    if str(r).startswith('src/') and r.suffix == '.rs':
        names=re.findall(r'#\[test\]\s*fn\s+(\w+)',(S/r).read_text())
        if names:counts[str(r)]=names
lib=sum(len(v) for k,v in counts.items() if not k.startswith('src/bin/'))
dev=sum(len(v) for k,v in counts.items() if k.startswith('src/bin/'))
new=[n for n in counts['src/evaluator.rs'] if n.startswith('pure_cache_')]
assert (lib,dev,len(new)) == (182,2,6)
assert before['src/influence.rs']==after['src/influence.rs']
graph=sha(json.dumps(after,sort_keys=True,separators=(',',':')).encode())
ngraph=sha(json.dumps(native,sort_keys=True,separators=(',',':')).encode())
emit('source-manifest.json',{'schema':'relative-path-sha256-v1','graph_method':'SHA256 of canonical compact sorted JSON files object','graph_sha256':graph,'native_graph_sha256':ngraph,'counts':{'native_and_manifests':46,'tools':23,'total':69},'files':after})
emit('basis-source-manifest.json',{'basis':str(B),'files':before})
emit('test-declarations.json',{'executed':False,'library':lib,'development':dev,'native_total':lib+dev,'new':new,'by_file':counts})
emit('source-proof.json',{'source_only':True,'changed':changed,'unchanged_members':64,'Node_Retained_Position_AttackBits_unchanged':True,'activity_shelter_only_weighting_visibility':True,'ordinary_inverse_whole_file':True,'quiescence_inverse_whole_file':True,'old_evaluator_test_tail_equal':True,'full_pawn_prefix_equal':True,'full_composition_finish_suffix_equal':True,'fast_finish_whole_body_equal':True,'public_full_and_selector_CACHE_false_verified':True,'influence_entire_file_unchanged':True,'tools23_unchanged':True,'root69_equal_at_copy':P['root69_equal_at_copy'],'new_test_names':new})
archive=E/'source69.tar.gz'
with tarfile.open(archive,'w:gz') as tf:
    for r in rels:tf.add(S/r,arcname=str(r),recursive=False)
with tarfile.open(archive,'r:gz') as tf:
    assert sorted(tf.getnames()) == sorted(after)
    for m in tf.getmembers():assert m.isfile() and sha(tf.extractfile(m).read()) == after[m.name]
assert {str(r):sha((S/r).read_bytes()) for r in rels} == after
emit('archive-manifest.json',{'path':str(archive),'sha256':sha(archive.read_bytes()),'members':after,'member_count':69,'reopened_verified':True,'source_after_equal':True})
emit('prepared.json',{'complete_source_proposal':True,'executed_native':False,'source':str(S),'basis':str(B),'basis_authority':'parent current c3fd806fa fullbyte; all69 bytes compared equal at copy','source_graph_sha256':graph,'native_graph_sha256':ngraph,'source_manifest_sha256':sha((E/'source-manifest.json').read_bytes()),'source_members':69,'native_members':46,'tools_members':23,'changed_files':changed,'expected_native_tests':184,'expected_library_tests':182,'expected_development_tests':2,'new_tests':new,'patch_sha256':sha((E/'trial.patch').read_bytes()),'archive_sha256':sha(archive.read_bytes()),'cache':{'slots':1024,'expected_entry_bytes':64,'expected_entry_alignment':64,'expected_heap_payload_bytes':65536,'zero_key_sentinel':'private nonempty coherent valid-tag placement domain'},'generic_fixed70_rule':{'aggregate_max':0.995,'minimum_lower_case_medians':5,'worst_case_ratio_max':1.02,'failure':'park; no resize or retry'},'build_clearance':False,'test_clearance':False,'cpu_clearance':False})
print(json.dumps({'complete':True,'source':str(S),'graph':graph,'native_graph':ngraph,'source_files':69,'changed':changed,'native_test_declarations':184,'patch_sha256':sha((E/'trial.patch').read_bytes()),'archive_sha256':sha(archive.read_bytes())},sort_keys=True))
