#!/usr/bin/env python3
"""Matched generic study build, adapted from the archived opt-in census builder."""
import argparse
import os
from pathlib import Path
import shlex
import shutil
import signal
import subprocess
import sys
import time

sys.dont_write_bytecode=True
from common import (HERE,ROOT,DEFAULT_CRATE,PRESERVED_CRATE,FEATURE,BINARY,DRIVER,
    HELPERS,baseline,read,write,sha,snapshot)

FLAGS=['-C','target-cpu=x86-64','-C','panic=unwind']


def environment():
    env=dict(os.environ,PATH='/usr/bin:/bin',RUSTC='/usr/bin/rustc',CARGO_INCREMENTAL='0')
    for key in list(env):
        if key in ['CARGO_ENCODED_RUSTFLAGS','CARGO_BUILD_RUSTFLAGS','RUSTFLAGS','RUSTC_WRAPPER',
                   'RUSTC_WORKSPACE_WRAPPER','LLVM_PROFILE_FILE'] or key.startswith(('CARGO_PROFILE_','ROOK2_')):
            env.pop(key,None)
    env.update(RUSTFLAGS=' '.join(FLAGS),CARGO_PROFILE_RELEASE_PANIC='unwind')
    return env


def command(crate,out,variant):
    return ['/usr/bin/cargo','build','--offline','--locked','--verbose','--release','--jobs','4',
        *(['--features',FEATURE] if variant=='new' else []),'--target','x86_64-unknown-linux-gnu',
        '--bin',BINARY,'--target-dir',str(out/'target')]


def effective_options(directory,variant):
    commands=[shlex.split(line.split('Running `',1)[1].rsplit('`',1)[0])
        for line in (directory/'stderr').read_text().splitlines() if 'Running `' in line]
    result={}
    for source in ['src/lib.rs',DRIVER]:
        matches=[cmd for cmd in commands if any(token==source or token.endswith('/'+source) for token in cmd)]
        assert len(matches)==1,(source,len(matches));cmd=matches[0];options={}
        features=[token for token in cmd if token.startswith('feature=')]
        assert features==(['feature="'+FEATURE+'"'] if variant=='new' else [])
        for index,token in enumerate(cmd):
            if token=='-C':value=cmd[index+1]
            elif token.startswith('-C') and len(token)>2:value=token[2:]
            else:continue
            key,sep,value=value.partition('=');value=value if sep else True
            assert key not in options or (key=='panic' and options[key]==value=='unwind')
            options[key]=value
        for key,value in [('opt-level','3'),('panic','unwind'),('codegen-units','1'),('debuginfo','1'),('target-cpu','x86-64')]:
            assert options.get(key)==value,(source,key,options)
        assert not any(key.startswith('profile-') or key=='llvm-args' for key in options)
        if source=='src/lib.rs':assert options.get('linker-plugin-lto') is True and 'lto' not in options
        else:assert options.get('lto')=='thin' and 'linker-plugin-lto' not in options
        result[source]=options
    return result


def cargo_configs(crate):
    paths=set()
    for parent in [crate,*crate.parents]:paths.update(p for p in [parent/'.cargo/config',parent/'.cargo/config.toml'] if p.is_file())
    cargo_home=Path(os.environ.get('CARGO_HOME',str(Path.home()/'.cargo')))
    paths.update(p for p in [cargo_home/'config',cargo_home/'config.toml'] if p.is_file())
    return {str(path):sha(path) for path in sorted(paths)}


def admit(directory):
    value=read(directory/'receipt.json');variant=value['variant']
    assert variant in ['preserved','new'] and value['schema']=='rook2-replicated-control-build-v1'
    assert value['complete'] is True and value['exit']==0
    crate=PRESERVED_CRATE if variant=='preserved' else DEFAULT_CRATE
    assert value['crate']==str(crate) and value['argv']==command(crate,directory,variant)
    assert value['features']==([FEATURE] if variant=='new' else []) and value['binaryName']==BINARY
    assert value['pgo']=='none' and value['flags']==FLAGS and value['profilePanic']=='unwind'
    assert value['sourceBefore']==value['sourceAfter']==snapshot(crate)
    for name,digest in value['sourceBefore'].items():assert sha(directory/'source-before'/name)==digest
    assert value['baselineBefore']==value['baselineAfter']==baseline()
    assert value['toolsBefore']==value['toolsAfter']
    for path,digest in value['toolsBefore'].items():assert sha(path)==digest
    assert value['cargoConfig']==cargo_configs(crate)
    assert value['effectiveOptions']==effective_options(directory,variant)
    assert value['initialAffinity']==value['finalAffinity']==sorted(HELPERS)
    assert value['binary']==str(directory/BINARY) and sha(value['binary'])==value['binarySha256']
    assert value['toolchain']['rustc']['exit']==value['toolchain']['cargo']['exit']==0
    assert 'release: 1.85.1\n' in value['toolchain']['rustc']['stdout']
    assert 'LLVM version: 19.1.7\n' in value['toolchain']['rustc']['stdout']
    assert value['stdoutSha256']==sha(directory/'stdout') and value['stderrSha256']==sha(directory/'stderr')
    return value


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--variant',choices=['preserved','new'],required=True)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();variant=args.variant;out=args.output.resolve()
    crate=PRESERVED_CRATE if variant=='preserved' else DEFAULT_CRATE
    assert set(os.sched_getaffinity(0))==HELPERS
    out.mkdir();before=snapshot(crate)
    for name,digest in before.items():
        destination=out/'source-before'/name;destination.parent.mkdir(parents=True,exist_ok=True)
        shutil.copy2(crate/name,destination);assert sha(destination)==digest
    tools={str(path):sha(path) for path in [HERE/'build.py',HERE/'common.py',Path('/usr/bin/cargo'),Path('/usr/bin/rustc')]}
    receipt=dict(schema='rook2-replicated-control-build-v1',complete=False,variant=variant,crate=str(crate),
        argv=command(crate,out,variant),features=[FEATURE] if variant=='new' else [],binaryName=BINARY,
        pgo='none',flags=FLAGS,profilePanic='unwind',sourceBefore=before,baselineBefore=baseline(),
        toolsBefore=tools,cargoConfig=cargo_configs(crate),initialAffinity=sorted(os.sched_getaffinity(0)))
    write(out/'receipt.json',receipt);started=time.monotonic_ns()
    try:
        with (out/'stdout').open('xb') as stdout,(out/'stderr').open('xb') as stderr:
            child=subprocess.Popen(receipt['argv'],cwd=crate,env=environment(),stdout=stdout,stderr=stderr,start_new_session=True)
            try:code=child.wait(timeout=300)
            except BaseException:
                try:os.killpg(child.pid,signal.SIGKILL)
                except ProcessLookupError:pass
                child.wait();raise
        receipt.update(exit=code,wallNs=time.monotonic_ns()-started,sourceAfter=snapshot(crate),baselineAfter=baseline(),
            toolsAfter={path:sha(path) for path in tools},finalAffinity=sorted(os.sched_getaffinity(0)),toolchain={})
        assert code==0
        for tool in ['rustc','cargo']:
            argv=['/usr/bin/'+tool,'-Vv' if tool=='rustc' else '--version']
            result=subprocess.run(argv,capture_output=True,text=True,timeout=10,check=True)
            receipt['toolchain'][tool]=dict(argv=argv,exit=result.returncode,stdout=result.stdout,stderr=result.stderr)
        receipt['effectiveOptions']=effective_options(out,variant)
        binary=out/'target/x86_64-unknown-linux-gnu/release'/BINARY;frozen=out/BINARY
        shutil.copy2(binary,frozen)
        receipt.update(binary=str(frozen),binarySha256=sha(frozen),complete=True,
            stdoutSha256=sha(out/'stdout'),stderrSha256=sha(out/'stderr'))
        write(out/'receipt.json',receipt);admit(out);print('built '+variant+' '+receipt['binarySha256'],flush=True)
    except BaseException as error:
        receipt.update(complete=False,failure=repr(error));write(out/'receipt.json',receipt);raise


if __name__=='__main__':main()
