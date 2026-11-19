#!/usr/bin/env python3
"""Loopback-only benchmark hosting with explicit external artifact routes."""
import argparse,json
from pathlib import Path
from http.server import SimpleHTTPRequestHandler,ThreadingHTTPServer
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--port',type=int,default=0);p.add_argument('--profiles',type=Path,required=True);a=p.parse_args()
profiles=json.loads(a.profiles.read_text());root=Path(__file__).resolve().parents[2]
class Handler(SimpleHTTPRequestHandler):
 def __init__(self,*args,**kwargs):super().__init__(*args,directory=str(root),**kwargs)
 def translate_path(self,path):
  if path.startswith('/artifact/'):
   from urllib.parse import unquote
   name=unquote(path.removeprefix('/artifact/'))
   return profiles[name]['wasm'] if name in profiles and 'wasm' in profiles[name] else str(root/'nonexistent-benchmark-artifact')
  return super().translate_path(path)
 def end_headers(self):
  self.send_header('Cross-Origin-Opener-Policy','same-origin');self.send_header('Cross-Origin-Embedder-Policy','require-corp');self.send_header('Cache-Control','no-store');super().end_headers()
server=ThreadingHTTPServer(('127.0.0.1',a.port),Handler);print(f'Open http://localhost:{server.server_address[1]}/',flush=True);server.serve_forever()
