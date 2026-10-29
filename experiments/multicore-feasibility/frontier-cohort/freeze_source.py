#!/usr/bin/env python3
"""Freeze source, tool and bounded serialization identities; no native work."""
import difflib
import json
import os
import subprocess
import sys
sys.dont_write_bytecode=True

def forbidden(*_args,**_kwargs):raise AssertionError('source freeze cannot launch a process')
for name in ['Popen','run','call','check_call','check_output']:setattr(subprocess,name,forbidden)
for name in dir(os):
    if name.startswith(('exec','spawn','posix_spawn')) or name=='system':setattr(os,name,forbidden)
from common import (HERE,CRATE,CONTROL_CRATE,CHANGED,ADDED,OPTIONS,TESTS,MEMOS,SERIALIZATION,count,
    baseline,code_paths,preparation,read,reused_paths,sha,source_admission)

def main():
    before,after=source_admission();policy=read(HERE/'policy.json');patches=[]
    for name in sorted(CHANGED+ADDED):
        old=(CONTROL_CRATE/name).read_text().splitlines(True) if name in before else []
        patches+=list(difflib.unified_diff(old,(CRATE/name).read_text().splitlines(True),
            fromfile='a/'+name if name in before else '/dev/null',tofile='b/'+name,n=0))
    (HERE/'source.patch').write_text(''.join(patches))
    paths=code_paths()+[HERE/'plan.md',HERE/'policy.json',HERE/'source-review.md',HERE/'source.patch']+MEMOS
    value=dict(schema='rook2-frontier-cohort-preparation-v1',candidateCrate=str(CRATE),controlCrate=str(CONTROL_CRATE),
        assignmentCheckpoint=policy['base'],controlSource=before,candidateSource=after,sourceChanges=CHANGED,
        sourceAdded=ADDED,sourceRemoved=[],focused=dict(target=['--lib'],selector='frontier_cohort::tests',expectedTests=TESTS,expectedPassed=6),
        reusedAggregateTests=count.TESTS,serialization=SERIALIZATION,case='profile-35',options=OPTIONS,
        pipelineSeconds=1800,perLifeSeconds=180,protectedArtifacts=baseline(),
        inputSha256={str(path):sha(path) for path in sorted(set(paths))},
        reusedEvidenceSha256={str(path):sha(path) for path in sorted(set(reused_paths()))},
        scope='Two original35 replays and cold expansion; streaming ID/time/accounting audit; typed identities and kernel values assured by frozen source/controls; no producer, readiness or speed claim')
    path=HERE/'preparation.json';path.write_text(json.dumps(value,indent=2)+'\n');assert preparation(path)==value
    print(json.dumps(dict(sourceFiles=len(after),freshFocusedExpected=6,reusedAggregateControls=6,replayLives=2,
        protectedArtifacts=len(value['protectedArtifacts']),inputPins=len(value['inputSha256']),preparationSha256=sha(path)),indent=2))

if __name__=='__main__':main()
