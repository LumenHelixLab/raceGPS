import { describe, it } from 'node:test';
import assert from 'node:assert/strict';
import { slugRoom, sanitizeMode } from '../src/room-utils.ts';

describe('room-utils', () => {
  it('slugRoom normalizes title and adds suffix', () => {
    const id = slugRoom('Akron Cruise Room');
    assert.match(id, /^akron-cruise-room-[A-Za-z0-9_-]{5}$/);
  });

  it('sanitizeMode accepts known modes', () => {
    assert.equal(sanitizeMode('race'), 'race');
    assert.equal(sanitizeMode('hot_pursuit'), 'hot_pursuit');
  });

  it('sanitizeMode falls back to cruise', () => {
    assert.equal(sanitizeMode('invalid'), 'cruise');
    assert.equal(sanitizeMode(null), 'cruise');
  });
});