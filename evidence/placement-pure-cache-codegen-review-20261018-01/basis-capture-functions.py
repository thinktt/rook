"""Capture bounded named bodies; no builds, probes, or engine invocation."""
from pathlib import Path
import hashlib
import json
import os
import subprocess

HERE = Path(__file__).resolve().parent
KEYS = {
    'activity': 'activity7compute',
    'king-pressure': 'activity13king_pressure',
    'q': '12visit_q_impl',
    'ordinary': '19visit_ordinary_impl',
    'ordering': '14ordering_phase',
    'charge': '11charge_node',
    'evaluation': '9full_impl',
    'root-run': '_ZN5rook23run17h',
}

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def main():
    assert sorted(os.sched_getaffinity(0)) == [0,1,2,3,4,5,8,9,10,11,12,13]
    identity = json.loads((HERE / 'identity.json').read_text())
    captured = {}
    commands = []
    for side, inputs in identity['images'].items():
        directory = HERE / side
        image = Path(inputs['image'])
        assert sha(image) == inputs['image_sha256']
        symbols = [line.split(maxsplit=3) for line in
                   (directory / 'nm-mangled.stdout').read_text().splitlines()]
        symbols = [row for row in symbols if len(row) == 4]
        captured[side] = {}
        for name, key in KEYS.items():
            matches = [row for row in symbols if key in row[3]]
            assert len(matches) == 1, (side, name, matches)
            start, size = int(matches[0][0],16), int(matches[0][1],16)
            command = ['/usr/bin/taskset','-c','0-5,8-13','/usr/bin/objdump',
                '-d','-C','-Mintel','--no-show-raw-insn',
                '--start-address='+hex(start),'--stop-address='+hex(start+size),str(image)]
            outpath = directory / (name + '.asm')
            errpath = directory / (name + '.stderr')
            with outpath.open('xb') as out, errpath.open('xb') as err:
                returned = subprocess.run(command, stdout=out, stderr=err)
            commands.append(dict(side=side, name=name, argv=command,
                exit_code=returned.returncode, actual_child_return_observed=True))
            assert returned.returncode == 0 and errpath.stat().st_size == 0
            captured[side][name] = dict(address=hex(start), bytes=size,
                symbol=matches[0][3], saved_asm_sha256=sha(outpath))
    assert all(sha(path) == digest for path,digest in identity['source_input_sha256'].items())
    with (HERE / 'function-capture.json').open('x') as out:
        json.dump(dict(complete=True, functions=captured,commands=commands,
            native_engine_runs=0,build_runs=0),out,indent=2)
        out.write('\n')
    print(json.dumps(dict(complete=True,functions=captured,commands=len(commands))))

if __name__ == '__main__':
    main()
