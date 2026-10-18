"""Bounded static own-PGO capture: no builds, probes, or engine execution."""
from pathlib import Path
import ast
import hashlib
import json
import os
import re
import subprocess

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
SIDES={
    'control':('complete117-pgo-use-build-20261018',
        '6a5ce6e27b74490e623fbb705f70c770ec12ff7e88f761fb0c7119ca2aee4a50'),
    'candidate':('activity-value-inputs-pgo-use-build-20261018-01',
        'd5ee1f3f7258f152c0a9c50664855c46f6b631e611a85bdfdae07f509654decc'),
}
FUNCTIONS={'activity':'activity7compute','evaluation':'9full_impl',
           'ordinary':'19visit_ordinary_impl','q':'12visit_q_impl'}
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def load(path):return json.loads(Path(path).read_text())
def write(path,value):
    with path.open('x') as out:json.dump(value,out,indent=2);out.write('\n')

def main():
    assert sorted(os.sched_getaffinity(0))==[0,1,2,3,4,5,8,9,10,11,12,13]
    assert os.environ['TMPDIR']=='/home/legolas/rook2-build-tmp'
    receipts={};identities={};inputs={};commands=[];metrics={}
    def run(argv,outpath):
        command=['/usr/bin/taskset','-c','0-5,8-13',*argv]
        errpath=outpath.with_suffix(outpath.suffix+'.stderr')
        with outpath.open('xb') as out,errpath.open('xb') as err:
            returned=subprocess.run(command,stdout=out,stderr=err)
        commands.append(dict(argv=command,exit_code=returned.returncode,
            actual_child_return_observed=True,stdout=str(outpath),stdout_sha256=sha(outpath)))
        assert returned.returncode==0 and errpath.stat().st_size==0
    for side,(directory,expected) in SIDES.items():
        build=ROOT/'evidence'/directory;receipt=load(build/'receipt.json')
        image=build/'rook2-exact';destination=HERE/side;destination.mkdir()
        assert sha(image)==receipt['binary_output']['sha256']==expected
        assert receipt['cargo_exit_code']==0 and receipt['pgo']['mode']=='profile-use'
        assert receipt['pgo']['input_sha256_before']==receipt['pgo']['input_sha256_after']
        assert receipt['pgo']['inputs_unchanged']
        assert receipt['source_sha256_before']==receipt['source_sha256_after']
        assert receipt['tool_sha256_before']==receipt['tool_sha256_after']
        assert len(receipt['source_sha256_before'])==46 and len(receipt['tool_sha256_before'])==23
        for name,digest in (receipt['source_sha256_before']|receipt['tool_sha256_before']).items():
            path=build/'source-before'/name;assert sha(path)==digest;inputs[str(path)]=digest
        for path,digest in receipt['pgo']['input_sha256_before'].items():
            assert sha(path)==digest;inputs[path]=digest
        training=load(receipt['pgo']['training_record'])
        verification_path=Path(receipt['pgo']['training_record']).parent/'verification.json'
        verification=load(verification_path)
        assert training['complete'] and training['engine_source_sha256']==receipt['source_sha256_before']
        assert len(training['raw_profiles_sha256'])==54
        assert training['profile_sha256']==sha(receipt['pgo']['profile'])==verification['merged_profile_sha256']
        assert verification['complete'] and verification['independent_remerge_byte_identical']
        assert verification['training_record_sha256']==sha(receipt['pgo']['training_record'])
        assert receipt['rust_flags']==['-C','target-cpu=x86-64','-C',
            'profile-use='+receipt['pgo']['profile'],'-C','llvm-args=-pgo-warn-missing-function']
        warning=(build/'build.stderr').read_text().lower()
        for text in ['no profile data available for function','profile data may be out of date',
                     'profile data mismatch','malformed instrumentation profile data','hash mismatch','unprofiled function']:
            assert text not in warning
        for path in [image,build/'receipt.json',verification_path,build/'build.stderr']:
            inputs[str(path)]=sha(path)
        receipts[side]=receipt
        identities[side]=dict(image=str(image),image_sha256=expected,receipt_sha256=sha(build/'receipt.json'),
            profile=receipt['pgo']['profile'],profile_sha256=sha(receipt['pgo']['profile']),
            training_record_sha256=sha(receipt['pgo']['training_record']),
            training_verification_sha256=sha(verification_path),native_source_files=46,tool_files=23,
            training_input_sha256=training['input_sha256'])
        run(['/usr/bin/nm','-n','-S','-C',str(image)],destination/'nm-demangled.txt')
        run(['/usr/bin/nm','-n','-S',str(image)],destination/'nm-mangled.txt')
        run(['/usr/bin/readelf','-W','-S',str(image)],destination/'sections.txt')
        run(['/usr/bin/readelf','-W','-r',str(image)],destination/'relocations.txt')
        symbols=[line.split(maxsplit=3) for line in (destination/'nm-mangled.txt').read_text().splitlines()]
        symbols=[row for row in symbols if len(row)==4]
        metrics[side]={}
        for name,key in FUNCTIONS.items():
            found=[row for row in symbols if key in row[3]];assert len(found)==1,(side,name,found)
            start,size=int(found[0][0],16),int(found[0][1],16)
            path=destination/(name+'.asm')
            run(['/usr/bin/objdump','-d','-C','-Mintel','--no-show-raw-insn',
                 '--start-address='+hex(start),'--stop-address='+hex(start+size),str(image)],path)
            instructions=[]
            for line in path.read_text().splitlines():
                match=re.match(r'^\s*([0-9a-f]+):\s+(\S+)\s*(.*)$',line)
                if match:instructions.append((int(match[1],16),match[2],match[3]))
            metrics[side][name]=dict(address=hex(start),bytes=size,symbol=found[0][3],
                prologue=[m+' '+o for _,m,o in instructions[:8]],
                rsp_subtractions=[o for _,m,o in instructions if m=='sub' and o.startswith('rsp,')],
                instruction_lines=len(instructions),static_calls=sum(m=='call' for _,m,_ in instructions),
                calls=[dict(address=hex(a),operands=o) for a,m,o in instructions if m=='call'])
    a,b=receipts['control'],receipts['candidate']
    for key in ['toolchain','mode','target_triple','target_cpu','jobs','cargo_config_sha256_before']:
        assert a[key]==b[key],key
    assert a['tool_sha256_before']==b['tool_sha256_before']
    assert a['source_sha256_before'].keys()==b['source_sha256_before'].keys()
    changes=[p for p,d in a['source_sha256_before'].items() if d!=b['source_sha256_before'][p]]
    assert changes==['src/activity.rs']
    assert identities['control']['profile_sha256']!=identities['candidate']['profile_sha256']
    assert identities['control']['training_input_sha256']==identities['candidate']['training_input_sha256']
    # Pin actual emitted payload; no new layout/ABI probe is built.
    rows=(HERE/'candidate/nm-demangled.txt').read_text().splitlines()
    table=next(line.split() for line in rows if line.endswith('rook2::activity::DESTINATION_VALUES'))
    address,size=int(table[0],16),int(table[1],16);assert size==256
    binary=Path(identities['candidate']['image']).read_bytes()
    for line in (HERE/'candidate/sections.txt').read_text().splitlines():
        match=re.match(r'^\s*\[\s*\d+\]\s+\.rodata\s+PROGBITS\s+([0-9a-f]+)\s+([0-9a-f]+)\s+([0-9a-f]+)',line)
        if match:
            start,offset,length=(int(x,16) for x in match.groups());break
    assert start<=address and address+size<=start+length
    actual=binary[offset+address-start:offset+address-start+size]
    text=(ROOT/'evidence'/SIDES['control'][0]/'source-before/src/activity.rs').read_text()
    matrix=ast.literal_eval(re.search(r'const DESTINATION_VALUE:.*?= (\[.*?\n\]);',text,re.S)[1])
    rook=ast.literal_eval(re.search(r'const ROOK_SEVENTH:.*?= (\[.*?\]);',text)[1])
    expected=bytes(rook[s%8] if variant and rank==6 else matrix[rank][s%8]
        for color in range(2) for variant in range(2) for s in range(64)
        for rank in [s//8 if color==0 else 7-s//8])
    assert actual==expected and binary.count(expected)==1
    (HERE/'candidate/destination-values.hex').write_text(actual.hex()+'\n')
    assert all(sha(path)==digest for path,digest in inputs.items())
    write(HERE/'capture.json',dict(complete=True,identities=identities,source_changes=changes,
        inputs_sha256=inputs,metrics=metrics,commands=commands,
        actual_table=dict(address=hex(address),bytes=size,full_payload_occurrences=1,
            source_construction_matches_actual_bytes=True),
        native_engine_runs=0,builds=0,probes=0,profilers=0,performance_claim=False))
    print(json.dumps(dict(complete=True,commands=len(commands),table=hex(address),
        metrics={side:{name:{k:v for k,v in item.items() if k!='calls'} for name,item in values.items()}
                 for side,values in metrics.items()})))

if __name__=='__main__':main()
