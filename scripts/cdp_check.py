import json
import os
import shutil
import subprocess
import sys
import time
import urllib.request
import websocket

DATA_DIR = r'C:\tmp\edge_debug_py'
if os.path.isdir(DATA_DIR):
    try:
        shutil.rmtree(DATA_DIR)
    except Exception:
        pass
os.makedirs(DATA_DIR, exist_ok=True)

edge_exe = r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe'
cmd = [
    edge_exe,
    f'--user-data-dir={DATA_DIR}',
    '--no-first-run',
    '--remote-debugging-port=9222','--remote-allow-origins=*',
    'http://localhost:5173/',
]
print('Starting Edge...', file=sys.stderr)
proc = subprocess.Popen(cmd)
# Wait for port
for _ in range(30):
    try:
        with urllib.request.urlopen('http://localhost:9222/json/list', timeout=1) as r:
            targets = json.loads(r.read().decode())
            if targets:
                break
    except Exception:
        pass
    time.sleep(0.5)
else:
    print('Edge did not start', file=sys.stderr)
    proc.terminate()
    sys.exit(1)

page = None
for t in targets:
    if t.get('type') == 'page' and 'localhost:5173' in t.get('url', ''):
        page = t
        break
if not page:
    page = next((t for t in targets if t.get('type') == 'page'), None)
print('Page target:', page.get('url') if page else None, file=sys.stderr)

ws_url = page['webSocketDebuggerUrl']
ws = websocket.create_connection(ws_url)

def send(obj):
    ws.send(json.dumps(obj))

send({"id": 1, "method": "Runtime.enable"})
send({"id": 2, "method": "Log.enable"})
send({"id": 3, "method": "Page.enable"})
# Reload to capture load events
send({"id": 4, "method": "Page.reload", "params": {"ignoreCache": True}})

# Collect messages for a while
end = time.time() + 12
while time.time() < end:
    try:
        msg = json.loads(ws.recv_timeout(2))
    except websocket.WebSocketTimeoutException:
        continue
    except Exception as e:
        print('recv err', e, file=sys.stderr)
        break
    method = msg.get('method', '')
    if method in ('Runtime.exceptionThrown', 'Log.entryAdded'):
        print(json.dumps(msg, indent=2))

# Evaluate state
send({
    "id": 10,
    "method": "Runtime.evaluate",
    "params": {
        "expression": "JSON.stringify({title: document.title, hasMapCanvas: !!document.querySelector('.maplibregl-canvas'), hasMapContainer: !!document.getElementById('map'), bodySnippet: document.body.innerHTML.slice(0,1500)})",
        "returnByValue": True,
    },
})
try:
    resp = json.loads(ws.recv_timeout(5))
    print('EVAL_RESULT:', json.dumps(resp, indent=2))
except Exception as e:
    print('eval err', e, file=sys.stderr)

ws.close()
proc.terminate()
print('Done', file=sys.stderr)
