"""Source-only preservation and exact worker-test identity check; no process.

Registration, signal routing and wait bodies intentionally change. This checks
unchanged inputs, numeric/activation/retirement bodies and narrow Cells Sync;
the separate reviewed SC registration proof remains necessary.
"""
from pathlib import Path
import hashlib
import json
import re

CONTROL=Path('/home/legolas/rook2-experiments/workspaces/single-owner-20261028-01')
CANDIDATE=Path('/home/legolas/rook2-experiments/workspaces/per-reader-completion-20261029-01')
FUNCTIONS=['compute_input','both_done','dispatch','owner_ready','is_complete_now','complete',
    'activate','restore_activation','claim_discard','retire_flight','park','wait_control']
TYPES=['Packet','SideOutput','Metadata','Flight','OwnerState','Metric','Readiness','Cells']
NEW_TESTS=[
    'colors_each_reader_publication_before_between_after_both_registrations',
    'colors_stale_true_notifier_remains_owed_across_generations',
    'colors_two_true_reader_notifiers_pending_on_sleep',
    'colors_spurious_wake_reregisters_both_before_predicates',
    'colors_each_reader_terminal_before_between_after_both_registrations',
    'colors_owner_terminal_before_between_after_both_registrations',
    'colors_all_reader_signal_evaluates_second_exchange_after_true_first',
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
        if name=='dispatch':
            before_call='            signal_completion(&self.shared);'
            after_call='            signal_all(&self.shared);'
            assert original.count(before_call)==changed.count(after_call)==1
            changed=changed.replace(after_call,before_call)
        assert original==changed,name
        functions[name]=digest(original.encode())
    types={}
    for name in TYPES:
        pattern=r'^(?:struct|enum) '+name+r'\b[\s\S]*?^}'
        original,changed=re.search(pattern,old,re.M),re.search(pattern,new,re.M)
        assert original and changed and original[0]==changed[0],name
        types[name]=digest(original[0].encode())
    assert old.count('unsafe impl Sync')==new.count('unsafe impl Sync')==1
    assert re.search(r'unsafe impl Sync for Cells\b',new)
    assert 'fence(Ordering::SeqCst)' not in new
    def tests(text):
        group=text[text.index('mod lifecycle_tests {'):]
        return sorted(re.findall(r'^    fn (colors_[A-Za-z0-9_]+)\(',group,re.M))
    original_tests,new_tests=tests(old),tests(new)
    assert len(original_tests)==len(set(original_tests))==27
    assert len(new_tests)==len(set(new_tests))==34
    assert set(original_tests)<=set(new_tests)
    assert sorted(set(new_tests)-set(original_tests))==sorted(NEW_TESTS)
    prefix='colors_worker::lifecycle_tests::'
    return dict(unchangedSourceSha256=unchanged,identicalWorkerFunctionSha256=functions,
        identicalWorkerTypeSha256=types,narrowCellsSyncCount=1,
        normalizedDispatchStatement=dict(before='signal_completion(&self.shared);',after='signal_all(&self.shared);',occurrences=1),
        existingWorkerTests=[prefix+name for name in original_tests],
        targetedWorkerTests=[prefix+name for name in sorted(NEW_TESTS)],
        affectedWorkerTests=[prefix+name for name in new_tests],
        scope='68 complete unchanged source files and selected unchanged worker kernels/ownership bodies; changed registration/wait/terminal routing needs the reviewed separate per-flag SC proof and focused native controls')


if __name__=='__main__': print(json.dumps(check(),indent=2))
