#!/usr/bin/env python3
"""Reconcile completed Alpine CPU14 receipts without running an engine."""
import argparse
import hashlib
import json
import math
from pathlib import Path
import statistics


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def read(p):
    return json.loads(p.read_text())


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('directory', type=Path)
    a = p.parse_args()
    b = a.directory.resolve()
    plan, status = read(b/'plan.json'), read(b/'status.json')
    assert status['complete'] and all(x['exit'] == 0 for x in status['stages'])
    for path, h in plan['inputSha256'].items():
        assert sha(Path(path)) == h, path

    def host(path):
        if path.startswith('/work/build/'):
            build = next(Path(x).parent.parent.parent for x in plan['inputSha256']
                         if x.endswith('/plain-output/glibc-static/build.json'))
            return build/path.removeprefix('/work/build/')
        if path.startswith('/work/'):
            return b/path.removeprefix('/work/')
        tools = '/home/legolas/rook2/tools/'
        if path.startswith(tools):
            return b/'tools'/path.removeprefix(tools)
        if path.startswith('/usr/'):
            alpine = Path(plan['prefix'][plan['prefix'].index('--ro-bind')+1])
            return alpine/path.removeprefix('/')
        return Path(path)

    def native(path):
        n = read(path)
        assert n['failure'] is None and n['native_exit_code'] == 0
        assert n['engine_sha256_before'] == n['engine_sha256_after'] == plan['engineSha256']
        assert n['inherited_supervisor_affinity'] == n['supervisor_affinity'] == [14]
        assert n['native_pre_exec']['affinity'] == n['native_post_exec']['affinity'] == [14]
        assert n['supervisor_signals'] == []
        assert n['launcher_sha256'] == sha(b/'tools/account_native.py')
        return n

    s, manifest = read(b/'standard54/summary.json'), read(b/'standard54/manifest.json')
    assert s['complete'] and s['failure'] is None and len(s['runs']) == 216
    assert len(s['case_summaries']) == 54
    assert s['input_sha256_after'] == manifest['input_sha256']
    for name, h in manifest['input_sha256'].items():
        assert sha(host(name)) == h, name
    medians, walls = {}, {}
    for row in s['runs']:
        d = b/'standard54'/f"{list(manifest['schedule']).index({k: row[k] for k in ['case', 'repeat', 'warmup']}):03d}-{row['case']}-r{row['repeat']}"
        n = native(d/'native.json')
        c = read(d/'comparator.stdout')
        assert c['status'] == 'pass' and c['selectedCases'] == [row['case']]
        assert c['results'][0]['exit'] == {'code': 0, 'signal': None}
        assert row['failure'] is None and row['cpu_s'] == n['total_cpu_s']
        assert row['native_receipt_sha256'] == sha(d/'native.json')
        assert row['comparator_sha256'] == sha(d/'comparator.stdout')
        if not row['warmup']:
            medians.setdefault(row['case'], []).append(n['total_cpu_s'])
            walls.setdefault(row['case'], []).append(n['wall_ns']/1e9)
    total = sum(statistics.median(x) for x in medians.values())
    assert total == s['sum_case_medians_s']
    g = read(b/'games12/summary.json')
    assert g['complete'] and g['complete12'] and len(g['games']) == 12 and g['searches'] == 632
    searches = posts = 0
    cpu = wall = 0
    for row in g['games']:
        d = host(row['resultPath']).parent
        result = read(d/'result.json')
        n = native(d/'native.json')
        assert result['failure'] is None and row['failure'] is None
        assert row['cpu_s'] == n['total_cpu_s'] and row['wall_ns'] == n['wall_ns']
        for name, h in result['file_sha256'].items():
            assert sha(d/name) == h
        replay = read(d/'replay.json')
        assert replay['pass'] and all(x['code'] == 0 and not x['forced'] for x in replay['processes'])
        tap = read(d/'wire/receipt.json')
        assert tap['failure'] is None and len(tap['searches']) == row['searches']
        for name, item in tap['raw'].items():
            path = d/'wire'/f'{name}.raw'
            assert sha(path) == item['sha256'] and path.stat().st_size == item['bytes']
        searches += row['searches']
        # Literal ordinary post records begin with a numeric depth token.
        posts += sum(bool(line.split()) and line.split()[0].lstrip(b'-').isdigit()
                     for line in (d/'wire/stdout.raw').read_bytes().splitlines())
        cpu += n['total_cpu_s']
        wall += n['wall_ns']/1e9
    # Python versions can sum the same binary floats differently by one ulp.
    assert searches == 632 and math.isclose(cpu, g['sum_game_cpu_s'], rel_tol=0, abs_tol=1e-9)
    result = dict(engineSha256=plan['engineSha256'], buildMode='plain non-PGO', containerCpu=14,
        standard54=dict(cases=54, lives=216, measured=162, sumCaseMedianCpuSeconds=total,
                        sumCaseMedianWallSeconds=sum(statistics.median(x) for x in walls.values())),
        games12=dict(games=12, searches=searches, posts=posts, repetitions=1,
                     sumNativeCpuSeconds=round(cpu, 6), sumNativeWallSeconds=wall),
        accounting='native whole lifetime; all container helpers share CPU14',
        finalPerformanceQualification=False, full3288Qualification=False)
    (b/'reconciled.json').write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
