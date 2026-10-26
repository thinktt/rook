"""Reversible user-owned Herdr/Codex task affinity for the declared native window."""
import os
from pathlib import Path

def identity(task):
    text=(task/'stat').read_text();return int(text[text.rfind(')')+2:].split()[19])

def selected_processes():
    result=[]
    for p in Path('/proc').iterdir():
        if not p.name.isdigit():continue
        try:
            if p.stat().st_uid!=os.getuid():continue
            comm=(p/'comm').read_text().strip();argv=(p/'cmdline').read_bytes().split(b'\0')
            chosen=comm in ['herdr','codex','codex-code-mode'] or (comm=='node' and any(x.endswith(b'/.local/bin/codex') for x in argv))
            if chosen:result.append(p)
        except (FileNotFoundError,ProcessLookupError):pass
    return result

class Placement:
    def __init__(self):self.original={};self.leaders={};self.events=[]
    def apply(self,cpus):
        rows=[]
        for p in selected_processes():
            try:
                pid=int(p.name);leader=(pid,identity(p));self.leaders.setdefault(leader,sorted(os.sched_getaffinity(pid)))
                for t in (p/'task').iterdir():
                    try:
                        tid=int(t.name);key=(pid,tid,identity(t));before=sorted(os.sched_getaffinity(tid));self.original.setdefault(key,before)
                        os.sched_setaffinity(tid,set(cpus));after=sorted(os.sched_getaffinity(tid));assert after==sorted(cpus)
                        rows.append(dict(pid=pid,tid=tid,starttime=key[2],before=before,after=after))
                    except (FileNotFoundError,ProcessLookupError):pass
            except (FileNotFoundError,ProcessLookupError):pass
        os.sched_setaffinity(0,set(cpus));record=dict(cpus=sorted(cpus),selectedTasks=rows,selfAffinity=sorted(os.sched_getaffinity(0)));self.events.append(record);return record
    def restore(self):
        rows=[]
        for p in selected_processes():
            try:
                pid=int(p.name);fallback=self.leaders.get((pid,identity(p)))
                if fallback is None:continue
                for t in (p/'task').iterdir():
                    try:
                        tid=int(t.name);key=(pid,tid,identity(t));cpus=self.original.get(key,fallback);os.sched_setaffinity(tid,set(cpus));rows.append(dict(pid=pid,tid=tid,starttime=key[2],restored=sorted(os.sched_getaffinity(tid)),inheritedNewThread=key not in self.original))
                    except (FileNotFoundError,ProcessLookupError):pass
            except (FileNotFoundError,ProcessLookupError):pass
        return rows
