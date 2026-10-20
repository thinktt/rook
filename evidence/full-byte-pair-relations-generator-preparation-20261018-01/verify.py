#!/usr/bin/env python3
"""Bounded offline generator/CLI verification; no Rust/native execution."""
from pathlib import Path
import hashlib
import json
import os
import re
import shutil
import subprocess

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
FROZEN=Path('/home/legolas/rook2-work/imp2-full-byte-pair-relations-20261018-oc3es5rp/src/relation_table.rs')
CANDIDATE=HERE/'proposed/scripts/generate_relation_table.py'
ORIGINAL=ROOT/'scripts/generate_relation_table.py'
H=[0,1,2,3,4,5,8,9,10,11,12,13]


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    assert sorted(os.sched_getaffinity(0))==H
    assert os.environ['TMPDIR']=='/home/legolas/rook2-build-tmp'
    inputs={str(p):sha(p) for p in [FROZEN,CANDIDATE,ORIGINAL,ROOT/'README.md']}
    assert sha(FROZEN)=='8b559327e7fe433750ab30add4e172570a4a0a80d10b3b3b63bd475dd731de49'
    assert (HERE/'basis/scripts/generate_relation_table.py').read_bytes()==ORIGINAL.read_bytes()
    original=ORIGINAL.read_text();candidate=CANDIDATE.read_text()
    assert original[original.index('def features'):original.index('def generate')]==candidate[candidate.index('def features'):candidate.index('def generate')]
    assert 'import subprocess' not in candidate and 'rustfmt' not in candidate
    scratch=HERE/'scratch';scratch.mkdir()
    (scratch/'scripts').mkdir();(scratch/'src').mkdir()
    shutil.copy2(CANDIDATE,scratch/'scripts/generate_relation_table.py')
    shutil.copy2(FROZEN,scratch/'src/relation_table.rs')
    out=scratch/'output.rs';out.write_bytes(b'controlled previous output\n')
    mismatch=scratch/'mismatch.rs';mismatch.write_bytes(FROZEN.read_bytes()+b'\n')
    mismatch_before=sha(mismatch)
    forbidden=scratch/'must-not-exist.rs'
    requests=[
      ('check-exact',[str(CANDIDATE),'--check',str(FROZEN)],HERE,0),
      ('default-stdout',[str(CANDIDATE)],HERE,0),
      ('explicit-output',[str(CANDIDATE),'--output',str(out)],HERE,0),
      ('README-relative',['scripts/generate_relation_table.py','--check','src/relation_table.rs'],scratch,0),
      ('check-mismatch',[str(CANDIDATE),'--check',str(mismatch)],HERE,1),
      ('mutually-exclusive',[str(CANDIDATE),'--check',str(FROZEN),'--output',str(forbidden)],HERE,2),
    ]
    commands=[]
    for name,args,cwd,expected in requests:
        argv=['/usr/bin/taskset','-c','0-5,8-13','/usr/bin/python3',*args]
        stdout=HERE/(name+'.stdout');stderr=HERE/(name+'.stderr')
        with stdout.open('xb') as o,stderr.open('xb') as e:
            child=subprocess.Popen(argv,cwd=cwd,stdout=o,stderr=e)
            pid=child.pid;exit_code=child.wait()
        record=dict(name=name,argv=argv,cwd=str(cwd),pid=pid,
                    direct_exit_code=exit_code,expected_exit_code=expected,
                    stdout_sha256=sha(stdout),stderr_sha256=sha(stderr),
                    actual_wait_observed=True,affinity_inherited_and_taskset=H)
        commands.append(record)
        # Retain each actual direct completion even if a later assertion fails.
        (HERE/(name+'.command.json')).write_text(json.dumps(record,indent=2)+'\n')
        assert exit_code==expected,(name,exit_code,expected)
    assert (HERE/'default-stdout.stdout').read_bytes()==FROZEN.read_bytes()==out.read_bytes()
    assert (scratch/'src/relation_table.rs').read_bytes()==FROZEN.read_bytes()
    assert sha(mismatch)==mismatch_before and not forbidden.exists()
    assert (HERE/'check-mismatch.stderr').read_text()=='generated relation source differs\n'
    for name in ['check-exact','README-relative']:
        assert (HERE/(name+'.stdout')).read_text()=='Exact relation table source matches the general formula generator\n'
        assert not (HERE/(name+'.stderr')).read_bytes()
    assert not (HERE/'default-stdout.stderr').read_bytes()
    assert not (HERE/'explicit-output.stdout').read_bytes() and not (HERE/'explicit-output.stderr').read_bytes()
    payload_source=out.read_text().split('pub(crate) static RELATIONS:',1)[1].split('= [',1)[1]
    tokens=re.findall(r'\b[UCF]\b',payload_source)
    assert len(tokens)==262144
    enum_values={'U':0,'C':1,'F':2}
    payload=bytes(enum_values[t] for t in tokens)
    payload_sha=hashlib.sha256(payload).hexdigest()
    assert payload_sha=='09eb9f279a6111078f8600b9ebffff5b3c7eb35a8bf5298e7ef7691d162284ee'
    plan_path=ROOT/'evidence/activity-value-inputs-complete117-preparation-20261018-01/validation-plan.json'
    plan=json.loads(plan_path.read_text())
    assert len(plan['source_sha256'])==112 and len(plan['diagnostic_sha256'])==43
    assert 'scripts/generate_relation_table.py' not in plan['source_sha256']
    assert all(sha(path)==digest for path,digest in inputs.items())
    result=dict(complete=True,scope='offline Python generator/CLI only',commands=commands,
       exact_generated_source_bytes=len(out.read_bytes()),source_sha256=sha(out),
       typed_payload_bytes=len(payload),typed_payload_sha256=payload_sha,
       features_and_ordered_formula_unchanged=True,
       README_relative_command_verified=True,public_CLI=dict(check='unchanged exact read-only comparison',
       default='unchanged stdout mode',output='new explicit path, writes/replaces exact generated bytes',
       mutually_exclusive=True),
       scripts_generator_outside_native69_and_cold43_and_full112=True,
       source112_map_reference=str(plan_path),source112_map_sha256=sha(plan_path),
       inputs_sha256=inputs,all_inputs_unchanged=True,all_children_closed=True,
       new_unit_tests=0,Rust_native_build_engine_profile_timing_Git_runs=0)
    (HERE/'verification.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:result[k] for k in ['complete','exact_generated_source_bytes','source_sha256','typed_payload_bytes','typed_payload_sha256','all_children_closed']}))

if __name__=='__main__':main()
