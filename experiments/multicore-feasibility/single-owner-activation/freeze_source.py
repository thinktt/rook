#!/usr/bin/env python3
"""Bind the one isolated source/tool preparation; starts no native process."""
import difflib
import json
from pathlib import Path
import subprocess
import sys

sys.dont_write_bytecode = True


def forbidden(*_args, **_kwargs):
    raise AssertionError('source freeze may not launch a process')


for name in ['Popen', 'run', 'call', 'check_call', 'check_output']:
    setattr(subprocess, name, forbidden)

from common import (HERE, ROOT, DEFAULT_CRATE, CONTROL_CRATE, CONTROL_EXPERIMENT,
    baseline, code_paths, preparation, read, reused_evidence_paths, sha, snapshot)
from source_check import check


def main():
    before, after = snapshot(CONTROL_CRATE), snapshot(DEFAULT_CRATE)
    changed = sorted(name for name in before.keys() & after.keys() if before[name] != after[name])
    added, removed = sorted(after.keys()-before.keys()), sorted(before.keys()-after.keys())
    assert len(before) == 68 and len(after) == 69 and removed == []
    assert added == ['src/evaluator/activation_tests.rs']
    patches = []
    for name in sorted(set(changed+added)):
        old = (CONTROL_CRATE/name).read_text().splitlines(True) if name in before else []
        new = (DEFAULT_CRATE/name).read_text().splitlines(True)
        patches.extend(difflib.unified_diff(old, new,
            fromfile='a/'+name if name in before else '/dev/null', tofile='b/'+name))
    (HERE/'source.patch').write_text(''.join(patches))
    groups = [
        ('colors-worker', 'colors_worker::lifecycle_tests', 27),
        ('activation', 'evaluator::activation_tests', 9),
        ('colors-lifetime', 'evaluator::colors_lifecycle_tests', 3),
        ('colors-numerical', 'evaluator::colors_tests', 8),
        ('ordinary-evaluator', 'evaluator::owner_inventory_tests', 6),
        ('q-evaluator', 'evaluator::q_inventory_tests', 6),
        ('ordinary-owner', 'ordinary::owner_inventory_tests', 5),
        ('q-owner', 'quiescence::q_inventory_tests', 6),
    ]
    focused = [dict(name=name, target=['--lib'], selector=selector,
                    expectedPassed=count, limitSeconds=300) for name, selector, count in groups]
    assert sum(row['expectedPassed'] for row in focused) == 70
    policy = read(HERE/'policy.json')
    policy.update(sourceFiles=len(after), sourceChanged=changed, sourceAdded=added, focused=focused)
    (HERE/'policy.json').write_text(json.dumps(policy, indent=2)+'\n')
    lead = Path('/home/legolas/agent-memos')
    inputs = code_paths() + [HERE/name for name in ['freeze_source.py', 'plan.md', 'policy.json',
        'ownership-proof.md', 'source.patch']]
    inputs += [ROOT/'docs/research/single-owner-activation-design.md',
        lead/'imp2-lead-to-imp2-single-owner-generic-discriminator-20261028.md',
        lead/'imp2-lead-single-owner-independent-challenge-20261028.md',
        lead/'imp2-lead-to-imp2-single-owner-activation-design-20261028.md',
        lead/'imp2-lead-owner-control-lease-reserve-20261028.md']
    reused = reused_evidence_paths()
    value = dict(schema='rook2-single-owner-activation-source-preparation-v1',
        baseSourceCheckpoint='12c6f0dac21e6b102f435deec1b816aea5737d36',
        designCheckpoint='c9845ea68ddda71779bb791a443a68598212556c',
        candidateCrate=str(DEFAULT_CRATE), controlCrate=str(CONTROL_CRATE),
        controlSource=before, candidateSource=after, sourceChanges=changed,
        sourceAdded=added, sourceRemoved=removed, protectedArtifacts=baseline(),
        focused=focused, readinessSemantics=read(CONTROL_EXPERIMENT/'preparation.json')['readinessSemantics'],
        evidenceReuse=dict(priorGenericWorkerPassed=25, priorUnchangedControls=35,
            freshFocusedSelected=70, unchangedNumericalFiles=17,
            scope='historical controls retained read-only; affected current worker/entry/numerical/inventory controls selected fresh; no full suite or feature qualification'),
        sourceChallenge=dict(sourceBodyCheck=check(),
            ownershipProof=str(HERE/'ownership-proof.md'),
            independentChallenge=str(lead/'imp2-lead-single-owner-independent-challenge-20261028.md'),
            terminalDominatesSavedDepth=True, fixedBodyInvariantAudited=True,
            standaloneParking='after joined shared prefix, before retained/stats/observer/finish suffix',
            timedCleanup='normal/error timing=None before actual activation close',
            featureLimits='default paths built/run; branch-transactions retains existing Rc non-Send limit, two trait/migration tests cfg out; optional feature compilation not selected'),
        reusedEvidenceSha256={str(p):sha(p) for p in sorted(set(reused))},
        inputSha256={str(p):sha(p) for p in sorted(set(inputs))},
        scope='one isolated single-owner generic48+4, both hooks, unchanged owned inputs/math/observations/SC-RMW; no PGO/qualification/adoption')
    destination = HERE/'preparation.json'
    destination.write_text(json.dumps(value, indent=2)+'\n')
    assert preparation(destination) == value
    print(json.dumps(dict(sourceFiles=len(after), changed=changed, added=added,
        focusedSelected=70, protectedArtifacts=len(value['protectedArtifacts']),
        inputPins=len(value['inputSha256']), reusedPins=len(value['reusedEvidenceSha256']),
        preparationSha256=sha(destination)), indent=2))


if __name__ == '__main__':
    main()
