#!/usr/bin/env python3
"""Freeze unchanged source and the existing own-PGO workflow; launches no process."""
import json
from pathlib import Path
import subprocess
import sys

sys.dont_write_bytecode = True


def forbidden(*_args, **_kwargs):
    raise AssertionError('PGO source preparation may not launch a process')


for name in ['Popen', 'run', 'call', 'check_call', 'check_output']:
    setattr(subprocess, name, forbidden)

from common import (HERE, ROOT, DEFAULT_CRATE, GENERIC, SOURCE_CHECKPOINT,
    LEAD_REVIEW, NAMES, TRAINING_MODES, baseline, code_paths, generic_evidence,
    preparation, read, reused_evidence_paths, sha, snapshot)


def main():
    source = snapshot(DEFAULT_CRATE)
    assert len(source) == 69 and source == read(GENERIC/'closure.json')['candidateSource']
    policy = read(HERE/'policy.json')
    assert policy['sourceCheckpoint'] == SOURCE_CHECKPOINT and policy['sourceFiles'] == 69
    assert policy['sourceChangeAllowed'] is False
    assert policy['comparison']['variants'] == NAMES
    assert policy['training']['modes'] == TRAINING_MODES
    inputs = code_paths()+[HERE/'freeze_source.py',HERE/'plan.md',HERE/'policy.json',LEAD_REVIEW]
    inputs += [GENERIC/'report.md',GENERIC/'test-repair.json',
        ROOT/'docs/research/single-owner-activation-design.md']
    value = dict(schema='rook2-single-owner-own-pgo-source-preparation-v1',
        sourceCheckpoint=SOURCE_CHECKPOINT, candidateCrate=str(DEFAULT_CRATE),
        candidateSource=source, sourceChangesAgainstGeneric=[], protectedArtifacts=baseline(),
        readinessSemantics=read(GENERIC/'preparation.json')['readinessSemantics'],
        trainingModes=TRAINING_MODES, trainingLives=216,
        comparisonConfigurations=NAMES, comparisonLives=270, idleProbes=5,
        reuseFocusedControls=dict(uniquePassed=70,testExecutions=71,initialFailed=1,freshUnitRuns=0),
        coldLayoutProcesses=1, closerApi='prepared_run tuple(record,receipt,effective), prospective record projection',
        inputSha256={str(p):sha(p) for p in sorted(set(inputs))},
        reusedEvidenceSha256={str(p):sha(p) for p in reused_evidence_paths()},
        scope='one unchanged-source own-PGO216/canonicalmerge/actualremerge/use/admission/descriptive270+5; no source/profile retune, broad qualification, adoption or external action')
    destination=HERE/'preparation.json'
    destination.write_text(json.dumps(value,indent=2)+'\n')
    assert preparation(destination) == value
    evidence = generic_evidence(value)
    assert evidence['freshGenericControls'] == 70 and evidence['sourceFiles'] == 69
    print(json.dumps(dict(sourceFiles=len(source),sourceChanges=[],
        protectedArtifacts=len(value['protectedArtifacts']),inputPins=len(value['inputSha256']),
        reusedPins=len(value['reusedEvidenceSha256']),trainingLives=216,
        comparisonLives=270,idle=5,preparationSha256=sha(destination)),indent=2))


if __name__ == '__main__':
    main()
