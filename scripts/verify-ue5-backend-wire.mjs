#!/usr/bin/env node
/**
 * Simulates RaceGPSBackendClient flow (UE5 PIE prep).
 * Usage: node scripts/verify-ue5-backend-wire.mjs
 */
const API = process.env.RACEGPS_API || 'http://127.0.0.1:8787';
const WS_BASE = API.replace(/^http/, 'ws') + '/ws/rooms';

async function createSession(name) {
  const res = await fetch(`${API}/api/session`, {
    method: 'POST',
    headers: { 'content-type': 'application/json' },
    body: JSON.stringify({ displayName: name }),
  });
  if (!res.ok) throw new Error(`session ${res.status}`);
  const session = await res.json();
  const match = (res.headers.get('set-cookie') || '').match(/racegps_sid=([^;]+)/);
  return { session, sid: match ? match[1] : '' };
}

function waitWsOpen(ws, ms = 5000) {
  return new Promise((resolve, reject) => {
    const t = setTimeout(() => reject(new Error('WS open timeout')), ms);
    ws.onopen = () => { clearTimeout(t); resolve(); };
    ws.onerror = (e) => { clearTimeout(t); reject(e); };
  });
}

function waitWsMessage(ws, type, ms = 5000) {
  return new Promise((resolve, reject) => {
    const t = setTimeout(() => reject(new Error(`timeout: ${type}`)), ms);
    ws.onmessage = (ev) => {
      try {
        const msg = JSON.parse(ev.data);
        if (msg.type === type) {
          clearTimeout(t);
          resolve(msg);
        }
      } catch { /* ignore */ }
    };
  });
}

async function main() {
  console.log('=== UE5 Backend Wire Verification ===\n');
  const health = await fetch(`${API}/health`);
  if (!health.ok) throw new Error('backend health failed');
  console.log('✓ GET /health');

  const { session, sid } = await createSession('UE5-PIE-Verify');
  if (!sid) throw new Error('no racegps_sid cookie');
  console.log(`✓ POST /api/session → ${session.playerId}`);

  const roomRes = await fetch(`${API}/api/rooms`, {
    method: 'POST',
    headers: {
      'content-type': 'application/json',
      cookie: `racegps_sid=${sid}`,
    },
    body: JSON.stringify({ title: 'UE5 PIE Test Room', mode: 'cruise' }),
  });
  if (!roomRes.ok) throw new Error(`create room ${roomRes.status}`);
  const room = await roomRes.json();
  console.log(`✓ POST /api/rooms → ${room.roomId}`);

  const { default: WebSocket } = await import('ws');
  const ws = new WebSocket(`${WS_BASE}/${room.roomId}`, {
    headers: { Cookie: `racegps_sid=${sid}` },
  });
  await waitWsOpen(ws);
  console.log('✓ WebSocket connected');

  const welcome = await waitWsMessage(ws, 'welcome');
  console.log(`✓ welcome → ${welcome.displayName || welcome.playerId}`);

  ws.send(JSON.stringify({
    type: 'chat_message',
    roomId: room.roomId,
    message: 'UE5 wire verification ping',
  }));

  ws.close();
  console.log('\nPIE wire verification PASSED — open UE5 LAN Browser with backend on 8787.');
}

main().catch((err) => {
  console.error('FAILED:', err.message);
  process.exit(1);
});