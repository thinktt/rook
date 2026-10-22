#!/usr/bin/python3
import os,subprocess,sys
from pathlib import Path
B=Path(__file__).resolve().parent
root=B/'rootfs'
cmd=['/usr/bin/bwrap','--bind' if '--mutable' in sys.argv else '--ro-bind',str(root),'/',
 '--unshare-user','--uid','0','--gid','0','--unshare-uts','--hostname','rook-alpine',
 '--proc','/proc','--dev','/dev','--tmpfs','/tmp',
 '--ro-bind','/home/legolas/rook2','/home/legolas/rook2',
 '--ro-bind','/home/legolas/king-spec','/home/legolas/king-spec',
 '--bind',str(B),'/work','--chdir','/work',
 '--clearenv','--setenv','PATH','/usr/local/cargo/bin:/usr/sbin:/usr/bin:/sbin:/bin',
 '--setenv','HOME','/root','--setenv','RUSTUP_HOME','/usr/local/rustup',
 '--setenv','CARGO_HOME','/usr/local/cargo','--setenv','LANG','C','--setenv','LC_ALL','C',
 '--setenv','TZ','UTC','--setenv','PYTHONDONTWRITEBYTECODE','1']
args=[a for a in sys.argv[1:] if a!='--mutable']
if '--mutable' in sys.argv:
 cmd+=['--ro-bind','/etc/resolv.conf','/etc/resolv.conf']
else:cmd+=['--unshare-net']
cmd+=['--',*args]
raise SystemExit(subprocess.call(cmd))
