#!/usr/bin/env python3
"""Freeze this one source/tool observation; never run a compiler or engine."""
import difflib
import json
from pathlib import Path
import subprocess
import sys
sys.dont_write_bytecode=True


def forbidden(*_args,**_kwargs):raise AssertionError('source freeze cannot launch a process')


for name in ['Popen','run','call','check_call','check_output']:setattr(subprocess,name,forbidden)
from common import (HERE,CRATE,CONTROL_CRATE,CHANGED,OPTIONS,TESTS,baseline,code_paths,preparation,
    read,reused_paths,sha,source_admission)


def main():
    before,after=source_admission();policy=read(HERE/'policy.json')
    patches=[]
    for name in sorted(CHANGED+['src/frontier_scale.rs']):
        old=(CONTROL_CRATE/name).read_text().splitlines(True) if name in before else []
        patches += list(difflib.unified_diff(old,(CRATE/name).read_text().splitlines(True),
            fromfile='a/'+name if name in before else '/dev/null',tofile='b/'+name,n=0))
    (HERE/'source.patch').write_text(''.join(patches))
    paths=code_paths()+[HERE/'plan.md',HERE/'policy.json',HERE/'source.patch',
        Path('/home/legolas/agent-memos/imp2-lead-to-imp2-frontier-scale-count-20261029.md')]
    paths += [HERE/'source-review.md']
    value=dict(schema='rook2-frontier-scale-count-preparation-v1',candidateCrate=str(CRATE),
        controlCrate=str(CONTROL_CRATE),baseSourceCheckpoint='19a1c1b83f6875064afc0b1677cb0c3e6d5bf303',
        assignmentCheckpoint=policy.get('base'),controlSource=before,candidateSource=after,
        sourceChanges=CHANGED,sourceAdded=['src/frontier_scale.rs'],sourceRemoved=[],
        focused=dict(target=['--lib'],selector='frontier_scale::tests',expectedTests=TESTS,expectedPassed=6),
        case='profile-35',options=OPTIONS,pipelineSeconds=900,perLifeSeconds=180,protectedArtifacts=baseline(),
        inputSha256={str(path):sha(path) for path in sorted(set(paths))},
        reusedEvidenceSha256={str(path):sha(path) for path in reused_paths()},
        scope='one aggregate observation; source/six tests assure counter domains, saved raw independently qualifies original wire/work/placement; no keys, services, consumer or timing comparison')
    path=HERE/'preparation.json';path.write_text(json.dumps(value,indent=2)+'\n');assert preparation(path)==value
    print(json.dumps(dict(sourceFiles=len(after),focusedPassedExpected=6,replayLives=1,case='profile-35',
        protectedArtifacts=len(value['protectedArtifacts']),inputPins=len(value['inputSha256']),preparationSha256=sha(path)),indent=2))


if __name__=='__main__':main()
