"""Offline static demo. Refresh/reset returns deterministic state; no persistence."""
import argparse
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs): super().__init__(*args, directory=str(ROOT), **kwargs)
    def do_GET(self):
        clean = self.path.split('?',1)[0]
        if clean.startswith(('/.git','/data/raw','/scripts','/.github')):
            self.send_error(404); return
        super().do_GET()
    def end_headers(self):
        self.send_header('Cache-Control','no-store')
        super().end_headers()

if __name__ == '__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--port',type=int,default=8762)
    parser.add_argument('--reset',action='store_true',help='Starts the immutable sample demo; browser reset button restores the clean view')
    args=parser.parse_args()
    print(f'Source Bridge: http://127.0.0.1:{args.port} (fixed source sample; no persisted state)',flush=True)
    ThreadingHTTPServer(('127.0.0.1',args.port),Handler).serve_forever()
