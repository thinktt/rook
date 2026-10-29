#!/usr/bin/env python3
"""Freeze the one selected source/tool preparation without launching a process."""
import difflib
import json
from pathlib import Path
import subprocess
import sys

sys.dont_write_bytecode=True


def forbidden(*_args,**_kwargs): raise AssertionError('source freeze may not launch a process')


for name in ['Popen','run','call','check_call','check_output']: setattr(subprocess,name,forbidden)

from common import (HERE,ROOT,DEFAULT_CRATE,CONTROL_CRATE,CONTROL_EXPERIMENT,CONTROL_RAW,
    baseline,code_paths,preparation,read,retained_control_tests,reused_evidence_paths,sha,snapshot)
from source_check import check


def main():
    before,after=snapshot(CONTROL_CRATE),snapshot(DEFAULT_CRATE)
    assert len(before)==len(after)==69 and before.keys()==after.keys()
    changed=sorted(name for name in before if before[name]!=after[name])
    assert changed==['src/colors_worker.rs']
    source_check=check()
    policy=read(HERE/'policy.json')
    focused=policy['focused']
    assert len(focused)==1 and focused[0]['selector']=='colors_worker::lifecycle_tests'
    assert focused[0]['expectedPassed']==32
    focused[0]['expectedTests']=source_check['affectedWorkerTests']
    # Only these source-derived policy fields are refreshed; all selected bounds
    # and placement remain the parent's frozen policy.
    policy.update(sourceFiles=69,sourceChanged=changed,sourceAdded=[],focused=focused)
    (HERE/'policy.json').write_text(json.dumps(policy,indent=2)+'\n')
    name=changed[0]
    patch=difflib.unified_diff((CONTROL_CRATE/name).read_text().splitlines(True),
        (DEFAULT_CRATE/name).read_text().splitlines(True),fromfile='a/'+name,tofile='b/'+name,n=0)
    (HERE/'source.patch').write_text(''.join(patch))
    lead=Path('/home/legolas/agent-memos/imp2-lead-to-imp2-completion-epoch-generic-discriminator-20261029.md')
    design=ROOT/'docs/research/completion-epoch-publication.md'
    inputs=code_paths()+[HERE/'plan.md',HERE/'policy.json',HERE/'ownership-proof.md',HERE/'source.patch',lead,design]
    record=read(CONTROL_RAW/'prepared-run.json')
    value=dict(schema='rook2-completion-epoch-source-preparation-v1',
        baseSourceCheckpoint='19a1c1b83f6875064afc0b1677cb0c3e6d5bf303',
        designCheckpoint=policy['base'],candidateCrate=str(DEFAULT_CRATE),controlCrate=str(CONTROL_CRATE),
        controlSource=before,candidateSource=after,sourceChanges=changed,sourceAdded=[],sourceRemoved=[],
        protectedArtifacts=baseline(),focused=focused,
        readinessSemantics=read(CONTROL_EXPERIMENT/'preparation.json')['readinessSemantics'],
        evidenceReuse=dict(priorGenericPassed=70,affectedExisting=27,newWorkerControls=5,rerun=32,retained=43,
            retainedTestIdentities=retained_control_tests(record),
            priorTestExecutionSummary=record['testExecutionSummary'],
            priorTestRepair=read(CONTROL_EXPERIMENT/'preparation.json')['repair'],
            scope='43 unchanged passing single-owner controls reused, including the fixture-only repair;27 existing and5 targeted worker controls selected fresh; no full suite'),
        sourceChallenge=dict(sourceBodyCheck=source_check,ownershipProof=str(HERE/'ownership-proof.md'),
            sourceDesign=str(design),selectedAssignment=str(lead),
            strongDonePublication=True,normalFlagLoadOnly=True,coldDoneSeqCst=True,hotAcquireUnchanged=True,coldTerminalRmwUnchanged=True,
            retainedActualRetirement=True,noHotCensus=True,noPerLifeLayoutQuery=True),
        reusedEvidenceSha256={str(path):sha(path) for path in reused_evidence_paths()},
        inputSha256={str(path):sha(path) for path in sorted(set(inputs))},
        scope='one completion-epoch generic48+4; unchanged owned inputs/numerics/observations/spins/activation; no PGO/qualification/adoption')
    destination=HERE/'preparation.json'
    destination.write_text(json.dumps(value,indent=2)+'\n')
    assert preparation(destination)==value
    print(json.dumps(dict(sourceFiles=69,changed=changed,focusedSelected=32,retainedControls=43,
        protectedArtifacts=len(value['protectedArtifacts']),inputPins=len(value['inputSha256']),
        reusedPins=len(value['reusedEvidenceSha256']),preparationSha256=sha(destination)),indent=2))


if __name__=='__main__': main()
