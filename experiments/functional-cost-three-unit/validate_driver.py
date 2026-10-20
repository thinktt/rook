#!/usr/bin/env python3
"""Four exact public projections on the frozen use artifact, before calibration."""
import argparse
import json
from pathlib import Path
import collect


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--engine', type=Path, required=True)
    ap.add_argument('--output', type=Path, required=True)
    a = ap.parse_args()
    engine = a.engine.resolve(strict=True)
    out = a.output.absolute()
    out.mkdir()  # Preserve failures; never overwrite or retry this instance.
    units = {u['id']: u for u in collect.load(collect.PUBLIC / 'functional-workloads.json')['units']}
    closure = {'engine_sha256': collect.digest(engine)}
    result = {'complete': False, 'engine': str(engine), **closure, 'checks': [], 'failure': None}
    try:
        for row, unit_id, _, _ in collect.ROWS:
            unit = units[unit_id]
            p = out / (row + '.json')
            collect.save(p, unit['workload']['request']['input'])
            expected = unit['expectedProjection']
            n, q = ((54, 234) if row == 'search' else
                    (0, sum(r['relationQueries'] for r in expected['results']))
                    if row.startswith('eval-') else (0, 0))
            actual, native = collect.run_child(engine, row, 'verify', 1, p, out / row, closure)
            collect.checked_observation(actual, row, 1,
                                        {'chargedSearchUnits': n, 'chargedRelationQueries': q}, expected)
            result['checks'].append({'row': row, 'exact': True, 'native_pid': native['native_pid'],
                                     'sink': actual['sink']})
        result['complete'] = True
    except BaseException as error:
        result['failure'] = repr(error)
        raise
    finally:
        collect.save(out / 'result.json', result)
    print(json.dumps(result))


if __name__ == '__main__':
    main()
