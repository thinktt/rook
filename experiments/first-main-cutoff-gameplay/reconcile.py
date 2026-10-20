#!/usr/bin/python3
"""Independent complete raw/native closure; original combined report remains literal."""
import hashlib,json,os,re,sys
from pathlib import Path
load=lambda p:json.loads(Path(p).read_text())
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(p,d):
 with Path(p).open('x') as f:json.dump(d,f,indent=2);f.write('\n')
def locate(p):return Path(p)
B=Path(sys.argv[1]);plan=load(B/'plan.json');image=plan['image'];identity=plan['imageSha256'];K=Path(plan['kit']);fixture=load(K/'accepted-games-v1.json')
for p,h in plan['pins'].items():assert sha(p)==h,p
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

fresh={};pids=set();nativeRecords=[];unavailable=[]
def native(stage,pid,expected_args):
 d=B/stage;n=load(d/'native'/f'{pid}.json');o=load(d/'native'/f'{pid}.owned.json');terminal=load(d/'terminal.json')
 assert pid==n['supervisor_pid']==o['supervisor_pid']
 assert n['native_pid']==o['native_pid']==n['waited_pid']==n['pre_exec']['pid']
 assert n['native_pid'] not in pids;pids.add(n['native_pid'])
 assert n['pre_exec']['pgid']==o['pgid']==terminal['pid']
 assert n['supervisor_affinity']==plan['helperCpus'] and n['pre_exec']['affinity']==[14]
 assert n['failure'] is None and n['exec_error'] is None and n['signals']==[] and n['native_signal'] is None
 assert n['image']==image and n['image_sha256_before']==n['image_sha256_after']==identity
 assert n['argv']==[image,*expected_args]
 assert n['wait_status']==n['native_exit_code']<<8
 if 'post_exec' in n:
  assert n['post_exec']['exe']==image and n['post_exec']['argv']==n['argv']
  assert n['post_exec']['affinity']==[14] and n['post_exec']['tasks']==[n['native_pid']]
 else:
  assert n['post_exec_unavailable'] in ['FileNotFoundError','ProcessLookupError','PermissionError'];unavailable.append({'stage':stage,'pid':n['native_pid'],'reason':n['post_exec_unavailable']})
 assert not Path(f'/proc/{pid}').exists() and not Path(f"/proc/{n['native_pid']}").exists()
 nativeRecords.append({'stage':stage,'supervisorPid':pid,'nativePid':n['native_pid'],'exit':n['native_exit_code'],'receiptSha256':sha(d/'native'/f'{pid}.json')})
 return n
for stage,count in [('games',12),('continuous',1),('seed-command-controls',11),('seed-persistence-controls',1)]:
 d=B/stage;t=load(d/'terminal.json');assert t['returncode']==0 and t['cleanup'] is None
 assert not (d/'comparator.stderr').read_bytes()
 assert load(d/'wire/launch-count.json')=={'expected':count,'observed':count}
 assert len(list((d/'native').glob('*.json')))==2*count
 receipts=[]
 for index in range(count):
  receipt=load(d/'wire'/f'{index:02d}'/'receipt.json');pid=receipt['pid'];args=[] if stage=='seed-command-controls' and index==10 else ['--diagnostic-seed-command']
  n=native(stage,pid,args)
  assert receipt['error'] is None and receipt['signal'] is None and receipt['status']==n['native_exit_code']
  assert receipt['imageBefore']==receipt['imageAfter']==identity
  assert receipt['configSha256']==sha(d/'tap-config.json')
  assert receipt['argv']==plan['launcherCommand']+args==load(d/'tap-config.json')['expectedCalls'][index]
  streams,total=raw(receipt);receipts.append({'receipt':receipt,'native':n,'streams':streams,'rawBytes':total})
 fresh[stage]=receipts
report=load(B/'games/report.json')
assert report['pass'] and report['version']==2 and report['mode']=='independent-games'
assert report['fixtureSha256']==sha(K/'accepted-games-v1.json') and report['runnerSha256']==sha(K/'run.mjs')
assert report['command']==plan['launcherCommand'] and report['executableSha256']==sha('/usr/bin/python3')
assert report['completeIndependentGames'] and not report['completeGameplayQualification'] and not report['completeFocusedReplay']
assert report['selectedGameIds']==[g['id'] for g in fixture['games']]
assert report['inventory']==report['fixtureInventory']=={'games':12,'searches':632,'families':{'main':4,'openings':4,'switching':4}}
assert len(report['games'])==len(report['processes'])==12
all_games=[];game_counts={'searches':0,'posts':0,'rawBytes':0}
for game,row,process,record in zip(fixture['games'],report['games'],report['processes'],fresh['games'],strict=True):
 counts=game_wire(record['streams'],[game]);assert counts['searches']==len(game['plies'])
 assert row=={'id':game['id'],'family':game['family'],'searches':len(game['plies']),'pass':True}
 assert process['gameIds']==[game['id']] and process['family']==game['family']
 assert process['code']==record['native']['native_exit_code']==0 and process['signal'] is None and not process['forced']
 for k in ['stdoutRecords','stderrRecords']:assert process[k]==counts[k]
 assert process['outputBytes']==len(record['streams']['stdout'].encode())+len(record['streams']['stderr'].encode())
 for k in ['searches','posts']:game_counts[k]+=counts[k]
 game_counts['rawBytes']+=record['rawBytes'];all_games.append({'id':game['id'],**counts})
assert game_counts['searches']==632 and game_counts['posts']==5801
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
def event(line):
 if line.startswith('move '):
  assert re.fullmatch(r'move [a-h][1-8][a-h][1-8][qrbn]?',line),line
  return {'type':'move','move':line[5:]}
 if line.startswith('stat01: '):
  m=re.fullmatch(r'stat01: +(-?\d+) +(\d+) +(-?\d+) +(\d+) +(\d+)(?: (.*))?',line);assert m,line
  cs,sid,depth,remaining,total=map(int,m.groups()[:5])
  return dict(type='status',engineCentiseconds=cs,searchId=sid,depthToken=depth,remaining=remaining,total=total,pv=(m[6] or '').replace('0','O'))
 m=re.fullmatch(r' *(-?\d+) +([+-]?\d+) +(\d+) +(\d+)(?: (.*))?',line);assert m,line
 depth,score,cs,sid=map(int,m.groups()[:4])
 return dict(type='post',depthToken=depth,evaluation=score,engineCentiseconds=cs,searchId=sid,pv=(m[5] or '').replace('0','O'))

wireFixture=load(plan['wireFixture']);wire=load(B/'wire/output/receipt.json');wireRows=load(B/'wire/native-pids.json');wireRawBytes=0;wirePosts=0
assert wire['engine']==plan['wireLauncher'] and wire['engine_sha256_before']==wire['engine_sha256_after']==sha(plan['wireLauncher'])
assert wire['fixture_sha256']==sha(plan['wireFixture']) and wire['checker_sha256']==sha(plan['wireChecker']) and wire['pass']
assert wire['effective_affinity']==plan['helperCpus'] and wire['performance_sample'] is False
assert len(wire['results'])==len(wireFixture['cases'])==len(wireRows)==8
assert load(B/'wire/terminal.json')['returncode']==0 and load(B/'wire/terminal.json')['cleanup'] is None and not (B/'wire/comparator.stderr').read_bytes()
assert load(B/'wire/comparator.stdout')=={'output':str(B/'wire/output'),'passed':True,'cases':8}
for case,row,observed in zip(wireFixture['cases'],wire['results'],wireRows,strict=True):
 assert row['id']==observed['case']==case['id'] and observed['argv']==[plan['wireLauncher']] and observed['observer_after_original_init']
 n=native('wire',observed['pid'],[]);assert n['native_exit_code']==row['exit_code']==row['observed_exit_code']==0 and row['complete_streams'] and row['status']=='pass'
 streams={}
 for name in ['stdin','stdout','stderr']:
  data=(B/'wire/output'/case['id']/(name+'.raw')).read_bytes();meta=row['raw'][name]
  assert len(data)==meta['bytes'] and hashlib.sha256(data).hexdigest()==meta['sha256'] and data.isascii();streams[name]=data;wireRawBytes+=len(data)
 assert streams['stderr']==b'' and streams['stdout'].endswith(b'\n') and b'\r' not in streams['stdout']
 output=streams['stdout'].decode().splitlines();at=0;commands=[]
 assert len(case['request']['input']['searches'])==len(case['expected']['results'])==len(row['searches'])==3
 for request,answer,actual in zip(case['request']['input']['searches'],case['expected']['results'],row['searches'],strict=True):
  commands.extend(request['commands']+[f"time {request['allowanceCs']}",'cm_parm','go']+request['queued'])
  for text in request['commands']:
   if text.startswith('cm_parm '):assert output[at]==' '.join(text.split());at+=1
  assert output[at]=='cm_parm';at+=1;events=[]
  for expected in answer['events']:
   got=event(output[at]);at+=1;assert got==expected;events.append(got);wirePosts+=got['type']=='post'
  abort=bool(request['queued'] and request['queued'][-1]=='force')
  if abort:assert output[at]=='aborting search ...';at+=1
  assert actual=={'status':'pass','events':events,'abort':abort}
 commands.append('quit');assert streams['stdin']==('\n'.join(commands)+'\n').encode() and at==len(output)
assert len(list((B/'wire/native').glob('*.json')))==16
assert len(pids)==len(nativeRecords)==33 and sum(r['exit']==1 for r in nativeRecords)==8 and sum(r['exit']==0 for r in nativeRecords)==25
combined=load(B/'combine/report.json');assert load(B/'combine/terminal.json')['returncode']==0 and load(B/'combine/terminal.json')['cleanup'] is None
assert not (B/'combine/comparator.stderr').read_bytes()
assert combined==load(B/'combine/comparator.stdout') and combined['pass'] and combined['completeIndependentGames'] and combined['completeFocusedReplay'] and not combined['completeGameplayQualification']
assert combined['inventory']=={'games':12,'searches':632,'families':{'main':4,'openings':4,'switching':4}} and combined['reportCount']==1
assert combined['command']==plan['launcherCommand'] and combined['executableSha256']==sha('/usr/bin/python3') and combined['runnerSha256']==sha(K/'run.mjs')
assert combined['reports']==[{'path':str(B/'games/report.json'),'sha256':sha(B/'games/report.json')}]
assert combined['continuity']['report']=={'path':str(B/'continuous/report.json'),'sha256':sha(B/'continuous/report.json')}
for path,h in plan['pins'].items():assert sha(path)==h,path
source=load(plan['sourceFreeze'])
for name,h in source['candidateFiles'].items():assert sha(Path(source['root'])/name)==h,name
for name,h in source['canonicalFiles'].items():assert sha(Path(plan['repo'])/name)==h,name
result={'verified':True,'nativeImageSha256':identity,'sourceAndArtifactsUnchanged':True,'games':{'nativeLifetimes':12,'games':12,**game_counts,'details':all_games},'continuity':{'nativeLifetimes':1,'segments':4,**continuity_counts},'seedCommandControls':{'nativeLifetimes':11,'expectedFatalExit1':8,'exit0':3,'optionalSequenceConflict':False},'seedPersistence':{'nativeLifetimes':1,'searches':3,'consumedSeeds':[3735928559,3735928559,17]},'wire':{'nativeLifetimes':8,'fixtures':8,'searches':24,'posts':wirePosts,'rawBytes':wireRawBytes,'originalCheckerUnchanged':True,'literalAcceptedRawParser':True},'nativeLifetimes':33,'nativeExit0':25,'nativeExpectedExit1':8,'postExecObservationsAvailable':33-len(unavailable),'postExecObservationsUnavailable':unavailable,'allNativeSupervisorPidsAbsent':True,'completeRawBytes':sum(x['rawBytes'] for rows in fresh.values() for x in rows)+wireRawBytes,'completeRawInputCleanupAndOutputConsumed':True,'originalCombinedFocusedReport':{'path':str(B/'combine/report.json'),'sha256':sha(B/'combine/report.json'),'completeFocusedReplay':True,'completeGameplayQualification':False},'nativeReceipts':nativeRecords,'engineRunsByIndependentChecker':0,'performanceMeasurement':False,'noNativeRetry':True,'scope':'Finite exact-image local behavioral coverage; full3288, performance qualification, promotion, Q1 and specification-owner acceptance remain separate.'}
assert result['completeRawBytes']<512*1024**2
put(B/'independent-reconciliation.json',result);print(json.dumps({k:v for k,v in result.items() if k!='nativeReceipts'}))
