import http from 'node:http';
import express from 'express';
import cors from 'cors';
import cookie from 'cookie';
import { nanoid } from 'nanoid';
import { WebSocketServer, WebSocket } from 'ws';
import type { ClientMessage, RaceGPSMode, RoomPlayer, RoomSnapshot, ServerMessage } from '@racegps/protocol';
import { parseClientMessage } from '@racegps/protocol';

const PORT = Number(process.env.RACEGPS_PORT || 8787);
const WEB_ORIGIN = process.env.RACEGPS_WEB_ORIGIN || 'http://localhost:5173';

interface Session { playerId: string; displayName: string }
interface SocketState extends Session { roomId?: string }
interface Room {
  roomId: string;
  title: string;
  mode: RaceGPSMode;
  createdAt: string;
  sockets: Map<WebSocket, SocketState>;
  players: Map<string, RoomPlayer>;
}

const sessions = new Map<string, Session>();
const rooms = new Map<string, Room>();

const app = express();
app.use(express.json());
app.use(cors({ origin: WEB_ORIGIN, credentials: true }));

app.get('/health', (_req, res) => res.json({ ok: true, service: 'racegps-backend' }));

app.post('/api/session', (req, res) => {
  const sid = nanoid();
  const displayName = String(req.body?.displayName || `Driver-${sid.slice(0, 4)}`).slice(0, 32);
  const session = { playerId: `p_${nanoid(10)}`, displayName };
  sessions.set(sid, session);
  res.cookie('racegps_sid', sid, {
    httpOnly: true,
    sameSite: 'lax',
    secure: false,
    maxAge: 1000 * 60 * 60 * 24 * 30
  });
  res.json(session);
});

app.get('/api/me', (req, res) => {
  const sid = getSid(req.headers.cookie);
  const session = sid ? sessions.get(sid) : undefined;
  if (!session) return res.status(401).json({ error: 'not_authenticated' });
  return res.json(session);
});

app.get('/api/rooms', (_req, res) => {
  res.json([...rooms.values()].map(roomToSnapshot));
});

app.post('/api/rooms', (req, res) => {
  const title = String(req.body?.title || 'Cruise Room').slice(0, 80);
  const mode = sanitizeMode(req.body?.mode);
  const room = createRoom(title, mode);
  res.json(roomToSnapshot(room));
});

const server = http.createServer(app);
const wss = new WebSocketServer({ noServer: true });

server.on('upgrade', (req, socket, head) => {
  if (!req.url?.startsWith('/ws/rooms/')) {
    socket.destroy();
    return;
  }

  const sid = getSid(req.headers.cookie);
  const session = sid ? sessions.get(sid) : undefined;
  if (!session) {
    socket.write('HTTP/1.1 401 Unauthorized\r\n\r\n');
    socket.destroy();
    return;
  }

  wss.handleUpgrade(req, socket, head, ws => {
    (req as http.IncomingMessage & { racegpsSession?: Session }).racegpsSession = session;
    wss.emit('connection', ws, req);
  });
});

wss.on('connection', (ws: WebSocket, req: http.IncomingMessage) => {
  const session = (req as http.IncomingMessage & { racegpsSession?: Session }).racegpsSession;
  if (!session) {
    ws.close(1008, 'Missing session');
    return;
  }
  const state: SocketState = { ...session };
  send(ws, { type: 'welcome', ...session });

  const roomId = req.url?.split('/').pop() || 'global-cruise';
  joinRoom(ws, state, roomId, 'Cruise Room', 'cruise');

  ws.on('message', raw => {
    const msg = parseClientMessage(raw.toString());
    if (!msg) return send(ws, { type: 'system_message', message: 'Invalid message.', level: 'error' });
    handleClientMessage(ws, state, msg);
  });

  ws.on('close', () => leaveCurrentRoom(ws, state));
});

function handleClientMessage(ws: WebSocket, state: SocketState, msg: ClientMessage): void {
  switch (msg.type) {
    case 'join_room':
      joinRoom(ws, state, msg.roomId, msg.roomId, msg.mode || 'cruise');
      break;
    case 'leave_room':
      leaveCurrentRoom(ws, state);
      break;
    case 'player_position': {
      const room = state.roomId ? rooms.get(state.roomId) : undefined;
      if (!room) return;
      const player = room.players.get(state.playerId);
      if (player) {
        player.lat = msg.lat; player.lon = msg.lon; player.heading = msg.heading; player.speed = msg.speed;
      }
      broadcast(room, { type: 'player_position', playerId: state.playerId, lat: msg.lat, lon: msg.lon, heading: msg.heading, speed: msg.speed, seq: msg.seq }, ws);
      break;
    }
    case 'chat_message': {
      const room = state.roomId ? rooms.get(state.roomId) : undefined;
      if (!room) return;
      const clean = msg.message.replace(/\s+/g, ' ').trim().slice(0, 240);
      if (!clean) return;
      broadcast(room, { type: 'chat_message', playerId: state.playerId, displayName: state.displayName, message: clean, sentAt: new Date().toISOString() });
      break;
    }
    case 'challenge_signal': {
      const room = state.roomId ? rooms.get(state.roomId) : undefined;
      if (!room) return;
      broadcast(room, { type: 'challenge_signal', fromPlayerId: state.playerId, toPlayerId: msg.toPlayerId, signal: msg.signal, challengeType: msg.challengeType });
      break;
    }
    case 'game_event': {
      const room = state.roomId ? rooms.get(state.roomId) : undefined;
      if (!room) return;
      broadcast(room, { type: 'game_event', playerId: state.playerId, event: msg.event });
      break;
    }
  }
}

function joinRoom(ws: WebSocket, state: SocketState, roomId: string, title: string, mode: RaceGPSMode): void {
  leaveCurrentRoom(ws, state);
  const room = rooms.get(roomId) || createRoom(title, mode, roomId);
  room.sockets.set(ws, state);
  state.roomId = room.roomId;
  const player: RoomPlayer = { playerId: state.playerId, displayName: state.displayName, role: mode === 'hot_pursuit' ? 'runner' : 'driver', mode };
  room.players.set(state.playerId, player);
  send(ws, { type: 'room_snapshot', room: roomToSnapshot(room) });
  broadcast(room, { type: 'player_joined', player }, ws);
  broadcast(room, { type: 'system_message', message: `${state.displayName} joined ${room.title}.` });
}

function leaveCurrentRoom(ws: WebSocket, state: SocketState): void {
  if (!state.roomId) return;
  const room = rooms.get(state.roomId);
  if (!room) return;
  room.sockets.delete(ws);
  room.players.delete(state.playerId);
  broadcast(room, { type: 'player_left', playerId: state.playerId });
  if (room.sockets.size === 0 && room.roomId !== 'global-cruise') rooms.delete(room.roomId);
  state.roomId = undefined;
}

function createRoom(title: string, mode: RaceGPSMode, roomId = slugRoom(title)): Room {
  const room: Room = { roomId, title, mode, createdAt: new Date().toISOString(), sockets: new Map(), players: new Map() };
  rooms.set(roomId, room);
  return room;
}

function roomToSnapshot(room: Room): RoomSnapshot {
  return { roomId: room.roomId, title: room.title, mode: room.mode, createdAt: room.createdAt, players: [...room.players.values()] };
}

function send(ws: WebSocket, msg: ServerMessage): void {
  if (ws.readyState === WebSocket.OPEN) ws.send(JSON.stringify(msg));
}

function broadcast(room: Room, msg: ServerMessage, except?: WebSocket): void {
  for (const ws of room.sockets.keys()) if (ws !== except) send(ws, msg);
}

function getSid(header?: string): string | undefined {
  return header ? cookie.parse(header).racegps_sid : undefined;
}

function slugRoom(title: string): string {
  return `${title.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '')}-${nanoid(5)}`;
}

function sanitizeMode(value: unknown): RaceGPSMode {
  return ['cruise','race','challenge','hot_pursuit','explore'].includes(String(value)) ? value as RaceGPSMode : 'cruise';
}

server.listen(PORT, () => console.log(`raceGPS backend running on http://localhost:${PORT}`));
