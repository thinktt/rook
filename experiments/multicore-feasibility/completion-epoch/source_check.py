"""Source-only completion-order admission and exact test identities; no process.

Normal done/flag publication and the cold predicate change. All other worker
code and declarations remain fixed; the separate mixed-order proof is necessary.
"""
from pathlib import Path
import hashlib
import json
import re

CONTROL=Path('/home/legolas/rook2-experiments/workspaces/single-owner-20261028-01')
CANDIDATE=Path('/home/legolas/rook2-experiments/workspaces/completion-epoch-20261029-01')
FUNCTIONS=['compute_input','both_done','dispatch','owner_ready','is_complete_now','complete',
    'activate','restore_activation','claim_discard','retire_flight','park','wait_control',
    'signal_completion','publish_terminal','shutdown','failed_spawn','drop','layout_projection']
TYPES=['Packet','SideOutput','Metadata','Flight','OwnerState','Metric','Readiness','Cells']
NEW_TESTS=[
    'colors_completion_epoch_normal_load_before_and_around_registration_each_reader',
    'colors_completion_epoch_owed_normal_wake_survives_exit_and_new_generation',
    'colors_completion_epoch_two_true_loaders_keep_both_wake_obligations',
    'colors_completion_epoch_spurious_wake_reregisters_before_normal_load',
    'colors_completion_epoch_terminal_exchange_preserves_owed_normal_wake',
]


def digest(data): return hashlib.sha256(data).hexdigest()


def snapshot(crate):
    paths=[crate/'Cargo.toml',crate/'Cargo.lock']+sorted(p for p in (crate/'src').rglob('*') if p.is_file())
    paths += [crate/name for name in ['build.rs','rust-toolchain','rust-toolchain.toml'] if (crate/name).is_file()]
    return {str(path.relative_to(crate)):digest(path.read_bytes()) for path in paths}


def extract(text,name):
    match=re.search(r'^([ ]{0,4})(?:(?:pub\(crate\)|unsafe) )?fn '+name+r'\b',text,re.M)
    assert match,name
    first=text[match.start():].splitlines()[0]
    if first.rstrip().endswith('}'): return first
    end=re.search(r'^'+match[1]+r'}$',text[match.end():],re.M)
    assert end,name
    return text[match.start():match.end()+end.end()]


def check(control=CONTROL,candidate=CANDIDATE):
    control,candidate=Path(control),Path(candidate)
    before,after=snapshot(control),snapshot(candidate)
    assert before.keys()==after.keys() and len(before)==len(after)==69
    assert [name for name in sorted(before) if before[name]!=after[name]]==['src/colors_worker.rs']
    unchanged={name:before[name] for name in before if name!='src/colors_worker.rs'}
    old=(control/'src/colors_worker.rs').read_text();new=(candidate/'src/colors_worker.rs').read_text()
    functions={}
    for name in FUNCTIONS:
        original,changed=extract(old,name),extract(new,name)
        assert original==changed,name
        functions[name]=digest(original.encode())
    types={}
    for name in TYPES:
        pattern=r'^(?:struct|enum) '+name+r'\b[\s\S]*?^}'
        original,changed=re.search(pattern,old,re.M),re.search(pattern,new,re.M)
        assert original and changed and original[0]==changed[0],name
        types[name]=digest(original[0].encode())
    def code(body): return '\n'.join(line for line in body.splitlines() if not line.lstrip().startswith('//'))
    old_active,new_active=code(extract(old,'run_active')),code(extract(new,'run_active'))
    old_store='reader.done.store(generation, Ordering::Release);'
    new_store='reader.done.store(generation, Ordering::SeqCst);'
    assert old_active.count(old_store)==new_active.count(new_store)==1
    normal_block="""            let waiting = shared.latch.waiting.load(Ordering::SeqCst);
            #[cfg(test)]
            test_pause(shared, &shared.tests.after_latch[side]);
            if waiting {
                let _sleep = shared.waits.sleep.lock().unwrap_or_else(|error| error.into_inner());
                shared.waits.completed.notify_all();
                #[cfg(test)]
                shared.tests.normal_notifications[side].fetch_add(1, Ordering::SeqCst);
            }"""
    assert new_active.count(normal_block)==1
    restored=new_active.replace(new_store,old_store).replace(normal_block,'            signal_completion(shared);')
    assert restored==old_active,'normal path differs outside the two designated seams'
    hot=extract(new,'both_done');cold=extract(new,'both_done_cold')
    assert cold==hot.replace('fn both_done(', 'fn both_done_cold(').replace('Ordering::Acquire','Ordering::SeqCst')
    old_wait,new_wait=code(extract(old,'wait_completion')),code(extract(new,'wait_completion'))
    assert new_wait.count('let done = both_done_cold(shared, generation);')==1
    assert new_wait.replace('let done = both_done_cold(shared, generation);','let done = both_done(shared, generation);')==old_wait
    assert new.count('both_done_cold(')==2,'cold SC predicate must have exactly its one cold caller'
    assert new_active.count('.latch.waiting.')==1 and '.latch.waiting.swap(' not in new_active
    assert 'fence(' not in new_active
    # Existing declaration extraction includes repr/cfg attributes and excludes
    # test-only types; no compiled geometry inference is substituted for layout.
    import importlib.util
    helper_path=Path('/home/legolas/rook2-multicore/experiments/multicore-feasibility/completion-fence/lowering.py')
    spec=importlib.util.spec_from_file_location('completion_epoch_declarations',helper_path)
    helper=importlib.util.module_from_spec(spec);spec.loader.exec_module(helper)
    old_declarations,new_declarations=helper.declarations(control/'src/colors_worker.rs'),helper.declarations(candidate/'src/colors_worker.rs')
    assert old_declarations==new_declarations,'production declaration/layout drift'
    production_types={name:digest(value) for name,value in old_declarations.items()}
    assert old.count('unsafe impl Sync')==new.count('unsafe impl Sync')==1
    assert re.search(r'unsafe impl Sync for Cells\b',new)
    assert 'fence(Ordering::SeqCst)' not in new
    def tests(text):
        group=text[text.index('mod lifecycle_tests {'):]
        return sorted(re.findall(r'^    fn (colors_[A-Za-z0-9_]+)\(',group,re.M))
    original_tests,new_tests=tests(old),tests(new)
    assert len(original_tests)==len(set(original_tests))==27
    assert len(new_tests)==len(set(new_tests))==32
    assert set(original_tests)<=set(new_tests)
    assert sorted(set(new_tests)-set(original_tests))==sorted(NEW_TESTS)
    for name in original_tests: assert extract(old,name)==extract(new,name),name
    prefix='colors_worker::lifecycle_tests::'
    return dict(unchangedSourceSha256=unchanged,identicalWorkerFunctionSha256=functions,
        identicalWorkerTypeSha256=types,narrowCellsSyncCount=1,
        productionDeclarationSha256=production_types,
        completionOrderAdmission=dict(normalDone='SeqCst',normalFlag='SeqCst load only; true owes unconditional Sleep/notify',
            coldDone='SeqCst equality after original SC registration',hotDone='unchanged Acquire equality',
            coldTerminalHelperAndCallersUnchanged=True,oldWorkerTestBodiesUnchanged=27),
        existingWorkerTests=[prefix+name for name in original_tests],
        targetedWorkerTests=[prefix+name for name in sorted(NEW_TESTS)],
        affectedWorkerTests=[prefix+name for name in new_tests],
        scope='68 unchanged source files, unchanged production declarations/terminal callers/hot Acquire/27 old tests; only explicit normal publication and cold predicate seams normalized; source admission supports but does not replace the mixed-order proof or actual lowering/native controls')


if __name__=='__main__': print(json.dumps(check(),indent=2))
