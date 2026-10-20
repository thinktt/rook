"""Review-only by default; explicit --apply changes only the plan's live user processes."""
import argparse
import datetime
import errno
import json
import os
from pathlib import Path

OUT = Path(__file__).resolve().parent


def identity(pid):
    proc = Path('/proc') / str(pid)
    raw = (proc / 'stat').read_text()
    end = raw.rfind(')')
    fields = raw[end + 2:].split()
    return dict(pid=pid, name=raw[raw.find('(') + 1:end],
                start_ticks=int(fields[19]), uid=proc.stat().st_uid,
                executable=os.readlink(proc / 'exe'))


def verify(record):
    actual = identity(record['pid'])
    assert actual['uid'] == os.getuid() != 0
    assert actual['name'] in {'codex', 'herdr', 'node'}
    for field in ('pid', 'name', 'start_ticks', 'executable'):
        assert actual[field] == record[field], (field, actual, record)


def threads(pid):
    return [int(p.name) for p in (Path('/proc') / str(pid) / 'task').iterdir()]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument('--apply', action='store_true')
    mode.add_argument('--restore', type=Path)
    args = parser.parse_args()
    if args.restore:
        receipt = json.loads(args.restore.read_text())
        for process in receipt['processes']:
            verify(process)
        restored = 0
        for process in receipt['processes']:
            for item in process['changed_threads']:
                try:
                    os.sched_setaffinity(item['tid'], item['before'])
                    assert sorted(os.sched_getaffinity(item['tid'])) == item['before']
                    restored += 1
                except ProcessLookupError:
                    pass
        print(json.dumps(dict(restored_existing_threads=restored)))
        return
    plan = json.loads((OUT / 'plan.json').read_text())
    target = set(plan['housekeeping_cpus'])
    assert target == {0, 1, 2, 3, 4, 5, 8, 9, 10, 11, 12, 13}
    # Validate every process before changing any thread. A restarted process
    # requires a refreshed, separately reviewed plan.
    for process in plan['processes']:
        verify(process)
    if not args.apply:
        print(json.dumps(dict(dry_run=True, process_ids=[p['pid'] for p in plan['processes']],
                              existing_threads=sum(len(threads(p['pid'])) for p in plan['processes']),
                              target=sorted(target), mutation=False)))
        return
    receipt = dict(started_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                   target=sorted(target), processes=[], complete=False)
    receipt_path = OUT / 'applied.json'
    assert not receipt_path.exists()
    try:
        for process in plan['processes']:
            changed = []
            receipt['processes'].append({**identity(process['pid']), 'changed_threads': changed})
            seen = set()
            for _ in range(3):
                for tid in threads(process['pid']):
                    if tid in seen:
                        continue
                    try:
                        before = sorted(os.sched_getaffinity(tid))
                        if set(before) != target:
                            changed.append(dict(tid=tid, before=before))
                            os.sched_setaffinity(tid, target)
                        assert set(os.sched_getaffinity(tid)) == target
                        seen.add(tid)
                    except ProcessLookupError:
                        pass
                live = threads(process['pid'])
                if all(set(os.sched_getaffinity(tid)) == target for tid in live):
                    break
            else:
                raise RuntimeError('Thread creation did not settle; use rollback receipt')
        receipt['complete'] = True
    finally:
        receipt['finished_utc'] = datetime.datetime.now(datetime.timezone.utc).isoformat()
        receipt_path.write_text(json.dumps(receipt, indent=2) + '\n')
    print(json.dumps(dict(complete=receipt['complete'],
                          changed_threads=sum(len(p['changed_threads']) for p in receipt['processes']),
                          receipt=str(receipt_path))))


if __name__ == '__main__':
    main()
