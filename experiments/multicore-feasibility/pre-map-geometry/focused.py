#!/usr/bin/env python3
"""Finite CLI and inherited one/two-CPU original08 correctness controls."""
import argparse
import json
import os
from pathlib import Path
import selectors
import subprocess
import sys
import time

sys.dont_write_bytecode = True
from common import HELPERS, SPEC, audit, colors_report, read, sha, stop_owned, write


def clean_environment():
    return {key: value for key, value in os.environ.items()
            if not key.startswith('ROOK2_') and key != 'LLVM_PROFILE_FILE'}


def affinity_replay(image, out, mask, configured):
    workload = next(c for c in read(SPEC/'workloads.json')['cases'] if c['id'] == 'profile-08')
    oracle_file = read(SPEC/'replay-oracle.json')
    oracle = next(c for c in oracle_file['cases'] if c['id'] == 'profile-08')
    options = ['--threads=3', '--owner-local-inventory', '--q-owner-local-inventory', '--pre-map-geometry', *oracle_file['mode']]
    command = [str(image), *options]
    setup = ('\n'.join([*workload['protocol']['recordsBeforeSearch'], 'cm_parm rnd'])+'\n').encode()
    prefix = b'cm_parm\n'
    sent, output = bytearray(), bytearray()
    started = time.monotonic_ns()
    env=clean_environment();env['ROOK2_COLORS_REPORT']=str(out/'colors.json')
    child = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
        stderr=subprocess.PIPE, env=env, start_new_session=True,
        preexec_fn=lambda: os.sched_setaffinity(0, set(mask)))
    selector = selectors.DefaultSelector()
    selector.register(child.stdout, selectors.EVENT_READ)
    deadline = time.monotonic()+180
    masks, errors = None, b''

    def send(data):
        child.stdin.write(data); child.stdin.flush(); sent.extend(data)

    def receive_until(predicate):
        while not predicate(bytes(output)):
            remaining = deadline-time.monotonic()
            assert remaining > 0, 'affinity control deadline'
            if not selector.select(min(remaining, 1)):
                continue
            chunk = os.read(child.stdout.fileno(), 65536)
            assert chunk, 'native exited before expected affinity-control reply'
            output.extend(chunk)
            assert len(output) <= 8*1024*1024

    try:
        send(prefix)
        receive_until(lambda data: data == prefix)
        tids = sorted(Path(f'/proc/{child.pid}/task').iterdir())
        masks = {p.name: sorted(os.sched_getaffinity(int(p.name))) for p in tids}
        assert len(masks) == configured and all(value == mask for value in masks.values())
        send(setup)
        receive_until(lambda data: data.endswith(b'cm_parm rnd=0\n'))
        send(b'go\n')
        receive_until(lambda data: any(line.startswith(b'move ') for line in data.splitlines()))
        sent.extend(b'quit\n')
        tail, errors = child.communicate(b'quit\n', timeout=max(.01, min(20, deadline-time.monotonic())))
        output.extend(tail)
        assert child.returncode == 0 and errors == b''
    except BaseException as error:
        stop_owned(child)
        write(out/'failure.json', dict(error=repr(error), nativePid=child.pid,
            masks=masks, exit=child.returncode))
        raise
    finally:
        selector.close()
        for stream in [child.stdin, child.stdout, child.stderr]:
            if stream is not None and not stream.closed:
                stream.close()
        (out/'stdin.raw').write_bytes(sent)
        (out/'stdout.raw').write_bytes(output)
        (out/'stderr.raw').write_bytes(errors)
    # Project the extra startup handshake and end(data) quit away explicitly.
    raw = dict(stdin=setup+b'go\n', stdout=bytes(output)[len(prefix):], stderr=errors)
    actual = dict(stdout=raw['stdout'].decode(), stderr=errors.decode(),
                  exit=dict(code=child.returncode, signal=None))
    posts = audit.original_streams(actual, workload, oracle, raw)
    assert not Path(f'/proc/{child.pid}').exists()
    report=read(out/'colors.json')
    if configured<3:
        assert report==dict(schema='rook2-colors-readiness-v1',enabled=False)
        map_epoch=None
    else:
        assert report['enabled'] is True
        map_epoch=report['map_ready_epoch'];assert type(map_epoch) is int and map_epoch>0
    return dict(argv=command, nativePid=child.pid, requestedThreads=3,
        configuredThreads=configured, inheritedMask=mask, taskAffinities=masks,
        orderedPosts=posts,mapReadyEpoch=map_epoch,colorsReport=report,exit=child.returncode,joined=True,pidAbsentAfterReap=True, elapsedNs=time.monotonic_ns()-started,
        sha256={name: sha(out/name) for name in ['stdin.raw', 'stdout.raw', 'stderr.raw','colors.json']},
        scope='original08 with extra startup cm_parm; inherited CPU permission and exact output/liveness, not timing')


def audit_result(path,image):
    path,image=Path(path).resolve(),Path(image).resolve();value=read(path)
    assert value['schema']=='rook2-pre-map-geometry-focused-cli-v1' and value['complete']
    assert value['engine']==str(image) and value['engineSha256']==sha(image)
    rows=value['cli'];assert len(rows)==20
    positives=[([],1,1,sorted(HELPERS)),(['--threads=1'],1,1,sorted(HELPERS)),
        (['--threads=2'],2,2,sorted(HELPERS)),(['--threads=3'],3,3,sorted(HELPERS)),
        (['--threads=8'],8,3,sorted(HELPERS)),(['--threads=3'],3,1,[14]),
        (['--threads=3'],3,2,[6,14]),(['--threads=8'],8,2,[6,14]),
        (['--threads=3','--owner-local-inventory','--q-owner-local-inventory'],3,3,sorted(HELPERS))]
    for row,(options,requested,configured,mask) in zip(rows,positives):
        assert row['argv']==[str(image),*options,'--inspect-threads'] and row['inheritedMask']==mask
        assert row['exit']==0 and row['stderr']==''
        assert json.loads(row['stdout'])==dict(requested_threads=requested,configured_threads=configured)
    for row,argument in zip(rows[9:14],['0','-1','','oops','184467440737095516160']):
        assert row['argv']==[str(image),'--threads='+argument,'--inspect-threads']
        assert row['exit']!=0 and row['stdout']=='' and row['stderr']
    extra=[(['--pre-map-geometry'],1,1),(['--threads=1','--pre-map-geometry'],1,1),
        (['--threads=2','--pre-map-geometry'],2,2),(['--threads=3','--pre-map-geometry'],3,3),
        (['--threads=3','--owner-local-inventory','--q-owner-local-inventory','--pre-map-geometry'],3,3)]
    for row,(options,requested,configured) in zip(rows[14:19],extra):
        assert row['argv']==[str(image),*options,'--inspect-threads'] and row['inheritedMask']==sorted(HELPERS)
        assert row['exit']==0 and row['stderr']==''
        assert json.loads(row['stdout'])==dict(requested_threads=requested,configured_threads=configured)
    assert rows[19]['argv']==[str(image),'--pre-map-geometry=oops','--inspect-threads']
    assert rows[19]['exit']!=0 and rows[19]['stdout']=='' and rows[19]['stderr']
    assert len(value['affinityReplays'])==2
    workload=next(row for row in read(SPEC/'workloads.json')['cases'] if row['id']=='profile-08')
    oracle_file=read(SPEC/'replay-oracle.json')
    oracle=next(row for row in oracle_file['cases'] if row['id']=='profile-08')
    all_rows=[*value['affinityReplays'],value['stagedWitness']]
    for row,name,mask,configured in zip(all_rows,['one-cpu','two-cpu','staged-protocol'],[[14],[6,14],[4,6,14]],[1,2,3]):
        directory=path.parent/name
        assert row['argv']==[str(image),'--threads=3','--owner-local-inventory','--q-owner-local-inventory','--pre-map-geometry',*oracle_file['mode']]
        assert row['requestedThreads']==3 and row['configuredThreads']==configured and row['inheritedMask']==mask
        assert len(row['taskAffinities'])==configured and all(item==mask for item in row['taskAffinities'].values())
        assert row['exit']==0 and row['joined'] is row['pidAbsentAfterReap'] is True
        assert not Path(f'/proc/{row["nativePid"]}').exists()
        for name,digest in row['sha256'].items():assert sha(directory/name)==digest
        incoming=(directory/'stdin.raw').read_bytes();outgoing=(directory/'stdout.raw').read_bytes()
        assert incoming.startswith(b'cm_parm\n') and incoming.endswith(b'quit\n') and outgoing.startswith(b'cm_parm\n')
        raw=dict(stdin=incoming[8:-5],stdout=outgoing[8:],stderr=(directory/'stderr.raw').read_bytes())
        actual=dict(stdout=raw['stdout'].decode(),stderr=raw['stderr'].decode(),exit=dict(code=0,signal=None))
        assert audit.original_streams(actual,workload,oracle,raw)==row['orderedPosts']
        report=read(directory/'colors.json');assert report==row['colorsReport']
        assert report==colors_report(directory/'colors.json',configured)
        if configured<3:
            assert report==dict(schema='rook2-colors-readiness-v1',enabled=False) and row['mapReadyEpoch'] is None
        else:
            assert report['publication_interval']=='request_before_optional_geometry_and_map_wait'
            assert report['map_ready_epoch']==row['mapReadyEpoch']>0
    assert len({row['nativePid'] for row in all_rows})==3
    return value


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--engine', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    image, out = args.engine.resolve(), args.output.resolve()
    out.mkdir()
    assert set(os.sched_getaffinity(0)) == HELPERS
    digest = sha(image)
    rows = []
    positive = [([], 1, 1, sorted(HELPERS)), (['--threads=1'], 1, 1, sorted(HELPERS)),
        (['--threads=2'], 2, 2, sorted(HELPERS)), (['--threads=3'], 3, 3, sorted(HELPERS)),
        (['--threads=8'], 8, 3, sorted(HELPERS)),
        (['--threads=3'], 3, 1, [14]), (['--threads=3'], 3, 2, [6, 14]),
        (['--threads=8'], 8, 2, [6, 14]),
        (['--threads=3','--owner-local-inventory','--q-owner-local-inventory'],3,3,sorted(HELPERS))]
    for options, requested, configured, mask in positive:
        command = [str(image), *options, '--inspect-threads']
        reply = subprocess.run(command, input=b'', capture_output=True, timeout=20,
            env=clean_environment(), preexec_fn=lambda mask=mask: os.sched_setaffinity(0, set(mask)))
        row = dict(argv=command, inheritedMask=mask, exit=reply.returncode,
            stdout=reply.stdout.decode(), stderr=reply.stderr.decode())
        rows.append(row); write(out/'cli-progress.json', rows)
        assert reply.returncode == 0 and reply.stderr == b''
        assert json.loads(reply.stdout) == dict(requested_threads=requested, configured_threads=configured)
    for value in ['0', '-1', '', 'oops', '184467440737095516160']:
        command = [str(image), '--threads='+value, '--inspect-threads']
        reply = subprocess.run(command, input=b'', capture_output=True, timeout=20, env=clean_environment())
        rows.append(dict(argv=command, inheritedMask=sorted(HELPERS), exit=reply.returncode,
                         stdout=reply.stdout.decode(), stderr=reply.stderr.decode()))
        write(out/'cli-progress.json', rows)
        assert reply.returncode != 0 and reply.stdout == b'' and reply.stderr
    geometry_positive=[(['--pre-map-geometry'],1,1),(['--threads=1','--pre-map-geometry'],1,1),
        (['--threads=2','--pre-map-geometry'],2,2),(['--threads=3','--pre-map-geometry'],3,3),
        (['--threads=3','--owner-local-inventory','--q-owner-local-inventory','--pre-map-geometry'],3,3)]
    for options,requested,configured in geometry_positive:
        command=[str(image),*options,'--inspect-threads']
        reply=subprocess.run(command,input=b'',capture_output=True,timeout=20,env=clean_environment())
        rows.append(dict(argv=command,inheritedMask=sorted(HELPERS),exit=reply.returncode,stdout=reply.stdout.decode(),stderr=reply.stderr.decode()))
        write(out/'cli-progress.json',rows)
        assert reply.returncode==0 and reply.stderr==b''
        assert json.loads(reply.stdout)==dict(requested_threads=requested,configured_threads=configured)
    command=[str(image),'--pre-map-geometry=oops','--inspect-threads']
    reply=subprocess.run(command,input=b'',capture_output=True,timeout=20,env=clean_environment())
    rows.append(dict(argv=command,inheritedMask=sorted(HELPERS),exit=reply.returncode,stdout=reply.stdout.decode(),stderr=reply.stderr.decode()))
    assert reply.returncode!=0 and reply.stdout==b'' and reply.stderr
    write(out/'cli-progress.json',rows)
    assert len(rows)==20
    probes = []
    for name, mask, configured in [('one-cpu', [14], 1), ('two-cpu', [6, 14], 2)]:
        directory = out/name; directory.mkdir()
        probes.append(affinity_replay(image, directory, mask, configured))
    witness_dir=out/'staged-protocol';witness_dir.mkdir()
    witness=affinity_replay(image,witness_dir,[4,6,14],3)
    assert sha(image) == digest
    result = dict(schema='rook2-pre-map-geometry-focused-cli-v1', complete=True,
        engine=str(image), engineSha256=digest, cli=rows, affinityReplays=probes,stagedWitness=witness)
    write(out/'result.json', result)
    audit_result(out/'result.json',image)
    print(json.dumps(dict(complete=True, cliControls=len(rows), affinityReplayLives=len(probes))))


if __name__ == '__main__':
    main()
