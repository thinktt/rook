import os,sys
os.execv('/usr/bin/python3',['/usr/bin/python3','/home/legolas/rook2/tools/account_native.py','--engine','/work/artifacts/rook2-instrumented','--record','/work/training/native/'+str(os.getpid())+'.json','--known-single-process',*sys.argv[1:]])
