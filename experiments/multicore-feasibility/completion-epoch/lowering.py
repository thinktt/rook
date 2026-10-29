#!/usr/bin/env python3
"""Two bounded objdump inspections using the existing completion-fence helper.

Import and audit_result start no process. Source-correlated instruction sites and
surrounding text are retained; unresolved sites or a different strong-store/
flag-load/terminal-exchange mechanism stop preparation before comparison.
"""
import argparse
import importlib.util
import os
from pathlib import Path
import re
import signal
import sys
import time

sys.dont_write_bytecode=True
from common import (CONTROL_SHA,CONTROL_CRATE,DEFAULT_CRATE,HELPERS,LOWERING_BASE,
    image_layout,read,sha,snapshot,write)
from source_check import extract,check

spec=importlib.util.spec_from_file_location('completion_epoch_existing_binutils',LOWERING_BASE)
base=importlib.util.module_from_spec(spec);spec.loader.exec_module(base)
SCHEMA='rook2-completion-epoch-lowering-v1'
TOOL=base.TOOLS['objdump']
CAP_SECONDS=120
WORKER='src/colors_worker.rs'


def sites(path,candidate):
    source=path.read_text();active=extract(source,'run_active')
    start=source.index(active);first=source.count('\n',0,start)+1
    lines=active.splitlines()
    def line_of(text):
        found=[first+i for i,line in enumerate(lines) if text in line]
        assert len(found)==1,(text,found)
        return [found[0],found[0]]
    result=dict(normalDone=line_of('reader.done.store(generation, Ordering::'+('SeqCst' if candidate else 'Release')+');'),
        normalFlag=line_of('let waiting = shared.latch.waiting.load(Ordering::SeqCst);' if candidate else 'signal_completion(shared);'))
    done_line=result['normalDone'][0]
    ends=[first+i for i,line in enumerate(lines) if first+i>done_line and line.strip()=='continue;']
    assert ends,'normal publication end unresolved'
    result['normalPublication']=[done_line,ends[0]]
    for label,name in [('coldTerminal','signal_completion'),('coldWait','wait_completion')]:
        body=extract(source,name);begin=source.index(body)
        result[label]=[source.count('\n',0,begin)+1,source.count('\n',0,begin+len(body))+1]
    return result


def excerpts(dump,source,candidate,label):
    """The existing line-correlated extraction pattern, narrowed to the normal publication and cold protocol sites."""
    ranges=sites(source,candidate);lines=dump.read_text(errors='replace').splitlines(True)
    anchors={name:[] for name in ranges};instructions={name:[] for name in ranges}
    locations=set();pending=set();new_context=False;symbol=None
    for index,line in enumerate(lines):
        header=re.match(r'^([0-9a-fA-F]+) <(.+)>:\s*$',line)
        if header: symbol=header[2];locations=set();pending=set();new_context=False
        if re.search(r'\.rs:\d+',line):
            if not new_context: pending=set()
            new_context=True
            match=re.search(r'colors_worker\.rs:(\d+)',line)
            if match: pending.add(int(match[1]))
        code=re.match(r'^\s*([0-9a-fA-F]+):\s+(?:(?:[0-9a-fA-F]{2})\s+)+\s*(\S.*)$',line)
        if code:
            if new_context: locations=pending;new_context=False
            for name,(low,high) in ranges.items():
                if any(low<=location<=high for location in locations):
                    anchors[name].append(index)
                    instructions[name].append(dict(address=code[1],symbol=symbol,sourceLines=sorted(locations),text=code[2].strip()))
    observed,artifacts={},{}
    for name in ranges:
        assert anchors[name],(label,name,'unresolved source-correlated machine site')
        selected=set()
        for index in anchors[name]: selected.update(range(max(0,index-18),min(len(lines),index+19)))
        text=''.join(lines[index] for index in sorted(selected))
        filename=label+'.'+name+'.asm';artifacts[filename]=text
        observed[name]=dict(sourceLineRange=ranges[name],instructions=instructions[name],
            assemblyArtifact=filename,assemblyBytes=len(text.encode()),
            context='18 raw objdump lines on either side of every source-correlated instruction; full dump retained')
    return observed,artifacts


def mechanism(observed):
    """Check each designated site; surrounding/global counts are not evidence."""
    def text(label,site):return '\n'.join(row['text'] for row in observed[label][site]['instructions'])
    done=text('candidate','normalDone');flag=text('candidate','normalFlag')
    assert re.search(r'\bxchg\w*\s+[^\n]*\(',done),'normal SC done store is not the expected memory xchg'
    assert re.search(r'\bmov\w*\s+[^\n]*\(',flag),'normal SC flag load is not a memory mov'
    assert not re.search(r'\b(?:lock|xchg\w*|cmpxchg\w*|xadd\w*|[msl]fence)\b',flag),'normal flag site has RMW/fence'
    for label in ['control','candidate']:
        assert re.search(r'\bxchg\w*\s+[^\n]*\(',text(label,'coldTerminal')),(label,'retained terminal exchange unresolved')
    return dict(admitted=True,sitesResolved=True,normalDone='source-correlated memory xchg',
        normalFlag='source-correlated memory mov with no RMW/explicit fence at designated site',
        coldTerminal='source-correlated memory xchg in both images',
        manualReview='Inspect saved addresses/registers and surrounding assembly before collection; source correlation is a bounded observation, not a compiler proof or isolated cost attribution')


def input_paths(control,candidate,old,new):
    paths=[Path(__file__).resolve(),Path(__file__).with_name('common.py'),Path(__file__).with_name('source_check.py'),
        LOWERING_BASE,TOOL.resolve(),control,candidate]
    paths += [Path(fn.__code__.co_filename).resolve() for fn in [image_layout,read,sha,snapshot,write]]
    paths += [crate/name for crate in [old,new] for name in snapshot(crate)]
    return sorted(set(path.resolve() for path in paths))


def audit_result(path,control,image,controlcrate,candidatecrate):
    path,control,image=Path(path).resolve(),Path(control).resolve(),Path(image).resolve()
    old,new=Path(controlcrate).resolve(),Path(candidatecrate).resolve()
    value=read(path);assert value['schema']==SCHEMA and value['complete'] is True
    assert value['control']==image_layout(control) and value['control']['sha256']==CONTROL_SHA
    assert value['candidate']==image_layout(image)
    assert value['controlCrate']==str(old) and value['candidateCrate']==str(new)
    assert value['sourceSha256']==dict(control=snapshot(old),candidate=snapshot(new))
    assert value['sourceAdmission']==check(old,new)
    assert set(value['inputSha256'])=={str(item) for item in input_paths(control,image,old,new)}
    for name,digest in value['inputSha256'].items():assert sha(name)==digest,name
    observed={};expected_raw=set()
    for index,(label,engine,crate) in enumerate([('control',control,old),('candidate',image,new)]):
        run=read(path.parent/(label+'.objdump.json'))
        assert value['toolRuns'][index]==run and run['argv']==[str(TOOL),'-d','-C','-l','--inlines',str(engine)]
        assert run['exit']==0 and run['failure'] is None and run['cleanupSignals']==[]
        assert value['startedMonotonicNs']<=run['startedMonotonicNs']<run['endedMonotonicNs']<run['deadlineMonotonicNs']<=value['deadlineMonotonicNs']
        for suffix in ['stdout','stderr']:
            raw=path.parent/run[suffix];assert sha(raw)==run[suffix+'Sha256'] and raw.stat().st_size==run[suffix+'Bytes']
        observed[label],artifacts=excerpts(path.parent/(label+'.objdump.stdout'),crate/WORKER,label=='candidate',label)
        for filename,text in artifacts.items():assert (path.parent/filename).read_text()==text
        expected_raw.update(artifacts)
        expected_raw.update(label+'.objdump.'+suffix for suffix in ['json','stdout','stderr'])
    assert len(value['toolRuns'])==2 and value['observed']==observed
    assert value['mechanism']==mechanism(observed)
    assert set(value['rawSha256'])==expected_raw
    for filename,digest in value['rawSha256'].items():assert sha(path.parent/filename)==digest
    assert value['elapsedNs']==value['endedMonotonicNs']-value['startedMonotonicNs']>0
    assert value['endedMonotonicNs']<value['deadlineMonotonicNs']==value['startedMonotonicNs']+CAP_SECONDS*10**9
    return value


def main():
    def interrupted(signum,_frame):raise InterruptedError('external signal '+str(signum))
    for signum in [signal.SIGINT,signal.SIGTERM]:signal.signal(signum,interrupted)
    parser=argparse.ArgumentParser(description=__doc__)
    for name in ['control','engine','output']:parser.add_argument('--'+name,type=Path,required=True)
    parser.add_argument('--control-crate',type=Path,default=CONTROL_CRATE)
    parser.add_argument('--candidate-crate',type=Path,default=DEFAULT_CRATE)
    args=parser.parse_args();out=args.output.resolve();out.mkdir()
    start=time.monotonic_ns();deadline=start+CAP_SECONDS*10**9
    control,image=args.control.resolve(),args.engine.resolve()
    old,new=args.control_crate.resolve(),args.candidate_crate.resolve()
    value=dict(schema=SCHEMA,complete=False,startedMonotonicNs=start,deadlineMonotonicNs=deadline,toolRuns=[],observed={})
    try:
        assert set(os.sched_getaffinity(0))==HELPERS and sha(control)==CONTROL_SHA
        inputs=input_paths(control,image,old,new)
        value.update(control=image_layout(control),candidate=image_layout(image),controlCrate=str(old),candidateCrate=str(new),
            sourceSha256=dict(control=snapshot(old),candidate=snapshot(new)),sourceAdmission=check(old,new),
            inputSha256={str(path):sha(path) for path in inputs})
        for label,target,crate in [('control',control,old),('candidate',image,new)]:
            value['toolRuns'].append(base.run_tool(out,label+'.objdump','objdump',[TOOL,'-d','-C','-l','--inlines',target],deadline-10*10**9))
            value['observed'][label],artifacts=excerpts(out/(label+'.objdump.stdout'),crate/WORKER,label=='candidate',label)
            for filename,text in artifacts.items():(out/filename).write_text(text)
        value['mechanism']=mechanism(value['observed'])
        assert all(sha(path)==digest for path,digest in value['inputSha256'].items())
        value.update(complete=True,endedMonotonicNs=time.monotonic_ns(),rawSha256={path.name:sha(path) for path in out.iterdir() if path.is_file()})
        value['elapsedNs']=value['endedMonotonicNs']-start
        write(out/'result.json',value);audit_result(out/'result.json',control,image,old,new)
        assert time.monotonic_ns()<deadline
    except BaseException as error:
        value.update(complete=False,failure=repr(error),endedMonotonicNs=time.monotonic_ns())
        write(out/'failure.json',value);raise
    print({'complete':True,'result':str(out/'result.json'),'mechanism':value['mechanism']})


if __name__=='__main__':main()
