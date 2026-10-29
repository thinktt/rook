"""Bounded source/input/SC-completion admission; never starts a process.

Shared Activity arithmetic, the private caller eligibility and zero-depth borrow
proof require the parent's review and selected parity/lifetime controls. Hashes
below do not claim broad whole-function equivalence for the changed evaluator.
"""
from pathlib import Path
import hashlib
import json
import re

CONTROL=Path('/home/legolas/rook2-experiments/workspaces/single-owner-20261028-01')
CANDIDATE=Path('/home/legolas/rook2-experiments/workspaces/pre-map-geometry-20261029-01')
CHANGED=['src/activity.rs','src/bin/rook2.rs','src/colors_worker.rs','src/evaluator.rs','src/ordinary.rs','src/quiescence.rs','src/session.rs']
ADDED=['src/evaluator/pre_map_geometry_tests.rs']
FUNCTIONS=['both_done','signal_completion','wait_completion','publish_terminal','retire_flight','park','wait_control']
TYPES=['SideOutput','Control','OwnerState','LifecycleRegion','LatchRegion','WaitRegion','ControlRegion','Metric','Readiness']


def digest(data):return hashlib.sha256(data).hexdigest()


def snapshot(crate):
    paths=[crate/'Cargo.toml',crate/'Cargo.lock']+sorted(path for path in (crate/'src').rglob('*') if path.is_file())
    paths += [crate/name for name in ['build.rs','rust-toolchain','rust-toolchain.toml'] if (crate/name).is_file()]
    return {str(path.relative_to(crate)):digest(path.read_bytes()) for path in paths}


def extract(text,name):
    match=re.search(r'^([ ]{0,4})(?:(?:pub\(crate\)|unsafe) )?fn '+name+r'\b',text,re.M);assert match,name
    first=text[match.start():].splitlines()[0]
    if first.rstrip().endswith('}'):return first
    end=re.search(r'^'+match[1]+r'}$',text[match.end():],re.M);assert end,name
    return text[match.start():match.end()+end.end()]


def focused_tests(row,crate=CANDIDATE):
    """Resolve only this experiment's existing inline/file test-module shapes."""
    selector=row['selector'];parts=selector.split('::')
    exact=row.get('exact',False);module_parts=parts[:-1] if exact else parts
    if row['target']==['--bin','rook2']:
        path=Path(crate)/'src/bin/rook2.rs';text=path.read_text()
        if module_parts:
            name=module_parts[-1];match=re.search(r'\bmod '+re.escape(name)+r'\s*\{',text);assert match,selector
            text=text[match.end():]
    else:
        path=Path(crate)/'src'/('/'.join(module_parts)+'.rs')
        if path.is_file():text=path.read_text()
        else:
            assert len(module_parts)>=2,selector
            path=Path(crate)/'src'/('/'.join(module_parts[:-1])+'.rs')
            text=path.read_text();match=re.search(r'\bmod '+re.escape(module_parts[-1])+r'\s*\{',text);assert match,selector
            text=text[match.end():]
    names=re.findall(r'#\[test\]\s*(?:#\[[^\n]+\]\s*)*(?:pub(?:\([^)]*\))?\s+)?fn\s+(\w+)\s*\(',text)
    qualified=sorted('::'.join([*module_parts,name]) for name in names)
    assert qualified and len(qualified)==len(set(qualified)),selector
    if exact:
        assert selector in qualified,selector
        return [selector]
    return qualified


def check(control=CONTROL,candidate=CANDIDATE):
    control,candidate=Path(control),Path(candidate);before,after=snapshot(control),snapshot(candidate)
    assert len(before)==69 and len(after)==70
    assert sorted(name for name in before if before[name]!=after[name])==CHANGED
    assert sorted(after.keys()-before.keys())==ADDED and not before.keys()-after.keys()
    old=(control/'src/colors_worker.rs').read_text();new=(candidate/'src/colors_worker.rs').read_text()
    functions={}
    for name in FUNCTIONS:
        original,changed=extract(old,name),extract(new,name);assert original==changed,name
        functions[name]=digest(original.encode())
    types={}
    for name in TYPES:
        pattern=r'^(?:struct|enum) '+name+r'\b[\s\S]*?^}'
        original,changed=re.search(pattern,old,re.M),re.search(pattern,new,re.M)
        assert original and changed and original[0]==changed[0],name
        types[name]=digest(original[0].encode())
    assert new.count('unsafe impl Sync')==1 and re.search(r'unsafe impl Sync for Cells\b',new)
    for needle in ['value: UnsafeCell<Packet>','output: UnsafeCell<SideOutput>','sides: [SideRegion; 2]','value: UnsafeCell<Influence>','map: MapRegion']:
        assert needle in new,needle
    readers=extract(new,'compute_input')
    for needle in ['cells.input.value.get().write','cells.map.payload.value.get().write','&mut *shared.cells']:
        assert needle not in readers,needle
    assert 'let influence = unsafe { &*shared.cells.map.payload.value.get() };' in readers
    assert 'shared.cells.map.ready.epoch.load(Ordering::Acquire) == generation' in readers
    assert 'return Ok(InputOutcome::Abandoned);' in readers
    assert 'shared.lifecycle.active_scopes.load(Ordering::Acquire) == 0' in readers
    publish=extract(new,'publish_fresh_map')
    write='self.shared.cells.map.payload.value.get().write(*influence);'
    release='self.shared.cells.map.ready.epoch.store(token.generation, Ordering::Release);'
    assert publish.count(write)==publish.count(release)==1 and publish.index(write)<publish.index(release)
    assert 'metadata.generation != token.generation || !metadata.fresh' in publish
    active=extract(new,'run_active')
    assert 'reader.done.store(generation, Ordering::Release);' in active and 'signal_completion(shared);' in active
    assert 'Ordering::SeqCst' not in extract(new,'both_done')
    return dict(unchangedSourceSha256={name:before[name] for name in before if name not in CHANGED},
        identicalCompletionFunctionSha256=functions,identicalWorkerTypeSha256=types,
        unsafeCells=dict(count=4,narrowSyncImplementations=1,kind='one Packet, two SideOutput, one Influence; atomics outside UnsafeCell'),
        mapPublication=dict(ownerWriteBeforeExactRelease=True,helperExactAcquireAndDirectBorrow=True,
            zeroDepthAbandonedEndsBorrows=True,normalDoneReleaseAndOriginalScFlagRmw=True),
        ownerMode='metadata-fresh-position',
        scope='62 unchanged source files and selected exact completion/storage bodies; staged Activity parity/private eligibility/borrow cancellation and demanded work remain separately reviewed and tested')


if __name__=='__main__':print(json.dumps(check(),indent=2))
