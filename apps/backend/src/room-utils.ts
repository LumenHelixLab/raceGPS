import { nanoid } from 'nanoid';
import type { RaceGPSMode } from '@racegps/protocol';

const MODES: RaceGPSMode[] = ['cruise', 'race', 'challenge', 'hot_pursuit', 'explore'];

export function slugRoom(title: string): string {
  return `${title.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '')}-${nanoid(5)}`;
}

export function sanitizeMode(value: unknown): RaceGPSMode {
  return MODES.includes(String(value) as RaceGPSMode) ? (value as RaceGPSMode) : 'cruise';
}