#!/usr/bin/env python3
"""External valid-data native clock/timing checks, without a DIAG transport claim."""
import json
from pathlib import Path
import shutil
import check_policies as runner

FILES = ['work-clock-v1.json', 'adaptive-time-v1.json', 'iteration-terminal-stop-v1.json',
         'root-randomization-v1.json', 'root-aspiration-v1.json',
         'seeded-timed-search-v1.json', 'generic-timed-search-v1.json',
         'output-score-v1.json', 'pv-line-v1.json', 'time-schedule-v1.json',
         'time-allowance-v1.json','personality-configuration-v1.json',
         'clock-session-setup-v1.json','root-go-outcome-v1.json','ordinary-joined-search-v1.json',
         'clock-seeded-sessions-v1.json','persistent-ordinary-session-public-v1.json',
         'persistent-ordinary-session-v1.json','interrupted-sessions-v1.json']
CASES = []

def generate(case):
    index=len(CASES)
    CASES.append(dict(operation=case['request']['operation'], input=case['request']['input'], expected=case['expected']))
    return [f'probe::run(concat!(env!("CARGO_MANIFEST_DIR"), "/cases/{index:04d}.json"));']

def prepare(output):
    (output/'cases').mkdir()
    for index,case in enumerate(CASES):
        (output/'cases'/f'{index:04d}.json').write_text(json.dumps(case,separators=(',',':'))+'\n')
    shutil.copyfile(Path(__file__).with_name('timing_probe.rs'),output/'src/probe.rs')

if __name__=='__main__':
    raise SystemExit(runner.main(FILES,generate,'mod probe;',Path(__file__),prepare,test_threads=2))
