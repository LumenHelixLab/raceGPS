export type RaceGPSMode = 'cruise' | 'race' | 'challenge' | 'hot_pursuit' | 'explore';
export type PlayerRole = 'driver' | 'cop' | 'runner' | 'ghost';

export type ClientMessage =
  | { type: 'join_room'; roomId: string; displayName: string; mode?: RaceGPSMode }
  | { type: 'leave_room'; roomId: string }
  | { type: 'player_position'; roomId: string; lat: number; lon: number; heading: number; speed: number; seq: number }
  | { type: 'chat_message'; roomId: string; message: string }
  | { type: 'challenge_signal'; roomId: string; toPlayerId?: string; signal: ChallengeSignal; challengeType: ChallengeType }
  | { type: 'game_event'; roomId: string; event: GameEvent };

export type ServerMessage =
  | { type: 'welcome'; playerId: string; displayName: string }
  | { type: 'room_snapshot'; room: RoomSnapshot }
  | { type: 'player_joined'; player: RoomPlayer }
  | { type: 'player_left'; playerId: string }
  | { type: 'player_position'; playerId: string; lat: number; lon: number; heading: number; speed: number; seq: number }
  | { type: 'chat_message'; playerId: string; displayName: string; message: string; sentAt: string }
  | { type: 'challenge_signal'; fromPlayerId: string; toPlayerId?: string; signal: ChallengeSignal; challengeType: ChallengeType }
  | { type: 'system_message'; message: string; level?: 'info' | 'warning' | 'error' }
  | { type: 'game_event'; playerId: string; event: GameEvent };

export type ChallengeSignal = 'flash_lights' | 'rev_engine' | 'drop_pin' | 'hot_signal' | 'ghost_signal';
export type ChallengeType = 'quick_sprint' | 'drag_race' | 'route_race' | 'hot_pursuit' | 'ghost_race';

export type GameEvent =
  | { kind: 'checkpoint_hit'; checkpointId: string; timestamp: number }
  | { kind: 'object_pickup'; objectId: string; timestamp: number }
  | { kind: 'pursuit_tag'; targetPlayerId: string; distanceMeters: number; timestamp: number }
  | { kind: 'race_start'; startsAt: number }
  | { kind: 'race_finish'; elapsedMs: number };

export interface RoomPlayer {
  playerId: string;
  displayName: string;
  role: PlayerRole;
  mode: RaceGPSMode;
  lat?: number;
  lon?: number;
  heading?: number;
  speed?: number;
}

export interface RoomSnapshot {
  roomId: string;
  mode: RaceGPSMode;
  title: string;
  players: RoomPlayer[];
  createdAt: string;
}

export function isObject(value: unknown): value is Record<string, unknown> {
  return typeof value === 'object' && value !== null;
}

export function parseClientMessage(raw: string): ClientMessage | null {
  try {
    const value = JSON.parse(raw);
    if (!isObject(value) || typeof value.type !== 'string') return null;
    return value as ClientMessage;
  } catch {
    return null;
  }
}
