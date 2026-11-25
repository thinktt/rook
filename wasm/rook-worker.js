
const decoder = new TextDecoder()
const encoder = new TextEncoder()
let wasm

// Functions provided by JavaScript to Rook
const imports = { rook: {
  output(channel, pointer, length) {
    const bytes = new Uint8Array(wasm.memory.buffer, pointer, length)
    const text = decoder.decode(bytes)
    
    self.postMessage({ channel, text })
  },

  epoch_seconds: () => Math.floor(Date.now() / 1000),
  poll_command: () => -1,
}}


// Fetch, compile, and instantiate then export the wasm functions
const { module, instance } = await WebAssembly.instantiateStreaming(
  fetch('/dist/rook.wasm'),
  imports
)
wasm = instance.exports


// create the chess engine
wasm.rook_init()
const engine = wasm.rook_create(0)


function sendCommand(commandTxt) {
  const command = encoder.encode(commandTxt)
  const commandPointer = wasm.rook_alloc(command.length)

  try {
    const memory = new Uint8Array(wasm.memory.buffer, commandPointer, command.length)
    memory.set(command)
    const status = wasm.rook_command(engine, commandPointer, command.length)
    return status

  } finally {
    // always free any allocated memory
    wasm.rook_free(commandPointer, command.length)
  }
}

sendCommand('xboard')
sendCommand('post')
sendCommand('level 0 5 0')


function demo() {
  const commandsStr = `
  cm_parm default
  cm_parm opp=86 opn=86 opb=86 opr=86 opq=86
  cm_parm myp=68 myn=86 myb=86 myr=86 myq=86
  cm_parm mycc=119 mymob=119 myks=17 mypp=83 mypw=17
  cm_parm opcc=119 opmob=119 opks=17 oppp=83 oppw=17
  cm_parm cfd=0 sop=27 avd=-32 rnd=0 sel=6 md=99
  cm_parm tts=16777216
  easy
  new
  time 6637
  force
  d2d4
  e7e6
  c1f4
  g8f6
  e2e3
  f6d5
  f4g3
  go
  `
  
  const commands = commandsStr.trim().split('\n').map(line => line.trim())
  
  for (const command of commands) {
    sendCommand(command)
  }
}


self.onmessage = ({ data }) => {
  if (data === 'demo') {
    demo()
    return  
  }

  sendCommand(data)
}