import os,subprocess,threading
from pathlib import Path
def run_and_watch(command,cwd,env,out,err,engine):
 p=subprocess.Popen(command,cwd=cwd,env=env,stdout=out,stderr=err);seen={};stop=threading.Event()
 def watch():
  while not stop.is_set():
   try:children=(Path('/proc')/str(p.pid)/'task'/str(p.pid)/'children').read_text().split()
   except OSError:children=[]
   for child in children:
    try:
     args=[x.decode(errors='replace') for x in (Path('/proc')/child/'cmdline').read_bytes().split(b'\0') if x]
     if args and args[0]==str(engine):seen[int(child)]={'pid':int(child),'argv':args,'affinity':sorted(os.sched_getaffinity(int(child)))}
    except OSError:pass
   stop.wait(.001)
 t=threading.Thread(target=watch);t.start();code=p.wait();stop.set();t.join();return subprocess.CompletedProcess(command,code),list(seen.values())
