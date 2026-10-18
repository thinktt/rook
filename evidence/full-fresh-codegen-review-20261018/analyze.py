from pathlib import Path
import re,json,hashlib,struct,shutil,sys
OUT=Path(__file__).parent
INPUT=json.loads((OUT/"inputs.json").read_text())
sha=lambda b:hashlib.sha256(b).hexdigest()
canon=lambda s:re.sub(r"\.llvm\.\d+","",s)
DATA={}
for label,artifact in INPUT["artifacts"].items():
    binary=Path(artifact["binary"]).read_bytes()
    sections=json.loads((OUT/(label+"-section-hashes.json")).read_text())
    chunks=re.split(r"(?m)^([0-9a-f]+) <(.+)>:\n",(OUT/(label+"-disassembly.txt")).read_text())
    bodies={int(chunks[i],16):chunks[i+2] for i in range(1,len(chunks),3)}
    symbols={}; counts={}
    for line in (OUT/(label+"-nm-demangled.txt")).read_text().splitlines():
        m=re.match(r"([0-9a-f]+) ([0-9a-f]+) ([tT]) (.*)",line)
        if not m: continue
        addr,size=int(m[1],16),int(m[2],16); name=canon(m[4]); occurrence=counts.get(name,0); counts[name]=occurrence+1
        section=sections[".text"]; offset=section["offset"]+addr-section["address"]
        body=bodies.get(addr,""); instructions=[]
        for line in body.splitlines():
            m=re.match(r"\s*([0-9a-f]+):\s*(.*)",line)
            if not m or int(m[1],16)>=addr+size: continue
            instruction=canon(m[2]); parts=instruction.split("#",1)
            if len(parts)==2 and "(%rip)" in parts[0]:
                target=re.search(r"[0-9a-f]+ <(.*)>",parts[1])
                if target:
                    instruction=re.sub(r"-?0x[0-9a-f]+\(%rip\)","RIP<"+target[1]+">",parts[0])
                else: instruction=parts[0]
            else: instruction=parts[0]
            instruction=re.sub(r"\b[0-9a-f]+ <(.*)>",r"TARGET<\1>",instruction)
            instructions.append(" ".join(instruction.split()))
        symbols[(name,occurrence)]={"name":name,"occurrence":occurrence,"address":addr,"size":size,"bytes_sha256":sha(binary[offset:offset+size]),"normalized_sha256":sha("\n".join(instructions).encode()),"instruction_count":len(instructions)}
    DATA[label]={"symbols":symbols,"binary":binary,"bodies":bodies}
A=DATA["root79"]["symbols"];B=DATA["fullfresh81"]["symbols"]; pairs=[]
for key in sorted(set(A)&set(B)):
    x,y=A[key],B[key]
    pairs.append({"name":key[0],"occurrence":key[1],"root79":x,"fullfresh81":y,"bytes_equal":x["bytes_sha256"]==y["bytes_sha256"],"normalized_equal":x["normalized_sha256"]==y["normalized_sha256"],"address_equal":x["address"]==y["address"],"size_equal":x["size"]==y["size"]})
(OUT/"function-comparison.json").write_text(json.dumps(pairs,indent=2)+"\n")
tables=[]
for a,b in [(0x8b908,0x8b8c8),(0x8b940,0x8b900),(0x8b928,0x8b8e8)]:
    targets=[]
    for label,addr in [("root79",a),("fullfresh81",b)]:
        words=struct.unpack_from("<8i",DATA[label]["binary"],addr)
        targets.append([addr+word for word in words])
    tables.append({"root79_base":a,"fullfresh81_base":b,"window_bytes":32,"root79_decoded_targets":targets[0],"fullfresh81_decoded_targets":targets[1],"equal":targets[0]==targets[1]})
(OUT/"quiescence-table-windows.json").write_text(json.dumps(tables,indent=2)+"\n")
focus=[x for x in pairs if any(s in x["name"] for s in ["rook2::evaluator::","rook2::ordinary::","rook2::quiescence::","rook2::endgame::finish"])]
summary={"matched_functions":len(pairs),"root79_function_symbols":len(A),"fullfresh81_function_symbols":len(B),"exact_bytes_equal":sum(x["bytes_equal"] for x in pairs),"normalized_equal":sum(x["normalized_equal"] for x in pairs),"same_address":sum(x["address_equal"] for x in pairs),"same_size":sum(x["size_equal"] for x in pairs),"focused_functions":focus,"normalization":"Strip instruction addresses and comments; strip LLVM module numeric suffixes; replace annotated RIP displacement with canonical referenced symbol+offset; replace annotated branch absolute addresses with canonical target symbols. Register operands, immediates, non-RIP memory offsets, instruction order and symbolic target offsets remain. Normalized equality does not establish data-referent equality; table windows are checked separately.","tool_executable_sha256":{tool:{"path":str(Path(shutil.which(tool)).resolve()),"sha256":sha(Path(shutil.which(tool)).read_bytes())} for tool in ["nm","size","objdump","readelf","python3"]}}
(OUT/"analysis-summary.json").write_text(json.dumps(summary,indent=2)+"\n")
print(json.dumps({k:v for k,v in summary.items() if k not in ["focused_functions","tool_executable_sha256","normalization"]},indent=2))
print(json.dumps([{ "name":x["name"],"bytes_equal":x["bytes_equal"],"normalized_equal":x["normalized_equal"],"instructions":x["root79"]["instruction_count"]} for x in focus],indent=2))
