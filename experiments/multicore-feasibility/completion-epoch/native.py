import importlib.util,json,os,pathlib,signal,subprocess,sys,time
ROOT=pathlib.Path('/home/legolas/rook2-multicore')
HERE=ROOT/'experiments/multicore-feasibility/completion-epoch'
RAW=pathlib.Path('/home/legolas/rook2-experiments/completion-epoch-20261029-01')
H={0,1,2,3,8,9,10,11,12,13}
spec=importlib.util.spec_from_file_location('completion_epoch_housekeeping',ROOT/'experiments/multicore-feasibility/coarse-pure-salvage/housekeeping.py')
h=importlib.util.module_from_spec(spec);spec.loader.exec_module(h)

def main():
    stage=sys.argv[1];assert stage in ['prepare','collect']
    placement=h.Placement();record=dict(schema='rook2-completion-epoch-housekeeping-v1',helperCpus=sorted(H),applies=[],restored=None,failure=None)
    child=None;code=None
    try:
     record['applies'].append(placement.apply(H))
     record['originals']=[dict(pid=p,tid=t,starttime=s,affinity=m) for (p,t,s),m in sorted(placement.original.items())]
     record['leaders']=[dict(pid=p,starttime=s,affinity=m) for (p,s),m in sorted(placement.leaders.items())]
     command=['/usr/bin/python3',str(HERE/'prepare.py'),'--preparation',str(HERE/'preparation.json'),'--output',str(RAW),'--stage',stage]
     child=subprocess.Popen(command,cwd=ROOT,start_new_session=True)
     code=child.wait(timeout=3600)
    except BaseException as error:
     record['failure']=repr(error)
     if child is not None and child.poll() is None:
      os.killpg(child.pid,signal.SIGINT)
      try:child.wait(timeout=15)
      except subprocess.TimeoutExpired:
       os.killpg(child.pid,signal.SIGKILL);child.wait()
     raise
    finally:
     record['restored']=placement.restore();record['postRestoreSelfAffinity']=sorted(os.sched_getaffinity(0))
     if RAW.exists():
      with (RAW/('housekeeping-'+stage+'.json')).open('x') as output: output.write(json.dumps(record,indent=2)+'\n')
    print('native wrapper terminal',stage,code,flush=True)
    sys.exit(code)


if __name__=='__main__': main()
