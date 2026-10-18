import {spawn} from 'node:child_process';
const argv=["/usr/bin/python3", "/home/legolas/rook2/tools/account_native.py", "--engine", "/usr/bin/python3.13", "--record", "/home/legolas/rook2/evidence/wire-tap-controls-20261018/test_nonzero_exit_is_retained_without_stream_mutation/native.json", "--known-single-process", "/home/legolas/rook2/evidence/wire-tap-controls-20261018/test_nonzero_exit_is_retained_without_stream_mutation/native-control.py", "7"];

const child=spawn(argv[0],argv.slice(1),{stdio:['pipe','pipe','pipe']});
let out='',sent=false,quit=false;
child.stdin.on('error',()=>{});
child.stdout.on('data',chunk=>{
  process.stdout.write(chunk);
  out+=chunk.toString('utf8');
  if (!sent && out.includes('READY\n')) {
    sent=true; child.stdin.write(Buffer.from('g'));
    setImmediate(()=>child.stdin.write('o\n'));
  }
  if (!quit && out.includes('move a1b2\n')) {
    quit=true; child.stdin.write('quit\n');
  }
});
child.stderr.on('data',chunk=>process.stderr.write(chunk));
child.on('error',()=>{process.exitCode=1;});
child.on('close',(code,signal)=>{process.exitCode=code ?? 1;});
