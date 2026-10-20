#!/usr/bin/env python3
"""Untimed12-game/continuity pre-gate of the exact ownPGO57 native image."""
import concurrent.futures
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time

ROOT=Path('/home/legolas/rook2')
PREP=Path(__file__).resolve().parent
KIT=Path('/home/legolas/king-spec/conformance/gate-replay')
APPROVAL=json.loads((PREP/'pregate-clearance.json').read_text())
assert APPROVAL['authorized'] is True,'HOLD: parent pre-gate clearance absent'
BUILD=Path(APPROVAL['ordinary_artifact']['build_directory'])
ENGINE=Path(APPROVAL['ordinary_artifact']['image'])
EXPECTED=APPROVAL['ordinary_artifact']['sha256']
assert isinstance(EXPECTED,str) and len(EXPECTED)==64
OUT=PREP.parent/'bitplane-pin-summary-pregate-20261020-01'
MASK={0,1,2,3,4,5,8,9,10,11,12,13}
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,d):
    with Path(p).open('x') as f: json.dump(d,f,indent=2);f.write('\n')
def terminal(path):
    row=json.loads(Path(path).read_text())
    assert row['actual_tool_terminal_observed'] is True and row['exit_code']==0
    assert (row.get('terminal_chunk_id') or row.get('chunk_id') or row.get('terminal_chunk') or '').strip()
def pins():
    names=['run.mjs','combine.mjs','continuous.mjs','seed-command-controls.mjs',
           'seed-persistence-controls.mjs','accepted-games-v1.json','continuous-switching-v1.json']
    files=[KIT/n for n in names]+[PREP/n for n in ['run_pregate.py','direct_wire_tap.mjs','sync_control_tap.mjs','reconcile_pregate.mjs','pregate-clearance.json','pregate-plan.json']]+[BUILD/'receipt.json',BUILD/'archive-receipt.json',ENGINE]
    plan=json.loads((PREP/'pregate-plan.json').read_text())
    files += [BUILD/'source-before'/name for name in {**plan['native_sha256'],**plan['tools_sha256']}]
    files += [Path(path) for path in json.loads((PREP/'pregate-clearance.json').read_text())['dependencies']]
    return {str(p):sha(p) for p in files}
def command(name,argv,env=None):
    with (OUT/(name+'.stdout')).open('xb') as o,(OUT/(name+'.stderr')).open('xb') as e:
        start=time.time();p=subprocess.run(argv,stdout=o,stderr=e,env=env)
    result={'argv':argv,'exit_code':p.returncode,'started':start,'finished':time.time()}
    write(OUT/(name+'.terminal.json'),result)
    return result
def replay(name,argv):
    config=OUT/(name+'.tap.json')
    write(config,{'version':1,'argv':[str(ENGINE),'--diagnostic-seed-command'],
      'image':str(ENGINE),'directory':str(OUT/(name+'.raw')),'maxBytes':32*1024*1024})
    env=os.environ.copy();env['ROOK2_DIRECT_TAP_CONFIG']=str(config)
    result=command(name,['node','--import',str(PREP/'direct_wire_tap.mjs'),*argv],env)
    report=json.loads((OUT/(name+'.json')).read_text())
    raw=json.loads((OUT/(name+'.raw/receipt.json')).read_text())
    assert result['exit_code']==0 and report['pass'] is True,(name,result)
    assert raw['failure'] is None and raw['exit']=={'code':0,'signal':None} and raw['native'],name
    for row in raw['raw'].values():
        assert row['bytes']==row['observedBytes'] and sha(row['path'])==row['sha256'],name
    return name
def main():
    assert os.sched_getaffinity(0)==MASK
    assert sha(ENGINE)==EXPECTED
    clearance=json.loads((PREP/'pregate-clearance.json').read_text());assert clearance['authorized'] is True
    plan=json.loads((PREP/'pregate-plan.json').read_text())
    assert clearance['plan_sha256']==sha(PREP/'pregate-plan.json')
    assert clearance['untimed_parallel_work_acknowledged'] is True
    assert str(OUT)==plan['output'] and str(ENGINE)==plan['ordinary_artifact']['image']
    assert EXPECTED==plan['ordinary_artifact']['sha256']
    assert set(clearance['prerequisites'])=={'postuse54_wire24','own_pgo70'}
    required=[ENGINE,BUILD/'receipt.json',BUILD/'archive-receipt.json',BUILD/'tool-terminal.json',
      Path(plan['source_freeze']),Path(plan['profile']['path']),Path(plan['profile']['training_record'])]
    required += [PREP/n for n in ['run_pregate.py','direct_wire_tap.mjs','sync_control_tap.mjs','reconcile_pregate.mjs']]
    required += [KIT/n for n in ['run.mjs','combine.mjs','continuous.mjs','seed-command-controls.mjs',
      'seed-persistence-controls.mjs','accepted-games-v1.json','continuous-switching-v1.json']]
    required.append(Path('/usr/bin/node'))
    for row in clearance['prerequisites'].values():
        assert row['complete'] is True and row['source_graph_sha256']==plan['source_graph_sha256']
        assert row['proof'] and row['actual_terminals']
        required.append(Path(row['proof']))
        for path in row['actual_terminals']:
            required.append(Path(path));terminal(path)
    assert clearance['dependencies'] and all(str(path) in clearance['dependencies'] for path in required)
    for path,h in clearance['dependencies'].items():assert sha(path)==h
    terminal(BUILD/'tool-terminal.json')
    source=json.loads(Path(plan['source_freeze']).read_text())
    assert source['files']=={**plan['native_sha256'],**plan['tools_sha256']}
    assert len(plan['native_sha256'])==51 and len(plan['tools_sha256'])==23
    b=json.loads((BUILD/'receipt.json').read_text())
    assert b['outcome']=='build-succeeded-with-stable-input-snapshot'
    assert b['binary_output']['sha256']==EXPECTED and b['pgo']['mode']=='profile-use' and b['pgo']['inputs_unchanged']
    assert b['source_sha256_before']==b['source_sha256_after']==plan['native_sha256']
    assert b['tool_sha256_before']==b['tool_sha256_after']==plan['tools_sha256']
    assert b['toolchain']==plan['toolchain']
    assert b['pgo']['profile']==plan['profile']['path']
    assert b['pgo']['input_sha256_before']==b['pgo']['input_sha256_after']==plan['profile']['input_sha256']
    assert sha(plan['profile']['path'])==plan['profile']['sha256']
    for name,h in {**plan['native_sha256'],**plan['tools_sha256']}.items():
        assert sha(BUILD/'source-before'/name)==h
    before=pins();OUT.mkdir()
    write(OUT/'binding.json',{'before':before,'engine_sha256':EXPECTED,'image':str(ENGINE),'affinity':sorted(MASK),
      'scope':'Untimed exact own-PGO57 regular pre-gate after current57 strict/wire+ownPGO70 pass; full195 native/117 are separately parent-owned; full3288 external, no CPU qualification.',
      'parallel_independent_games':3})
    fixture=json.loads((KIT/'accepted-games-v1.json').read_text())
    games=fixture['games'];assert len(games)==12 and sum(len(g['plies']) for g in games)==632
    def one(g):
        name=g['id']
        return replay(name,[str(KIT/'run.mjs'),'--game',name,'--timeout-ms','300000',
          '--report',str(OUT/(name+'.json')),'--',str(ENGINE)])
    completed=[]
    try:
        for start in range(0,len(games),3):
            with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
                futures={pool.submit(one,g):g['id'] for g in games[start:start+3]}
                for f in concurrent.futures.as_completed(futures):
                    completed.append(f.result());print('PASSED',completed[-1],len(completed),flush=True)
        replay('continuous',[str(KIT/'continuous.mjs'),'--timeout-ms','300000',
          '--report',str(OUT/'continuous.json'),'--',str(ENGINE)])
        r=command('combine',['node',str(KIT/'combine.mjs'),'--report',str(OUT/'combined.json'),
          '--continuous',str(OUT/'continuous.json'),*[str(OUT/(g['id']+'.json')) for g in games]])
        assert r['exit_code']==0
        combined=json.loads((OUT/'combined.json').read_text());assert combined['pass'] and combined['completeFocusedReplay']
        config=OUT/'seed-command-controls.tap.json'
        write(config,{'version':1,'image':str(ENGINE),'directory':str(OUT/'seed-command-controls.raw')})
        env=os.environ.copy();env['ROOK2_SYNC_TAP_CONFIG']=str(config)
        r=command('seed-command-controls',['node','--import',str(PREP/'sync_control_tap.mjs'),str(KIT/'seed-command-controls.mjs'),
          '--',str(ENGINE)],env);assert r['exit_code']==0
        # Persistence controls launch one live child. Retain their raw bytes too.
        name='seed-persistence-controls';config=OUT/(name+'.tap.json')
        write(config,{'version':1,'argv':[str(ENGINE),'--diagnostic-seed-command'],
          'image':str(ENGINE),'directory':str(OUT/(name+'.raw')),'maxBytes':32*1024*1024})
        env=os.environ.copy();env['ROOK2_DIRECT_TAP_CONFIG']=str(config)
        r=command(name,['node','--import',str(PREP/'direct_wire_tap.mjs'),str(KIT/(name+'.mjs')),'--',str(ENGINE)],env)
        assert r['exit_code']==0
        raw=json.loads((OUT/(name+'.raw/receipt.json')).read_text())
        assert raw['failure'] is None and raw['native'] and raw['exit']=={'code':0,'signal':None}
        after=pins();assert before==after
        write(OUT/'outcome.json',{'complete':True,'engine_sha256':EXPECTED,'games':12,'searches':632,
          'continuous_searches':8,'after':after,'scope':'Untimed own-PGO pre-gate only; no performance or external3288 transfer'})
        return 0
    except BaseException as error:
        write(OUT/'failure.json',{'error':repr(error),'completed':completed,'after':pins()})
        raise
if __name__=='__main__':sys.exit(main())
