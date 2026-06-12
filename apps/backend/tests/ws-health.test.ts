import { describe, it, before, after } from 'node:test';
import assert from 'node:assert/strict';
import http from 'node:http';
import { spawn, type ChildProcess } from 'node:child_process';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';

const __dirname = dirname(fileURLToPath(import.meta.url));
const backendRoot = join(__dirname, '..');
const TEST_PORT = 18787;

let child: ChildProcess | null = null;

function waitForHealth(port: number, timeoutMs = 15000): Promise<void> {
  const start = Date.now();
  return new Promise((resolve, reject) => {
    const tick = () => {
      const req = http.get(`http://127.0.0.1:${port}/health`, (res) => {
        res.resume();
        if (res.statusCode === 200) resolve();
        else if (Date.now() - start > timeoutMs) reject(new Error(`health status ${res.statusCode}`));
        else setTimeout(tick, 200);
      });
      req.on('error', () => {
        if (Date.now() - start > timeoutMs) reject(new Error('health timeout'));
        else setTimeout(tick, 200);
      });
    };
    tick();
  });
}

describe('racegps backend ws stack', () => {
  before(async () => {
    child = spawn('npx', ['tsx', 'src/index.ts'], {
      cwd: backendRoot,
      env: { ...process.env, RACEGPS_PORT: String(TEST_PORT) },
      stdio: 'pipe',
      shell: true,
    });
    await waitForHealth(TEST_PORT);
  });

  after(() => {
    child?.kill('SIGTERM');
    child = null;
  });

  it('GET /health returns ok', async () => {
    const res = await fetch(`http://127.0.0.1:${TEST_PORT}/health`);
    assert.equal(res.status, 200);
    const body = await res.json() as { ok?: boolean; service?: string };
    assert.equal(body.ok, true);
    assert.equal(body.service, 'racegps-backend');
  });

  it('GET /api/rooms returns array', async () => {
    const res = await fetch(`http://127.0.0.1:${TEST_PORT}/api/rooms`);
    assert.equal(res.status, 200);
    const body = await res.json() as unknown[];
    assert.ok(Array.isArray(body));
  });
});