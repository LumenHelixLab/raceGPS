# Easy Test Beta Desktop Launcher Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ship an Electron+Vite desktop launcher (first-run wizard, Package/Dev launch, shared settings) plus auth-less Workshop local routes wired to existing Akron/rgpack CLIs, and freeze-safe Race HUD/settings implementation notes citing Akron widget patterns — one milestone, no cook spam.

**Architecture:** One npm workspace app `apps/racegps-launcher` (Electron main + Vite/React renderer) owns onboarding, path validation, Package vs Dev launch stubs, and Workshop UI routes. Shared settings live in `packages/launcher-settings` (zod schema + JSON I/O) and persist to `%AppData%\raceGPS\settings.json`. Race stays Cleveland via `LaunchClevelandRace.bat` / documented package exe overrides only; Workshop shells out to `python -m rgpack` and `tools/akron-semantic-compiler` / `tools/universal-city-compiler`. Build & Engine documents the exact path contract. Race HUD/settings is code+docs first; runtime evidence only when Chris unlocks Dev launch.

**Tech Stack:** Node 22+/24 (monorepo engines), TypeScript 5.6+, Electron 33+, Vite 6+, React 19, react-router-dom 7, zod 3, Node.js built-in `node:test` + tsx, `@racegps/ui-kit` tokens; Python 3.11 via `.venv-grokbot` for Workshop CLI; Unreal 5.7 Cleveland race-base (Dev bat only until cook unlock).

**Spec:** `C:\Users\cgp22\Documents\raceGPS-handoff\2026-09-27-EASY-TEST-BETA-LAUNCHER-DESIGN.md` (mirror intent: Easy Test Beta Desktop Launcher Design, 2026-09-27)  
**Worktree:** `C:\projects\raceGPS-grokbot-cleveland` on `grokbot/cleveland-integration`  
**Uproject:** `apps/unreal-akron-beta/raceGPSAkronBeta.uproject`

## Global Constraints

- Worktree: C:\projects\raceGPS-grokbot-cleveland branch grokbot/cleveland-integration
- GlobalDefaultGameMode stays CruiseSprint; Cleveland via overrides only
- No full Akron Unreal shell merge; Akron compilers into Workshop only
- No unattended LaunchClevelandRace / Gate 1 spam; NullRHI ≠ PASS
- No master merge / robocopy / reconcile promotion
- Package mode may be "awaiting build" until Chris unlocks cook
- Research modern OSS with dates before each lane implements
- Research & Training bot creation is OUT OF SCOPE for code tasks (Prototyper creates after Chris asks) — but include a Task 0 ops note for Unreal PM research-when-idle folder docs/evidence/grokbot/research/

### Additional inventory locks (2026-09-28 spot-check)

- Dev Race entry already exists at `apps/unreal-akron-beta/LaunchClevelandRace.bat` (not repo root).
- `cityhub/` is Express API only (no frontend). `packages/ui-kit` is CSS tokens only. No existing Electron app under `apps/`.
- Put launcher+Workshop web UI in **`apps/racegps-launcher/`** (fits root `workspaces: ["apps/*","packages/*"]`). Do **not** invent a second web shell under `cityhub/` or `packages/ui-kit/`.
- `Content/UI/**` are Blueprint `.txt` stubs only. Live C++ patterns: `apps/unreal-akron-beta/Source/raceGPSAkronBeta/Public/{MainMenuWidget,SettingsWidget,OnboardingManager,PauseMenuWidget,VisualQualitySettings}.h`.
- `raceGPSWorkshop` / `WorkshopAppSubsystem` = boot scaffolding only; Workshop MVP UI is the Electron local routes, not a full Unreal Workshop shell merge.
- G4 / Shipping package archive is empty on this tip — Package mode UI must say **awaiting build**.

---

## File map

| Path | Role |
|------|------|
| `docs/evidence/grokbot/research/README.md` | Unreal PM research-when-idle index |
| `docs/evidence/grokbot/research/TEMPLATE-idle-brief.md` | Idle-research brief template |
| `docs/evidence/grokbot/research/OUT-OF-SCOPE-research-training-bot.md` | Ops note: R&T bot not created by this plan |
| `packages/launcher-settings/package.json` | `@racegps/launcher-settings` workspace package |
| `packages/launcher-settings/tsconfig.json` | Strict TS for schema package |
| `packages/launcher-settings/src/schema.ts` | zod schema + inferred types |
| `packages/launcher-settings/src/defaults.ts` | Default settings values |
| `packages/launcher-settings/src/paths.ts` | Resolve `%AppData%\raceGPS\settings.json` |
| `packages/launcher-settings/src/io.ts` | load / save / validate / reset |
| `packages/launcher-settings/src/index.ts` | Package exports |
| `packages/launcher-settings/tests/settings.test.ts` | Unit tests (node:test + tsx) |
| `apps/racegps-launcher/package.json` | Electron+Vite+React app scripts |
| `apps/racegps-launcher/electron.vite.config.ts` | Main/preload/renderer Vite config |
| `apps/racegps-launcher/tsconfig.json` | App TS config |
| `apps/racegps-launcher/tsconfig.node.json` | Node-side TS config |
| `apps/racegps-launcher/electron/main.ts` | Electron main: windows, IPC, spawn |
| `apps/racegps-launcher/electron/preload.ts` | contextBridge API |
| `apps/racegps-launcher/src/main.tsx` | React entry |
| `apps/racegps-launcher/src/App.tsx` | Router: wizard / home / settings / workshop/* |
| `apps/racegps-launcher/src/styles.css` | Imports `@racegps/ui-kit` tokens + layout |
| `apps/racegps-launcher/src/pages/WizardPage.tsx` | First-run wizard |
| `apps/racegps-launcher/src/pages/HomePage.tsx` | Play Race / Open Workshop / status chips |
| `apps/racegps-launcher/src/pages/SettingsPage.tsx` | Mode, paths, reveal logs, reset |
| `apps/racegps-launcher/src/lib/pathValidation.ts` | Validate Package exe / Dev bat / Workshop python |
| `apps/racegps-launcher/src/lib/launch.ts` | IPC client wrappers for launch |
| `apps/racegps-launcher/src/workshop/LandingPage.tsx` | Workshop landing |
| `apps/racegps-launcher/src/workshop/PackPage.tsx` | Create/open pack dir |
| `apps/racegps-launcher/src/workshop/CompilePage.tsx` | Overpass/semantic compile UI |
| `apps/racegps-launcher/src/workshop/ValidatePage.tsx` | `python -m rgpack validate` |
| `apps/racegps-launcher/src/workshop/ExportPage.tsx` | Export / reveal `.rgpack` dir |
| `apps/racegps-launcher/src/workshop/runCli.ts` | Spawn helpers + log capture |
| `apps/racegps-launcher/index.html` | Renderer HTML shell |
| `docs/contracts/LAUNCHER_PATH_CONTRACT.md` | Exact Package vs Dev paths |
| `docs/evidence/grokbot/easy-test-beta/README.md` | Evidence index for milestone |
| `docs/evidence/grokbot/easy-test-beta/EVIDENCE-TEMPLATE.md` | Screenshot/log note template |
| `docs/evidence/grokbot/easy-test-beta/FAIL-CLOSED-CHECKLIST.md` | Unreal PM grade sheet |
| `docs/evidence/grokbot/easy-test-beta/RACE-HUD-SETTINGS-PLAN.md` | Freeze-safe Race HUD/settings notes |
| `apps/unreal-akron-beta/Source/raceGPSAkronBeta/...` | Later Race Systems edits (Task 8 notes only until unlock) |

**Out of scope (later / other owners):** Research & Training agent creation; StreetMap + Landscape Combinator tourism Cleveland; Race `.rgpack` consumption; Mode B stills; cook / UAT package; master merge; Gate 1 unattended launches.

---

### Task 0: Ops — research folder + Unreal PM idle-research template (docs only)

**Files:**
- Create: `docs/evidence/grokbot/research/README.md`
- Create: `docs/evidence/grokbot/research/TEMPLATE-idle-brief.md`
- Create: `docs/evidence/grokbot/research/OUT-OF-SCOPE-research-training-bot.md`

**Interfaces:**
- Consumes: design § "Research & training ops (Chris 2026-09-27)"
- Produces: folder Unreal PM drops cite-and-path briefs into while idle; explicit note that **Research & Training bot creation is OUT OF SCOPE** for this plan (Prototyper creates after Chris asks)

- [ ] **Step 1: Create research index**

Write `docs/evidence/grokbot/research/README.md`:

```markdown
# Unreal PM — research-when-idle

**Worktree:** `C:\projects\raceGPS-grokbot-cleveland` (`grokbot/cleveland-integration`)  
**Purpose:** Short researched briefs (launcher frameworks, Workshop UX, Race HUD/CommonUI, packaging) with links, dates, and a recommend/reject line.

## Rules

1. Research modern open-source **before** each lane implements (cite sources with dates).
2. Prefer finished OSS patterns over inventing scaffolding.
3. Do **not** own Gate 1 launches, cook spam, or goal-lock overrides from this folder.
4. **Research & Training bot** is created by Prototyper only after Chris asks — see `OUT-OF-SCOPE-research-training-bot.md`.

## Brief naming

`YYYY-MM-DD-<topic>.md` using `TEMPLATE-idle-brief.md`.
```

- [ ] **Step 2: Write idle-brief template**

Write `docs/evidence/grokbot/research/TEMPLATE-idle-brief.md`:

```markdown
# Research brief: <TOPIC>

**Date:** YYYY-MM-DD (America/New_York)  
**Author:** Unreal PM (idle research)  
**Lane impacted:** Launcher | Workshop | Race HUD | Build & Engine | Other

## Question

One paragraph: what decision does this brief unblock?

## Sources (with dates)

| Source | URL | Accessed | Notes |
|--------|-----|----------|-------|
| example | https://… | YYYY-MM-DD | …

## Findings

- Bullet findings only; quote version numbers.

## Recommend / Reject

**Recommend:** …  
**Reject:** …  
**Why:** …
```

- [ ] **Step 3: Write OUT-OF-SCOPE bot note**

Write `docs/evidence/grokbot/research/OUT-OF-SCOPE-research-training-bot.md`:

```markdown
# OUT OF SCOPE — Research & Training bot creation

Per design 2026-09-27 and plan 2026-09-28: **do not create** the Research & Training agent, seat, or brief as part of easy-test-beta code tasks.

- Trigger remains: Unreal PM "managing stop" / board locked / idle after a gate, **or** Chris asks Prototyper.
- Prototyper creates the teammate after Chris asks.
- Until then, Unreal PM uses this `research/` folder for idle briefs.
- Bot must not own Gate 1 launches, cook spam, or goal-lock overrides.
```

- [ ] **Step 4: Verify files exist (no Unreal, no git required)**

Run:

```powershell
cd C:\projects\raceGPS-grokbot-cleveland
Get-Item docs\evidence\grokbot\research\README.md,
         docs\evidence\grokbot\research\TEMPLATE-idle-brief.md,
         docs\evidence\grokbot\research\OUT-OF-SCOPE-research-training-bot.md |
  Select-Object FullName, Length
```

Expected: three files, each Length > 200.

---

### Task 1: Shared settings schema (JSON + zod/TS) + unit tests

**Research gate (before implement):** skim Electron userData / game-launcher settings patterns (Electron `app.getPath('userData')` docs; cite access date in PR/commit note). Prefer `%AppData%\raceGPS\settings.json` as design locked.

**Files:**
- Create: `packages/launcher-settings/package.json`
- Create: `packages/launcher-settings/tsconfig.json`
- Create: `packages/launcher-settings/src/schema.ts`
- Create: `packages/launcher-settings/src/defaults.ts`
- Create: `packages/launcher-settings/src/paths.ts`
- Create: `packages/launcher-settings/src/io.ts`
- Create: `packages/launcher-settings/src/index.ts`
- Create: `packages/launcher-settings/tests/settings.test.ts`

**Interfaces:**
- Consumes: none
- Produces:
  - Type `RaceMode = "package" | "dev"`
  - Type `LauncherSettings` (zod-inferred)
  - `DEFAULT_SETTINGS: LauncherSettings`
  - `settingsFilePath(appDataRoot?: string): string` → `<appDataRoot>\raceGPS\settings.json`
  - `parseSettings(data: unknown): LauncherSettings` (throws `ZodError`)
  - `loadSettings(filePath: string): LauncherSettings` (missing file → defaults; corrupt → throws)
  - `saveSettings(filePath: string, settings: LauncherSettings): void`
  - `resetSettings(filePath: string): LauncherSettings`

**Exact JSON shape** written to `%AppData%\raceGPS\settings.json`:

```json
{
  "schemaVersion": 1,
  "raceMode": "package",
  "paths": {
    "worktreeRoot": "C:\\projects\\raceGPS-grokbot-cleveland",
    "devBat": "C:\\projects\\raceGPS-grokbot-cleveland\\apps\\unreal-akron-beta\\LaunchClevelandRace.bat",
    "packageExe": "C:\\projects\\raceGPS-grokbot-cleveland\\apps\\unreal-akron-beta\\PackagedBuilds\\Win64\\raceGPSRace.exe",
    "workshopPython": "C:\\projects\\raceGPS-grokbot-cleveland\\.venv-grokbot\\Scripts\\python.exe",
    "uproject": "C:\\projects\\raceGPS-grokbot-cleveland\\apps\\unreal-akron-beta\\raceGPSAkronBeta.uproject",
    "logDir": "C:\\projects\\raceGPS-grokbot-cleveland\\apps\\unreal-akron-beta\\Saved\\Logs"
  },
  "gpuNote": "",
  "firstRunCompleted": false,
  "lastLaunch": {
    "target": null,
    "at": null,
    "ok": null
  }
}
```

- [ ] **Step 1: Write failing tests**

Create `packages/launcher-settings/tests/settings.test.ts`:

```typescript
import assert from "node:assert/strict";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import test from "node:test";
import {
  DEFAULT_SETTINGS,
  loadSettings,
  parseSettings,
  resetSettings,
  saveSettings,
  settingsFilePath,
} from "../src/index.ts";

test("parseSettings accepts canonical shape", () => {
  const s = parseSettings(DEFAULT_SETTINGS);
  assert.equal(s.schemaVersion, 1);
  assert.equal(s.raceMode, "package");
  assert.equal(s.firstRunCompleted, false);
  assert.equal(s.paths.devBat.includes("LaunchClevelandRace.bat"), true);
});

test("parseSettings rejects bad raceMode", () => {
  assert.throws(() => parseSettings({ ...DEFAULT_SETTINGS, raceMode: "editor" }));
});

test("settingsFilePath joins AppData/raceGPS/settings.json", () => {
  const p = settingsFilePath("D:\\AppData");
  assert.equal(p, path.join("D:\\AppData", "raceGPS", "settings.json"));
});

test("loadSettings returns defaults when file missing", () => {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), "rg-settings-"));
  const file = path.join(dir, "settings.json");
  const s = loadSettings(file);
  assert.deepEqual(s, DEFAULT_SETTINGS);
});

test("saveSettings + loadSettings round-trip", () => {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), "rg-settings-"));
  const file = path.join(dir, "settings.json");
  const next = {
    ...DEFAULT_SETTINGS,
    firstRunCompleted: true,
    raceMode: "dev" as const,
    gpuNote: "RTX",
  };
  saveSettings(file, next);
  assert.deepEqual(loadSettings(file), next);
});

test("resetSettings writes defaults", () => {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), "rg-settings-"));
  const file = path.join(dir, "settings.json");
  saveSettings(file, { ...DEFAULT_SETTINGS, firstRunCompleted: true });
  const s = resetSettings(file);
  assert.equal(s.firstRunCompleted, false);
  assert.deepEqual(loadSettings(file), DEFAULT_SETTINGS);
});
```

- [ ] **Step 2: Add package.json + tsconfig (tests will fail until src exists)**

`packages/launcher-settings/package.json`:

```json
{
  "name": "@racegps/launcher-settings",
  "version": "0.1.0",
  "type": "module",
  "main": "src/index.ts",
  "types": "src/index.ts",
  "exports": {
    ".": "./src/index.ts"
  },
  "scripts": {
    "test": "node --import tsx --test tests/*.test.ts",
    "typecheck": "tsc -p tsconfig.json --noEmit"
  },
  "dependencies": {
    "zod": "^3.24.2"
  },
  "devDependencies": {
    "@types/node": "^22.8.0",
    "tsx": "^4.19.2",
    "typescript": "^5.6.3"
  }
}
```

`packages/launcher-settings/tsconfig.json`:

```json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "NodeNext",
    "moduleResolution": "NodeNext",
    "strict": true,
    "skipLibCheck": true,
    "noEmit": true,
    "types": ["node"]
  },
  "include": ["src/**/*.ts", "tests/**/*.ts"]
}
```

- [ ] **Step 3: Run tests — expect FAIL**

```powershell
cd C:\projects\raceGPS-grokbot-cleveland
npm install --workspace @racegps/launcher-settings
npm run test --workspace @racegps/launcher-settings
```

Expected: FAIL (module not found / Cannot find package).

- [ ] **Step 4: Implement schema + io**

`packages/launcher-settings/src/schema.ts`:

```typescript
import { z } from "zod";

export const RaceModeSchema = z.enum(["package", "dev"]);
export type RaceMode = z.infer<typeof RaceModeSchema>;

export const LauncherPathsSchema = z.object({
  worktreeRoot: z.string().min(1),
  devBat: z.string().min(1),
  packageExe: z.string().min(1),
  workshopPython: z.string().min(1),
  uproject: z.string().min(1),
  logDir: z.string().min(1),
});

export const LastLaunchSchema = z.object({
  target: z.enum(["race", "workshop"]).nullable(),
  at: z.string().nullable(),
  ok: z.boolean().nullable(),
});

export const LauncherSettingsSchema = z.object({
  schemaVersion: z.literal(1),
  raceMode: RaceModeSchema,
  paths: LauncherPathsSchema,
  gpuNote: z.string(),
  firstRunCompleted: z.boolean(),
  lastLaunch: LastLaunchSchema,
});

export type LauncherSettings = z.infer<typeof LauncherSettingsSchema>;

export function parseSettings(data: unknown): LauncherSettings {
  return LauncherSettingsSchema.parse(data);
}
```

`packages/launcher-settings/src/defaults.ts`:

```typescript
import type { LauncherSettings } from "./schema.ts";

const ROOT = "C:\\projects\\raceGPS-grokbot-cleveland";
const AKRON = `${ROOT}\\apps\\unreal-akron-beta`;

export const DEFAULT_SETTINGS: LauncherSettings = {
  schemaVersion: 1,
  raceMode: "package",
  paths: {
    worktreeRoot: ROOT,
    devBat: `${AKRON}\\LaunchClevelandRace.bat`,
    packageExe: `${AKRON}\\PackagedBuilds\\Win64\\raceGPSRace.exe`,
    workshopPython: `${ROOT}\\.venv-grokbot\\Scripts\\python.exe`,
    uproject: `${AKRON}\\raceGPSAkronBeta.uproject`,
    logDir: `${AKRON}\\Saved\\Logs`,
  },
  gpuNote: "",
  firstRunCompleted: false,
  lastLaunch: { target: null, at: null, ok: null },
};
```

`packages/launcher-settings/src/paths.ts`:

```typescript
import path from "node:path";

export function settingsFilePath(appDataRoot?: string): string {
  const root = appDataRoot ?? process.env.APPDATA ?? "";
  if (!root) {
    throw new Error("APPDATA unset; pass appDataRoot explicitly");
  }
  return path.join(root, "raceGPS", "settings.json");
}
```

`packages/launcher-settings/src/io.ts`:

```typescript
import fs from "node:fs";
import path from "node:path";
import { DEFAULT_SETTINGS } from "./defaults.ts";
import { parseSettings, type LauncherSettings } from "./schema.ts";

export function loadSettings(filePath: string): LauncherSettings {
  if (!fs.existsSync(filePath)) {
    return structuredClone(DEFAULT_SETTINGS);
  }
  const raw = JSON.parse(fs.readFileSync(filePath, "utf8"));
  return parseSettings(raw);
}

export function saveSettings(filePath: string, settings: LauncherSettings): void {
  const parsed = parseSettings(settings);
  fs.mkdirSync(path.dirname(filePath), { recursive: true });
  fs.writeFileSync(filePath, JSON.stringify(parsed, null, 2) + "\n", "utf8");
}

export function resetSettings(filePath: string): LauncherSettings {
  const defaults = structuredClone(DEFAULT_SETTINGS);
  saveSettings(filePath, defaults);
  return defaults;
}
```

`packages/launcher-settings/src/index.ts`:

```typescript
export {
  LauncherSettingsSchema,
  LauncherPathsSchema,
  RaceModeSchema,
  LastLaunchSchema,
  parseSettings,
  type LauncherSettings,
  type RaceMode,
} from "./schema.ts";
export { DEFAULT_SETTINGS } from "./defaults.ts";
export { settingsFilePath } from "./paths.ts";
export { loadSettings, saveSettings, resetSettings } from "./io.ts";
```

- [ ] **Step 5: Run tests — expect PASS**

```powershell
cd C:\projects\raceGPS-grokbot-cleveland
npm run test --workspace @racegps/launcher-settings
```

Expected: all 6 tests PASS.

- [ ] **Step 6: Commit (plan-allowed; settings package only)**

```powershell
git add packages/launcher-settings
git commit -m "feat(launcher-settings): zod schema + AppData settings IO"
```

Only if working tree for these paths is clean of unrelated dirty files; otherwise leave uncommitted for Chris review.

---

### Task 2: Electron+Vite launcher scaffold (`apps/racegps-launcher`)

**Research gate:** Electron+Vite official template / `electron-vite` docs (cite access date in `docs/evidence/grokbot/research/YYYY-MM-DD-electron-vite.md` using Task 0 template). Alternative Tauri only if Electron install blocked.

**Files:**
- Create: `apps/racegps-launcher/package.json`
- Create: `apps/racegps-launcher/electron.vite.config.ts`
- Create: `apps/racegps-launcher/tsconfig.json`
- Create: `apps/racegps-launcher/tsconfig.node.json`
- Create: `apps/racegps-launcher/index.html`
- Create: `apps/racegps-launcher/electron/main.ts`
- Create: `apps/racegps-launcher/electron/preload.ts`
- Create: `apps/racegps-launcher/src/main.tsx`
- Create: `apps/racegps-launcher/src/App.tsx`
- Create: `apps/racegps-launcher/src/styles.css`
- Create: `apps/racegps-launcher/src/pages/PlaceholderHome.tsx` (replaced in Tasks 3–4)
- Create: `apps/racegps-launcher/src/vite-env.d.ts`

**Interfaces:**
- Consumes: `@racegps/launcher-settings`, `@racegps/ui-kit`
- Produces:
  - npm scripts: `dev`, `build`, `preview`, `typecheck`, `test`
  - Preload API `window.racegps.getSettings(): Promise<LauncherSettings>`
  - Preload API `window.racegps.saveSettings(s: LauncherSettings): Promise<void>`
  - Main process settings path via `path.join(app.getPath('appData'), 'raceGPS', 'settings.json')` (same on-disk contract as `settingsFilePath`)

- [ ] **Step 1: Write package.json with real scripts**

`apps/racegps-launcher/package.json`:

```json
{
  "name": "@racegps/launcher",
  "version": "0.1.0",
  "private": true,
  "type": "module",
  "main": "./out/main/index.js",
  "scripts": {
    "dev": "electron-vite dev",
    "build": "electron-vite build",
    "preview": "electron-vite preview",
    "typecheck": "tsc -p tsconfig.json --noEmit && tsc -p tsconfig.node.json --noEmit",
    "test": "node --import tsx --test src/**/*.test.ts electron/**/*.test.ts"
  },
  "dependencies": {
    "@racegps/launcher-settings": "0.1.0",
    "@racegps/ui-kit": "0.1.0",
    "react": "^19.0.0",
    "react-dom": "^19.0.0",
    "react-router-dom": "^7.1.1"
  },
  "devDependencies": {
    "@types/node": "^22.8.0",
    "@types/react": "^19.0.2",
    "@types/react-dom": "^19.0.2",
    "@vitejs/plugin-react": "^4.3.4",
    "electron": "^33.2.1",
    "electron-vite": "^2.3.0",
    "tsx": "^4.19.2",
    "typescript": "^5.6.3",
    "vite": "^6.0.6"
  }
}
```

- [ ] **Step 2: Write electron-vite config + HTML + minimal pages**

`apps/racegps-launcher/electron.vite.config.ts`:

```typescript
import { resolve } from "node:path";
import { defineConfig, externalizeDepsPlugin } from "electron-vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  main: {
    plugins: [externalizeDepsPlugin()],
    build: { rollupOptions: { input: { index: resolve("electron/main.ts") } } },
  },
  preload: {
    plugins: [externalizeDepsPlugin()],
    build: { rollupOptions: { input: { index: resolve("electron/preload.ts") } } },
  },
  renderer: {
    root: ".",
    build: {
      rollupOptions: {
        input: { index: resolve("index.html") },
      },
    },
    plugins: [react()],
  },
});
```

`apps/racegps-launcher/index.html`:

```html
<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta
      http-equiv="Content-Security-Policy"
      content="default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'"
    />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>raceGPS Launcher</title>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.tsx"></script>
  </body>
</html>
```

`apps/racegps-launcher/src/main.tsx`:

```tsx
import React from "react";
import { createRoot } from "react-dom/client";
import { BrowserRouter } from "react-router-dom";
import { App } from "./App";
import "./styles.css";

createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <BrowserRouter>
      <App />
    </BrowserRouter>
  </React.StrictMode>,
);
```

`apps/racegps-launcher/src/App.tsx`:

```tsx
import { Navigate, Route, Routes } from "react-router-dom";
import { PlaceholderHome } from "./pages/PlaceholderHome";

export function App() {
  return (
    <Routes>
      <Route path="/" element={<PlaceholderHome />} />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}
```

`apps/racegps-launcher/src/pages/PlaceholderHome.tsx`:

```tsx
export function PlaceholderHome() {
  return (
    <main style={{ padding: 24, fontFamily: "system-ui" }}>
      <h1>raceGPS Launcher</h1>
      <p>Scaffold OK. Wizard/Home land in later tasks.</p>
    </main>
  );
}
```

`apps/racegps-launcher/src/styles.css`:

```css
@import "@racegps/ui-kit/tokens.css";

:root {
  color-scheme: dark;
  font-family: system-ui, sans-serif;
  background: #0b0f14;
  color: #e8eef7;
}

body {
  margin: 0;
}

button {
  cursor: pointer;
}
```

If `@racegps/ui-kit` does not export `tokens.css` via package exports, import with relative path `../../../packages/ui-kit/tokens.css` instead and note in commit.

- [ ] **Step 3: Write Electron main + preload (settings IPC only)**

`apps/racegps-launcher/electron/preload.ts`:

```typescript
import { contextBridge, ipcRenderer } from "electron";
import type { LauncherSettings } from "@racegps/launcher-settings";

contextBridge.exposeInMainWorld("racegps", {
  getSettings: (): Promise<LauncherSettings> => ipcRenderer.invoke("settings:get"),
  saveSettings: (s: LauncherSettings): Promise<void> =>
    ipcRenderer.invoke("settings:save", s),
  resetSettings: (): Promise<LauncherSettings> => ipcRenderer.invoke("settings:reset"),
  validatePaths: (): Promise<unknown> => ipcRenderer.invoke("paths:validate"),
  launchRace: (): Promise<{ ok: boolean; detail: string }> =>
    ipcRenderer.invoke("launch:race"),
  launchWorkshop: (): Promise<{ ok: boolean; detail: string }> =>
    ipcRenderer.invoke("launch:workshop"),
  openLogs: (): Promise<void> => ipcRenderer.invoke("logs:open"),
  runWorkshopCli: (argv: string[]): Promise<{ code: number; stdout: string; stderr: string }> =>
    ipcRenderer.invoke("workshop:cli", argv),
});
```

`apps/racegps-launcher/src/vite-env.d.ts`:

```typescript
import type { LauncherSettings } from "@racegps/launcher-settings";

export {};

declare global {
  interface Window {
    racegps: {
      getSettings: () => Promise<LauncherSettings>;
      saveSettings: (s: LauncherSettings) => Promise<void>;
      resetSettings: () => Promise<LauncherSettings>;
      validatePaths: () => Promise<unknown>;
      launchRace: () => Promise<{ ok: boolean; detail: string }>;
      launchWorkshop: () => Promise<{ ok: boolean; detail: string }>;
      openLogs: () => Promise<void>;
      runWorkshopCli: (
        argv: string[],
      ) => Promise<{ code: number; stdout: string; stderr: string }>;
    };
  }
}
```

`apps/racegps-launcher/electron/main.ts`:

```typescript
import { app, BrowserWindow, ipcMain, shell } from "electron";
import path from "node:path";
import {
  loadSettings,
  resetSettings,
  saveSettings,
  settingsFilePath,
  type LauncherSettings,
} from "@racegps/launcher-settings";

function settingsPath(): string {
  return settingsFilePath(app.getPath("appData"));
}

function createWindow(): void {
  const win = new BrowserWindow({
    width: 1100,
    height: 720,
    webPreferences: {
      preload: path.join(__dirname, "../preload/index.js"),
      contextIsolation: true,
      nodeIntegration: false,
    },
  });

  if (process.env.ELECTRON_RENDERER_URL) {
    win.loadURL(process.env.ELECTRON_RENDERER_URL);
  } else {
    win.loadFile(path.join(__dirname, "../renderer/index.html"));
  }
}

app.whenReady().then(() => {
  ipcMain.handle("settings:get", () => loadSettings(settingsPath()));
  ipcMain.handle("settings:save", (_e, s: LauncherSettings) => {
    saveSettings(settingsPath(), s);
  });
  ipcMain.handle("settings:reset", () => resetSettings(settingsPath()));
  // launch/validate stubs filled in Task 4
  ipcMain.handle("paths:validate", () => ({ stub: true }));
  ipcMain.handle("launch:race", () => ({
    ok: false,
    detail: "launch stub — wire in Task 4",
  }));
  ipcMain.handle("launch:workshop", () => ({
    ok: true,
    detail: "workshop stub — navigate renderer /workshop",
  }));
  ipcMain.handle("logs:open", async () => {
    const s = loadSettings(settingsPath());
    await shell.openPath(s.paths.logDir);
  });
  ipcMain.handle("workshop:cli", async () => ({
    code: 1,
    stdout: "",
    stderr: "workshop cli stub — Task 7",
  }));

  createWindow();
});

app.on("window-all-closed", () => {
  if (process.platform !== "darwin") app.quit();
});
```

Add matching `tsconfig.json` / `tsconfig.node.json` with `"strict": true`, `"jsx": "react-jsx"`, `"moduleResolution": "bundler"` for renderer and `"NodeNext"` for electron side (match monorepo style).

- [ ] **Step 4: Install + typecheck + smoke dev**

```powershell
cd C:\projects\raceGPS-grokbot-cleveland
npm install --workspace @racegps/launcher
npm run typecheck --workspace @racegps/launcher
```

Expected: typecheck PASS. Then:

```powershell
npm run dev --workspace @racegps/launcher
```

Expected: Electron window shows "raceGPS Launcher" / "Scaffold OK". **Do not** launch Unreal from this step.

- [ ] **Step 5: Commit scaffold only (optional)**

```powershell
git add apps/racegps-launcher packages/ui-kit package-lock.json
git commit -m "feat(launcher): electron-vite React scaffold"
```

---

### Task 3: First-run wizard + settings persist

**Files:**
- Create: `apps/racegps-launcher/src/pages/WizardPage.tsx`
- Create: `apps/racegps-launcher/src/pages/SettingsPage.tsx`
- Modify: `apps/racegps-launcher/src/App.tsx`
- Create: `apps/racegps-launcher/src/lib/useSettings.ts`
- Create: `apps/racegps-launcher/src/pages/wizard.test.ts` (pure helper tests if extracted)

**Interfaces:**
- Consumes: `window.racegps.getSettings/saveSettings`
- Produces: wizard writes `firstRunCompleted: true`; App routes `/wizard` when false, else `/`

- [ ] **Step 1: Write route-guard helper test**

`apps/racegps-launcher/src/lib/firstRun.ts`:

```typescript
import type { LauncherSettings } from "@racegps/launcher-settings";

export function initialRoute(settings: LauncherSettings): "/wizard" | "/" {
  return settings.firstRunCompleted ? "/" : "/wizard";
}
```

`apps/racegps-launcher/src/lib/firstRun.test.ts`:

```typescript
import assert from "node:assert/strict";
import test from "node:test";
import { DEFAULT_SETTINGS } from "@racegps/launcher-settings";
import { initialRoute } from "./firstRun.ts";

test("first run goes to wizard", () => {
  assert.equal(initialRoute(DEFAULT_SETTINGS), "/wizard");
});

test("completed goes home", () => {
  assert.equal(
    initialRoute({ ...DEFAULT_SETTINGS, firstRunCompleted: true }),
    "/",
  );
});
```

Run: `npm run test --workspace @racegps/launcher`  
Expected: PASS after files exist (adjust package.json test glob if needed: `node --import tsx --test src/lib/*.test.ts`).

- [ ] **Step 2: Implement WizardPage**

Fields (exact): Race package exe path, Dev bat path, Workshop python path, worktree root, GPU/adapter note (text), Package vs Dev default (`raceMode` radio).

On Finish:

```typescript
await window.racegps.saveSettings({
  ...current,
  paths: { ...current.paths, /* edited fields */ },
  gpuNote,
  raceMode,
  firstRunCompleted: true,
});
navigate("/");
```

- [ ] **Step 3: Implement SettingsPage**

Controls: raceMode toggle, all six path fields, GPU note, buttons **Reveal logs** (`window.racegps.openLogs`), **Reset defaults** (`window.racegps.resetSettings`), **Save**.

- [ ] **Step 4: Wire App bootstrap**

```tsx
// App.tsx — on mount load settings, Navigate to initialRoute(settings)
```

Routes: `/wizard`, `/`, `/settings` (Task 4 home; Task 6 workshop).

- [ ] **Step 5: Manual smoke**

```powershell
npm run dev --workspace @racegps/launcher
```

Delete `%AppData%\raceGPS\settings.json` if present → wizard appears → Finish → file exists with `firstRunCompleted: true`. Restart → lands on home placeholder.

- [ ] **Step 6: Commit**

```powershell
git add apps/racegps-launcher
git commit -m "feat(launcher): first-run wizard + settings persist"
```

---

### Task 4: Launcher home — validate paths + launch stubs

**Files:**
- Create: `apps/racegps-launcher/src/pages/HomePage.tsx`
- Create: `apps/racegps-launcher/src/lib/pathValidation.ts`
- Create: `apps/racegps-launcher/src/lib/pathValidation.test.ts`
- Modify: `apps/racegps-launcher/electron/main.ts` (real validate + launch)
- Modify: `apps/racegps-launcher/src/App.tsx` (HomePage at `/`)

**Interfaces:**
- Consumes: settings paths; `LaunchClevelandRace.bat` for Dev; package exe for Package
- Produces:
  - `validateLauncherPaths(settings) -> { devBatOk, packageExeOk, workshopPythonOk, uprojectOk, chips: StatusChip[] }`
  - Dev Race launch: `cmd.exe /c start "" "<devBat>"` **without** `nullrhi` / `playtest` args (human default Sunset windowed per bat)
  - Package Race launch: if exe missing → `{ ok:false, detail:"awaiting build" }` CTA; never pretend PASS
  - Workshop launch: navigate to `/workshop` in renderer (same app)

- [ ] **Step 1: Failing unit tests for validation**

```typescript
import assert from "node:assert/strict";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import test from "node:test";
import { DEFAULT_SETTINGS } from "@racegps/launcher-settings";
import { validateLauncherPaths } from "./pathValidation.ts";

test("marks missing package exe as awaiting build", () => {
  const missing = path.join(os.tmpdir(), "no-such-raceGPSRace.exe");
  const r = validateLauncherPaths({
    ...DEFAULT_SETTINGS,
    raceMode: "package",
    paths: { ...DEFAULT_SETTINGS.paths, packageExe: missing },
  }, fs.existsSync);
  assert.equal(r.packageExeOk, false);
  assert.equal(r.awaitingBuild, true);
});

test("dev bat ok when exists", () => {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), "rg-bat-"));
  const bat = path.join(dir, "LaunchClevelandRace.bat");
  fs.writeFileSync(bat, "@echo off\n");
  const r = validateLauncherPaths({
    ...DEFAULT_SETTINGS,
    raceMode: "dev",
    paths: { ...DEFAULT_SETTINGS.paths, devBat: bat },
  }, fs.existsSync);
  assert.equal(r.devBatOk, true);
});
```

- [ ] **Step 2: Implement pathValidation.ts**

```typescript
import type { LauncherSettings } from "@racegps/launcher-settings";

export type PathValidation = {
  devBatOk: boolean;
  packageExeOk: boolean;
  workshopPythonOk: boolean;
  uprojectOk: boolean;
  awaitingBuild: boolean;
  chips: { id: string; label: string; tone: "ok" | "warn" | "fail" }[];
};

export function validateLauncherPaths(
  settings: LauncherSettings,
  exists: (p: string) => boolean = (p) => {
    try {
      return require("node:fs").existsSync(p);
    } catch {
      return false;
    }
  },
): PathValidation {
  const devBatOk = exists(settings.paths.devBat);
  const packageExeOk = exists(settings.paths.packageExe);
  const workshopPythonOk = exists(settings.paths.workshopPython);
  const uprojectOk = exists(settings.paths.uproject);
  const awaitingBuild = settings.raceMode === "package" && !packageExeOk;
  const chips = [
    {
      id: "mode",
      label: `Mode: ${settings.raceMode}`,
      tone: "ok" as const,
    },
    {
      id: "devBat",
      label: devBatOk ? "Dev bat found" : "Dev bat missing",
      tone: devBatOk ? "ok" : "fail",
    },
    {
      id: "package",
      label: packageExeOk
        ? "Package exe found"
        : "Package awaiting build",
      tone: packageExeOk ? "ok" : "warn",
    },
    {
      id: "python",
      label: workshopPythonOk ? "Workshop python OK" : "Workshop python missing",
      tone: workshopPythonOk ? "ok" : "fail",
    },
  ];
  return {
    devBatOk,
    packageExeOk,
    workshopPythonOk,
    uprojectOk,
    awaitingBuild,
    chips,
  };
}
```

Prefer `import fs from "node:fs"` inside Electron main; renderer calls IPC `paths:validate` so browser bundle never `require`s fs. Keep the pure function injectable for tests.

- [ ] **Step 3: Wire main-process launch:race**

In `electron/main.ts`:

```typescript
import { spawn } from "node:child_process";
import fs from "node:fs";
import { validateLauncherPaths } from "../src/lib/pathValidation"; // or duplicate thin main-side module under electron/pathValidation.ts to avoid bundling React

ipcMain.handle("paths:validate", () => {
  const s = loadSettings(settingsPath());
  return validateLauncherPaths(s, fs.existsSync);
});

ipcMain.handle("launch:race", async () => {
  const s = loadSettings(settingsPath());
  const v = validateLauncherPaths(s, fs.existsSync);
  if (s.raceMode === "package") {
    if (!v.packageExeOk) {
      return {
        ok: false,
        detail:
          "Package mode awaiting build — switch to Dev, or point packageExe at a Chris-unlocked cook output (see docs/contracts/LAUNCHER_PATH_CONTRACT.md).",
      };
    }
    spawn(s.paths.packageExe, [], { detached: true, stdio: "ignore" }).unref();
    return { ok: true, detail: `spawned ${s.paths.packageExe}` };
  }
  if (!v.devBatOk) {
    return {
      ok: false,
      detail: `Dev bat missing. Expected: ${s.paths.devBat}`,
    };
  }
  // Human default only — NEVER append nullrhi / playtest / -unattended here.
  spawn("cmd.exe", ["/c", "start", "raceGPS Cleveland Race", s.paths.devBat], {
    detached: true,
    stdio: "ignore",
    cwd: path.dirname(s.paths.devBat),
  }).unref();
  return { ok: true, detail: `started ${s.paths.devBat}` };
});
```

Move `pathValidation.ts` under `electron/` **or** `packages/launcher-settings` if sharing is cleaner; do not import React pages into main.

- [ ] **Step 4: HomePage UI**

Buttons: **Play Race**, **Open Workshop** (`navigate('/workshop')`), **Settings**. Status chips from validation. If `awaitingBuild`, show CTA panel: "Package not built yet — use Dev mode or wait for Chris cook unlock."

- [ ] **Step 5: Test validation only (no Unreal required)**

```powershell
npm run test --workspace @racegps/launcher
```

Expected: pathValidation tests PASS. Manual: Package mode Play Race → CTA string, no UE process. Dev mode Play Race only when Chris/operator intentionally clicks — plan implementers may stub-verify spawn args without leaving the bat running unattended. **Do not** loop Gate 1 / nullrhi.

---

### Task 5: Build & Engine — `LAUNCHER_PATH_CONTRACT.md`

**Files:**
- Create: `docs/contracts/LAUNCHER_PATH_CONTRACT.md`

**Interfaces:**
- Consumes: inventory of `LaunchClevelandRace.bat`, `raceGPS.bat`, empty PackagedBuilds
- Produces: documented Package vs Dev layout the launcher reads (cite from unlock notes)

- [ ] **Step 1: Write contract doc (exact paths, no TBD)**

Write `docs/contracts/LAUNCHER_PATH_CONTRACT.md` with these locked rows:

| Mode | Entry | Resolved default path |
|------|-------|-------------------------|
| Dev Race | `LaunchClevelandRace.bat` | `C:\projects\raceGPS-grokbot-cleveland\apps\unreal-akron-beta\LaunchClevelandRace.bat` |
| Dev map/game overrides (inside bat) | map `/Game/Maps/Cleveland5_0KmWorld` ; game `/Script/raceGPSAkronBeta.ClevelandShowcaseGameMode` ; UE `C:\Program Files\Epic Games\UE_5.7\Engine\Binaries\Win64\UnrealEditor.exe` ; uproject `...\raceGPSAkronBeta.uproject` | GlobalDefaultGameMode **unchanged** (CruiseSprint) |
| Package Race | Win64 shipping/game exe | `C:\projects\raceGPS-grokbot-cleveland\apps\unreal-akron-beta\PackagedBuilds\Win64\raceGPSRace.exe` |
| Package status (2026-09-28) | **awaiting build** | G4/Shipping archive empty until Chris unlocks cook |
| Workshop python | venv | `C:\projects\raceGPS-grokbot-cleveland\.venv-grokbot\Scripts\python.exe` |
| Workshop CLIs | rgpack / semantic | `python -m rgpack` with `PYTHONPATH`/`cwd` including `tools\`; `tools\akron-semantic-compiler\compile_akron.py`; `tools\universal-city-compiler\cli.py` |
| Logs | UE Saved/Logs | `C:\projects\raceGPS-grokbot-cleveland\apps\unreal-akron-beta\Saved\Logs` |
| Settings | AppData | `%AppData%\raceGPS\settings.json` |
| Legacy GPU lock bat (reference only) | `apps\unreal-akron-beta\raceGPS.bat` | Workshop vs Race lock under `Saved\raceGPS\gpu.lock` — launcher MVP navigates Workshop in-process and does not replace this bat yet |

Include **Forbidden launcher args:** `nullrhi`, `-unattended`, `playtest` / `-ClevelandAutoLap` for human Play Race button. Those remain operator-only on the bat CLI.

- [ ] **Step 2: Cross-link from HomePage CTA** to this doc path (string in UI is enough).

- [ ] **Step 3: Verify**

```powershell
Test-Path C:\projects\raceGPS-grokbot-cleveland\docs\contracts\LAUNCHER_PATH_CONTRACT.md
Test-Path C:\projects\raceGPS-grokbot-cleveland\apps\unreal-akron-beta\LaunchClevelandRace.bat
Test-Path C:\projects\raceGPS-grokbot-cleveland\apps\unreal-akron-beta\PackagedBuilds\Win64\raceGPSRace.exe
```

Expected: contract + Dev bat = True; package exe = False (honest awaiting build).

---

### Task 6: Workshop local UI routes scaffold (auth-less)

**Files:**
- Create: `apps/racegps-launcher/src/workshop/LandingPage.tsx`
- Create: `apps/racegps-launcher/src/workshop/PackPage.tsx`
- Create: `apps/racegps-launcher/src/workshop/CompilePage.tsx`
- Create: `apps/racegps-launcher/src/workshop/ValidatePage.tsx`
- Create: `apps/racegps-launcher/src/workshop/ExportPage.tsx`
- Create: `apps/racegps-launcher/src/workshop/WorkshopLayout.tsx`
- Modify: `apps/racegps-launcher/src/App.tsx`

**Interfaces:**
- Consumes: react-router; settings.worktreeRoot
- Produces: routes `/workshop` → `/workshop/pack` → `/workshop/compile` → `/workshop/validate` → `/workshop/export` (auth-less). Empty states honest ("no pack open").

- [ ] **Step 1: WorkshopLayout with step nav**

Links: Landing | Pack | Compile | Validate | Export | Back to Launcher (`/`).

- [ ] **Step 2: Minimal page bodies**

Each page renders an `<h1>` and a short empty-state paragraph. PackPage holds React state `packDir: string | null` in a tiny context:

```tsx
// workshop/PackContext.tsx
export type PackState = { packDir: string | null; setPackDir: (p: string | null) => void };
```

Default pack output suggestion: `{worktreeRoot}\Saved\workshop-packs\burke_overpass_proof_v1`.

- [ ] **Step 3: Wire routes in App.tsx**

```tsx
<Route path="/workshop" element={<WorkshopLayout />}>
  <Route index element={<LandingPage />} />
  <Route path="pack" element={<PackPage />} />
  <Route path="compile" element={<CompilePage />} />
  <Route path="validate" element={<ValidatePage />} />
  <Route path="export" element={<ExportPage />} />
</Route>
```

- [ ] **Step 4: Smoke**

`npm run dev --workspace @racegps/launcher` → Open Workshop → walk routes without CLI yet.

---

### Task 7: Wire Overpass/semantic CLI into Workshop routes

**Research gate:** confirm existing PASS path from handoff semantic pin + `python -m rgpack export-overpass --fixture`. Cite in research brief.

**Files:**
- Create: `apps/racegps-launcher/electron/workshopCli.ts`
- Modify: `apps/racegps-launcher/electron/main.ts` (`workshop:cli`)
- Modify: `apps/racegps-launcher/src/workshop/CompilePage.tsx`
- Modify: `apps/racegps-launcher/src/workshop/ValidatePage.tsx`
- Modify: `apps/racegps-launcher/src/workshop/ExportPage.tsx`
- Create: `apps/racegps-launcher/electron/workshopCli.test.ts` (argv builder unit tests)

**Interfaces:**
- Consumes:
  - `settings.paths.workshopPython`
  - `settings.paths.worktreeRoot`
  - Offline fixture: `tests\fixtures\rgpack\overpass_burke_tiny\overpass.json`
- Produces:
  - `buildRgpackExportArgv(outDir, packId) -> string[]` for `python -m rgpack export-overpass --fixture -o <out> --pack-id <id>`
  - `buildRgpackValidateArgv(packDir) -> string[]` for `python -m rgpack validate <packDir>`
  - `buildAkronCompileCommand() -> { cwd, argv }` → `python compile_akron.py` with cwd `tools\akron-semantic-compiler`
  - IPC `workshop:cli` runs with `env: { ...process.env, PYTHONPATH: worktreeRoot\tools }` and `cwd: worktreeRoot` for `-m rgpack`
  - Surfaces stdout/stderr + log path in UI; on fail show CLI/log path (never silent)

- [ ] **Step 1: Argv builder tests**

```typescript
import assert from "node:assert/strict";
import test from "node:test";
import { buildRgpackExportArgv, buildRgpackValidateArgv } from "./workshopCli.ts";

test("export uses fixture flag and out dir", () => {
  const argv = buildRgpackExportArgv(
    "C:\\packs\\burke",
    "burke_overpass_proof_v1",
  );
  assert.deepEqual(argv, [
    "-m",
    "rgpack",
    "export-overpass",
    "--fixture",
    "-o",
    "C:\\packs\\burke",
    "--pack-id",
    "burke_overpass_proof_v1",
  ]);
});

test("validate passes pack dir", () => {
  assert.deepEqual(buildRgpackValidateArgv("C:\\packs\\burke"), [
    "-m",
    "rgpack",
    "validate",
    "C:\\packs\\burke",
  ]);
});
```

- [ ] **Step 2: Implement workshopCli.ts spawn**

```typescript
import { spawn } from "node:child_process";
import path from "node:path";

export function buildRgpackExportArgv(outDir: string, packId: string): string[] {
  return ["-m", "rgpack", "export-overpass", "--fixture", "-o", outDir, "--pack-id", packId];
}

export function buildRgpackValidateArgv(packDir: string): string[] {
  return ["-m", "rgpack", "validate", packDir];
}

export function runPythonModule(opts: {
  python: string;
  worktreeRoot: string;
  argv: string[];
}): Promise<{ code: number; stdout: string; stderr: string }> {
  const tools = path.join(opts.worktreeRoot, "tools");
  return new Promise((resolve) => {
    const child = spawn(opts.python, opts.argv, {
      cwd: opts.worktreeRoot,
      env: { ...process.env, PYTHONPATH: tools },
      windowsHide: true,
    });
    let stdout = "";
    let stderr = "";
    child.stdout.on("data", (d) => (stdout += String(d)));
    child.stderr.on("data", (d) => (stderr += String(d)));
    child.on("close", (code) => resolve({ code: code ?? 1, stdout, stderr }));
  });
}
```

Semantic compile button (secondary): spawn `python compile_akron.py` with `cwd: path.join(worktreeRoot, "tools", "akron-semantic-compiler")` — document output under `citypacks/akron-oh-beta-001/` as reference; primary Workshop happy-path for MVP remains **rgpack fixture export** (already proven). Universal compiler `cli.py` exposed as advanced dropdown only (no live Overpass required for MVP proof).

- [ ] **Step 3: Wire Compile / Validate / Export pages**

- CompilePage: button "Export Burke offline fixture → rgpack" calls IPC; shows stdout; on `RESULT PASS` set packDir.
- ValidatePage: button runs validate on packDir; show PASS/FAIL.
- ExportPage: reveal folder via `shell.openPath(packDir)`; copy path; note "Race .rgpack load is later — export proof only".

- [ ] **Step 4: CLI smoke (no Unreal)**

```powershell
cd C:\projects\raceGPS-grokbot-cleveland
.\.venv-grokbot\Scripts\python.exe -m rgpack export-overpass --fixture -o Saved\workshop-packs\burke_plan_proof --pack-id burke_plan_proof
.\.venv-grokbot\Scripts\python.exe -m rgpack validate Saved\workshop-packs\burke_plan_proof
```

Expected: RESULT PASS both. Then same through Workshop UI.

---

### Task 8: Race HUD/settings — freeze-safe plan + implementation notes

**Files:**
- Create: `docs/evidence/grokbot/easy-test-beta/RACE-HUD-SETTINGS-PLAN.md`
- Optionally Create (code-only, no PIE required): stub comments or thin C++ headers under Cleveland path **only if** Race Systems is unlocked for code — default for this plan is **docs-first**. Do not launch editor.

**Interfaces:**
- Consumes patterns from:
  - `apps/unreal-akron-beta/Source/raceGPSAkronBeta/Public/MainMenuWidget.h`
  - `.../SettingsWidget.h` (Apply/Reset/Back + TabSwitcher)
  - `.../OnboardingManager.h` (step machine — launcher already owns first-run; Race skips re-onboarding)
  - `.../PauseMenuWidget.h` (Resume/Settings)
  - `.../VisualQualitySettings.h` (`EVisualQualityTier` Low/Medium/High/Epic)
  - Content stubs: `Content/UI/HUD/WBP_NeonHUD.txt`, `WBP_Speedometer.txt`, `Content/UI/Settings/WBP_Settings.txt`, `Content/UI/Pause/WBP_PauseMenu.txt`
- Produces: implementation checklist Race Systems executes later; **runtime evidence only when Dev launch allowed / Chris unlock**

- [ ] **Step 1: Write RACE-HUD-SETTINGS-PLAN.md**

Must include:

1. **OSS research checkbox** — CommonUI / Lyra-style pause + Chaos Vehicle HUD samples; cite dates in `docs/evidence/grokbot/research/`.
2. **Port ideas, do not merge Akron shell** — list functions to mirror (`OnApplyClicked`, quality tiers, pause Resume) without importing Akron map/menu GameModes.
3. **Cleveland HUD MVP fields:** speed (km/h), race state, checkpoint/lap distance clarity — map to stubs `WBP_Speedometer`, `WBP_LapTimer`, `WBP_CheckpointDistance`, root `WBP_NeonHUD`.
4. **In-Race settings MVP:** graphics presets via `EVisualQualityTier`; input hints; Apply/Resume from pause — mirror `SettingsWidget` + `PauseMenuWidget`.
5. **Game mode rule:** Cleveland only via `LaunchClevelandRace.bat` overrides (`ClevelandShowcaseGameMode`); never change GlobalDefaultGameMode.
6. **Evidence rule:** PIE/`-game` log + screenshots; **NullRHI ≠ PASS**; no unattended Gate 1.
7. **Freeze order:** (a) docs+stub alignment, (b) C++/WBP wiring when Race Systems scheduled, (c) attended Dev launch for screenshots after Chris unlock.

- [ ] **Step 2: Self-check links resolve**

```powershell
cd C:\projects\raceGPS-grokbot-cleveland
@(
  "apps\unreal-akron-beta\Source\raceGPSAkronBeta\Public\MainMenuWidget.h",
  "apps\unreal-akron-beta\Source\raceGPSAkronBeta\Public\SettingsWidget.h",
  "apps\unreal-akron-beta\Source\raceGPSAkronBeta\Public\OnboardingManager.h",
  "apps\unreal-akron-beta\Source\raceGPSAkronBeta\Public\PauseMenuWidget.h",
  "apps\unreal-akron-beta\Source\raceGPSAkronBeta\Public\VisualQualitySettings.h",
  "Content\UI\HUD\WBP_NeonHUD.txt",
  "Content\UI\HUD\WBP_Speedometer.txt",
  "Content\UI\Settings\WBP_Settings.txt"
) | ForEach-Object { "$((Test-Path $_)) $_" }
```

Expected: all True.

- [ ] **Step 3: Do not launch Unreal in this task**

Record in the doc: "Runtime evidence deferred to Chris unlock / attended Dev."

---

### Task 9: Evidence templates + Unreal PM FAIL-CLOSED checklist

**Files:**
- Create: `docs/evidence/grokbot/easy-test-beta/README.md`
- Create: `docs/evidence/grokbot/easy-test-beta/EVIDENCE-TEMPLATE.md`
- Create: `docs/evidence/grokbot/easy-test-beta/FAIL-CLOSED-CHECKLIST.md`

**Interfaces:**
- Consumes: design success-criteria table
- Produces: Unreal PM grade sheet; lane owners drop screenshots/notes here

- [ ] **Step 1: README index**

Rows for Launcher / Workshop / Race / Build contract / Research ops with "Done when" copied from design + pointer to evidence files.

- [ ] **Step 2: EVIDENCE-TEMPLATE.md**

```markdown
# Evidence — <LANE> — <YYYY-MM-DD>

**Lane:** Launcher | Workshop | Race | Build contract | Research ops  
**Operator:**  
**Mode:** Package | Dev | N/A  
**NullRHI used?** No (required No for visual PASS)

## What was run

Exact commands / UI clicks.

## Artifacts

- Screenshot paths:
- Log paths:

## Result

PASS | FAIL | BLOCKED (awaiting build / awaiting Chris unlock)

## Notes

Honest empty/awaiting states OK. NullRHI or black void is not visual PASS.
```

- [ ] **Step 3: FAIL-CLOSED-CHECKLIST.md**

Unreal PM grades:

| Gate | Question | PASS only if |
|------|----------|--------------|
| L1 | Wizard restores settings? | File round-trip + screenshot |
| L2 | Play Race respects mode? | Package → awaiting-build CTA **or** exe spawn; Dev → bat start; no nullrhi from UI |
| L3 | Open Workshop routes? | Auth-less walk to export |
| W1 | Fixture export PASS? | `python -m rgpack` RESULT PASS + UI log |
| W2 | Validate fail surfaces log? | Deliberate bad path shows stderr |
| R1 | HUD/settings notes cite Akron patterns? | Doc links resolve |
| R2 | Runtime Race evidence? | Only after Chris unlock; screenshots not NullRHI |
| B1 | Path contract written? | `docs/contracts/LAUNCHER_PATH_CONTRACT.md` |
| O1 | Research folder exists? | Task 0 files present |
| O2 | R&T bot created by this plan? | **Must be NO** |

Any "visual PASS" with NullRHI → **FAIL-CLOSED**.

- [ ] **Step 4: Verify tree**

```powershell
Get-ChildItem C:\projects\raceGPS-grokbot-cleveland\docs\evidence\grokbot\easy-test-beta |
  Select-Object Name, Length
```

---

## Self-review (spec coverage)

| Design requirement | Task |
|--------------------|------|
| Desktop launcher install/setup/settings | Tasks 2–4 |
| Package default / Dev team / same settings shell | Tasks 1, 3, 4 |
| Cleveland race content + Akron compilers in Workshop only | Tasks 4, 5, 7; Global Constraints |
| No full Akron Unreal shell merge | Global Constraints + Task 8 |
| Milestone: launcher + Workshop routes + Race HUD/settings notes | Tasks 2–9 |
| Parallel three-lane under Unreal PM | Lane notes in Tasks 5/8/9; PM checklist Task 9 |
| Research modern OSS each stage | Research gates Tasks 1,2,7,8 + Task 0 folder |
| PM research-when-idle folder | Task 0 |
| R&T bot when PM stops | **OUT OF SCOPE** code; Task 0 ops note only |
| Shared `%AppData%\raceGPS\settings.json` | Task 1 exact shape |
| Workshop auth-less landing→pack→compile→validate→export | Tasks 6–7 |
| Reuse offline Burke / `python -m rgpack` | Task 7 |
| Race HUD + in-race settings patterns from Akron widgets | Task 8 |
| Build contract Package vs Dev | Task 5 |
| Package may be awaiting build | Tasks 4–5 |
| No unattended LaunchClevelandRace / NullRHI ≠ PASS | Global Constraints + Tasks 4, 8, 9 |
| No master merge / robocopy / reconcile | Global Constraints |
| Race `.rgpack` load later | Task 7 ExportPage note |
| GlobalDefaultGameMode stays CruiseSprint | Global Constraints + Task 5 |
| Prefer `apps/racegps-launcher` over inventing cityhub frontend | File map + inventory locks |

**Placeholder scan:** none of TBD / TODO / "implement later" remain in task steps.  
**Type consistency:** `LauncherSettings`, `raceMode: "package"|"dev"`, IPC `window.racegps.*`, packDir string — aligned across Tasks 1–7.  
**Path consistency:** Dev bat under `apps/unreal-akron-beta/LaunchClevelandRace.bat`; package exe under `PackagedBuilds\Win64\raceGPSRace.exe`.

---

## Execution handoff (for Chris / Prototyper)

Plan complete when written to:

1. `C:\projects\raceGPS-grokbot-cleveland\docs\superpowers\plans\2026-09-28-easy-test-beta-launcher.md`
2. `C:\Users\cgp22\Documents\raceGPS-handoff\2026-09-28-EASY-TEST-BETA-LAUNCHER-PLAN.md`
3. `C:\projects\raceGPS-grokbot-cleveland\docs\handoff\2026-09-28-EASY-TEST-BETA-LAUNCHER-PLAN.md`

Implement with superpowers:subagent-driven-development (recommended) or executing-plans after Chris approves. Do **not** create agents or brief Wave 1 from this plan write alone.
