import './styles.css';
import { MapLibre3DAdapter } from '@racegps/map-adapters';
import { ArcadeCar } from './arcade-car.js';
const API = 'http://localhost:8787';
let ws;
let playerId = '';
let displayName = '';
let roomId = 'global-cruise';
let seq = 0;
let lat = 41.4993;
let lon = -81.6944;
// Street-level initial view — close to ground, looking forward
const map = new MapLibre3DAdapter({ center: { lat, lon }, zoom: 18, pitch: 75, bearing: -17.6 });
// Fetch citypack on load for buildings + roads in all modes
debug('Loading city data...');
console.log('[raceGPS] fetching citypack...');
fetch(`${API}/api/citypack`)
    .then(r => { console.log('[raceGPS] citypack status:', r.status); return r.ok ? r.json() : null; })
    .then((pack) => {
    console.log('[raceGPS] citypack loaded:', pack?.name, 'roads:', pack?.roads?.length, 'buildings:', pack?.buildings?.length);
    debug(`City: ${pack?.name || 'unknown'} | Roads: ${pack?.roads?.length || 0} | Buildings: ${pack?.buildings?.length || 0}`);
    cityPackData = pack;
    if (!pack)
        return;
    if (pack.roads)
        map.drawRoads(pack.roads);
    if (pack.buildings)
        map.drawBuildings(pack.buildings);
    tryEnterStreetView();
})
    .catch(err => { console.error('[raceGPS] citypack fetch failed:', err); debug('Citypack failed'); });
// Race state
let currentLobbyId = '';
let raceActive = false;
let raceStartMs = 0;
let cpIndex = 0;
const totalCPs = 5; // matches default
// Driving state
let speed = 0; // m/s
let heading = 0; // degrees, 0 = north
const keys = {};
let driveInterval;
let serverCrashed = false;
// City data for street view
let cityPackData = null;
let streetViewEntered = false;
let arcadeOriginLat = 0;
let arcadeOriginLon = 0;
// Arcade kinematic car (no physics engine)
const arcadeCar = new ArcadeCar();
let arcadeReady = false;
document.querySelector('#app').innerHTML = `
  <main class="shell">
    <!-- Street-level HUD overlay -->
    <div class="hud-overlay">
      <div class="compass" id="compass">
        <div class="compass-arrow">▲</div>
        <div class="compass-label">N</div>
      </div>
      <div class="gear-indicator" id="gearIndicator">D</div>
      <div class="speed-flash" id="speedFlash"></div>
      <div class="debug-panel" id="debugPanel">Initializing...</div>
    </div>
    <aside class="panel">
      <div class="brand">
        <img src="/assets/racegps-mark.svg" class="brand-mark" alt="raceGPS" />
        <div><h1>race<span>GPS</span></h1><p class="tagline">Real World Driving</p></div>
      </div>

      <section class="card" id="connectCard">
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
        <div class="btn-row" style="margin-top:8px">
          <button class="secondary" id="spawnCarBtn">🚗 Spawn Car</button>
          <button class="secondary" id="autoDriveBtn">▶ Auto Drive</button>
        </div>
        <label style="margin-top:12px">Car Model</label>
        <div class="car-picker">
          <button class="car-btn active" data-car="/models/kenney-sedan-sports.glb">🏎️ Sports Sedan</button>
          <button class="car-btn" data-car="/models/kenney-race.glb">🏁 Race Car</button>
          <button class="car-btn" data-car="/models/kenney-suv.glb">🚙 SUV</button>
          <button class="car-btn" data-car="/models/kenney-taxi.glb">🚕 Taxi</button>
          <button class="car-btn" data-car="/models/kenney-police.glb">🚓 Police</button>
          <button class="car-btn" data-car="/models/kenney-hatchback-sports.glb">🚗 Hatchback</button>
        </div>
      </section>

      <!-- Race Lobby Panel (hidden until race lobby active) -->
      <section class="card" id="lobbyCard" style="display:none">
        <h3>🏁 Race Lobby</h3>
        <div id="lobbyInfo"></div>
        <div id="lobbyPlayers" class="lobby-players"></div>
        <div class="btn-row" id="lobbyActions">
          <button id="readyBtn">Ready Up</button>
          <button class="secondary" id="startRaceBtn" disabled>Start Race</button>
        </div>
        <button class="secondary" id="leaveLobbyBtn" style="width:100%;margin-top:8px">Leave Lobby</button>
      </section>

      <!-- Race HUD (hidden until race active) -->
      <section class="card" id="raceHud" style="display:none">
        <h3>🏎️ Race</h3>
        <div class="race-timer" id="raceTimer">00:00.0</div>
        <div class="race-speed" id="raceSpeed">0 km/h</div>
        <div class="cp-bar"><div class="cp-fill" id="cpBar" style="width:0%"></div></div>
        <p class="status" id="cpText">Checkpoints: 0/5</p>
        <p class="status" style="font-size:11px;color:#636e72">↑↓ throttle · ←→ steer · Space brake</p>
        <button class="secondary" id="finishBtn" style="width:100%;margin-top:8px">Cross Finish Line</button>
      </section>

      <!-- Race Results (hidden until race over) -->
      <section class="card" id="resultsCard" style="display:none">
        <h3>🏆 Results</h3>
        <div id="resultsList"></div>
        <button id="backToRoomBtn" style="width:100%;margin-top:8px">Back to Room</button>
      </section>

      <!-- Signal Challenge -->
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
        <h3>Race Lobby</h3>
        <label>Lobby Name</label>
        <input id="lobbyName" value="Cleveland Sprint" />
        <button id="createLobbyBtn" style="width:100%;margin-top:8px">Create Race Lobby</button>
      </section>

      <section class="card">
        <h3>Mode Spine</h3>
        <p class="status">Cruise → signal → lobby → race/chase/challenge → score → share.</p>
      </section>
    </aside>

    <section class="map-wrap">
      <div id="map"></div>
      <!-- Countdown Overlay -->
      <div class="countdown-overlay" id="countdownOverlay" style="display:none">
        <div class="countdown-number" id="countdownNumber">5</div>
      </div>
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
const markImg = document.querySelector('.brand-mark');
if (markImg)
    markImg.onerror = () => markImg.style.display = 'none';
// ── Event Bindings ──────────────────────────────────────
document.querySelector('#connectBtn').addEventListener('click', connect);
document.querySelector('#moveBtn').addEventListener('click', () => sendPosition(true));
document.querySelector('#spawnCarBtn').addEventListener('click', () => {
    console.log('[raceGPS] spawn car clicked');
    map.upsertPlayerMarker('debug-car', { lat, lon }, 'Debug Car', heading);
    debug('Car spawned — check if visible');
});
document.querySelector('#autoDriveBtn').addEventListener('click', () => {
    console.log('[raceGPS] auto drive clicked');
    keys['ArrowUp'] = true;
    keys['ArrowRight'] = true;
    setTimeout(() => { keys['ArrowUp'] = false; keys['ArrowRight'] = false; }, 3000);
    debug('Auto-driving for 3s...');
});
// Car picker
document.querySelectorAll('.car-btn').forEach(btn => {
    btn.addEventListener('click', () => {
        document.querySelectorAll('.car-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        const carUrl = btn.dataset.car;
        console.log('[raceGPS] switching car to:', carUrl);
        map.switchCarModel(carUrl);
    });
});
document.querySelector('#chatForm').addEventListener('submit', (e) => { e.preventDefault(); sendChat(); });
document.querySelectorAll('[data-signal]').forEach(btn => btn.addEventListener('click', () => sendSignal(btn.dataset.signal)));
// Race lobby
document.querySelector('#createLobbyBtn').addEventListener('click', createLobby);
document.querySelector('#readyBtn').addEventListener('click', toggleReady);
document.querySelector('#startRaceBtn').addEventListener('click', startRace);
document.querySelector('#leaveLobbyBtn').addEventListener('click', leaveLobby);
document.querySelector('#finishBtn').addEventListener('click', finishRace);
document.querySelector('#backToRoomBtn').addEventListener('click', backToRoom);
// ── Keyboard Controls ────────────────────────────────────
addEventListener('keydown', e => { keys[e.key] = true; e.preventDefault(); });
addEventListener('keyup', e => { keys[e.key] = false; e.preventDefault(); });
// ── Connection ──────────────────────────────────────────
async function connect() {
    console.log('[raceGPS] connect clicked');
    displayName = (document.querySelector('#displayName').value || 'Driver').trim();
    roomId = (document.querySelector('#roomId').value || 'global-cruise').trim();
    const mode = document.querySelector('#mode').value;
    const session = await fetch(`${API}/api/session`, {
        method: 'POST', credentials: 'include', headers: { 'content-type': 'application/json' }, body: JSON.stringify({ displayName })
    }).then(r => r.json());
    playerId = session.playerId;
    console.log('[raceGPS] session created, playerId:', playerId);
    // Initialize arcade car
    if (!arcadeReady) {
        console.log('[raceGPS] initializing arcade car...');
        const originLat = cityPackData?.center.lat ?? lat;
        const originLon = cityPackData?.center.lon ?? lon;
        arcadeOriginLat = originLat;
        arcadeOriginLon = originLon;
        arcadeReady = true;
        // Snap car to city center facing north
        lat = originLat;
        lon = originLon;
        arcadeCar.reset(lat, lon, heading);
        console.log('[raceGPS] Arcade car ready, origin:', originLat, originLon);
    }
    else {
        arcadeCar.reset(lat, lon, heading);
    }
    ws?.close();
    ws = new WebSocket(`ws://localhost:8787/ws/rooms/${roomId}`);
    ws.onopen = () => {
        console.log('[raceGPS] websocket open');
        debug('Connected — press ↑ to drive');
        status(`Connected as <span class="neon">${displayName}</span> in ${roomId}.`);
        ws?.send(JSON.stringify({ type: 'join_room', roomId, displayName, mode }));
        sendPosition(false);
        resetRaceUI();
        startDriving();
        tryEnterStreetView();
    };
    ws.onmessage = ev => handleMessage(JSON.parse(ev.data));
    ws.onclose = () => {
        status('Disconnected.');
        stopDriving();
        debug('Disconnected');
    };
}
function resetRaceUI() {
    currentLobbyId = '';
    raceActive = false;
    cpIndex = 0;
    stopDriving();
    speed = 0;
    document.querySelector('#lobbyCard').style.display = 'none';
    document.querySelector('#raceHud').style.display = 'none';
    document.querySelector('#resultsCard').style.display = 'none';
    document.querySelector('#countdownOverlay').style.display = 'none';
}
// ── Race Lobby Actions ──────────────────────────────────
function createLobby() {
    if (!ws || ws.readyState !== WebSocket.OPEN)
        return;
    const name = (document.querySelector('#lobbyName').value || 'Sprint Race').trim();
    ws.send(JSON.stringify({ type: 'race_create_lobby', roomId, title: name, checkpointIds: [], laps: 1, maxPlayers: 8 }));
}
function toggleReady() {
    if (!ws || !currentLobbyId)
        return;
    ws.send(JSON.stringify({ type: 'race_toggle_ready', roomId, lobbyId: currentLobbyId }));
    // Optimistic UI: toggle button text
    const btn = document.querySelector('#readyBtn');
    btn.textContent = btn.textContent === 'Ready Up' ? 'Not Ready' : 'Ready Up';
}
function startRace() {
    if (!ws || !currentLobbyId)
        return;
    ws.send(JSON.stringify({ type: 'race_start_countdown', roomId, lobbyId: currentLobbyId }));
}
function leaveLobby() {
    if (!ws || !currentLobbyId)
        return;
    ws.send(JSON.stringify({ type: 'race_leave_lobby', roomId, lobbyId: currentLobbyId }));
    resetRaceUI();
}
function finishRace() {
    if (!ws || !currentLobbyId || !raceActive)
        return;
    const elapsed = Date.now() - raceStartMs;
    ws.send(JSON.stringify({ type: 'race_finished', roomId, lobbyId: currentLobbyId, elapsedMs: elapsed, ghost: [] }));
}
function backToRoom() {
    resetRaceUI();
}
// ── Message Handler ─────────────────────────────────────
function handleMessage(msg) {
    switch (msg.type) {
        case 'welcome':
            playerId = msg.playerId;
            break;
        case 'room_snapshot':
            chat(`[System] joined ${msg.room.title}. Players: ${msg.room.players.length}`);
            msg.room.players.forEach(p => { if (p.lat && p.lon)
                map.upsertPlayerMarker(p.playerId, { lat: p.lat, lon: p.lon }, p.displayName, p.heading ?? 0); });
            break;
        case 'player_joined':
            chat(`[System] ${msg.player.displayName} joined.`);
            break;
        case 'player_left':
            map.removePlayerMarker(msg.playerId);
            chat(`[System] player left.`);
            break;
        case 'player_position':
            map.upsertPlayerMarker(msg.playerId, { lat: msg.lat, lon: msg.lon }, msg.playerId === playerId ? displayName : msg.playerId, msg.heading);
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
        case 'game_event': {
            if (msg.event.kind === 'checkpoint_hit' && raceActive) {
                cpIndex++;
                updateCPBar();
            }
            break;
        }
        // ── Race Lobby Messages ─────────────────────────────
        case 'race_lobby_snapshot':
        case 'race_lobby_updated':
            updateLobbyUI(msg.lobby);
            break;
        case 'race_countdown':
            showCountdown(msg.secondsRemaining);
            break;
        case 'race_started':
            raceActive = true;
            raceStartMs = msg.raceStart;
            cpIndex = 0;
            // Render city road network if provided
            if (msg.citypack) {
                map.setCenter(msg.citypack.center, 15);
                map.drawRoads(msg.citypack.roads);
                if (msg.citypack.buildings) {
                    map.drawBuildings(msg.citypack.buildings);
                }
            }
            showRaceHUD();
            break;
        case 'race_player_finished':
            chat(`[Race] ${msg.result.displayName} finished in ${(msg.result.elapsedMs / 1000).toFixed(1)}s`);
            break;
        case 'race_results':
            showResults(msg.results, msg.winner);
            break;
        // ── Physics Messages ─────────────────────────────────
        case 'race_physics_update':
            map.upsertPlayerMarker(msg.playerId, msg.tick.position, msg.playerId === playerId ? displayName : msg.playerId, msg.tick.heading);
            // Track server crash state + speedometer for local player
            if (msg.playerId === playerId) {
                serverCrashed = msg.tick.isCrashed;
                lat = msg.tick.position.lat;
                lon = msg.tick.position.lon;
                heading = msg.tick.heading;
                speed = msg.tick.speed;
                if (arcadeReady) {
                    arcadeCar.reset(lat, lon, heading);
                }
                const kmh = Math.round(msg.tick.speed * 3.6);
                const speedEl = document.querySelector('#raceSpeed');
                if (speedEl)
                    speedEl.textContent = `${kmh} km/h`;
                if (msg.tick.isCrashed) {
                    status(`<span class="hot">💥 CRASHED — ${msg.tick.crashCause}</span>`);
                }
                else {
                    // Street-level chase camera
                    map.syncStreetCamera(lat, lon, heading, speed);
                }
            }
            break;
        case 'race_crash_event':
            if (msg.cause !== 'recovered') {
                chat(`<span class="hot">[Crash]</span> ${msg.displayName} crashed: ${msg.cause}`);
            }
            else {
                chat(`[Race] ${msg.displayName} recovered from crash`);
                if (msg.playerId === playerId)
                    serverCrashed = false;
            }
            break;
    }
}
// ── Lobby UI ────────────────────────────────────────────
function updateLobbyUI(lobby) {
    currentLobbyId = lobby.lobbyId;
    document.querySelector('#lobbyCard').style.display = 'block';
    const info = document.querySelector('#lobbyInfo');
    info.innerHTML = `<p><strong>${escapeHtml(lobby.title)}</strong> — ${lobby.state === 'lobby' ? 'Waiting for players' : lobby.state === 'countdown' ? 'Starting...' : lobby.state === 'racing' ? 'Racing!' : 'Finished'}</p>`;
    const playersEl = document.querySelector('#lobbyPlayers');
    playersEl.innerHTML = lobby.players.map(p => `<div class="lobby-player ${p.ready ? 'ready' : ''}">
      <span class="player-name">${escapeHtml(p.displayName)}</span>
      <span class="player-ready">${p.ready ? '✅' : '⏳'}</span>
    </div>`).join('');
    // Enable start button if all ready (host check — first player)
    const allReady = lobby.players.length > 0 && lobby.players.every(p => p.ready);
    const startBtn = document.querySelector('#startRaceBtn');
    startBtn.disabled = !allReady || lobby.state !== 'lobby';
}
// ── Countdown Overlay ───────────────────────────────────
function showCountdown(seconds) {
    const overlay = document.querySelector('#countdownOverlay');
    const num = document.querySelector('#countdownNumber');
    overlay.style.display = 'flex';
    if (seconds === 0) {
        num.textContent = 'GO!';
        num.className = 'countdown-number go';
        setTimeout(() => { overlay.style.display = 'none'; }, 800);
    }
    else {
        num.textContent = String(seconds);
        num.className = 'countdown-number';
    }
}
// ── Race HUD ────────────────────────────────────────────
function showRaceHUD() {
    document.querySelector('#lobbyCard').style.display = 'none';
    document.querySelector('#raceHud').style.display = 'block';
    document.querySelector('#resultsCard').style.display = 'none';
    serverCrashed = false;
    updateCPBar();
    startRaceTimer();
    startDriving();
}
function updateCPBar() {
    const pct = Math.min(100, (cpIndex / totalCPs) * 100);
    document.querySelector('#cpBar').style.width = `${pct}%`;
    document.querySelector('#cpText').textContent = `Checkpoints: ${cpIndex}/${totalCPs}`;
}
let raceTimerInterval;
function startRaceTimer() {
    if (raceTimerInterval)
        clearInterval(raceTimerInterval);
    raceTimerInterval = setInterval(() => {
        if (!raceActive) {
            clearInterval(raceTimerInterval);
            return;
        }
        const elapsed = Date.now() - raceStartMs;
        const totalSec = (elapsed / 1000).toFixed(1);
        document.querySelector('#raceTimer').textContent = `${totalSec}s`;
    }, 100);
}
// ── Results ─────────────────────────────────────────────
function showResults(results, winner) {
    raceActive = false;
    if (raceTimerInterval)
        clearInterval(raceTimerInterval);
    stopDriving();
    speed = 0;
    document.querySelector('#raceHud').style.display = 'none';
    document.querySelector('#lobbyCard').style.display = 'none';
    document.querySelector('#resultsCard').style.display = 'block';
    const list = document.querySelector('#resultsList');
    list.innerHTML = `
    <div class="winner-banner">🏆 ${escapeHtml(winner.displayName)} — ${(winner.elapsedMs / 1000).toFixed(1)}s</div>
    ${results.map((r, i) => `
      <div class="result-row ${r.playerId === playerId ? 'me' : ''}">
        <span class="result-pos">${i + 1}.</span>
        <span class="result-name">${escapeHtml(r.displayName)}</span>
        <span class="result-time">${(r.elapsedMs / 1000).toFixed(1)}s</span>
      </div>
    `).join('')}
  `;
}
// ── Driving Physics (Arcade Kinematic) ─────────────────────────
function startDriving() {
    if (driveInterval)
        clearInterval(driveInterval);
    driveInterval = setInterval(driveTick, 50); // 20 Hz local simulation
}
function stopDriving() {
    if (driveInterval) {
        clearInterval(driveInterval);
        driveInterval = undefined;
    }
}
function tryEnterStreetView() {
    if (streetViewEntered)
        return;
    if (!cityPackData || !cityPackData.roads)
        return;
    if (!ws || ws.readyState !== WebSocket.OPEN)
        return;
    streetViewEntered = true;
    // Use same origin so car and renderer share the same coordinate system
    map.enterStreetView(cityPackData.roads, cityPackData.buildings || [], arcadeOriginLat, arcadeOriginLon);
    console.log('[raceGPS] Street view entered');
}
function driveTick() {
    if (serverCrashed || !arcadeReady) {
        if (!arcadeReady && Math.random() < 0.01)
            console.log('[raceGPS] driveTick skipped: arcade not ready');
        return;
    }
    const dt = 0.05; // 50ms tick
    const throttle = (keys['ArrowUp'] || keys['w'] || keys['W']) ? 1 : (keys['ArrowDown'] || keys['s'] || keys['S']) ? -0.5 : 0;
    const steer = (keys['ArrowLeft'] || keys['a'] || keys['A']) ? -1 : (keys['ArrowRight'] || keys['d'] || keys['D']) ? 1 : 0;
    const brake = keys[' '] || keys['Spacebar'];
    const state = arcadeCar.update({ throttle, steer, brake }, dt);
    if (!state)
        return;
    lat = state.lat;
    lon = state.lon;
    heading = state.heading;
    speed = state.speed;
    // Update street-level view (arcade driving)
    map.updateStreetView(state, speed);
    // Update minimap marker
    map.upsertPlayerMarker(playerId, { lat, lon }, displayName, heading);
    seq++;
    if (ws && ws.readyState === WebSocket.OPEN) {
        // Only broadcast position in cruise/explore; races use server physics
        if (!raceActive) {
            ws.send(JSON.stringify({ type: 'player_position', roomId, lat, lon, heading, speed, seq }));
        }
        // Auto-hit checkpoint if in race and near one
        if (raceActive && currentLobbyId && cpIndex < totalCPs) {
            if (seq % 10 === 0) { // throttle checkpoint checks
                ws.send(JSON.stringify({ type: 'race_checkpoint_hit', roomId, lobbyId: currentLobbyId, checkpointId: `cp_${cpIndex}`, seq }));
            }
        }
    }
    // Update speedometer
    const kmh = Math.round(Math.abs(speed) * 3.6);
    const speedEl = document.querySelector('#raceSpeed');
    if (speedEl)
        speedEl.textContent = `${kmh} km/h`;
    // Update compass
    const compass = document.querySelector('#compass');
    if (compass) {
        const arrow = compass.querySelector('.compass-arrow');
        if (arrow)
            arrow.style.transform = `rotate(${heading}deg)`;
        const label = compass.querySelector('.compass-label');
        if (label) {
            const dirs = ['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW'];
            const idx = Math.round(heading / 45) % 8;
            label.textContent = dirs[idx];
        }
    }
    // Gear indicator
    const gearEl = document.querySelector('#gearIndicator');
    if (gearEl) {
        if (throttle < 0)
            gearEl.textContent = 'R';
        else if (brake)
            gearEl.textContent = 'B';
        else if (speed < 1)
            gearEl.textContent = 'P';
        else
            gearEl.textContent = 'D';
    }
}
async function sendPosition(randomize) {
    if (!ws || ws.readyState !== WebSocket.OPEN)
        return;
    if (randomize) {
        lat += (Math.random() - .5) * .01;
        lon += (Math.random() - .5) * .01;
    }
    map.upsertPlayerMarker(playerId || 'me', { lat, lon }, displayName || 'ME', heading);
    seq++;
    ws.send(JSON.stringify({ type: 'player_position', roomId, lat, lon, heading, speed, seq }));
    if (arcadeReady) {
        arcadeCar.reset(lat, lon, heading);
    }
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
// ── Utilities ───────────────────────────────────────────
function chat(html) {
    const log = document.querySelector('#chatLog');
    const line = document.createElement('div');
    line.className = 'chat-line';
    line.innerHTML = html;
    log.appendChild(line);
    log.scrollTop = log.scrollHeight;
}
function status(html) { document.querySelector('#status').innerHTML = html; }
function escapeHtml(s) { return s.replace(/[&<>\"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '\"': '&quot;' }[c])); }
function debug(msg) {
    console.log('[DEBUG]', msg);
    const el = document.querySelector('#debugPanel');
    if (el)
        el.textContent = msg;
}
