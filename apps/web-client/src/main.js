import './styles.css';
import { MockMapAdapter } from '@racegps/map-adapters';
const API = 'http://localhost:8787';
let ws;
let playerId = '';
let displayName = '';
let roomId = 'global-cruise';
let seq = 0;
let lat = 41.4993;
let lon = -81.6944;
const map = new MockMapAdapter();
document.querySelector('#app').innerHTML = `
  <main class="shell">
    <aside class="panel">
      <div class="brand">
        <img src="/assets/racegps-mark.svg" class="brand-mark" alt="raceGPS" />
        <div><h1>race<span>GPS</span></h1><p class="tagline">Real World Driving</p></div>
      </div>

      <section class="card">
        <p class="status"><strong>One Earth.</strong> Many cities. Many rooms. One player identity. One global career.</p>
        <label>Display name</label>
        <input id="displayName" value="Raziel13" />
        <label>Room ID</label>
        <input id="roomId" value="global-cruise" />
        <label>Mode</label>
        <select id="mode">
          <option value="cruise">Cruise</option>
          <option value="race">Race</option>
          <option value="challenge">Challenge</option>
          <option value="hot_pursuit">Hot Pursuit</option>
          <option value="explore">Explore</option>
        </select>
        <div class="btn-row"><button id="connectBtn">Connect</button><button class="secondary" id="moveBtn">Move Marker</button></div>
      </section>

      <section class="card">
        <h3>Signal Challenge</h3>
        <div class="signal-row">
          <button data-signal="flash_lights">Flash</button>
          <button data-signal="rev_engine">Rev</button>
          <button data-signal="drop_pin">Drop Pin</button>
          <button data-signal="hot_signal">Hot Signal</button>
          <button data-signal="ghost_signal">Ghost</button>
        </div>
      </section>

      <section class="card">
        <h3>Mode Spine</h3>
        <p class="status">Cruise → signal → lobby → race/chase/challenge → score → share.</p>
      </section>
    </aside>

    <section class="map-wrap">
      <div id="map"></div>
      <div class="hud">
        <div class="hud-card"><div class="status" id="status">Disconnected. Connect to enter the raceGPS world.</div></div>
        <div class="hud-card">
          <div class="chat-log" id="chatLog"></div>
          <form class="chat-form" id="chatForm"><input id="chatInput" placeholder="room chat..." maxlength="240" /><button>Send</button></form>
        </div>
      </div>
    </section>
  </main>
`;
const mapEl = document.querySelector('#map');
map.mount(mapEl);
map.setCenter({ lat, lon });
// The public folder mirrors the brand asset into Vite path at runtime if served from repo root.
const markImg = document.querySelector('.brand-mark');
if (markImg)
    markImg.onerror = () => markImg.style.display = 'none';
document.querySelector('#connectBtn').addEventListener('click', connect);
document.querySelector('#moveBtn').addEventListener('click', () => sendPosition(true));
document.querySelector('#chatForm').addEventListener('submit', (e) => { e.preventDefault(); sendChat(); });
document.querySelectorAll('[data-signal]').forEach(btn => btn.addEventListener('click', () => sendSignal(btn.dataset.signal)));
async function connect() {
    displayName = (document.querySelector('#displayName').value || 'Driver').trim();
    roomId = (document.querySelector('#roomId').value || 'global-cruise').trim();
    const mode = document.querySelector('#mode').value;
    const session = await fetch(`${API}/api/session`, {
        method: 'POST', credentials: 'include', headers: { 'content-type': 'application/json' }, body: JSON.stringify({ displayName })
    }).then(r => r.json());
    playerId = session.playerId;
    ws?.close();
    ws = new WebSocket(`ws://localhost:8787/ws/rooms/${roomId}`);
    ws.onopen = () => {
        status(`Connected as <span class="neon">${displayName}</span> in ${roomId}.`);
        ws?.send(JSON.stringify({ type: 'join_room', roomId, displayName, mode }));
        sendPosition(false);
    };
    ws.onmessage = ev => handleMessage(JSON.parse(ev.data));
    ws.onclose = () => status('Disconnected.');
}
function handleMessage(msg) {
    switch (msg.type) {
        case 'welcome':
            playerId = msg.playerId;
            break;
        case 'room_snapshot':
            chat(`[System] joined ${msg.room.title}. Players: ${msg.room.players.length}`);
            msg.room.players.forEach(p => { if (p.lat && p.lon)
                map.upsertPlayerMarker(p.playerId, { lat: p.lat, lon: p.lon }, p.displayName); });
            break;
        case 'player_joined':
            chat(`[System] ${msg.player.displayName} joined.`);
            break;
        case 'player_left':
            map.removePlayerMarker(msg.playerId);
            chat(`[System] player left.`);
            break;
        case 'player_position':
            map.upsertPlayerMarker(msg.playerId, { lat: msg.lat, lon: msg.lon }, msg.playerId === playerId ? displayName : msg.playerId);
            break;
        case 'chat_message':
            chat(`<strong>${msg.displayName}</strong>: ${escapeHtml(msg.message)}`);
            break;
        case 'challenge_signal':
            chat(`<span class="hot">[Signal]</span> ${msg.fromPlayerId} sent ${msg.signal} for ${msg.challengeType}.`);
            break;
        case 'system_message':
            chat(`[System] ${escapeHtml(msg.message)}`);
            break;
        case 'game_event':
            chat(`[Game] ${msg.playerId}: ${msg.event.kind}`);
            break;
    }
}
function sendPosition(randomize) {
    if (!ws || ws.readyState !== WebSocket.OPEN)
        return;
    if (randomize) {
        lat += (Math.random() - .5) * .01;
        lon += (Math.random() - .5) * .01;
    }
    map.upsertPlayerMarker(playerId || 'me', { lat, lon }, displayName || 'ME');
    ws.send(JSON.stringify({ type: 'player_position', roomId, lat, lon, heading: Math.random() * 360, speed: Math.random() * 80, seq: ++seq }));
}
function sendChat() {
    const input = document.querySelector('#chatInput');
    const message = input.value.trim();
    if (!message || !ws || ws.readyState !== WebSocket.OPEN)
        return;
    ws.send(JSON.stringify({ type: 'chat_message', roomId, message }));
    input.value = '';
}
function sendSignal(signal) {
    if (!ws || ws.readyState !== WebSocket.OPEN)
        return;
    ws.send(JSON.stringify({ type: 'challenge_signal', roomId, signal, challengeType: signal === 'hot_signal' ? 'hot_pursuit' : 'quick_sprint' }));
}
function chat(html) {
    const log = document.querySelector('#chatLog');
    const line = document.createElement('div');
    line.className = 'chat-line';
    line.innerHTML = html;
    log.appendChild(line);
    log.scrollTop = log.scrollHeight;
}
function status(html) { document.querySelector('#status').innerHTML = html; }
function escapeHtml(s) { return s.replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c])); }
