#!/usr/bin/env python3
"""Freeze the selected source/tool identities and exact focused rows; no process."""
import difflib
import json
from pathlib import Path
import subprocess
import sys
sys.dont_write_bytecode=True


def forbidden(*_args,**_kwargs):raise AssertionError('source freeze may not launch a process')


for name in ['Popen','run','call','check_call','check_output']:setattr(subprocess,name,forbidden)
from common import (HERE,ROOT,DEFAULT_CRATE,CONTROL_CRATE,CONTROL_EXPERIMENT,CONTROL_RAW,
    baseline,code_paths,preparation,read,retained_control_tests,reused_evidence_paths,sha,snapshot)
from source_check import CHANGED,ADDED,check,focused_tests


def main():
    before,after=snapshot(CONTROL_CRATE),snapshot(DEFAULT_CRATE);source_check=check()
    changed=sorted(name for name in before if before[name]!=after[name])
    assert changed==CHANGED and sorted(after.keys()-before.keys())==ADDED
    policy=read(HERE/'policy.json');focused=policy['focused']
    assert focused
    for row in focused:
        identities=focused_tests(row)
        assert len(identities)==row['expectedPassed'],(row['selector'],len(identities),row['expectedPassed'])
        if 'expectedTests' in row:assert row['expectedTests']==identities
        row['expectedTests']=identities
    assert len({name for row in focused for name in row['expectedTests']})==sum(row['expectedPassed'] for row in focused),'overlapping focused filters'
    policy.update(sourceFiles=70,sourceChanged=changed,sourceAdded=ADDED,focused=focused)
    (HERE/'policy.json').write_text(json.dumps(policy,indent=2)+'\n')
    patches=[]
    for name in sorted(changed+ADDED):
        original=(CONTROL_CRATE/name).read_text().splitlines(True) if name in before else []
        patches += list(difflib.unified_diff(original,(DEFAULT_CRATE/name).read_text().splitlines(True),
            fromfile='a/'+name if name in before else '/dev/null',tofile='b/'+name,n=0))
    (HERE/'source.patch').write_text(''.join(patches))
    record=read(CONTROL_RAW/'prepared-run.json');prior=read(CONTROL_EXPERIMENT/'preparation.json')
    reuse=dict(policy['evidenceReuse'])
    reuse.update(priorGenericPassed=70,priorTestExecutionSummary=record['testExecutionSummary'],priorTestRepair=prior['repair'],
        rerun=sum(row['expectedPassed'] for row in focused))
    reuse['retainedTestIdentities']=sorted(reuse['retainedTestIdentities'])
    assert set(reuse['retainedTestIdentities'])<=set(retained_control_tests(record))
    reuse['retained']=len(reuse['retainedTestIdentities'])
    semantics=dict(prior['readinessSemantics'])
    semantics.update(publicationInterval='request_before_optional_geometry_and_map_wait',
        changedBoundary='reader ready/kernel intervals include geometry preparation and map waiting; residual join is not saved work',
        mapReadyWitness='real joined map_ready_epoch; staged protocol positive, new unstaged3/three-thread idle zero; disabled/missing dormant reports are None; no hot census')
    lead=Path('/home/legolas/agent-memos/imp2-lead-to-imp2-pre-map-geometry-generic-20261029.md')
    design=ROOT/'docs/research/pre-map-activity-geometry.md'
    inputs=code_paths()+[HERE/'plan.md',HERE/'policy.json',HERE/'ownership-proof.md',HERE/'source.patch',lead,design]
    value=dict(schema='rook2-pre-map-geometry-source-preparation-v1',baseSourceCheckpoint='19a1c1b83f6875064afc0b1677cb0c3e6d5bf303',
        designCheckpoint=policy['base'],candidateCrate=str(DEFAULT_CRATE),controlCrate=str(CONTROL_CRATE),
        controlSource=before,candidateSource=after,sourceChanges=changed,sourceAdded=ADDED,sourceRemoved=[],
        protectedArtifacts=baseline(),focused=focused,readinessSemantics=semantics,evidenceReuse=reuse,
        sourceChallenge=dict(sourceBodyCheck=source_check,ownershipProof=str(HERE/'ownership-proof.md'),sourceDesign=str(design),
            selectedAssignment=str(lead),fixedPrivateCallerReviewRequired=True,noGeneralCancellationApi=True,noPerLifeLayoutQuery=True),
        reusedEvidenceSha256={str(path):sha(path) for path in reused_evidence_paths()},
        inputSha256={str(path):sha(path) for path in sorted(set(inputs))},
        scope='one pre-map geometry generic60+5; whole-feature/common-path drift, no isolated phase-savings, PGO, qualification or adoption')
    destination=HERE/'preparation.json';destination.write_text(json.dumps(value,indent=2)+'\n')
    assert preparation(destination)==value
    print(json.dumps(dict(sourceFiles=70,changed=changed,added=ADDED,focusedSelected=reuse['rerun'],retained=reuse['retained'],
        protectedArtifacts=len(value['protectedArtifacts']),inputPins=len(value['inputSha256']),reusedPins=len(value['reusedEvidenceSha256']),preparationSha256=sha(destination)),indent=2))


if __name__=='__main__':main()
