const worker = new Worker('./minimal-worker.js', { type: 'module' })

worker.onmessage = ({ data }) => {
  if (data.channel === 1) console.log(data.text)
  if (data.channel === 2) console.error(data.text)
}


window.worker = worker 