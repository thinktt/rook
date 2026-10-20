#!/usr/bin/python3
"""Offline custom equivalence/provenance checks. Never emits released-schema passes."""
import hashlib, json, re, sys
from pathlib import Path

def load(p): return json.loads(Path(p).read_text())
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(p,d):
    with Path(p).open('x') as f: json.dump(d,f,indent=2); f.write('\n')
def locate(p):
    return Path(str(p).replace('/home/legolas/rook2/evidence/', '/home/legolas/rook2-experiments/original-worktree/evidence/'))
B=Path(sys.argv[1]); plan=load(B/'plan.json'); image=plan['image']; identity=plan['imageSha256']
K=Path(plan['kit']); fixture=load(K/'accepted-games-v1.json')
for p,h in plan['pins'].items(): assert sha(p)==h, p
assert sha(image)==identity

def raw(receipt):
    streams={}; total=0
    for n in ['stdin','stdout','stderr']:
        row=receipt['raw'][n]; data=locate(row['path']).read_bytes()
        assert hashlib.sha256(data).hexdigest()==row['sha256']
        assert len(data)==row['bytes']==row.get('observedBytes',row['bytes'])
        assert row.get('discardedObservedBytes',0)==0
        streams[n]=data.decode('ascii'); total+=len(data)
    return streams,total

def game_wire(streams,games):
    out=streams['stdout'].splitlines(keepends=True)
    assert all(line.endswith('\n') and '\r' not in line for line in out)
    out=[x[:-1] for x in out]; cursor=0; searches=posts=0; inputs=[]; traces=[]
    def take(s):
        nonlocal cursor
        assert cursor<len(out) and out[cursor]==s, (cursor,s,out[cursor:cursor+1]); cursor+=1
    for game in games:
        inputs.extend(['xboard','new','force','post','easy','level 0 5 0',*game['initialMoves'],'cm_parm default'])
        take('cm_parm default')
        for row in game['plies']:
            commands=game['personalityCommands'][row['personality']]
            inputs.extend(['force',*commands,f"king_seed {row['seed']}",f"time {row['clockCentiseconds']}",f"otim {row['clockCentiseconds']}",'go'])
            for command in commands: take(command)
            take(f"king_seed {row['seed']}")
            for expected in row['expected']['posts']:
                assert cursor<len(out)
                match=re.fullmatch(r'\s*(\d+)\s+([+-]?\d+)\s+([+-]?\d+)\s+(\d+)\s+(.+)',out[cursor]); assert match
                depth,evaluation,cs,search_id=map(int,match.groups()[:4])
                actual={'depthToken':depth,'evaluation':evaluation,'engineCentiseconds':cs,'searchId':search_id,'pv':match[5].strip().replace('0','O')}
                assert depth>=1000 and actual==expected, (cursor,actual,expected)
                cursor+=1; posts+=1
            take('move '+row['expected']['move'])
            if row['expected']['result'] is not None: take(row['expected']['result'])
            traces.append(f"KING_SEARCH_SEED seed={row['seed']}"); searches+=1
    inputs.append('quit')
    assert streams['stdin']=='\n'.join(inputs)+'\n'
    assert streams['stderr']=='\n'.join(traces)+'\n'
    assert cursor==len(out)
    return {'searches':searches,'posts':posts,'stdoutRecords':cursor,'stderrRecords':len(traces)}

def reuse():
    source=Path(plan['reuseSummary']); summary=load(source)
    assert summary['complete'] and summary['complete12'] and summary['failure'] is None
    assert len(summary['runs'])==48
    entries=[]; native_pids=set(); selected_totals={'searches':0,'posts':0,'rawBytes':0}
    for game in fixture['games']:
        candidates=[r for r in summary['runs'] if r['game']==game['id'] and r['repeat']==0 and r['warmup'] is True]
        assert len(candidates)==1
        selected=candidates[0]; result_path=locate(selected['result']); d=result_path.parent; result=load(result_path)
        assert sha(result_path)==selected['result_sha256']
        assert selected['failure'] is None and result['failure'] is None and result['cleanup'] is None
        assert result['comparator_exit']==0 and result['capture'] is True and result['game']==game['id']
        for name,h in result['file_sha256'].items(): assert sha(d/name)==h,(d,name)
        replay=load(d/'replay.json'); native=load(d/'native.json'); wire=load(d/'wire/receipt.json')
        assert replay['pass'] is True and replay['version']==2 and replay['mode']=='independent-games'
        assert replay['fixtureSha256']==sha(K/'accepted-games-v1.json') and replay['runnerSha256']==sha(K/'run.mjs')
        assert replay['selectedGameIds']==[game['id']]
        assert replay['games']==[{'id':game['id'],'family':game['family'],'searches':len(game['plies']),'pass':True}]
        assert len(replay['processes'])==1
        process=replay['processes'][0]
        assert process['gameIds']==[game['id']] and process['family']==game['family']
        assert process['code']==0 and process['signal'] is None and process['forced'] is False
        assert native['engine_sha256_before']==native['engine_sha256_after']==identity
        assert native['argv']==[native['engine'],'--diagnostic-seed-command']
        assert locate(native['engine'])==Path(image)
        assert replay['command'][0]==native['python_executable']
        assert replay['executableSha256']==native['python_executable_sha256']
        assert replay['command'][1]==str(Path(plan['repo'])/'tools/account_native.py')
        assert native['launcher_sha256']==sha(replay['command'][1])
        assert native['exec_error'] is None and native['failure'] is None and native['supervisor_signals']==[]
        assert native['native_exit_code']==0 and native['native_wait_status']==0
        assert result['native_pid']==native['native_pid']==wire['native']['pid']
        assert wire['native']['image']==native['engine']
        assert wire['launcherPid']==native['supervisor_pid']
        assert wire['argv']==replay['command']+['--diagnostic-seed-command']
        assert wire['launcherExit']=={'code':0,'signal':None}
        assert wire['failure'] is None and wire['pending'] is None
        assert native['native_pre_exec']['affinity']==native['native_post_exec']['affinity']==[14]
        assert native['native_post_exec']['path']==native['engine']
        assert native['native_pid'] not in native_pids; native_pids.add(native['native_pid'])
        streams,total=raw(wire); counts=game_wire(streams,[game]); assert counts['searches']==result['searches']
        assert counts['stdoutRecords']==process['stdoutRecords'] and counts['stderrRecords']==process['stderrRecords']
        assert process['outputBytes']==wire['raw']['stdout']['bytes']+wire['raw']['stderr']['bytes']
        for k in ['searches','posts']: selected_totals[k]+=counts[k]
        selected_totals['rawBytes']+=total
        entries.append({'game':game['id'],'repeat':0,'warmup':True,'historicalResult':selected['result'],
                        'result':str(result_path),'resultSha256':sha(result_path),
                        'replay':str(d/'replay.json'),'replaySha256':sha(d/'replay.json'),
                        'native':str(d/'native.json'),'nativeSha256':sha(d/'native.json'),
                        'wireReceipt':str(d/'wire/receipt.json'),'wireReceiptSha256':sha(d/'wire/receipt.json'),
                        'nativePid':native['native_pid'],**counts,'rawBytes':total})
    assert len(entries)==len(native_pids)==12 and selected_totals=={'searches':632,'posts':5801,'rawBytes':760487}
    return {'schema':'rook2-reviewed-independent12-equivalence-v1','customReconciliationPass':True,
            'releasedCombineInvoked':False,'selection':'repeat0/warmup, current fixture order; all48 original lifetimes preserved',
            'summary':str(source),'summarySha256':sha(source),'imageSha256':identity,'nativeArgvSuffix':['--diagnostic-seed-command'],
            'games':12,**selected_totals,'entries':entries,
            'limitation':'Original replay executableSha256 identifies Python, and per-game --record paths differ. This is custom reviewed native equivalence under released README, not a rewritten/combined released-schema pass.'}

reuse_result=reuse()
if '--reuse-only' in sys.argv:
    put(B/'reuse-index.json',reuse_result)
    print(json.dumps({k:v for k,v in reuse_result.items() if k!='entries'})); sys.exit(0)
assert load(B/'reuse-index.json')==reuse_result
fresh={}; pids=set()
for stage,count in [('continuous',1),('seed-command-controls',11),('seed-persistence-controls',1)]:
    d=B/stage; terminal=load(d/'terminal.json'); assert terminal['returncode']==0 and terminal['cleanup'] is None
    assert (d/'comparator.stderr').read_bytes()==b''
    assert load(d/'wire/launch-count.json')=={'expected':count,'observed':count}
    receipts=[]; native_files=list((d/'native').glob('*.json'))
    assert len(native_files)==2*count
    for index in range(count):
        receipt=load(d/'wire'/f'{index:02d}'/'receipt.json'); pid=receipt['pid']
        n=load(d/'native'/f'{pid}.json'); owned=load(d/'native'/f'{pid}.owned.json')
        assert n['supervisor_pid']==owned['supervisor_pid']==pid
        assert n['native_pid']==owned['native_pid']==n['waited_pid']==n['pre_exec']['pid']
        assert n['native_pid'] not in pids;pids.add(n['native_pid'])
        assert n['pre_exec']['pgid']==owned['pgid']==terminal['pid']
        assert n['supervisor_affinity']==plan['helperCpus'] and n['pre_exec']['affinity']==[14]
        assert n['failure'] is None and n['exec_error'] is None and n['signals']==[]
        assert receipt['error'] is None and receipt['signal'] is None
        assert n['native_signal'] is None and n['native_exit_code']==receipt['status']
        assert n['image']==image and n['image_sha256_before']==n['image_sha256_after']==receipt['imageBefore']==receipt['imageAfter']==identity
        expected_args=[] if stage=='seed-command-controls' and index==10 else ['--diagnostic-seed-command']
        assert n['argv']==[image,*expected_args]
        if 'post_exec' in n:
            assert n['post_exec']['exe']==image and n['post_exec']['argv']==n['argv']
            assert n['post_exec']['affinity']==[14] and n['post_exec']['tasks']==[n['native_pid']]
        assert receipt['argv']==plan['launcherCommand']+expected_args
        assert receipt['argv']==load(d/'tap-config.json')['expectedCalls'][index]
        streams,total=raw(receipt); receipts.append({'receipt':receipt,'native':n,'streams':streams,'rawBytes':total})
    fresh[stage]=receipts

continuous=fresh['continuous'][0]; report=load(B/'continuous/report.json')
schedule=load(K/'continuous-switching-v1.json'); games=[]
for segment in schedule['segments']:
    game=next(g for g in fixture['games'] if g['id']==segment['game'])
    games.append({**game,'plies':game['plies'][:segment['searches']]})
continuity_counts=game_wire(continuous['streams'],games)
assert continuity_counts['searches']==8 and len(games)==4 and continuous['native']['native_exit_code']==0
assert report['pass'] is True and report['version']==1 and report['mode']=='continuous-switching'
assert report['hostTimeoutMs']==60000 and report['command']==plan['launcherCommand']
assert report['fixtureSha256']==sha(K/'accepted-games-v1.json') and report['scheduleSha256']==sha(K/'continuous-switching-v1.json')
assert report['runnerSha256']==sha(K/'continuous.mjs') and report['comparatorSha256']==sha(K/'run.mjs')
assert report['executableSha256']==sha('/usr/bin/python3')
assert report['games']==[{'id':g['id'],'family':g['family'],'searches':len(g['plies']),'pass':True} for g in games]
assert len(report['processes'])==1
process=report['processes'][0]
assert process['code']==0 and process['signal'] is None and process['forced'] is False
assert process['gameIds']==[g['id'] for g in games]
for k in ['stdoutRecords','stderrRecords']: assert process[k]==continuity_counts[k]
assert process['outputBytes']==len(continuous['streams']['stdout'].encode())+len(continuous['streams']['stderr'].encode())

cases=[('xboard\nking_seed 0\nking_seed 4294967295\nking_seed 0xffffffff\nking_seed 010\nking_seed +7\nking_seed -0\n\tking_seed\t0X10  \nking_seed 31\r\nquit\n','king_seed 0\nking_seed 4294967295\nking_seed 4294967295\nking_seed 8\nking_seed 7\nking_seed 0\nking_seed 16\nking_seed 31\n','',0)]
cases.extend((f'king_seed {v}\n','','king-native: invalid diagnostic seed command\n',1) for v in ['08','4294967296','-1','7 extra','1.0','+','abc',''])
cases.extend([( 'king_seed\nquit\n','Error (unknown command): king_seed\n','',0),('king_seed 7\nquit\n','Error (unknown command): king_seed\n','',0)])
for item,case in zip(fresh['seed-command-controls'],cases,strict=True):
    assert [item['streams'][n] for n in ['stdin','stdout','stderr']]==list(case[:3])
    assert item['native']['native_exit_code']==case[3]
control=load(B/'seed-command-controls/comparator.stdout')
assert control=={'pass':True,'acceptedAssignments':8,'invalidAssignments':8,'noValueUnknown':True,'normalModeUnknown':True,'conflictChecked':False}

persistent=fresh['seed-persistence-controls'][0]; streams=persistent['streams']
setup=['xboard','new','force','nopost','easy','level 0 5 0','cm_parm default md=1 rnd=0']; search=['time 18100','otim 18100','go']
assert streams['stdin']=='\n'.join([*setup,'king_seed 3735928559',*search,*setup,*search,*setup,'king_seed 17',*search,'quit'])+'\n'
assert streams['stderr']=='KING_SEARCH_SEED seed=3735928559\nKING_SEARCH_SEED seed=3735928559\nKING_SEARCH_SEED seed=17\n'
lines=streams['stdout'].splitlines(keepends=True); assert len(lines)==8 and all(x.endswith('\n') for x in lines)
for index,line in [(0,'cm_parm default md=1 rnd=0\n'),(1,'king_seed 3735928559\n'),(3,'cm_parm default md=1 rnd=0\n'),(5,'cm_parm default md=1 rnd=0\n'),(6,'king_seed 17\n')]:assert lines[index]==line
for index in [2,4,7]: assert re.fullmatch(r'move [a-h][1-8][a-h][1-8][qrbn]?\n',lines[index],re.I)
assert persistent['native']['native_exit_code']==0
assert load(B/'seed-persistence-controls/comparator.stdout')=={'pass':True,'searches':3,'consumedSeeds':[3735928559,3735928559,17],'cleanExit':True}
assert len(pids)==13
for p,h in plan['pins'].items():assert sha(p)==h,p
result={'schema':'rook2-exact62-focused-custom-reconciliation-v1','customReconciliationPass':True,
        'releasedComparators':{'continuous':True,'seedCommandControls':True,'seedPersistenceControls':True},
        'reusedIndependent':{'games':12,'searches':632,'posts':5801,'nativeExits0':12,'selection':'repeat0/warmup'},
        'continuity':{'processes':1,'segments':4,**continuity_counts,'exit0':True},
        'seedControls':{'processes':11,'expectedFatalExit1':8,'exit0':3,'optionalSequenceConflict':False},
        'persistence':{'processes':1,'searches':3,'consumedSeeds':[3735928559,3735928559,17],'exit0':True},
        'freshNativeLifetimes':13,'freshSearches':11,'freshExit0':5,'freshExpectedExit1':8,
        'freshRawBytes':sum(x['rawBytes'] for rows in fresh.values() for x in rows),
        'nativeImageSha256':identity,'nativeConfiguration':'image plus --diagnostic-seed-command, except required disabled-option ordinary child',
        'reuseIndexSha256':sha(B/'reuse-index.json'),'planSha256':sha(B/'plan.json'),
        'releasedCombineInvoked':False,'frozenReportsRewritten':False,
        'qualification':'Finite local evidence only. Custom reviewed equivalence route; owner acceptance, full3288 and performance qualification remain separate.'}
put(B/'independent-reconciliation.json',result); print(json.dumps(result))
