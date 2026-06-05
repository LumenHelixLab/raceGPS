import json
import urllib.request
import websocket
import time
import sys

list_url = 'http://localhost:9222/json/list'
with urllib.request.urlopen(list_url) as resp:
    targets = json.loads(resp.read().decode())

target = None
for t in targets:
    if t.get('type') == 'page':
        target = t
        break
if not target:
    print('No page target found', file=sys.stderr)
    print(json.dumps(targets, indent=2))
    sys.exit(1)

ws_url = target['webSocketDebuggerUrl']
print('Connecting to', ws_url, file=sys.stderr)
ws = websocket.create_connection(ws_url)

def send(cmd):
    ws.send(json.dumps(cmd))

send({"id": 1, "method": "Runtime.enable"})
send({"id": 2, "method": "Log.enable"})
send({"id": 3, "method": "Page.enable"})
send({"id": 4, "method": "Page.navigate", "params": {"url": "http://localhost:5173/"}})

end = time.time() + 12
while time.time() < end:
    try:
        msg = json.loads(ws.recv())
    except Exception as e:
        print('recv error', e, file=sys.stderr)
        break
    method = msg.get('method', '')
    if method in ('Runtime.exceptionThrown', 'Log.entryAdded'):
        print(json.dumps(msg, indent=2))
    if msg.get('id') == 4 and 'result' in msg:
        print('navigation started', msg['result'], file=sys.stderr)

# Wait a bit more for scripts/load
send({"id": 5, "method": "Runtime.evaluate", "params": {"expression": "document.title", "returnByValue": True}})
send({"id": 6, "method": "Runtime.evaluate", "params": {"expression": "document.querySelector('.maplibregl-canvas') !== null", "returnByValue": True}})
try:
    for _ in range(5):
        msg = json.loads(ws.recv())
        if msg.get('id') in (5, 6):
            print(json.dumps(msg, indent=2))
except Exception as e:
    print('eval recv error', e, file=sys.stderr)

ws.close()
print('Done', file=sys.stderr)
