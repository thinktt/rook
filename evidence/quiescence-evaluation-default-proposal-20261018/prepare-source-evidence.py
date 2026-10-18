from pathlib import Path
import hashlib,json,difflib,re
E=Path('/home/legolas/rook2/evidence/quiescence-evaluation-default-proposal-20261018')
Q=Path('/tmp/imp2-quiescence-evaluation-20261018-native-child')
N=Path('/tmp/imp2-quiescence-evaluation-default-20261018-native-child')
P=Path('/home/legolas/rook2/evidence/quiescence-evaluation-proposal-20261018')
B=P/'base'
def sha(v): return hashlib.sha256(v).hexdigest()
def dump(name,obj): (E/name).write_text(json.dumps(obj,indent=2,sort_keys=True)+'\n')
qm=json.loads((P/'proposal-source-sha256.json').read_text())
bm=json.loads((P/'base-source-sha256.json').read_text())
assert all(sha((Q/k).read_bytes())==v for k,v in qm.items())
assert all(sha((B/k).read_bytes())==v for k,v in bm.items())
nm={k:sha((N/k).read_bytes()) for k in qm}
changed_q=[k for k in nm if nm[k]!=qm[k]]
assert changed_q==['src/evaluator.rs'],changed_q
changed_b=[k for k in nm if nm[k]!=bm.get(k)]
assert changed_b==['diagnostic/src/main.rs','diagnostic/src/quiescence_evaluation.rs','src/evaluator.rs','src/quiescence.rs','src/quiescence_policy.rs'],changed_b
bs=(B/'src/evaluator.rs').read_text(); qs=(Q/'src/evaluator.rs').read_text(); ns=(N/'src/evaluator.rs').read_text()
def policy(s):
 start=s.index('        let sparse = node.position.counts.iter().all(|c| {')
 end=s.index('\n    }\n}\n\n#[cfg(test)]',start)
 return s[start:end]
bbody=policy(bs); qbody=policy(qs); nbody=policy(ns)
pat=re.compile(r'if OBSERVE \{\n[ \t]*([^\n]+)\n[ \t]*\} else \{\n[ \t]*([^\n]+)\n[ \t]*\}')
assert len(list(pat.finditer(nbody)))==3
true_body=pat.sub(lambda m:m.group(1),nbody)
false_body=pat.sub(lambda m:m.group(2),nbody)
assert true_body==qbody
assert false_body==bbody
assert ns.count('if OBSERVE {')==3
assert ns.count('self.select_noncheck_impl::<false, _, _>(')==1
assert ns.count('self.select_noncheck_impl::<true, _, _>(')==1
assert ns.count('fn select_noncheck_impl<const OBSERVE: bool, F, G>(')==1
# All text outside the selection-method section must be unchanged from original Q.
start='    pub fn select_noncheck('
end='\n#[cfg(test)]'
assert ns[:ns.index(start)]==qs[:qs.index(start)]
assert ns[ns.index(end):]==qs[qs.index(end):]
for name,value in [('policy-const-true.txt',true_body),('policy-const-false.txt',false_body),('policy-shared.txt',nbody)]: (E/name).write_text(value+'\n')
dump('policy-source-comparison.json',{
 'normalization':'Replace exactly three if OBSERVE evaluation-call expressions with selected call text; no whitespace or condition normalization.',
 'const_true_exactly_equals_original_q_observed_body':true_body==qbody,
 'const_false_exactly_equals_retained82_default_body':false_body==bbody,
 'const_gate_count':3,'one_shared_policy_body':True,
 'default_const':False,'detailed_const':True,
 'true_body_sha256':sha(true_body.encode()),'false_body_sha256':sha(false_body.encode()),
 'shared_body_sha256':sha(nbody.encode()),
 'outside_selection_section_unchanged_from_q':True,
 'baseline_evaluator_sha256':bm['src/evaluator.rs'],
 'original_q_evaluator_sha256':qm['src/evaluator.rs'],
 'corrected_evaluator_sha256':nm['src/evaluator.rs']})
def diff(paths,old_root):
 chunks=[]
 for path in paths:
  old=(old_root/path).read_text().splitlines(keepends=True) if (old_root/path).exists() else []
  new=(N/path).read_text().splitlines(keepends=True)
  chunks.append(''.join(difflib.unified_diff(old,new,fromfile='a/'+path if old else '/dev/null',tofile='b/'+path)))
 return ''.join(chunks)
patches={
 'default-seam-from-q.patch':diff(changed_q,Q),
 'quiescence-evaluation-default.patch':diff(changed_b,B),
 'native.patch':diff([k for k in changed_b if k.startswith('src/')],B),
 'diagnostic.patch':diff([k for k in changed_b if k.startswith('diagnostic/')],B)}
for name,value in patches.items(): (E/name).write_text(value)
assert sha((E/'diagnostic.patch').read_bytes())==sha((P/'diagnostic.patch').read_bytes())
dump('proposal-source-sha256.json',nm)
dump('changed-from-q-sha256.json',{k:{'old':qm[k],'new':nm[k]} for k in changed_q})
dump('changed-from-retained82-sha256.json',{k:{'old':bm.get(k),'new':nm[k]} for k in changed_b})
dump('source-receipt.json',{
 'status':'cold source proposal; uncompiled and untested',
 'source_root':str(N),'prior_q_source_root':str(Q),'retained82_baseline':str(B),
 'changed_from_q':changed_q,'changed_from_retained82':changed_b,
 'prior_q_verified_unchanged':True,'baseline_verified_unchanged':True,
 'new_operations_beyond_original_q':0,
 'original_q_operations':['evaluation.quiescenceEntry','evaluation.quiescenceDisposition'],
 'original_q_cases':466,'original_q_result_records':7500,
 'original_q_test_sources_retained':{'native':3,'diagnostic':10},
 'selection_json_sha256':sha((P/'selection.json').read_bytes()),
 'patch_sha256':{name:sha((E/name).read_bytes()) for name in patches},
 'manifest_sha256':sha((E/'proposal-source-sha256.json').read_bytes()),
 'builds':0,'tests':0,'engine_runs':0,'compiler_invocations':0,'profilers':0,
 'binary_reads_during_pilot':0,
 'requested_model_effort_speed':'Sol 6.1 High Normal; actual speed unavailable'})
print(json.dumps({'source_root':str(N),'patches':{name:sha((E/name).read_bytes()) for name in patches},'manifest_sha256':sha((E/'proposal-source-sha256.json').read_bytes()),'evaluator_sha256':nm['src/evaluator.rs'],'const_projections_exact':True},indent=2))
