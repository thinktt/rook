#!/usr/bin/env python3
"""Constrain only this lead's verified Codex ancestors after collection ends."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import time

ROOT = Path(__file__).resolve().parents[2]
LIVE = ROOT/'evidence/production12-cpu-20261018-pgo'
OBSERVATION = ROOT/'evidence/production12-cpu-analysis-preparation-20261018/helper-affinity-observation.json'
HELPERS = {0,1,2,3,4,5,8,9,10,11,12,13}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def process(pid):
    path = Path('/proc')/str(pid)
    stat = (path/'stat').read_text(); fields = stat[stat.rfind(')')+2:].split()
    return dict(pid=pid,parent=int(fields[1]),name=(path/'comm').read_text().strip(),
                start_ticks=fields[19],uid=path.stat().st_uid,exe=os.readlink(path/'exe'))


def threads(pid):
    result = {}
    for task in (Path('/proc')/str(pid)/'task').iterdir():
        try: result[task.name] = sorted(os.sched_getaffinity(int(task.name)))
        except ProcessLookupError: pass
    return result


def write(path,value):
    with path.open('x') as stream: json.dump(value,stream,indent=2);stream.write('\n')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',required=True,type=Path,help='Absent receipt directory')
    args = parser.parse_args()
    if args.output.exists(): parser.error('output must be absent')
    terminal = LIVE/'terminal.json'
    if not terminal.exists(): parser.error('original collector handle37105 must be polled to terminal first')
    manifest = json.loads((LIVE/'collection/manifest.json').read_text())
    active = []
    for path in Path('/proc').iterdir():
        if not path.name.isdigit(): continue
        try:
            argv = (path/'cmdline').read_bytes().decode().split('\0'); exe = os.readlink(path/'exe')
            if (str(LIVE/'driver.py') in argv or exe == manifest['engine']
                    or (str(ROOT/'tools/collect_games.py') in argv and str(LIVE/'collection') in argv)):
                active.append(int(path.name))
        except (OSError,UnicodeDecodeError): pass
    if active: parser.error(f'old collection/native remains live: {active}')
    observed = json.loads(OBSERVATION.read_text())
    targets = [item for item in observed['process_ancestry_point_observation'] if item['name'] == 'codex']
    if len(targets) != 2: parser.error('expected exactly the two previously observed own Codex ancestors')
    required = {item['pid'] for item in targets}
    ancestry = []; pid = os.getpid()
    for _ in range(16):
        info = process(pid); ancestry.append(info)
        if required <= {item['pid'] for item in ancestry} or info['parent'] == 0: break
        pid = info['parent']
    current = {item['pid']:item for item in ancestry}
    for item in targets:
        info = current.get(item['pid'])
        if (info is None or info['name'] != 'codex' or info['start_ticks'] != item['start_ticks']
                or info['uid'] != os.getuid()):
            parser.error('recorded target is no longer a verified own Codex ancestor; retain a new observation')
    args.output.mkdir()
    before = {str(item['pid']):dict(process=current[item['pid']],threads=threads(item['pid'])) for item in targets}
    inputs = {str(path):sha(path) for path in [Path(__file__),OBSERVATION,terminal]}
    write(args.output/'before.json',dict(own_ancestry=ancestry,targets=before,helpers=sorted(HELPERS),input_sha256=inputs,
        prior_collection_matching_processes=active,scope='Own lead/client process threads only; no other agent, host, cpuset, kernel or security change'))
    result = dict(complete=False,failure=None,rounds=0,targets={})
    try:
        for round_index in range(8):
            for item in targets:
                pid = item['pid']; actual = process(pid)
                assert actual == current[pid],'ancestor identity changed'
                for tid in threads(pid):
                    try: os.sched_setaffinity(int(tid),HELPERS)
                    except ProcessLookupError: pass
            result['rounds'] = round_index+1
            after = {str(item['pid']):dict(process=process(item['pid']),threads=threads(item['pid'])) for item in targets}
            if all(value == sorted(HELPERS) for item in after.values() for value in item['threads'].values()):
                result.update(complete=True,targets=after); break
            time.sleep(0.01)
        assert result['complete'],'thread inventories did not converge to helper affinity'
        assert all(sha(Path(path)) == digest for path,digest in inputs.items()),'input changed'
    except BaseException as error:
        result['failure'] = f'{type(error).__name__}: {error}'; result['complete'] = False
        result['targets'] = {str(item['pid']):dict(process=process(item['pid']),threads=threads(item['pid'])) for item in targets}
    result['scope'] = 'Verified own thread affinities at this point; no claim about other guest tasks or continuous isolation. New threads inherit their creator affinity.'
    write(args.output/'result.json',result)
    print(json.dumps(dict(output=str(args.output),complete=result['complete'],failure=result['failure'],
                         target_pids=[item['pid'] for item in targets],threads=sum(len(x['threads']) for x in result['targets'].values()))))
    return 0 if result['complete'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
