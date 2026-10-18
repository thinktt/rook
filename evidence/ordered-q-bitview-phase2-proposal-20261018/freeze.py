#!/usr/bin/env python3
"""Deferred source-only freeze. Run only after parent's CPU terminal clearance."""
from pathlib import Path
import datetime,hashlib,json,os,platform,re,shutil,tarfile
E=Path(__file__).resolve().parent
if (E/'prepared.json').exists():raise RuntimeError('Frozen proposal already exists; preserve it and use a new evidence version')
if not (E/'archive-clearance.json').exists():raise RuntimeError('Parent actual-terminal archive clearance required')
paths=json.loads((E/'paths.json').read_text());BASE=Path(paths['base']);SOURCE=Path(paths['source'])
def sha(data):return hashlib.sha256(data).hexdigest()
def h(path):return sha(path.read_bytes())
def emit(name,value):(E/name).write_text(json.dumps(value,indent=2,sort_keys=True)+'\n')
base_native=json.loads((E/'base-native43-sha256.json').read_text());base_tools=json.loads((E/'base-tools23-sha256.json').read_text())
assert (len(base_native),len(base_tools))==(43,23)
assert all(h(BASE/name)==value for name,value in {**base_native,**base_tools}.items())
native={name:h(SOURCE/name) for name in base_native};tools={name:h(SOURCE/name) for name in base_tools}
changed=[name for name,value in native.items() if value!=base_native[name]]
assert set(changed)=={'src/attacks.rs','src/movegen.rs','src/quiescence.rs'} and tools==base_tools
cold=json.loads((E/'cold-patch-review.json').read_text());assert all(h(SOURCE/name)==value for name,value in cold['changed_files'].items())
assert all(h(E/name)==value for name,value in cold['patches'].items())
q=(SOURCE/'src/quiescence.rs').read_text();inverse=q
for new,old in [
('                let projected = position.attack_view().projected(&position, movement);','                let board = movegen::projected_board(&position, movement);'),
('                    movegen::check_routes_bits(&projected, enemy_king, position.side, movement.to());','                    movegen::check_routes(&board, enemy_king, position.side, movement.to());'),
('                if projected.attacked(king_after, position.side.opponent()) {','                if movegen::attacked(&board, king_after, position.side.opponent()) {')]:
    assert inverse.count(new)==1;inverse=inverse.replace(new,old)
assert inverse==(BASE/'src/quiescence.rs').read_text()
attacks=(SOURCE/'src/attacks.rs').read_text();old_attacks=(BASE/'src/attacks.rs').read_text()
assert attacks.split('\n#[cfg(test)]\n',1)[0]==old_attacks.split('\n#[cfg(test)]\n',1)[0]
marker='\n    /// Compare before own-king legality:';index=attacks.index(marker)
assert attacks[:index]+attacks[attacks.rfind('\n}'):]==old_attacks
movegen=(SOURCE/'src/movegen.rs').read_text();a=movegen.index('/// Q supplies its one projected tag-plane view.');b=movegen.index('/// The tactical caller supplies a projected board',a)
stripped=movegen[:a]+movegen[b:];stripped=stripped.replace('#[cfg(test)]\npub(crate) fn check_routes(', 'pub(crate) fn check_routes(',1)
assert stripped==(BASE/'src/movegen.rs').read_text()
emit('native43-sha256.json',native);emit('tools23-sha256.json',tools)
emit('source-manifest.json',{'native43':native,'tools23':tools,'native43_graph_sha256':sha(json.dumps(native,sort_keys=True,separators=(',',':')).encode()),'tools23_graph_sha256':sha(json.dumps(tools,sort_keys=True,separators=(',',':')).encode())})
def tests(root):return {name:re.findall(r'#\[test\]\s*fn\s+(\w+)',(root/name).read_text()) for name in base_native if name.endswith('.rs')}
before=tests(BASE);after=tests(SOURCE)
assert sum(map(len,before.values()))==143 and sum(map(len,after.values()))==145
assert len(before['src/bin/rook2-dev.rs'])==len(after['src/bin/rook2-dev.rs'])==2
added={name:[test for test in names if test not in before[name]] for name,names in after.items()};added={name:value for name,value in added.items() if value}
assert set(added)=={'src/attacks.rs'} and len(added['src/attacks.rs'])==2
assert all(set(names).issubset(after[name]) for name,names in before.items())
emit('test-source-inventory.json',{'status':'declaration counts only; uncompiled/unexecuted','base_native_units':143,'expected_native_units':145,'expected_library_units':143,'expected_development_units':2,'added':added,'tests':after})
files={**native,**tools}
for name in files:
    target=E/'proposal-source'/name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(SOURCE/name,target)
with tarfile.open(E/'source-native43-tools23.tar.gz','w:gz') as archive:
    for name in sorted(files):archive.add(SOURCE/name,arcname=name,recursive=False)
with tarfile.open(E/'source-native43-tools23.tar.gz') as archive:
    members=archive.getmembers();assert len(members)==66 and len({m.name for m in members})==66
    assert all(m.isfile() and sha(archive.extractfile(m).read())==files[m.name] for m in members)
authority=Path('/home/legolas/rook2/evidence/ordered-bit-checkers-review-20261018/review-phase1-phase2-20261018T092625Z-3b886e.md')
shutil.copyfile(authority,E/'authority-review.md')
identity=Path('/home/legolas/rook2/evidence/ordered-bit-checkers-phase1-validation-20261018/identity.json')
base_identity=json.loads(identity.read_text())
assert base_identity['native_sha256']=='132ba1356b06423763b4f6328825ef93b22b91ba374bc26ff92f0ef71e0e6c81'
emit('reference-manifest.json',{'authority':str(authority),'authority_sha256':h(authority),'base_prepared':paths['base_prepared'],'base_prepared_sha256':paths['base_prepared_sha256'],'base_identity':str(identity),'base_identity_sha256':h(identity),'declared_generic_control_sha256':base_identity['native_sha256'],'declared_generic_control_receipt_sha256':base_identity['native_build_receipt_sha256'],'binary_rehashed_or_executed':False})
manifest=json.loads((E/'source-manifest.json').read_text())
artifacts=['paths.json','base-native43-sha256.json','base-tools23-sha256.json','native43-sha256.json','tools23-sha256.json','source-manifest.json','proposal.patch','q-site.patch','route-owner.patch','pseudo-test-source.patch','scoped-source-proof.json','test-source-plan.json','test-source-inventory.json','source-native43-tools23.tar.gz','reference-manifest.json','authority-review.md','cold-patch-review.json','archive-clearance.json','review.md','freeze.py']
prepared={'status':'FROZEN SOURCE ONLY; parent review required; no native execution','created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'source':str(SOURCE),'base':str(BASE),'affinity':sorted(os.sched_getaffinity(0)),'python':platform.python_version(),'native43_graph_sha256':manifest['native43_graph_sha256'],'tools23_graph_sha256':manifest['tools23_graph_sha256'],'changed_native_paths':changed,'expected_native_units':145,'expected_library_units':143,'expected_development_units':2,'source_archive_members':66,'source_archive_verified_exact':True,'native_commands_launched':0,'build_test_engine_codegen_profiler_jobs':0,'performance_or_adoption_claim':False,'source_stable_after':all(h(SOURCE/name)==value for name,value in files.items()),'base_stable_after':all(h(BASE/name)==value for name,value in {**base_native,**base_tools}.items()),'artifacts':{name:h(E/name) for name in artifacts}}
assert prepared['source_stable_after'] and prepared['base_stable_after'];emit('prepared.json',prepared)
print(json.dumps({'source':str(SOURCE),'prepared_sha256':h(E/'prepared.json'),'native43':prepared['native43_graph_sha256'],'tools23':prepared['tools23_graph_sha256'],'proposal_patch_sha256':prepared['artifacts']['proposal.patch'],'source_archive_sha256':prepared['artifacts']['source-native43-tools23.tar.gz'],'expected_native_units':145,'source_stable':True,'base_stable':True},indent=2))
