"""Restrict this pane's verified client/launcher threads; no global change."""
from pathlib import Path
import hashlib
import json
import os
import time

OUT = Path(__file__).resolve().parent
HELPERS = {0, 1, 2, 3, 4, 5, 8, 9, 10, 11, 12, 13}
TARGETS = [1116, 1138, 1207, 1322, 2165]
PANE = os.environ['HERDR_PANE_ID']


def process(pid):
    path = Path('/proc')/str(pid)
    tail = (path/'stat').read_text().rsplit(')', 1)[1].split()
    env = dict(item.split(b'=', 1) for item in (path/'environ').read_bytes().split(b'\0') if b'=' in item)
    return dict(pid=pid, parent=int(tail[1]), start_ticks=tail[19],
                uid=path.stat().st_uid, name=(path/'comm').read_text().strip(),
                exe=os.readlink(path/'exe'), pane=env.get(b'HERDR_PANE_ID', b'').decode())


def threads(pid):
    result = {}
    for task in (Path('/proc')/str(pid)/'task').iterdir():
        try:
            result[task.name] = sorted(os.sched_getaffinity(int(task.name)))
        except ProcessLookupError:
            pass
    return result


def write(name, value):
    with (OUT/name).open('x') as stream:
        json.dump(value, stream, indent=2)
        stream.write('\n')


assert os.sched_getaffinity(0) == HELPERS
ancestors = []
pid = os.getpid()
while pid > 1:
    info = process(pid)
    ancestors.append(info)
    if pid == 1116:
        break
    pid = info['parent']
assert {1116, 1138, 1207} <= {item['pid'] for item in ancestors}
identities = {pid: process(pid) for pid in TARGETS}
for pid, item in identities.items():
    assert item['uid'] == os.getuid() and item['pane'] == PANE
    assert item['name'] in ['node', 'codex', 'codex-code-mode']
    if pid != 1116:
        assert item['parent'] in identities
before = {str(pid): dict(process=item, threads=threads(pid)) for pid, item in identities.items()}
write('before.json', dict(targets=before, own_ancestry=ancestors, helpers=sorted(HELPERS),
                         proc_stat=Path('/proc/stat').read_text(),
                         scope='Own pane launcher/client/server/code-mode only; other panes/Herdr/system/host untouched'))
result = dict(complete=False, failure=None)
try:
    for round_index in range(8):
        for pid, identity in identities.items():
            assert process(pid) == identity
            for tid in threads(pid):
                try:
                    os.sched_setaffinity(int(tid), HELPERS)
                except ProcessLookupError:
                    pass
        after = {str(pid): dict(process=process(pid), threads=threads(pid)) for pid in TARGETS}
        if all(mask == sorted(HELPERS) for item in after.values() for mask in item['threads'].values()):
            result.update(complete=True, rounds=round_index+1, targets=after)
            break
        time.sleep(0.01)
    assert result['complete'], 'thread inventory did not converge'
except BaseException as error:
    result['failure'] = f'{type(error).__name__}: {error}'
result.update(scope='Point verification only; future threads inherit creator mask. Other guest work remains outside this scope.',
              script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
write('result.json', result)
print(json.dumps(dict(complete=result['complete'], failure=result['failure'], target_pids=TARGETS,
                      threads=sum(len(item['threads']) for item in result.get('targets', {}).values()))))
raise SystemExit(0 if result['complete'] else 1)
