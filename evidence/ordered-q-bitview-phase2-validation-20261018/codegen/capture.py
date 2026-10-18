from pathlib import Path
import subprocess,hashlib,json,os,difflib
OUT=Path(__file__).parent
BASE=Path("/home/legolas/rook2/evidence")
BUILD_DIRS={"phase1":"ordered-bit-checkers-phase1-build-20261018","phase2":"ordered-q-bitview-phase2-build-02-20261018"}
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
records=[]; identities={}
for tool in ["nm","size","objdump","readelf","python3"]:
    done=subprocess.run([tool,"--version"],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    dest=OUT/(tool+"-version.txt"); dest.write_bytes(done.stdout+done.stderr)
    records.append({"argv":[tool,"--version"],"exit_code":done.returncode,"output":dest.name,"sha256":sha(dest)})
for label,dirname in BUILD_DIRS.items():
    build=BASE/dirname; receipt=json.loads((build/"receipt.json").read_text()); binary=build/"rook2-exact"
    source={name:sha(build/"source-before"/name) for name in receipt["source_sha256_before"]}
    assert source==receipt["source_sha256_before"]
    tools={name:sha(build/"source-before"/name) for name in receipt["tool_sha256_before"]}
    assert tools==receipt["tool_sha256_before"]
    assert sha(binary)==receipt["binary_output"]["sha256"]
    identities[label]={"build":str(build),"binary":str(binary),"binary_sha256":sha(binary),"receipt_sha256":sha(build/"receipt.json"),"source_sha256":source,"tool_source_sha256":tools,"verified_snapshot_files":len(source)+len(tools),"build_settings":{k:receipt[k] for k in ["mode","target_triple","target_cpu","rust_flags","pgo","toolchain","argv","build_effective_environment"]}}
    commands={"nm-demangled.txt":["nm","-n","-S","--defined-only","-C",str(binary)],"nm-raw.txt":["nm","-n","-S","--defined-only",str(binary)],"size.txt":["size","-A",str(binary)],"sections.txt":["readelf","-SW",str(binary)],"disassembly.txt":["objdump","-d","-w","-C","--no-show-raw-insn",str(binary)]}
    for name,argv in commands.items():
        done=subprocess.run(argv,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        dest=OUT/(label+"-"+name); dest.write_bytes(done.stdout)
        err=OUT/(label+"-"+name+".stderr"); err.write_bytes(done.stderr)
        records.append({"argv":argv,"exit_code":done.returncode,"stdout":dest.name,"stdout_sha256":sha(dest),"stderr":err.name,"stderr_sha256":sha(err)})
        assert done.returncode==0
before=identities["phase1"]["source_sha256"]; after=identities["phase2"]["source_sha256"]
changed=[n for n in sorted(set(before)|set(after)) if before.get(n)!=after.get(n)]
(OUT/"source-diff.txt").write_text("".join("".join(difflib.unified_diff((BASE/BUILD_DIRS["phase1"]/"source-before"/name).read_text().splitlines(True),(BASE/BUILD_DIRS["phase2"]/"source-before"/name).read_text().splitlines(True),fromfile="phase1/"+name,tofile="phase2/"+name)) for name in changed))
assert identities["phase1"]["binary_sha256"]=="132ba1356b06423763b4f6328825ef93b22b91ba374bc26ff92f0ef71e0e6c81"
assert identities["phase2"]["binary_sha256"]=="3462a87a37f90188808efbf5128e57eb65837aae0f2e6a23bbeec4c5392e2d24"
for field in ["mode","target_triple","target_cpu","rust_flags","pgo","toolchain"]:
    assert identities["phase1"]["build_settings"][field]==identities["phase2"]["build_settings"][field],field+" differs"
assert set(changed)=={"src/attacks.rs","src/movegen.rs","src/quiescence.rs"}
assert identities["phase1"]["tool_source_sha256"]==identities["phase2"]["tool_source_sha256"]
(OUT/"inputs.json").write_text(json.dumps({"affinity":sorted(os.sched_getaffinity(0)),"artifacts":identities,"changed_source_paths":changed},indent=2)+"\n")
(OUT/"commands.json").write_text(json.dumps(records,indent=2)+"\n")
print(json.dumps({"changed_source_paths":changed,"command_count":len(records),"binary_sha256":{k:v["binary_sha256"] for k,v in identities.items()}},indent=2))
